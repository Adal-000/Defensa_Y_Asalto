#=======================================#
# Archivo para mostrar el mapa del juego
#=======================================#

import tkinter as tk


def mapa(root, GoPlay, cerrar_todo, configurar_ventana, obtener_datos_partida=None):
    """
    Descripción:
        Crea la ventana base del mapa. Esta pantalla es un esqueleto
        visual para la futura partida tipo tower defense: incluye una
        franja superior con el botón para volver, paneles de información,
        controles de compra y un área central para dibujar el mapa.

    Entradas:
        root: ventana raíz oculta.
        GoPlay: función para volver a la ventana Play.
        cerrar_todo: función para cerrar completamente el programa.
        configurar_ventana: función que centra y configura la ventana.

    Salidas:
        No retorna ningún valor.

    Restricciones:
        El botón Volver destruye esta ventana y abre nuevamente Play.
        Por ahora los botones de compra son solamente visuales.
    """

    window_mapa = tk.Toplevel(root)
    configurar_ventana(window_mapa, "Mapa")
    datos_partida = obtener_datos_partida() if obtener_datos_partida is not None else {}
    nombre_jugador = datos_partida.get("jugador") or "Jugador"
    nombre_contrincante = datos_partida.get("contrincante") or "Contrincante"

    def GoPlayR():
        window_mapa.destroy()
        GoPlay()

    # --- Franja superior -------------------------------------------------

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

    caja_informacion_superior = tk.Label(
        window_mapa,
        text=f"Jugador: {nombre_jugador}",
        font=("Arial", 14, "bold"),
        width=88,
        height=2,
        relief="solid",
        bd=2,
        anchor="w",
        padx=14
    )
    caja_informacion_superior.place(x=160, y=20)

    titulo = tk.Label(
        window_mapa,
        text="Mapa",
        font=("Arial", 28, "bold")
    )
    titulo.place(relx=0.5, y=105, anchor="center")

    # --- Columna izquierda: eventos e información ------------------------

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
    caja_eventos.insert(
        tk.END,
        "Aquí aparecerán las cosas que pasen durante la partida. "
        "Si el texto llega al borde, continúa automáticamente en el "
        "siguiente renglón."
    )
    caja_eventos.config(state="disabled")
    caja_eventos.place(x=40, y=165)

    # --- Columna izquierda inferior: compras -----------------------------

    etiqueta_compras = tk.Label(
        window_mapa,
        text="Compras",
        font=("Arial", 13, "bold")
    )
    etiqueta_compras.place(x=40, y=465)

    nombres_botones = [
        "Comprar 1",
        "Comprar 2",
        "Comprar 3"
    ]

    for indice, nombre_boton in enumerate(nombres_botones):
        x_base = 40
        y_base = 500 + (indice * 48)

        boton_compra = tk.Button(
            window_mapa,
            text=nombre_boton,
            font=("Arial", 10, "bold"),
            width=11,
            height=1
        )
        boton_compra.place(x=x_base, y=y_base)

        campo_cantidad = tk.Entry(
            window_mapa,
            font=("Arial", 11),
            width=4,
            justify="center"
        )
        campo_cantidad.insert(0, "#")
        campo_cantidad.place(x=x_base + 105, y=y_base + 2)

    # --- Zona derecha: tablero del mapa ----------------------------------

    etiqueta_tablero = tk.Label(
        window_mapa,
        text="Área del mapa",
        font=("Arial", 13, "bold")
    )
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

    # Líneas guía temporales para visualizar el espacio de juego.
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

    caja_informacion_contrincante = tk.Text(
        window_mapa,
        font=("Arial", 12),
        width=77,
        height=3,
        relief="solid",
        bd=2,
        wrap="word"
    )
    caja_informacion_contrincante.insert(tk.END, f"Contrincante: {nombre_contrincante}")
    caja_informacion_contrincante.config(state="disabled")
    caja_informacion_contrincante.place(x=430, y=595)

    window_mapa.protocol("WM_DELETE_WINDOW", cerrar_todo)