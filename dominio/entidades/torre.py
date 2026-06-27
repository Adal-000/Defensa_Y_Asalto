"""
Descripcion:
    Modulo que define la clase Torre, utilizada por el jugador
    defensor para proteger la base central. Incluye tres tipos de
    torre predefinidos, cada uno con su propia habilidad especial.
"""


class Torre:
    """
    Descripcion:
        Representa una torre defensiva colocada en el tablero de
        juego. Cada torre tiene estadisticas de combate y una
        habilidad especial que se activa cada cierta cantidad de
        turnos.

    Entradas:
        nombre (str): Nombre identificador del tipo de torre.
        costo (int): Cantidad de dinero necesaria para comprarla.
        vida (int): Puntos de vida iniciales de la torre.
        dano (int): Dano que infringe la torre por ataque.
        alcance (int): Distancia (en casillas) hasta la cual la
            torre puede atacar a una unidad.
        habilidad (str): Nombre descriptivo de la habilidad especial.
        turnos_habilidad (int): Cantidad de turnos necesarios para
            volver a activar la habilidad especial.
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        No retorna nada. Construye una instancia de Torre.

    Restricciones:
        - costo, vida, dano, alcance y turnos_habilidad deben ser
          valores numericos positivos.
        - fila y columna deben corresponder a una posicion valida
          dentro del tablero definido por la interfaz grafica.
    """

    def __init__(self, nombre, costo, vida, dano, alcance, habilidad,
                 turnos_habilidad, fila=0, columna=0):
        self.nombre = nombre
        self.costo = costo
        self.vida = vida
        self.vida_maxima = vida
        self.dano = dano
        self.alcance = alcance
        self.habilidad = habilidad
        self.turnos_habilidad = turnos_habilidad
        self.turnos_restantes_habilidad = 0
        self.fila = fila
        self.columna = columna
        self.dano_extra_temporal = 0
        self.turnos_dano_extra = 0
        self.congelada = False

    def esta_destruida(self):
        """
        Descripcion:
            Indica si la torre ha sido destruida por falta de vida.

        Entradas:
            Ninguna.

        Salidas:
            bool: True si la vida de la torre es menor o igual a
            cero, False en caso contrario.

        Restricciones:
            Ninguna.
        """
        return self.vida <= 0

    def recibir_dano(self, cantidad_dano):
        """
        Descripcion:
            Reduce la vida de la torre segun la cantidad de dano
            recibido. La vida nunca desciende por debajo de cero.

        Entradas:
            cantidad_dano (int): Cantidad de dano a aplicar.

        Salidas:
            None: Modifica el atributo vida de la torre.

        Restricciones:
            - cantidad_dano debe ser un valor mayor o igual a cero.
        """
        self.vida = max(0, self.vida - cantidad_dano)

    def calcular_dano_ataque(self):
        """
        Descripcion:
            Calcula el dano total que la torre puede infringir en su
            siguiente ataque, sumando el dano base con el bono
            temporal otorgado por alguna habilidad especial.

        Entradas:
            Ninguna.

        Salidas:
            int: Dano total del ataque.

        Restricciones:
            Ninguna.
        """
        return self.dano + self.dano_extra_temporal

    def puede_usar_habilidad(self):
        """
        Descripcion:
            Indica si la habilidad especial de la torre ya esta
            disponible para ser usada nuevamente.

        Entradas:
            Ninguna.

        Salidas:
            bool: True si la habilidad esta lista para usarse, False
            si todavia debe esperar turnos.

        Restricciones:
            Ninguna.
        """
        return self.turnos_restantes_habilidad <= 0

    def reiniciar_contador_habilidad(self):
        """
        Descripcion:
            Reinicia el contador de turnos de la habilidad especial
            despues de haber sido utilizada.

        Entradas:
            Ninguna.

        Salidas:
            None: Modifica el atributo turnos_restantes_habilidad.

        Restricciones:
            Ninguna.
        """
        self.turnos_restantes_habilidad = self.turnos_habilidad

    def avanzar_turno(self):
        """
        Descripcion:
            Actualiza el estado de la torre al pasar un turno: reduce
            el contador de espera de la habilidad especial y elimina
            los efectos temporales (como el bono de dano) que ya
            hayan expirado.

        Entradas:
            Ninguna.

        Salidas:
            None: Modifica los contadores internos de la torre.

        Restricciones:
            Ninguna.
        """
        if self.turnos_restantes_habilidad > 0:
            self.turnos_restantes_habilidad -= 1

        if self.turnos_dano_extra > 0:
            self.turnos_dano_extra -= 1
            if self.turnos_dano_extra == 0:
                self.dano_extra_temporal = 0

    def activar_habilidad(self, objetivo=None, lista_torres=None):
        """
        Descripcion:
            Activa la habilidad especial correspondiente al tipo de
            torre. El comportamiento depende del nombre de la
            habilidad asignada a la torre.

        Entradas:
            objetivo (Unidad): Unidad sobre la cual puede aplicarse
                la habilidad (por ejemplo, para congelarla). Puede
                ser None si la habilidad no requiere objetivo.
            lista_torres (list[Torre]): Lista de torres del tablero,
                usada por habilidades que afectan a torres cercanas
                (por ejemplo, reparar). Puede ser None si la
                habilidad no la necesita.

        Salidas:
            str: Mensaje descriptivo de lo ocurrido al activar la
            habilidad.

        Restricciones:
            - La habilidad solo se activa si puede_usar_habilidad()
              devuelve True.
        """
        if not self.puede_usar_habilidad():
            return f"{self.nombre} aun no puede volver a usar su habilidad."

        mensaje = ""

        if self.habilidad == "disparo_doble":
            mensaje = f"{self.nombre} realiza un disparo doble."
            if objetivo is not None:
                objetivo.recibir_dano(self.calcular_dano_ataque())

        elif self.habilidad == "dano_area":
            mensaje = f"{self.nombre} ataca a todas las unidades cercanas."

        elif self.habilidad == "congelar_unidad":
            mensaje = f"{self.nombre} congela a una unidad enemiga."
            if objetivo is not None:
                objetivo.congelada = True
                objetivo.turnos_congelada = 2

        elif self.habilidad == "reparar_torre_cercana":
            mensaje = f"{self.nombre} repara a una torre cercana."
            if lista_torres:
                for torre_cercana in lista_torres:
                    if torre_cercana is not self and not torre_cercana.esta_destruida():
                        torre_cercana.vida = min(
                            torre_cercana.vida_maxima,
                            torre_cercana.vida + 20,
                        )
                        break

        elif self.habilidad == "aumentar_dano_temporal":
            self.dano_extra_temporal = self.dano // 2
            self.turnos_dano_extra = 2
            mensaje = f"{self.nombre} aumenta su dano temporalmente."

        else:
            mensaje = f"{self.nombre} no tiene una habilidad reconocida."

        self.reiniciar_contador_habilidad()
        return mensaje


def crear_torre_arquera(fila=0, columna=0):
    """
    Descripcion:
        Crea una torre de tipo "Torre Arquera", especializada en
        ataques rapidos y dobles.

    Entradas:
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        Torre: Instancia de Torre configurada como Torre Arquera.

    Restricciones:
        Ninguna.
    """
    return Torre(
        nombre="Torre Arquera",
        costo=100,
        vida=130,
        dano=22,
        alcance=4,
        habilidad="disparo_doble",
        turnos_habilidad=2,
        fila=fila,
        columna=columna,
    )


def crear_torre_cañon(fila=0, columna=0):
    """
    Descripcion:
        Crea una torre de tipo "Torre Cañon", especializada en
        infringir dano a varias unidades a la vez.

    Entradas:
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        Torre: Instancia de Torre configurada como Torre Cañon.

    Restricciones:
        Ninguna.
    """
    return Torre(
        nombre="Torre Cañon",
        costo=150,
        vida=180,
        dano=34,
        alcance=3,
        habilidad="dano_area",
        turnos_habilidad=3,
        fila=fila,
        columna=columna,
    )


def crear_torre_hielo(fila=0, columna=0):
    """
    Descripcion:
        Crea una torre de tipo "Torre de Hielo", especializada en
        congelar unidades enemigas para retrasar su avance.

    Entradas:
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        Torre: Instancia de Torre configurada como Torre de Hielo.

    Restricciones:
        Ninguna.
    """
    return Torre(
        nombre="Torre de Hielo",
        costo=120,
        vida=140,
        dano=16,
        alcance=4,
        habilidad="congelar_unidad",
        turnos_habilidad=3,
        fila=fila,
        columna=columna,
    )


def crear_torre_soporte(fila=0, columna=0):
    """
    Descripcion:
        Crea una torre de tipo "Torre de Soporte", especializada en
        reparar torres cercanas y aumentar el dano propio de forma
        temporal.

    Entradas:
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        Torre: Instancia de Torre configurada como Torre de Soporte.

    Restricciones:
        Ninguna.
    """
    return Torre(
        nombre="Torre de Soporte",
        costo=130,
        vida=155,
        dano=14,
        alcance=3,
        habilidad="reparar_torre_cercana",
        turnos_habilidad=3,
        fila=fila,
        columna=columna,
    )


FABRICANTES_TORRES = {
    "arquera": crear_torre_arquera,
    "cañon": crear_torre_cañon,
    "hielo": crear_torre_hielo,
    "soporte": crear_torre_soporte,
}


def crear_torre_por_tipo(tipo_torre, fila=0, columna=0):
    """
    Descripcion:
        Funcion de fabrica que crea una torre segun el tipo solicitado
        por nombre clave (por ejemplo, "arquera", "cañon", "hielo" o
        "soporte").

    Entradas:
        tipo_torre (str): Clave del tipo de torre a crear.
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        Torre: Nueva instancia de Torre del tipo solicitado.
        None: Si el tipo de torre no existe.

    Restricciones:
        - tipo_torre debe ser una de las claves definidas en
          FABRICANTES_TORRES.
    """
    fabricante = FABRICANTES_TORRES.get(tipo_torre)
    if fabricante is None:
        return None
    return fabricante(fila, columna)
