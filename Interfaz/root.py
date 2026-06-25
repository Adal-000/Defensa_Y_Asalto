# iniciar desde este archivo
#=======================================#
# Archivo base para manejo de ventanas
#=======================================#

import os
import sys
import tkinter as tk

# Permite importar los modulos de la carpeta Logica/ (ubicada al
# mismo nivel que Interfaz/) sin necesidad de instalar el proyecto
# como paquete.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Logica"))

from main import main
from play import play
from config import config
from perfil import perfil
from puntajes import puntajes
from login import login



def configurar_ventana(window1, nombre):
    """
    Descripción:
        Configura una ventana con tamaño fijo, centrada en la pantalla
        del usuario y con un título específico.

    Entradas:
        window1: ventana creada con Tk o Toplevel.
        nombre: título que tendrá la ventana.

    Salidas:
        No retorna ningún valor.

    Restricciones:
        La ventana queda con tamaño fijo de 1150x700.
        La ventana no se puede redimensionar.
    """

    p_ancho = window1.winfo_screenwidth()
    p_alto = window1.winfo_screenheight()

    ancho = 1150
    alto = 700

    x = (p_ancho // 2) - (ancho // 2)
    y = (p_alto // 2) - (alto // 2)

    window1.geometry(f"{ancho}x{alto}+{x}+{y}")
    window1.title(nombre)
    window1.resizable(False, False)


root = tk.Tk()
root.withdraw()

# Guarda el nombre de usuario que inició sesión, para que las demás
# ventanas (Perfil, Play, Puntajes) sepan quién está jugando. NO funka
estado_sesion = {"usuario_actual": None}


def establecer_usuario_actual(nombre_usuario):
    """
    Descripción:
        Guarda el nombre de usuario que acaba de iniciar sesión.

    Entradas:
        nombre_usuario: nombre del usuario que inició sesión.
    """

    estado_sesion["usuario_actual"] = nombre_usuario


def obtener_usuario_actual():
    """
    Descripción:
        Devuelve el nombre de usuario que tiene la sesión activa.

    Salidas:
        El nombre de usuario actual, o None si nadie ha iniciado sesión.
    """

    return estado_sesion["usuario_actual"]


def GoLogin():
    """
    Descripción:
        Abre la ventana de inicio de sesión / registro.
    """

    login(root, GoMain, cerrar_todo, configurar_ventana, establecer_usuario_actual)


def GoMain():
    """
    Descripción:
        Abre la ventana principal.
    """

    main(root, GoPerfil, GoPlay, GoConfig, cerrar_todo, configurar_ventana,
         obtener_usuario_actual)


def GoPerfil():
    """
    Descripción:
        Abre la ventana de perfil.
    """

    perfil(root, GoMain, GoPuntajes, cerrar_todo, configurar_ventana,
           obtener_usuario_actual)


def GoPuntajes():
    """
    Descripción:
        Abre la ventana de puntajes desde perfil.
    """

    puntajes(root, GoPerfil, cerrar_todo, configurar_ventana, obtener_usuario_actual)


def GoPlay():
    """
    Descripción:
        Abre la ventana de juego.
    """

    play(root, GoMain, cerrar_todo, configurar_ventana, obtener_usuario_actual)


def GoConfig():
    """
    Descripción:
        Abre la ventana de configuración.
    """

    config(root, GoMain, cerrar_todo, configurar_ventana)


def cerrar_todo():
    """
    Descripción:
        Cierra completamente el programa.
    """

    root.destroy()


GoLogin()

root.mainloop()