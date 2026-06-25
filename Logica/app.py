"""
Descripcion:
    Modulo de interfaz logica del Desarrollador 2. Expone las
    funciones principales que el Desarrollador 1 debe llamar desde
    la interfaz grafica en Tkinter, sin que este necesite conocer
    los detalles internos de las clases Jugador, Torre, Unidad,
    Base, Partida o Combate.

    Ninguna funcion de este modulo depende de Tkinter ni de ninguna
    libreria grafica; solo se trabaja con datos basicos de Python
    (str, int, bool, dict, list) para que el Desarrollador 1 pueda
    conectarlos facilmente con los widgets de su interfaz.
"""

import archivos
from archivos import registrar_jugador as _registrar_jugador
from archivos import validar_login as _validar_login
from archivos import buscar_jugador as _buscar_jugador
from partida import crear_partida as _crear_partida
from ranking import obtener_top_defensores as _obtener_top_defensores
from ranking import obtener_top_atacantes as _obtener_top_atacantes

_partida_actual = None


def registrar_jugador(usuario, contrasena):
    """
    Descripcion:
        Registra un nuevo jugador en el sistema de archivos.

    Entradas:
        usuario (str): Nombre de usuario deseado.
        contrasena (str): Contrasena deseada.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje
        descriptivo, listos para mostrarse en la interfaz grafica.

    Restricciones:
        - usuario no debe estar previamente registrado.
    """
    return _registrar_jugador(usuario, contrasena)


def validar_login(usuario, contrasena):
    """
    Descripcion:
        Valida las credenciales de un jugador para permitirle
        iniciar sesion en el juego.

    Entradas:
        usuario (str): Nombre de usuario ingresado.
        contrasena (str): Contrasena ingresada.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje
        descriptivo, listos para mostrarse en la interfaz grafica.

    Restricciones:
        Ninguna.
    """
    return _validar_login(usuario, contrasena)


def obtener_jugador(usuario):
    """
    Descripcion:
        Obtiene la informacion completa de un jugador registrado,
        util para mostrar su perfil (victorias como defensor y como
        atacante) en la interfaz grafica.

    Entradas:
        usuario (str): Nombre de usuario del jugador a consultar.

    Salidas:
        dict: Diccionario con "nombre_usuario", "victorias_defensor",
        "victorias_atacante" y "total_victorias". None si el
        jugador no existe.

    Restricciones:
        Ninguna.
    """
    jugador_encontrado = _buscar_jugador(usuario)

    if jugador_encontrado is None:
        return None

    return {
        "nombre_usuario": jugador_encontrado.nombre_usuario,
        "victorias_defensor": jugador_encontrado.victorias_defensor,
        "victorias_atacante": jugador_encontrado.victorias_atacante,
        "total_victorias": jugador_encontrado.total_victorias(),
    }


def crear_partida(defensor, atacante):
    """
    Descripcion:
        Crea una nueva partida entre los dos jugadores indicados y
        la establece como la partida activa del sistema.

    Entradas:
        defensor (str): Nombre de usuario del jugador defensor.
        atacante (str): Nombre de usuario del jugador atacante.

    Salidas:
        dict: Estado inicial de la partida, igual al que devuelve
        obtener_estado_partida().

    Restricciones:
        - defensor y atacante deben ser distintos entre si.
    """
    global _partida_actual
    _partida_actual = _crear_partida(defensor, atacante)
    return _partida_actual.obtener_estado_partida()


def comprar_torre(tipo_torre, fila, columna):
    """
    Descripcion:
        Permite al defensor comprar una torre dentro de la partida
        activa.

    Entradas:
        tipo_torre (str): Tipo de torre a comprar.
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje
        descriptivo.

    Restricciones:
        - Debe existir una partida activa creada con crear_partida.
    """
    if _partida_actual is None:
        return False, "No hay una partida activa."
    return _partida_actual.comprar_torre(tipo_torre, fila, columna)


def comprar_unidad(tipo_unidad, fila, columna):
    """
    Descripcion:
        Permite al atacante comprar una unidad dentro de la partida
        activa.

    Entradas:
        tipo_unidad (str): Tipo de unidad a comprar.
        fila (int): Fila del tablero donde se coloca la unidad.
        columna (int): Columna del tablero donde se coloca la
            unidad.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje
        descriptivo.

    Restricciones:
        - Debe existir una partida activa creada con crear_partida.
    """
    if _partida_actual is None:
        return False, "No hay una partida activa."
    return _partida_actual.comprar_unidad(tipo_unidad, fila, columna)


def ejecutar_combate():
    """
    Descripcion:
        Ejecuta un turno de combate dentro de la partida activa.

    Entradas:
        Ninguna.

    Salidas:
        dict: Resumen del turno de combate (eventos ocurridos, vida
        de la base, dinero actualizado, si la ronda finalizo, etc.).
        Si no hay partida activa, devuelve un diccionario vacio.

    Restricciones:
        - Debe existir una partida activa creada con crear_partida.
    """
    if _partida_actual is None:
        return {}
    return _partida_actual.ejecutar_combate()


def obtener_estado_partida():
    """
    Descripcion:
        Obtiene el estado actual completo de la partida activa,
        listo para que la interfaz grafica lo muestre.

    Entradas:
        Ninguna.

    Salidas:
        dict: Estado actual de la partida. Si no hay partida activa,
        devuelve un diccionario vacio.

    Restricciones:
        - Debe existir una partida activa creada con crear_partida.
    """
    if _partida_actual is None:
        return {}
    return _partida_actual.obtener_estado_partida()


def obtener_top_defensores():
    """
    Descripcion:
        Obtiene el ranking de los 5 mejores jugadores como
        defensores.

    Entradas:
        Ninguna.

    Salidas:
        list[dict]: Lista ordenada de jugadores con sus victorias
        como defensor.

    Restricciones:
        Ninguna.
    """
    return _obtener_top_defensores()


def obtener_top_atacantes():
    """
    Descripcion:
        Obtiene el ranking de los 5 mejores jugadores como
        atacantes.

    Entradas:
        Ninguna.

    Salidas:
        list[dict]: Lista ordenada de jugadores con sus victorias
        como atacante.

    Restricciones:
        Ninguna.
    """
    return _obtener_top_atacantes()
