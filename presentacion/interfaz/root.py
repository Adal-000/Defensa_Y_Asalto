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
    Descripcion:
        Configura una ventana con tamaño fijo, centrada en pantalla y
        con un título específico.
    
    Entradas:
        ventana (object): Valor recibido por la funcion.
        nombre (object): Valor recibido por la funcion.
    
    Salidas:
        None: Ejecuta la accion y puede modificar el estado interno, la
        interfaz o los datos relacionados.
    
    Restricciones:
        - Los parametros recibidos deben respetar el tipo y el formato
        esperado por la funcion.
        - Requiere que los widgets, ventanas o callbacks usados por la
        interfaz existan antes de ejecutarse.
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
    Descripcion:
        Inicia la aplicación gráfica completa.
    
    Entradas:
        Ninguna.
    
    Salidas:
        None: Ejecuta la accion y puede modificar el estado interno, la
        interfaz o los datos relacionados.
    
    Restricciones:
        - Requiere que los widgets, ventanas o callbacks usados por la
        interfaz existan antes de ejecutarse.
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
        """
        Descripcion:
            Ejecuta la logica correspondiente a establecer usuario
            actual dentro del flujo del juego.
        
        Entradas:
            nombre_usuario (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        estado_sesion["usuario_actual"] = nombre_usuario

    def obtener_usuario_actual():
        """
        Descripcion:
            Obtiene la informacion correspondiente a obtener usuario
            actual para que otras partes del programa puedan utilizarla.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        return estado_sesion["usuario_actual"]

    def cerrar_todo():
        """
        Descripcion:
            Cierra o libera los recursos asociados a cerrar todo.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        app.detener_musica()
        root.destroy()

    def GoLogin():
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoLogin.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        login(root, GoMain, cerrar_todo, configurar_ventana, establecer_usuario_actual)

    def GoMain():
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoMain.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
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
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoPerfil.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        perfil(root, GoMain, GoPuntajes, cerrar_todo, configurar_ventana, obtener_usuario_actual)

    def GoPuntajes():
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoPuntajes.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        puntajes(root, GoPerfil, cerrar_todo, configurar_ventana, obtener_usuario_actual)

    def GoPlay():
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoPlay.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        play(root, GoMain, GoMapa, cerrar_todo, configurar_ventana, obtener_usuario_actual)

    def GoMapa():
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoMapa.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        mapa(root, GoPlay, cerrar_todo, configurar_ventana, obtener_datos_partida)

    def GoConfig():
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoConfig.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        config(root, GoMain, cerrar_todo, configurar_ventana)

    GoLogin()
    root.mainloop()


if __name__ == "__main__":
    main()
