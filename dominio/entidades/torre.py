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
        """
        Descripcion:
            Inicializa la instancia y asigna los valores necesarios para
            que el objeto pueda utilizarse correctamente.
        
        Entradas:
            nombre (object): Valor recibido por la funcion.
            costo (object): Valor recibido por la funcion.
            vida (object): Valor recibido por la funcion.
            dano (object): Valor recibido por la funcion.
            alcance (object): Valor recibido por la funcion.
            habilidad (object): Valor recibido por la funcion.
            turnos_habilidad (object): Valor recibido por la funcion.
            fila (object): Valor recibido por la funcion. Valor
            opcional.
            columna (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            None: Inicializa los atributos de la instancia.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Debe ejecutarse sobre objetos del dominio creados
            correctamente.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
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


def crear_torre_normal(fila=0, columna=0):
    """
    Descripcion:
        Crea la "Torre normal": la defensa basica y equilibrada.
        Tiene alcance largo y dispara dos veces seguidas cuando su
        habilidad esta lista, pero no es la mas resistente ni la que
        mas dano hace por golpe. Corresponde a las imagenes
        "torre_xxx_normal1/2.png" de cada faccion.

    Entradas:
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        Torre: Instancia de Torre configurada como Torre normal.

    Restricciones:
        Ninguna.
    """
    return Torre(
        nombre="Torre normal",
        costo=90,
        vida=220,
        dano=28,
        alcance=4,
        habilidad="disparo_doble",
        turnos_habilidad=4,
        fila=fila,
        columna=columna,
    )


def crear_torre_pesada(fila=0, columna=0):
    """
    Descripcion:
        Crea la "Torre pesada": la defensa mas cara y mas resistente.
        Pega mas fuerte que el resto y ataca a varias unidades a la
        vez gracias a su habilidad de dano en area, a cambio de tener
        menos alcance. Corresponde a las imagenes
        "torre_xxx_pesada1/2.png" de cada faccion.

    Entradas:
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        Torre: Instancia de Torre configurada como Torre pesada.

    Restricciones:
        Ninguna.
    """
    return Torre(
        nombre="Torre pesada",
        costo=130,
        vida=320,
        dano=38,
        alcance=3,
        habilidad="dano_area",
        turnos_habilidad=4,
        fila=fila,
        columna=columna,
    )


def crear_torre_especial(fila=0, columna=0):
    """
    Descripcion:
        Crea la "Torre especial": la defensa de soporte/control. Su
        dano por golpe es el mas bajo de las tres, pero compensa
        congelando unidades enemigas para frenar el avance del
        atacante. Corresponde a las imagenes
        "torre_xxx_especial1/2.png" de cada faccion.

    Entradas:
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        Torre: Instancia de Torre configurada como Torre especial.

    Restricciones:
        Ninguna.
    """
    return Torre(
        nombre="Torre especial",
        costo=110,
        vida=260,
        dano=24,
        alcance=4,
        habilidad="congelar_unidad",
        turnos_habilidad=4,
        fila=fila,
        columna=columna,
    )


FABRICANTES_TORRES = {
    "normal": crear_torre_normal,
    "pesada": crear_torre_pesada,
    "especial": crear_torre_especial,
    # Alias en espanol para no romper interfaces, comandos de consola
    # o pruebas antiguas que todavia usen los nombres originales.
    "arquera": crear_torre_normal,
    "cañon": crear_torre_pesada,
    "canon": crear_torre_pesada,
    "hielo": crear_torre_especial,
    "soporte": crear_torre_especial,
}


CLAVES_CATALOGO_TORRES = ("normal", "pesada", "especial")


def crear_torre_por_tipo(tipo_torre, fila=0, columna=0):
    """
    Descripcion:
        Funcion de fabrica que crea una torre segun el tipo solicitado
        por nombre clave. El catalogo oficial usa "normal", "pesada" y
        "especial" porque son las tres familias que existen en las
        imagenes de Imagenes/estructuras/<faccion>/.

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
    fabricante = FABRICANTES_TORRES.get(str(tipo_torre).strip().lower())
    if fabricante is None:
        return None
    return fabricante(fila, columna)
