"""
Descripcion:
    Modulo de interfaz logica del Desarrollador 2. Expone las
    funciones principales que el Desarrollador 1 debe llamar desde
    la interfaz grafica en Tkinter, sin que este necesite conocer
    los detalles internos de las clases Jugador, Torre, Unidad,
    Base, Partida o Combate.

    Ninguna funcion de este modulo depende de Tkinter ni de ninguna
    libreria grafica; solo se trabaja con datos basicos de Python
    (str, int, bool, dict, list) para que el Desarrollador 1 pueda
    conectarlos facilmente con los widgets de su interfaz.
"""

from infraestructura.persistencia import archivos
from infraestructura.persistencia.archivos import registrar_jugador as _registrar_jugador
from infraestructura.persistencia.archivos import validar_login as _validar_login
from infraestructura.persistencia.archivos import buscar_jugador as _buscar_jugador
from infraestructura.persistencia.archivos import cargar_jugadores as _cargar_jugadores
from aplicacion.partida import crear_partida as _crear_partida
from aplicacion.ranking import obtener_top_defensores as _obtener_top_defensores
from aplicacion.ranking import obtener_top_atacantes as _obtener_top_atacantes
from aplicacion.facciones import obtener_catalogo_facciones as _obtener_catalogo_facciones
from aplicacion.configuracion import obtener_configuracion as _obtener_configuracion
from aplicacion.configuracion import actualizar_configuracion as _actualizar_configuracion
from aplicacion.configuracion import restablecer_configuracion as _restablecer_configuracion

_partida_actual = None


def registrar_jugador(usuario, contrasena):
    """
    Descripcion:
        Registra un nuevo jugador en el sistema de archivos.

    Entradas:
        usuario (str): Nombre de usuario deseado.
        contrasena (str): Contrasena deseada.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje
        descriptivo, listos para mostrarse en la interfaz grafica.

    Restricciones:
        - usuario no debe estar previamente registrado.
    """
    return _registrar_jugador(usuario, contrasena)


def validar_login(usuario, contrasena):
    """
    Descripcion:
        Valida las credenciales de un jugador para permitirle
        iniciar sesion en el juego.

    Entradas:
        usuario (str): Nombre de usuario ingresado.
        contrasena (str): Contrasena ingresada.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje
        descriptivo, listos para mostrarse en la interfaz grafica.

    Restricciones:
        Ninguna.
    """
    return _validar_login(usuario, contrasena)


def obtener_jugador(usuario):
    """
    Descripcion:
        Obtiene la informacion completa de un jugador registrado,
        util para mostrar su perfil (victorias como defensor y como
        atacante) en la interfaz grafica.

    Entradas:
        usuario (str): Nombre de usuario del jugador a consultar.

    Salidas:
        dict: Diccionario con "nombre_usuario", "victorias_defensor",
        "victorias_atacante" y "total_victorias". None si el
        jugador no existe.

    Restricciones:
        Ninguna.
    """
    jugador_encontrado = _buscar_jugador(usuario)

    if jugador_encontrado is None:
        return None

    return {
        "nombre_usuario": jugador_encontrado.nombre_usuario,
        "victorias_defensor": jugador_encontrado.victorias_defensor,
        "victorias_atacante": jugador_encontrado.victorias_atacante,
        "total_victorias": jugador_encontrado.total_victorias(),
    }


def crear_partida(defensor, atacante):
    """
    Descripcion:
        Crea una nueva partida entre los dos jugadores indicados y
        la establece como la partida activa del sistema.

    Entradas:
        defensor (str): Nombre de usuario del jugador defensor.
        atacante (str): Nombre de usuario del jugador atacante.

    Salidas:
        dict: Estado inicial de la partida, igual al que devuelve
        obtener_estado_partida().

    Restricciones:
        - defensor y atacante deben ser distintos entre si.
    """
    global _partida_actual
    _partida_actual = _crear_partida(defensor, atacante)
    return _partida_actual.obtener_estado_partida()


def comprar_torre(tipo_torre, fila, columna):
    """
    Descripcion:
        Permite al defensor comprar una torre dentro de la partida
        activa.

    Entradas:
        tipo_torre (str): Tipo de torre a comprar.
        fila (int): Fila del tablero donde se coloca la torre.
        columna (int): Columna del tablero donde se coloca la torre.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje
        descriptivo.

    Restricciones:
        - Debe existir una partida activa creada con crear_partida.
    """
    if _partida_actual is None:
        return False, "No hay una partida activa."
    return _partida_actual.comprar_torre(tipo_torre, fila, columna)


def comprar_muro(fila, columna):
    """
    Descripcion:
        Permite al defensor comprar un muro dentro de la partida
        activa. Esta funcion queda disponible para que la interfaz
        grafica pueda agregar compra de muros sin cambiar la logica.

    Entradas:
        fila (int): Fila del tablero donde se coloca el muro.
        columna (int): Columna del tablero donde se coloca el muro.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje
        descriptivo.

    Restricciones:
        - Debe existir una partida activa creada con crear_partida.
    """
    if _partida_actual is None:
        return False, "No hay una partida activa."
    return _partida_actual.comprar_muro(fila, columna)


def comprar_unidad(tipo_unidad, fila, columna):
    """
    Descripcion:
        Permite al atacante comprar una unidad dentro de la partida
        activa.

    Entradas:
        tipo_unidad (str): Tipo de unidad a comprar.
        fila (int): Fila del tablero donde se coloca la unidad.
        columna (int): Columna del tablero donde se coloca la
            unidad.

    Salidas:
        tuple[bool, str]: Exito de la operacion y mensaje
        descriptivo.

    Restricciones:
        - Debe existir una partida activa creada con crear_partida.
    """
    if _partida_actual is None:
        return False, "No hay una partida activa."
    return _partida_actual.comprar_unidad(tipo_unidad, fila, columna)


def iniciar_fase_ataque():
    """
    Descripcion:
        Finaliza la construccion del defensor y activa la compra y
        colocacion de unidades del atacante en la partida actual.
    """
    if _partida_actual is None:
        return False, "No hay una partida activa."
    return _partida_actual.iniciar_fase_ataque()


def iniciar_fase_combate():
    """
    Descripcion:
        Inicia la fase de combate de la ronda actual si ya se colocaron
        unidades atacantes.
    """
    if _partida_actual is None:
        return False, "No hay una partida activa."
    return _partida_actual.iniciar_fase_combate()


def resolver_preparacion_agotada():
    """
    Descripcion:
        Resuelve el final de los 15 segundos de preparación. Si no hay
        unidades atacantes, el defensor gana la ronda; si ya hay unidades,
        se inicia el combate en tiempo real.
    """
    if _partida_actual is None:
        return False, "No hay una partida activa."
    return _partida_actual.resolver_preparacion_agotada()


def ejecutar_combate():
    """
    Descripcion:
        Ejecuta un turno de combate dentro de la partida activa.

    Entradas:
        Ninguna.

    Salidas:
        dict: Resumen del turno de combate (eventos ocurridos, vida
        de la base, dinero actualizado, si la ronda finalizo, etc.).
        Si no hay partida activa, devuelve un diccionario vacio.

    Restricciones:
        - Debe existir una partida activa creada con crear_partida.
    """
    if _partida_actual is None:
        return {}
    return _partida_actual.ejecutar_combate()


def obtener_estado_partida():
    """
    Descripcion:
        Obtiene el estado actual completo de la partida activa,
        listo para que la interfaz grafica lo muestre.

    Entradas:
        Ninguna.

    Salidas:
        dict: Estado actual de la partida. Si no hay partida activa,
        devuelve un diccionario vacio.

    Restricciones:
        - Debe existir una partida activa creada con crear_partida.
    """
    if _partida_actual is None:
        return {}
    return _partida_actual.obtener_estado_partida()


def obtener_catalogo_torres():
    """
    Descripcion:
        Devuelve informacion basica de los tipos de torres que puede
        comprar el defensor. Es util para llenar menus o etiquetas de
        ayuda en la interfaz grafica.

    Entradas:
        Ninguna.

    Salidas:
        list[dict]: Lista con clave, nombre, costo, vida, dano,
        alcance y habilidad de cada torre disponible.

    Restricciones:
        Ninguna.
    """
    from dominio.entidades.torre import FABRICANTES_TORRES

    catalogo = []
    for clave, fabricante in FABRICANTES_TORRES.items():
        torre = fabricante()
        catalogo.append({
            "clave": clave,
            "nombre": torre.nombre,
            "costo": torre.costo,
            "vida": torre.vida,
            "dano": torre.dano,
            "alcance": torre.alcance,
            "habilidad": torre.habilidad,
            "turnos_habilidad": torre.turnos_habilidad,
        })
    return catalogo


def obtener_catalogo_unidades():
    """
    Descripcion:
        Devuelve informacion basica de los tipos de unidades que
        puede comprar el atacante. Es util para llenar menus o
        etiquetas de ayuda en la interfaz grafica.

    Entradas:
        Ninguna.

    Salidas:
        list[dict]: Lista con clave, nombre, costo, vida, dano,
        velocidad y habilidad de cada unidad disponible.

    Restricciones:
        Ninguna.
    """
    from dominio.entidades.unidad import FABRICANTES_UNIDADES, CLAVES_CATALOGO_UNIDADES

    catalogo = []
    for clave in CLAVES_CATALOGO_UNIDADES:
        fabricante = FABRICANTES_UNIDADES[clave]
        unidad = fabricante()
        catalogo.append({
            "clave": clave,
            "nombre": unidad.nombre,
            "costo": unidad.costo,
            "vida": unidad.vida,
            "dano": unidad.dano,
            "velocidad": unidad.velocidad,
            "habilidad": unidad.habilidad,
            "turnos_habilidad": unidad.turnos_habilidad,
        })
    return catalogo


def obtener_top_defensores():
    """
    Descripcion:
        Obtiene el ranking de los 5 mejores jugadores como
        defensores.

    Entradas:
        Ninguna.

    Salidas:
        list[dict]: Lista ordenada de jugadores con sus victorias
        como defensor.

    Restricciones:
        Ninguna.
    """
    return _obtener_top_defensores()


def obtener_top_atacantes():
    """
    Descripcion:
        Obtiene el ranking de los 5 mejores jugadores como
        atacantes.

    Entradas:
        Ninguna.

    Salidas:
        list[dict]: Lista ordenada de jugadores con sus victorias
        como atacante.

    Restricciones:
        Ninguna.
    """
    return _obtener_top_atacantes()


def obtener_catalogo_facciones():
    """
    Descripcion:
        Devuelve el catalogo de facciones visuales disponibles para
        la interfaz. Estas facciones no alteran reglas de juego; solo
        aportan nombre, codigo e imagen sugerida.

    Entradas:
        Ninguna.

    Salidas:
        list[dict]: Lista de facciones visuales.

    Restricciones:
        Ninguna.
    """
    return _obtener_catalogo_facciones()


def obtener_todos_puntajes():
    """
    Descripcion:
        Devuelve todos los jugadores registrados con sus victorias de
        defensor, atacante y total, ordenados por total de victorias.

    Entradas:
        Ninguna.

    Salidas:
        list[dict]: Puntajes completos de todos los jugadores.

    Restricciones:
        Ninguna.
    """
    jugadores = _cargar_jugadores()
    jugadores_ordenados = sorted(
        jugadores,
        key=lambda jugador: (jugador.total_victorias(), jugador.victorias_defensor, jugador.victorias_atacante),
        reverse=True,
    )
    return [
        {
            "nombre_usuario": jugador.nombre_usuario,
            "victorias_defensor": jugador.victorias_defensor,
            "victorias_atacante": jugador.victorias_atacante,
            "total_victorias": jugador.total_victorias(),
        }
        for jugador in jugadores_ordenados
    ]


def obtener_configuracion():
    """Devuelve las preferencias actuales de interfaz y conexion."""
    return _obtener_configuracion()


def actualizar_configuracion(**opciones):
    """Actualiza preferencias conocidas de interfaz y conexion."""
    return _actualizar_configuracion(**opciones)


def restablecer_configuracion():
    """Restaura las preferencias predeterminadas."""
    return _restablecer_configuracion()
