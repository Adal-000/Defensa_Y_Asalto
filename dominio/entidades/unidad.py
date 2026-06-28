"""
Descripcion:
    Modulo que define la clase Unidad, utilizada por el jugador
    atacante para asaltar la base central del defensor. Incluye tres
    tipos de unidad predefinidos, cada uno con su propia habilidad
    especial.
"""


class Unidad:
    """
    Descripcion:
        Representa una unidad atacante que avanza por el tablero
        para danar torres y, finalmente, la base central del
        defensor.

    Entradas:
        nombre (str): Nombre identificador del tipo de unidad.
        costo (int): Cantidad de dinero necesaria para comprarla.
        vida (int): Puntos de vida iniciales de la unidad.
        dano (int): Dano que infringe la unidad por ataque.
        velocidad (int): Cantidad de casillas que la unidad avanza
            por turno.
        habilidad (str): Nombre descriptivo de la habilidad especial.
        turnos_habilidad (int): Cantidad de turnos necesarios para
            volver a activar la habilidad especial.
        fila (int): Fila del tablero donde se coloca la unidad.
        columna (int): Columna del tablero donde se coloca la unidad.

    Salidas:
        No retorna nada. Construye una instancia de Unidad.

    Restricciones:
        - costo, vida, dano, velocidad y turnos_habilidad deben ser
          valores numericos positivos.
        - fila y columna deben corresponder a una posicion valida
          dentro del tablero definido por la interfaz grafica.
    """

    def __init__(self, nombre, costo, vida, dano, velocidad, habilidad,
                 turnos_habilidad, fila=0, columna=0):
        self.nombre = nombre
        self.costo = costo
        self.vida = vida
        self.vida_maxima = vida
        self.dano = dano
        self.velocidad = velocidad
        self.habilidad = habilidad
        self.turnos_habilidad = turnos_habilidad
        self.turnos_restantes_habilidad = 0
        self.fila = fila
        self.columna = columna
        self.escudo_activo = False
        self.turnos_escudo = 0
        self.velocidad_extra_temporal = 0
        self.turnos_velocidad_extra = 0
        self.congelada = False
        self.turnos_congelada = 0

    def esta_eliminada(self):
        """
        Descripcion:
            Indica si la unidad ha sido eliminada por falta de vida.

        Entradas:
            Ninguna.

        Salidas:
            bool: True si la vida de la unidad es menor o igual a
            cero, False en caso contrario.

        Restricciones:
            Ninguna.
        """
        return self.vida <= 0

    def recibir_dano(self, cantidad_dano):
        """
        Descripcion:
            Reduce la vida de la unidad segun el dano recibido. Si la
            unidad tiene un escudo activo, el dano se reduce a la
            mitad mientras el escudo dure.

        Entradas:
            cantidad_dano (int): Cantidad de dano a aplicar.

        Salidas:
            None: Modifica el atributo vida de la unidad.

        Restricciones:
            - cantidad_dano debe ser un valor mayor o igual a cero.
        """
        dano_real = cantidad_dano
        if self.escudo_activo:
            dano_real = cantidad_dano // 2

        self.vida = max(0, self.vida - dano_real)

    def calcular_velocidad_actual(self):
        """
        Descripcion:
            Calcula la velocidad real de la unidad considerando
            bonos temporales y el efecto de congelamiento.

        Entradas:
            Ninguna.

        Salidas:
            int: Velocidad efectiva de la unidad en el turno actual.

        Restricciones:
            Ninguna.
        """
        if self.congelada:
            return 0
        return self.velocidad + self.velocidad_extra_temporal

    def puede_usar_habilidad(self):
        """
        Descripcion:
            Indica si la habilidad especial de la unidad ya esta
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
            Actualiza el estado de la unidad al pasar un turno:
            reduce el contador de espera de la habilidad especial y
            elimina los efectos temporales que ya hayan expirado,
            incluyendo el congelamiento.

        Entradas:
            Ninguna.

        Salidas:
            None: Modifica los contadores internos de la unidad.

        Restricciones:
            Ninguna.
        """
        if self.turnos_restantes_habilidad > 0:
            self.turnos_restantes_habilidad -= 1

        if self.turnos_escudo > 0:
            self.turnos_escudo -= 1
            if self.turnos_escudo == 0:
                self.escudo_activo = False

        if self.turnos_velocidad_extra > 0:
            self.turnos_velocidad_extra -= 1
            if self.turnos_velocidad_extra == 0:
                self.velocidad_extra_temporal = 0

        if self.turnos_congelada > 0:
            self.turnos_congelada -= 1
            if self.turnos_congelada == 0:
                self.congelada = False

    def calcular_dano_contra(self, tipo_objetivo):
        """
        Descripcion:
            Calcula el dano que la unidad inflige contra un tipo de
            objetivo especifico, aplicando un bono adicional si la
            unidad tiene la habilidad de dano extra contra torres y
            el objetivo es una torre.

        Entradas:
            tipo_objetivo (str): Tipo de objetivo atacado. Debe ser
                "torre" o "base".

        Salidas:
            int: Dano total a aplicar contra el objetivo.

        Restricciones:
            - tipo_objetivo debe ser "torre" o "base".
        """
        dano_total = self.dano

        if tipo_objetivo == "torre" and self.habilidad == "dano_extra_torres":
            dano_total = int(self.dano * 1.5)

        return dano_total

    def activar_habilidad(self):
        """
        Descripcion:
            Activa la habilidad especial correspondiente al tipo de
            unidad. El comportamiento depende del nombre de la
            habilidad asignada a la unidad.

        Entradas:
            Ninguna.

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

        if self.habilidad == "ataque_doble":
            mensaje = f"{self.nombre} realiza un ataque doble."

        elif self.habilidad == "escudo_temporal":
            self.escudo_activo = True
            self.turnos_escudo = 2
            mensaje = f"{self.nombre} activa un escudo temporal."

        elif self.habilidad == "curacion":
            self.vida = min(self.vida_maxima, self.vida + 15)
            mensaje = f"{self.nombre} se cura un poco."

        elif self.habilidad == "aumento_velocidad":
            self.velocidad_extra_temporal = 1
            self.turnos_velocidad_extra = 2
            mensaje = f"{self.nombre} aumenta su velocidad temporalmente."

        elif self.habilidad == "dano_extra_torres":
            mensaje = f"{self.nombre} se prepara para danar torres con mas fuerza."

        else:
            mensaje = f"{self.nombre} no tiene una habilidad reconocida."

        self.reiniciar_contador_habilidad()
        return mensaje


def crear_unidad_soldado(fila=0, columna=0):
    """
    Descripcion:
        Crea el "Soldado base": la unidad equilibrada del atacante.
        Sirve para presionar carriles sin ser ni muy barata ni muy
        poderosa. Corresponde a las imagenes de la carpeta
        "Soldado base" de cada faccion.
    """
    return Unidad(
        nombre="Soldado base",
        costo=90,
        vida=220,
        dano=28,
        velocidad=1,
        habilidad="ataque_doble",
        turnos_habilidad=4,
        fila=fila,
        columna=columna,
    )


def crear_unidad_rapida(fila=0, columna=0):
    """
    Descripcion:
        Crea el "Soldado rapido". Tiene menos vida y pega menos
        fuerte, pero avanza mas rapido y obliga al defensor a cubrir
        carriles abiertos. Corresponde a las imagenes de la carpeta
        "Soldado rápido" de cada faccion.
    """
    return Unidad(
        nombre="Soldado rápido",
        costo=70,
        vida=150,
        dano=20,
        velocidad=2,
        habilidad="aumento_velocidad",
        turnos_habilidad=4,
        fila=fila,
        columna=columna,
    )


def crear_unidad_tanque(fila=0, columna=0):
    """
    Descripcion:
        Crea el "Soldado tanque". Es el mas caro y el mas lento, pero
        resiste mas dano y pega mas fuerte, ademas de hacer dano extra
        contra torres. Corresponde a las imagenes de la carpeta
        "Soldado tanque" de cada faccion.
    """
    return Unidad(
        nombre="Soldado tanque",
        costo=130,
        vida=320,
        dano=38,
        velocidad=1,
        habilidad="dano_extra_torres",
        turnos_habilidad=4,
        fila=fila,
        columna=columna,
    )


FABRICANTES_UNIDADES = {
    "soldado": crear_unidad_soldado,
    "rapido": crear_unidad_rapida,
    "tanque": crear_unidad_tanque,
    # Alias para no romper pruebas o botones viejos si existieran.
    "explorador": crear_unidad_rapida,
    "escudero": crear_unidad_tanque,
    "demoledor": crear_unidad_tanque,
}


CLAVES_CATALOGO_UNIDADES = ("soldado", "rapido", "tanque")


def crear_unidad_por_tipo(tipo_unidad, fila=0, columna=0):
    """
    Descripcion:
        Funcion de fabrica que crea una unidad segun el tipo solicitado.
        El catalogo oficial usa soldado, rapido y tanque porque son las
        tres familias que existen en las imagenes del proyecto.
    """
    fabricante = FABRICANTES_UNIDADES.get(tipo_unidad)
    if fabricante is None:
        return None
    return fabricante(fila, columna)
