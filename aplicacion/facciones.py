"""
Catalogo visual de facciones para la interfaz.

Las facciones solo cambian la apariencia del lobby y del mapa. No
modifican dinero, daño, vida, velocidad, habilidades, rondas ni victoria.
"""

FACCIONES_VISUALES = [
    {
        "clave": "espana",
        "nombre": "España",
        "codigo": "ESP",
        "imagen": "Imagenes/Soldados/España/Soldado base/Soldado_ESP_gun1.png",
    },
    {
        "clave": "inglaterra",
        "nombre": "Inglaterra",
        "codigo": "ENG",
        "imagen": "Imagenes/Soldados/Inglaterra/Soldado base/Soldado_ENG_gun1.png",
    },
    {
        "clave": "alemania",
        "nombre": "Alemania",
        "codigo": "ALE",
        "imagen": "Imagenes/Soldados/Alemania/Soldado normal/Soldado_ALE_gun1.png",
    },
    {
        "clave": "rusia",
        "nombre": "Rusia",
        "codigo": "RUS",
        "imagen": "Imagenes/Soldados/Rusia/Soldado base/Soldado_RUS_gun1.png",
    },
    {
        "clave": "italia",
        "nombre": "Italia",
        "codigo": "ITA",
        "imagen": "Imagenes/Soldados/Italia/Soldado base/Soldado_ITA_gun1.png",
    },
    {
        "clave": "eeuu",
        "nombre": "EE.UU",
        "codigo": "USA",
        "imagen": "Imagenes/Soldados/EEUU/Soldado base/Soldado_USA_gun1.png",
    },
]


def obtener_catalogo_facciones():
    """
    Devuelve las facciones visuales disponibles para Tkinter.
    """
    return [faccion.copy() for faccion in FACCIONES_VISUALES]
