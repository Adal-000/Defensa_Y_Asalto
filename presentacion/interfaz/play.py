#=======================================#
# Archivo para jugar
#=======================================#

import queue
import socket
import threading
import tkinter as tk
from tkinter import messagebox

from aplicacion import app
from infraestructura.red.cliente import ClientePartida, PUERTO_PREDETERMINADO
from infraestructura.red.servidor import ServidorPartida


ACCION_CAMBIAR_FACCION = "cambiar_faccion"
ACCION_ELEGIR_FACCION = "elegir_faccion"
ACCION_LISTO_LOBBY = "listo_lobby"
COLOR_FONDO = "#f0f0f0"
COLOR_PANEL = "#ffffff"
COLOR_BORDE = "#9a9a9a"
COLOR_SELECCION = "#b7d7ff"
COLOR_LISTO = "#1f8f3a"
COLOR_ALERTA = "#c40000"
COLOR_AYUDA = "#fff3bf"

LOBBY_LOCAL = {}

DATOS_PARTIDA = {
    "rol": "",
    "usuario": "",
    "faccion": "",
    "puerto": "",
    "modo": "red"
}


def obtener_datos_partida():
    """
    Descripcion:
        Devuelve los datos básicos de la partida seleccionada. Se usa
        desde root.py o desde el mapa.
    
    Entradas:
        Ninguna.
    
    Salidas:
        object: Resultado calculado o recuperado por la operacion.
    
    Restricciones:
        - Requiere que los widgets, ventanas o callbacks usados por la
        interfaz existan antes de ejecutarse.
    """
    return DATOS_PARTIDA.copy()


class AdaptadorClienteTkinter:
    """
    Descripcion:
        Encapsula el cliente de red para que Tkinter procese los
        mensajes recibidos desde el hilo de escucha usando una cola.
    
    Entradas:
        Ninguna.
    
    Salidas:
        No retorna nada. Define la clase AdaptadorClienteTkinter para
        ser instanciada o utilizada por otros modulos.
    
    Restricciones:
        - Requiere que los widgets, ventanas o callbacks usados por la
        interfaz existan antes de ejecutarse.
    """

    def __init__(self, cola_mensajes):
        """
        Descripcion:
            Inicializa la instancia y asigna los valores necesarios para
            que el objeto pueda utilizarse correctamente.
        
        Entradas:
            cola_mensajes (object): Valor recibido por la funcion.
        
        Salidas:
            None: Inicializa los atributos de la instancia.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        self.cola_mensajes = cola_mensajes
        self.cliente = ClientePartida(callback_mensaje=self._recibir_mensaje)

    def _recibir_mensaje(self, mensaje):
        """
        Descripcion:
            Ejecuta la logica correspondiente a  recibir mensaje dentro
            del flujo del juego.
        
        Entradas:
            mensaje (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        self.cola_mensajes.put(mensaje)

    def conectar(self, host, usuario, rol, puerto):
        """
        Descripcion:
            Ejecuta la logica correspondiente a conectar dentro del
            flujo del juego.
        
        Entradas:
            host (object): Valor recibido por la funcion.
            usuario (object): Valor recibido por la funcion.
            rol (object): Valor recibido por la funcion.
            puerto (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        return self.cliente.conectar(host, usuario, puerto=puerto, rol=rol)

    def cerrar(self):
        """
        Descripcion:
            Ejecuta la logica correspondiente a cerrar dentro del flujo
            del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        self.cliente.cerrar()


def play(root, GoMain, GoMapa, cerrar_todo, configurar_ventana, obtener_usuario_actual):
    """
    Descripcion:
        Crea una sola ventana de sala en red. Maneja correctamente el
        ciclo de vida de ventanas, servidor y cliente según quién creó
        la sala y quién se unió. Flujo al CREAR sala y pulsar Volver: -
        Si nadie se unió: cierra servidor, cierra cliente, vuelve a
        main. - Si había alguien unido: cierra servidor (lo expulsa),
        ambos vuelven a main. El que se unió recibe aviso de sala
        cerrada. Flujo al UNIRSE a sala y pulsar Volver: - El cliente se
        desconecta del servidor. - El creador recibe aviso de que el
        contrincante salió, se le quita la facción elegida si tenía una
        y vuelve al estado de espera (como si nadie se hubiera unido
        todavía).
    
    Entradas:
        root (object): Valor recibido por la funcion.
        GoMain (object): Valor recibido por la funcion.
        GoMapa (object): Valor recibido por la funcion.
        cerrar_todo (object): Valor recibido por la funcion.
        configurar_ventana (object): Valor recibido por la funcion.
        obtener_usuario_actual (object): Valor recibido por la funcion.
    
    Salidas:
        None: Ejecuta la accion y puede modificar el estado interno, la
        interfaz o los datos relacionados.
    
    Restricciones:
        - Los parametros recibidos deben respetar el tipo y el formato
        esperado por la funcion.
        - Requiere que los widgets, ventanas o callbacks usados por la
        interfaz existan antes de ejecutarse.
    """

    window2 = tk.Toplevel(root)
    configurar_ventana(window2, "Play en red")
    window2.configure(bg=COLOR_FONDO)

    cola_mensajes = queue.Queue()
    adaptador = AdaptadorClienteTkinter(cola_mensajes)
    servidor_local = {"instancia": None, "hilo": None}

    # cerrando: flag principal para evitar dobles cierres
    # after_id / after_conexion_id / retorno_id: IDs de callbacks pendientes
    # conectando: flag para evitar doble click en Continuar
    control_ventana = {
        "cerrando": False,
        "after_id": None,
        "after_conexion_id": None,
        "retorno_id": None,
        "conectando": False,
    }

    preferencias = app.obtener_configuracion()

    estado_red = {
        "conectado": False,
        "jugadores_conectados": 0,
        "rol": "",
        "puerto": PUERTO_PREDETERMINADO,
        "usuario": obtener_usuario_actual() or "Invitado",
        "en_espera": False,
        "sala_estuvo_completa": False,
    }

    catalogo_facciones = app.obtener_catalogo_facciones()
    imagenes_facciones = {}
    datos_facciones_por_nombre = {faccion["nombre"]: faccion for faccion in catalogo_facciones}
    faccion_temporal = tk.StringVar(value="")
    facciones_ocupadas = {}
    listos_remotos = set()
    faccion_confirmada = tk.StringVar(value="")
    seleccion_bloqueada = tk.BooleanVar(value=False)
    listo_para_mapa = tk.BooleanVar(value=False)

    # ------------------------------------------------------------------ #
    # Utilidades de red                                                    #
    # ------------------------------------------------------------------ #

    def obtener_ip_local_visible():
        """
        Descripcion:
            Obtiene la informacion correspondiente a obtener ip local
            visible para que otras partes del programa puedan
            utilizarla.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        try:
            socket_prueba = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_prueba.connect(("8.8.8.8", 80))
            ip_local = socket_prueba.getsockname()[0]
            socket_prueba.close()
            return ip_local
        except OSError:
            return "127.0.0.1"

    def obtener_clave_sala():
        """
        Descripcion:
            Obtiene la informacion correspondiente a obtener clave sala
            para que otras partes del programa puedan utilizarla.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        return str(estado_red["puerto"])

    def obtener_datos_sala():
        """
        Descripcion:
            Obtiene la informacion correspondiente a obtener datos sala
            para que otras partes del programa puedan utilizarla.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        clave = obtener_clave_sala()
        if clave not in LOBBY_LOCAL:
            LOBBY_LOCAL[clave] = {"facciones": {}, "listos": set()}
        return LOBBY_LOCAL[clave]

    def limpiar_sala_local():
        """
        Descripcion:
            Ejecuta la logica correspondiente a limpiar sala local
            dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        clave = obtener_clave_sala()
        LOBBY_LOCAL.pop(clave, None)

    def registrar_estado_local(listo=False):
        """
        Descripcion:
            Ejecuta la logica correspondiente a registrar estado local
            dentro del flujo del juego.
        
        Entradas:
            listo (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not estado_red["conectado"] or not estado_red["rol"]:
            return
        sala = obtener_datos_sala()
        if faccion_confirmada.get():
            sala["facciones"][estado_red["rol"]] = faccion_confirmada.get()
        elif estado_red["rol"] in sala["facciones"]:
            del sala["facciones"][estado_red["rol"]]
        if listo:
            sala["listos"].add(estado_red["rol"])
        else:
            sala["listos"].discard(estado_red["rol"])

    def enviar_accion_lobby(accion, **datos):
        """
        Descripcion:
            Envia la informacion o accion correspondiente a enviar
            accion lobby.
        
        Entradas:
            accion (object): Valor recibido por la funcion.
            **datos (object): Valor recibido por la funcion. Argumentos
            nombrados adicionales.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if adaptador.cliente.conectado:
            adaptador.cliente.enviar_accion(accion, **datos)

    def sincronizar_lobby_remoto(datos):
        """
        Descripcion:
            Sincroniza los datos relacionados con sincronizar lobby
            remoto entre la interfaz, la logica o la red.
        
        Entradas:
            datos (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        facciones_ocupadas.clear()
        facciones_ocupadas.update(datos.get("facciones_lobby", {}))
        listos_remotos.clear()
        listos_remotos.update(datos.get("listos_lobby", []))
        sala = obtener_datos_sala()
        sala["facciones"] = facciones_ocupadas.copy()
        sala["listos"] = set(listos_remotos)

    def hay_dos_jugadores():
        """
        Descripcion:
            Ejecuta la logica correspondiente a hay dos jugadores dentro
            del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            bool: True si la condicion evaluada se cumple, False en caso
            contrario.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        return estado_red["jugadores_conectados"] >= 2

    def roles_necesarios_listos():
        """
        Descripcion:
            Ejecuta la logica correspondiente a roles necesarios listos
            dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        sala = obtener_datos_sala()
        return {"defensor", "atacante"}.issubset(sala["listos"])

    def facciones_validas_en_sala():
        """
        Descripcion:
            Ejecuta la logica correspondiente a facciones validas en
            sala dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            bool: True si la condicion evaluada se cumple, False en caso
            contrario.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        sala = obtener_datos_sala()
        facciones = sala["facciones"]
        if not {"defensor", "atacante"}.issubset(facciones):
            return False
        return facciones["defensor"] != facciones["atacante"]

    def faccion_esta_ocupada_por_otro(nombre_faccion):
        """
        Descripcion:
            Ejecuta la logica correspondiente a faccion esta ocupada por
            otro dentro del flujo del juego.
        
        Entradas:
            nombre_faccion (object): Valor recibido por la funcion.
        
        Salidas:
            bool: True si la condicion evaluada se cumple, False en caso
            contrario.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        sala = obtener_datos_sala()
        for rol, faccion in sala["facciones"].items():
            if rol != estado_red["rol"] and faccion == nombre_faccion:
                return True
        return False

    # ------------------------------------------------------------------ #
    # Ciclo de vida de la ventana                                          #
    # ------------------------------------------------------------------ #

    def _cancelar_afters():
        """
        Descripcion:
            Cancela todos los callbacks after pendientes.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        for clave in ("after_id", "after_conexion_id", "retorno_id"):
            if control_ventana[clave] is not None:
                try:
                    window2.after_cancel(control_ventana[clave])
                except tk.TclError:
                    pass
                control_ventana[clave] = None

    def _vaciar_cola():
        """
        Descripcion:
            Ejecuta la logica correspondiente a  vaciar cola dentro del
            flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        while not cola_mensajes.empty():
            try:
                cola_mensajes.get_nowait()
            except queue.Empty:
                break

    def _cerrar_cliente():
        """
        Descripcion:
            Desconecta el cliente (envía SALIR al servidor).
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        adaptador.cliente.callback_mensaje = None
        adaptador.cerrar()

    def _detener_servidor():
        """
        Descripcion:
            Detiene el servidor local si existe.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        servidor = servidor_local["instancia"]
        hilo = servidor_local["hilo"]
        servidor_local["instancia"] = None
        servidor_local["hilo"] = None
        if servidor is not None:
            servidor.detener()
        if hilo is not None and hilo.is_alive() and hilo is not threading.current_thread():
            hilo.join(timeout=0.3)

    def _destruir_ventana():
        """
        Descripcion:
            Ejecuta la logica correspondiente a  destruir ventana dentro
            del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        try:
            if window2.winfo_exists():
                window2.destroy()
        except tk.TclError:
            pass

    def ventana_activa():
        """
        Descripcion:
            Ejecuta la logica correspondiente a ventana activa dentro
            del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if control_ventana["cerrando"]:
            return False
        try:
            return bool(window2.winfo_exists())
        except tk.TclError:
            control_ventana["cerrando"] = True
            return False

    def cerrar_sala_completa(ir_a_main=True, destruir_app=False):
        """
        Descripcion:
            Cierra TODO: afters, cliente, servidor, sala local y
            ventana. Luego navega según corresponda. Parámetros:
            ir_a_main (bool): Si True navega a GoMain al terminar.
            destruir_app (bool): Si True cierra toda la aplicación.
        
        Entradas:
            ir_a_main (object): Valor recibido por la funcion. Valor
            opcional.
            destruir_app (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if control_ventana["cerrando"]:
            return
        control_ventana["cerrando"] = True

        _cancelar_afters()
        _vaciar_cola()
        _cerrar_cliente()
        _detener_servidor()
        limpiar_sala_local()
        _destruir_ventana()

        if destruir_app:
            cerrar_todo()
        elif ir_a_main:
            GoMain()

    def cerrar_solo_cliente(ir_a_main=True):
        """
        Descripcion:
            Cierra cliente pero NO el servidor (caso: el que se unió
            vuelve). El servidor sigue vivo y notifica al creador.
        
        Entradas:
            ir_a_main (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
        """
        if control_ventana["cerrando"]:
            return
        control_ventana["cerrando"] = True

        _cancelar_afters()
        _vaciar_cola()
        _cerrar_cliente()
        limpiar_sala_local()
        _destruir_ventana()

        if ir_a_main:
            GoMain()

    # ------------------------------------------------------------------ #
    # Botón Volver                                                         #
    # ------------------------------------------------------------------ #

    def GoMainR():
        """
        Descripcion:
            Lógica del botón Volver según el rol: - Creador del
            servidor: cierra servidor y cliente → ambos vuelven a main.
            El que se unió (si había) recibe mensaje de servidor caído.
            - El que se unió: desconecta solo al cliente. El servidor
            notifica al creador que el contrincante salió.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        es_creador = variable_modo_conexion.get() == "crear_servidor"

        if es_creador:
            # Cerramos servidor → el otro jugador recibe conexión_perdida
            cerrar_sala_completa(ir_a_main=True)
        else:
            # Solo desconectamos este cliente; el servidor sigue vivo
            cerrar_solo_cliente(ir_a_main=True)

    # ------------------------------------------------------------------ #
    # Ir al mapa (ambos jugadores listos)                                 #
    # ------------------------------------------------------------------ #

    def GoMapaR():
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoMapaR.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        DATOS_PARTIDA["rol"] = estado_red["rol"]
        DATOS_PARTIDA["usuario"] = estado_red["usuario"]
        DATOS_PARTIDA["faccion"] = faccion_confirmada.get()
        DATOS_PARTIDA["puerto"] = estado_red["puerto"]
        DATOS_PARTIDA["modo"] = "red"
        DATOS_PARTIDA["es_host"] = variable_modo_conexion.get() == "crear_servidor"
        # El mapa hereda adaptador y servidor para mantener la conexión activa.
        DATOS_PARTIDA["adaptador"] = adaptador
        DATOS_PARTIDA["servidor_local"] = servidor_local["instancia"]

        # Marcamos cerrando para frenar procesar_mensajes_red pero sin
        # cerrar cliente ni servidor (el mapa los necesita).
        control_ventana["cerrando"] = True
        _cancelar_afters()
        _vaciar_cola()
        limpiar_sala_local()
        _destruir_ventana()
        GoMapa()

    # ------------------------------------------------------------------ #
    # Retorno automático por desconexión                                   #
    # ------------------------------------------------------------------ #

    def volver_a_main_por_desconexion(mensaje):
        """
        Descripcion:
            Llamado cuando el servidor notifica que la conexión se
            perdió o que el contrincante abandonó. Casos: A) Éramos el
            que se unió y el creador cerró la sala: Mostramos messagebox
            "La sala ha sido cerrada", volvemos a main. B) Éramos el
            creador y el que se unió se desconectó: Mostramos messagebox
            "El contrincante salió", reiniciamos UI (quitamos facción,
            volvemos a espera).
        
        Entradas:
            mensaje (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if control_ventana["cerrando"] or control_ventana.get("retorno_id") is not None:
            return

        agregar_evento(mensaje)
        try:
            etiqueta_conexion.config(text=mensaje, fg=COLOR_ALERTA)
        except tk.TclError:
            control_ventana["cerrando"] = True
            return

        es_creador = variable_modo_conexion.get() == "crear_servidor"

        if not es_creador:
            # Fuimos expulsados porque el servidor se cerró
            def ejecutar_retorno_unido():
                """
                Descripcion:
                    Ejecuta la logica correspondiente a ejecutar retorno
                    unido dentro del flujo del juego.
                
                Entradas:
                    Ninguna.
                
                Salidas:
                    None: Ejecuta la accion y puede modificar el estado
                    interno, la interfaz o los datos relacionados.
                
                Restricciones:
                    - Requiere que los widgets, ventanas o callbacks
                    usados por la interfaz existan antes de ejecutarse.
                """
                control_ventana["retorno_id"] = None
                if control_ventana["cerrando"]:
                    return
                # Cerramos solo cliente (servidor ya no existe)
                cerrar_sala_completa(ir_a_main=False)
                messagebox.showinfo(
                    "Sala cerrada",
                    "La sala ha sido cerrada por el anfitrión.",
                    parent=root,
                )
                GoMain()

            control_ventana["retorno_id"] = window2.after(800, ejecutar_retorno_unido)

        else:
            # El contrincante abandonó → reiniciar UI, volver a espera
            def ejecutar_reinicio_creador():
                """
                Descripcion:
                    Ejecuta la logica correspondiente a ejecutar
                    reinicio creador dentro del flujo del juego.
                
                Entradas:
                    Ninguna.
                
                Salidas:
                    None: Ejecuta la accion y puede modificar el estado
                    interno, la interfaz o los datos relacionados.
                
                Restricciones:
                    - Requiere que los widgets, ventanas o callbacks
                    usados por la interfaz existan antes de ejecutarse.
                """
                control_ventana["retorno_id"] = None
                if control_ventana["cerrando"]:
                    return
                _reiniciar_ui_tras_salida_contrincante()

            control_ventana["retorno_id"] = window2.after(300, ejecutar_reinicio_creador)

    def _reiniciar_ui_tras_salida_contrincante():
        """
        Descripcion:
            Reinicia el estado de UI del creador cuando el contrincante
            se va: - Quita facción elegida / seleccionada - Quita estado
            'listo' - Actualiza etiquetas - Muestra aviso
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        if not ventana_activa():
            return

        # Resetear estado de facción y listo
        faccion_confirmada.set("")
        faccion_temporal.set("")
        seleccion_bloqueada.set(False)
        listo_para_mapa.set(False)
        estado_red["en_espera"] = False
        estado_red["sala_estuvo_completa"] = False
        estado_red["jugadores_conectados"] = 1

        # Limpiar sala local
        sala = obtener_datos_sala()
        sala["facciones"].clear()
        sala["listos"].clear()

        try:
            texto_faccion.config(text="Elige una facción", fg="black")
            texto_espera.config(text="Esperando que alguien se una")
            etiqueta_conexion.config(
                text="Conectado. Esperando al segundo jugador.", fg="orange"
            )
        except tk.TclError:
            return

        refrescar_botones()

        messagebox.showinfo(
            "Contrincante salió",
            "El contrincante abandonó la sala.\nPuedes esperar a otro jugador.",
            parent=window2,
        )

    # ------------------------------------------------------------------ #
    # UI: Construcción de widgets                                          #
    # ------------------------------------------------------------------ #

    boton_volver = tk.Button(
        window2, text="Volver", font=("Arial", 12, "bold"), width=10,
        height=2, bg="red", command=GoMainR
    )
    boton_volver.place(x=10, y=8)

    titulo = tk.Label(window2, text="Play en red", font=("Arial", 28, "bold"), bg=COLOR_FONDO)
    titulo.place(relx=0.5, y=42, anchor="center")

    panel_superior = tk.Frame(window2, bg=COLOR_PANEL, relief="groove", bd=2, padx=12, pady=10)
    panel_superior.place(relx=0.5, y=118, anchor="center")

    variable_modo_conexion = tk.StringVar(value="crear_servidor")
    tk.Label(panel_superior, text="Modo:", font=("Arial", 11, "bold"), bg=COLOR_PANEL).grid(row=0, column=0, padx=4)
    tk.Radiobutton(panel_superior, text="Crear servidor", variable=variable_modo_conexion, value="crear_servidor", bg=COLOR_PANEL).grid(row=0, column=1, padx=4)
    tk.Radiobutton(panel_superior, text="Unirse a partida", variable=variable_modo_conexion, value="unirse_partida", bg=COLOR_PANEL).grid(row=0, column=2, padx=4)

    tk.Label(panel_superior, text="IP servidor:", font=("Arial", 11), bg=COLOR_PANEL).grid(row=1, column=0, padx=4)
    campo_ip = tk.Entry(panel_superior, font=("Arial", 11), width=15)
    campo_ip.insert(0, preferencias.get("ip_servidor_predeterminada", "127.0.0.1"))
    campo_ip.grid(row=1, column=1, padx=4)

    tk.Label(panel_superior, text="Usuario:", font=("Arial", 11), bg=COLOR_PANEL).grid(row=1, column=2, padx=4)
    campo_usuario = tk.Label(panel_superior, text=obtener_usuario_actual() or "Invitado", font=("Arial", 11, "bold"), width=14, bg=COLOR_PANEL, relief="sunken", anchor="w")
    campo_usuario.grid(row=1, column=3, padx=4)

    tk.Label(panel_superior, text="Rol:", font=("Arial", 11), bg=COLOR_PANEL).grid(row=1, column=4, padx=4)
    variable_rol = tk.StringVar(value="defensor")
    tk.OptionMenu(panel_superior, variable_rol, "defensor", "atacante").grid(row=1, column=5, padx=4)

    tk.Label(panel_superior, text="Puerto:", font=("Arial", 11), bg=COLOR_PANEL).grid(row=1, column=6, padx=4)
    campo_puerto = tk.Entry(panel_superior, font=("Arial", 11), width=7)
    campo_puerto.insert(0, str(preferencias.get("puerto_predeterminado", PUERTO_PREDETERMINADO)))
    campo_puerto.grid(row=1, column=7, padx=4)

    etiqueta_conexion = tk.Label(window2, text="Sin conexión.", font=("Arial", 12, "bold"), fg="red", bg=COLOR_FONDO)
    etiqueta_conexion.place(relx=0.5, y=176, anchor="center")

    etiqueta_ayuda_red = tk.Label(
        window2,
        text="Si creas servidor, el segundo jugador debe conectarse a la IP local y puerto mostrados aquí.",
        font=("Arial", 10, "bold"), bg=COLOR_AYUDA, fg="#3d2b00", relief="solid", bd=1, padx=8, pady=3
    )
    etiqueta_ayuda_red.place(relx=0.5, y=200, anchor="center")

    etiqueta_datos_host = tk.Label(
        window2, text="IP para compartir: -- | Puerto: --",
        font=("Arial", 12, "bold"), bg="#d7f5ff", fg="#00384d", relief="solid", bd=2, padx=10, pady=4
    )
    etiqueta_datos_host.place(relx=0.5, y=229, anchor="center")

    panel_facciones = tk.Frame(window2, bg=COLOR_FONDO)
    panel_facciones.place(relx=0.5, y=285, anchor="n")
    botones_faccion = {}

    texto_faccion = tk.Label(window2, text="Elige una facción", font=("Arial", 12, "bold"), width=34, height=2, relief="solid", bd=2, bg=COLOR_FONDO)
    texto_faccion.place(relx=0.5, y=260, anchor="center")

    texto_espera = tk.Label(window2, text="", font=("Arial", 11, "bold"), fg=COLOR_ALERTA, bg=COLOR_FONDO, width=24)
    texto_espera.place(x=905, y=615)

    caja_info_facciones = tk.Listbox(window2, font=("Consolas", 9), width=42, height=4)
    caja_info_facciones.place(x=265, y=600)

    caja_eventos = tk.Listbox(window2, font=("Consolas", 9), width=48, height=4)
    caja_eventos.place(x=610, y=600)

    # ------------------------------------------------------------------ #
    # Helpers de UI                                                        #
    # ------------------------------------------------------------------ #

    def agregar_evento(texto):
        """
        Descripcion:
            Ejecuta la logica correspondiente a agregar evento dentro
            del flujo del juego.
        
        Entradas:
            texto (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if texto and ventana_activa():
            try:
                if not caja_eventos.winfo_exists():
                    return
            except tk.TclError:
                control_ventana["cerrando"] = True
                return
            caja_eventos.insert(tk.END, texto)
            caja_eventos.yview(tk.END)

    def actualizar_info_facciones(texto=None):
        """
        Descripcion:
            Actualiza la informacion o el componente asociado a
            actualizar info facciones.
        
        Entradas:
            texto (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not ventana_activa():
            return
        try:
            if not caja_info_facciones.winfo_exists():
                return
        except tk.TclError:
            control_ventana["cerrando"] = True
            return
        caja_info_facciones.delete(0, tk.END)
        if texto:
            caja_info_facciones.insert(tk.END, texto)
        if faccion_confirmada.get():
            caja_info_facciones.insert(tk.END, f"Tu facción: {faccion_confirmada.get()}")
        elif faccion_temporal.get():
            caja_info_facciones.insert(tk.END, f"Seleccionada: {faccion_temporal.get()}")
        else:
            caja_info_facciones.insert(tk.END, "Debe elegir una facción.")
        resumen_red = adaptador.cliente.obtener_resumen_red()
        usuarios_por_rol = resumen_red.get("usuarios_por_rol", {})
        if usuarios_por_rol:
            caja_info_facciones.insert(tk.END, "Jugadores conectados:")
            for rol in ("defensor", "atacante"):
                caja_info_facciones.insert(tk.END, f"{rol}: {usuarios_por_rol.get(rol, 'pendiente')}")
        for rol, faccion in obtener_datos_sala()["facciones"].items():
            caja_info_facciones.insert(tk.END, f"facción {rol}: {faccion}")

    def texto_boton_faccion(nombre_faccion, ocupada=False, seleccionada=False):
        """
        Descripcion:
            Ejecuta la logica correspondiente a texto boton faccion
            dentro del flujo del juego.
        
        Entradas:
            nombre_faccion (object): Valor recibido por la funcion.
            ocupada (object): Valor recibido por la funcion. Valor
            opcional.
            seleccionada (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        datos_faccion = datos_facciones_por_nombre.get(nombre_faccion, {})
        codigo = datos_faccion.get("codigo", "")
        prefijo = "✓ " if seleccionada else "🔒 " if ocupada else ""
        return f"{prefijo}{codigo}\n{nombre_faccion}"

    def pintar_rectangulo(imagen, color, x1, y1, x2, y2):
        """
        Descripcion:
            Ejecuta la logica correspondiente a pintar rectangulo dentro
            del flujo del juego.
        
        Entradas:
            imagen (object): Valor recibido por la funcion.
            color (object): Valor recibido por la funcion.
            x1 (object): Valor recibido por la funcion.
            y1 (object): Valor recibido por la funcion.
            x2 (object): Valor recibido por la funcion.
            y2 (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        imagen.put(color, to=(x1, y1, x2, y2))

    def crear_imagen_bandera(codigo):
        """
        Descripcion:
            Crea y configura el elemento asociado a crear imagen bandera
            para usarlo dentro del juego o la interfaz.
        
        Entradas:
            codigo (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        ancho = 120
        alto = 72
        imagen = tk.PhotoImage(master=window2, width=ancho, height=alto)
        pintar_rectangulo(imagen, "white", 0, 0, ancho, alto)

        if codigo == "ESP":
            pintar_rectangulo(imagen, "#aa151b", 0, 0, ancho, 18)
            pintar_rectangulo(imagen, "#f1bf00", 0, 18, ancho, 54)
            pintar_rectangulo(imagen, "#aa151b", 0, 54, ancho, alto)
        elif codigo == "ENG":
            pintar_rectangulo(imagen, "#cf142b", 0, 28, ancho, 44)
            pintar_rectangulo(imagen, "#cf142b", 52, 0, 68, alto)
        elif codigo == "ALE":
            pintar_rectangulo(imagen, "#000000", 0, 0, ancho, 24)
            pintar_rectangulo(imagen, "#dd0000", 0, 24, ancho, 48)
            pintar_rectangulo(imagen, "#ffce00", 0, 48, ancho, alto)
        elif codigo == "RUS":
            pintar_rectangulo(imagen, "#ffffff", 0, 0, ancho, 24)
            pintar_rectangulo(imagen, "#0039a6", 0, 24, ancho, 48)
            pintar_rectangulo(imagen, "#d52b1e", 0, 48, ancho, alto)
        elif codigo == "ITA":
            pintar_rectangulo(imagen, "#009246", 0, 0, 40, alto)
            pintar_rectangulo(imagen, "#ffffff", 40, 0, 80, alto)
            pintar_rectangulo(imagen, "#ce2b37", 80, 0, ancho, alto)
        elif codigo == "USA":
            alto_fr = alto // 13
            for indice in range(13):
                color = "#b22234" if indice % 2 == 0 else "#ffffff"
                pintar_rectangulo(imagen, color, 0, indice * alto_fr, ancho, (indice + 1) * alto_fr)
            pintar_rectangulo(imagen, "#3c3b6e", 0, 0, 52, 39)
            for y in (7, 19, 31):
                for x in (8, 20, 32, 44):
                    pintar_rectangulo(imagen, "#ffffff", x, y, x + 3, y + 3)
        pintar_rectangulo(imagen, "#555555", 0, 0, ancho, 1)
        pintar_rectangulo(imagen, "#555555", 0, alto - 1, ancho, alto)
        pintar_rectangulo(imagen, "#555555", 0, 0, 1, alto)
        pintar_rectangulo(imagen, "#555555", ancho - 1, 0, ancho, alto)
        return imagen

    def refrescar_botones():
        """
        Descripcion:
            Ejecuta la logica correspondiente a refrescar botones dentro
            del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not ventana_activa():
            return
        for nombre_faccion, boton in botones_faccion.items():
            try:
                if not boton.winfo_exists():
                    continue
            except tk.TclError:
                control_ventana["cerrando"] = True
                return
            ocupada = faccion_esta_ocupada_por_otro(nombre_faccion)
            seleccionada = nombre_faccion == faccion_temporal.get()
            color = "#ffc7c7" if ocupada else COLOR_FONDO
            if seleccionada:
                color = COLOR_SELECCION
            boton.config(
                text=texto_boton_faccion(nombre_faccion, ocupada, seleccionada),
                image=imagenes_facciones.get(nombre_faccion),
                compound="top",
                relief="sunken" if seleccionada else "raised",
                bg=color,
                activebackground=color,
            )
        actualizar_info_facciones()

    def seleccionar_faccion(nombre_faccion):
        """
        Descripcion:
            Registra la seleccion correspondiente a seleccionar faccion.
        
        Entradas:
            nombre_faccion (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not hay_dos_jugadores():
            texto_faccion.config(text="Esperando al contrincante", fg=COLOR_ALERTA)
            return
        if faccion_esta_ocupada_por_otro(nombre_faccion):
            texto_faccion.config(text="Facción ya elegida", fg=COLOR_ALERTA)
            actualizar_info_facciones("Facción ya elegida por el otro jugador.")
            return
        if seleccion_bloqueada.get():
            cambiar_faccion_click()
        faccion_temporal.set(nombre_faccion)
        texto_faccion.config(text=f"Facción {nombre_faccion}", fg="black")
        refrescar_botones()

    for indice, datos_faccion in enumerate(catalogo_facciones):
        nombre_faccion = datos_faccion["nombre"]
        fila = indice // 3
        columna = indice % 3
        imagen = crear_imagen_bandera(datos_faccion["codigo"])
        imagenes_facciones[nombre_faccion] = imagen
        boton_faccion = tk.Button(
            panel_facciones,
            text=texto_boton_faccion(nombre_faccion),
            image=imagen, compound="top",
            font=("Arial", 12, "bold"), width=170, height=120,
            command=lambda faccion=nombre_faccion: seleccionar_faccion(faccion)
        )
        boton_faccion.imagen_faccion = imagen
        boton_faccion.grid(row=fila, column=columna, padx=24, pady=8)
        botones_faccion[nombre_faccion] = boton_faccion

    # ------------------------------------------------------------------ #
    # Acciones de lobby                                                    #
    # ------------------------------------------------------------------ #

    def elegir_faccion_click():
        """
        Descripcion:
            Ejecuta la logica correspondiente a elegir faccion click
            dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not hay_dos_jugadores():
            texto_faccion.config(text="Esperando al contrincante", fg=COLOR_ALERTA)
            agregar_evento("No se puede elegir facción hasta que haya 2 jugadores.")
            return
        if not faccion_temporal.get():
            texto_faccion.config(text="Elige una facción", fg=COLOR_ALERTA)
            return
        sala = obtener_datos_sala()
        for rol, faccion in sala["facciones"].items():
            if rol != estado_red["rol"] and faccion == faccion_temporal.get():
                texto_faccion.config(text="Facción ya elegida", fg=COLOR_ALERTA)
                agregar_evento("Facción ya elegida por el contrincante.")
                return
        faccion_confirmada.set(faccion_temporal.get())
        seleccion_bloqueada.set(True)
        listo_para_mapa.set(False)
        registrar_estado_local(False)
        enviar_accion_lobby(ACCION_ELEGIR_FACCION, faccion=faccion_confirmada.get())
        texto_faccion.config(text="Facción elegida", fg=COLOR_LISTO)
        refrescar_botones()

    def cambiar_faccion_click():
        """
        Descripcion:
            Ejecuta la logica correspondiente a cambiar faccion click
            dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        seleccion_bloqueada.set(False)
        listo_para_mapa.set(False)
        faccion_confirmada.set("")
        registrar_estado_local(False)
        enviar_accion_lobby(ACCION_CAMBIAR_FACCION)
        texto_espera.config(text="")
        texto_faccion.config(
            text="Elige una facción" if not faccion_temporal.get() else f"Facción {faccion_temporal.get()}",
            fg="black"
        )

    def iniciar_combate_click():
        """
        Descripcion:
            Inicia el proceso asociado a iniciar combate click.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not hay_dos_jugadores():
            texto_faccion.config(text="Esperando al contrincante", fg=COLOR_ALERTA)
            return
        if not faccion_confirmada.get():
            texto_faccion.config(text="Elige una facción", fg=COLOR_ALERTA)
            return
        listo_para_mapa.set(True)
        estado_red["en_espera"] = True
        registrar_estado_local(True)
        enviar_accion_lobby(ACCION_LISTO_LOBBY)
        if facciones_validas_en_sala() and roles_necesarios_listos():
            GoMapaR()
            return
        texto_espera.config(text="Esperando jugador")
        agregar_evento("Listo. Esperando al contrincante.")

    # ------------------------------------------------------------------ #
    # Creación de servidor y conexión de cliente                           #
    # ------------------------------------------------------------------ #

    def buscar_puerto_disponible(puerto_preferido):
        """
        Descripcion:
            Ejecuta la logica correspondiente a buscar puerto disponible
            dentro del flujo del juego.
        
        Entradas:
            puerto_preferido (object): Valor recibido por la funcion.
        
        Salidas:
            tuple: Conjunto de valores resultantes de la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        puertos_a_probar = [puerto_preferido] + list(range(5001, 5011)) + list(range(5050, 5061))
        revisados = []
        for puerto_candidato in puertos_a_probar:
            if puerto_candidato in revisados:
                continue
            revisados.append(puerto_candidato)
            try:
                socket_prueba = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_prueba.bind(("0.0.0.0", puerto_candidato))
                socket_prueba.close()
                return True, puerto_candidato, "Puerto disponible."
            except OSError:
                continue
        return False, puerto_preferido, "No se encontró un puerto disponible."

    def iniciar_servidor_local(puerto):
        """
        Descripcion:
            Inicia el proceso asociado a iniciar servidor local.
        
        Entradas:
            puerto (object): Valor recibido por la funcion.
        
        Salidas:
            tuple: Conjunto de valores resultantes de la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
        """
        if servidor_local["instancia"] is not None:
            return True, "Servidor local ya estaba iniciado."
        encontrado, puerto_final, mensaje = buscar_puerto_disponible(puerto)
        if not encontrado:
            return False, mensaje
        servidor = ServidorPartida(puerto=puerto_final)
        hilo = threading.Thread(target=servidor.iniciar, daemon=True)
        servidor_local["instancia"] = servidor
        servidor_local["hilo"] = hilo
        hilo.start()
        campo_puerto.delete(0, tk.END)
        campo_puerto.insert(0, str(puerto_final))
        ip_local = obtener_ip_local_visible()
        etiqueta_datos_host.config(text=f"IP para compartir: {ip_local} | Puerto: {puerto_final}")
        return True, f"Servidor creado. El segundo jugador debe conectarse a {ip_local}:{puerto_final}."

    def conectar_cliente(host, usuario, rol, puerto):
        """
        Descripcion:
            Ejecuta la logica correspondiente a conectar cliente dentro
            del flujo del juego.
        
        Entradas:
            host (object): Valor recibido por la funcion.
            usuario (object): Valor recibido por la funcion.
            rol (object): Valor recibido por la funcion.
            puerto (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
        """
        estado_red["puerto"] = puerto
        estado_red["usuario"] = usuario
        etiqueta_datos_host.config(text=f"IP para compartir: {obtener_ip_local_visible()} | Puerto: {puerto}")
        exito, mensaje = adaptador.conectar(host, usuario, rol, puerto)
        etiqueta_conexion.config(text=mensaje, fg="green" if exito else "red")
        agregar_evento(mensaje)
        if exito:
            estado_red["conectado"] = True
            boton_conectar.config(state="disabled")
            adaptador.cliente.obtener_estado()
        else:
            control_ventana["conectando"] = False
            boton_conectar.config(state="normal")

    def conectar_click():
        """
        Descripcion:
            Ejecuta la logica correspondiente a conectar click dentro
            del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if control_ventana["conectando"] or estado_red["conectado"]:
            agregar_evento("Ya existe una conexión activa en esta sala.")
            return
        control_ventana["conectando"] = True
        boton_conectar.config(state="disabled")
        host = campo_ip.get().strip()
        usuario = estado_red["usuario"]
        rol = variable_rol.get().strip()
        try:
            puerto = int(campo_puerto.get())
        except ValueError:
            messagebox.showwarning("Puerto inválido", "El puerto debe ser un número entero.")
            control_ventana["conectando"] = False
            boton_conectar.config(state="normal")
            return

        if variable_modo_conexion.get() == "crear_servidor":
            exito, mensaje = iniciar_servidor_local(puerto)
            etiqueta_conexion.config(text=mensaje, fg="green" if exito else "red")
            agregar_evento(mensaje)
            if not exito:
                control_ventana["conectando"] = False
                boton_conectar.config(state="normal")
                return
            puerto = int(campo_puerto.get())

            def conectar_local_demorado():
                """
                Descripcion:
                    Ejecuta la logica correspondiente a conectar local
                    demorado dentro del flujo del juego.
                
                Entradas:
                    Ninguna.
                
                Salidas:
                    None: Ejecuta la accion y puede modificar el estado
                    interno, la interfaz o los datos relacionados.
                
                Restricciones:
                    - Requiere que los widgets, ventanas o callbacks
                    usados por la interfaz existan antes de ejecutarse.
                """
                control_ventana["after_conexion_id"] = None
                if control_ventana["cerrando"]:
                    return
                try:
                    if window2.winfo_exists():
                        conectar_cliente("127.0.0.1", usuario, rol, puerto)
                except tk.TclError:
                    control_ventana["cerrando"] = True

            control_ventana["after_conexion_id"] = window2.after(250, conectar_local_demorado)
            return

        conectar_cliente(host, usuario, rol, puerto)
        control_ventana["conectando"] = False
        if not estado_red["conectado"]:
            boton_conectar.config(state="normal")

    boton_conectar = tk.Button(
        panel_superior, text="Continuar", font=("Arial", 11, "bold"),
        bg="lightgreen", command=conectar_click
    )
    boton_conectar.grid(row=1, column=8, padx=8)

    boton_cambiar_faccion = tk.Button(
        window2, text="Cambiar facción", font=("Arial", 12, "bold"),
        width=16, bg="#ffd36b", command=cambiar_faccion_click
    )
    boton_cambiar_faccion.place(x=55, y=585)

    boton_elegir_faccion = tk.Button(
        window2, text="Elegir facción", font=("Arial", 12, "bold"),
        width=16, bg="lightgreen", command=elegir_faccion_click
    )
    boton_elegir_faccion.place(x=55, y=635)

    boton_iniciar_combate = tk.Button(
        window2, text="Jugar", font=("Arial", 13, "bold"),
        width=18, height=2, bg="orange", command=iniciar_combate_click
    )
    boton_iniciar_combate.place(x=1010, y=610)

    # ------------------------------------------------------------------ #
    # Loop de procesamiento de mensajes de red                             #
    # ------------------------------------------------------------------ #

    def procesar_mensajes_red():
        """
        Descripcion:
            Ejecuta la logica correspondiente a procesar mensajes red
            dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
        """
        if not ventana_activa():
            return
        while not cola_mensajes.empty():
            if not ventana_activa():
                return
            mensaje = cola_mensajes.get()
            texto = mensaje.get("mensaje", "")
            if texto:
                agregar_evento(texto)
            datos = mensaje.get("datos", {})
            if isinstance(datos, dict):
                estado_red["jugadores_conectados"] = int(
                    datos.get("jugadores_conectados", estado_red["jugadores_conectados"])
                )
                estado_red["rol"] = datos.get("rol_cliente", datos.get("rol", estado_red["rol"]))
                sincronizar_lobby_remoto(datos)

                if estado_red["jugadores_conectados"] >= 2:
                    estado_red["sala_estuvo_completa"] = True

                roles_faltantes = datos.get("roles_faltantes", [])
                mensaje_sala = datos.get("mensaje_sala", "")
                if roles_faltantes:
                    texto_espera.config(text="Falta: " + ", ".join(roles_faltantes))
                elif mensaje_sala:
                    texto_espera.config(text=mensaje_sala)

                refrescar_botones()

                # Conexión perdida: el servidor desapareció (nos expulsaron)
                if datos.get("conexion_perdida"):
                    volver_a_main_por_desconexion("Se cerró la conexión con la sala.")
                    return

                # El contrincante se desconectó de una sala que estuvo completa
                if (estado_red["sala_estuvo_completa"]
                        and estado_red["jugadores_conectados"] < 2):
                    volver_a_main_por_desconexion(
                        "El contrincante abandonó la sala."
                    )
                    return

                if hay_dos_jugadores():
                    etiqueta_conexion.config(
                        text="Sala completa: 2 jugadores conectados.", fg="green"
                    )
                elif estado_red["conectado"]:
                    etiqueta_conexion.config(
                        text="Conectado. Esperando al segundo jugador.", fg="orange"
                    )

            if estado_red["en_espera"] and facciones_validas_en_sala() and roles_necesarios_listos():
                GoMapaR()
                return

        if not control_ventana["cerrando"]:
            try:
                if window2.winfo_exists():
                    control_ventana["after_id"] = window2.after(300, procesar_mensajes_red)
            except tk.TclError:
                control_ventana["cerrando"] = True

    # ------------------------------------------------------------------ #
    # Protocolo de cierre de la X de la ventana                           #
    # ------------------------------------------------------------------ #

    def cerrar_ventana():
        """
        Descripcion:
            Al cerrar la X de la ventana cerramos todo y destruimos la
            app.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        cerrar_sala_completa(ir_a_main=False, destruir_app=True)

    control_ventana["after_id"] = window2.after(300, procesar_mensajes_red)
    window2.protocol("WM_DELETE_WINDOW", cerrar_ventana)
