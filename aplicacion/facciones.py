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
        "soldado_base": "Imagenes/Soldados/España/Soldado base/Soldado_ESP_gun1.png",
        "soldado_rapido": "Imagenes/Soldados/España/Soldado rápido/Soldado_ESP_walk1.png",
        "soldado_tanque": "Imagenes/Soldados/España/Soldado tanque/Soldado_ESP_tank1.png",
        "estructura_base": "Imagenes/estructuras/España/Edificio_ESP_principal.png",
        "torre_normal": "Imagenes/estructuras/España/torre_ESP_normal1.png",
        "torre_pesada": "Imagenes/estructuras/España/torre_ESP_pesada1.png",
        "torre_especial": "Imagenes/estructuras/España/torre_ESP_especial1.png",
        "color_proyectil": "#f1bf00",
    },
    {
        "clave": "inglaterra",
        "nombre": "Inglaterra",
        "codigo": "ENG",
        "imagen": "Imagenes/Soldados/Inglaterra/Soldado base/Soldado_ENG_gun1.png",
        "soldado_base": "Imagenes/Soldados/Inglaterra/Soldado base/Soldado_ENG_gun1.png",
        "soldado_rapido": "Imagenes/Soldados/Inglaterra/Soldado rápido/Soldado_ENG_walk1.png",
        "soldado_tanque": "Imagenes/Soldados/Inglaterra/Soldado tanque/Soldado_ENG_tank1.png",
        "estructura_base": "Imagenes/estructuras/Inglaterra/Edificio_ENG_principal.png",
        "torre_normal": "Imagenes/estructuras/Inglaterra/torre_ENG_normal1.png",
        "torre_pesada": "Imagenes/estructuras/Inglaterra/torre_ENG_pesada1.png",
        "torre_especial": "Imagenes/estructuras/Inglaterra/torre_ENG_especial1.png",
        "color_proyectil": "#cf142b",
    },
    {
        "clave": "alemania",
        "nombre": "Alemania",
        "codigo": "ALE",
        "imagen": "Imagenes/Soldados/Alemania/Soldado normal/Soldado_ALE_gun1.png",
        "soldado_base": "Imagenes/Soldados/Alemania/Soldado normal/Soldado_ALE_gun1.png",
        "soldado_rapido": "Imagenes/Soldados/Alemania/Soldado rápido/Soldado_ALE_walk1.png",
        "soldado_tanque": "Imagenes/Soldados/Alemania/Soldado tanque/Soldado_BRA_tank1.png",
        "estructura_base": "Imagenes/estructuras/Alemania/Edificio_principal_GER.png",
        "torre_normal": "Imagenes/estructuras/Alemania/torre_GER_normal1.png",
        "torre_pesada": "Imagenes/estructuras/Alemania/torre_GER_pesada1.png",
        "torre_especial": "Imagenes/estructuras/Alemania/torre_GER_especial1.png",
        "color_proyectil": "#dd0000",
    },
    {
        "clave": "rusia",
        "nombre": "Rusia",
        "codigo": "RUS",
        "imagen": "Imagenes/Soldados/Rusia/Soldado base/Soldado_RUS_gun1.png",
        "soldado_base": "Imagenes/Soldados/Rusia/Soldado base/Soldado_RUS_gun1.png",
        "soldado_rapido": "Imagenes/Soldados/Rusia/Soldado rápido/Soldado_RUS_walk1.png",
        "soldado_tanque": "Imagenes/Soldados/Rusia/Soldado tanque/Soldado_RUS_tank1.png",
        "estructura_base": "Imagenes/estructuras/Rusia/Edificio_RUS_principal.png",
        "torre_normal": "Imagenes/estructuras/Rusia/torre_RUS_normal1.png",
        "torre_pesada": "Imagenes/estructuras/Rusia/torre_RUS_pesada1.png",
        "torre_especial": "Imagenes/estructuras/Rusia/torre_RUS_especial1.png",
        "color_proyectil": "#0039a6",
    },
    {
        "clave": "italia",
        "nombre": "Italia",
        "codigo": "ITA",
        "imagen": "Imagenes/Soldados/Italia/Soldado base/Soldado_ITA_gun1.png",
        "soldado_base": "Imagenes/Soldados/Italia/Soldado base/Soldado_ITA_gun1.png",
        "soldado_rapido": "Imagenes/Soldados/Italia/Soldado rápido/Soldado_ITA_walk1.png",
        "soldado_tanque": "Imagenes/Soldados/Italia/Soldado tanque/Soldado_BRA_tank1.png",
        "estructura_base": "Imagenes/estructuras/Italia/Edificio_ITA_principal.png",
        "torre_normal": "Imagenes/estructuras/Italia/torre_ITA_normal1.png",
        "torre_pesada": "Imagenes/estructuras/Italia/torre_ITA_pesada1.png",
        "torre_especial": "Imagenes/estructuras/Italia/torre_ITA_especial1.png",
        "color_proyectil": "#009246",
    },
    {
        "clave": "eeuu",
        "nombre": "EE.UU",
        "codigo": "USA",
        "imagen": "Imagenes/Soldados/EEUU/Soldado base/Soldado_USA_gun1.png",
        "soldado_base": "Imagenes/Soldados/EEUU/Soldado base/Soldado_USA_gun1.png",
        "soldado_rapido": "Imagenes/Soldados/EEUU/Soldado rápido/Soldado_USA_walk1.png",
        "soldado_tanque": "Imagenes/Soldados/EEUU/Soldado tanque/Soldado_USA_tank1.png",
        "estructura_base": "Imagenes/estructuras/EEUU/Edificio_USA_principal.png",
        "torre_normal": "Imagenes/estructuras/EEUU/torre_USA_normal1.png",
        "torre_pesada": "Imagenes/estructuras/EEUU/torre_USA_pesada1.png",
        "torre_especial": "Imagenes/estructuras/EEUU/torre_USA_especial1.png",
        "color_proyectil": "#3c3b6e",
    },
]


def obtener_catalogo_facciones():
    """
    Devuelve las facciones visuales disponibles para Tkinter.
    """
    return [faccion.copy() for faccion in FACCIONES_VISUALES]
