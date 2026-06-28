"""
Catalogo de habilidades especiales por faccion.

Cada faccion tiene una habilidad especial distinta tanto para el
defensor como para el atacante (ambos roles pueden usarla si juegan
esa faccion). La habilidad ataca un area del lado del rival:

- El defensor la dispara desde su base (fila 0) hacia el campo del
  atacante (filas 8 a 10).
- El atacante la dispara desde el lado contrario a la base del
  defensor (fila 10) hacia el campo del defensor (filas 1 a 7).

Estos efectos son ataques de area instantaneos, separados de las
compras normales de torres/muros/unidades: tienen su propio costo en
dinero y su propio tiempo de enfriamiento (cooldown) para que no se
puedan abusar turno a turno.
"""

FILA_BASE_DEFENSOR = 0
FILA_EXTREMO_ATACANTE = 10

HABILIDADES_POR_FACCION = {
    "España": {
        "nombre": "Bombardeo de artillería",
        "descripcion": "Una lluvia de obuses cae sobre el campo del rival.",
        "costo": 180,
        "cooldown_segundos": 18,
        "dano": 45,
        "filas_de_alcance": 3,
        "color": "#f1bf00",
        "tipo_efecto": "artilleria",
    },
    "Inglaterra": {
        "nombre": "Lluvia de flechas",
        "descripcion": "Una andanada de flechas en abanico golpea varias filas.",
        "costo": 150,
        "cooldown_segundos": 15,
        "dano": 35,
        "filas_de_alcance": 4,
        "color": "#cf142b",
        "tipo_efecto": "flechas",
    },
    "Alemania": {
        "nombre": "Gas tóxico",
        "descripcion": "Una nube de gas avanza y daña todo lo que toca durante varios segundos.",
        "costo": 170,
        "cooldown_segundos": 20,
        "dano": 30,
        "dano_persistente_turnos": 3,
        "filas_de_alcance": 5,
        "color": "#5a8f3c",
        "tipo_efecto": "gas",
    },
    "Rusia": {
        "nombre": "Ataque de mortero",
        "descripcion": "Una explosión concentrada de gran impacto en un punto del campo.",
        "costo": 190,
        "cooldown_segundos": 20,
        "dano": 55,
        "filas_de_alcance": 2,
        "color": "#0039a6",
        "tipo_efecto": "mortero",
    },
    "Italia": {
        "nombre": "Cortina de humo y fuego",
        "descripcion": "Fuego de cobertura que cruza el campo causando daño parejo.",
        "costo": 160,
        "cooldown_segundos": 16,
        "dano": 32,
        "filas_de_alcance": 4,
        "color": "#009246",
        "tipo_efecto": "fuego",
    },
    "EE.UU": {
        "nombre": "Lluvia de granadas",
        "descripcion": "Granadas lanzadas en arco desde la retaguardia.",
        "costo": 175,
        "cooldown_segundos": 18,
        "dano": 40,
        "filas_de_alcance": 3,
        "color": "#3c3b6e",
        "tipo_efecto": "granadas",
    },
    "EEUU": {
        "nombre": "Lluvia de granadas",
        "descripcion": "Granadas lanzadas en arco desde la retaguardia.",
        "costo": 175,
        "cooldown_segundos": 18,
        "dano": 40,
        "filas_de_alcance": 3,
        "color": "#3c3b6e",
        "tipo_efecto": "granadas",
    },
}

HABILIDAD_PREDETERMINADA = {
    "nombre": "Ataque especial",
    "descripcion": "Un ataque de area especial de la facción.",
    "costo": 170,
    "cooldown_segundos": 18,
    "dano": 35,
    "filas_de_alcance": 3,
    "color": "#888888",
    "tipo_efecto": "generico",
}


def obtener_habilidad_de_faccion(faccion):
    """
    Descripcion:
        Devuelve una copia de los datos de la habilidad especial de
        una faccion. Si la faccion no esta en el catalogo, devuelve
        una habilidad generica predeterminada para que el juego nunca
        se quede sin botón de habilidad por una faccion no mapeada.

    Entradas:
        faccion (str): Nombre de la faccion (por ejemplo "Alemania").

    Salidas:
        dict: Copia de los datos de la habilidad especial.

    Restricciones:
        Ninguna.
    """
    datos = HABILIDADES_POR_FACCION.get(str(faccion).strip())
    if datos is None:
        datos = HABILIDAD_PREDETERMINADA
    return dict(datos)


def calcular_filas_objetivo(rol, filas_de_alcance):
    """
    Descripcion:
        Calcula que filas del tablero recibe el impacto de la
        habilidad especial segun quien la dispara.

        - El defensor dispara desde su base (fila 0) hacia adelante,
          golpeando las primeras filas de la zona del atacante
          (8, 9, 10, ...).
        - El atacante dispara desde el extremo opuesto a la base
          (fila 10) hacia atras, golpeando las ultimas filas de la
          zona del defensor (7, 6, 5, ...).

    Entradas:
        rol (str): "defensor" o "atacante".
        filas_de_alcance (int): Cuantas filas de profundidad cubre el
            impacto.

    Salidas:
        set[int]: Conjunto de filas afectadas.

    Restricciones:
        - rol debe ser "defensor" o "atacante".
    """
    filas_de_alcance = max(1, int(filas_de_alcance))

    if rol == "defensor":
        # Golpea las primeras filas de la zona atacante (8..10).
        inicio = 8
        return set(range(inicio, min(inicio + filas_de_alcance, 11)))

    # Atacante: golpea las ultimas filas de la zona defensor (7..1).
    fin = 7
    inicio = max(1, fin - filas_de_alcance + 1)
    return set(range(inicio, fin + 1))
