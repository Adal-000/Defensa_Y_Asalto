#=======================================#
# Archivo para iniciar sesion antes de jugar
#=======================================#

<<<<<<< HEAD
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
=======
import tkinter as tk
>>>>>>> origin/feature/interfaz


FACCIONES = ["España", "Inglaterra", "Alemania", "Rusia", "Italia", "EE.UU"]


def play(root, GoMain, GoMapa, cerrar_todo, configurar_ventana, obtener_usuario_actual):
    """
    Descripción:
        Crea la ventana Play. Esta pantalla contiene los datos básicos
        de conexión y el esqueleto para elegir una facción antes de
        pasar a la ventana del mapa.

    Entradas:
        root: ventana raíz oculta.
        GoMain: función para volver al menú principal.
        GoMapa: función para abrir la ventana de mapa.
        cerrar_todo: función para cerrar completamente el programa.
        configurar_ventana: función que centra y configura la ventana.
        obtener_usuario_actual: función que devuelve el usuario actual.

    Salidas:
        No retorna ningún valor.

    Restricciones:
        Solo se puede confirmar una facción a la vez. Después de elegirla,
        no se puede cambiar hasta presionar Cambiar facción.
    """

    window2 = tk.Toplevel(root)
    configurar_ventana(window2, "Play")

<<<<<<< HEAD
    cola_mensajes = queue.Queue()
    adaptador = AdaptadorClienteTkinter(cola_mensajes)
    estado_actual = {"datos": None, "mensaje_final_mostrado": False}
    servidor_local = {"instancia": None, "hilo": None}

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
=======
    faccion_temporal = tk.StringVar(value="")
    faccion_confirmada = tk.StringVar(value="")
    seleccion_bloqueada = tk.BooleanVar(value=False)

    def GoMainR():
>>>>>>> origin/feature/interfaz
        window2.destroy()
        GoMain()

    def GoMapaR():
        window2.destroy()
        GoMapa()

    boton_volver = tk.Button(
        window2,
        text="Volver",
        font=("Arial", 12, "bold"),
        width=10,
        height=2,
        bg="red",
        command=GoMainR
    )
    boton_volver.place(x=20, y=20)

    titulo = tk.Label(
        window2,
        text="Play",
        font=("Arial", 28, "bold")
    )
    titulo.place(relx=0.5, y=45, anchor="center")

    # --- Datos de conexión ----------------------------------------------

<<<<<<< HEAD
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
=======
    panel_conexion = tk.Frame(window2, relief="solid", bd=2, padx=12, pady=10)
    panel_conexion.place(relx=0.5, y=115, anchor="center")

    campos_conexion = [
        ("IP", "127.0.0.1"),
        ("Usuario", obtener_usuario_actual() or "Invitado"),
        ("Rol", "Sin rol"),
        ("Puerto", "0000")
    ]

    for indice, (nombre_campo, valor_inicial) in enumerate(campos_conexion):
        etiqueta = tk.Label(
            panel_conexion,
            text=nombre_campo,
            font=("Arial", 11, "bold")
        )
        etiqueta.grid(row=0, column=indice, padx=8, pady=(0, 4))

        campo = tk.Entry(panel_conexion, font=("Arial", 11), width=16, justify="center")
        campo.insert(0, valor_inicial)
        campo.grid(row=1, column=indice, padx=8)
>>>>>>> origin/feature/interfaz

    boton_conectar = tk.Button(
        panel_conexion,
        text="Conectar",
        font=("Arial", 11, "bold"),
        width=12,
        bg="lightgreen"
    )
    boton_conectar.grid(row=1, column=4, padx=(16, 8))

    estado_conexion = tk.Label(
        panel_conexion,
        text="Sin conexión",
        font=("Arial", 11, "bold"),
        fg="red",
        width=14
    )
    estado_conexion.grid(row=1, column=5, padx=8)

    # --- Selección de facción -------------------------------------------

    etiqueta_facciones = tk.Label(
        window2,
        text="Selecciona una facción",
        font=("Arial", 18, "bold")
    )
    etiqueta_facciones.place(relx=0.5, y=185, anchor="center")

    panel_facciones = tk.Frame(window2)
    panel_facciones.place(relx=0.5, y=360, anchor="center")

    botones_faccion = {}

    def refrescar_botones():
        for nombre_faccion, boton in botones_faccion.items():
            if nombre_faccion == faccion_temporal.get():
                boton.config(relief="sunken", bg="#b7d7ff")
            else:
                boton.config(relief="raised", bg="SystemButtonFace")

    def seleccionar_faccion(nombre_faccion):
        if seleccion_bloqueada.get():
            texto_faccion.config(text="Facción elegida")
            return

        faccion_temporal.set(nombre_faccion)
        texto_faccion.config(text=f"Facción {nombre_faccion}")
        refrescar_botones()

    for indice, nombre_faccion in enumerate(FACCIONES):
        fila = indice // 3
        columna = indice % 3

        boton_faccion = tk.Button(
            panel_facciones,
            text=f"\n[ Espacio bandera ]\n\n{nombre_faccion}",
            font=("Arial", 13, "bold"),
            width=20,
            height=6,
            command=lambda faccion=nombre_faccion: seleccionar_faccion(faccion)
        )
        boton_faccion.grid(row=fila, column=columna, padx=18, pady=14)
        botones_faccion[nombre_faccion] = boton_faccion

    # --- Acciones inferiores --------------------------------------------

    texto_soldado = tk.Label(
        window2,
        text="Soldado no elegido",
        font=("Arial", 13, "bold"),
        width=24,
        height=2,
        relief="solid",
        bd=2
    )
    texto_soldado.place(x=325, y=625, anchor="center")

    texto_faccion = tk.Label(
        window2,
        text="Facción sin elegir",
        font=("Arial", 13, "bold"),
        width=24,
        height=2,
        relief="solid",
        bd=2
    )
    texto_faccion.place(x=575, y=625, anchor="center")

<<<<<<< HEAD
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
=======
    def elegir_faccion_click():
        if not faccion_temporal.get():
            texto_faccion.config(text="Elige una facción antes")
            return

        faccion_confirmada.set(faccion_temporal.get())
        seleccion_bloqueada.set(True)
        texto_faccion.config(text="Facción elegida")

    def cambiar_faccion_click():
        seleccion_bloqueada.set(False)
        faccion_confirmada.set("")
        if faccion_temporal.get():
            texto_faccion.config(text=f"Facción {faccion_temporal.get()}")
        else:
            texto_faccion.config(text="Facción sin elegir")
>>>>>>> origin/feature/interfaz

    def iniciar_combate_click():
        if not faccion_confirmada.get():
            texto_faccion.config(text="Elige una facción antes")
            return
        GoMapaR()

    boton_cambiar_faccion = tk.Button(
        window2,
        text="Cambiar facción",
        font=("Arial", 12, "bold"),
        width=16,
        bg="#ffd36b",
        command=cambiar_faccion_click
    )
    boton_cambiar_faccion.place(x=85, y=575)

    boton_elegir_faccion = tk.Button(
        window2,
        text="Elegir facción",
        font=("Arial", 12, "bold"),
        width=16,
        bg="lightgreen",
        command=elegir_faccion_click
    )
    boton_elegir_faccion.place(x=85, y=635)

    boton_iniciar_combate = tk.Button(
        window2,
        text="Iniciar combate",
        font=("Arial", 13, "bold"),
        width=18,
        height=2,
        bg="orange",
        command=iniciar_combate_click
    )
    boton_iniciar_combate.place(x=875, y=610)

<<<<<<< HEAD
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
=======
    window2.protocol("WM_DELETE_WINDOW", cerrar_todo)
>>>>>>> origin/feature/interfaz
