"""
Configuracion simple en memoria para preferencias de interfaz.

Estas opciones no cambian reglas del juego; solo ayudan a adaptar valores
predeterminados de conexion durante la sesion.
"""

CONFIGURACION_PREDETERMINADA = {
    "tema": "claro", # No se usa
    "mostrar_cuadricula": True, # No se usa
    "mostrar_proyectiles": True, #No se usa
    "ip_servidor_predeterminada": "127.0.0.1", # Direccion IP predeterminada para el servidor de juego ya sea local o remoto.
    "puerto_predeterminado": 5000, # Puerto predeterminado para la conexion al servidor de juego, VERIFICAR QUE ESTE DISPONIBLE
    "ruta_musica": "",
}

_configuracion_actual = CONFIGURACION_PREDETERMINADA.copy()


def obtener_configuracion():
    """
    Descripcion:
        Devuelve una copia de la configuracion actual.
    
    Entradas:
        Ninguna.
    
    Salidas:
        object: Resultado calculado o recuperado por la operacion.
    
    Restricciones:
        Ninguna.
    """
    return _configuracion_actual.copy()


def actualizar_configuracion(**opciones):
    """
    Descripcion:
        Actualiza opciones conocidas y devuelve la configuracion
        completa.
    
    Entradas:
        **opciones (object): Valor recibido por la funcion. Argumentos
        nombrados adicionales.
    
    Salidas:
        object: Resultado calculado o recuperado por la operacion.
    
    Restricciones:
        - Los parametros recibidos deben respetar el tipo y el formato
        esperado por la funcion.
    """
    for clave, valor in opciones.items():
        if clave in _configuracion_actual:
            _configuracion_actual[clave] = valor
    return obtener_configuracion()


def restablecer_configuracion():
    """
    Descripcion:
        Restaura los valores de configuracion predeterminados.
    
    Entradas:
        Ninguna.
    
    Salidas:
        object: Resultado calculado o recuperado por la operacion.
    
    Restricciones:
        Ninguna.
    """
    _configuracion_actual.clear()
    _configuracion_actual.update(CONFIGURACION_PREDETERMINADA)
    return obtener_configuracion()
