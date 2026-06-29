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
    ACCION_USAR_HABILIDAD_ESPECIAL,
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
        """
        Descripcion:
            Inicializa la instancia y asigna los valores necesarios para
            que el objeto pueda utilizarse correctamente.
        
        Entradas:
            callback_mensaje (object): Valor recibido por la funcion.
            Valor opcional.
        
        Salidas:
            None: Inicializa los atributos de la instancia.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
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
        # Callbacks temporales de enviar_accion_y_esperar() esperando
        # la respuesta del PROXIMO mensaje que llegue del servidor.
        self._esperas_respuesta = []

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

        if self.callback_mensaje is not None:
            self.callback_mensaje({
                "tipo": "evento",
                "exito": False,
                "mensaje": "Conexión cerrada por el servidor.",
                "datos": {"conexion_perdida": True},
            })
        self.cerrar()

    def _procesar_mensaje_entrante(self, mensaje):
        """
        Descripcion:
            Guarda un mensaje recibido, notifica a quien este esperando
            la respuesta de una accion (ver enviar_accion_y_esperar) y
            llama el callback configurado, si existe.

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

            # Notifica al callback de espera mas antiguo (FIFO) que
            # acepte este mensaje. El servidor responde a los mensajes
            # de un mismo cliente en el mismo orden en que los recibe,
            # asi que la primera espera pendiente corresponde a la
            # primera accion todavia sin confirmar.
            if self._esperas_respuesta:
                callback_mas_antiguo = self._esperas_respuesta[0]
                if callback_mas_antiguo(mensaje):
                    self._esperas_respuesta.pop(0)

        if self.callback_mensaje is not None:
            self.callback_mensaje(mensaje)

    def _sincronizar_victoria_si_finalizo(self, estado):
        """
        Descripcion:
            Cuando el servidor avisa que la partida terminó, guarda esa
            victoria en el jugadores.json local de esta computadora. Se
            hace una sola vez por partida para no duplicar contador.
        
        Entradas:
            estado (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
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
            Envia una accion generica al servidor sin esperar la
            respuesta real: devuelve "exito" apenas el mensaje sale
            por el socket. Sirve para acciones donde no importa
            confirmar el resultado exacto (por ejemplo pedir el
            estado). Para compras y otras acciones donde el usuario
            necesita saber si el servidor la aceptó de verdad, usar
            enviar_accion_y_esperar en su lugar.

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

    def enviar_accion_y_esperar(self, accion, tiempo_espera=2.0, **datos):
        """
        Descripcion:
            Envia una accion al servidor y espera la respuesta real
            que el servidor manda para ESA accion, en lugar de asumir
            que se acepto solo porque el mensaje salio por la red.

            Esto evita el caso en que la interfaz dice "comprada
            correctamente" y en realidad el servidor la rechazo (por
            ejemplo porque la partida todavia no se habia creado, o
            la accion no estaba permitida en la fase exacta de ese
            instante): sin esto, ese rechazo solo se notaba despues,
            de forma silenciosa, en el siguiente estado recibido por
            polling.

            El servidor atiende los mensajes de un mismo cliente uno a
            la vez y en orden (TCP + un hilo de escucha por cliente),
            asi que el primer mensaje nuevo que llegue despues de
            enviar esta accion es, en la practica, su respuesta.

        Entradas:
            accion (str): Accion definida en el protocolo.
            tiempo_espera (float): Segundos maximos a esperar la
                respuesta antes de devolver un resultado optimista.
            **datos: Datos necesarios para la accion.

        Salidas:
            tuple[bool, str]: Exito real informado por el servidor
            (o del envio, si no hubo respuesta a tiempo) y mensaje
            descriptivo.

        Restricciones:
            - El cliente debe estar conectado.
            - accion debe ser valida dentro del protocolo.
        """
        if not self.conectado or self.conexion is None:
            return False, "No hay conexion activa con el servidor."

        evento_respuesta = threading.Event()
        resultado = {}

        def capturar_respuesta(mensaje):
            # Solo nos interesan las respuestas directas a una accion
            # (tipo "resultado", que el servidor usa tanto para exito
            # como para error). Los mensajes tipo "estado" son
            # broadcasts que el servidor manda a todos los clientes
            # (incluyendo los que dispara su propio bucle de combate
            # en otro hilo) y no son la respuesta a esta accion en
            # particular; si los acepataramos aqui, podriamos quedarnos
            # con un mensaje que no tiene relacion con la compra que
            # se esta esperando confirmar.
            """
            Descripcion:
                Ejecuta la logica correspondiente a capturar respuesta
                dentro del flujo del juego.
            
            Entradas:
                mensaje (object): Valor recibido por la funcion.
            
            Salidas:
                bool: True si la condicion evaluada se cumple, False en
                caso contrario.
            
            Restricciones:
                - Los parametros recibidos deben respetar el tipo y el
                formato esperado por la funcion.
                - Requiere una conexion, sala o mensaje valido cuando la
                operacion dependa de la red.
            """
            if mensaje.get("tipo") != "resultado":
                return False
            if not evento_respuesta.is_set():
                resultado["exito"] = mensaje.get("exito", True)
                resultado["mensaje"] = mensaje.get("mensaje", "")
                evento_respuesta.set()
            return True

        with self.bloqueo:
            self._esperas_respuesta.append(capturar_respuesta)

        try:
            mensaje = crear_mensaje(accion, **datos)
            enviar_mensaje(self.conexion, mensaje)
        except (OSError, ErrorProtocolo) as error:
            with self.bloqueo:
                if capturar_respuesta in self._esperas_respuesta:
                    self._esperas_respuesta.remove(capturar_respuesta)
            return False, str(error)

        llego_a_tiempo = evento_respuesta.wait(timeout=tiempo_espera)

        with self.bloqueo:
            if capturar_respuesta in self._esperas_respuesta:
                self._esperas_respuesta.remove(capturar_respuesta)

        if not llego_a_tiempo:
            # El servidor no respondio a tiempo (lag de red, etc.):
            # devolvemos un resultado optimista en vez de bloquear la
            # interfaz indefinidamente, igual que el comportamiento
            # anterior de enviar_accion.
            return True, "Accion enviada (sin confirmación del servidor todavía)."

        return bool(resultado.get("exito", True)), resultado.get("mensaje", "")

    def comprar_torre(self, tipo_torre, fila, columna):
        """
        Descripcion:
            Envia al servidor la solicitud para comprar una torre y
            espera la confirmacion real antes de informar el
            resultado, para que la interfaz nunca diga "comprada"
            cuando el servidor en realidad la rechazo.

        Entradas:
            tipo_torre (str): Tipo de torre a comprar.
            fila (int): Fila de colocacion.
            columna (int): Columna de colocacion.

        Salidas:
            tuple[bool, str]: Exito real informado por el servidor y
            mensaje descriptivo.

        Restricciones:
            - Solo funcionara en el servidor si este cliente es defensor.
        """
        return self.enviar_accion_y_esperar(
            ACCION_COMPRAR_TORRE,
            tipo_torre=tipo_torre,
            fila=fila,
            columna=columna,
        )

    def comprar_muro(self, fila, columna):
        """
        Descripcion:
            Envia al servidor la solicitud para comprar un muro y
            espera la confirmacion real antes de informar el
            resultado.

        Entradas:
            fila (int): Fila de colocacion.
            columna (int): Columna de colocacion.

        Salidas:
            tuple[bool, str]: Exito real informado por el servidor y
            mensaje descriptivo.

        Restricciones:
            - Solo funcionara en el servidor si este cliente es defensor.
        """
        return self.enviar_accion_y_esperar(ACCION_COMPRAR_MURO, fila=fila, columna=columna)

    def comprar_unidad(self, tipo_unidad, fila, columna):
        """
        Descripcion:
            Envia al servidor la solicitud para comprar una unidad y
            espera la confirmacion real antes de informar el
            resultado. Esto es lo que evita que, justo en el primer
            turno (cuando el atacante puede hacer clic antes de que
            el servidor termine de emparejar a ambos jugadores y crear
            la partida), la interfaz diga "comprada correctamente"
            mientras el servidor en realidad la rechazo en silencio.

        Entradas:
            tipo_unidad (str): Tipo de unidad a comprar.
            fila (int): Fila de colocacion.
            columna (int): Columna de colocacion.

        Salidas:
            tuple[bool, str]: Exito real informado por el servidor y
            mensaje descriptivo.

        Restricciones:
            - Solo funcionara en el servidor si este cliente es atacante.
        """
        return self.enviar_accion_y_esperar(
            ACCION_COMPRAR_UNIDAD,
            tipo_unidad=tipo_unidad,
            fila=fila,
            columna=columna,
        )

    def usar_habilidad_especial(self):
        """
        Descripcion:
            Envia al servidor la solicitud para activar la habilidad
            especial de la facción de este cliente. El servidor
            determina cual habilidad corresponde según la facción que
            este rol eligió en el lobby; el costo y el daño los
            calcula siempre la clase Partida, nunca la interfaz.

        Entradas:
            Ninguna.

        Salidas:
            tuple[bool, str]: Exito del envio y mensaje descriptivo.

        Restricciones:
            - Debe existir una partida creada en el servidor.
            - El rol debe tener dinero suficiente y la habilidad debe
              estar fuera de su tiempo de enfriamiento.
        """
        return self.enviar_accion(ACCION_USAR_HABILIDAD_ESPECIAL)


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
        
        Entradas:
            numero_ronda (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
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
                "segundos_restantes_preparacion": (
                    self.ultimo_estado.get("segundos_restantes_preparacion")
                    if isinstance(self.ultimo_estado, dict)
                    else None
                ),
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
        """
        Descripcion:
            Ejecuta la logica correspondiente a imprimir mensaje dentro
            del flujo del juego.
        
        Entradas:
            mensaje (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
        """
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
