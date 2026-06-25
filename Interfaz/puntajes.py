#=======================================#
# Archivo para ver puntajes de otros
#=======================================#


import tkinter as tk

import app


def puntajes(root, GoPerfil, cerrar_todo, configurar_ventana,
             obtener_usuario_actual):
    """
    Descripción:
        Crea la ventana de puntajes del jugador y puntajes mundiales.

    Entradas:
        root: ventana raíz oculta.
        GoPerfil: función para volver a la ventana de perfil.
        cerrar_todo: función para cerrar completamente el programa.
        configurar_ventana: función que centra y configura la ventana.
        obtener_usuario_actual: función que devuelve el nombre del
            jugador que inició sesión.

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

    nombre_usuario_actual = obtener_usuario_actual()
    datos_jugador = app.obtener_jugador(nombre_usuario_actual) if nombre_usuario_actual else None

    if datos_jugador is not None:
        texto_mis_puntajes_contenido = (
            f"Victorias como defensor: {datos_jugador['victorias_defensor']}\n"
            f"Victorias como atacante: {datos_jugador['victorias_atacante']}"
        )
    else:
        texto_mis_puntajes_contenido = "Inicia sesión para ver tus puntajes."

    texto_mis_puntajes = tk.Label(
        window_puntajes,
        text=texto_mis_puntajes_contenido,
        font=("Arial", 16),
        justify="left"
    )

    texto_mis_puntajes.place(relx=0.32, rely=0.58, anchor="center")

    top_defensores = app.obtener_top_defensores()
    top_atacantes = app.obtener_top_atacantes()

    lineas_ranking = ["Top defensores:"]
    for posicion, jugador_ranking in enumerate(top_defensores, start=1):
        lineas_ranking.append(
            f"{posicion}. {jugador_ranking['nombre_usuario']} "
            f"({jugador_ranking['victorias_defensor']} victorias)"
        )

    lineas_ranking.append("")
    lineas_ranking.append("Top atacantes:")
    for posicion, jugador_ranking in enumerate(top_atacantes, start=1):
        lineas_ranking.append(
            f"{posicion}. {jugador_ranking['nombre_usuario']} "
            f"({jugador_ranking['victorias_atacante']} victorias)"
        )

    if not top_defensores and not top_atacantes:
        lineas_ranking = ["Aún no hay jugadores registrados."]

    texto_puntajes_mundiales = tk.Label(
        window_puntajes,
        text="\n".join(lineas_ranking),
        font=("Arial", 14),
        justify="left"
    )

    texto_puntajes_mundiales.place(relx=0.68, rely=0.58, anchor="center")

    window_puntajes.protocol("WM_DELETE_WINDOW", cerrar_todo)