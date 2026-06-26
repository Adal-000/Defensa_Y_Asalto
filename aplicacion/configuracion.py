"""
Configuracion simple en memoria para preferencias de interfaz.

Estas opciones no cambian reglas del juego; solo ayudan a adaptar la
experiencia visual y valores predeterminados de conexion durante la sesion.
"""

CONFIGURACION_PREDETERMINADA = {
    "tema": "claro",
    "mostrar_cuadricula": True,
    "mostrar_proyectiles": True,
    "ip_servidor_predeterminada": "127.0.0.1",
    "puerto_predeterminado": 5000,
    "musica_pygame_activada": False,
    "volumen_musica": 70,
    "ruta_musica": "",
}

_configuracion_actual = CONFIGURACION_PREDETERMINADA.copy()


def obtener_configuracion():
    """Devuelve una copia de la configuracion actual."""
    return _configuracion_actual.copy()


def actualizar_configuracion(**opciones):
    """Actualiza opciones conocidas y devuelve la configuracion completa."""
    for clave, valor in opciones.items():
        if clave in _configuracion_actual:
            _configuracion_actual[clave] = valor
    return obtener_configuracion()


def restablecer_configuracion():
    """Restaura los valores de configuracion predeterminados."""
    _configuracion_actual.clear()
    _configuracion_actual.update(CONFIGURACION_PREDETERMINADA)
    return obtener_configuracion()
