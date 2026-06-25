#=======================================#
# Archivo para iniciar sesion antes de jugar
#=======================================#

import os
import queue
import socket
import sys
import threading
import tkinter as tk
from tkinter import messagebox

RUTA_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUTA_LOGICA = os.path.join(RUTA_PROYECTO, "Logica")
RUTA_RED = os.path.join(RUTA_PROYECTO, "Red")

for ruta in (RUTA_LOGICA, RUTA_RED):
    if ruta not in sys.path:
        sys.path.append(ruta)

import app
from cliente import ClientePartida, PUERTO_PREDETERMINADO
from servidor import ServidorPartida


FACCIONES = ["España", "Inglaterra", "Alemania", "Rusia", "Italia", "EE.UU"]
TIPOS_TORRE = [torre["clave"] for torre in app.obtener_catalogo_torres()]
TIPOS_UNIDAD = [unidad["clave"] for unidad in app.obtener_catalogo_unidades()]
CANTIDAD_FILAS_TABLERO = 11
CANTIDAD_COLUMNAS_TABLERO = 6


class AdaptadorClienteTkinter:
    """
    Descripcion:
        Encapsula el ClientePartida de red para que la ventana de
        Tkinter pueda enviar acciones al servidor sin mezclar la
        logica de combate con la interfaz grafica.

    Entradas:
        cola_mensajes (queue.Queue): Cola donde se guardan los
            mensajes recibidos desde el hilo del cliente.

    Salidas:
        No retorna nada. Crea un adaptador listo para conectar.

    Restricciones:
        - La cola debe existir antes de crear el adaptador.
        - Los widgets de Tkinter no deben modificarse directamente
          desde el hilo de red.
    """

    def __init__(self, cola_mensajes):
        self.cola_mensajes = cola_mensajes
        self.cliente = ClientePartida(callback_mensaje=self._recibir_mensaje)

    def _recibir_mensaje(self, mensaje):
        """
        Descripcion:
            Guarda en una cola segura los mensajes recibidos del
            servidor para que Tkinter los procese con after().

        Entradas:
            mensaje (dict): Mensaje recibido desde el servidor.

        Salidas:
            None: Agrega el mensaje a la cola.

        Restricciones:
            - No debe modificar widgets directamente.
        """
        self.cola_mensajes.put(mensaje)

    def conectar(self, host, usuario, rol, puerto):
        """
        Descripcion:
            Conecta el cliente de red con el servidor de partida.

        Entradas:
            host (str): IP o nombre del servidor.
            usuario (str): Nombre del jugador.
            rol (str): Rol solicitado, defensor o atacante.
            puerto (int): Puerto TCP del servidor.

        Salidas:
            tuple[bool, str]: Resultado de la conexion y mensaje.

        Restricciones:
            - host y usuario no deben estar vacios.
            - rol debe ser compatible con el servidor.
        """
        return self.cliente.conectar(host, usuario, puerto=puerto, rol=rol)

    def cerrar(self):
        """
        Descripcion:
            Cierra la conexion con el servidor si existe.

        Entradas:
            Ninguna.

        Salidas:
            None: Cierra el socket del cliente.

        Restricciones:
            Ninguna.
        """
        self.cliente.cerrar()


def play(root, GoMain, *argumentos):
    """
    Descripcion:
        Crea la ventana de juego conectada al modo cliente-servidor.
        La interfaz solo muestra el estado recibido, dibuja un tablero
        simple, permite elegir una faccion visual del jugador y envia
        acciones al servidor mediante ClientePartida. Acepta tanto la
        llamada nueva con GoMapa como la llamada anterior sin GoMapa
        para mantener compatibilidad entre versiones de root.py.

    Entradas:
        root: ventana raiz oculta.
        GoMain: funcion para volver al menu principal.
        argumentos (tuple): Puede contener cerrar_todo, configurar_ventana
            y obtener_usuario_actual; o GoMapa, cerrar_todo,
            configurar_ventana y obtener_usuario_actual.

    Salidas:
        No retorna ningun valor.

    Restricciones:
        - Debe existir un servidor ejecutandose para jugar en red.
        - La logica de dinero, combate y victoria vive en el servidor.
        - La faccion es una seleccion visual local para la interfaz.
        - La firma recibida debe tener 3 o 4 argumentos adicionales.
    """

    if len(argumentos) == 3:
        GoMapa = None
        cerrar_todo, configurar_ventana, obtener_usuario_actual = argumentos
    elif len(argumentos) == 4:
        GoMapa, cerrar_todo, configurar_ventana, obtener_usuario_actual = argumentos
    else:
        raise TypeError(
            "play() debe recibir root, GoMain y luego "
            "cerrar_todo/configurar_ventana/obtener_usuario_actual "
            "o GoMapa/cerrar_todo/configurar_ventana/obtener_usuario_actual"
        )

    window2 = tk.Toplevel(root)
    configurar_ventana(window2, "Play en red")

    cola_mensajes = queue.Queue()
    adaptador = AdaptadorClienteTkinter(cola_mensajes)
    estado_actual = {"datos": None, "mensaje_final_mostrado": False}
    servidor_local = {"instancia": None, "hilo": None}
    faccion_temporal = tk.StringVar(value=FACCIONES[0])
    faccion_confirmada = tk.StringVar(value="")
    seleccion_faccion_bloqueada = tk.BooleanVar(value=False)

    def detener_servidor_local():
        """
        Descripcion:
            Detiene el servidor creado desde esta ventana, si existe.

        Entradas:
            Ninguna.

        Salidas:
            None: Cierra el socket servidor local.

        Restricciones:
            Ninguna.
        """
        if servidor_local["instancia"] is not None:
            servidor_local["instancia"].detener()
            servidor_local["instancia"] = None
            servidor_local["hilo"] = None

    def GoMainR():
        adaptador.cerrar()
        detener_servidor_local()
        window2.destroy()
        GoMain()

    def GoMapaR():
        window2.destroy()
        GoMapa()

    boton_volver = tk.Button(
        window2, text="Volver", font=("Arial", 12, "bold"), width=10,
        height=2, bg="red", command=GoMainR
    )
    boton_volver.place(x=20, y=20)

    titulo = tk.Label(window2, text="Play en red", font=("Arial", 28, "bold"))
    titulo.place(relx=0.5, rely=0.06, anchor="center")

    panel_conexion = tk.Frame(window2)
    panel_conexion.place(relx=0.5, rely=0.15, anchor="center")

    variable_modo_conexion = tk.StringVar(value="crear_servidor")
    tk.Label(panel_conexion, text="Modo:", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=4, sticky="e")
    tk.Radiobutton(
        panel_conexion,
        text="Crear servidor",
        variable=variable_modo_conexion,
        value="crear_servidor",
    ).grid(row=0, column=1, padx=4, sticky="w")
    tk.Radiobutton(
        panel_conexion,
        text="Unirse a partida",
        variable=variable_modo_conexion,
        value="unirse_partida",
    ).grid(row=0, column=2, padx=4, sticky="w")

    tk.Label(panel_conexion, text="IP servidor:", font=("Arial", 11)).grid(row=1, column=0, padx=4)
    campo_ip = tk.Entry(panel_conexion, font=("Arial", 11), width=15)
    campo_ip.insert(0, "127.0.0.1")
    campo_ip.grid(row=1, column=1, padx=4)

    tk.Label(panel_conexion, text="Usuario:", font=("Arial", 11)).grid(row=1, column=2, padx=4)
    campo_usuario = tk.Entry(panel_conexion, font=("Arial", 11), width=14)
    campo_usuario.insert(0, obtener_usuario_actual() or "")
    campo_usuario.grid(row=1, column=3, padx=4)

    tk.Label(panel_conexion, text="Rol:", font=("Arial", 11)).grid(row=1, column=4, padx=4)
    variable_rol = tk.StringVar(value="defensor")
    tk.OptionMenu(panel_conexion, variable_rol, "defensor", "atacante").grid(row=1, column=5, padx=4)

    tk.Label(panel_conexion, text="Puerto:", font=("Arial", 11)).grid(row=1, column=6, padx=4)
    campo_puerto = tk.Entry(panel_conexion, font=("Arial", 11), width=7)
    campo_puerto.insert(0, str(PUERTO_PREDETERMINADO))
    campo_puerto.grid(row=1, column=7, padx=4)

    etiqueta_conexion = tk.Label(window2, text="Sin conexion.", font=("Arial", 12, "bold"), fg="red")
    etiqueta_conexion.place(relx=0.5, rely=0.21, anchor="center")

    panel_faccion = tk.Frame(window2, relief="solid", bd=1, padx=8, pady=5)
    panel_faccion.place(relx=0.5, rely=0.255, anchor="center")

    tk.Label(panel_faccion, text="Faccion:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=4)
    menu_facciones = tk.OptionMenu(panel_faccion, faccion_temporal, *FACCIONES)
    menu_facciones.config(width=12)
    menu_facciones.grid(row=0, column=1, padx=4)

    etiqueta_faccion = tk.Label(
        panel_faccion,
        text="Faccion sin confirmar",
        font=("Arial", 10, "bold"),
        fg="red",
        width=22,
    )
    etiqueta_faccion.grid(row=0, column=2, padx=4)

    def elegir_faccion_click():
        """
        Descripcion:
            Confirma la faccion elegida por el jugador en la interfaz.
            Esta seleccion es visual y no calcula reglas de combate.

        Entradas:
            Ninguna.

        Salidas:
            None: Actualiza el estado visual de la faccion.

        Restricciones:
            - Debe existir una faccion seleccionada en el menu.
            - No envia reglas de combate al servidor.
        """
        if not faccion_temporal.get():
            etiqueta_faccion.config(text="Elige una faccion", fg="red")
            return
        faccion_confirmada.set(faccion_temporal.get())
        seleccion_faccion_bloqueada.set(True)
        etiqueta_faccion.config(text=f"Faccion: {faccion_confirmada.get()}", fg="green")
        menu_facciones.config(state="disabled")

    def cambiar_faccion_click():
        """
        Descripcion:
            Permite cambiar nuevamente la faccion local antes o durante
            la partida sin modificar la logica del servidor.

        Entradas:
            Ninguna.

        Salidas:
            None: Desbloquea el selector de facciones.

        Restricciones:
            - Solo modifica datos visuales de la interfaz.
        """
        seleccion_faccion_bloqueada.set(False)
        faccion_confirmada.set("")
        etiqueta_faccion.config(text="Faccion sin confirmar", fg="red")
        menu_facciones.config(state="normal")

    tk.Button(
        panel_faccion,
        text="Elegir",
        font=("Arial", 10, "bold"),
        bg="lightgreen",
        command=elegir_faccion_click,
    ).grid(row=0, column=3, padx=4)
    tk.Button(
        panel_faccion,
        text="Cambiar",
        font=("Arial", 10, "bold"),
        bg="#ffd36b",
        command=cambiar_faccion_click,
    ).grid(row=0, column=4, padx=4)

    texto_estado = tk.Label(window2, text="Conectate a un servidor para comenzar.", font=("Arial", 12), justify="left")
    texto_estado.place(relx=0.20, rely=0.33, anchor="n")

    marco_tablero = tk.Frame(window2, bd=2, relief="solid")
    marco_tablero.place(relx=0.50, rely=0.33, anchor="n")
    celdas_tablero = []
    for fila in range(CANTIDAD_FILAS_TABLERO):
        fila_celdas = []
        for columna in range(CANTIDAD_COLUMNAS_TABLERO):
            celda = tk.Label(marco_tablero, text="", width=4, height=2, relief="ridge", bg="white")
            celda.grid(row=fila, column=columna)
            fila_celdas.append(celda)
        celdas_tablero.append(fila_celdas)

    caja_eventos = tk.Listbox(window2, font=("Consolas", 9), width=48, height=17)
    caja_eventos.place(relx=0.79, rely=0.33, anchor="n")

    def agregar_evento(texto):
        """
        Descripcion:
            Agrega un mensaje al cuadro de eventos de la interfaz.

        Entradas:
            texto (str): Mensaje que se desea mostrar.

        Salidas:
            None: Modifica el Listbox de eventos.

        Restricciones:
            - Debe llamarse desde el hilo principal de Tkinter.
        """
        if texto:
            caja_eventos.insert(tk.END, texto)
            caja_eventos.yview(tk.END)

    def dibujar_tablero(estado):
        """
        Descripcion:
            Dibuja una vista simple del tablero usando el estado
            oficial recibido desde el servidor.

        Entradas:
            estado (dict): Estado de partida devuelto por el servidor.

        Salidas:
            None: Actualiza colores y textos de las celdas.

        Restricciones:
            - El estado debe contener listas de torres, muros y
              unidades con fila y columna.
        """
        for fila in range(CANTIDAD_FILAS_TABLERO):
            for columna in range(CANTIDAD_COLUMNAS_TABLERO):
                texto = "B" if fila == 0 else ""
                color = "lightgreen" if fila == 0 else "white"
                celdas_tablero[fila][columna].config(text=texto, bg=color)

        for torre in estado.get("torres", []):
            celdas_tablero[torre["fila"]][torre["columna"]].config(text="T", bg="lightblue")
        for muro in estado.get("muros", []):
            celdas_tablero[muro["fila"]][muro["columna"]].config(text="M", bg="gray80")
        for unidad in estado.get("unidades", []):
            celdas_tablero[unidad["fila"]][unidad["columna"]].config(text="U", bg="salmon")

    def refrescar_estado(estado):
        """
        Descripcion:
            Actualiza etiquetas y tablero con el estado oficial de la
            partida recibido por red.

        Entradas:
            estado (dict): Estado actual de la partida.

        Salidas:
            None: Modifica widgets de la ventana.

        Restricciones:
            - Debe llamarse desde Tkinter usando after() o eventos de
              la ventana.
        """
        estado_actual["datos"] = estado

        if not estado:
            texto_estado.config(text="Esperando al segundo jugador o al estado del servidor.")
            return

        texto_estado.config(text=(
            f"Ronda: {estado['numero_ronda']}\n"
            f"Defensor: {estado['nombre_defensor']} (dinero: {estado['dinero_defensor']})\n"
            f"Atacante: {estado['nombre_atacante']} (dinero: {estado['dinero_atacante']})\n"
            f"Marcador: {estado['rondas_ganadas_defensor']} - {estado['rondas_ganadas_atacante']}\n"
            f"Base: {estado['vida_base']}/{estado['vida_maxima_base']}\n"
            f"Torres: {len(estado['torres'])} | Muros: {len(estado.get('muros', []))}\n"
            f"Unidades: {len(estado['unidades'])}\n"
            f"Faccion: {faccion_confirmada.get() or 'Sin confirmar'}\n"
            f"Finalizada: {'Si' if estado['partida_finalizada'] else 'No'}"
        ))
        dibujar_tablero(estado)

        if estado.get("partida_finalizada") and not estado_actual["mensaje_final_mostrado"]:
            estado_actual["mensaje_final_mostrado"] = True
            messagebox.showinfo(
                "Partida finalizada",
                f"{estado['ganador_partida']} gano la partida como {estado['rol_ganador_partida']}.",
            )

    def procesar_mensajes_red():
        """
        Descripcion:
            Procesa mensajes pendientes recibidos del servidor y
            actualiza la interfaz desde el hilo principal de Tkinter.

        Entradas:
            Ninguna.

        Salidas:
            None: Consume la cola de mensajes de red.

        Restricciones:
            - Debe programarse periodicamente con after().
        """
        while not cola_mensajes.empty():
            mensaje = cola_mensajes.get()
            texto_mensaje = mensaje.get("mensaje", "")
            if texto_mensaje:
                agregar_evento(texto_mensaje)

            datos = mensaje.get("datos", {})
            if isinstance(datos, dict):
                resultado = datos.get("resultado_combate")
                if isinstance(resultado, dict):
                    for evento in resultado.get("eventos", []):
                        agregar_evento(evento)

            if mensaje.get("estado") is not None:
                refrescar_estado(mensaje["estado"])

        if window2.winfo_exists():
            window2.after(300, procesar_mensajes_red)

    def buscar_puerto_disponible(puerto_preferido):
        """
        Descripcion:
            Busca un puerto disponible para crear el servidor local. Si
            el puerto elegido esta bloqueado por permisos o por otro
            programa, prueba puertos cercanos y una segunda zona segura.

        Entradas:
            puerto_preferido (int): Puerto escrito por el usuario.

        Salidas:
            tuple[bool, int, str]: Indica si encontro puerto, el puerto
            disponible y un mensaje descriptivo.

        Restricciones:
            - puerto_preferido debe ser entero.
            - Solo prueba puertos TCP locales.
        """
        puertos_a_probar = [puerto_preferido]
        puertos_a_probar.extend(range(5001, 5011))
        puertos_a_probar.extend(range(5050, 5061))

        puertos_revisados = []
        for puerto_candidato in puertos_a_probar:
            if puerto_candidato in puertos_revisados:
                continue
            puertos_revisados.append(puerto_candidato)
            try:
                socket_prueba = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_prueba.bind(("0.0.0.0", puerto_candidato))
                socket_prueba.close()
                if puerto_candidato == puerto_preferido:
                    return True, puerto_candidato, "Puerto disponible."
                return (
                    True,
                    puerto_candidato,
                    f"El puerto {puerto_preferido} no estaba disponible. "
                    f"Se usara el puerto {puerto_candidato}.",
                )
            except OSError:
                continue

        return (
            False,
            puerto_preferido,
            "No se encontro un puerto disponible. Prueba con otro puerto "
            "o revisa permisos/firewall.",
        )

    def iniciar_servidor_local(puerto):
        """
        Descripcion:
            Crea un servidor de partida desde la misma interfaz y lo
            ejecuta en un hilo para que Tkinter no se congele.

        Entradas:
            puerto (int): Puerto donde escuchara el servidor local.

        Salidas:
            tuple[bool, str]: Resultado de iniciar el servidor.

        Restricciones:
            - El puerto debe estar libre.
            - Solo debe existir un servidor local por ventana Play.
        """
        if servidor_local["instancia"] is not None:
            return True, "Servidor local ya estaba iniciado."

        puerto_encontrado, puerto_final, mensaje_puerto = buscar_puerto_disponible(puerto)
        if not puerto_encontrado:
            return False, mensaje_puerto

        servidor = ServidorPartida(puerto=puerto_final)
        hilo_servidor = threading.Thread(target=servidor.iniciar, daemon=True)
        servidor_local["instancia"] = servidor
        servidor_local["hilo"] = hilo_servidor
        hilo_servidor.start()
        campo_puerto.delete(0, tk.END)
        campo_puerto.insert(0, str(puerto_final))

        if puerto_final != puerto:
            return True, f"{mensaje_puerto} Servidor creado correctamente."
        return True, f"Servidor creado. Otro jugador puede unirse al puerto {puerto_final}."

    def conectar_cliente(host, usuario, rol, puerto):
        """
        Descripcion:
            Conecta el ClientePartida al servidor indicado y pide el
            estado inicial si la conexion fue exitosa.

        Entradas:
            host (str): IP del servidor.
            usuario (str): Nombre de usuario.
            rol (str): Rol solicitado.
            puerto (int): Puerto del servidor.

        Salidas:
            None: Actualiza mensajes visibles.

        Restricciones:
            - El servidor debe estar escuchando.
        """
        exito, mensaje = adaptador.conectar(host, usuario, rol, puerto)
        etiqueta_conexion.config(text=mensaje, fg="green" if exito else "red")
        agregar_evento(mensaje)
        if exito:
            adaptador.cliente.obtener_estado()

    def conectar_click():
        """
        Descripcion:
            Permite elegir entre crear un servidor local o unirse a una
            partida existente, y luego conecta el cliente de esta ventana.

        Entradas:
            Ninguna.

        Salidas:
            None: Actualiza mensajes visibles y estado de conexion.

        Restricciones:
            - El puerto debe ser un entero.
            - Para unirse a una partida, la IP debe apuntar a un servidor activo.
        """
        host = campo_ip.get().strip()
        usuario = campo_usuario.get().strip()
        rol = variable_rol.get().strip()
        modo_conexion = variable_modo_conexion.get()
        try:
            puerto = int(campo_puerto.get())
        except ValueError:
            messagebox.showwarning("Puerto invalido", "El puerto debe ser un numero entero.")
            return

        if modo_conexion == "crear_servidor":
            exito_servidor, mensaje_servidor = iniciar_servidor_local(puerto)
            etiqueta_conexion.config(text=mensaje_servidor, fg="green" if exito_servidor else "red")
            agregar_evento(mensaje_servidor)
            if not exito_servidor:
                return
            puerto_conexion = int(campo_puerto.get())
            window2.after(250, lambda: conectar_cliente("127.0.0.1", usuario, rol, puerto_conexion))
            return

        conectar_cliente(host, usuario, rol, puerto)

    boton_conectar = tk.Button(panel_conexion, text="Continuar", font=("Arial", 11, "bold"), bg="lightgreen", command=conectar_click)
    boton_conectar.grid(row=1, column=8, padx=8)

    panel_compras = tk.Frame(window2)
    panel_compras.place(relx=0.50, rely=0.82, anchor="n")

    variable_tipo_torre = tk.StringVar(value=TIPOS_TORRE[0])
    variable_tipo_unidad = tk.StringVar(value=TIPOS_UNIDAD[0])

    tk.Label(panel_compras, text="Defensa", font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=5)
    tk.OptionMenu(panel_compras, variable_tipo_torre, *TIPOS_TORRE).grid(row=1, column=0, padx=3)
    campo_fila_defensa = tk.Entry(panel_compras, width=5)
    campo_fila_defensa.insert(0, "3")
    campo_fila_defensa.grid(row=1, column=1, padx=3)
    campo_columna_defensa = tk.Entry(panel_compras, width=5)
    campo_columna_defensa.insert(0, "2")
    campo_columna_defensa.grid(row=1, column=2, padx=3)

    def obtener_posicion_defensa():
        """
        Descripcion:
            Lee la fila y columna de defensa desde los campos de texto.

        Entradas:
            Ninguna.

        Salidas:
            tuple[int, int]: Fila y columna ingresadas.
            None: Si algun valor no es entero.

        Restricciones:
            - Los campos deben contener numeros enteros.
        """
        try:
            return int(campo_fila_defensa.get()), int(campo_columna_defensa.get())
        except ValueError:
            messagebox.showwarning("Posicion invalida", "Fila y columna deben ser numeros enteros.")
            return None

    def comprar_torre_click():
        posicion = obtener_posicion_defensa()
        if posicion is not None:
            exito, mensaje = adaptador.cliente.comprar_torre(variable_tipo_torre.get(), posicion[0], posicion[1])
            agregar_evento(mensaje)
            if not exito:
                messagebox.showwarning("No se pudo enviar", mensaje)

    def comprar_muro_click():
        posicion = obtener_posicion_defensa()
        if posicion is not None:
            exito, mensaje = adaptador.cliente.comprar_muro(posicion[0], posicion[1])
            agregar_evento(mensaje)
            if not exito:
                messagebox.showwarning("No se pudo enviar", mensaje)

    tk.Button(panel_compras, text="Comprar torre", bg="lightblue", command=comprar_torre_click).grid(row=1, column=3, padx=3)
    tk.Button(panel_compras, text="Comprar muro", bg="lightgray", command=comprar_muro_click).grid(row=1, column=4, padx=3)

    tk.Label(panel_compras, text="Ataque", font=("Arial", 11, "bold")).grid(row=2, column=0, columnspan=5, pady=(10, 0))
    tk.OptionMenu(panel_compras, variable_tipo_unidad, *TIPOS_UNIDAD).grid(row=3, column=0, padx=3)
    campo_fila_unidad = tk.Entry(panel_compras, width=5)
    campo_fila_unidad.insert(0, "10")
    campo_fila_unidad.grid(row=3, column=1, padx=3)
    campo_columna_unidad = tk.Entry(panel_compras, width=5)
    campo_columna_unidad.insert(0, "2")
    campo_columna_unidad.grid(row=3, column=2, padx=3)

    def comprar_unidad_click():
        """
        Descripcion:
            Envia al servidor una solicitud para comprar unidad con la
            posicion escrita en la interfaz.

        Entradas:
            Ninguna.

        Salidas:
            None: Envia la accion por red o muestra un error.

        Restricciones:
            - La fila y columna deben ser enteros.
        """
        try:
            fila = int(campo_fila_unidad.get())
            columna = int(campo_columna_unidad.get())
        except ValueError:
            messagebox.showwarning("Posicion invalida", "Fila y columna deben ser numeros enteros.")
            return

        exito, mensaje = adaptador.cliente.comprar_unidad(variable_tipo_unidad.get(), fila, columna)
        agregar_evento(mensaje)
        if not exito:
            messagebox.showwarning("No se pudo enviar", mensaje)

    tk.Button(panel_compras, text="Comprar unidad", bg="salmon", command=comprar_unidad_click).grid(row=3, column=3, padx=3)

    panel_combate = tk.Frame(window2)
    panel_combate.place(relx=0.20, rely=0.82, anchor="n")

    def enviar_accion_simple(funcion_cliente):
        """
        Descripcion:
            Ejecuta una accion simple del cliente y muestra el
            resultado del envio en la lista de eventos.

        Entradas:
            funcion_cliente (function): Metodo sin parametros del
                cliente de red.

        Salidas:
            None: Envia accion al servidor.

        Restricciones:
            - Debe haber conexion activa para que el envio sea exitoso.
        """
        exito, mensaje = funcion_cliente()
        agregar_evento(mensaje)
        if not exito:
            messagebox.showwarning("No se pudo enviar", mensaje)

    tk.Button(panel_combate, text="Iniciar combate", font=("Arial", 11, "bold"), bg="orange", command=lambda: enviar_accion_simple(adaptador.cliente.iniciar_combate)).grid(row=0, column=0, padx=4, pady=3)
    tk.Button(panel_combate, text="Pausar", font=("Arial", 11), command=lambda: enviar_accion_simple(adaptador.cliente.pausar_combate)).grid(row=0, column=1, padx=4, pady=3)
    tk.Button(panel_combate, text="Actualizar", font=("Arial", 11), command=lambda: enviar_accion_simple(adaptador.cliente.obtener_estado)).grid(row=1, column=0, padx=4, pady=3)
    tk.Button(panel_combate, text="Turno manual", font=("Arial", 11), command=lambda: enviar_accion_simple(adaptador.cliente.ejecutar_combate)).grid(row=1, column=1, padx=4, pady=3)

    def cerrar_ventana():
        adaptador.cerrar()
        detener_servidor_local()
        cerrar_todo()

    window2.after(300, procesar_mensajes_red)
    window2.protocol("WM_DELETE_WINDOW", cerrar_ventana)
