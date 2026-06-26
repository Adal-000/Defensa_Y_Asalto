#=======================================#
# Archivo para manejo de ventanas main
#=======================================#

import tkinter as tk

COLOR_FONDO = "#18202b"
COLOR_PANEL = "#243244"
COLOR_PANEL_CLARO = "#31445c"
COLOR_DORADO = "#f6b73c"
COLOR_ROJO = "#d94b4b"
COLOR_AZUL = "#3f8cff"
COLOR_VERDE = "#4caf50"
COLOR_MORADO = "#7e57c2"
COLOR_TEXTO = "#f5f7fb"
COLOR_TEXTO_SUAVE = "#b8c7d9"


def main(root, GoPerfil, GoPlay, GoConfig, cerrar_todo, configurar_ventana,
         obtener_usuario_actual):
    """
    Descripción:
        Crea la ventana principal del juego Defensa y Asalto con un
        aspecto más cercano a menú de videojuego.
    """

    window = tk.Toplevel(root)
    configurar_ventana(window, "Defensa y Asalto")
    window.configure(bg=COLOR_FONDO)

    def GoPerfilR():
        window.destroy()
        GoPerfil()

    def GoPlayR():
        window.destroy()
        GoPlay()

    def GoConfigR():
        window.destroy()
        GoConfig()

    def aplicar_hover(boton, color_base, color_hover):
        boton.bind("<Enter>", lambda _evento: boton.config(bg=color_hover, relief="sunken"))
        boton.bind("<Leave>", lambda _evento: boton.config(bg=color_base, relief="raised"))

    def crear_boton_menu(parent, texto, icono, color, comando):
        boton = tk.Button(
            parent,
            text=f"{icono}\n{texto}",
            font=("Arial", 17, "bold"),
            width=16,
            height=4,
            bg=color,
            fg="white",
            activebackground=COLOR_DORADO,
            activeforeground="#111111",
            relief="raised",
            bd=4,
            cursor="hand2",
            command=comando,
        )
        aplicar_hover(boton, color, COLOR_DORADO)
        return boton

    fondo = tk.Canvas(window, width=1150, height=700, bg=COLOR_FONDO, highlightthickness=0)
    fondo.place(x=0, y=0)

    # Decoración simple tipo tablero/base.
    for x in range(0, 1150, 80):
        fondo.create_line(x, 0, x + 220, 700, fill="#202b3a", width=1)
    for y in range(40, 700, 80):
        fondo.create_line(0, y, 1150, y, fill="#1f2a38", width=1)
    fondo.create_polygon(0, 700, 260, 520, 0, 430, fill="#22324a", outline="")
    fondo.create_polygon(1150, 700, 880, 520, 1150, 430, fill="#3a2630", outline="")

    nombre_usuario_actual = obtener_usuario_actual() or "Invitado"

    barra_sesion = tk.Label(
        window,
        text=f"Comandante: {nombre_usuario_actual}",
        font=("Arial", 12, "bold"),
        bg="#111821",
        fg=COLOR_DORADO,
        padx=18,
        pady=8,
        relief="solid",
        bd=2,
    )
    barra_sesion.place(x=24, y=22)

    panel_titulo = tk.Frame(window, bg=COLOR_PANEL, highlightbackground=COLOR_DORADO, highlightthickness=3)
    panel_titulo.place(relx=0.5, y=130, anchor="center", width=840, height=125)

    titulo = tk.Label(
        panel_titulo,
        text="DEFENSA Y ASALTO",
        font=("Arial", 36, "bold"),
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO,
    )
    titulo.pack(pady=(20, 0))

    subtitulo = tk.Label(
        panel_titulo,
        text="Construye la base, despliega tropas y domina el campo de batalla",
        font=("Arial", 12, "bold"),
        bg=COLOR_PANEL,
        fg=COLOR_TEXTO_SUAVE,
    )
    subtitulo.pack(pady=(4, 0))

    panel_menu = tk.Frame(window, bg=COLOR_PANEL_CLARO, highlightbackground="#0d1118", highlightthickness=4)
    panel_menu.place(relx=0.5, y=410, anchor="center", width=760, height=360)

    etiqueta_menu = tk.Label(
        panel_menu,
        text="MENÚ PRINCIPAL",
        font=("Arial", 16, "bold"),
        bg=COLOR_PANEL_CLARO,
        fg=COLOR_DORADO,
    )
    etiqueta_menu.grid(row=0, column=0, columnspan=2, pady=(22, 8))

    boton_perfil = crear_boton_menu(panel_menu, "Perfil", "🛡", COLOR_AZUL, GoPerfilR)
    boton_play = crear_boton_menu(panel_menu, "Jugar", "⚔", COLOR_ROJO, GoPlayR)
    boton_config = crear_boton_menu(panel_menu, "Config", "⚙", COLOR_MORADO, GoConfigR)
    boton_cerrar = crear_boton_menu(panel_menu, "Cerrar", "⏻", "#455a64", cerrar_todo)

    boton_perfil.grid(row=1, column=0, padx=42, pady=18)
    boton_play.grid(row=1, column=1, padx=42, pady=18)
    boton_config.grid(row=2, column=0, padx=42, pady=18)
    boton_cerrar.grid(row=2, column=1, padx=42, pady=18)

    consejo = tk.Label(
        window,
        text="Tip: configura IP/puerto antes de crear una partida en red.",
        font=("Arial", 11, "italic"),
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO_SUAVE,
    )
    consejo.place(relx=0.5, y=635, anchor="center")

    window.protocol("WM_DELETE_WINDOW", cerrar_todo)
