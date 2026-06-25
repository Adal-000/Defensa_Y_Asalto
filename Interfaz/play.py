#=======================================#
# Archivo para iniciar sesion antes de jugar
#=======================================#

import os
import sys
import tkinter as tk

RUTA_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUTA_RED = os.path.join(RUTA_PROYECTO, "Red")
if RUTA_RED not in sys.path:
    sys.path.append(RUTA_RED)

from cliente import ClientePartida, PUERTO_PREDETERMINADO


FACCIONES = ["Rusia", "España", "Italia", "EE.UU", "Alemania", "Francia"]
DATOS_PARTIDA = {
    "jugador": "",
    "contrincante": "Contrincante",
    "faccion": "",
    "rol": "",
}


def obtener_datos_partida():
    """Devuelve los datos confirmados en la pantalla Play."""
    return DATOS_PARTIDA.copy()


def play(root, GoMain, GoMapa, cerrar_todo, configurar_ventana, obtener_usuario_actual):
    """
    Descripción:
        Crea la ventana Play. Mantiene arriba los datos de conexión y
        permite escoger una facción antes de entrar al mapa.
    """

    window2 = tk.Toplevel(root)
    configurar_ventana(window2, "Play")

    cliente_red = ClientePartida()
    faccion_temporal = tk.StringVar(value="")
    faccion_confirmada = tk.StringVar(value="")
    seleccion_bloqueada = tk.BooleanVar(value=False)
    facciones_ocupadas = set()
    jugadores_conectados = tk.IntVar(value=0)

    def GoMainR():
        cliente_red.cerrar()
        window2.destroy()
        GoMain()

    def GoMapaR():
        DATOS_PARTIDA.update({
            "jugador": campo_usuario.get().strip() or obtener_usuario_actual() or "Invitado",
            "contrincante": "Contrincante",
            "faccion": faccion_confirmada.get(),
            "rol": rol_seleccionado.get(),
        })
        window2.destroy()
        GoMapa()

    boton_volver = tk.Button(
        window2, text="Volver", font=("Arial", 12, "bold"), width=10,
        height=2, bg="red", command=GoMainR
    )
    boton_volver.place(x=20, y=20)

    titulo = tk.Label(window2, text="Play en red", font=("Arial", 28, "bold"))
    titulo.place(relx=0.5, y=52, anchor="center")

    # --- Datos de conexión: se conserva la franja superior original -------

    modo_partida = tk.StringVar(value="crear")
    rol_seleccionado = tk.StringVar(value="defensor")

    etiqueta_modo = tk.Label(window2, text="Modo:", font=("Arial", 11, "bold"))
    etiqueta_modo.place(x=175, y=92)

    radio_crear = tk.Radiobutton(
        window2, text="Crear servidor", variable=modo_partida, value="crear",
        font=("Arial", 9)
    )
    radio_crear.place(x=230, y=88)

    radio_unirse = tk.Radiobutton(
        window2, text="Unirse a partida", variable=modo_partida, value="unirse",
        font=("Arial", 9)
    )
    radio_unirse.place(x=365, y=88)

    etiqueta_ip = tk.Label(window2, text="IP servidor:", font=("Arial", 10))
    etiqueta_ip.place(x=145, y=122)
    campo_ip = tk.Entry(window2, font=("Arial", 10), width=16)
    campo_ip.insert(0, "192.168.0.9")
    campo_ip.place(x=228, y=117)

    etiqueta_usuario = tk.Label(window2, text="Usuario:", font=("Arial", 10))
    etiqueta_usuario.place(x=395, y=122)
    campo_usuario = tk.Entry(window2, font=("Arial", 10), width=16)
    campo_usuario.insert(0, obtener_usuario_actual() or "Invitado")
    campo_usuario.config(state="disabled")
    campo_usuario.place(x=491, y=117)

    etiqueta_rol = tk.Label(window2, text="Rol:", font=("Arial", 10))
    etiqueta_rol.place(x=620, y=122)
    menu_rol = tk.OptionMenu(window2, rol_seleccionado, "defensor", "atacante")
    menu_rol.config(font=("Arial", 9), width=9, height=1)
    menu_rol.place(x=657, y=112)

    etiqueta_puerto = tk.Label(window2, text="Puerto:", font=("Arial", 10))
    etiqueta_puerto.place(x=762, y=122)
    campo_puerto = tk.Entry(window2, font=("Arial", 10), width=7)
    campo_puerto.insert(0, "5003")
    campo_puerto.place(x=820, y=117)

    estado_conexion = tk.Label(
        window2, text="Sin conexión", font=("Arial", 11, "bold"),
        fg="red", width=24
    )
    estado_conexion.place(relx=0.5, y=154, anchor="center")

    def actualizar_desde_red(mensaje):
        datos = mensaje.get("datos", {}) if isinstance(mensaje, dict) else {}
        if not isinstance(datos, dict):
            return
        jugadores_conectados.set(int(datos.get("jugadores_conectados", jugadores_conectados.get()) or 0))
        if datos.get("rol_cliente"):
            rol_seleccionado.set(datos["rol_cliente"])
        ocupadas = datos.get("facciones_ocupadas", [])
        if isinstance(ocupadas, list):
            facciones_ocupadas.clear()
            facciones_ocupadas.update(ocupadas)
        refrescar_botones()

    cliente_red.callback_mensaje = actualizar_desde_red

    def conectar_click():
        try:
            puerto = int(campo_puerto.get())
        except ValueError:
            estado_conexion.config(text="Puerto inválido", fg="red")
            return
        exito, mensaje = cliente_red.conectar(
            campo_ip.get().strip(), campo_usuario.get().strip(), puerto, rol_seleccionado.get()
        )
        texto_estado = "Conectado al servidor." if exito else mensaje[:24]
        estado_conexion.config(text=texto_estado, fg="green" if exito else "red")
        if exito:
            jugadores_conectados.set(max(jugadores_conectados.get(), 1))
            cliente_red.obtener_estado()

    boton_conectar = tk.Button(
        window2, text="Continuar", font=("Arial", 11, "bold"),
        width=10, bg="lightgreen", command=conectar_click
    )
    boton_conectar.place(x=892, y=109)

    # --- Selección de facción -------------------------------------------

    panel_facciones = tk.Frame(window2)
    panel_facciones.place(relx=0.5, y=330, anchor="center")

    botones_faccion = {}

    def refrescar_botones():
        for nombre_faccion, boton in botones_faccion.items():
            bloqueada_por_otro = nombre_faccion in facciones_ocupadas
            if nombre_faccion == faccion_temporal.get():
                boton.config(relief="sunken", bg="#b7d7ff", state="normal")
            elif bloqueada_por_otro:
                boton.config(relief="raised", bg="#d0d0d0", state="disabled")
            else:
                boton.config(relief="raised", bg="SystemButtonFace", state="normal")

    def seleccionar_faccion(nombre_faccion):
        if seleccion_bloqueada.get():
            texto_faccion.config(text=f"Confirmada: {faccion_confirmada.get()}")
            return
        if nombre_faccion in facciones_ocupadas:
            texto_faccion.config(text="Facción ocupada")
            return
        faccion_temporal.set(nombre_faccion)
        texto_faccion.config(text=f"Elegida: {nombre_faccion}")
        refrescar_botones()

    for indice, nombre_faccion in enumerate(FACCIONES):
        fila = indice // 3
        columna = indice % 3
        boton_faccion = tk.Button(
            panel_facciones,
            text=f"┌────────────┐\n│  Bandera   │\n└────────────┘\n{nombre_faccion}",
            font=("Arial", 13, "bold"), width=18, height=5,
            command=lambda faccion=nombre_faccion: seleccionar_faccion(faccion)
        )
        boton_faccion.grid(row=fila, column=columna, padx=24, pady=18)
        botones_faccion[nombre_faccion] = boton_faccion

    texto_faccion = tk.Label(
        window2, text="Elige una facción", font=("Arial", 13, "bold"),
        width=34, height=2, relief="solid", bd=2
    )
    texto_faccion.place(relx=0.5, y=575, anchor="center")

    def elegir_faccion_click():
        if not faccion_temporal.get():
            texto_faccion.config(text="Elige una facción antes")
            return
        faccion_confirmada.set(faccion_temporal.get())
        seleccion_bloqueada.set(True)
        texto_faccion.config(text=f"Confirmada: {faccion_confirmada.get()}")
        refrescar_botones()

    def cambiar_faccion_click():
        seleccion_bloqueada.set(False)
        faccion_confirmada.set("")
        faccion_temporal.set("")
        texto_faccion.config(text="Elige una facción")
        refrescar_botones()

    def jugar_click():
        if not faccion_confirmada.get():
            texto_faccion.config(text="Elige una facción antes")
            return
        resumen = cliente_red.obtener_resumen_red()
        if not resumen.get("conectado"):
            texto_faccion.config(text="Conéctate al servidor")
            return
        if jugadores_conectados.get() < 2:
            texto_faccion.config(text="Esperando jugador contrincante")
            cliente_red.obtener_estado()
            return
        cliente_red.iniciar_combate()
        GoMapaR()

    boton_elegir_faccion = tk.Button(
        window2, text="Elegir facción", font=("Arial", 12, "bold"),
        width=16, bg="lightgreen", command=elegir_faccion_click
    )
    boton_elegir_faccion.place(x=55, y=620)

    boton_cambiar_faccion = tk.Button(
        window2, text="Cambiar facción", font=("Arial", 12, "bold"),
        width=16, bg="#ffd36b", command=cambiar_faccion_click
    )
    boton_cambiar_faccion.place(x=230, y=620)

    boton_jugar = tk.Button(
        window2, text="Jugar", font=("Arial", 13, "bold"), width=18,
        height=2, bg="orange", command=jugar_click
    )
    boton_jugar.place(x=905, y=610)

    window2.protocol("WM_DELETE_WINDOW", cerrar_todo)
