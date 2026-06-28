"""
Descripcion:
    Modulo que define la clase Muro. Los muros son estructuras
    defensivas simples que el defensor puede comprar para bloquear
    o retrasar el avance de las unidades atacantes. No atacan, pero
    reciben dano y pueden ser destruidos.
"""


class Muro:
    """
    Descripcion:
        Representa un muro defensivo colocado en el tablero. Su
        objetivo es absorber dano y retrasar a las unidades
        atacantes antes de que alcancen la base central.

    Entradas:
        costo (int): Cantidad de dinero necesaria para comprar el
            muro.
        vida (int): Puntos de vida iniciales del muro.
        fila (int): Fila del tablero donde se coloca el muro.
        columna (int): Columna del tablero donde se coloca el muro.

    Salidas:
        No retorna nada. Construye una instancia de Muro.

    Restricciones:
        - costo y vida deben ser enteros positivos.
        - fila y columna deben corresponder a una posicion valida
          dentro del tablero de la partida.
    """

    def __init__(self, costo=60, vida=220, fila=0, columna=0):
        self.nombre = "Muro"
        self.costo = costo
        self.vida = vida
        self.vida_maxima = vida
        self.fila = fila
        self.columna = columna

    def recibir_dano(self, cantidad_dano):
        """
        Descripcion:
            Reduce la vida del muro segun el dano recibido. La vida
            nunca baja de cero.

        Entradas:
            cantidad_dano (int): Cantidad de dano que recibe el muro.

        Salidas:
            None: Modifica directamente el atributo vida del muro.

        Restricciones:
            - cantidad_dano debe ser mayor o igual a cero.
        """
        self.vida = max(0, self.vida - cantidad_dano)

    def esta_destruido(self):
        """
        Descripcion:
            Indica si el muro fue destruido por falta de vida.

        Entradas:
            Ninguna.

        Salidas:
            bool: True si la vida del muro es menor o igual a cero,
            False en caso contrario.

        Restricciones:
            Ninguna.
        """
        return self.vida <= 0


def crear_muro(fila=0, columna=0):
    """
    Descripcion:
        Crea un muro defensivo con valores predeterminados para ser
        comprado por el defensor.

    Entradas:
        fila (int): Fila donde se colocara el muro.
        columna (int): Columna donde se colocara el muro.

    Salidas:
        Muro: Nueva instancia de Muro.

    Restricciones:
        - fila y columna deben validarse desde la clase Partida antes
          de confirmar la compra.
    """
    return Muro(fila=fila, columna=columna)
