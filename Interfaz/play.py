#=======================================#
# Archivo para jugar
#=======================================#

import tkinter as tk
from tkinter import messagebox

import app


TIPOS_TORRE = ["arquera", "cañon", "hielo", "soporte"]
TIPOS_UNIDAD = ["soldado", "escudero", "explorador", "demoledor"]


def play(root, GoMain, cerrar_todo, configurar_ventana, obtener_usuario_actual):
    """
    Descripción:
        Crea la ventana de juego. Permite crear una partida contra
        otro jugador, comprar torres y unidades, ejecutar turnos de
        combate y ver el estado actual de la partida en tiempo real.

    Entradas:
        root: ventana raíz oculta.
        GoMain: función para volver al menú principal.
        cerrar_todo: función para cerrar completamente el programa.
        configurar_ventana: función que centra y configura la ventana.
        obtener_usuario_actual: función que devuelve el nombre del
            jugador que inició sesión (jugará como defensor).

    Salidas:
        No retorna ningún valor.

    Restricciones:
        El botón Volver destruye esta ventana y abre nuevamente el menú principal.
        Debe haber un usuario con sesión iniciada para crear una partida.
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
        font=("Arial", 28, "bold")
    )
    titulo.place(relx=0.5, rely=0.07, anchor="center")

    # --- Panel de creación de partida -----------------------------------

    panel_creacion = tk.Frame(window2)
    panel_creacion.place(relx=0.5, rely=0.16, anchor="center")

    etiqueta_rival = tk.Label(panel_creacion, text="Usuario rival (atacante):",
                               font=("Arial", 12))
    etiqueta_rival.grid(row=0, column=0, padx=8)

    campo_rival = tk.Entry(panel_creacion, font=("Arial", 12), width=18)
    campo_rival.grid(row=0, column=1, padx=8)

    # --- Panel de estado de la partida -----------------------------------

    texto_estado = tk.Label(
        window2,
        text="Crea una partida para comenzar.",
        font=("Arial", 13),
        justify="left"
    )
    texto_estado.place(relx=0.27, rely=0.30, anchor="n")

    caja_eventos = tk.Listbox(window2, font=("Consolas", 10), width=55, height=14)
    caja_eventos.place(relx=0.73, rely=0.30, anchor="n")

    def refrescar_estado():
        """
        Descripción:
            Consulta el estado actual de la partida y actualiza la
            etiqueta de estado en pantalla.
        """
        estado = app.obtener_estado_partida()

        if not estado:
            texto_estado.config(text="No hay una partida activa.")
            return

        texto_estado.config(text=(
            f"Ronda: {estado['numero_ronda']}\n"
            f"Defensor: {estado['nombre_defensor']} "
            f"(dinero: {estado['dinero_defensor']})\n"
            f"Atacante: {estado['nombre_atacante']} "
            f"(dinero: {estado['dinero_atacante']})\n"
            f"Marcador: {estado['rondas_ganadas_defensor']} - "
            f"{estado['rondas_ganadas_atacante']}\n"
            f"Vida de la base: {estado['vida_base']}/{estado['vida_maxima_base']}\n"
            f"Torres en juego: {len(estado['torres'])}\n"
            f"Unidades en juego: {len(estado['unidades'])}\n"
            f"Partida finalizada: {'Sí' if estado['partida_finalizada'] else 'No'}"
        ))

        if estado["partida_finalizada"]:
            messagebox.showinfo(
                "Partida finalizada",
                f"{estado['ganador_partida']} ganó la partida "
                f"como {estado['rol_ganador_partida']}."
            )

    def agregar_eventos_a_la_lista(lista_eventos):
        """
        Descripción:
            Agrega una lista de mensajes de eventos al final del
            cuadro de eventos visible en pantalla.

        Entradas:
            lista_eventos: lista de cadenas de texto con los eventos
                ocurridos durante el último turno de combate.
        """
        for evento in lista_eventos:
            caja_eventos.insert(tk.END, evento)
        caja_eventos.yview(tk.END)

    def crear_partida_click():
        """
        Descripción:
            Crea una nueva partida usando al usuario con sesión
            iniciada como defensor y al usuario escrito en el campo
            de texto como atacante.
        """
        nombre_defensor = obtener_usuario_actual()
        nombre_atacante = campo_rival.get().strip()

        if not nombre_defensor:
            messagebox.showwarning("Sesión requerida",
                                    "Debes iniciar sesión para jugar.")
            return

        if not nombre_atacante:
            messagebox.showwarning("Falta el rival",
                                    "Escribe el nombre de usuario del atacante.")
            return

        if nombre_defensor == nombre_atacante:
            messagebox.showwarning("Usuarios iguales",
                                    "El defensor y el atacante deben ser distintos.")
            return

        app.crear_partida(nombre_defensor, nombre_atacante)
        caja_eventos.delete(0, tk.END)
        caja_eventos.insert(tk.END, f"Partida creada: {nombre_defensor} (defensor) "
                                     f"vs {nombre_atacante} (atacante).")
        refrescar_estado()

    boton_crear_partida = tk.Button(
        panel_creacion,
        text="Crear partida",
        font=("Arial", 12, "bold"),
        bg="lightgreen",
        command=crear_partida_click
    )
    boton_crear_partida.grid(row=0, column=2, padx=8)

    # --- Panel de compras --------------------------------------------------

    panel_compras = tk.Frame(window2)
    panel_compras.place(relx=0.27, rely=0.62, anchor="n")

    etiqueta_torre = tk.Label(panel_compras, text="Comprar torre:", font=("Arial", 12, "bold"))
    etiqueta_torre.grid(row=0, column=0, columnspan=3, pady=(0, 6))

    variable_tipo_torre = tk.StringVar(value=TIPOS_TORRE[0])
    menu_torre = tk.OptionMenu(panel_compras, variable_tipo_torre, *TIPOS_TORRE)
    menu_torre.grid(row=1, column=0, padx=4)

    campo_fila_torre = tk.Entry(panel_compras, width=5)
    campo_fila_torre.insert(0, "3")
    campo_fila_torre.grid(row=1, column=1, padx=4)

    campo_columna_torre = tk.Entry(panel_compras, width=5)
    campo_columna_torre.insert(0, "2")
    campo_columna_torre.grid(row=1, column=2, padx=4)

    def comprar_torre_click():
        """
        Descripción:
            Lee el tipo de torre y la posición elegida, e intenta
            comprarla dentro de la partida activa.
        """
        try:
            fila = int(campo_fila_torre.get())
            columna = int(campo_columna_torre.get())
        except ValueError:
            messagebox.showwarning("Posición inválida",
                                    "Fila y columna deben ser números enteros.")
            return

        exito, mensaje = app.comprar_torre(variable_tipo_torre.get(), fila, columna)
        caja_eventos.insert(tk.END, mensaje)
        caja_eventos.yview(tk.END)
        refrescar_estado()

    boton_comprar_torre = tk.Button(
        panel_compras,
        text="Comprar torre",
        bg="lightblue",
        command=comprar_torre_click
    )
    boton_comprar_torre.grid(row=1, column=3, padx=8)

    etiqueta_unidad = tk.Label(panel_compras, text="Comprar unidad:", font=("Arial", 12, "bold"))
    etiqueta_unidad.grid(row=2, column=0, columnspan=3, pady=(14, 6))

    variable_tipo_unidad = tk.StringVar(value=TIPOS_UNIDAD[0])
    menu_unidad = tk.OptionMenu(panel_compras, variable_tipo_unidad, *TIPOS_UNIDAD)
    menu_unidad.grid(row=3, column=0, padx=4)

    campo_fila_unidad = tk.Entry(panel_compras, width=5)
    campo_fila_unidad.insert(0, "10")
    campo_fila_unidad.grid(row=3, column=1, padx=4)

    campo_columna_unidad = tk.Entry(panel_compras, width=5)
    campo_columna_unidad.insert(0, "2")
    campo_columna_unidad.grid(row=3, column=2, padx=4)

    def comprar_unidad_click():
        """
        Descripción:
            Lee el tipo de unidad y la posición elegida, e intenta
            comprarla dentro de la partida activa.
        """
        try:
            fila = int(campo_fila_unidad.get())
            columna = int(campo_columna_unidad.get())
        except ValueError:
            messagebox.showwarning("Posición inválida",
                                    "Fila y columna deben ser números enteros.")
            return

        exito, mensaje = app.comprar_unidad(variable_tipo_unidad.get(), fila, columna)
        caja_eventos.insert(tk.END, mensaje)
        caja_eventos.yview(tk.END)
        refrescar_estado()

    boton_comprar_unidad = tk.Button(
        panel_compras,
        text="Comprar unidad",
        bg="lightblue",
        command=comprar_unidad_click
    )
    boton_comprar_unidad.grid(row=3, column=3, padx=8)

    # --- Botón de combate --------------------------------------------------

    def ejecutar_combate_click():
        """
        Descripción:
            Ejecuta un turno de combate dentro de la partida activa
            y muestra los eventos ocurridos en el cuadro de eventos.
        """
        resultado = app.ejecutar_combate()

        if not resultado:
            messagebox.showwarning("Sin partida", "Primero crea una partida.")
            return

        if resultado["eventos"]:
            agregar_eventos_a_la_lista(resultado["eventos"])
        else:
            caja_eventos.insert(tk.END, "(Turno sin eventos de combate)")
            caja_eventos.yview(tk.END)

        refrescar_estado()

    boton_combate = tk.Button(
        window2,
        text="Ejecutar turno de combate",
        font=("Arial", 13, "bold"),
        bg="orange",
        command=ejecutar_combate_click
    )
    boton_combate.place(relx=0.27, rely=0.92, anchor="center")

    window2.protocol("WM_DELETE_WINDOW", cerrar_todo)
