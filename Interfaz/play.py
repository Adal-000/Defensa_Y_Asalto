#=======================================#
# Archivo para jugar
#=======================================#

import tkinter as tk


def play(root, GoMain, cerrar_todo, configurar_ventana):
    """
    Descripción:
        Crea la ventana de juego.

    Entradas:
        root: ventana raíz oculta.
        GoMain: función para volver al menú principal.
        cerrar_todo: función para cerrar completamente el programa.
        configurar_ventana: función que centra y configura la ventana.

    Salidas:
        No retorna ningún valor.

    Restricciones:
        El botón Volver destruye esta ventana y abre nuevamente el menú principal.
    """

    window2 = tk.Toplevel(root)
    configurar_ventana(window2, "Play")

    def GoMainR():
        window2.destroy()
        GoMain()

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
        font=("Arial", 36, "bold")
    )

    titulo.place(relx=0.5, rely=0.35, anchor="center")

    texto = tk.Label(
        window2,
        text="Aquí irá la pantalla principal del juego",
        font=("Arial", 20)
    )

    texto.place(relx=0.5, rely=0.48, anchor="center")

    window2.protocol("WM_DELETE_WINDOW", cerrar_todo)