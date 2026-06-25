"""
Descripcion:
    Modulo que define la clase Partida, encargada de coordinar todo
    el flujo del juego "Defensa y Asalto de Base": el sistema de
    dinero, las rondas, las compras de torres y unidades, la fase de
    combate y las condiciones de victoria.
"""

from base import Base
from torre import crear_torre_por_tipo
from unidad import crear_unidad_por_tipo
from combate import ejecutar_turno_de_combate
from archivos import actualizar_victoria

DINERO_INICIAL_DEFENSOR = 300
DINERO_INICIAL_ATACANTE = 250
DINERO_EXTRA_POR_RONDA = 100
RONDAS_PARA_GANAR_PARTIDA = 3
FILA_BASE = 0
MAXIMO_TURNOS_POR_RONDA = 30


class Partida:
    """
    Descripcion:
        Representa una partida completa entre un jugador defensor y
        un jugador atacante. Administra el dinero de cada jugador,
        las torres y unidades en juego, la base central, el numero
        de rondas ganadas por cada jugador y el historial de eventos
        de la partida.

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

    def __init__(self, nombre_defensor, nombre_atacante):
        self.nombre_defensor = nombre_defensor
        self.nombre_atacante = nombre_atacante

        self.dinero_defensor = 0
        self.dinero_atacante = 0

        self.torres = []
        self.unidades = []
        self.base = Base()

        self.rondas_ganadas_defensor = 0
        self.rondas_ganadas_atacante = 0
        self.numero_ronda = 0
        self.turnos_en_ronda_actual = 0

        self.partida_finalizada = False
        self.ganador_partida = None
        self.rol_ganador_partida = None

        self.historial_eventos = []

        self.iniciar_nueva_ronda()

    def iniciar_nueva_ronda(self):
        """
        Descripcion:
            Prepara una nueva ronda: reinicia la base, limpia las
            torres y unidades de la ronda anterior, y entrega el
            dinero inicial correspondiente a ambos jugadores.

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
        self.torres = []
        self.unidades = []
        self.base.reiniciar()

        self.dinero_defensor = DINERO_INICIAL_DEFENSOR + (
            DINERO_EXTRA_POR_RONDA * (self.numero_ronda - 1)
        )
        self.dinero_atacante = DINERO_INICIAL_ATACANTE + (
            DINERO_EXTRA_POR_RONDA * (self.numero_ronda - 1)
        )

        self.historial_eventos.append(
            f"Inicia la ronda {self.numero_ronda}."
        )

    def comprar_torre(self, tipo_torre, fila, columna):
        """
        Descripcion:
            Permite al defensor comprar y colocar una torre en el
            tablero, siempre que tenga suficiente dinero disponible.

        Entradas:
            tipo_torre (str): Tipo de torre a comprar (por ejemplo,
                "arquera", "cañon", "hielo" o "soporte").
            fila (int): Fila del tablero donde se colocara la torre.
            columna (int): Columna del tablero donde se colocara la
                torre.

        Salidas:
            tuple[bool, str]: El primer valor indica si la compra
            fue exitosa. El segundo valor es un mensaje descriptivo
            del resultado.

        Restricciones:
            - tipo_torre debe ser un tipo de torre valido.
            - El defensor debe tener dinero suficiente para comprar
              la torre.
        """
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

    def comprar_unidad(self, tipo_unidad, fila, columna):
        """
        Descripcion:
            Permite al atacante comprar y colocar una unidad en el
            tablero, siempre que tenga suficiente dinero disponible.

        Entradas:
            tipo_unidad (str): Tipo de unidad a comprar (por
                ejemplo, "soldado", "escudero", "explorador" o
                "demoledor").
            fila (int): Fila del tablero donde se colocara la
                unidad.
            columna (int): Columna del tablero donde se colocara la
                unidad.

        Salidas:
            tuple[bool, str]: El primer valor indica si la compra
            fue exitosa. El segundo valor es un mensaje descriptivo
            del resultado.

        Restricciones:
            - tipo_unidad debe ser un tipo de unidad valido.
            - El atacante debe tener dinero suficiente para comprar
              la unidad.
        """
        nueva_unidad = crear_unidad_por_tipo(tipo_unidad, fila, columna)

        if nueva_unidad is None:
            return False, "Tipo de unidad invalido."

        if self.dinero_atacante < nueva_unidad.costo:
            return False, "El atacante no tiene suficiente dinero."

        self.dinero_atacante -= nueva_unidad.costo
        self.unidades.append(nueva_unidad)
        self.historial_eventos.append(
            f"El atacante compra {nueva_unidad.nombre} en ({fila}, {columna})."
        )

        return True, f"{nueva_unidad.nombre} comprada correctamente."

    def _otorgar_dinero_por_combate(self, vida_torres_antes, vida_unidades_antes):
        """
        Descripcion:
            Otorga dinero a los jugadores segun lo ocurrido durante
            el ultimo turno de combate: el defensor gana dinero por
            cada unidad eliminada y el atacante gana dinero por cada
            torre danada, destruida o por dano causado a la base.

        Entradas:
            vida_torres_antes (dict): Diccionario que asocia el id
                de cada torre con su vida antes del turno de
                combate.
            vida_unidades_antes (dict): Diccionario que asocia el id
                de cada unidad con su vida antes del turno de
                combate.

        Salidas:
            None: Modifica los atributos dinero_defensor y
            dinero_atacante.

        Restricciones:
            Ninguna.
        """
        for identificador_unidad, vida_anterior in vida_unidades_antes.items():
            unidad_actual = next(
                (unidad for unidad in self.unidades if id(unidad) == identificador_unidad),
                None,
            )
            if unidad_actual is None or unidad_actual.esta_eliminada():
                self.dinero_defensor += 20

        for identificador_torre, vida_anterior in vida_torres_antes.items():
            torre_actual = next(
                (torre for torre in self.torres if id(torre) == identificador_torre),
                None,
            )
            if torre_actual is None:
                self.dinero_atacante += 30
            elif torre_actual.vida < vida_anterior:
                self.dinero_atacante += 10

    def ejecutar_combate(self):
        """
        Descripcion:
            Ejecuta un turno de combate completo dentro de la ronda
            actual: mueve unidades, resuelve ataques, otorga dinero
            por las acciones realizadas y verifica si la ronda ha
            terminado.

        Entradas:
            Ninguna.

        Salidas:
            dict: Estado resumido del turno de combate, incluyendo
            los eventos ocurridos y si la ronda ha finalizado.

        Restricciones:
            - No debe llamarse si la partida ya finalizo.
        """
        if self.partida_finalizada:
            return {"eventos": [], "ronda_finalizada": True}

        vida_torres_antes = {id(torre): torre.vida for torre in self.torres}
        vida_unidades_antes = {id(unidad): unidad.vida for unidad in self.unidades}

        eventos_turno = []
        self.torres, self.unidades = ejecutar_turno_de_combate(
            self.torres, self.unidades, self.base, FILA_BASE, eventos_turno
        )

        self._otorgar_dinero_por_combate(vida_torres_antes, vida_unidades_antes)

        self.turnos_en_ronda_actual += 1
        self.historial_eventos.extend(eventos_turno)

        ronda_finalizada = self._verificar_fin_de_ronda()

        return {
            "eventos": eventos_turno,
            "ronda_finalizada": ronda_finalizada,
            "vida_base": self.base.vida,
            "dinero_defensor": self.dinero_defensor,
            "dinero_atacante": self.dinero_atacante,
        }

    def _verificar_fin_de_ronda(self):
        """
        Descripcion:
            Verifica si la ronda actual debe terminar segun las
            condiciones de victoria del defensor o del atacante, y
            en caso afirmativo actualiza el marcador de la partida.

        Entradas:
            Ninguna.

        Salidas:
            bool: True si la ronda finalizo, False si debe
            continuar.

        Restricciones:
            Ninguna.
        """
        if self.base.fue_destruida():
            self._finalizar_ronda("atacante")
            return True

        atacante_sin_dinero_ni_unidades = (
            self.dinero_atacante <= 0 and len(self.unidades) == 0
        )
        todas_unidades_eliminadas = len(self.unidades) == 0 and self.turnos_en_ronda_actual > 0

        if atacante_sin_dinero_ni_unidades or todas_unidades_eliminadas:
            self._finalizar_ronda("defensor")
            return True

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
            None: Modifica el marcador de la partida y, si
            corresponde, finaliza la partida completa.

        Restricciones:
            - rol_ganador_ronda debe ser "defensor" o "atacante".
        """
        if rol_ganador_ronda == "defensor":
            self.rondas_ganadas_defensor += 1
            self.historial_eventos.append(
                f"El defensor ({self.nombre_defensor}) gana la ronda {self.numero_ronda}."
            )
        else:
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
            Marca la partida como finalizada, determina el nombre
            del jugador ganador y actualiza su registro de victorias
            en el archivo de jugadores.

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

        actualizar_victoria(self.ganador_partida, rol_ganador)

    def obtener_estado_partida(self):
        """
        Descripcion:
            Genera un resumen del estado actual de la partida, listo
            para ser usado por la interfaz grafica del Desarrollador
            1.

        Entradas:
            Ninguna.

        Salidas:
            dict: Diccionario con la informacion relevante de la
            partida: nombres de jugadores, dinero, numero de ronda,
            marcador, vida de la base, torres, unidades y si la
            partida ha finalizado.

        Restricciones:
            Ninguna.
        """
        return {
            "nombre_defensor": self.nombre_defensor,
            "nombre_atacante": self.nombre_atacante,
            "dinero_defensor": self.dinero_defensor,
            "dinero_atacante": self.dinero_atacante,
            "numero_ronda": self.numero_ronda,
            "rondas_ganadas_defensor": self.rondas_ganadas_defensor,
            "rondas_ganadas_atacante": self.rondas_ganadas_atacante,
            "vida_base": self.base.vida,
            "vida_maxima_base": self.base.vida_maxima,
            "base_destruida": self.base.fue_destruida(),
            "torres": [
                {
                    "nombre": torre.nombre,
                    "vida": torre.vida,
                    "fila": torre.fila,
                    "columna": torre.columna,
                }
                for torre in self.torres
            ],
            "unidades": [
                {
                    "nombre": unidad.nombre,
                    "vida": unidad.vida,
                    "fila": unidad.fila,
                    "columna": unidad.columna,
                }
                for unidad in self.unidades
            ],
            "partida_finalizada": self.partida_finalizada,
            "ganador_partida": self.ganador_partida,
            "rol_ganador_partida": self.rol_ganador_partida,
            "ultimos_eventos": self.historial_eventos[-10:],
        }


def crear_partida(nombre_defensor, nombre_atacante):
    """
    Descripcion:
        Funcion de conveniencia para crear una nueva partida entre
        dos jugadores. Pensada para ser llamada directamente desde
        la interfaz grafica del Desarrollador 1.

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
    return Partida(nombre_defensor, nombre_atacante)
