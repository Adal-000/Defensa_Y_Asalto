#=======================================#
# Archivo para iniciar sesion antes de jugar
#=======================================#

import tkinter as tk


FACCIONES = ["Rusia", "España", "Italia", "EE.UU", "Alemania", "Francia"]


# Estado temporal mientras se integra la conexión real entre jugadores.
ESTADO_SALA = {
    "jugadores_conectados": 2,
    "jugador_actual": "",
    "contrincante": "Contrincante",
    "facciones_confirmadas": {},
    "jugadores_listos": set()
}


def play(root, GoMain, GoMapa, cerrar_todo, configurar_ventana, obtener_usuario_actual):
    """
    Descripción:
        Crea la ventana Play. Permite seleccionar una facción, confirmarla,
        cambiarla antes de jugar y avanzar al mapa cuando la sala tiene dos
        jugadores conectados y ambos ya eligieron facción.
    """

    window2 = tk.Toplevel(root)
    configurar_ventana(window2, "Play")

    nombre_jugador = obtener_usuario_actual() or "Invitado"
    ESTADO_SALA["jugador_actual"] = nombre_jugador
    ESTADO_SALA["facciones_confirmadas"].setdefault(ESTADO_SALA["contrincante"], "")

    faccion_temporal = tk.StringVar(value="")
    faccion_confirmada = tk.StringVar(value=ESTADO_SALA["facciones_confirmadas"].get(nombre_jugador, ""))
    seleccion_bloqueada = tk.BooleanVar(value=bool(faccion_confirmada.get()))
    jugar_solicitado = tk.BooleanVar(value=False)

    def GoMainR():
        window2.destroy()
        GoMain()

    def GoMapaR():
        window2.destroy()
        GoMapa({
            "jugador": nombre_jugador,
            "contrincante": ESTADO_SALA["contrincante"],
            "faccion": faccion_confirmada.get(),
            "faccion_contrincante": ESTADO_SALA["facciones_confirmadas"].get(ESTADO_SALA["contrincante"], "")
        })

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

    titulo = tk.Label(window2, text="Play", font=("Arial", 28, "bold"))
    titulo.place(relx=0.5, y=45, anchor="center")

    # --- Datos de conexión ----------------------------------------------

    panel_conexion = tk.Frame(window2, relief="solid", bd=2, padx=12, pady=10)
    panel_conexion.place(relx=0.5, y=115, anchor="center")

    campos_conexion = [
        ("IP", "127.0.0.1"),
        ("Usuario", nombre_jugador),
        ("Rol", "Sala"),
        ("Puerto", "0000")
    ]

    for indice, (nombre_campo, valor_inicial) in enumerate(campos_conexion):
        etiqueta = tk.Label(panel_conexion, text=nombre_campo, font=("Arial", 11, "bold"))
        etiqueta.grid(row=0, column=indice, padx=8, pady=(0, 4))

        campo = tk.Entry(panel_conexion, font=("Arial", 11), width=16, justify="center")
        campo.insert(0, valor_inicial)
        campo.grid(row=1, column=indice, padx=8)

    estado_conexion = tk.Label(
        panel_conexion,
        text="2 conectados",
        font=("Arial", 11, "bold"),
        fg="green",
        width=14
    )
    estado_conexion.grid(row=1, column=5, padx=8)

    def conectar_click():
        ESTADO_SALA["jugadores_conectados"] = 2
        estado_conexion.config(text="2 conectados", fg="green")
        mensaje_estado.config(text="Elige una facción")

    boton_conectar = tk.Button(
        panel_conexion,
        text="Conectar",
        font=("Arial", 11, "bold"),
        width=12,
        bg="lightgreen",
        command=conectar_click
    )
    boton_conectar.grid(row=1, column=4, padx=(16, 8))

    # --- Selección de facción -------------------------------------------

    panel_facciones = tk.Frame(window2)
    panel_facciones.place(relx=0.5, y=315, anchor="center")

    botones_faccion = {}

    def facciones_ocupadas():
        return {
            faccion for jugador, faccion in ESTADO_SALA["facciones_confirmadas"].items()
            if jugador != nombre_jugador and faccion
        }

    def refrescar_botones():
        ocupadas = facciones_ocupadas()
        for nombre_faccion, boton in botones_faccion.items():
            if nombre_faccion in ocupadas:
                boton.config(relief="raised", bg="#dddddd", state="disabled")
            else:
                boton.config(state="normal")
                if nombre_faccion == faccion_temporal.get():
                    boton.config(relief="sunken", bg="#b7d7ff")
                else:
                    boton.config(relief="raised", bg="SystemButtonFace")

    def seleccionar_faccion(nombre_faccion):
        if seleccion_bloqueada.get():
            mensaje_estado.config(text="Pulsa Cambiar facción para modificar")
            return
        if nombre_faccion in facciones_ocupadas():
            mensaje_estado.config(text="Esa facción ya fue elegida")
            return

        faccion_temporal.set(nombre_faccion)
        mensaje_estado.config(text=f"Facción seleccionada: {nombre_faccion}")
        refrescar_botones()

    for indice, nombre_faccion in enumerate(FACCIONES):
        fila = indice // 3
        columna = indice % 3

        marco_faccion = tk.Frame(panel_facciones)
        marco_faccion.grid(row=fila, column=columna, padx=20, pady=14)

        caja_bandera = tk.Label(
            marco_faccion,
            text="Bandera",
            font=("Arial", 9, "bold"),
            width=18,
            height=3,
            relief="solid",
            bd=2,
            bg="white"
        )
        caja_bandera.pack(pady=(0, 4))

        boton_faccion = tk.Button(
            marco_faccion,
            text=nombre_faccion,
            font=("Arial", 13, "bold"),
            width=18,
            height=2,
            command=lambda faccion=nombre_faccion: seleccionar_faccion(faccion)
        )
        boton_faccion.pack()
        botones_faccion[nombre_faccion] = boton_faccion

    # --- Acciones inferiores --------------------------------------------

    mensaje_estado = tk.Label(
        window2,
        text="Elige una facción",
        font=("Arial", 13, "bold"),
        width=36,
        height=2,
        relief="solid",
        bd=2
    )
    mensaje_estado.place(relx=0.5, y=595, anchor="center")

    def elegir_faccion_click():
        if not faccion_temporal.get():
            mensaje_estado.config(text="Elige una facción antes")
            return

        faccion_confirmada.set(faccion_temporal.get())
        ESTADO_SALA["facciones_confirmadas"][nombre_jugador] = faccion_confirmada.get()
        seleccion_bloqueada.set(True)
        mensaje_estado.config(text=f"Facción elegida: {faccion_confirmada.get()}")
        refrescar_botones()

    def cambiar_faccion_click():
        seleccion_bloqueada.set(False)
        faccion_temporal.set("")
        faccion_confirmada.set("")
        ESTADO_SALA["facciones_confirmadas"].pop(nombre_jugador, None)
        ESTADO_SALA["jugadores_listos"].discard(nombre_jugador)
        jugar_solicitado.set(False)
        mensaje_estado.config(text="Elige una facción")
        refrescar_botones()

    def iniciar_combate_click():
        if ESTADO_SALA["jugadores_conectados"] < 2:
            mensaje_estado.config(text="Esperando jugador contrincante")
            return
        if not faccion_confirmada.get():
            mensaje_estado.config(text="Elige una facción antes")
            return

        faccion_rival = ESTADO_SALA["facciones_confirmadas"].get(ESTADO_SALA["contrincante"], "")
        if not faccion_rival:
            mensaje_estado.config(text="Esperando jugador contrincante")
            return

        ESTADO_SALA["jugadores_listos"].add(nombre_jugador)
        jugar_solicitado.set(True)
        if len(ESTADO_SALA["jugadores_listos"]) < 2:
            mensaje_estado.config(text="Esperando que ambos pulsen Jugar")
            return

        GoMapaR()

    boton_elegir_faccion = tk.Button(
        window2,
        text="Elegir facción",
        font=("Arial", 12, "bold"),
        width=16,
        bg="lightgreen",
        command=elegir_faccion_click
    )
    boton_elegir_faccion.place(x=65, y=585)

    boton_cambiar_faccion = tk.Button(
        window2,
        text="Cambiar facción",
        font=("Arial", 12, "bold"),
        width=16,
        bg="#ffd36b",
        command=cambiar_faccion_click
    )
    boton_cambiar_faccion.place(x=65, y=635)

    boton_jugar = tk.Button(
        window2,
        text="Jugar",
        font=("Arial", 14, "bold"),
        width=16,
        height=2,
        bg="orange",
        command=iniciar_combate_click
    )
    boton_jugar.place(x=915, y=615, anchor="center")

    if faccion_confirmada.get():
        faccion_temporal.set(faccion_confirmada.get())
        mensaje_estado.config(text=f"Facción elegida: {faccion_confirmada.get()}")
    refrescar_botones()

    window2.protocol("WM_DELETE_WINDOW", cerrar_todo)
