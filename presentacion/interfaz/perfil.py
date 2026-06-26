#=======================================#
# Archivo para ver sus puntajes
#=======================================#

import tkinter as tk

from aplicacion import app

COLOR_FONDO = "#18202b"
COLOR_PANEL = "#243244"
COLOR_PANEL_CLARO = "#31445c"
COLOR_DORADO = "#f6b73c"
COLOR_TEXTO = "#f5f7fb"
COLOR_SUAVE = "#b8c7d9"
COLOR_AZUL = "#3f8cff"
COLOR_ROJO = "#d94b4b"
COLOR_NARANJA = "#ef6c00"


def perfil(root, GoMain, GoPuntajes, cerrar_todo, configurar_ventana,
           obtener_usuario_actual):
    """
    Descripción:
        Crea la ventana de perfil del jugador con estilo visual de juego.
    """

    window1 = tk.Toplevel(root)
    configurar_ventana(window1, "Perfil")
    window1.configure(bg=COLOR_FONDO)

    def GoMainR():
        window1.destroy()
        GoMain()

    def GoPuntajesR():
        window1.destroy()
        GoPuntajes()

    def hover(boton, base, hover_color):
        boton.bind("<Enter>", lambda _evento: boton.config(bg=hover_color, relief="sunken"))
        boton.bind("<Leave>", lambda _evento: boton.config(bg=base, relief="raised"))

    fondo = tk.Canvas(window1, width=1150, height=700, bg=COLOR_FONDO, highlightthickness=0)
    fondo.place(x=0, y=0)
    for x in range(-160, 1150, 90):
        fondo.create_line(x, 0, x + 260, 700, fill="#202b3a", width=1)
    fondo.create_polygon(0, 700, 300, 500, 0, 400, fill="#22324a", outline="")
    fondo.create_polygon(1150, 700, 850, 500, 1150, 400, fill="#3a2630", outline="")

    boton_volver = tk.Button(window1, text="Volver", font=("Arial", 12, "bold"), width=10, height=2, bg=COLOR_ROJO, fg="white", command=GoMainR, cursor="hand2", bd=3)
    boton_volver.place(x=24, y=24)
    hover(boton_volver, COLOR_ROJO, COLOR_DORADO)

    boton_puntajes = tk.Button(window1, text="🏆 Puntajes", font=("Arial", 12, "bold"), width=13, height=2, bg=COLOR_AZUL, fg="white", command=GoPuntajesR, cursor="hand2", bd=3)
    boton_puntajes.place(x=142, y=24)
    hover(boton_puntajes, COLOR_AZUL, COLOR_DORADO)

    nombre_usuario_actual = obtener_usuario_actual()
    datos_jugador = app.obtener_jugador(nombre_usuario_actual) if nombre_usuario_actual is not None else None

    panel = tk.Frame(window1, bg=COLOR_PANEL, highlightbackground=COLOR_DORADO, highlightthickness=3)
<<<<<<< ours
    panel.place(relx=0.5, rely=0.52, anchor="center", width=760, height=480)

    titulo = tk.Label(panel, text="PERFIL DEL COMANDANTE", font=("Arial", 28, "bold"), bg=COLOR_PANEL, fg=COLOR_TEXTO)
    titulo.pack(pady=(28, 4))

    subtitulo = tk.Label(panel, text="Resumen de trayectoria y victorias por rol", font=("Arial", 12, "bold"), bg=COLOR_PANEL, fg=COLOR_SUAVE)
    subtitulo.pack(pady=(0, 22))

    contenido = tk.Frame(panel, bg=COLOR_PANEL)
    contenido.pack(fill="both", expand=True, padx=42, pady=10)
=======
    panel.place(relx=0.5, y=355, anchor="center", width=760, height=430)

    titulo = tk.Label(panel, text="PERFIL DEL COMANDANTE", font=("Arial", 28, "bold"), bg=COLOR_PANEL, fg=COLOR_TEXTO)
    titulo.pack(pady=(20, 4))

    subtitulo = tk.Label(panel, text="Resumen de trayectoria y victorias por rol", font=("Arial", 12, "bold"), bg=COLOR_PANEL, fg=COLOR_SUAVE)
    subtitulo.pack(pady=(0, 14))

    contenido = tk.Frame(panel, bg=COLOR_PANEL)
    contenido.pack(fill="both", expand=True, padx=42, pady=6)
>>>>>>> theirs
    contenido.grid_columnconfigure(0, weight=1)
    contenido.grid_columnconfigure(1, weight=1)

    if datos_jugador is not None:
        total_victorias = datos_jugador["total_victorias"]
        tarjeta_usuario = tk.Frame(contenido, bg=COLOR_PANEL_CLARO, highlightbackground="#111821", highlightthickness=2)
<<<<<<< ours
        tarjeta_usuario.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 22))
=======
        tarjeta_usuario.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
>>>>>>> theirs
        tk.Label(tarjeta_usuario, text="Usuario", font=("Arial", 12, "bold"), bg=COLOR_PANEL_CLARO, fg=COLOR_SUAVE).pack(pady=(12, 0))
        tk.Label(tarjeta_usuario, text=datos_jugador["nombre_usuario"], font=("Arial", 24, "bold"), bg=COLOR_PANEL_CLARO, fg=COLOR_DORADO).pack(pady=(0, 12))

        estadisticas = [
            ("Defensor", datos_jugador["victorias_defensor"], COLOR_AZUL, "🛡"),
            ("Atacante", datos_jugador["victorias_atacante"], COLOR_NARANJA, "⚔"),
        ]
        for columna, (nombre, valor, color, icono) in enumerate(estadisticas):
            tarjeta = tk.Frame(contenido, bg="#f5f7fb", highlightbackground=color, highlightthickness=3)
            tarjeta.grid(row=1, column=columna, sticky="nsew", padx=14, pady=4)
            tk.Label(tarjeta, text=icono, font=("Arial", 24), bg="#f5f7fb", fg=color).pack(pady=(14, 0))
            tk.Label(tarjeta, text=nombre, font=("Arial", 13, "bold"), bg="#f5f7fb", fg="#263238").pack()
            tk.Label(tarjeta, text=str(valor), font=("Arial", 30, "bold"), bg="#f5f7fb", fg=color).pack(pady=(0, 16))

        etiqueta_total = tk.Label(contenido, text=f"Total de victorias: {total_victorias}", font=("Arial", 16, "bold"), bg="#173a59", fg="white", pady=12)
<<<<<<< ours
        etiqueta_total.grid(row=2, column=0, columnspan=2, sticky="ew", padx=14, pady=(24, 0))
=======
        etiqueta_total.grid(row=2, column=0, columnspan=2, sticky="ew", padx=14, pady=(14, 0))
>>>>>>> theirs
    else:
        tk.Label(panel, text="No se encontró información del jugador actual.", font=("Arial", 16, "bold"), bg=COLOR_PANEL, fg=COLOR_SUAVE).pack(expand=True)

    window1.protocol("WM_DELETE_WINDOW", cerrar_todo)
