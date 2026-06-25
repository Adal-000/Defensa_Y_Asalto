#=======================================#
# Archivo para manejo de ventanas main
#=======================================#


import tkinter as tk


def main(root, GoPerfil, GoPlay, GoConfig, cerrar_todo, configurar_ventana):
    """
    Descripción:
        Crea la ventana principal del juego Defensa y Asalto.

    Entradas:
        root: ventana raíz oculta.
        GoPerfil: función para abrir la ventana de perfil.
        GoPlay: función para abrir la ventana de juego.
        GoConfig: función para abrir la ventana de configuración.
        cerrar_todo: función para cerrar completamente el programa.
        configurar_ventana: función que centra y configura la ventana.

    Salidas:
        No retorna ningún valor.

    Restricciones:
        Al abrir otra ventana, esta ventana principal se destruye.
    """

    window = tk.Toplevel(root)
    configurar_ventana(window, "Defensa y Asalto")

    def GoPerfilR():
        window.destroy()
        GoPerfil()

    def GoPlayR():
        window.destroy()
        GoPlay()

    def GoConfigR():
        window.destroy()
        GoConfig()

    contenedor = tk.Frame(window)
    contenedor.place(relx=0.5, rely=0.5, anchor="center")

    titulo = tk.Label(
        contenedor,
        text="Defensa y Asalto",
        font=("Arial", 36, "bold"),
        width=28,
        height=2,
        relief="solid",
        bd=3
    )

    titulo.grid(
        row=0,
        column=0,
        columnspan=2,
        padx=20,
        pady=(0, 60)
    )

    boton_perfil = tk.Button(
        contenedor,
        text="Perfil",
        font=("Arial", 20, "bold"),
        width=16,
        height=3,
        command=GoPerfilR
    )

    boton_play = tk.Button(
        contenedor,
        text="Play",
        font=("Arial", 20, "bold"),
        width=16,
        height=3,
        command=GoPlayR
    )

    boton_config = tk.Button(
        contenedor,
        text="Config",
        font=("Arial", 20, "bold"),
        width=16,
        height=3,
        command=GoConfigR
    )

    boton_cerrar = tk.Button(
        contenedor,
        text="Cerrar juego",
        font=("Arial", 20, "bold"),
        width=16,
        height=3,
        command=cerrar_todo
    )

    boton_perfil.grid(row=1, column=0, padx=35, pady=20)
    boton_play.grid(row=1, column=1, padx=35, pady=20)

    boton_config.grid(row=2, column=0, padx=35, pady=20)
    boton_cerrar.grid(row=2, column=1, padx=35, pady=20)

    window.protocol("WM_DELETE_WINDOW", cerrar_todo)