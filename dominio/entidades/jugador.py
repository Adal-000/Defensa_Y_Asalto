"""
Descripcion:
    Modulo que define la clase Jugador, encargada de representar a un
    usuario del juego "Defensa y Asalto de Base", junto con su informacion
    de acceso (usuario y contrasena) y sus estadisticas de victorias
    como defensor y como atacante.
"""


class Jugador:
    """
    Descripcion:
        Representa a un jugador registrado en el sistema. Guarda sus
        credenciales de acceso y el conteo de victorias obtenidas en
        cada uno de los dos roles posibles dentro de una partida.

    Entradas:
        nombre_usuario (str): Nombre unico que identifica al jugador.
        contrasena (str): Contrasena asociada al jugador para iniciar sesion.
        victorias_defensor (int): Cantidad de victorias acumuladas como
            defensor. Por defecto es 0.
        victorias_atacante (int): Cantidad de victorias acumuladas como
            atacante. Por defecto es 0.

    Salidas:
        No retorna nada. Construye una instancia de Jugador.

    Restricciones:
        - nombre_usuario no debe estar vacio.
        - victorias_defensor y victorias_atacante deben ser enteros
          mayores o iguales a cero.
    """

    def __init__(self, nombre_usuario, contrasena, victorias_defensor=0,
                 victorias_atacante=0):
        """
        Descripcion:
            Inicializa la instancia y asigna los valores necesarios para
            que el objeto pueda utilizarse correctamente.
        
        Entradas:
            nombre_usuario (object): Valor recibido por la funcion.
            contrasena (object): Valor recibido por la funcion.
            victorias_defensor (object): Valor recibido por la funcion.
            Valor opcional.
            victorias_atacante (object): Valor recibido por la funcion.
            Valor opcional.
        
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
        self.nombre_usuario = nombre_usuario
        self.contrasena = contrasena
        self.victorias_defensor = victorias_defensor
        self.victorias_atacante = victorias_atacante

    def sumar_victoria(self, rol):
        """
        Descripcion:
            Incrementa en uno el contador de victorias del jugador
            segun el rol indicado.

        Entradas:
            rol (str): Rol con el que se obtuvo la victoria. Debe ser
                "defensor" o "atacante".

        Salidas:
            None: Modifica directamente el atributo correspondiente
            (victorias_defensor o victorias_atacante).

        Restricciones:
            - rol debe ser exactamente "defensor" o "atacante", en caso
              contrario no se modifica ningun contador.
        """
        if rol == "defensor":
            self.victorias_defensor += 1
        elif rol == "atacante":
            self.victorias_atacante += 1

    def total_victorias(self):
        """
        Descripcion:
            Calcula el total de victorias del jugador sumando las
            obtenidas como defensor y como atacante.

        Entradas:
            Ninguna.

        Salidas:
            int: Suma de victorias_defensor y victorias_atacante.

        Restricciones:
            Ninguna.
        """
        return self.victorias_defensor + self.victorias_atacante

    def a_diccionario(self):
        """
        Descripcion:
            Convierte la informacion del jugador en un diccionario para
            que pueda ser almacenada facilmente en un archivo (por
            ejemplo, en formato JSON).

        Entradas:
            Ninguna.

        Salidas:
            dict: Diccionario con las claves "nombre_usuario",
            "contrasena", "victorias_defensor" y "victorias_atacante".

        Restricciones:
            Ninguna.
        """
        return {
            "nombre_usuario": self.nombre_usuario,
            "contrasena": self.contrasena,
            "victorias_defensor": self.victorias_defensor,
            "victorias_atacante": self.victorias_atacante,
        }

    @staticmethod
    def desde_diccionario(datos_jugador):
        """
        Descripcion:
            Reconstruye un objeto Jugador a partir de un diccionario,
            tipicamente leido desde un archivo de almacenamiento.

        Entradas:
            datos_jugador (dict): Diccionario con las claves
                "nombre_usuario", "contrasena", "victorias_defensor" y
                "victorias_atacante".

        Salidas:
            Jugador: Nueva instancia de Jugador construida con los
            datos del diccionario.

        Restricciones:
            - El diccionario debe contener al menos las claves
              "nombre_usuario" y "contrasena".
        """
        return Jugador(
            nombre_usuario=datos_jugador["nombre_usuario"],
            contrasena=datos_jugador["contrasena"],
            victorias_defensor=datos_jugador.get("victorias_defensor", 0),
            victorias_atacante=datos_jugador.get("victorias_atacante", 0),
        )

    def __repr__(self):
        """
        Descripcion:
            Ejecuta la logica correspondiente a   repr   dentro del
            flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Debe ejecutarse sobre objetos del dominio creados
            correctamente.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        return (f"Jugador(usuario={self.nombre_usuario!r}, "
                f"victorias_defensor={self.victorias_defensor}, "
                f"victorias_atacante={self.victorias_atacante})")
