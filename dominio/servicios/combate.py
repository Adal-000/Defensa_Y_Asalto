"""
Descripcion:
    Modulo encargado de la fase de combate del juego. Se ocupa del
    movimiento de unidades, los ataques entre torres, muros,
    unidades y base, la aplicacion de dano, la eliminacion de
    elementos sin vida y la activacion de habilidades especiales
    durante el combate.
"""


def calcular_distancia(fila_torre, columna_torre, fila_unidad, columna_unidad):
    """
    Descripcion:
        Calcula la distancia simple entre dos posiciones del tablero.
        Se usa principalmente para saber si una unidad esta dentro
        del alcance de una torre.

    Entradas:
        fila_torre (int): Fila donde se encuentra la torre.
        columna_torre (int): Columna donde se encuentra la torre.
        fila_unidad (int): Fila donde se encuentra la unidad.
        columna_unidad (int): Columna donde se encuentra la unidad.

    Salidas:
        int: Distancia calculada como la suma de las diferencias
        absolutas de fila y columna.

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
    distancia = calcular_distancia(
        torre.fila, torre.columna, unidad.fila, unidad.columna
    )
    return distancia <= torre.alcance


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


def _muro_en_posicion(lista_muros, fila, columna):
    """
    Descripcion:
        Busca un muro vivo en una posicion especifica del tablero.

    Entradas:
        lista_muros (list[Muro]): Muros actuales de la ronda.
        fila (int): Fila a revisar.
        columna (int): Columna a revisar.

    Salidas:
        Muro: Muro encontrado en la posicion indicada.
        None: Si no existe un muro vivo en esa posicion.

    Restricciones:
        - lista_muros puede estar vacia.
    """
    if lista_muros is None:
        return None

    for muro in lista_muros:
        if not muro.esta_destruido() and muro.fila == fila and muro.columna == columna:
            return muro
    return None


def _torre_en_posicion(lista_torres, fila, columna):
    """
    Descripcion:
        Busca una torre viva en una posicion especifica del tablero.
        Se usa para evitar que una unidad atraviese una estructura
        defensiva y para permitirle atacarla desde la casilla anterior.
    """
    if lista_torres is None:
        return None

    for torre in lista_torres:
        if not torre.esta_destruida() and torre.fila == fila and torre.columna == columna:
            return torre
    return None


def _estructura_en_posicion(lista_torres, lista_muros, fila, columna):
    torre = _torre_en_posicion(lista_torres, fila, columna)
    if torre is not None:
        return "torre", torre

    muro = _muro_en_posicion(lista_muros, fila, columna)
    if muro is not None:
        return "muro", muro

    return None, None


def mover_unidad(unidad, fila_objetivo, lista_muros=None, lista_torres=None):
    """
    Descripcion:
        Mueve una unidad hacia la base del defensor. La unidad avanza
        por su columna, pero no entra en la casilla de una torre o un
        muro. Si una estructura esta justo al frente, se queda en su
        casilla actual para atacarla durante la fase de ataque.
    """
    velocidad_actual = unidad.calcular_velocidad_actual()

    if velocidad_actual <= 0:
        return

    direccion = -1 if unidad.fila > fila_objetivo else 1

    for _ in range(velocidad_actual):
        siguiente_fila = unidad.fila + direccion

        if direccion == -1 and siguiente_fila < fila_objetivo:
            siguiente_fila = fila_objetivo
        elif direccion == 1 and siguiente_fila > fila_objetivo:
            siguiente_fila = fila_objetivo

        if siguiente_fila == fila_objetivo:
            break

        _, estructura = _estructura_en_posicion(
            lista_torres, lista_muros, siguiente_fila, unidad.columna
        )
        if estructura is not None:
            break

        unidad.fila = siguiente_fila

        if unidad.fila == fila_objetivo:
            break

def activar_habilidades_inicio_turno(lista_unidades, registrador_eventos=None):
    """
    Descripcion:
        Activa automaticamente habilidades de unidades que deben
        ocurrir antes del movimiento o antes de recibir dano, como
        escudo temporal, curacion y aumento de velocidad.

    Entradas:
        lista_unidades (list[Unidad]): Unidades actuales del
            atacante.
        registrador_eventos (list[str]): Lista opcional donde se
            agregan mensajes de eventos.

    Salidas:
        None: Modifica los estados internos de las unidades.

    Restricciones:
        - Solo se activan habilidades disponibles.
        - La curacion solo se activa si la unidad no tiene la vida
          completa.
    """
    for unidad in lista_unidades:
        if unidad.esta_eliminada() or not unidad.puede_usar_habilidad():
            continue

        debe_activar = False

        if unidad.habilidad == "escudo_temporal" and not unidad.escudo_activo:
            debe_activar = True
        elif unidad.habilidad == "curacion" and unidad.vida < unidad.vida_maxima:
            debe_activar = True
        elif unidad.habilidad == "aumento_velocidad" and unidad.velocidad_extra_temporal == 0:
            debe_activar = True

        if debe_activar:
            mensaje = unidad.activar_habilidad()
            if registrador_eventos is not None:
                registrador_eventos.append(mensaje)


def _buscar_unidad_en_rango(torre, lista_unidades):
    """
    Descripcion:
        Busca la primera unidad viva que este dentro del alcance de
        una torre.

    Entradas:
        torre (Torre): Torre que buscara objetivo.
        lista_unidades (list[Unidad]): Unidades atacantes actuales.

    Salidas:
        Unidad: Primera unidad viva encontrada dentro del rango.
        None: Si no hay unidades disponibles en rango.

    Restricciones:
        Ninguna.
    """
    for unidad in lista_unidades:
        if not unidad.esta_eliminada() and torre_en_rango(torre, unidad):
            return unidad
    return None


def _activar_habilidad_torre(torre, objetivo, lista_torres, lista_unidades,
                             registrador_eventos=None):
    """
    Descripcion:
        Ejecuta la habilidad especial de una torre cuando esta se
        encuentra disponible. Algunas habilidades usan un objetivo
        individual y otras afectan varias unidades o torres.

    Entradas:
        torre (Torre): Torre que activa la habilidad.
        objetivo (Unidad): Unidad objetivo principal. Puede ser None
            para habilidades de soporte.
        lista_torres (list[Torre]): Torres actuales del defensor.
        lista_unidades (list[Unidad]): Unidades actuales del atacante.
        registrador_eventos (list[str]): Lista opcional de eventos.

    Salidas:
        None: Modifica la vida o estado de unidades/torres y agrega
        eventos si corresponde.

    Restricciones:
        - La habilidad solo se activa si esta disponible.
    """
    if not torre.puede_usar_habilidad():
        return

    if torre.habilidad == "dano_area":
        unidades_afectadas = 0
        for unidad in lista_unidades:
            if not unidad.esta_eliminada() and torre_en_rango(torre, unidad):
                unidad.recibir_dano(torre.calcular_dano_ataque())
                unidades_afectadas += 1

        if unidades_afectadas > 0:
            torre.reiniciar_contador_habilidad()
            if registrador_eventos is not None:
                registrador_eventos.append(
                    f"{torre.nombre} usa dano en area contra "
                    f"{unidades_afectadas} unidad(es)."
                )
        return

    if torre.habilidad == "reparar_torre_cercana":
        hay_torre_danada = any(
            otra_torre is not torre
            and not otra_torre.esta_destruida()
            and otra_torre.vida < otra_torre.vida_maxima
            for otra_torre in lista_torres
        )
        if not hay_torre_danada:
            return

        mensaje = torre.activar_habilidad(objetivo=None, lista_torres=lista_torres)
        if registrador_eventos is not None:
            registrador_eventos.append(mensaje)
        return

    if objetivo is None:
        return

    if torre.habilidad in ("disparo_doble", "congelar_unidad", "aumentar_dano_temporal"):
        mensaje = torre.activar_habilidad(objetivo=objetivo, lista_torres=lista_torres)
        if registrador_eventos is not None:
            registrador_eventos.append(mensaje)


def fase_ataque_torres(lista_torres, lista_unidades, registrador_eventos=None):
    """
    Descripcion:
        Ejecuta el ataque de cada torre activa contra la primera
        unidad enemiga que se encuentre dentro de su alcance. Tambien
        activa habilidades especiales de las torres cuando estan
        disponibles.

    Entradas:
        lista_torres (list[Torre]): Torres del defensor.
        lista_unidades (list[Unidad]): Unidades del atacante.
        registrador_eventos (list[str]): Lista opcional donde se
            agregan mensajes describiendo lo ocurrido. Puede ser
            None si no se desea registrar eventos.

    Salidas:
        None: Modifica la vida o estado de las unidades atacadas.

    Restricciones:
        - Las torres destruidas no realizan ataques.
        - Las unidades ya eliminadas no pueden ser objetivo.
    """
    for torre in lista_torres:
        if torre.esta_destruida():
            continue

        objetivo = _buscar_unidad_en_rango(torre, lista_unidades)

        if objetivo is not None:
            dano = torre.calcular_dano_ataque()
            objetivo.recibir_dano(dano)
            if registrador_eventos is not None:
                registrador_eventos.append(
                    f"{torre.nombre} ataca a {objetivo.nombre} por {dano} de dano."
                )

        _activar_habilidad_torre(
            torre, objetivo, lista_torres, lista_unidades, registrador_eventos
        )


def _buscar_objetivo_unidad(unidad, lista_torres, lista_muros, base, fila_base):
    """
    Descripcion:
        Determina que objetivo debe atacar una unidad. Primero revisa
        si ya esta sobre una estructura por compatibilidad con estados
        anteriores; luego revisa la casilla que tiene al frente. Esto
        hace que las tropas no atraviesen torres o muros: se detienen
        y atacan desde la casilla anterior.
    """
    tipo, objetivo = _estructura_en_posicion(
        lista_torres, lista_muros, unidad.fila, unidad.columna
    )
    if objetivo is not None:
        return tipo, objetivo

    direccion = -1 if unidad.fila > fila_base else 1
    fila_frente = unidad.fila + direccion

    if direccion == -1 and fila_frente <= fila_base:
        return "base", base

    tipo, objetivo = _estructura_en_posicion(
        lista_torres, lista_muros, fila_frente, unidad.columna
    )
    if objetivo is not None:
        return tipo, objetivo

    if unidad_llego_a_base(unidad, fila_base):
        return "base", base

    return None, None

def _calcular_dano_unidad(unidad, tipo_objetivo):
    """
    Descripcion:
        Calcula el dano que una unidad debe aplicar a un objetivo,
        considerando habilidades especiales como dano extra contra
        torres.

    Entradas:
        unidad (Unidad): Unidad que realizara el ataque.
        tipo_objetivo (str): Tipo de objetivo: "torre", "muro" o
            "base".

    Salidas:
        int: Dano que debe aplicarse al objetivo.

    Restricciones:
        - tipo_objetivo debe ser uno de los valores indicados.
    """
    if tipo_objetivo == "torre" and unidad.habilidad == "dano_extra_torres":
        if unidad.puede_usar_habilidad():
            unidad.reiniciar_contador_habilidad()
            return int(unidad.dano * 1.5)
        return unidad.dano

    return unidad.calcular_dano_contra(tipo_objetivo)


def _aplicar_ataque_unidad(unidad, tipo_objetivo, objetivo,
                           registrador_eventos=None):
    """
    Descripcion:
        Aplica el dano de una unidad sobre un objetivo concreto y
        registra un mensaje de combate.

    Entradas:
        unidad (Unidad): Unidad que ataca.
        tipo_objetivo (str): Tipo de objetivo: "torre", "muro" o
            "base".
        objetivo: Objeto que recibira el dano.
        registrador_eventos (list[str]): Lista opcional de eventos.

    Salidas:
        int: Cantidad de dano aplicada.

    Restricciones:
        - objetivo debe tener metodo recibir_dano.
    """
    dano = _calcular_dano_unidad(unidad, tipo_objetivo)
    objetivo.recibir_dano(dano)

    if registrador_eventos is not None:
        if tipo_objetivo == "base":
            registrador_eventos.append(
                f"{unidad.nombre} ataca la base por {dano} de dano."
            )
        else:
            registrador_eventos.append(
                f"{unidad.nombre} ataca a {objetivo.nombre} por {dano} de dano."
            )

    return dano


def fase_ataque_unidades(lista_unidades, lista_torres, base, fila_base,
                          registrador_eventos=None, lista_muros=None):
    """
    Descripcion:
        Ejecuta el ataque de cada unidad activa. Si encuentra una
        torre o muro en su misma posicion, ataca esa estructura. Si
        ya llego a la fila de la base, ataca directamente a la base
        central. Tambien aplica ataque doble cuando corresponde.

    Entradas:
        lista_unidades (list[Unidad]): Unidades del atacante.
        lista_torres (list[Torre]): Torres del defensor.
        base (Base): Base central del defensor.
        fila_base (int): Fila en la que se encuentra la base central.
        registrador_eventos (list[str]): Lista opcional de eventos.
        lista_muros (list[Muro]): Muros actuales del defensor.

    Salidas:
        None: Modifica la vida de torres, muros o base.

    Restricciones:
        - Las unidades eliminadas no pueden atacar.
        - Las unidades congeladas no pueden atacar en este turno.
    """
    for unidad in lista_unidades:
        if unidad.esta_eliminada() or unidad.congelada:
            continue

        tipo_objetivo, objetivo = _buscar_objetivo_unidad(
            unidad, lista_torres, lista_muros, base, fila_base
        )

        if objetivo is None:
            continue

        _aplicar_ataque_unidad(unidad, tipo_objetivo, objetivo, registrador_eventos)

        if unidad.habilidad == "ataque_doble" and unidad.puede_usar_habilidad():
            if tipo_objetivo == "base" or not _objetivo_destruido(tipo_objetivo, objetivo):
                unidad.reiniciar_contador_habilidad()
                _aplicar_ataque_unidad(
                    unidad, tipo_objetivo, objetivo, registrador_eventos
                )
                if registrador_eventos is not None:
                    registrador_eventos.append(
                        f"{unidad.nombre} activa ataque doble."
                    )


def _objetivo_destruido(tipo_objetivo, objetivo):
    """
    Descripcion:
        Verifica si un objetivo de combate fue destruido o eliminado.

    Entradas:
        tipo_objetivo (str): Tipo de objetivo: "torre", "muro" o
            "base".
        objetivo: Objeto revisado.

    Salidas:
        bool: True si el objetivo ya no tiene vida, False en caso
        contrario.

    Restricciones:
        - El objetivo debe corresponder al tipo indicado.
    """
    if tipo_objetivo == "torre":
        return objetivo.esta_destruida()
    if tipo_objetivo == "muro":
        return objetivo.esta_destruido()
    if tipo_objetivo == "base":
        return objetivo.fue_destruida()
    return False


def eliminar_elementos_sin_vida(lista_torres, lista_unidades, lista_muros=None):
    """
    Descripcion:
        Filtra las listas de torres, unidades y muros, removiendo
        aquellos elementos que ya no tienen vida.

    Entradas:
        lista_torres (list[Torre]): Torres actuales del defensor.
        lista_unidades (list[Unidad]): Unidades actuales del
            atacante.
        lista_muros (list[Muro]): Muros actuales del defensor. Puede
            ser None.

    Salidas:
        tuple: Si no se pasan muros, retorna torres y unidades vivas.
        Si se pasan muros, retorna torres, unidades y muros vivos.

    Restricciones:
        Ninguna.
    """
    torres_vivas = [torre for torre in lista_torres if not torre.esta_destruida()]
    unidades_vivas = [unidad for unidad in lista_unidades if not unidad.esta_eliminada()]

    if lista_muros is None:
        return torres_vivas, unidades_vivas

    muros_vivos = [muro for muro in lista_muros if not muro.esta_destruido()]
    return torres_vivas, unidades_vivas, muros_vivos


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
                               registrador_eventos=None, lista_muros=None):
    """
    Descripcion:
        Ejecuta un turno completo de combate: activa habilidades de
        inicio, mueve unidades, resuelve ataques, avanza contadores
        y elimina elementos sin vida.

    Entradas:
        lista_torres (list[Torre]): Torres actuales del defensor.
        lista_unidades (list[Unidad]): Unidades actuales del
            atacante.
        base (Base): Base central del defensor.
        fila_base (int): Fila en la que se encuentra la base central.
        registrador_eventos (list[str]): Lista opcional de eventos.
        lista_muros (list[Muro]): Muros actuales del defensor. Puede
            ser None para mantener compatibilidad con pruebas simples.

    Salidas:
        tuple: Si no se pasan muros, retorna torres y unidades vivas.
        Si se pasan muros, retorna torres, unidades y muros vivos.

    Restricciones:
        Ninguna.
    """
    activar_habilidades_inicio_turno(lista_unidades, registrador_eventos)

    for unidad in lista_unidades:
        if not unidad.esta_eliminada():
            mover_unidad(unidad, fila_base, lista_muros, lista_torres)

    fase_ataque_torres(lista_torres, lista_unidades, registrador_eventos)
    fase_ataque_unidades(
        lista_unidades,
        lista_torres,
        base,
        fila_base,
        registrador_eventos,
        lista_muros,
    )

    avanzar_turno_combate(lista_torres, lista_unidades)

    return eliminar_elementos_sin_vida(lista_torres, lista_unidades, lista_muros)
