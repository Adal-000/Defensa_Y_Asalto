# Defensa y Asalto de Base

Proyecto de Introducción a la Programación. Juego de estrategia para
dos jugadores en Python con interfaz gráfica en Tkinter.

## Cambios recientes (corrección de jugabilidad)

Esta versión corrige varios problemas del flujo cliente-servidor y
del ritmo del combate:

- El reloj de preparación (15s atacante + 15s defensor) ahora lo
  controla siempre el servidor/clase `Partida`, no la interfaz. Esto
  evita que cada dispositivo muestre un tiempo distinto.
- Se eliminaron funciones duplicadas y dos sistemas de temporizador
  que competían entre sí en `presentacion/interfaz/mapa.py`.
- Las piezas compradas ahora se ven de inmediato en el tablero (antes
  la compra no refrescaba la vista).
- El catálogo de torres se redujo a los 3 tipos reales que existen en
  `Imagenes/estructuras/<faccion>/`: `normal`, `pesada`, `especial`.
- Se corrigieron los nombres de los soldados (`soldado`, `rapido`,
  `tanque`) para que coincidan con las carpetas de
  `Imagenes/Soldados/<faccion>/`.
- Se subió la vida y se bajó el daño de torres, muros, soldados y
  base para que el combate sea más lento y equilibrado: dos piezas
  del mismo costo ahora se intercambian 6 a 10 golpes en vez de
  eliminarse casi de inmediato.
- El panel de compra ahora muestra vida y daño además del costo.
- La música de fondo ahora es global a todo el programa (usa
  `pygame.mixer` desde `aplicacion/musica.py`): empieza a sonar al
  abrir el programa con la canción predeterminada de `Musica/` y
  sigue sonando sin importar qué ventana esté abierta. Solo se
  detiene si el jugador entra a Configuración y presiona "Detener",
  o al cerrar el programa por completo.
- Cada facción tiene una habilidad especial propia, usable tanto por
  el defensor como por el atacante si juegan esa facción (botón
  "💥 Habilidad" en el mapa). Es un ataque de área independiente de
  las compras normales, con su propio costo y tiempo de enfriamiento:
  el defensor la dispara desde su base hacia el campo del atacante,
  y el atacante la dispara desde el lado contrario a la base hacia
  el campo del defensor. Ver la sección "Habilidades especiales por
  facción" más abajo.

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
│   └── config.py         # Configuración de conexión
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

Al arrancar, el programa intenta reproducir música de fondo con
`pygame.mixer` (instalar con `pip install pygame` si no está
disponible). Si pygame no está instalado, el juego sigue funcionando
normalmente, solo sin sonido. La música suena de forma continua sin
importar qué ventana esté abierta; solo se detiene desde el botón
"Detener" en la ventana de Configuración o al cerrar el programa.

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
obtener_catalogo_facciones()
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
- Clase `Torre` con tipos: `normal`, `pesada`, `especial` (alineados a las
  imagenes de `Imagenes/estructuras/<faccion>/`).
- Clase `Unidad` con tipos: `soldado` (Soldado base), `rapido` (Soldado
  rápido), `tanque` (Soldado tanque), alineados a `Imagenes/Soldados/<faccion>/`.
- Clase `Muro` para bloquear unidades.
- Clase `Base` con vida y destrucción.
- Clase `Partida` para rondas, dinero, compras, marcador y victoria.
- Módulo `combate.py` para movimiento, ataques, daño, eliminación y habilidades.
- Catálogo visual de facciones: España, Inglaterra, Alemania, Rusia, Italia y EE.UU.


## Rondas, dinero y condiciones de victoria

Cada partida se juega por rondas y gana la partida completa el primer
jugador que llegue a 3 rondas ganadas. Cada ronda sigue este orden:

1. El atacante recibe dinero y tiene **15 segundos** para comprar y
   colocar sus unidades en su zona del tablero.
2. Al agotarse esos 15 segundos, el atacante queda **bloqueado** (no
   puede comprar mas tropas) y el defensor recibe dinero para construir.
3. El defensor tiene otros **15 segundos** para comprar y colocar
   torres y muros en su zona del tablero.
4. Al agotarse el tiempo del defensor, si el atacante coloco al menos
   una unidad, inicia el **combate en tiempo real**; si no coloco
   ninguna, el defensor gana la ronda de inmediato sin combate.
5. Durante el combate ambos jugadores pueden seguir comprando: el
   defensor más torres/muros y el atacante más unidades, mientras les
   alcance el dinero.
6. Si el atacante tiene dinero suficiente para otra unidad pero no
   tiene ninguna unidad viva en el tablero, se le dan 7 segundos de
   gracia; si no coloca nada en ese tiempo, termina la ronda.
7. Si el dinero del atacante ya no alcanza para la unidad mas barata y
   no tiene unidades vivas, la ronda termina de inmediato.
8. Si la base del defensor es destruida, la ronda termina de inmediato
   a favor del atacante.
9. Se determina el ganador de la ronda y se actualiza el marcador.
10. Si nadie ha ganado 3 rondas, inicia una nueva ronda (vuelve al
    paso 1, con mas dinero disponible para ambos).

El defensor gana la ronda si la base central sigue en pie y el atacante
se queda sin dinero o todas sus unidades son eliminadas. El atacante gana
la ronda si destruye la base central del defensor. Al terminar la partida
se actualiza el registro de victorias del jugador ganador segun el rol
utilizado.

Tanto en modo local como en red, el reloj de los 15 segundos de cada
fase lo calcula siempre la clase `Partida` (campo
`segundos_restantes_preparacion` del estado), nunca un contador propio
de la interfaz grafica. Esto evita que el defensor y el atacante vean
temporizadores distintos cuando juegan desde dos dispositivos.

## Sistema de dinero

- El defensor inicia con dinero para comprar torres y muros.
- El atacante inicia con dinero para comprar unidades.
- En cada ronda aumenta el dinero inicial con un bono adicional.
- El defensor gana dinero al eliminar unidades.
- El atacante gana dinero al dañar o destruir torres.
- El atacante gana dinero al dañar la base central.

## Habilidades implementadas

Torres (defensor, costo - vida - daño - alcance):

- `normal` ($90, vida 220, daño 28, alcance 4): disparo doble cada
  4 turnos de combate.
- `pesada` ($130, vida 320, daño 38, alcance 3): daño en área cada
  4 turnos (golpea a todas las unidades dentro de su alcance).
- `especial` ($110, vida 260, daño 24, alcance 4): congela una unidad
  enemiga cada 4 turnos para retrasar su avance.

Unidades (atacante, costo - vida - daño - velocidad):

- `soldado` / Soldado base ($90, vida 220, daño 28, velocidad 1):
  ataque doble cada 4 turnos.
- `rapido` / Soldado rápido ($70, vida 150, daño 20, velocidad 2):
  avanza 2 casillas por turno.
- `tanque` / Soldado tanque ($130, vida 320, daño 38, velocidad 1):
  daño extra contra torres.

El balance esta pensado para que dos piezas del mismo costo (por
ejemplo Soldado base vs Torre normal, ambas a $90) se golpeen entre
6 y 10 veces antes de que una caiga, en vez de eliminarse en 1-3
golpes. El ritmo de combate sigue siendo de un turno por segundo,
pero con vida alta y daño moderado el avance se aprecia mas lento y
parejo.

## Habilidades especiales por facción

Ademas de torres, muros y soldados, cada facción tiene una habilidad
especial unica que cualquiera de los dos roles puede usar si esta
jugando con esa facción (el defensor con su propio botón, el
atacante con el suyo). Es un ataque de área independiente de las
compras normales: tiene su propio costo, su propio daño y su propio
tiempo de enfriamiento (cooldown), definidos en
`dominio/entidades/habilidad_especial.py`.

| Facción | Habilidad | Costo | Daño | Enfriamiento |
|---|---|---|---|---|
| Alemania | Gas tóxico | $170 | 30 | 20s |
| EE.UU | Lluvia de granadas | $175 | 40 | 18s |
| España | Bombardeo de artillería | $180 | 45 | 18s |
| Inglaterra | Lluvia de flechas | $150 | 35 | 15s |
| Rusia | Ataque de mortero | $190 | 55 | 20s |
| Italia | Cortina de humo y fuego | $160 | 32 | 16s |

Dirección del ataque (de dónde "salen" los proyectiles):

- El **defensor** la dispara desde su base (fila 0) hacia las
  primeras filas de la zona del atacante, dañando a las unidades que
  estén ahí.
- El **atacante** la dispara desde el lado contrario a la base (el
  extremo opuesto del tablero) hacia las últimas filas de la zona
  del defensor, dañando a las torres y muros que estén ahí.

La facción de cada rol se fija al elegirla en el lobby de `play.py`
(mensaje `elegir_faccion`) y queda guardada en la partida mediante
`Partida.establecer_faccion(rol, faccion)`; el servidor sincroniza
esto automáticamente. Para usarla se llama
`Partida.usar_habilidad_especial(rol)`, que valida fase, dinero y
enfriamiento antes de aplicar el daño.


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
torre normal 2 2
muro 5 1
unidad soldado 10 2
iniciar
pausar
estado
salir
```

Para tiempo real, se usa `iniciar`. Desde ese momento el servidor avanza
la simulacion de combate automaticamente cada segundo y envia el estado
actualizado a ambos clientes.

### Conexion con Tkinter

La pantalla `Interfaz/play.py` ya trabaja como cliente de red. Al entrar
a Play, el jugador puede elegir entre `Crear servidor` para hospedar la
partida desde su computadora o `Unirse a partida` para conectarse a la
IP de otro servidor. La interfaz no llama directamente a `Partida` cuando
se juega en dos computadoras; usa `ClientePartida` para enviar acciones
y recibir el estado oficial calculado por el servidor. Los metodos
principales son:

```python
cliente.conectar(ip_servidor, usuario, rol="defensor")
cliente.comprar_torre("normal", fila, columna)
cliente.comprar_muro(fila, columna)
cliente.comprar_unidad("soldado", fila, columna)
cliente.iniciar_combate()
cliente.pausar_combate()
estado = cliente.obtener_ultimo_estado_local()
resumen_red = cliente.obtener_resumen_red()
```

Si el puerto escrito no esta disponible al crear servidor desde `Play`, la interfaz prueba puertos alternativos cercanos y actualiza el campo `Puerto` con el que debe usar el segundo jugador. La pantalla tambien muestra de forma destacada la IP local y el puerto que el anfitrion debe compartir.

Las facciones de `Play` son visuales: se cargan desde `aplicacion.obtener_catalogo_facciones()`, usan imagenes existentes de `Imagenes/Soldados/`, dibujan una bandera dentro del boton de pais, muestran su codigo y no cambian dinero, daño, vida, velocidad, habilidades, rondas ni victoria.

El servidor envia en `datos` campos estandar para facilitar la interfaz:

- `fase_actual`: `esperando_jugadores`, `preparacion`, `combate` o `finalizada`.
- `combate_activo`: indica si el servidor esta avanzando la simulacion automaticamente.
- `partida_creada`: indica si ya se conectaron defensor y atacante.
- `jugadores_conectados`: cantidad de clientes activos.
- `roles_ocupados`: roles actualmente conectados.
- `rol_cliente` y `usuario_cliente`: aparecen en respuestas dirigidas a un cliente.
- `acciones_permitidas`: lista de acciones que el cliente puede enviar segun su rol y fase.
- `codigo_error`: aparece cuando una accion falla por fase, rol o condicion de partida.

El servidor valida que los usuarios existan en `datos/jugadores.json`
antes de aceptar una conexion de partida. Por eso, los jugadores deben
registrarse desde la interfaz antes de entrar al modo en red.

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
- Validacion de usuarios registrados antes de entrar al servidor.
- Estado estandar de red con fase actual y combate activo.
- Limpieza de sala cuando todos los clientes se desconectan.
- Acciones permitidas por rol y fase de partida.
- Codigos de error para acciones fuera de fase o combate sin unidades.

## Cómo ejecutar la demo de consola

Útil para probar la lógica sin abrir ventanas:

```bash
python demo_consola.py
```


### Configuración de interfaz

La pantalla `Config` permite ajustar preferencias de la sesión: IP predeterminada y puerto predeterminado para abrir `Play`. Estas opciones no cambian reglas del juego; solo afectan valores sugeridos de conexión.

## Nota para la interfaz gráfica

`play.py` ya permite crear un servidor local, unirse a un servidor remoto,
comprar torres, comprar muros, comprar unidades, iniciar/pausar combate
y actualizar el tablero
usando el estado oficial recibido por red. La pantalla `Mapa` muestra el dinero de defensor y atacante en tarjetas visibles, permite colocar piezas haciendo clic en casillas válidas, consulta el estado de red para dibujar lo que ambos jugadores colocan y usa un contador de preparación antes de iniciar el combate automáticamente.

La interfaz debe seguir
limitandose a mostrar datos y enviar acciones; el calculo de combate,
dinero, rondas y victoria permanece en `Logica/` y en el servidor.
