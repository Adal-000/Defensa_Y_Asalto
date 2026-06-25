# Defensa y Asalto de Base

Proyecto de Introducción a la Programación. Juego de estrategia para
dos jugadores en Python con interfaz gráfica en Tkinter.

## Estructura del repositorio

```text
Defensa_Y_Asalto/
├── Interfaz/             # Desarrollador 1 — ventanas Tkinter
│   ├── root.py           # Punto de entrada del programa completo
│   ├── login.py          # Inicio de sesión y registro
│   ├── main.py           # Menú principal
│   ├── perfil.py         # Perfil del jugador
│   ├── puntajes.py       # Ranking propio y mundial
│   ├── play.py           # Pantalla de juego
│   └── config.py         # Configuración visual
├── Logica/               # Desarrollador 2 — lógica interna del juego
│   ├── jugador.py        # Clase Jugador
│   ├── archivos.py       # Registro, login, JSON y victorias
│   ├── torre.py          # Torres defensivas y habilidades
│   ├── unidad.py         # Unidades atacantes y habilidades
│   ├── muro.py           # Muros defensivos
│   ├── base.py           # Base central
│   ├── combate.py        # Movimiento, ataques y habilidades
│   ├── partida.py        # Rondas, dinero y victoria
│   ├── ranking.py        # Top 5 defensores y atacantes
│   └── app.py            # Funciones públicas para Tkinter
├── datos/
│   ├── .gitkeep
│   └── jugadores.json    # Se crea/actualiza en ejecución
├── pruebas/
│   └── test_logica.py    # Pruebas unitarias de la lógica
└── demo_consola.py       # Simulación por consola, sin Tkinter
```

## Cómo ejecutar el juego

Desde la raíz del repositorio:

```bash
python Interfaz/root.py
```

`root.py` agrega automáticamente la carpeta `Logica/` a `sys.path`,
así que no es necesario instalar nada adicional.

## Funciones principales para la interfaz

El Desarrollador 1 debe conectarse principalmente con `Logica/app.py`.
Ese archivo no usa Tkinter; solo recibe y devuelve datos simples.

Funciones disponibles:

```python
registrar_jugador(usuario, contrasena)
validar_login(usuario, contrasena)
obtener_jugador(usuario)
crear_partida(defensor, atacante)
comprar_torre(tipo_torre, fila, columna)
comprar_muro(fila, columna)
comprar_unidad(tipo_unidad, fila, columna)
ejecutar_combate()
obtener_estado_partida()
obtener_catalogo_torres()
obtener_catalogo_unidades()
obtener_top_defensores()
obtener_top_atacantes()
```

## Lógica implementada

La parte del Desarrollador 2 incluye:

- Registro e inicio de sesión con archivo JSON.
- Evita usuarios repetidos.
- Limpieza y validación básica de credenciales.
- Actualización de victorias por rol al finalizar la partida.
- Ranking top 5 de defensores y atacantes.
- Clase `Jugador`.
- Clase `Torre` con tipos: `arquera`, `cañon`, `hielo`, `soporte`.
- Clase `Unidad` con tipos: `soldado`, `escudero`, `explorador`, `demoledor`.
- Clase `Muro` para bloquear unidades.
- Clase `Base` con vida y destrucción.
- Clase `Partida` para rondas, dinero, compras, marcador y victoria.
- Módulo `combate.py` para movimiento, ataques, daño, eliminación y habilidades.

## Sistema de dinero

- El defensor inicia con dinero para comprar torres y muros.
- El atacante inicia con dinero para comprar unidades.
- En cada ronda aumenta el dinero inicial con un bono adicional.
- El defensor gana dinero al eliminar unidades.
- El atacante gana dinero al dañar o destruir torres.
- El atacante gana dinero al dañar la base central.

## Habilidades implementadas

Torres:

- `arquera`: disparo doble.
- `cañon`: daño en área.
- `hielo`: congela unidades.
- `soporte`: repara torres dañadas.

Unidades:

- `soldado`: ataque doble.
- `escudero`: escudo temporal.
- `explorador`: aumento de velocidad.
- `demoledor`: daño extra contra torres.

## Cómo ejecutar las pruebas

Desde la raíz del repositorio:

```bash
python -m unittest pruebas.test_logica -v
```

Actualmente las pruebas cubren:

- Registro.
- Login.
- Carga y guardado de jugadores.
- Actualización de victorias.
- Compra de torres.
- Compra de muros.
- Compra de unidades.
- Validación de posiciones ocupadas y fuera del tablero.
- Daño a unidades, torres, muros y base.
- Habilidades de torres y unidades.
- Condiciones de victoria.
- Recompensas de dinero por combate.
- Ranking.

## Cómo ejecutar la demo de consola

Útil para probar la lógica sin abrir ventanas:

```bash
python demo_consola.py
```

## Nota para la interfaz gráfica

`play.py` ya permite crear partidas, comprar torres, comprar unidades y
ejecutar combate. La función `comprar_muro(fila, columna)` ya existe en
la lógica y queda lista para conectarse desde Tkinter si se desea agregar
un botón de compra de muros.
