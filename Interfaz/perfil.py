#=======================================#
# Archivo para ver sus puntajes
#=======================================#


import tkinter as tk

import app


def perfil(root, GoMain, GoPuntajes, cerrar_todo, configurar_ventana,
           obtener_usuario_actual):
    """
    Descripción:
        Crea la ventana de perfil del juego.

    Entradas:
        root: ventana raíz oculta.
        GoMain: función para volver al menú principal.
        GoPuntajes: función para abrir la ventana de puntajes.
        cerrar_todo: función para cerrar completamente el programa.
        configurar_ventana: función que centra y configura la ventana.
        obtener_usuario_actual: función que devuelve el nombre del
            jugador que inició sesión.

    Salidas:
        No retorna ningún valor.

    Restricciones:
        El botón Volver destruye esta ventana y abre nuevamente el menú principal.
        El botón Puntajes destruye esta ventana y abre la ventana de puntajes.
    """

    window1 = tk.Toplevel(root)
    configurar_ventana(window1, "Perfil")

    def GoMainR():
        window1.destroy()
        GoMain()

    def GoPuntajesR():
        window1.destroy()
        GoPuntajes()

    boton_volver = tk.Button(
        window1,
        text="Volver",
        font=("Arial", 12, "bold"),
        width=10,
        height=2,
        bg="red",
        command=GoMainR
    )

    boton_volver.place(x=20, y=20)

    boton_puntajes = tk.Button(
        window1,
        text="Puntajes",
        font=("Arial", 12, "bold"),
        width=12,
        height=2,
        bg="lightblue",
        command=GoPuntajesR
    )

    boton_puntajes.place(x=130, y=20)

    titulo = tk.Label(
        window1,
        text="Perfil",
        font=("Arial", 36, "bold")
    )

    titulo.place(relx=0.5, rely=0.35, anchor="center")

    texto = tk.Label(
        window1,
        text="Aquí irá la información del perfil del jugador",
        font=("Arial", 20)
    )

    texto.place(relx=0.5, rely=0.48, anchor="center")

    nombre_usuario_actual = obtener_usuario_actual()

    if nombre_usuario_actual is not None:
        datos_jugador = app.obtener_jugador(nombre_usuario_actual)
    else:
        datos_jugador = None

    if datos_jugador is not None:
        texto_estadisticas = (
            f"Usuario: {datos_jugador['nombre_usuario']}\n"
            f"Victorias como defensor: {datos_jugador['victorias_defensor']}\n"
            f"Victorias como atacante: {datos_jugador['victorias_atacante']}\n"
            f"Total de victorias: {datos_jugador['total_victorias']}"
        )
    else:
        texto_estadisticas = "No se encontró información del jugador actual."

    etiqueta_estadisticas = tk.Label(
        window1,
        text=texto_estadisticas,
        font=("Arial", 16),
        justify="left"
    )

    etiqueta_estadisticas.place(relx=0.5, rely=0.65, anchor="center")

    window1.protocol("WM_DELETE_WINDOW", cerrar_todo)