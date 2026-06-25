#=======================================#
# Archivo para mostrar el mapa del juego
#=======================================#

import tkinter as tk


def mapa(root, GoPlay, cerrar_todo, configurar_ventana, datos_partida=None):
    """
    Descripción:
        Crea la ventana base del mapa. Muestra el jugador actual arriba,
        el contrincante abajo, tres controles de compra a la izquierda y
        campos centrales de información no modificables para datos futuros.
    """

    datos_partida = datos_partida or {}
    jugador = datos_partida.get("jugador") or "Jugador"
    contrincante = datos_partida.get("contrincante") or "Contrincante"

    window_mapa = tk.Toplevel(root)
    configurar_ventana(window_mapa, "Mapa")

    def GoPlayR():
        window_mapa.destroy()
        GoPlay()

    boton_volver = tk.Button(
        window_mapa,
        text="Volver",
        font=("Arial", 12, "bold"),
        width=10,
        height=2,
        bg="red",
        command=GoPlayR
    )
    boton_volver.place(x=20, y=20)

    caja_jugador = tk.Label(
        window_mapa,
        text=f"Jugador: {jugador}",
        font=("Arial", 14, "bold"),
        width=88,
        height=2,
        relief="solid",
        bd=2,
        anchor="w",
        padx=14
    )
    caja_jugador.place(x=160, y=20)

    titulo = tk.Label(window_mapa, text="Mapa", font=("Arial", 28, "bold"))
    titulo.place(relx=0.5, y=105, anchor="center")

    etiqueta_eventos = tk.Label(
        window_mapa,
        text="Información de la partida",
        font=("Arial", 13, "bold")
    )
    etiqueta_eventos.place(x=40, y=135)

    caja_eventos = tk.Text(
        window_mapa,
        font=("Consolas", 11),
        width=34,
        height=15,
        relief="solid",
        bd=2,
        wrap="word"
    )
    caja_eventos.insert(tk.END, "Datos de la partida pendientes de definir.")
    caja_eventos.config(state="disabled")
    caja_eventos.place(x=40, y=165)

    etiqueta_compras = tk.Label(window_mapa, text="Compras", font=("Arial", 13, "bold"))
    etiqueta_compras.place(x=40, y=465)

    nombres_botones = ["Comprar 1", "Comprar 2", "Comprar 3"]

    for indice, nombre_boton in enumerate(nombres_botones):
        y_base = 500 + (indice * 48)

        boton_compra = tk.Button(
            window_mapa,
            text=nombre_boton,
            font=("Arial", 10, "bold"),
            width=11,
            height=1
        )
        boton_compra.place(x=40, y=y_base)

        campo_cantidad = tk.Entry(
            window_mapa,
            font=("Arial", 11),
            width=4,
            justify="center"
        )
        campo_cantidad.insert(0, "#")
        campo_cantidad.place(x=145, y=y_base + 2)

        dato_futuro = tk.Label(
            window_mapa,
            text="Dato pendiente",
            font=("Arial", 10),
            width=16,
            height=1,
            relief="solid",
            bd=1,
            bg="#f3f3f3"
        )
        dato_futuro.place(x=195, y=y_base + 1)

    etiqueta_tablero = tk.Label(window_mapa, text="Área del mapa", font=("Arial", 13, "bold"))
    etiqueta_tablero.place(x=430, y=135)

    cuadro_mapa = tk.Canvas(
        window_mapa,
        width=660,
        height=405,
        bg="white",
        relief="solid",
        bd=3,
        highlightthickness=0
    )
    cuadro_mapa.place(x=430, y=165)

    for x in range(0, 661, 60):
        cuadro_mapa.create_line(x, 0, x, 405, fill="#dddddd")
    for y in range(0, 406, 45):
        cuadro_mapa.create_line(0, y, 660, y, fill="#dddddd")

    cuadro_mapa.create_text(
        330,
        202,
        text="Espacio reservado para el mapa tower defense",
        font=("Arial", 16, "bold"),
        fill="gray35"
    )

    caja_contrincante = tk.Label(
        window_mapa,
        text=f"Contrincante: {contrincante}",
        font=("Arial", 14, "bold"),
        width=77,
        height=2,
        relief="solid",
        bd=2,
        anchor="w",
        padx=14
    )
    caja_contrincante.place(x=430, y=595)

    window_mapa.protocol("WM_DELETE_WINDOW", cerrar_todo)
