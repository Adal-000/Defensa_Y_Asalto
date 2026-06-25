"""
Descripcion:
    Modulo encargado de la persistencia de los jugadores del juego.
    Permite cargar y guardar la informacion de los jugadores en un
    archivo JSON, registrar nuevos jugadores, validar inicios de
    sesion y actualizar las victorias al finalizar una partida.
"""

import json
import os

from jugador import Jugador

# Carpeta raiz del proyecto (un nivel arriba de la carpeta Logica/).
# Se calcula a partir de la ubicacion de este archivo para que la ruta
# al archivo de jugadores funcione sin importar desde donde se ejecute
# el programa (por ejemplo, desde Interfaz/root.py).
_CARPETA_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RUTA_ARCHIVO_JUGADORES = os.path.join(_CARPETA_RAIZ_PROYECTO, "datos", "jugadores.json")


def _asegurar_carpeta_datos(ruta_archivo):
    """
    Descripcion:
        Verifica que la carpeta donde se guardara el archivo de
        jugadores exista. Si no existe, la crea.

    Entradas:
        ruta_archivo (str): Ruta completa del archivo de jugadores.

    Salidas:
        None: Crea la carpeta contenedora en el sistema de archivos
        si esta no existe.

    Restricciones:
        - ruta_archivo debe incluir el nombre del archivo, no solo
          la carpeta.
    """
    carpeta = os.path.dirname(ruta_archivo)
    if carpeta and not os.path.exists(carpeta):
        os.makedirs(carpeta)


def cargar_jugadores(ruta_archivo=RUTA_ARCHIVO_JUGADORES):
    """
    Descripcion:
        Carga la lista de jugadores almacenados en el archivo JSON
        indicado. Si el archivo no existe todavia, se devuelve una
        lista vacia en lugar de generar un error.

    Entradas:
        ruta_archivo (str): Ruta del archivo JSON de jugadores.
            Por defecto usa RUTA_ARCHIVO_JUGADORES.

    Salidas:
        list[Jugador]: Lista de objetos Jugador reconstruidos a
        partir del archivo.

    Restricciones:
        - El archivo, si existe, debe contener una lista de
          diccionarios validos para Jugador.desde_diccionario.
    """
    if not os.path.exists(ruta_archivo):
        return []

    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        try:
            datos_crudos = json.load(archivo)
        except json.JSONDecodeError:
            return []

    return [Jugador.desde_diccionario(datos) for datos in datos_crudos]


def guardar_jugadores(lista_jugadores, ruta_archivo=RUTA_ARCHIVO_JUGADORES):
    """
    Descripcion:
        Guarda una lista de objetos Jugador en un archivo JSON,
        sobrescribiendo el contenido anterior.

    Entradas:
        lista_jugadores (list[Jugador]): Lista de jugadores a guardar.
        ruta_archivo (str): Ruta del archivo JSON donde se guardaran
            los datos. Por defecto usa RUTA_ARCHIVO_JUGADORES.

    Salidas:
        None: Escribe la informacion en el archivo indicado.

    Restricciones:
        - lista_jugadores debe contener unicamente instancias de
          Jugador.
    """
    _asegurar_carpeta_datos(ruta_archivo)
    datos_a_guardar = [jugador.a_diccionario() for jugador in lista_jugadores]

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos_a_guardar, archivo, indent=4, ensure_ascii=False)


def buscar_jugador(nombre_usuario, ruta_archivo=RUTA_ARCHIVO_JUGADORES):
    """
    Descripcion:
        Busca un jugador por su nombre de usuario dentro del archivo
        de jugadores.

    Entradas:
        nombre_usuario (str): Nombre de usuario a buscar.
        ruta_archivo (str): Ruta del archivo JSON de jugadores.

    Salidas:
        Jugador: El jugador encontrado, si existe.
        None: Si ningun jugador coincide con el nombre de usuario.

    Restricciones:
        - La busqueda distingue mayusculas y minusculas.
    """
    lista_jugadores = cargar_jugadores(ruta_archivo)
    for jugador in lista_jugadores:
        if jugador.nombre_usuario == nombre_usuario:
            return jugador
    return None


def registrar_jugador(nombre_usuario, contrasena,
                       ruta_archivo=RUTA_ARCHIVO_JUGADORES):
    """
    Descripcion:
        Registra un nuevo jugador en el sistema, evitando que se
        repitan nombres de usuario ya existentes.

    Entradas:
        nombre_usuario (str): Nombre de usuario deseado para el
            nuevo jugador.
        contrasena (str): Contrasena para el nuevo jugador.
        ruta_archivo (str): Ruta del archivo JSON de jugadores.

    Salidas:
        tuple[bool, str]: El primer valor indica si el registro fue
        exitoso (True) o no (False). El segundo valor es un mensaje
        descriptivo del resultado.

    Restricciones:
        - nombre_usuario y contrasena no deben estar vacios.
        - No puede existir previamente un jugador con el mismo
          nombre_usuario.
    """
    if not nombre_usuario or not contrasena:
        return False, "El usuario y la contrasena no pueden estar vacios."

    lista_jugadores = cargar_jugadores(ruta_archivo)

    for jugador in lista_jugadores:
        if jugador.nombre_usuario == nombre_usuario:
            return False, "Ese nombre de usuario ya esta en uso."

    nuevo_jugador = Jugador(nombre_usuario, contrasena)
    lista_jugadores.append(nuevo_jugador)
    guardar_jugadores(lista_jugadores, ruta_archivo)

    return True, "Jugador registrado correctamente."


def validar_login(nombre_usuario, contrasena,
                   ruta_archivo=RUTA_ARCHIVO_JUGADORES):
    """
    Descripcion:
        Valida que las credenciales ingresadas correspondan a un
        jugador existente en el sistema.

    Entradas:
        nombre_usuario (str): Nombre de usuario ingresado.
        contrasena (str): Contrasena ingresada.
        ruta_archivo (str): Ruta del archivo JSON de jugadores.

    Salidas:
        tuple[bool, str]: El primer valor indica si el inicio de
        sesion fue exitoso. El segundo valor es un mensaje
        descriptivo del resultado.

    Restricciones:
        - Las credenciales deben coincidir exactamente con las
          almacenadas (la validacion distingue mayusculas/minusculas).
    """
    jugador_encontrado = buscar_jugador(nombre_usuario, ruta_archivo)

    if jugador_encontrado is None:
        return False, "El usuario no existe."

    if jugador_encontrado.contrasena != contrasena:
        return False, "La contrasena es incorrecta."

    return True, "Inicio de sesion exitoso."


def actualizar_victoria(nombre_usuario, rol,
                         ruta_archivo=RUTA_ARCHIVO_JUGADORES):
    """
    Descripcion:
        Actualiza el registro de victorias de un jugador al finalizar
        una partida, incrementando el contador correspondiente al rol
        con el que gano.

    Entradas:
        nombre_usuario (str): Nombre de usuario del jugador ganador.
        rol (str): Rol con el que gano la partida. Debe ser
            "defensor" o "atacante".
        ruta_archivo (str): Ruta del archivo JSON de jugadores.

    Salidas:
        bool: True si la actualizacion fue exitosa, False si el
        jugador no fue encontrado.

    Restricciones:
        - El jugador debe existir previamente en el archivo.
        - rol debe ser "defensor" o "atacante".
    """
    lista_jugadores = cargar_jugadores(ruta_archivo)

    for jugador in lista_jugadores:
        if jugador.nombre_usuario == nombre_usuario:
            jugador.sumar_victoria(rol)
            guardar_jugadores(lista_jugadores, ruta_archivo)
            return True

    return False
