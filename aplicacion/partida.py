"""
Descripcion:
    Modulo que define la clase Partida, encargada de coordinar todo
    el flujo del juego "Defensa y Asalto de Base": sistema de
    dinero, rondas, compras de torres, muros y unidades, fase de
    combate y condiciones de victoria.
"""

import time

from dominio.entidades.base import Base
from dominio.entidades.torre import crear_torre_por_tipo
from dominio.entidades.unidad import crear_unidad_por_tipo
from dominio.entidades.muro import crear_muro
from dominio.entidades.habilidad_especial import (
    obtener_habilidad_de_faccion,
    calcular_filas_objetivo,
)
from dominio.servicios.combate import ejecutar_turno_de_combate
from infraestructura.persistencia.archivos import actualizar_victoria

DINERO_BASE_RONDA = 500
DINERO_BASE_ATACANTE_EXTRA = 250   # Bono extra que solo recibe el atacante
BONO_GANADOR_RONDA = 200
INCREMENTO_DINERO_POR_RONDA = 200
RONDAS_PARA_GANAR_PARTIDA = 3
SEGUNDOS_PREPARACION_ATACANTE = 15
SEGUNDOS_PREPARACION_DEFENSOR = 15
SEGUNDOS_ESPERA_REFUERZO_ATACANTE = 7
FILA_BASE = 0
FILAS_DEFENSOR_VALIDAS = range(1, 8)
FILAS_ATACANTE_VALIDAS = range(8, 11)
MAXIMO_TURNOS_POR_RONDA = 45
TURNOS_ESPERA_ATACANTE_SIN_UNIDADES = 7
CANTIDAD_FILAS_TABLERO = 11
CANTIDAD_COLUMNAS_TABLERO = 6
RECOMPENSA_DEFENSOR_POR_UNIDAD = 20
RECOMPENSA_ATACANTE_POR_TORRE_DANADA = 10
RECOMPENSA_ATACANTE_POR_TORRE_DESTRUIDA = 30
RECOMPENSA_ATACANTE_POR_MURO_DANADO = 8
RECOMPENSA_ATACANTE_POR_MURO_DESTRUIDO = 20
RECOMPENSA_ATACANTE_POR_BASE_DANADA = 15
FASE_CONSTRUCCION_DEFENSOR = "construccion_defensor"
FASE_ATAQUE_ATACANTE = "ataque_atacante"
FASE_COMBATE = "combate"


class Partida:
    """
    Descripcion:
        Representa una partida completa entre un jugador defensor y
        un jugador atacante. Administra el dinero de cada jugador,
        las estructuras y unidades en juego, la base central, el
        numero de rondas ganadas y el historial de eventos.

    Entradas:
        nombre_defensor (str): Nombre de usuario del jugador que
            actua como defensor.
        nombre_atacante (str): Nombre de usuario del jugador que
            actua como atacante.

    Salidas:
        No retorna nada. Construye una instancia de Partida lista
        para iniciar la primera ronda.

    Restricciones:
        - nombre_defensor y nombre_atacante deben corresponder a
          jugadores previamente registrados en el sistema.
        - nombre_defensor y nombre_atacante no deben ser iguales.
    """

    def __init__(self, nombre_defensor, nombre_atacante, guardar_victorias=True):
        self.nombre_defensor = nombre_defensor
        self.nombre_atacante = nombre_atacante
        self.guardar_victorias = guardar_victorias

        self.dinero_defensor = 0
        self.dinero_atacante = 0

        self.torres = []
        self.muros = []
        self.unidades = []
        self.base = Base()

        self.rondas_ganadas_defensor = 0
        self.rondas_ganadas_atacante = 0
        self.numero_ronda = 0
        self.turnos_en_ronda_actual = 0
        self.turnos_sin_unidades_atacantes = 0
        self.fase_ronda = FASE_CONSTRUCCION_DEFENSOR
        self.tiempo_inicio_fase = None
        self.rol_ganador_ultima_ronda = None
        self.esperando_refuerzo_atacante = False
        self.tiempo_inicio_espera_refuerzo = None

        self.partida_finalizada = False
        self.ganador_partida = None
        self.rol_ganador_partida = None

        self.faccion_defensor = None
        self.faccion_atacante = None
        self.ultimo_uso_habilidad_defensor = None
        self.ultimo_uso_habilidad_atacante = None

        self.historial_eventos = []

        self.iniciar_nueva_ronda()

    def establecer_faccion(self, rol, faccion):
        """
        Descripcion:
            Registra que faccion esta usando el defensor o el
            atacante. Esto determina cual es su habilidad especial
            (cada faccion tiene una distinta) y no afecta dinero,
            vida, daño ni ninguna otra regla del juego.

        Entradas:
            rol (str): "defensor" o "atacante".
            faccion (str): Nombre de la faccion elegida.

        Salidas:
            tuple[bool, str]: Exito de la accion y mensaje
            descriptivo.

        Restricciones:
            - rol debe ser "defensor" o "atacante".
        """
        if rol == "defensor":
            self.faccion_defensor = faccion
            return True, f"Facción del defensor establecida en {faccion}."
        if rol == "atacante":
            self.faccion_atacante = faccion
            return True, f"Facción del atacante establecida en {faccion}."
        return False, "Rol invalido para establecer facción."

    def iniciar_nueva_ronda(self):
        """
        Descripcion:
            Prepara una nueva ronda: reinicia la base, limpia torres,
            muros y unidades de la ronda anterior, entrega el dinero
            inicial del defensor y deja la ronda en fase de construccion.

        Entradas:
            Ninguna.

        Salidas:
            None: Modifica el estado interno de la partida.

        Restricciones:
            - No debe llamarse si la partida ya finalizo.
        """
        if self.partida_finalizada:
            return

        self.numero_ronda += 1
        self.turnos_en_ronda_actual = 0
        self.turnos_sin_unidades_atacantes = 0
        self.torres = []
        self.muros = []
        self.unidades = []
        self.base.reiniciar()
        # Orden de cada ronda: primero el atacante coloca tropas (15s),
        # despues el atacante queda bloqueado y el defensor coloca sus
        # defensas (15s) y por ultimo inicia el combate.
        self.fase_ronda = FASE_ATAQUE_ATACANTE
        self.tiempo_inicio_fase = time.time()

        dinero_base = DINERO_BASE_RONDA + (
            INCREMENTO_DINERO_POR_RONDA * (self.numero_ronda - 1)
        )
        dinero_ganador = dinero_base + BONO_GANADOR_RONDA

        if self.rol_ganador_ultima_ronda == "defensor":
            self.dinero_defensor = dinero_ganador
            self.dinero_atacante = dinero_base + DINERO_BASE_ATACANTE_EXTRA
        elif self.rol_ganador_ultima_ronda == "atacante":
            self.dinero_defensor = dinero_base
            self.dinero_atacante = dinero_ganador + DINERO_BASE_ATACANTE_EXTRA
        else:
            self.dinero_defensor = dinero_base
            self.dinero_atacante = dinero_base + DINERO_BASE_ATACANTE_EXTRA

        self.historial_eventos.append(
            f"Inicia la ronda {self.numero_ronda}: el atacante prepara tropas primero; luego el defensor planea la defensa."
        )
        self.historial_eventos.append(
            f"Defensor recibe ${self.dinero_defensor} y atacante recibe ${self.dinero_atacante}."
        )

    def iniciar_fase_ataque(self):
        """
        Descripcion:
            Cierra la construccion del defensor y entrega el dinero
            inicial al atacante para comprar y colocar unidades.
        """
        if self.partida_finalizada:
            return False, "La partida ya finalizó."

        if self.fase_ronda == FASE_ATAQUE_ATACANTE:
            return True, "La fase de ataque ya está activa."

        if self.fase_ronda == FASE_COMBATE:
            return False, "No se puede volver a comprar unidades durante el combate."

        self.fase_ronda = FASE_ATAQUE_ATACANTE
        self.tiempo_inicio_fase = time.time()
        mensaje = (
            f"Fase de ataque activa. Atacante disponible: ${self.dinero_atacante}."
        )
        self.historial_eventos.append(mensaje)
        return True, mensaje


    def iniciar_fase_defensa(self):
        """
        Descripcion:
            Cierra la preparacion del atacante (queda bloqueado para
            colocar mas tropas hasta el combate) y abre los 15
            segundos de preparacion del defensor.
        """
        if self.partida_finalizada:
            return False, "La partida ya finalizó."

        if self.fase_ronda == FASE_CONSTRUCCION_DEFENSOR:
            return True, "La fase de defensa ya está activa."

        if self.fase_ronda == FASE_COMBATE:
            return False, "La defensa inicial ya terminó; durante el combate ambos pueden comprar."

        self.fase_ronda = FASE_CONSTRUCCION_DEFENSOR
        self.tiempo_inicio_fase = time.time()
        mensaje = "Fase de defensa activa: el defensor planea sus estructuras."
        self.historial_eventos.append(mensaje)
        return True, mensaje

    def iniciar_fase_combate(self):
        """
        Descripcion:
            Inicia la fase de combate luego de la construccion del
            defensor y la compra/colocacion de unidades del atacante.
            Si el atacante no colocó ninguna unidad durante su tiempo
            de preparacion, el defensor gana la ronda directamente en
            lugar de iniciar un combate vacio.
        """
        if self.partida_finalizada:
            return False, "La partida ya finalizó."

        if self.fase_ronda == FASE_COMBATE:
            return True, "La fase de combate ya está activa."

        if self.fase_ronda == FASE_ATAQUE_ATACANTE:
            return False, self.iniciar_fase_defensa()[1]

        if len(self.unidades) == 0:
            self.historial_eventos.append(
                "El atacante no colocó unidades durante la preparación. "
                "El defensor gana la ronda."
            )
            self._finalizar_ronda("defensor")
            return True, "Sin unidades atacantes: el defensor gana la ronda."

        self.fase_ronda = FASE_COMBATE
        self.tiempo_inicio_fase = time.time()
        self.esperando_refuerzo_atacante = False
        self.tiempo_inicio_espera_refuerzo = None
        mensaje = "Inicia la fase de combate."
        self.historial_eventos.append(mensaje)
        return True, mensaje

    def _posicion_esta_dentro_del_tablero(self, fila, columna):
        """
        Descripcion:
            Valida si una posicion pertenece al tablero definido por
            la logica de la partida.

        Entradas:
            fila (int): Fila que se desea revisar.
            columna (int): Columna que se desea revisar.

        Salidas:
            bool: True si la posicion esta dentro del tablero, False
            en caso contrario.

        Restricciones:
            - fila y columna deben ser numeros enteros.
        """
        return (
            isinstance(fila, int)
            and isinstance(columna, int)
            and 0 <= fila < CANTIDAD_FILAS_TABLERO
            and 0 <= columna < CANTIDAD_COLUMNAS_TABLERO
        )

    def _posicion_defensiva_ocupada(self, fila, columna):
        """
        Descripcion:
            Determina si una posicion ya esta ocupada por una torre o
            un muro del defensor.

        Entradas:
            fila (int): Fila a revisar.
            columna (int): Columna a revisar.

        Salidas:
            bool: True si la posicion esta ocupada, False en caso
            contrario.

        Restricciones:
            Ninguna.
        """
        for torre in self.torres:
            if torre.fila == fila and torre.columna == columna:
                return True

        for muro in self.muros:
            if muro.fila == fila and muro.columna == columna:
                return True

        return False

    def _posicion_unidad_ocupada(self, fila, columna):
        """
        Descripcion:
            Determina si una posicion ya esta ocupada por una unidad
            atacante.

        Entradas:
            fila (int): Fila a revisar.
            columna (int): Columna a revisar.

        Salidas:
            bool: True si existe una unidad en esa posicion, False
            en caso contrario.

        Restricciones:
            Ninguna.
        """
        for unidad in self.unidades:
            if unidad.fila == fila and unidad.columna == columna:
                return True
        return False

    def _validar_compra_defensiva(self, fila, columna):
        """
        Descripcion:
            Valida que una torre o muro pueda colocarse en la
            posicion indicada.

        Entradas:
            fila (int): Fila donde se quiere colocar la defensa.
            columna (int): Columna donde se quiere colocar la defensa.

        Salidas:
            tuple[bool, str]: Indica si la posicion es valida y un
            mensaje descriptivo.

        Restricciones:
            - No se permite colocar defensas en la fila de la base.
            - No se permite usar posiciones ocupadas.
        """
        if not self._posicion_esta_dentro_del_tablero(fila, columna):
            return False, "La posicion esta fuera del tablero."

        if fila == FILA_BASE:
            return False, "No se puede colocar una defensa sobre la base."

        if fila not in FILAS_DEFENSOR_VALIDAS:
            return False, "Las defensas solo se colocan en las filas 1 a 7."

        if self._posicion_defensiva_ocupada(fila, columna):
            return False, "La posicion ya esta ocupada por una defensa."

        return True, "Posicion valida."

    def _validar_compra_unidad(self, fila, columna):
        """
        Descripcion:
            Valida que una unidad atacante pueda colocarse en la
            posicion indicada.

        Entradas:
            fila (int): Fila donde se quiere colocar la unidad.
            columna (int): Columna donde se quiere colocar la unidad.

        Salidas:
            tuple[bool, str]: Indica si la posicion es valida y un
            mensaje descriptivo.

        Restricciones:
            - No se permite colocar unidades directamente sobre la
              base central.
            - No se permite colocar unidades sobre otra unidad.
        """
        if not self._posicion_esta_dentro_del_tablero(fila, columna):
            return False, "La posicion esta fuera del tablero."

        if fila == FILA_BASE:
            return False, "No se puede colocar una unidad sobre la base."

        if fila not in FILAS_ATACANTE_VALIDAS:
            return False, "Las unidades solo se colocan en las filas 8 a 10."

        if self._posicion_unidad_ocupada(fila, columna):
            return False, "La posicion ya esta ocupada por una unidad."

        return True, "Posicion valida."

    def comprar_torre(self, tipo_torre, fila, columna):
        """
        Descripcion:
            Permite al defensor comprar y colocar una torre en el
            tablero, siempre que tenga dinero suficiente y la
            posicion sea valida.

        Entradas:
            tipo_torre (str): Tipo de torre a comprar.
            fila (int): Fila del tablero donde se colocara la torre.
            columna (int): Columna del tablero donde se colocara la
                torre.

        Salidas:
            tuple[bool, str]: El primer valor indica si la compra fue
            exitosa. El segundo valor es un mensaje descriptivo.

        Restricciones:
            - tipo_torre debe ser un tipo de torre valido.
            - El defensor debe tener dinero suficiente.
            - La posicion debe estar libre y dentro del tablero.
        """
        if self.partida_finalizada:
            return False, "La partida ya finalizó."

        # El defensor puede colocar torres en cualquier fase (incluso durante el combate)

        posicion_valida, mensaje_posicion = self._validar_compra_defensiva(
            fila, columna
        )
        if not posicion_valida:
            return False, mensaje_posicion

        nueva_torre = crear_torre_por_tipo(tipo_torre, fila, columna)

        if nueva_torre is None:
            return False, "Tipo de torre invalido."

        if self.dinero_defensor < nueva_torre.costo:
            return False, "El defensor no tiene suficiente dinero."

        self.dinero_defensor -= nueva_torre.costo
        self.torres.append(nueva_torre)
        self.historial_eventos.append(
            f"El defensor compra {nueva_torre.nombre} en ({fila}, {columna})."
        )

        return True, f"{nueva_torre.nombre} comprada correctamente."

    def comprar_muro(self, fila, columna):
        """
        Descripcion:
            Permite al defensor comprar y colocar un muro en el
            tablero. El muro sirve para bloquear o retrasar unidades
            atacantes.

        Entradas:
            fila (int): Fila del tablero donde se colocara el muro.
            columna (int): Columna del tablero donde se colocara el
                muro.

        Salidas:
            tuple[bool, str]: El primer valor indica si la compra fue
            exitosa. El segundo valor es un mensaje descriptivo.

        Restricciones:
            - El defensor debe tener dinero suficiente.
            - La posicion debe estar libre y dentro del tablero.
        """
        if self.partida_finalizada:
            return False, "La partida ya finalizó."

        # El defensor puede colocar muros en cualquier fase (incluso durante el combate)

        posicion_valida, mensaje_posicion = self._validar_compra_defensiva(
            fila, columna
        )
        if not posicion_valida:
            return False, mensaje_posicion

        nuevo_muro = crear_muro(fila, columna)

        if self.dinero_defensor < nuevo_muro.costo:
            return False, "El defensor no tiene suficiente dinero."

        self.dinero_defensor -= nuevo_muro.costo
        self.muros.append(nuevo_muro)
        self.historial_eventos.append(
            f"El defensor compra un muro en ({fila}, {columna})."
        )

        return True, "Muro comprado correctamente."

    def comprar_unidad(self, tipo_unidad, fila, columna):
        """
        Descripcion:
            Permite al atacante comprar y colocar una unidad en el
            tablero, siempre que tenga dinero suficiente y la
            posicion sea valida.

        Entradas:
            tipo_unidad (str): Tipo de unidad a comprar.
            fila (int): Fila del tablero donde se colocara la unidad.
            columna (int): Columna del tablero donde se colocara la
                unidad.

        Salidas:
            tuple[bool, str]: El primer valor indica si la compra fue
            exitosa. El segundo valor es un mensaje descriptivo.

        Restricciones:
            - tipo_unidad debe ser un tipo de unidad valido.
            - El atacante debe tener dinero suficiente.
            - La posicion debe estar libre y dentro del tablero.
        """
        if self.partida_finalizada:
            return False, "La partida ya finalizó."

        # El atacante puede colocar unidades en cualquier fase excepto cuando la partida terminó

        posicion_valida, mensaje_posicion = self._validar_compra_unidad(
            fila, columna
        )
        if not posicion_valida:
            return False, mensaje_posicion

        nueva_unidad = crear_unidad_por_tipo(tipo_unidad, fila, columna)

        if nueva_unidad is None:
            return False, "Tipo de unidad invalido."

        if self.dinero_atacante < nueva_unidad.costo:
            return False, "El atacante no tiene suficiente dinero."

        self.dinero_atacante -= nueva_unidad.costo
        self.unidades.append(nueva_unidad)
        self.turnos_sin_unidades_atacantes = 0
        self.historial_eventos.append(
            f"El atacante compra {nueva_unidad.nombre} en ({fila}, {columna})."
        )

        return True, f"{nueva_unidad.nombre} comprada correctamente."

    def _segundos_restantes_cooldown_habilidad(self, rol):
        """
        Descripcion:
            Calcula cuantos segundos faltan para que el rol indicado
            pueda volver a usar su habilidad especial de facción.

        Entradas:
            rol (str): "defensor" o "atacante".

        Salidas:
            int: Segundos restantes de enfriamiento (0 si ya esta
            disponible).

        Restricciones:
            Ninguna.
        """
        faccion = self.faccion_defensor if rol == "defensor" else self.faccion_atacante
        habilidad = obtener_habilidad_de_faccion(faccion)
        ultimo_uso = (
            self.ultimo_uso_habilidad_defensor
            if rol == "defensor"
            else self.ultimo_uso_habilidad_atacante
        )
        if ultimo_uso is None:
            return 0
        transcurrido = time.time() - ultimo_uso
        restante = habilidad["cooldown_segundos"] - int(transcurrido)
        return max(0, restante)

    def usar_habilidad_especial(self, rol):
        """
        Descripcion:
            Activa la habilidad especial de la facción del rol que la
            solicita. Es un ataque de area instantaneo independiente
            de las compras normales: tiene su propio costo en dinero
            y su propio tiempo de enfriamiento.

            - Si la usa el defensor, dispara desde su base (fila 0)
              hacia las primeras filas de la zona del atacante y daña
              a las unidades que esten ahi.
            - Si la usa el atacante, dispara desde el lado contrario
              a la base (fila 10) hacia las ultimas filas de la zona
              del defensor y daña a las torres y muros que esten ahi.

        Entradas:
            rol (str): "defensor" o "atacante".

        Salidas:
            tuple[bool, str]: Exito de la accion y mensaje
            descriptivo. El mensaje de exito incluye cuantos objetivos
            fueron alcanzados.

        Restricciones:
            - rol debe ser "defensor" o "atacante".
            - El rol debe tener dinero suficiente para el costo de su
              habilidad.
            - La habilidad debe estar fuera de su tiempo de
              enfriamiento.
            - No se puede usar si la partida ya finalizó.
        """
        if self.partida_finalizada:
            return False, "La partida ya finalizó."

        if rol not in ("defensor", "atacante"):
            return False, "Rol invalido."

        if rol == "defensor" and self.fase_ronda == FASE_ATAQUE_ATACANTE:
            return False, "Espera a tu turno de preparación para usar la habilidad."

        if rol == "atacante" and self.fase_ronda == FASE_CONSTRUCCION_DEFENSOR:
            return False, "Estás bloqueado mientras el defensor prepara sus defensas."

        faccion = self.faccion_defensor if rol == "defensor" else self.faccion_atacante
        habilidad = obtener_habilidad_de_faccion(faccion)

        segundos_cooldown = self._segundos_restantes_cooldown_habilidad(rol)
        if segundos_cooldown > 0:
            return False, f"Habilidad en enfriamiento: espera {segundos_cooldown}s más."

        dinero_disponible = self.dinero_defensor if rol == "defensor" else self.dinero_atacante
        if dinero_disponible < habilidad["costo"]:
            return False, f"Necesitas ${habilidad['costo']} para usar {habilidad['nombre']}."

        filas_objetivo = calcular_filas_objetivo(rol, habilidad["filas_de_alcance"])
        dano = habilidad["dano"]
        objetivos_alcanzados = 0

        if rol == "defensor":
            self.dinero_defensor -= habilidad["costo"]
            self.ultimo_uso_habilidad_defensor = time.time()
            for unidad in self.unidades:
                if unidad.fila in filas_objetivo and unidad.vida > 0:
                    unidad.vida = max(0, unidad.vida - dano)
                    objetivos_alcanzados += 1
            self.unidades = [u for u in self.unidades if u.vida > 0]
        else:
            self.dinero_atacante -= habilidad["costo"]
            self.ultimo_uso_habilidad_atacante = time.time()
            for torre in self.torres:
                if torre.fila in filas_objetivo and torre.vida > 0:
                    torre.vida = max(0, torre.vida - dano)
                    objetivos_alcanzados += 1
            for muro in self.muros:
                if muro.fila in filas_objetivo and muro.vida > 0:
                    muro.vida = max(0, muro.vida - dano)
                    objetivos_alcanzados += 1
            self.torres = [t for t in self.torres if t.vida > 0]
            self.muros = [m for m in self.muros if m.vida > 0]

        mensaje = (
            f"{habilidad['nombre']} alcanzó {objetivos_alcanzados} objetivo(s)."
            if objetivos_alcanzados > 0
            else f"{habilidad['nombre']} no alcanzó ningún objetivo."
        )
        self.historial_eventos.append(f"[{rol}] usa {habilidad['nombre']}: {mensaje}")
        return True, mensaje

    def _otorgar_dinero_por_combate(self, vida_torres_antes,
                                     vida_unidades_antes, vida_muros_antes,
                                     vida_base_antes):
        """
        Descripcion:
            Otorga dinero a los jugadores segun lo ocurrido durante
            el ultimo turno de combate: el defensor gana dinero por
            unidades eliminadas y el atacante gana dinero por torres
            danadas, torres destruidas o dano causado a la base.

        Entradas:
            vida_torres_antes (dict): Relacion entre id de torre y
                vida antes del combate.
            vida_unidades_antes (dict): Relacion entre id de unidad y
                vida antes del combate.
            vida_muros_antes (dict): Relacion entre id de muro y
                vida antes del combate.
            vida_base_antes (int): Vida de la base antes del combate.

        Salidas:
            None: Modifica dinero_defensor y dinero_atacante.

        Restricciones:
            Ninguna.
        """
        eventos_dinero = []

        for identificador_unidad in vida_unidades_antes:
            unidad_actual = next(
                (unidad for unidad in self.unidades if id(unidad) == identificador_unidad),
                None,
            )
            if unidad_actual is None or unidad_actual.esta_eliminada():
                self.dinero_defensor += RECOMPENSA_DEFENSOR_POR_UNIDAD
                eventos_dinero.append(
                    f"Defensor gana ${RECOMPENSA_DEFENSOR_POR_UNIDAD} por eliminar una unidad."
                )

        for identificador_torre, vida_anterior in vida_torres_antes.items():
            torre_actual = next(
                (torre for torre in self.torres if id(torre) == identificador_torre),
                None,
            )
            if torre_actual is None:
                self.dinero_atacante += RECOMPENSA_ATACANTE_POR_TORRE_DESTRUIDA
                eventos_dinero.append(
                    f"Atacante gana ${RECOMPENSA_ATACANTE_POR_TORRE_DESTRUIDA} por destruir una torre."
                )
            elif torre_actual.vida < vida_anterior:
                self.dinero_atacante += RECOMPENSA_ATACANTE_POR_TORRE_DANADA
                eventos_dinero.append(
                    f"Atacante gana ${RECOMPENSA_ATACANTE_POR_TORRE_DANADA} por dañar una torre."
                )

        for identificador_muro, vida_anterior in vida_muros_antes.items():
            muro_actual = next(
                (muro for muro in self.muros if id(muro) == identificador_muro),
                None,
            )
            if muro_actual is None:
                self.dinero_atacante += RECOMPENSA_ATACANTE_POR_MURO_DESTRUIDO
                eventos_dinero.append(
                    f"Atacante gana ${RECOMPENSA_ATACANTE_POR_MURO_DESTRUIDO} por destruir un muro."
                )
            elif muro_actual.vida < vida_anterior:
                self.dinero_atacante += RECOMPENSA_ATACANTE_POR_MURO_DANADO
                eventos_dinero.append(
                    f"Atacante gana ${RECOMPENSA_ATACANTE_POR_MURO_DANADO} por dañar un muro."
                )

        if self.base.vida < vida_base_antes:
            self.dinero_atacante += RECOMPENSA_ATACANTE_POR_BASE_DANADA
            eventos_dinero.append(
                f"Atacante gana ${RECOMPENSA_ATACANTE_POR_BASE_DANADA} por dañar la base."
            )

        return eventos_dinero

    def ejecutar_combate(self):
        """
        Descripcion:
            Ejecuta un turno de combate completo dentro de la ronda
            actual: activa habilidades, mueve unidades, resuelve
            ataques, otorga dinero por acciones y verifica si la
            ronda termino.

        Entradas:
            Ninguna.

        Salidas:
            dict: Estado resumido del turno de combate, incluyendo
            eventos ocurridos y si la ronda finalizo.

        Restricciones:
            - No debe llamarse si la partida ya finalizo.
        """
        if self.partida_finalizada:
            return {"eventos": [], "ronda_finalizada": True}

        if self.fase_ronda != FASE_COMBATE:
            fase_iniciada, mensaje_fase = self.iniciar_fase_combate()
            if not fase_iniciada:
                return {
                    "eventos": [mensaje_fase],
                    "ronda_finalizada": False,
                    "vida_base": self.base.vida,
                    "dinero_defensor": self.dinero_defensor,
                    "dinero_atacante": self.dinero_atacante,
                    "fase_ronda": self.fase_ronda,
                }

        vida_torres_antes = {id(torre): torre.vida for torre in self.torres}
        vida_unidades_antes = {id(unidad): unidad.vida for unidad in self.unidades}
        vida_muros_antes = {id(muro): muro.vida for muro in self.muros}
        vida_base_antes = self.base.vida

        eventos_turno = []
        if self.turnos_en_ronda_actual == 0:
            eventos_turno.append("La fase de combate está en curso.")
        resultado_combate = ejecutar_turno_de_combate(
            self.torres,
            self.unidades,
            self.base,
            FILA_BASE,
            eventos_turno,
            self.muros,
        )
        self.torres, self.unidades, self.muros = resultado_combate

        eventos_dinero = self._otorgar_dinero_por_combate(
            vida_torres_antes, vida_unidades_antes, vida_muros_antes,
            vida_base_antes
        )
        eventos_turno.extend(eventos_dinero)

        self.turnos_en_ronda_actual += 1
        self.historial_eventos.extend(eventos_turno)

        indice_eventos_fin = len(self.historial_eventos)
        ronda_finalizada = self._verificar_fin_de_ronda()
        eventos_turno.extend(self.historial_eventos[indice_eventos_fin:])

        return {
            "eventos": eventos_turno,
            "ronda_finalizada": ronda_finalizada,
            "vida_base": self.base.vida,
            "dinero_defensor": self.dinero_defensor,
            "dinero_atacante": self.dinero_atacante,
        }

    def segundos_restantes_preparacion(self):
        """
        Descripcion:
            Calcula cuantos segundos le quedan a la fase de
            preparacion actual (ataque del atacante o construccion
            del defensor). Sirve para que la interfaz y el servidor
            usen el mismo reloj en lugar de temporizadores locales
            independientes que se desincronizan entre dispositivos.

        Entradas:
            Ninguna.

        Salidas:
            int: Segundos restantes (nunca negativo). Devuelve 0 si
            la fase actual es combate, si la partida finalizo o si
            todavia no se registro un inicio de fase.
        """
        if self.partida_finalizada or self.fase_ronda == FASE_COMBATE:
            return 0

        if self.tiempo_inicio_fase is None:
            return SEGUNDOS_PREPARACION_ATACANTE

        if self.fase_ronda == FASE_ATAQUE_ATACANTE:
            limite = SEGUNDOS_PREPARACION_ATACANTE
        else:
            limite = SEGUNDOS_PREPARACION_DEFENSOR

        transcurrido = time.time() - self.tiempo_inicio_fase
        restante = limite - int(transcurrido)
        return max(0, restante)

    def tiempo_de_fase_agotado(self):
        """
        Descripcion:
            Indica si el tiempo de la fase de preparacion actual ya
            se agoto segun el reloj del servidor.

        Entradas:
            Ninguna.

        Salidas:
            bool: True si ya no quedan segundos en la fase actual de
            preparacion, False en caso contrario o si la fase actual
            es combate.
        """
        if self.fase_ronda == FASE_COMBATE or self.partida_finalizada:
            return False
        return self.segundos_restantes_preparacion() <= 0

    def resolver_preparacion_agotada(self):
        """
        Descripcion:
            Resuelve el final del tiempo de preparacion actual segun
            la fase en la que se encuentre la ronda:

            - Si el atacante agoto sus 15 segundos: queda bloqueado
              (ya no puede comprar mas unidades en esta fase) y se
              abren los 15 segundos de preparacion del defensor,
              tenga o no unidades colocadas todavia.
            - Si el defensor agoto sus 15 segundos: si el atacante no
              colocó ninguna unidad, el defensor gana la ronda de
              inmediato; si ya hay unidades, inicia el combate.

        Entradas:
            Ninguna.

        Salidas:
            tuple[bool, str]: Exito de la acción y mensaje descriptivo.
        """
        if self.partida_finalizada:
            return False, "La partida ya finalizó."

        if self.fase_ronda == FASE_COMBATE:
            return True, "El combate ya estaba en curso."

        if self.fase_ronda == FASE_ATAQUE_ATACANTE:
            self.historial_eventos.append(
                "Tiempo de preparación del atacante agotado. El atacante "
                "queda bloqueado y ahora el defensor coloca sus defensas."
            )
            return self.iniciar_fase_defensa()

        return self.iniciar_fase_combate()

    def _verificar_fin_de_ronda(self):
        """
        Descripcion:
            Verifica si la ronda actual debe terminar segun las
            condiciones de victoria del defensor o atacante, y en
            caso afirmativo actualiza el marcador de la partida.

        Entradas:
            Ninguna.

        Salidas:
            bool: True si la ronda finalizo, False si continua.

        Restricciones:
            Ninguna.
        """
        if self.base.fue_destruida():
            self.historial_eventos.append(
                "La base central fue destruida. El atacante gana la ronda."
            )
            self._finalizar_ronda("atacante")
            return True

        if self.base.vida > 0 and len(self.unidades) == 0 and self.turnos_en_ronda_actual > 0:
            if self.dinero_atacante <= 0:
                self.historial_eventos.append(
                    "El atacante se queda sin dinero y sin unidades. El defensor gana la ronda."
                )
                self._finalizar_ronda("defensor")
                return True

            self.turnos_sin_unidades_atacantes += 1
            turnos_restantes = max(
                0,
                TURNOS_ESPERA_ATACANTE_SIN_UNIDADES - self.turnos_sin_unidades_atacantes,
            )
            if self.turnos_sin_unidades_atacantes >= TURNOS_ESPERA_ATACANTE_SIN_UNIDADES:
                self.historial_eventos.append(
                    "El atacante no colocó nuevas tropas durante 7 segundos. El defensor gana la ronda."
                )
                self._finalizar_ronda("defensor")
                return True
            self.historial_eventos.append(
                f"Atacante sin tropas: tiene {turnos_restantes}s para colocar otra unidad."
            )
        else:
            self.turnos_sin_unidades_atacantes = 0

        if self.turnos_en_ronda_actual >= MAXIMO_TURNOS_POR_RONDA:
            self._finalizar_ronda("defensor")
            return True

        return False

    def _finalizar_ronda(self, rol_ganador_ronda):
        """
        Descripcion:
            Registra el resultado de la ronda actual, actualiza el
            marcador de rondas ganadas y verifica si alguno de los
            jugadores ya gano la partida completa.

        Entradas:
            rol_ganador_ronda (str): Rol que gano la ronda. Debe ser
                "defensor" o "atacante".

        Salidas:
            None: Modifica el marcador y, si corresponde, finaliza la
            partida completa.

        Restricciones:
            - rol_ganador_ronda debe ser "defensor" o "atacante".
        """
        if rol_ganador_ronda == "defensor":
            self.rol_ganador_ultima_ronda = "defensor"
            self.rondas_ganadas_defensor += 1
            self.historial_eventos.append(
                f"El defensor ({self.nombre_defensor}) gana la ronda {self.numero_ronda}."
            )
        else:
            self.rol_ganador_ultima_ronda = "atacante"
            self.rondas_ganadas_atacante += 1
            self.historial_eventos.append(
                f"El atacante ({self.nombre_atacante}) gana la ronda {self.numero_ronda}."
            )

        if self.rondas_ganadas_defensor >= RONDAS_PARA_GANAR_PARTIDA:
            self._finalizar_partida("defensor")
        elif self.rondas_ganadas_atacante >= RONDAS_PARA_GANAR_PARTIDA:
            self._finalizar_partida("atacante")
        else:
            self.iniciar_nueva_ronda()

    def _finalizar_partida(self, rol_ganador):
        """
        Descripcion:
            Marca la partida como finalizada, determina el nombre del
            jugador ganador y actualiza su registro de victorias en
            el archivo de jugadores.

        Entradas:
            rol_ganador (str): Rol con el que se gano la partida.
                Debe ser "defensor" o "atacante".

        Salidas:
            None: Modifica el estado de la partida y el archivo de
            jugadores.

        Restricciones:
            - rol_ganador debe ser "defensor" o "atacante".
        """
        self.partida_finalizada = True
        self.rol_ganador_partida = rol_ganador

        if rol_ganador == "defensor":
            self.ganador_partida = self.nombre_defensor
        else:
            self.ganador_partida = self.nombre_atacante

        self.historial_eventos.append(
            f"{self.ganador_partida} gana la partida completa como {rol_ganador}."
        )

        if self.guardar_victorias:
            actualizar_victoria(self.ganador_partida, rol_ganador)

    def _segundos_restantes_refuerzo(self):
        """
        Descripcion:
            Devuelve los segundos que le quedan al atacante para
            colocar otra unidad cuando se quedó sin tropas en combate.
        """
        if not self.esperando_refuerzo_atacante or self.tiempo_inicio_espera_refuerzo is None:
            return None

        transcurrido = time.time() - self.tiempo_inicio_espera_refuerzo
        restante = SEGUNDOS_ESPERA_REFUERZO_ATACANTE - int(transcurrido)
        return max(0, restante)


    def obtener_estado_partida(self):
        """
        Descripcion:
            Genera un resumen del estado actual de la partida, listo
            para ser usado por la interfaz grafica del Desarrollador
            1.

        Entradas:
            Ninguna.

        Salidas:
            dict: Diccionario con nombres de jugadores, dinero,
            numero de ronda, marcador, vida de la base, torres,
            muros, unidades y estado final de la partida.

        Restricciones:
            Ninguna.
        """
        return {
            "nombre_defensor": self.nombre_defensor,
            "nombre_atacante": self.nombre_atacante,
            "dinero_defensor": self.dinero_defensor,
            "dinero_atacante": self.dinero_atacante,
            "numero_ronda": self.numero_ronda,
            "fase_ronda": self.fase_ronda,
            "rondas_ganadas_defensor": self.rondas_ganadas_defensor,
            "rondas_ganadas_atacante": self.rondas_ganadas_atacante,
            "rondas_para_ganar_partida": RONDAS_PARA_GANAR_PARTIDA,
            "rol_ganador_ultima_ronda": self.rol_ganador_ultima_ronda,
            "segundos_restantes_preparacion": self.segundos_restantes_preparacion(),
            "esperando_refuerzo_atacante": self.esperando_refuerzo_atacante,
            "segundos_refuerzo_atacante": self._segundos_restantes_refuerzo(),
            "vida_base": self.base.vida,
            "vida_maxima_base": self.base.vida_maxima,
            "base_destruida": self.base.fue_destruida(),
            "torres": [
                {
                    "nombre": torre.nombre,
                    "clave": getattr(torre, "clave", ""),
                    "vida": torre.vida,
                    "vida_maxima": torre.vida_maxima,
                    "dano": torre.dano,
                    "alcance": torre.alcance,
                    "habilidad": torre.habilidad,
                    "fila": torre.fila,
                    "columna": torre.columna,
                }
                for torre in self.torres
            ],
            "muros": [
                {
                    "nombre": muro.nombre,
                    "vida": muro.vida,
                    "vida_maxima": muro.vida_maxima,
                    "fila": muro.fila,
                    "columna": muro.columna,
                }
                for muro in self.muros
            ],
            "unidades": [
                {
                    "nombre": unidad.nombre,
                    "clave": getattr(unidad, "clave", ""),
                    "vida": unidad.vida,
                    "vida_maxima": unidad.vida_maxima,
                    "dano": unidad.dano,
                    "velocidad": unidad.velocidad,
                    "habilidad": unidad.habilidad,
                    "fila": unidad.fila,
                    "columna": unidad.columna,
                }
                for unidad in self.unidades
            ],
            "turnos_sin_unidades_atacantes": self.turnos_sin_unidades_atacantes,
            "segundos_espera_sin_unidades": max(0, TURNOS_ESPERA_ATACANTE_SIN_UNIDADES - self.turnos_sin_unidades_atacantes),
            "partida_finalizada": self.partida_finalizada,
            "ganador_partida": self.ganador_partida,
            "rol_ganador_partida": self.rol_ganador_partida,
            "faccion_defensor": self.faccion_defensor,
            "faccion_atacante": self.faccion_atacante,
            "habilidad_defensor": self._info_habilidad_publica("defensor"),
            "habilidad_atacante": self._info_habilidad_publica("atacante"),
            "ultimos_eventos": self.historial_eventos[-10:],
        }

    def _info_habilidad_publica(self, rol):
        """
        Descripcion:
            Empaqueta la informacion de la habilidad especial de un
            rol para exponerla en el estado: nombre, descripcion,
            costo, daño, segundos de enfriamiento restantes y si esta
            disponible para usarse ahora mismo. Sirve para que la
            interfaz dibuje el boton de habilidad con su estado real
            sin duplicar las reglas de negocio.

        Entradas:
            rol (str): "defensor" o "atacante".

        Salidas:
            dict: Datos listos para mostrar en la interfaz.

        Restricciones:
            Ninguna.
        """
        faccion = self.faccion_defensor if rol == "defensor" else self.faccion_atacante
        habilidad = obtener_habilidad_de_faccion(faccion)
        dinero_disponible = self.dinero_defensor if rol == "defensor" else self.dinero_atacante
        segundos_cooldown = self._segundos_restantes_cooldown_habilidad(rol)

        bloqueada_por_fase = (
            (rol == "defensor" and self.fase_ronda == FASE_ATAQUE_ATACANTE)
            or (rol == "atacante" and self.fase_ronda == FASE_CONSTRUCCION_DEFENSOR)
        )

        return {
            "faccion": faccion,
            "nombre": habilidad["nombre"],
            "descripcion": habilidad["descripcion"],
            "costo": habilidad["costo"],
            "dano": habilidad["dano"],
            "color": habilidad["color"],
            "tipo_efecto": habilidad["tipo_efecto"],
            "cooldown_segundos": habilidad["cooldown_segundos"],
            "segundos_restantes_cooldown": segundos_cooldown,
            "disponible": (
                not self.partida_finalizada
                and not bloqueada_por_fase
                and segundos_cooldown == 0
                and dinero_disponible >= habilidad["costo"]
            ),
        }


def crear_partida(nombre_defensor, nombre_atacante, guardar_victorias=True):
    """
    Descripcion:
        Funcion de conveniencia para crear una nueva partida entre
        dos jugadores. Pensada para ser llamada desde la interfaz
        grafica del Desarrollador 1.

    Entradas:
        nombre_defensor (str): Nombre de usuario del jugador
            defensor.
        nombre_atacante (str): Nombre de usuario del jugador
            atacante.

    Salidas:
        Partida: Nueva instancia de Partida lista para jugarse.

    Restricciones:
        - nombre_defensor y nombre_atacante deben ser distintos.
    """
    return Partida(nombre_defensor, nombre_atacante, guardar_victorias)
