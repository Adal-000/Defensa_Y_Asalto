"""
Descripcion:
    Modulo encargado de generar los rankings de los mejores
    jugadores, tanto en el rol de defensor como en el rol de
    atacante. La informacion generada aqui esta lista para que el
    Desarrollador 1 la muestre en la interfaz grafica con Tkinter.
"""

from infraestructura.persistencia.archivos import cargar_jugadores, RUTA_ARCHIVO_JUGADORES

CANTIDAD_MAXIMA_RANKING = 5


def obtener_top_defensores(ruta_archivo=RUTA_ARCHIVO_JUGADORES,
                            cantidad=CANTIDAD_MAXIMA_RANKING):
    """
    Descripcion:
        Genera la lista de los mejores jugadores segun su cantidad
        de victorias como defensor, ordenados de mayor a menor.

    Entradas:
        ruta_archivo (str): Ruta del archivo JSON de jugadores.
        cantidad (int): Cantidad maxima de jugadores a incluir en el
            ranking. Por defecto es 5.

    Salidas:
        list[dict]: Lista de diccionarios con las claves
        "nombre_usuario" y "victorias_defensor", ordenada de mayor a
        menor cantidad de victorias.

    Restricciones:
        - cantidad debe ser un entero positivo.
    """
    lista_jugadores = cargar_jugadores(ruta_archivo)

    jugadores_ordenados = sorted(
        lista_jugadores,
        key=lambda jugador: jugador.victorias_defensor,
        reverse=True,
    )

    return [
        {
            "nombre_usuario": jugador.nombre_usuario,
            "victorias_defensor": jugador.victorias_defensor,
        }
        for jugador in jugadores_ordenados[:cantidad]
    ]


def obtener_top_atacantes(ruta_archivo=RUTA_ARCHIVO_JUGADORES,
                           cantidad=CANTIDAD_MAXIMA_RANKING):
    """
    Descripcion:
        Genera la lista de los mejores jugadores segun su cantidad
        de victorias como atacante, ordenados de mayor a menor.

    Entradas:
        ruta_archivo (str): Ruta del archivo JSON de jugadores.
        cantidad (int): Cantidad maxima de jugadores a incluir en el
            ranking. Por defecto es 5.

    Salidas:
        list[dict]: Lista de diccionarios con las claves
        "nombre_usuario" y "victorias_atacante", ordenada de mayor a
        menor cantidad de victorias.

    Restricciones:
        - cantidad debe ser un entero positivo.
    """
    lista_jugadores = cargar_jugadores(ruta_archivo)

    jugadores_ordenados = sorted(
        lista_jugadores,
        key=lambda jugador: jugador.victorias_atacante,
        reverse=True,
    )

    return [
        {
            "nombre_usuario": jugador.nombre_usuario,
            "victorias_atacante": jugador.victorias_atacante,
        }
        for jugador in jugadores_ordenados[:cantidad]
    ]
