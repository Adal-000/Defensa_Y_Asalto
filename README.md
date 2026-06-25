# Defensa y Asalto de Base

Proyecto de Introducción a la Programación. Juego de estrategia para
dos jugadores en Python con interfaz gráfica en Tkinter.

## Estructura del repositorio

```
Defensa_Y_Asalto/
├── Interfaz/             # Desarrollador 1 — ventanas Tkinter
│   ├── root.py           # Punto de entrada del programa completo
│   ├── login.py          # Inicio de sesión y registro
│   ├── main.py           # Menú principal
│   ├── perfil.py         # Perfil del jugador (victorias)
│   ├── puntajes.py       # Ranking propio y mundial
│   ├── play.py           # Pantalla de juego (compras y combate)
│   └── config.py         # Configuración
├── Logica/               # Desarrollador 2 — lógica interna del juego
│   ├── jugador.py
│   ├── archivos.py
│   ├── torre.py
│   ├── unidad.py
│   ├── base.py
│   ├── combate.py
│   ├── partida.py
│   ├── ranking.py
│   └── app.py            # Funciones públicas para la interfaz
├── datos/
│   └── jugadores.json    # Se crea automáticamente (no se versiona)
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
así que no es necesario instalar nada adicional ni cambiar de
directorio.

## Flujo de pantallas

1. **Login** (`login.py`): el jugador se registra o inicia sesión.
   Usa `app.registrar_jugador` y `app.validar_login`.
2. **Menú principal** (`main.py`): muestra el usuario con sesión activa.
3. **Perfil** (`perfil.py`): muestra las victorias del jugador como
   defensor y como atacante, usando `app.obtener_jugador`.
4. **Puntajes** (`puntajes.py`): muestra las victorias propias y el
   top 5 de defensores/atacantes a nivel mundial, usando
   `app.obtener_top_defensores` y `app.obtener_top_atacantes`.
5. **Play** (`play.py`): el usuario logueado juega como **defensor**
   contra un rival que se escribe como **atacante**. Permite:
   - Crear la partida (`app.crear_partida`).
   - Comprar torres (`app.comprar_torre`) eligiendo tipo, fila y columna.
   - Comprar unidades (`app.comprar_unidad`) eligiendo tipo, fila y columna.
   - Ejecutar turnos de combate (`app.ejecutar_combate`), viendo los
     eventos en una lista y el estado (dinero, vida de la base,
     marcador) en una etiqueta que se actualiza en cada acción.

Tipos de torre: `arquera`, `cañon`, `hielo`, `soporte`.
Tipos de unidad: `soldado`, `escudero`, `explorador`, `demoledor`.

> Nota: `play.py` no dibuja el tablero en un `Canvas` todavía; usa
> campos de texto para fila/columna y una lista de eventos. Es un
> punto de partida funcional que se puede mejorar visualmente sin
> tocar la lógica de `Logica/`.

## Cómo ejecutar las pruebas

```bash
python -m unittest pruebas.test_logica -v
```

## Cómo ejecutar la demo de consola (sin Tkinter)

Útil para depurar la lógica sin abrir ninguna ventana:

```bash
python demo_consola.py
```
