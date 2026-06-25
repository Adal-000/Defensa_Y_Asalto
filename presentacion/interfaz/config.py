#=======================================#
# Archivo para manejo de configuracion
#=======================================#


import tkinter as tk


def config(root, GoMain, cerrar_todo, configurar_ventana):
    """
    Descripción:
        Crea la ventana de configuración.

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

    window3 = tk.Toplevel(root)
    configurar_ventana(window3, "Config")

    def GoMainR():
        window3.destroy()
        GoMain()

    boton_volver = tk.Button(
        window3,
        text="Volver",
        font=("Arial", 12, "bold"),
        width=10,
        height=2,
        bg="red",
        command=GoMainR
    )

    boton_volver.place(x=20, y=20)

    titulo = tk.Label(
        window3,
        text="Configuración",
        font=("Arial", 36, "bold")
    )

    titulo.place(relx=0.5, rely=0.35, anchor="center")

    texto = tk.Label(
        window3,
        text="Aquí irán las opciones de configuración",
        font=("Arial", 20)
    )

    texto.place(relx=0.5, rely=0.48, anchor="center")

    window3.protocol("WM_DELETE_WINDOW", cerrar_todo)