# Defensa y Asalto de Base

Proyecto de Introducción a la Programación.
Juego de estrategia para dos jugadores desarrollado en Python con interfaz gráfica en Tkinter y modo multijugador mediante conexión cliente-servidor.

---

## Integrantes
Adalberto Josue Mejías Bonilla
- 2026100990
Daruil Jesús Jiménez Monge
- 2026012437
## Descripción general

**Defensa y Asalto de Base** es un juego de estrategia para dos jugadores. Un jugador toma el rol de **defensor** y debe proteger su base colocando torres y muros. El otro jugador toma el rol de **atacante** y debe enviar unidades para destruir la base enemiga.

El juego incluye registro de usuarios, inicio de sesión, perfil de jugador, ranking, selección de facciones, música, sistema de dinero, rondas, combate en tiempo real y conexión entre dos computadoras usando sockets.

---

## Reglas principales

* La partida se juega entre dos roles: defensor y atacante.
* El defensor coloca torres y muros para proteger la base.
* El atacante coloca unidades para avanzar hacia la base.
* La partida se divide en rondas.
* Gana la partida el primer jugador que gane 3 rondas.
* El atacante gana una ronda si destruye la base del defensor.
* El defensor gana una ronda si logra eliminar las unidades atacantes o si el atacante no puede seguir atacando.
* Cada jugador usa dinero para comprar sus piezas.
* Durante el combate ambos jugadores pueden seguir comprando si tienen dinero disponible.

---

## Torres

| Torre    | Costo | Vida | Daño | Alcance | Función                                       |
| -------- | ----: | ---: | ---: | ------: | --------------------------------------------- |
| Normal   |    90 |  220 |   28 |       4 | Torre equilibrada con disparo doble.          |
| Pesada   |   130 |  320 |   38 |       3 | Torre resistente con daño en área.            |
| Especial |   110 |  260 |   24 |       4 | Torre de control que puede congelar unidades. |

---

## Unidades

| Unidad         | Costo | Vida | Daño | Velocidad | Función                               |
| -------------- | ----: | ---: | ---: | --------: | ------------------------------------- |
| Soldado base   |    90 |  220 |   28 |         1 | Unidad equilibrada.                   |
| Soldado rápido |    70 |  150 |   20 |         2 | Unidad veloz para presionar carriles. |
| Soldado tanque |   130 |  320 |   38 |         1 | Unidad resistente con daño alto.      |

---

## Facciones

El juego incluye las siguientes facciones visuales:

* España
* Inglaterra
* Alemania
* Rusia
* Italia
* EE.UU

Cada facción tiene imágenes propias para soldados, torres, estructuras y banderas. Además, cada facción posee una habilidad especial.

| Facción    | Habilidad especial      | Costo | Daño | Enfriamiento |
| ---------- | ----------------------- | ----: | ---: | -----------: |
| España     | Bombardeo de artillería |   180 |   45 |         18 s |
| Inglaterra | Lluvia de flechas       |   150 |   35 |         15 s |
| Alemania   | Gas tóxico              |   170 |   30 |         20 s |
| Rusia      | Ataque de mortero       |   190 |   55 |         20 s |
| Italia     | Cortina de humo y fuego |   160 |   32 |         16 s |
| EE.UU      | Lluvia de granadas      |   175 |   40 |         18 s |

---

## Estructura del proyecto

```text
Defensa_Y_Asalto/
├── aplicacion/
│   ├── app.py
│   ├── configuracion.py
│   ├── facciones.py
│   ├── musica.py
│   ├── partida.py
│   └── ranking.py
├── dominio/
│   ├── entidades/
│   │   ├── base.py
│   │   ├── habilidad_especial.py
│   │   ├── jugador.py
│   │   ├── muro.py
│   │   ├── torre.py
│   │   └── unidad.py
│   └── servicios/
│       └── combate.py
├── infraestructura/
│   ├── persistencia/
│   │   └── archivos.py
│   └── red/
│       ├── cliente.py
│       ├── protocolo.py
│       └── servidor.py
├── presentacion/
│   └── interfaz/
│       ├── config.py
│       ├── login.py
│       ├── main.py
│       ├── mapa.py
│       ├── perfil.py
│       ├── play.py
│       ├── puntajes.py
│       └── root.py
├── Imagenes/
├── Musica/
├── run_gui.py
└── README.md
```

---

## Requisitos

* Python 3.10 o superior.
* Tkinter.
* Pillow para manejo de imágenes.
* pygame o pygame-ce para música.

Instalación recomendada:

```bash
python -m pip install pillow pygame-ce
```

Si se usa `pygame` en lugar de `pygame-ce`:

```bash
python -m pip install pygame
```

---

## Instrucciones de ejecución

Desde la carpeta raíz del proyecto:

```bash
python run_gui.py
```

Si el sistema usa `py` en Windows:

```bash
py run_gui.py
```

---

## Ejecución en red

Para jugar en dos computadoras:

1. Ambas computadoras deben estar conectadas a la misma red.
2. Un jugador crea la sala desde la pantalla de juego.
3. El juego muestra una IP y un puerto.
4. El segundo jugador se une usando esa IP y ese puerto.
5. Cada jugador selecciona su facción.
6. Cuando ambos estén listos, inicia el mapa de juego.

Si Windows bloquea la conexión, se debe permitir Python en el firewall.

---

## Capturas de pantalla

Colocar aquí las capturas del proyecto:

* Login.
* Registro.
* Menú principal.
* Selección de facción.
* Mapa de juego.
* Perfil.
* Ranking.
* Configuración.

---

## Video evidencia de desarrollo del proyecto

Link del video:

```
PEGAR AQUÍ EL LINK DEL VIDEO DE 10+ MINUTOS
```

---

## Repositorio de GitHub

Link del repositorio:

```
PEGAR AQUÍ EL LINK DEL REPOSITORIO
```

---

## Conclusiones

El desarrollo del proyecto permitió aplicar conceptos de programación orientada a objetos, separación por capas, manejo de archivos, conexión por red y construcción de interfaces gráficas. Además, ayudó a comprender la importancia de dividir correctamente la lógica del juego, la interfaz y la persistencia de datos.