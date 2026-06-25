"""
Descripcion:
    Servidor para partidas multijugador en tiempo real de "Defensa y
    Asalto de Base". El servidor mantiene la unica partida oficial y
    las computadoras de los jugadores se conectan como clientes para
    enviar acciones.

    Este archivo no usa Tkinter. Se comunica con la logica del juego
    mediante la clase Partida y envia estados por sockets usando JSON.
"""

import os
import socket
import sys
import threading
import time

RUTA_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUTA_LOGICA = os.path.join(RUTA_PROYECTO, "Logica")
RUTA_RED = os.path.join(RUTA_PROYECTO, "Red")

if RUTA_LOGICA not in sys.path:
    sys.path.append(RUTA_LOGICA)

if RUTA_RED not in sys.path:
    sys.path.append(RUTA_RED)

from partida import crear_partida
from protocolo import (
    ACCION_COMPRAR_MURO,
    ACCION_COMPRAR_TORRE,
    ACCION_COMPRAR_UNIDAD,
    ACCION_EJECUTAR_COMBATE,
    ACCION_INICIAR_COMBATE,
    ACCION_OBTENER_ESTADO,
    ACCION_PAUSAR_COMBATE,
    ACCION_SALIR,
    ACCION_UNIRSE,
    ErrorProtocolo,
    ROL_ATACANTE,
    ROL_DEFENSOR,
    TIPO_CONEXION,
    TIPO_ERROR,
    TIPO_ESTADO,
    TIPO_EVENTO,
    TIPO_RESULTADO,
    crear_respuesta,
    enviar_mensaje,
    obtener_accion,
    obtener_entero,
    obtener_texto,
    recibir_mensaje,
)

HOST_PREDETERMINADO = "0.0.0.0"
PUERTO_PREDETERMINADO = 5000
INTERVALO_COMBATE_SEGUNDOS = 1.0
MAXIMO_JUGADORES = 2


class ClienteConectado:
    """
    Descripcion:
        Representa un cliente conectado al servidor. Guarda su socket,
        direccion, usuario, rol y archivo de lectura.

    Entradas:
        conexion (socket): Conexion TCP con el cliente.
        direccion (tuple): Direccion remota del cliente.
        usuario (str): Nombre de usuario del jugador conectado.
        rol (str): Rol asignado dentro de la partida.

    Salidas:
        No retorna nada. Construye un objeto con los datos del cliente.

    Restricciones:
        - rol debe ser "defensor" o "atacante".
        - conexion debe estar abierta al crear el objeto.
    """

    def __init__(self, conexion, direccion, usuario, rol, archivo_lectura=None):
        self.conexion = conexion
        self.direccion = direccion
        self.usuario = usuario
        self.rol = rol
        if archivo_lectura is None:
            self.archivo_lectura = conexion.makefile("r", encoding="utf-8")
        else:
            self.archivo_lectura = archivo_lectura
        self.conectado = True

    def cerrar(self):
        """
        Descripcion:
            Cierra de forma segura los recursos de red del cliente.

        Entradas:
            Ninguna.

        Salidas:
            None: Cierra el archivo de lectura y el socket.

        Restricciones:
            Ninguna.
        """
        self.conectado = False

        try:
            self.archivo_lectura.close()
        except OSError:
            pass

        try:
            self.conexion.close()
        except OSError:
            pass


class ServidorPartida:
    """
    Descripcion:
        Administra el servidor TCP de una partida. Acepta dos clientes,
        asigna roles, crea la partida y procesa acciones en tiempo real.

    Entradas:
        host (str): Direccion donde escuchara el servidor. Por defecto
            "0.0.0.0" para aceptar conexiones de la red local.
        puerto (int): Puerto TCP usado por el servidor.
        intervalo_combate (float): Segundos entre cada avance de
            combate automatico cuando el combate esta activo.

    Salidas:
        No retorna nada. Construye un servidor listo para iniciarse.

    Restricciones:
        - puerto debe estar libre.
        - Solo se aceptan dos jugadores por partida.
        - El servidor debe ejecutarse en una computadora accesible por
          la otra dentro de la misma red.
    """

    def __init__(self, host=HOST_PREDETERMINADO, puerto=PUERTO_PREDETERMINADO,
                 intervalo_combate=INTERVALO_COMBATE_SEGUNDOS):
        self.host = host
        self.puerto = puerto
        self.intervalo_combate = intervalo_combate
        self.socket_servidor = None
        self.servidor_activo = False
        self.combate_activo = False
        self.partida = None
        self.clientes_por_rol = {
            ROL_DEFENSOR: None,
            ROL_ATACANTE: None,
        }
        self.bloqueo = threading.Lock()

    def iniciar(self):
        """
        Descripcion:
            Inicia el servidor, queda escuchando conexiones y crea un
            hilo para cada cliente conectado.

        Entradas:
            Ninguna.

        Salidas:
            None: Mantiene el servidor activo hasta que se cierre el
            proceso o se llame detener().

        Restricciones:
            - Debe ejecutarse antes de iniciar los clientes.
            - Solo una instancia debe usar el mismo puerto a la vez.
        """
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_servidor.bind((self.host, self.puerto))
        self.socket_servidor.listen(MAXIMO_JUGADORES)
        self.servidor_activo = True

        print(f"Servidor iniciado en {self._obtener_ip_local()}:{self.puerto}")
        print("Esperando jugadores...")

        hilo_combate = threading.Thread(target=self._bucle_combate, daemon=True)
        hilo_combate.start()

        try:
            while self.servidor_activo:
                conexion, direccion = self.socket_servidor.accept()
                hilo_cliente = threading.Thread(
                    target=self._preparar_cliente,
                    args=(conexion, direccion),
                    daemon=True,
                )
                hilo_cliente.start()
        except OSError:
            pass
        finally:
            self.detener()

    def detener(self):
        """
        Descripcion:
            Detiene el servidor y cierra todas las conexiones activas.

        Entradas:
            Ninguna.

        Salidas:
            None: Modifica el estado interno y cierra sockets.

        Restricciones:
            Ninguna.
        """
        self.servidor_activo = False
        self.combate_activo = False

        for cliente in list(self.clientes_por_rol.values()):
            if cliente is not None:
                cliente.cerrar()

        if self.socket_servidor is not None:
            try:
                self.socket_servidor.close()
            except OSError:
                pass

    def _obtener_ip_local(self):
        """
        Descripcion:
            Intenta obtener una IP local util para que el otro jugador
            se conecte desde otra computadora.

        Entradas:
            Ninguna.

        Salidas:
            str: IP local aproximada del equipo servidor.

        Restricciones:
            - Si no hay red disponible, devuelve "127.0.0.1".
        """
        try:
            conexion_temporal = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            conexion_temporal.connect(("8.8.8.8", 80))
            ip_local = conexion_temporal.getsockname()[0]
            conexion_temporal.close()
            return ip_local
        except OSError:
            return "127.0.0.1"

    def _preparar_cliente(self, conexion, direccion):
        """
        Descripcion:
            Recibe el primer mensaje de un cliente, valida su usuario,
            le asigna un rol y lo registra en el servidor.

        Entradas:
            conexion (socket): Socket aceptado.
            direccion (tuple): Direccion del cliente.

        Salidas:
            None: Registra el cliente y crea su hilo de escucha.

        Restricciones:
            - El primer mensaje debe ser la accion "unirse".
        """
        archivo_lectura = conexion.makefile("r", encoding="utf-8")

        try:
            mensaje_inicial = recibir_mensaje(archivo_lectura)
            if mensaje_inicial is None:
                conexion.close()
                return

            accion = obtener_accion(mensaje_inicial)
            if accion != ACCION_UNIRSE:
                enviar_mensaje(
                    conexion,
                    crear_respuesta(TIPO_ERROR, False, "El primer mensaje debe ser unirse."),
                )
                conexion.close()
                return

            usuario = obtener_texto(mensaje_inicial, "usuario")
            rol_solicitado = obtener_texto(mensaje_inicial, "rol", obligatorio=False)

            with self.bloqueo:
                rol_asignado = self._asignar_rol(usuario, rol_solicitado)

                if rol_asignado is None:
                    enviar_mensaje(
                        conexion,
                        crear_respuesta(TIPO_ERROR, False, "La sala ya tiene dos jugadores."),
                    )
                    conexion.close()
                    return

                cliente = ClienteConectado(
                    conexion, direccion, usuario, rol_asignado, archivo_lectura
                )
                self.clientes_por_rol[rol_asignado] = cliente

            enviar_mensaje(
                cliente.conexion,
                crear_respuesta(
                    TIPO_CONEXION,
                    True,
                    f"Conectado como {rol_asignado}.",
                    datos={"rol": rol_asignado, "usuario": usuario},
                ),
            )

            print(f"{usuario} conectado como {rol_asignado} desde {direccion}.")
            self._crear_partida_si_es_posible()
            self._enviar_estado_a_todos("Jugador conectado.")
            self._escuchar_cliente(cliente)

        except (ErrorProtocolo, OSError) as error:
            try:
                enviar_mensaje(conexion, crear_respuesta(TIPO_ERROR, False, str(error)))
            except OSError:
                pass
            try:
                archivo_lectura.close()
                conexion.close()
            except OSError:
                pass

    def _asignar_rol(self, usuario, rol_solicitado=""):
        """
        Descripcion:
            Asigna un rol disponible a un usuario. Si el usuario pide
            un rol libre se respeta; si no pide rol, se asigna el
            primero disponible.

        Entradas:
            usuario (str): Nombre del jugador que se conecta.
            rol_solicitado (str): Rol pedido por el cliente. Puede
                estar vacio.

        Salidas:
            str: Rol asignado.
            None: Si no hay cupo o el usuario ya esta conectado.

        Restricciones:
            - No permite repetir el mismo usuario en ambos roles.
        """
        for cliente in self.clientes_por_rol.values():
            if cliente is not None and cliente.usuario == usuario:
                return None

        rol_solicitado = str(rol_solicitado).strip().lower()
        if rol_solicitado in self.clientes_por_rol:
            if self.clientes_por_rol[rol_solicitado] is None:
                return rol_solicitado
            return None

        if self.clientes_por_rol[ROL_DEFENSOR] is None:
            return ROL_DEFENSOR

        if self.clientes_por_rol[ROL_ATACANTE] is None:
            return ROL_ATACANTE

        return None

    def _crear_partida_si_es_posible(self):
        """
        Descripcion:
            Crea la partida cuando ya existen defensor y atacante
            conectados.

        Entradas:
            Ninguna.

        Salidas:
            None: Modifica self.partida si ambos jugadores estan
            conectados.

        Restricciones:
            - Solo crea la partida una vez.
        """
        with self.bloqueo:
            defensor = self.clientes_por_rol[ROL_DEFENSOR]
            atacante = self.clientes_por_rol[ROL_ATACANTE]

            if self.partida is None and defensor is not None and atacante is not None:
                self.partida = crear_partida(defensor.usuario, atacante.usuario)
                print("Partida creada correctamente.")

    def _escuchar_cliente(self, cliente):
        """
        Descripcion:
            Escucha constantemente los mensajes de un cliente y los
            manda a procesar.

        Entradas:
            cliente (ClienteConectado): Cliente que se desea escuchar.

        Salidas:
            None: Procesa mensajes hasta que el cliente se desconecte.

        Restricciones:
            - cliente debe estar conectado.
        """
        while self.servidor_activo and cliente.conectado:
            try:
                mensaje = recibir_mensaje(cliente.archivo_lectura)
                if mensaje is None:
                    break

                self._procesar_mensaje(cliente, mensaje)

            except ErrorProtocolo as error:
                self._enviar_a_cliente(
                    cliente,
                    crear_respuesta(TIPO_ERROR, False, str(error)),
                )
            except OSError:
                break

        self._desconectar_cliente(cliente)

    def _procesar_mensaje(self, cliente, mensaje):
        """
        Descripcion:
            Procesa una accion enviada por un cliente y ejecuta la
            funcion correspondiente en la partida oficial.

        Entradas:
            cliente (ClienteConectado): Cliente que envio la accion.
            mensaje (dict): Mensaje recibido por red.

        Salidas:
            None: Ejecuta acciones y envia respuestas por red.

        Restricciones:
            - Las acciones defensivas solo puede enviarlas el defensor.
            - Las acciones atacantes solo puede enviarlas el atacante.
        """
        accion = obtener_accion(mensaje)

        if accion == ACCION_SALIR:
            cliente.cerrar()
            return

        if accion == ACCION_OBTENER_ESTADO:
            self._enviar_estado_a_cliente(cliente, "Estado actual enviado.")
            return

        if self.partida is None:
            self._enviar_a_cliente(
                cliente,
                crear_respuesta(
                    TIPO_RESULTADO,
                    False,
                    "Aun falta que se conecte el segundo jugador.",
                ),
            )
            return

        with self.bloqueo:
            if accion == ACCION_COMPRAR_TORRE:
                self._validar_rol(cliente, ROL_DEFENSOR)
                tipo_torre = obtener_texto(mensaje, "tipo_torre")
                fila = obtener_entero(mensaje, "fila")
                columna = obtener_entero(mensaje, "columna")
                exito, texto = self.partida.comprar_torre(tipo_torre, fila, columna)

            elif accion == ACCION_COMPRAR_MURO:
                self._validar_rol(cliente, ROL_DEFENSOR)
                fila = obtener_entero(mensaje, "fila")
                columna = obtener_entero(mensaje, "columna")
                exito, texto = self.partida.comprar_muro(fila, columna)

            elif accion == ACCION_COMPRAR_UNIDAD:
                self._validar_rol(cliente, ROL_ATACANTE)
                tipo_unidad = obtener_texto(mensaje, "tipo_unidad")
                fila = obtener_entero(mensaje, "fila")
                columna = obtener_entero(mensaje, "columna")
                exito, texto = self.partida.comprar_unidad(tipo_unidad, fila, columna)

            elif accion == ACCION_EJECUTAR_COMBATE:
                resultado = self.partida.ejecutar_combate()
                exito = True
                texto = "Turno de combate ejecutado."
                self._enviar_resultado_y_estado(exito, texto, resultado)
                return

            elif accion == ACCION_INICIAR_COMBATE:
                self.combate_activo = True
                exito = True
                texto = "Combate en tiempo real iniciado."

            elif accion == ACCION_PAUSAR_COMBATE:
                self.combate_activo = False
                exito = True
                texto = "Combate pausado."

            else:
                exito = False
                texto = "Accion no implementada por el servidor."

            estado = self.partida.obtener_estado_partida()

        respuesta = crear_respuesta(
            TIPO_RESULTADO,
            exito,
            texto,
            estado=estado,
            datos={"accion": accion, "rol": cliente.rol},
        )
        self._enviar_a_cliente(cliente, respuesta)
        self._enviar_estado_a_todos(texto)

    def _validar_rol(self, cliente, rol_requerido):
        """
        Descripcion:
            Valida que un cliente tenga permiso para ejecutar una
            accion segun su rol.

        Entradas:
            cliente (ClienteConectado): Cliente que intenta actuar.
            rol_requerido (str): Rol necesario para la accion.

        Salidas:
            None: No modifica datos si el rol es correcto.

        Restricciones:
            - Lanza ErrorProtocolo si el rol no coincide.
        """
        if cliente.rol != rol_requerido:
            raise ErrorProtocolo(f"Esta accion solo la puede hacer el {rol_requerido}.")

    def _bucle_combate(self):
        """
        Descripcion:
            Ejecuta automaticamente turnos de combate cada cierto
            intervalo mientras el combate en tiempo real este activo.

        Entradas:
            Ninguna.

        Salidas:
            None: Modifica la partida y envia estados a los clientes.

        Restricciones:
            - Requiere que exista una partida creada.
        """
        while True:
            time.sleep(self.intervalo_combate)

            if not self.servidor_activo:
                break

            if not self.combate_activo:
                continue

            with self.bloqueo:
                if self.partida is None or self.partida.partida_finalizada:
                    self.combate_activo = False
                    continue

                resultado = self.partida.ejecutar_combate()
                estado = self.partida.obtener_estado_partida()

                if resultado.get("ronda_finalizada") or estado.get("partida_finalizada"):
                    self.combate_activo = False

            self._enviar_a_todos(
                crear_respuesta(
                    TIPO_ESTADO,
                    True,
                    "Combate actualizado.",
                    estado=estado,
                    datos={"resultado_combate": resultado, "combate_activo": self.combate_activo},
                )
            )

    def _enviar_resultado_y_estado(self, exito, mensaje, resultado):
        """
        Descripcion:
            Envia a todos los clientes una respuesta con el resultado
            de un turno puntual de combate.

        Entradas:
            exito (bool): Indica si la accion fue exitosa.
            mensaje (str): Mensaje descriptivo.
            resultado (dict): Resultado devuelto por ejecutar_combate.

        Salidas:
            None: Envia datos por red.

        Restricciones:
            - self.partida debe existir.
        """
        estado = self.partida.obtener_estado_partida()
        self._enviar_a_todos(
            crear_respuesta(
                TIPO_RESULTADO,
                exito,
                mensaje,
                estado=estado,
                datos={"resultado_combate": resultado},
            )
        )

    def _enviar_estado_a_cliente(self, cliente, mensaje):
        """
        Descripcion:
            Envia el estado actual de la partida a un solo cliente.

        Entradas:
            cliente (ClienteConectado): Cliente destino.
            mensaje (str): Mensaje descriptivo.

        Salidas:
            None: Envia datos por red.

        Restricciones:
            Ninguna.
        """
        estado = None
        if self.partida is not None:
            estado = self.partida.obtener_estado_partida()

        self._enviar_a_cliente(
            cliente,
            crear_respuesta(TIPO_ESTADO, True, mensaje, estado=estado),
        )

    def _enviar_estado_a_todos(self, mensaje):
        """
        Descripcion:
            Envia el estado actual de la partida a todos los clientes
            conectados.

        Entradas:
            mensaje (str): Mensaje descriptivo.

        Salidas:
            None: Envia datos por red.

        Restricciones:
            Ninguna.
        """
        estado = None
        if self.partida is not None:
            estado = self.partida.obtener_estado_partida()

        self._enviar_a_todos(
            crear_respuesta(
                TIPO_ESTADO,
                True,
                mensaje,
                estado=estado,
                datos={"combate_activo": self.combate_activo},
            )
        )

    def _enviar_a_cliente(self, cliente, mensaje):
        """
        Descripcion:
            Envia un mensaje a un cliente especifico.

        Entradas:
            cliente (ClienteConectado): Cliente destino.
            mensaje (dict): Mensaje que se desea enviar.

        Salidas:
            None: Escribe en el socket del cliente.

        Restricciones:
            - Si el cliente esta desconectado, el envio puede fallar.
        """
        try:
            enviar_mensaje(cliente.conexion, mensaje)
        except OSError:
            cliente.cerrar()

    def _enviar_a_todos(self, mensaje):
        """
        Descripcion:
            Envia un mensaje a todos los clientes conectados.

        Entradas:
            mensaje (dict): Mensaje que se desea enviar.

        Salidas:
            None: Envia datos por red a cada cliente activo.

        Restricciones:
            Ninguna.
        """
        clientes = list(self.clientes_por_rol.values())
        for cliente in clientes:
            if cliente is not None and cliente.conectado:
                self._enviar_a_cliente(cliente, mensaje)

    def _desconectar_cliente(self, cliente):
        """
        Descripcion:
            Elimina un cliente del registro del servidor y avisa al
            otro jugador si queda conectado.

        Entradas:
            cliente (ClienteConectado): Cliente que se desconecto.

        Salidas:
            None: Actualiza clientes_por_rol.

        Restricciones:
            Ninguna.
        """
        cliente.cerrar()

        with self.bloqueo:
            if self.clientes_por_rol.get(cliente.rol) is cliente:
                self.clientes_por_rol[cliente.rol] = None
            self.combate_activo = False

        print(f"{cliente.usuario} se desconecto.")
        self._enviar_a_todos(
            crear_respuesta(
                TIPO_EVENTO,
                True,
                f"{cliente.usuario} se desconecto. Combate pausado.",
                datos={"combate_activo": False},
            )
        )


def iniciar_servidor(host=HOST_PREDETERMINADO, puerto=PUERTO_PREDETERMINADO):
    """
    Descripcion:
        Funcion de conveniencia para iniciar el servidor desde otro
        archivo o desde la terminal.

    Entradas:
        host (str): Direccion donde escuchara el servidor.
        puerto (int): Puerto TCP que usara el servidor.

    Salidas:
        None: Ejecuta el servidor.

    Restricciones:
        - El puerto debe estar disponible.
    """
    servidor = ServidorPartida(host, puerto)
    servidor.iniciar()


if __name__ == "__main__":
    puerto = PUERTO_PREDETERMINADO
    if len(sys.argv) >= 2:
        puerto = int(sys.argv[1])

    iniciar_servidor(puerto=puerto)
