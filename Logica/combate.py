"""
Descripcion:
    Modulo encargado de la fase de combate del juego. Se ocupa del
    movimiento de unidades, los ataques entre torres y unidades, la
    aplicacion de dano, la eliminacion de elementos sin vida y la
    activacion de habilidades especiales durante el combate.
"""


def calcular_distancia(fila_torre, columna_torre, fila_unidad, columna_unidad):
    """
    Descripcion:
        Calcula la distancia simple (en numero de casillas) entre
        una torre y una unidad, usada para determinar si la torre
        tiene a la unidad dentro de su alcance.

    Entradas:
        fila_torre (int): Fila donde se encuentra la torre.
        columna_torre (int): Columna donde se encuentra la torre.
        fila_unidad (int): Fila donde se encuentra la unidad.
        columna_unidad (int): Columna donde se encuentra la unidad.

    Salidas:
        int: Distancia entre la torre y la unidad, calculada como la
        suma de las diferencias absolutas de fila y columna.

    Restricciones:
        Ninguna.
    """
    return abs(fila_torre - fila_unidad) + abs(columna_torre - columna_unidad)


def torre_en_rango(torre, unidad):
    """
    Descripcion:
        Determina si una unidad se encuentra dentro del alcance de
        ataque de una torre.

    Entradas:
        torre (Torre): Torre que intenta atacar.
        unidad (Unidad): Unidad objetivo.

    Salidas:
        bool: True si la unidad esta dentro del alcance de la torre,
        False en caso contrario.

    Restricciones:
        Ninguna.
    """
    distancia = calcular_distancia(torre.fila, torre.columna,
                                    unidad.fila, unidad.columna)
    return distancia <= torre.alcance


def mover_unidad(unidad, fila_objetivo):
    """
    Descripcion:
        Mueve una unidad hacia la base del defensor, avanzando segun
        su velocidad actual. Se asume que la base se encuentra en la
        fila_objetivo y que las unidades avanzan disminuyendo su
        numero de fila.

    Entradas:
        unidad (Unidad): Unidad que se va a mover.
        fila_objetivo (int): Fila en la que se encuentra la base
            central, limite del movimiento de la unidad.

    Salidas:
        None: Modifica el atributo fila de la unidad.

    Restricciones:
        - Si la unidad esta congelada, no se desplaza en este turno.
    """
    velocidad_actual = unidad.calcular_velocidad_actual()

    if unidad.fila < fila_objetivo:
        unidad.fila = min(fila_objetivo, unidad.fila + velocidad_actual)
    elif unidad.fila > fila_objetivo:
        unidad.fila = max(fila_objetivo, unidad.fila - velocidad_actual)


def unidad_llego_a_base(unidad, fila_base):
    """
    Descripcion:
        Indica si una unidad ha alcanzado la fila donde se encuentra
        la base central.

    Entradas:
        unidad (Unidad): Unidad a evaluar.
        fila_base (int): Fila en la que se encuentra la base central.

    Salidas:
        bool: True si la unidad se encuentra en la misma fila que la
        base, False en caso contrario.

    Restricciones:
        Ninguna.
    """
    return unidad.fila == fila_base


def fase_ataque_torres(lista_torres, lista_unidades, registrador_eventos=None):
    """
    Descripcion:
        Ejecuta el ataque de cada torre activa contra la primera
        unidad enemiga que se encuentre dentro de su alcance.

    Entradas:
        lista_torres (list[Torre]): Torres del defensor.
        lista_unidades (list[Unidad]): Unidades del atacante.
        registrador_eventos (list[str]): Lista opcional donde se
            agregan mensajes describiendo lo ocurrido. Puede ser
            None si no se desea registrar eventos.

    Salidas:
        None: Modifica la vida de las unidades atacadas y, en caso
        de existir, agrega mensajes a registrador_eventos.

    Restricciones:
        - Las torres destruidas no realizan ataques.
        - Las unidades ya eliminadas no pueden ser objetivo.
    """
    for torre in lista_torres:
        if torre.esta_destruida():
            continue

        for unidad in lista_unidades:
            if unidad.esta_eliminada():
                continue

            if torre_en_rango(torre, unidad):
                unidad.recibir_dano(torre.calcular_dano_ataque())
                if registrador_eventos is not None:
                    registrador_eventos.append(
                        f"{torre.nombre} ataca a {unidad.nombre} por "
                        f"{torre.calcular_dano_ataque()} de dano."
                    )
                break


def fase_ataque_unidades(lista_unidades, lista_torres, base,
                          fila_base, registrador_eventos=None):
    """
    Descripcion:
        Ejecuta el ataque de cada unidad activa. Si la unidad
        encuentra una torre en su misma posicion, ataca a la torre.
        Si la unidad ya llego a la fila de la base, ataca
        directamente a la base central.

    Entradas:
        lista_unidades (list[Unidad]): Unidades del atacante.
        lista_torres (list[Torre]): Torres del defensor.
        base (Base): Base central del defensor.
        fila_base (int): Fila en la que se encuentra la base central.
        registrador_eventos (list[str]): Lista opcional donde se
            agregan mensajes describiendo lo ocurrido. Puede ser
            None si no se desea registrar eventos.

    Salidas:
        None: Modifica la vida de las torres o de la base, y en
        caso de existir, agrega mensajes a registrador_eventos.

    Restricciones:
        - Las unidades eliminadas no pueden atacar.
        - Las unidades congeladas no pueden atacar en este turno.
    """
    for unidad in lista_unidades:
        if unidad.esta_eliminada() or unidad.congelada:
            continue

        torre_en_misma_posicion = None
        for torre in lista_torres:
            if (not torre.esta_destruida() and torre.fila == unidad.fila
                    and torre.columna == unidad.columna):
                torre_en_misma_posicion = torre
                break

        if torre_en_misma_posicion is not None:
            dano = unidad.calcular_dano_contra("torre")
            torre_en_misma_posicion.recibir_dano(dano)
            if registrador_eventos is not None:
                registrador_eventos.append(
                    f"{unidad.nombre} ataca a {torre_en_misma_posicion.nombre} "
                    f"por {dano} de dano."
                )
        elif unidad_llego_a_base(unidad, fila_base):
            dano = unidad.calcular_dano_contra("base")
            base.recibir_dano(dano)
            if registrador_eventos is not None:
                registrador_eventos.append(
                    f"{unidad.nombre} ataca la base por {dano} de dano."
                )


def eliminar_elementos_sin_vida(lista_torres, lista_unidades):
    """
    Descripcion:
        Filtra las listas de torres y unidades, removiendo aquellas
        que ya fueron destruidas o eliminadas por falta de vida.

    Entradas:
        lista_torres (list[Torre]): Torres actuales del defensor.
        lista_unidades (list[Unidad]): Unidades actuales del
            atacante.

    Salidas:
        tuple[list[Torre], list[Unidad]]: Tupla con la nueva lista
        de torres vivas y la nueva lista de unidades vivas.

    Restricciones:
        Ninguna.
    """
    torres_vivas = [torre for torre in lista_torres if not torre.esta_destruida()]
    unidades_vivas = [unidad for unidad in lista_unidades if not unidad.esta_eliminada()]
    return torres_vivas, unidades_vivas


def avanzar_turno_combate(lista_torres, lista_unidades):
    """
    Descripcion:
        Actualiza los contadores de habilidades y efectos temporales
        de todas las torres y unidades activas, simulando el paso de
        un turno completo.

    Entradas:
        lista_torres (list[Torre]): Torres actuales del defensor.
        lista_unidades (list[Unidad]): Unidades actuales del
            atacante.

    Salidas:
        None: Modifica los contadores internos de cada torre y
        unidad.

    Restricciones:
        Ninguna.
    """
    for torre in lista_torres:
        if not torre.esta_destruida():
            torre.avanzar_turno()

    for unidad in lista_unidades:
        if not unidad.esta_eliminada():
            unidad.avanzar_turno()


def ejecutar_turno_de_combate(lista_torres, lista_unidades, base, fila_base,
                               registrador_eventos=None):
    """
    Descripcion:
        Ejecuta un turno completo de combate: mueve las unidades,
        realiza los ataques de torres y unidades, aplica el avance
        de contadores y elimina los elementos sin vida.

    Entradas:
        lista_torres (list[Torre]): Torres actuales del defensor.
        lista_unidades (list[Unidad]): Unidades actuales del
            atacante.
        base (Base): Base central del defensor.
        fila_base (int): Fila en la que se encuentra la base central.
        registrador_eventos (list[str]): Lista opcional donde se
            agregan mensajes describiendo lo ocurrido durante el
            turno.

    Salidas:
        tuple[list[Torre], list[Unidad]]: Listas actualizadas de
        torres y unidades vivas despues del turno.

    Restricciones:
        Ninguna.
    """
    for unidad in lista_unidades:
        if not unidad.esta_eliminada():
            mover_unidad(unidad, fila_base)

    fase_ataque_torres(lista_torres, lista_unidades, registrador_eventos)
    fase_ataque_unidades(lista_unidades, lista_torres, base, fila_base,
                          registrador_eventos)

    avanzar_turno_combate(lista_torres, lista_unidades)

    return eliminar_elementos_sin_vida(lista_torres, lista_unidades)
