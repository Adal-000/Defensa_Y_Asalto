#=======================================#
# Archivo para iniciar sesion antes de jugar
#=======================================#

import tkinter as tk


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

    faccion_temporal = tk.StringVar(value="")
    faccion_confirmada = tk.StringVar(value="")
    seleccion_bloqueada = tk.BooleanVar(value=False)

    def GoMainR():
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

    window2.protocol("WM_DELETE_WINDOW", cerrar_todo)
