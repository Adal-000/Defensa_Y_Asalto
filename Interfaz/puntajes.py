#=======================================#
# Archivo para ver puntajes de otros
#=======================================#


import tkinter as tk


def puntajes(root, GoPerfil, cerrar_todo, configurar_ventana):
    """
    Descripción:
        Crea la ventana de puntajes del jugador y puntajes mundiales.

    Entradas:
        root: ventana raíz oculta.
        GoPerfil: función para volver a la ventana de perfil.
        cerrar_todo: función para cerrar completamente el programa.
        configurar_ventana: función que centra y configura la ventana.

    Salidas:
        No retorna ningún valor.

    Restricciones:
        El botón Volver destruye esta ventana y abre nuevamente Perfil.
    """

    window_puntajes = tk.Toplevel(root)
    configurar_ventana(window_puntajes, "Puntajes")

    def GoPerfilR():
        window_puntajes.destroy()
        GoPerfil()

    boton_volver = tk.Button(
        window_puntajes,
        text="Volver",
        font=("Arial", 12, "bold"),
        width=10,
        height=2,
        bg="red",
        command=GoPerfilR
    )

    boton_volver.place(x=20, y=20)

    titulo = tk.Label(
        window_puntajes,
        text="Puntajes",
        font=("Arial", 36, "bold")
    )

    titulo.place(relx=0.5, rely=0.20, anchor="center")

    caja_mis_puntajes = tk.Label(
        window_puntajes,
        text="Mis puntajes",
        font=("Arial", 24, "bold"),
        width=22,
        height=2,
        relief="solid",
        bd=2
    )

    caja_mis_puntajes.place(relx=0.32, rely=0.42, anchor="center")

    caja_puntajes_mundiales = tk.Label(
        window_puntajes,
        text="Puntajes mundiales",
        font=("Arial", 24, "bold"),
        width=22,
        height=2,
        relief="solid",
        bd=2
    )

    caja_puntajes_mundiales.place(relx=0.68, rely=0.42, anchor="center")

    texto_mis_puntajes = tk.Label(
        window_puntajes,
        text="Aquí se mostrarán los puntajes del jugador.",
        font=("Arial", 16)
    )

    texto_mis_puntajes.place(relx=0.32, rely=0.55, anchor="center")

    texto_puntajes_mundiales = tk.Label(
        window_puntajes,
        text="Aquí se mostrarán los puntajes mundiales.",
        font=("Arial", 16)
    )

    texto_puntajes_mundiales.place(relx=0.68, rely=0.55, anchor="center")

    window_puntajes.protocol("WM_DELETE_WINDOW", cerrar_todo)