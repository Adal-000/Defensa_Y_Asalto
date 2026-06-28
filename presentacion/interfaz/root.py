"""
Descripcion:
    Punto de entrada de la interfaz grafica Tkinter.

    Este modulo pertenece a la capa de presentacion. Su unica
    responsabilidad es crear la ventana principal y coordinar la
    navegacion entre pantallas. No contiene reglas de negocio.
"""

import tkinter as tk

from aplicacion import app
from presentacion.interfaz.config import config
from presentacion.interfaz.login import login
from presentacion.interfaz.main import main as ventana_main
from presentacion.interfaz.mapa import mapa
from presentacion.interfaz.perfil import perfil
from presentacion.interfaz.play import obtener_datos_partida, play
from presentacion.interfaz.puntajes import puntajes


ANCHO_VENTANA = 1150
ALTO_VENTANA = 700


def configurar_ventana(ventana, nombre):
    """
    Descripción:
        Configura una ventana con tamaño fijo, centrada en pantalla y
        con un título específico.

    Entradas:
        ventana: ventana creada con Tk o Toplevel.
        nombre: título de la ventana.

    Salidas:
        No retorna ningún valor.
    """
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()

    x = (pantalla_ancho // 2) - (ANCHO_VENTANA // 2)
    y = (pantalla_alto // 2) - (ALTO_VENTANA // 2)

    ventana.geometry(f"{ANCHO_VENTANA}x{ALTO_VENTANA}+{x}+{y}")
    ventana.title(nombre)
    ventana.resizable(False, False)


def main():
    """
    Descripción:
        Inicia la aplicación gráfica completa.

    Entradas:
        Ninguna.

    Salidas:
        No retorna ningún valor. Ejecuta el mainloop de Tkinter.
    """
    root = tk.Tk()
    root.withdraw()

    # La música de fondo es global a todo el programa: se inicia una
    # sola vez aquí y sigue sonando sin importar qué ventana esté
    # abierta (login, menú, perfil, configuración, juego, etc.). Solo
    # se detiene si el jugador lo pide explícitamente desde la
    # ventana de Configuración, o al cerrar el programa.
    app.iniciar_musica_de_fondo()

    estado_sesion = {"usuario_actual": None}

    def establecer_usuario_actual(nombre_usuario):
        estado_sesion["usuario_actual"] = nombre_usuario

    def obtener_usuario_actual():
        return estado_sesion["usuario_actual"]

    def cerrar_todo():
        app.detener_musica()
        root.destroy()

    def GoLogin():
        login(root, GoMain, cerrar_todo, configurar_ventana, establecer_usuario_actual)

    def GoMain():
        ventana_main(
            root,
            GoPerfil,
            GoPlay,
            GoConfig,
            cerrar_todo,
            configurar_ventana,
            obtener_usuario_actual,
        )

    def GoPerfil():
        perfil(root, GoMain, GoPuntajes, cerrar_todo, configurar_ventana, obtener_usuario_actual)

    def GoPuntajes():
        puntajes(root, GoPerfil, cerrar_todo, configurar_ventana, obtener_usuario_actual)

    def GoPlay():
        play(root, GoMain, GoMapa, cerrar_todo, configurar_ventana, obtener_usuario_actual)

    def GoMapa():
        mapa(root, GoPlay, cerrar_todo, configurar_ventana, obtener_datos_partida)

    def GoConfig():
        config(root, GoMain, cerrar_todo, configurar_ventana)

    GoLogin()
    root.mainloop()


if __name__ == "__main__":
    main()
