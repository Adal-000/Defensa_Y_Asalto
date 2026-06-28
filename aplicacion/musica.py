"""
Descripcion:
    Reproductor de musica de fondo, global para todo el programa.

    A diferencia de un reproductor creado dentro de una ventana en
    particular, el estado de este modulo vive a nivel de proceso
    (igual que aplicacion/configuracion.py), por lo que la musica
    sigue sonando sin importar que ventana este abierta (login, menu
    principal, configuracion, juego, etc.). Solo se detiene si:

    - El jugador entra a la ventana de Configuración y presiona
      "Detener" explícitamente.
    - Se cierra todo el programa.

    Usa pygame.mixer porque permite cambiar de pista, ajustar volumen
    y dejar musica sonando en bucle sin bloquear la interfaz de
    Tkinter (pygame.mixer.music corre en su propio hilo interno).
"""

import importlib.util
import os

RUTA_MUSICA_PREDETERMINADA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Musica",
    "tema_estrategia.wav",
)

_estado = {
    "pygame": None,
    "inicializado": False,
    "reproduciendo": False,
    "ruta_actual": None,
    "volumen": 0.6,
}


def _obtener_pygame():
    """
    Descripcion:
        Importa pygame e inicializa pygame.mixer una sola vez por
        ejecucion del programa (patron singleton a nivel de modulo).
        Si pygame no esta instalado en el entorno, devuelve None en
        vez de lanzar una excepcion, para que el resto del programa
        pueda seguir funcionando sin musica.

    Entradas:
        Ninguna.

    Salidas:
        module | None: El modulo pygame ya inicializado, o None si
        no esta disponible.

    Restricciones:
        Ninguna.
    """
    if _estado["inicializado"]:
        return _estado["pygame"]

    if importlib.util.find_spec("pygame") is None:
        _estado["inicializado"] = True
        _estado["pygame"] = None
        return None

    import pygame

    pygame.mixer.init()
    pygame.mixer.music.set_volume(_estado["volumen"])
    _estado["pygame"] = pygame
    _estado["inicializado"] = True
    return pygame


def pygame_disponible():
    """
    Descripcion:
        Indica si pygame esta instalado y disponible para reproducir
        musica en este entorno.

    Entradas:
        Ninguna.

    Salidas:
        bool: True si pygame.mixer puede usarse.

    Restricciones:
        Ninguna.
    """
    return _obtener_pygame() is not None


def reproducir(ruta=None, en_bucle=True):
    """
    Descripcion:
        Reproduce un archivo de musica. Si no se indica una ruta, usa
        la ultima ruta reproducida; si nunca se reprodujo nada, usa
        la cancion predeterminada de la carpeta Musica/.

    Entradas:
        ruta (str | None): Ruta del archivo de audio a reproducir.
            Si es None, se usa la pista actual o la predeterminada.
        en_bucle (bool): Si True, la cancion se repite indefinidamente.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje descriptivo.

    Restricciones:
        - Requiere pygame instalado en el entorno de Python.
        - El archivo debe existir en disco.
    """
    pygame = _obtener_pygame()
    if pygame is None:
        return False, "Para reproducir música instala pygame en el entorno de Python."

    ruta_objetivo = (ruta or _estado["ruta_actual"] or RUTA_MUSICA_PREDETERMINADA).strip()

    if not ruta_objetivo or not os.path.exists(ruta_objetivo):
        return False, "El archivo de música no existe."

    try:
        pygame.mixer.music.load(ruta_objetivo)
        pygame.mixer.music.play(-1 if en_bucle else 0)
    except Exception as error:
        return False, f"No se pudo reproducir el audio: {error}"

    _estado["ruta_actual"] = ruta_objetivo
    _estado["reproduciendo"] = True
    return True, "Reproduciendo música."


def reproducir_predeterminada_si_no_hay_nada(ruta_configurada=None):
    """
    Descripcion:
        Punto de entrada pensado para llamarse una sola vez al
        arrancar el programa (desde root.py). Si el jugador ya tiene
        una ruta de musica guardada en su configuracion, la usa; si
        no, reproduce la cancion predeterminada de la carpeta
        Musica/. No hace nada si pygame no esta disponible (el juego
        sigue funcionando en silencio en ese caso).

    Entradas:
        ruta_configurada (str | None): Ruta guardada en la
            configuracion del jugador, si existe.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje descriptivo.

    Restricciones:
        - Requiere pygame instalado en el entorno de Python para
          producir sonido real.
    """
    ruta = (ruta_configurada or "").strip() or RUTA_MUSICA_PREDETERMINADA
    return reproducir(ruta, en_bucle=True)


def detener():
    """
    Descripcion:
        Detiene la reproduccion de musica. Esta es la unica forma de
        apagar la musica: el jugador debe entrar a la ventana de
        Configuración y presionar "Detener" (o cerrar el programa).
        Cambiar de ventana del juego (login, menu, perfil, jugar,
        etc.) ya NO detiene la musica.

    Entradas:
        Ninguna.

    Salidas:
        None.

    Restricciones:
        Ninguna.
    """
    pygame = _estado.get("pygame")
    if pygame is not None and _estado.get("reproduciendo"):
        pygame.mixer.music.stop()
    _estado["reproduciendo"] = False


def esta_reproduciendo():
    """
    Descripcion:
        Indica si la musica esta sonando actualmente.

    Entradas:
        Ninguna.

    Salidas:
        bool: True si hay musica reproduciendose ahora mismo.

    Restricciones:
        Ninguna.
    """
    return bool(_estado.get("reproduciendo"))


def obtener_ruta_actual():
    """
    Descripcion:
        Devuelve la ruta del archivo que esta sonando o que sono por
        ultima vez en esta sesion.

    Entradas:
        Ninguna.

    Salidas:
        str | None: Ruta del archivo de audio.

    Restricciones:
        Ninguna.
    """
    return _estado.get("ruta_actual")


def establecer_volumen(volumen):
    """
    Descripcion:
        Ajusta el volumen de la musica de fondo.

    Entradas:
        volumen (float): Valor entre 0.0 (silencio) y 1.0 (máximo).

    Salidas:
        None.

    Restricciones:
        Ninguna.
    """
    volumen = max(0.0, min(1.0, float(volumen)))
    _estado["volumen"] = volumen
    pygame = _estado.get("pygame")
    if pygame is not None:
        pygame.mixer.music.set_volume(volumen)
