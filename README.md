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
├── Red/                  # Cliente-servidor para dos computadoras
│   ├── protocolo.py      # Mensajes JSON por sockets
│   ├── servidor.py       # Servidor con la partida oficial
│   └── cliente.py        # Cliente para conectar la interfaz
├── datos/
│   ├── .gitkeep
│   └── jugadores.json    # Se crea/actualiza en ejecución
├── pruebas/
│   ├── test_logica.py    # Pruebas unitarias de la lógica
│   └── test_red.py       # Pruebas del protocolo de red
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


## Modo multijugador en dos computadoras

El modo de red usa una arquitectura cliente-servidor:

```text
Computadora servidor
└── Mantiene la unica Partida real

Computadora defensor
└── Envia acciones al servidor y recibe estados

Computadora atacante
└── Envia acciones al servidor y recibe estados
```

La partida no se duplica en las dos computadoras. El servidor controla
el estado oficial, valida las compras y ejecuta el combate en tiempo real.

### Ejecutar servidor

En la computadora que sera anfitriona:

```bash
python Red/servidor.py
```

El servidor mostrara una IP parecida a esta:

```text
Servidor iniciado en 192.168.1.25:5000
Esperando jugadores...
```

### Ejecutar clientes de prueba por consola

En la computadora del defensor:

```bash
python Red/cliente.py 192.168.1.25 daniel defensor
```

En la computadora del atacante:

```bash
python Red/cliente.py 192.168.1.25 mario atacante
```

Cambie `192.168.1.25` por la IP mostrada por el servidor. Ambas
computadoras deben estar en la misma red o tener permiso de firewall.

### Comandos disponibles en el cliente de consola

```text
torre arquera 2 2
muro 5 1
unidad soldado 10 2
iniciar
pausar
estado
salir
```

Para tiempo real, se usa `iniciar`. Desde ese momento el servidor ejecuta
un turno de combate automaticamente cada segundo y envia el estado
actualizado a ambos clientes.

### Conexion futura con Tkinter

La interfaz no debe llamar directamente a `Partida` cuando se juegue en
dos computadoras. Debe crear un `ClientePartida` y usar metodos como:

```python
cliente.conectar(ip_servidor, usuario, rol="defensor")
cliente.comprar_torre("arquera", fila, columna)
cliente.comprar_muro(fila, columna)
cliente.comprar_unidad("soldado", fila, columna)
cliente.iniciar_combate()
cliente.pausar_combate()
estado = cliente.obtener_ultimo_estado_local()
```

El siguiente paso del proyecto es tomar ese `estado` y dibujarlo en
`play.py` con botones, tablero, torres, muros, unidades y barra de vida
de la base.

## Cómo ejecutar las pruebas

Desde la raíz del repositorio:

```bash
python -m unittest pruebas.test_logica pruebas.test_red -v
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
- Protocolo JSON de red.
- Cliente sin conexion.
- Asignacion basica de roles del servidor.

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
