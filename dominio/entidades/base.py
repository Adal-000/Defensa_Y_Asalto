"""
Descripcion:
    Modulo que define la clase Base, encargada de representar la
    base central del jugador defensor. El objetivo principal del
    atacante es destruir esta base antes de que se le acabe el
    dinero o sus unidades sean eliminadas.
"""


class Base:
    """
    Descripcion:
        Representa la base central que el defensor debe proteger.
        Tiene una cantidad de vida que disminuye cuando es atacada
        por las unidades enemigas que logran llegar hasta ella.

    Entradas:
        vida_inicial (int): Cantidad de vida con la que inicia la
            base. Por defecto es 200.

    Salidas:
        No retorna nada. Construye una instancia de Base.

    Restricciones:
        - vida_inicial debe ser un valor entero positivo.
    """

    def __init__(self, vida_inicial=200):
        self.vida_maxima = vida_inicial
        self.vida = vida_inicial

    def recibir_dano(self, cantidad_dano):
        """
        Descripcion:
            Reduce la vida de la base segun la cantidad de dano
            recibido. La vida nunca desciende por debajo de cero.

        Entradas:
            cantidad_dano (int): Cantidad de dano a aplicar.

        Salidas:
            None: Modifica el atributo vida de la base.

        Restricciones:
            - cantidad_dano debe ser un valor mayor o igual a cero.
        """
        self.vida = max(0, self.vida - cantidad_dano)

    def fue_destruida(self):
        """
        Descripcion:
            Indica si la base central ha sido destruida.

        Entradas:
            Ninguna.

        Salidas:
            bool: True si la vida de la base es menor o igual a
            cero, False en caso contrario.

        Restricciones:
            Ninguna.
        """
        return self.vida <= 0

    def porcentaje_vida_restante(self):
        """
        Descripcion:
            Calcula el porcentaje de vida restante de la base con
            respecto a su vida maxima. Util para que la interfaz
            grafica muestre una barra de vida.

        Entradas:
            Ninguna.

        Salidas:
            float: Porcentaje de vida restante, entre 0.0 y 100.0.

        Restricciones:
            Ninguna.
        """
        if self.vida_maxima == 0:
            return 0.0
        return (self.vida / self.vida_maxima) * 100

    def reiniciar(self):
        """
        Descripcion:
            Restaura la vida de la base a su valor maximo. Util al
            iniciar una nueva ronda dentro de la misma partida.

        Entradas:
            Ninguna.

        Salidas:
            None: Modifica el atributo vida de la base.

        Restricciones:
            Ninguna.
        """
        self.vida = self.vida_maxima
