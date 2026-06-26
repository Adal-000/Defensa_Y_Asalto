"""
Descripcion:
    Cliente de red para conectarse a una partida multijugador de
    "Defensa y Asalto de Base". Este modulo no usa Tkinter; entrega
    metodos simples para que la interfaz pueda conectarse, enviar
    acciones y recibir estados actualizados desde el servidor.
"""

import socket
import sys
import threading

from infraestructura.persistencia.archivos import sincronizar_victoria_red
from infraestructura.red.protocolo import (
    ACCION_COMPRAR_MURO,
    ACCION_COMPRAR_TORRE,
    ACCION_COMPRAR_UNIDAD,
    ACCION_INICIAR_COMBATE,
    ACCION_OBTENER_ESTADO,
    ACCION_PAUSAR_COMBATE,
    ACCION_SALIR,
    ACCION_UNIRSE,
    ErrorProtocolo,
    crear_mensaje,
    enviar_mensaje,
    recibir_mensaje,
)

PUERTO_PREDETERMINADO = 5000


class ClientePartida:
    """
    Descripcion:
        Representa el cliente de una computadora jugadora. Se conecta
        al servidor, envia acciones y guarda el ultimo estado recibido.

    Entradas:
        callback_mensaje (function): Funcion opcional que recibe cada
            mensaje entrante. Es util para que Tkinter actualice la
            pantalla cuando llegue un nuevo estado.

    Salidas:
        No retorna nada. Construye un cliente listo para conectarse.

    Restricciones:
        - Debe conectarse a un servidor activo antes de enviar acciones.
        - callback_mensaje debe aceptar un parametro tipo dict.
    """

    def __init__(self, callback_mensaje=None):
        self.callback_mensaje = callback_mensaje
        self.conexion = None
        self.archivo_lectura = None
        self.conectado = False
        self.usuario = None
        self.rol = None
        self.ultimo_estado = None
        self.fase_actual = None
        self.combate_activo = False
        self.ultimo_error = None
        self.ultimos_mensajes = []
        self.usuarios_por_rol = {}
        self.roles_faltantes = []
        self.sala_lista = False
        self.mensaje_sala = ""
        self.victorias_sincronizadas = set()
        self.bloqueo = threading.Lock()

    def conectar(self, host, usuario, puerto=PUERTO_PREDETERMINADO, rol=""):
        """
        Descripcion:
            Conecta el cliente con el servidor y envia el mensaje
            inicial para unirse a la sala.

        Entradas:
            host (str): IP o nombre del servidor.
            usuario (str): Nombre de usuario del jugador.
            puerto (int): Puerto TCP del servidor.
            rol (str): Rol deseado, "defensor" o "atacante". Puede
                dejarse vacio para asignacion automatica.

        Salidas:
            tuple[bool, str]: Exito de la conexion y mensaje
            descriptivo.

        Restricciones:
            - El servidor debe estar ejecutandose.
            - usuario no debe estar vacio.
        """
        usuario = str(usuario).strip()
        if usuario == "":
            return False, "El usuario no puede estar vacio."

        try:
            self.conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conexion.connect((host, puerto))
            self.archivo_lectura = self.conexion.makefile("r", encoding="utf-8")
            self.conectado = True
            self.usuario = usuario

            mensaje_union = crear_mensaje(ACCION_UNIRSE, usuario=usuario, rol=rol)
            enviar_mensaje(self.conexion, mensaje_union)

            hilo_escucha = threading.Thread(target=self._escuchar_servidor, daemon=True)
            hilo_escucha.start()

            return True, "Conectado al servidor."

        except OSError as error:
            self.cerrar()
            return False, f"No se pudo conectar al servidor: {error}"

    def _escuchar_servidor(self):
        """
        Descripcion:
            Escucha mensajes entrantes del servidor y actualiza el
            ultimo estado conocido por el cliente.

        Entradas:
            Ninguna.

        Salidas:
            None: Modifica ultimo_estado y ultimos_mensajes.

        Restricciones:
            - Requiere una conexion abierta.
        """
        while self.conectado:
            try:
                mensaje = recibir_mensaje(self.archivo_lectura)
                if mensaje is None:
                    break
                self._procesar_mensaje_entrante(mensaje)
            except (OSError, ErrorProtocolo):
                break

        self.cerrar()

    def _procesar_mensaje_entrante(self, mensaje):
        """
        Descripcion:
            Guarda un mensaje recibido y llama el callback configurado,
            si existe.

        Entradas:
            mensaje (dict): Mensaje recibido del servidor.

        Salidas:
            None: Actualiza atributos internos.

        Restricciones:
            Ninguna.
        """
        with self.bloqueo:
            self.ultimos_mensajes.append(mensaje)
            if len(self.ultimos_mensajes) > 50:
                self.ultimos_mensajes = self.ultimos_mensajes[-50:]

            if "estado" in mensaje and mensaje["estado"] is not None:
                self.ultimo_estado = mensaje["estado"]
                self._sincronizar_victoria_si_finalizo(mensaje["estado"])

            if mensaje.get("exito") is False:
                self.ultimo_error = mensaje.get("mensaje")

            datos = mensaje.get("datos", {})
            if isinstance(datos, dict):
                if "rol" in datos:
                    self.rol = datos["rol"]
                if "rol_cliente" in datos:
                    self.rol = datos["rol_cliente"]
                if "fase_actual" in datos:
                    self.fase_actual = datos["fase_actual"]
                if "combate_activo" in datos:
                    self.combate_activo = bool(datos["combate_activo"])
                if "usuarios_por_rol" in datos and isinstance(datos["usuarios_por_rol"], dict):
                    self.usuarios_por_rol = datos["usuarios_por_rol"].copy()
                if "roles_faltantes" in datos and isinstance(datos["roles_faltantes"], list):
                    self.roles_faltantes = list(datos["roles_faltantes"])
                if "sala_lista" in datos:
                    self.sala_lista = bool(datos["sala_lista"])
                if "mensaje_sala" in datos:
                    self.mensaje_sala = str(datos["mensaje_sala"])

        if self.callback_mensaje is not None:
            self.callback_mensaje(mensaje)

    def _sincronizar_victoria_si_finalizo(self, estado):
        """
        Descripcion:
            Cuando el servidor avisa que la partida terminó, guarda
            esa victoria en el jugadores.json local de esta computadora.
            Se hace una sola vez por partida para no duplicar contador.
        """
        if not isinstance(estado, dict):
            return

        if not estado.get("partida_finalizada"):
            return

        ganador = estado.get("ganador_partida")
        rol = estado.get("rol_ganador_partida")
        numero_ronda = estado.get("numero_ronda")
        llave = (ganador, rol, numero_ronda)

        if not ganador or rol not in ("defensor", "atacante"):
            return

        if llave in self.victorias_sincronizadas:
            return

        if sincronizar_victoria_red(ganador, rol):
            self.victorias_sincronizadas.add(llave)


    def enviar_accion(self, accion, **datos):
        """
        Descripcion:
            Envia una accion generica al servidor.

        Entradas:
            accion (str): Accion definida en el protocolo.
            **datos: Datos necesarios para la accion.

        Salidas:
            tuple[bool, str]: Exito del envio y mensaje descriptivo.

        Restricciones:
            - El cliente debe estar conectado.
            - accion debe ser valida dentro del protocolo.
        """
        if not self.conectado or self.conexion is None:
            return False, "No hay conexion activa con el servidor."

        try:
            mensaje = crear_mensaje(accion, **datos)
            enviar_mensaje(self.conexion, mensaje)
            return True, "Accion enviada."
        except (OSError, ErrorProtocolo) as error:
            return False, str(error)

    def comprar_torre(self, tipo_torre, fila, columna):
        """
        Descripcion:
            Envia al servidor la solicitud para comprar una torre.

        Entradas:
            tipo_torre (str): Tipo de torre a comprar.
            fila (int): Fila de colocacion.
            columna (int): Columna de colocacion.

        Salidas:
            tuple[bool, str]: Exito del envio y mensaje descriptivo.

        Restricciones:
            - Solo funcionara en el servidor si este cliente es defensor.
        """
        return self.enviar_accion(
            ACCION_COMPRAR_TORRE,
            tipo_torre=tipo_torre,
            fila=fila,
            columna=columna,
        )

    def comprar_muro(self, fila, columna):
        """
        Descripcion:
            Envia al servidor la solicitud para comprar un muro.

        Entradas:
            fila (int): Fila de colocacion.
            columna (int): Columna de colocacion.

        Salidas:
            tuple[bool, str]: Exito del envio y mensaje descriptivo.

        Restricciones:
            - Solo funcionara en el servidor si este cliente es defensor.
        """
        return self.enviar_accion(ACCION_COMPRAR_MURO, fila=fila, columna=columna)

    def comprar_unidad(self, tipo_unidad, fila, columna):
        """
        Descripcion:
            Envia al servidor la solicitud para comprar una unidad.

        Entradas:
            tipo_unidad (str): Tipo de unidad a comprar.
            fila (int): Fila de colocacion.
            columna (int): Columna de colocacion.

        Salidas:
            tuple[bool, str]: Exito del envio y mensaje descriptivo.

        Restricciones:
            - Solo funcionara en el servidor si este cliente es atacante.
        """
        return self.enviar_accion(
            ACCION_COMPRAR_UNIDAD,
            tipo_unidad=tipo_unidad,
            fila=fila,
            columna=columna,
        )


    def ejecutar_combate(self):
        """
        Descripcion:
            Solicita al servidor ejecutar un solo turno de combate.
            Este metodo es util para pruebas o para un modo manual;
            para tiempo real se recomienda iniciar_combate().

        Entradas:
            Ninguna.

        Salidas:
            tuple[bool, str]: Exito del envio y mensaje descriptivo.

        Restricciones:
            - Debe existir una partida creada en el servidor.
        """
        return self.enviar_accion("ejecutar_combate")

    def iniciar_combate(self, numero_ronda=None):
        """
        Descripcion:
            Solicita al servidor que empiece a ejecutar el combate en
            tiempo real. El numero de ronda evita que dos temporizadores
            atrasados inicien o cierren una ronda nueva por accidente.
        """
        datos = {}
        if numero_ronda is not None:
            datos["numero_ronda"] = numero_ronda
        return self.enviar_accion(ACCION_INICIAR_COMBATE, **datos)

    def pausar_combate(self):
        """
        Descripcion:
            Solicita al servidor pausar el avance automatico del
            combate.

        Entradas:
            Ninguna.

        Salidas:
            tuple[bool, str]: Exito del envio y mensaje descriptivo.

        Restricciones:
            - Debe haber conexion activa.
        """
        return self.enviar_accion(ACCION_PAUSAR_COMBATE)

    def obtener_estado(self):
        """
        Descripcion:
            Solicita al servidor el estado actual de la partida.

        Entradas:
            Ninguna.

        Salidas:
            tuple[bool, str]: Exito del envio y mensaje descriptivo.

        Restricciones:
            - Debe haber conexion activa.
        """
        return self.enviar_accion(ACCION_OBTENER_ESTADO)

    def cerrar(self):
        """
        Descripcion:
            Cierra la conexion del cliente con el servidor.

        Entradas:
            Ninguna.

        Salidas:
            None: Cierra socket y archivo de lectura.

        Restricciones:
            Ninguna.
        """
        self.conectado = False

        try:
            if self.conexion is not None:
                enviar_mensaje(self.conexion, crear_mensaje(ACCION_SALIR))
        except (OSError, ErrorProtocolo):
            pass

        try:
            if self.archivo_lectura is not None:
                self.archivo_lectura.close()
        except OSError:
            pass

        try:
            if self.conexion is not None:
                self.conexion.close()
        except OSError:
            pass

    def obtener_ultimo_estado_local(self):
        """
        Descripcion:
            Devuelve el ultimo estado recibido desde el servidor sin
            hacer una nueva solicitud por red.

        Entradas:
            Ninguna.

        Salidas:
            dict: Ultimo estado recibido.
            None: Si todavia no se ha recibido estado.

        Restricciones:
            Ninguna.
        """
        with self.bloqueo:
            return self.ultimo_estado

    def obtener_resumen_red(self):
        """
        Descripcion:
            Devuelve los datos de red mas recientes recibidos desde el
            servidor, sin enviar una nueva solicitud. Es util para que
            una interfaz consulte rol, fase, combate activo y ultimo
            error de forma simple.

        Entradas:
            Ninguna.

        Salidas:
            dict: Resumen local de la conexion del cliente.

        Restricciones:
            - Los datos dependen del ultimo mensaje recibido desde el
              servidor.
        """
        with self.bloqueo:
            return {
                "conectado": self.conectado,
                "usuario": self.usuario,
                "rol": self.rol,
                "fase_actual": self.fase_actual,
                "combate_activo": self.combate_activo,
                "ultimo_error": self.ultimo_error,
                "tiene_estado": self.ultimo_estado is not None,
                "usuarios_por_rol": self.usuarios_por_rol.copy(),
                "roles_faltantes": list(self.roles_faltantes),
                "sala_lista": self.sala_lista,
                "mensaje_sala": self.mensaje_sala,
            }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python Red/cliente.py <ip_servidor> <usuario> [rol]")
        print("Ejemplo: python Red/cliente.py 192.168.1.25 daniel defensor")
        sys.exit(0)

    ip_servidor = sys.argv[1]
    usuario_cli = sys.argv[2]
    rol_cli = ""
    if len(sys.argv) >= 4:
        rol_cli = sys.argv[3]

    def imprimir_mensaje(mensaje):
        print(mensaje)

    cliente = ClientePartida(callback_mensaje=imprimir_mensaje)
    exito_conexion, mensaje_conexion = cliente.conectar(ip_servidor, usuario_cli, rol=rol_cli)
    print(mensaje_conexion)

    if exito_conexion:
        print("Comandos: torre tipo fila columna | muro fila columna | unidad tipo fila columna")
        print("          iniciar | pausar | estado | salir")

        while cliente.conectado:
            comando = input("> ").strip().split()
            if not comando:
                continue

            if comando[0] == "salir":
                cliente.cerrar()
                break
            elif comando[0] == "torre" and len(comando) == 4:
                cliente.comprar_torre(comando[1], int(comando[2]), int(comando[3]))
            elif comando[0] == "muro" and len(comando) == 3:
                cliente.comprar_muro(int(comando[1]), int(comando[2]))
            elif comando[0] == "unidad" and len(comando) == 4:
                cliente.comprar_unidad(comando[1], int(comando[2]), int(comando[3]))
            elif comando[0] == "iniciar":
                cliente.iniciar_combate()
            elif comando[0] == "pausar":
                cliente.pausar_combate()
            elif comando[0] == "estado":
                cliente.obtener_estado()
            else:
                print("Comando no reconocido.")
