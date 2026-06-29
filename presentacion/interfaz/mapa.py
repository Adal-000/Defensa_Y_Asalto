#=======================================#
# Archivo para mostrar el mapa del juego
#=======================================#

import math
import os
import time
import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageOps, ImageTk
except ImportError:
    Image = None
    ImageOps = None
    ImageTk = None

from aplicacion import app


FILAS_TABLERO = 11
COLUMNAS_TABLERO = 6
ANCHO_CELDA = 115
ALTO_CELDA = 39
ANCHO_TABLERO = COLUMNAS_TABLERO * ANCHO_CELDA
ALTO_TABLERO = FILAS_TABLERO * ALTO_CELDA
FILA_BASE = 0
FILAS_DEFENSOR = range(1, 8)
FILAS_ATACANTE = range(8, 11)

COLOR_DEFENSA = "#dbeeff"
COLOR_ATAQUE = "#ffe8cf"
COLOR_BASE = "#ffd4d4"
COLOR_BORDE = "#666666"
COLOR_PANEL = "#ffffff"
SEGUNDOS_PREPARACION_ROL = 15

TIEMPO_PREPARACION_SEGUNDOS = 15
INTERVALO_POLLING_MS = 250
INTERVALO_POLLING_RAPIDO_MS = 120
INTERVALO_COMBATE_LOCAL_MS = 1000
RONDAS_PARA_GANAR = 3

FASE_ATAQUE_ATACANTE = "ataque_atacante"
FASE_CONSTRUCCION_DEFENSOR = "construccion_defensor"
FASE_COMBATE = "combate"


RUTA_PROYECTO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
RUTA_IMAGENES = os.path.join(RUTA_PROYECTO, "Imagenes")

CARPETAS_FACCION = {
    "España": ("España", "Espa#U00f1a", "Espania"),
    "Inglaterra": ("Inglaterra",),
    "Alemania": ("Alemania",),
    "Rusia": ("Rusia",),
    "Italia": ("Italia",),
    "EE.UU": ("EEUU", "EE.UU", "Estados Unidos"),
    "EEUU": ("EEUU", "EE.UU", "Estados Unidos"),
}

CODIGO_FACCION = {
    "España": "ESP",
    "Inglaterra": "ENG",
    "Alemania": "GER",
    "Rusia": "RUS",
    "Italia": "ITA",
    "EE.UU": "USA",
    "EEUU": "USA",
}

CLAVE_UNIDAD_POR_NOMBRE = {
    "soldado base": "soldado",
    "soldado": "soldado",
    "soldado normal": "soldado",
    "soldado rápido": "rapido",
    "soldado rapido": "rapido",
    "explorador": "rapido",
    "soldado tanque": "tanque",
    "tanque": "tanque",
    "escudero": "tanque",
    "demoledor": "tanque",
}

CLAVE_TORRE_POR_NOMBRE = {
    "torre normal": "normal",
    "normal": "normal",
    "torre arquera": "normal",
    "arquera": "normal",
    "torre pesada": "pesada",
    "pesada": "pesada",
    "torre cañon": "pesada",
    "torre canon": "pesada",
    "cañon": "pesada",
    "canon": "pesada",
    "torre especial": "especial",
    "especial": "especial",
    "torre de hielo": "especial",
    "hielo": "especial",
    "torre de soporte": "especial",
    "soporte": "especial",
}


# =====================================================================
# Entrada principal de la ventana
# =====================================================================

def mapa(root, GoPlay, cerrar_todo, configurar_ventana, obtener_datos_partida=None):
    """
    Descripcion:
        Crea la ventana jugable del mapa. Mantiene la lógica
        sincronizada con el servidor cuando hay red y usa la lógica
        local de app.py cuando se abre sin conexión.
    
    Entradas:
        root (object): Valor recibido por la funcion.
        GoPlay (object): Valor recibido por la funcion.
        cerrar_todo (object): Valor recibido por la funcion.
        configurar_ventana (object): Valor recibido por la funcion.
        obtener_datos_partida (object): Valor recibido por la funcion.
        Valor opcional.
    
    Salidas:
        None: Ejecuta la accion y puede modificar el estado interno, la
        interfaz o los datos relacionados.
    
    Restricciones:
        - Los parametros recibidos deben respetar el tipo y el formato
        esperado por la funcion.
        - Requiere que los widgets, ventanas o callbacks usados por la
        interfaz existan antes de ejecutarse.
    """

    window_mapa = tk.Toplevel(root)
    configurar_ventana(window_mapa, "Mapa")
    window_mapa.configure(bg=COLOR_PANEL)

    datos_partida = obtener_datos_partida() if obtener_datos_partida is not None else {}

    rol_jugador = (datos_partida.get("rol") or "defensor").strip().lower()
    nombre_usuario = datos_partida.get("usuario") or datos_partida.get("jugador") or "Jugador"

    faccion_jugador = datos_partida.get("faccion") or "Alemania"
    faccion_defensor = datos_partida.get("faccion_defensor")
    faccion_atacante = datos_partida.get("faccion_atacante")

    if not faccion_defensor:
        faccion_defensor = faccion_jugador if rol_jugador == "defensor" else "España"

    if not faccion_atacante:
        faccion_atacante = faccion_jugador if rol_jugador == "atacante" else "EE.UU"

    adaptador_red = datos_partida.get("adaptador")
    cliente_red = datos_partida.get("cliente_red")
    servidor_local = datos_partida.get("servidor_local")

    if cliente_red is None and adaptador_red is not None:
        cliente_red = getattr(adaptador_red, "cliente", None)

    modo_red = cliente_red is not None and getattr(cliente_red, "conectado", False)

    catalogo_facciones = app.obtener_catalogo_facciones()
    facciones_por_nombre = {faccion["nombre"]: faccion for faccion in catalogo_facciones}

    # Nombres de los jugadores para crear la partida local (sin red).
    # En modo red estos nombres los define el servidor segun quien se
    # conecto como defensor y quien como atacante.
    nombre_defensor = datos_partida.get("nombre_defensor") or (
        nombre_usuario if rol_jugador == "defensor" else "Defensor"
    )
    nombre_atacante = datos_partida.get("nombre_atacante") or (
        nombre_usuario if rol_jugador == "atacante" else "Atacante"
    )

    imagenes_mapa = {}
    cuadro_mapa = None
    etiqueta_marcador = None
    etiqueta_temporizador = None
    etiqueta_dinero_defensor = None
    etiqueta_dinero_atacante = None
    etiqueta_resultado = None
    boton_turno = None
    boton_habilidad = None
    caja_informacion_contrincante = None
    seleccion_actual = {"tipo": None, "clave": None, "nombre": None}
    ultimo_estado = {"datos": {}}
    botones_compra = []
    imagenes = {}

    preferencias = app.obtener_configuracion()

    def obtener_estado_visible():
        """
        Descripcion:
            Obtiene la informacion correspondiente a obtener estado
            visible para que otras partes del programa puedan
            utilizarla.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if modo_red:
            estado_red = cliente_red.obtener_ultimo_estado_local()
            if estado_red is not None:
                return estado_red
            return ultimo_estado["datos"]
        return app.obtener_estado_partida()

    def mostrar_cuadricula_activa():
        """
        Descripcion:
            Muestra o consulta el estado visible relacionado con mostrar
            cuadricula activa.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        return bool(app.obtener_configuracion().get("mostrar_cuadricula", True))

    def mostrar_proyectiles_activos():
        """
        Descripcion:
            Muestra o consulta el estado visible relacionado con mostrar
            proyectiles activos.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        return bool(app.obtener_configuracion().get("mostrar_proyectiles", True))

    if modo_red:
        cliente_red.obtener_estado()
        cliente_red.enviar_accion("elegir_faccion", faccion=faccion_jugador)
    else:
        app.crear_partida(nombre_defensor, nombre_atacante)
        app.establecer_faccion("defensor", faccion_defensor)
        app.establecer_faccion("atacante", faccion_atacante)

    control = {
        "cerrando": False,
        "after_polling": None,
        "after_timer": None,
        "after_combate": None,
        "after_volver": None,
        "after_ocultar_resultado": None,
        "combate_local_activo": False,
    }
    estado_ui = {
        "fase": FASE_ATAQUE_ATACANTE,
        "segundos": TIEMPO_PREPARACION_SEGUNDOS,
        "ronda": 1,
        "victorias_defensor": 0,
        "victorias_atacante": 0,
        "partida_finalizada": False,
        "resultados_mostrados": set(),
        "puntuacion_anterior": (0, 0),
    }
    # Rastreo de timestamps de habilidades para detectar disparo del rival
    ultimo_timestamp_habilidad = {"defensor": None, "atacante": None}
    # Momento (reloj local, time.monotonic) en que CADA rol disparó su
    # última habilidad especial. Se usa para mostrarle al usuario
    # "hace cuántos segundos" se usó, sin depender de la red.
    momento_disparo = {"defensor": None, "atacante": None}
    # Estado del efecto visual de habilidad especial actualmente en
    # pantalla. dibujar_zonas() borra TODO el canvas en cada refresco
    # (polling/combate), así que la animación debe volver a pintarse
    # cada vez que eso pase mientras siga activa; por eso se guarda
    # aquí en vez de solo en variables locales de la función.
    efecto_habilidad_activo = {
        "rol": None,
        "info": None,
        "inicio": None,
        "duracion_total": None,
        "fase_marco_oculto": False,
    }

    # -----------------------------------------------------------------
    # Utilidades generales
    # -----------------------------------------------------------------

    def ventana_activa():
        """
        Descripcion:
            Ejecuta la logica correspondiente a ventana activa dentro
            del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if control["cerrando"]:
            return False
        try:
            return bool(window_mapa.winfo_exists())
        except tk.TclError:
            control["cerrando"] = True
            return False

    def cancelar_after(clave):
        """
        Descripcion:
            Ejecuta la logica correspondiente a cancelar after dentro
            del flujo del juego.
        
        Entradas:
            clave (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if control.get(clave) is not None:
            try:
                window_mapa.after_cancel(control[clave])
            except tk.TclError:
                pass
            control[clave] = None

    def detener_todo():
        """
        Descripcion:
            Detiene el proceso asociado a detener todo.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        control["combate_local_activo"] = False
        for clave in ("after_polling", "after_timer", "after_combate", "after_volver", "after_ocultar_resultado"):
            cancelar_after(clave)

    def cerrar_mapa(volver_a_play=False):
        """
        Descripcion:
            Cierra o libera los recursos asociados a cerrar mapa.
        
        Entradas:
            volver_a_play (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if control["cerrando"]:
            return
        control["cerrando"] = True
        detener_todo()
        if adaptador_red is not None:
            try:
                adaptador_red.cerrar()
            except Exception:
                pass
        elif cliente_red is not None:
            try:
                cliente_red.cerrar()
            except Exception:
                pass

        if servidor_local is not None:
            try:
                if isinstance(servidor_local, dict):
                    instancia_servidor = servidor_local.get("instancia")
                    if instancia_servidor is not None:
                        instancia_servidor.detener()
                else:
                    servidor_local.detener()
            except Exception:
                pass
        try:
            if window_mapa.winfo_exists():
                window_mapa.destroy()
        except tk.TclError:
            pass
        if volver_a_play:
            GoPlay()

    def GoPlayR():
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoPlayR.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        cerrar_mapa(volver_a_play=True)

    def cerrar_ventana():
        """
        Descripcion:
            Cierra o libera los recursos asociados a cerrar ventana.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        cerrar_mapa()
        cerrar_todo()

    def escribir_evento(texto):
        """
        Descripcion:
            Ejecuta la logica correspondiente a escribir evento dentro
            del flujo del juego.
        
        Entradas:
            texto (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not texto or not ventana_activa():
            return
        try:
            caja_eventos.config(state="normal")
            caja_eventos.insert(tk.END, f"• {texto}\n")
            caja_eventos.see(tk.END)
            caja_eventos.config(state="disabled")
        except tk.TclError:
            control["cerrando"] = True

    # -----------------------------------------------------------------
    # Carga de imágenes
    # -----------------------------------------------------------------

    def buscar_archivo_por_nombre(carpeta, palabra):
        """
        Descripcion:
            Ejecuta la logica correspondiente a buscar archivo por
            nombre dentro del flujo del juego.
        
        Entradas:
            carpeta (object): Valor recibido por la funcion.
            palabra (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not os.path.isdir(carpeta):
            return None
        palabra = palabra.lower()
        for raiz, _, archivos in os.walk(carpeta):
            for archivo in archivos:
                if archivo.lower().endswith((".png", ".gif")) and palabra in archivo.lower():
                    return os.path.join(raiz, archivo)
        return None

    def buscar_primer_png(carpeta):
        """
        Descripcion:
            Ejecuta la logica correspondiente a buscar primer png dentro
            del flujo del juego.
        
        Entradas:
            carpeta (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not os.path.isdir(carpeta):
            return None
        for raiz, _, archivos in os.walk(carpeta):
            for archivo in archivos:
                if archivo.lower().endswith((".png", ".gif")):
                    return os.path.join(raiz, archivo)
        return None

    def cargar_photoimage(ruta, ancho_max=None, alto_max=None, ajustar_exactamente=False):
        """
        Descripcion:
            Ejecuta la logica correspondiente a cargar photoimage dentro
            del flujo del juego.
        
        Entradas:
            ruta (object): Valor recibido por la funcion.
            ancho_max (object): Valor recibido por la funcion. Valor
            opcional.
            alto_max (object): Valor recibido por la funcion. Valor
            opcional.
            ajustar_exactamente (object): Valor recibido por la funcion.
            Valor opcional.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not ruta or not os.path.exists(ruta):
            return None

        if Image is not None and ImageTk is not None and ancho_max and alto_max:
            try:
                imagen_pil = Image.open(ruta).convert("RGBA")
                if ajustar_exactamente:
                    imagen_pil = ImageOps.fit(
                        imagen_pil,
                        (int(ancho_max), int(alto_max)),
                        method=Image.Resampling.LANCZOS,
                        centering=(0.5, 0.5),
                    )
                else:
                    imagen_pil.thumbnail(
                        (int(ancho_max), int(alto_max)),
                        Image.Resampling.LANCZOS,
                    )
                return ImageTk.PhotoImage(imagen_pil, master=window_mapa)
            except Exception:
                pass

        try:
            imagen = tk.PhotoImage(master=window_mapa, file=ruta)
            if ancho_max and alto_max:
                factor = max(
                    1,
                    int(math.ceil(max(imagen.width() / ancho_max, imagen.height() / alto_max))),
                )
                if factor > 1:
                    imagen = imagen.subsample(factor, factor)
            return imagen
        except tk.TclError:
            return None

    def obtener_carpeta_faccion(tipo, faccion):
        """
        Descripcion:
            Obtiene la informacion correspondiente a obtener carpeta
            faccion para que otras partes del programa puedan
            utilizarla.
        
        Entradas:
            tipo (object): Valor recibido por la funcion.
            faccion (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        base = os.path.join(RUTA_IMAGENES, tipo)
        candidatos = CARPETAS_FACCION.get(faccion, (faccion,))
        for candidato in candidatos:
            ruta = os.path.join(base, candidato)
            if os.path.isdir(ruta):
                return ruta
        if os.path.isdir(base):
            for carpeta in os.listdir(base):
                for candidato in candidatos:
                    if candidato.lower() in carpeta.lower():
                        return os.path.join(base, carpeta)
        return base

    def obtener_faccion_por_rol(rol):
        """
        Descripcion:
            Obtiene la informacion correspondiente a obtener faccion por
            rol para que otras partes del programa puedan utilizarla.
        
        Entradas:
            rol (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        datos_red = obtener_ultimos_datos_red()
        facciones = datos_red.get("facciones_lobby", {}) if isinstance(datos_red, dict) else {}

        if rol in facciones:
            return facciones[rol]

        if rol == "defensor":
            return faccion_defensor

        if rol == "atacante":
            return faccion_atacante

        return faccion_jugador

    def clave_unidad(unidad):
        """
        Descripcion:
            Ejecuta la logica correspondiente a clave unidad dentro del
            flujo del juego.
        
        Entradas:
            unidad (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        clave = unidad.get("clave") or ""
        if clave:
            return clave
        return CLAVE_UNIDAD_POR_NOMBRE.get(str(unidad.get("nombre", "")).lower(), "soldado")

    def clave_torre(torre):
        """
        Descripcion:
            Ejecuta la logica correspondiente a clave torre dentro del
            flujo del juego.
        
        Entradas:
            torre (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        clave = torre.get("clave") or ""
        if clave in ("normal", "pesada", "especial"):
            return clave
        return CLAVE_TORRE_POR_NOMBRE.get(str(torre.get("nombre", "")).lower(), "normal")

    def imagen_unidad(unidad):
        """
        Descripcion:
            Ejecuta la logica correspondiente a imagen unidad dentro del
            flujo del juego.
        
        Entradas:
            unidad (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        clave = clave_unidad(unidad)
        faccion = obtener_faccion_por_rol("atacante")
        llave = ("unidad", faccion, clave)
        if llave in imagenes:
            return imagenes[llave]

        carpeta_faccion = obtener_carpeta_faccion("Soldados", faccion)
        carpetas_por_clave = {
            "soldado": ("Soldado base", "Soldado normal"),
            "rapido": ("Soldado rápido", "Soldado r#U00e1pido"),
            "tanque": ("Soldado tanque",),
        }
        ruta = None
        for nombre_carpeta in carpetas_por_clave.get(clave, ("Soldado base",)):
            ruta_carpeta = os.path.join(carpeta_faccion, nombre_carpeta)
            ruta = buscar_primer_png(ruta_carpeta)
            if ruta:
                break
        if ruta is None:
            ruta = buscar_primer_png(carpeta_faccion)
        imagenes[llave] = cargar_photoimage(ruta, 52, 36)
        return imagenes[llave]

    def imagen_torre(torre):
        """
        Descripcion:
            Ejecuta la logica correspondiente a imagen torre dentro del
            flujo del juego.
        
        Entradas:
            torre (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        clave = clave_torre(torre)
        faccion = obtener_faccion_por_rol("defensor")
        llave = ("torre", faccion, clave)
        if llave in imagenes:
            return imagenes[llave]

        carpeta_faccion = obtener_carpeta_faccion("estructuras", faccion)
        codigo = CODIGO_FACCION.get(faccion, "")
        ruta = None
        palabras = [clave]
        if codigo:
            palabras.insert(0, f"torre_{codigo}_{clave}")
        for palabra in palabras:
            ruta = buscar_archivo_por_nombre(carpeta_faccion, palabra)
            if ruta:
                break
        if ruta is None:
            ruta = buscar_primer_png(carpeta_faccion)
        imagenes[llave] = cargar_photoimage(ruta, 58, 42)
        return imagenes[llave]

    def imagen_base():
        """
        Descripcion:
            Ejecuta la logica correspondiente a imagen base dentro del
            flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        faccion = obtener_faccion_por_rol("defensor")
        llave = ("base", faccion)
        if llave in imagenes:
            return imagenes[llave]
        carpeta_faccion = obtener_carpeta_faccion("estructuras", faccion)
        ruta = buscar_archivo_por_nombre(carpeta_faccion, "principal")
        imagenes[llave] = cargar_photoimage(ruta, 80, 44)
        return imagenes[llave]

    def imagen_muro():
        """
        Descripcion:
            Ejecuta la logica correspondiente a imagen muro dentro del
            flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        llave = ("muro",)
        if llave not in imagenes:
            ruta = buscar_primer_png(os.path.join(RUTA_IMAGENES, "muros"))
            imagenes[llave] = cargar_photoimage(ruta, 70, 28)
        return imagenes[llave]

    def imagen_fondo_mapa():
        """
        Descripcion:
            Ejecuta la logica correspondiente a imagen fondo mapa dentro
            del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        llave = ("fondo_mapa",)
        if llave in imagenes:
            return imagenes[llave]
        ruta = buscar_archivo_por_nombre(RUTA_IMAGENES, "mapa")
        if ruta is None:
            ruta = os.path.join(RUTA_IMAGENES, "Fondo.png")
        imagenes[llave] = cargar_photoimage(
            ruta,
            ANCHO_TABLERO,
            ALTO_TABLERO,
            ajustar_exactamente=True,
        )
        return imagenes[llave]

    # -----------------------------------------------------------------
    # Estado red/local
    # -----------------------------------------------------------------

    def obtener_ultimos_datos_red():
        """
        Descripcion:
            Obtiene la informacion correspondiente a obtener ultimos
            datos red para que otras partes del programa puedan
            utilizarla.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
        """
        if not modo_red:
            return {}
        try:
            mensajes = list(cliente_red.ultimos_mensajes)
        except Exception:
            return {}
        for mensaje in reversed(mensajes):
            datos = mensaje.get("datos")
            if isinstance(datos, dict):
                return datos
        return {}

    def _obtener_estado():
        """
        Descripcion:
            Ejecuta la logica correspondiente a  obtener estado dentro
            del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        if modo_red:
            estado = cliente_red.obtener_ultimo_estado_local()
            return estado if estado else {}
        return app.obtener_estado_partida()

    def _accion_comprar_torre(clave, fila, columna):
        """
        Descripcion:
            Ejecuta la logica correspondiente a  accion comprar torre
            dentro del flujo del juego.
        
        Entradas:
            clave (object): Valor recibido por la funcion.
            fila (object): Valor recibido por la funcion.
            columna (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        if modo_red:
            return cliente_red.comprar_torre(clave, fila, columna)
        return app.comprar_torre(clave, fila, columna)

    def _accion_comprar_muro(fila, columna):
        """
        Descripcion:
            Ejecuta la logica correspondiente a  accion comprar muro
            dentro del flujo del juego.
        
        Entradas:
            fila (object): Valor recibido por la funcion.
            columna (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        if modo_red:
            return cliente_red.comprar_muro(fila, columna)
        return app.comprar_muro(fila, columna)

    def _accion_comprar_unidad(clave, fila, columna):
        """
        Descripcion:
            Ejecuta la logica correspondiente a  accion comprar unidad
            dentro del flujo del juego.
        
        Entradas:
            clave (object): Valor recibido por la funcion.
            fila (object): Valor recibido por la funcion.
            columna (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        if modo_red:
            return cliente_red.comprar_unidad(clave, fila, columna)
        return app.comprar_unidad(clave, fila, columna)

    def _accion_iniciar_combate(numero_ronda):
        """
        Descripcion:
            Ejecuta la logica correspondiente a  accion iniciar combate
            dentro del flujo del juego.
        
        Entradas:
            numero_ronda (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        if modo_red:
            return cliente_red.iniciar_combate()
        return app.resolver_preparacion_agotada()

    def _accion_usar_habilidad_especial():
        """
        Descripcion:
            Ejecuta la logica correspondiente a  accion usar habilidad
            especial dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        if modo_red:
            return cliente_red.usar_habilidad_especial()
        return app.usar_habilidad_especial(rol_jugador)

    # -----------------------------------------------------------------
    # Marcador, temporizador y resultados
    # -----------------------------------------------------------------

    def actualizar_marcador(estado=None):
        """
        Descripcion:
            Actualiza la informacion o el componente asociado a
            actualizar marcador.
        
        Entradas:
            estado (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        estado = estado or _obtener_estado()
        ronda = estado.get("numero_ronda", estado_ui["ronda"])
        vic_def = estado.get("rondas_ganadas_defensor", estado_ui["victorias_defensor"])
        vic_ata = estado.get("rondas_ganadas_atacante", estado_ui["victorias_atacante"])
        para_ganar = estado.get("rondas_para_ganar_partida", RONDAS_PARA_GANAR)
        etiqueta_marcador.config(
            text=f"Ronda {ronda} | Defensor {vic_def} - {vic_ata} Atacante | gana el primero en {para_ganar}"
        )

    def actualizar_temporizador_label():
        """
        Descripcion:
            Actualiza la informacion o el componente asociado a
            actualizar temporizador label.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        fase = estado_ui["fase"]
        if estado_ui["partida_finalizada"]:
            etiqueta_temporizador.config(text="Partida finalizada", fg="#444444")
        elif fase == FASE_COMBATE:
            etiqueta_temporizador.config(text="⚔ Combate en tiempo real", fg="#1565c0")
        elif fase == FASE_ATAQUE_ATACANTE:
            seg = estado_ui["segundos"]
            etiqueta_temporizador.config(
                text=f"⏱ Preparación atacante: {seg}s",
                fg="#c45100" if seg <= 5 else "#b05a00",
            )
        elif fase == FASE_CONSTRUCCION_DEFENSOR:
            seg = estado_ui["segundos"]
            etiqueta_temporizador.config(
                text=f"⏱ Preparación defensor: {seg}s",
                fg="#c45100" if seg <= 5 else "#173a59",
            )
        else:
            etiqueta_temporizador.config(text="Preparación", fg="#333333")

    def mostrar_caja_resultado(ganador_ronda, partida_finalizada=False, ganador_partida=None):
        """
        Descripcion:
            Muestra o consulta el estado visible relacionado con mostrar
            caja resultado.
        
        Entradas:
            ganador_ronda (object): Valor recibido por la funcion.
            partida_finalizada (object): Valor recibido por la funcion.
            Valor opcional.
            ganador_partida (object): Valor recibido por la funcion.
            Valor opcional.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not ventana_activa():
            return

        gano_ronda = ganador_ronda == rol_jugador
        if partida_finalizada:
            gano_partida = ganador_partida == rol_jugador
            texto = "¡GANASTE LA PARTIDA!" if gano_partida else "PERDISTE LA PARTIDA"
            detalle = "Se actualizó el historial del ganador."
            color = "#1b5e20" if gano_partida else "#b71c1c"
            titulo = "Resultado de partida"
        else:
            texto = "¡GANASTE LA RONDA!" if gano_ronda else "PERDISTE LA RONDA"
            detalle = f"Ronda ganada por el {ganador_ronda}."
            color = "#2e7d32" if gano_ronda else "#c62828"
            titulo = "Resultado de ronda"

        etiqueta_resultado.config(text=texto, bg=color, fg="white")
        etiqueta_resultado.place(relx=0.5, y=350, anchor="center")
        etiqueta_resultado.lift()
        escribir_evento(detalle)
        try:
            messagebox.showinfo(titulo, f"{texto}\n{detalle}", parent=window_mapa)
        except tk.TclError:
            pass

        if partida_finalizada:
            escribir_evento("Volviendo a la sala. La victoria quedó guardada en perfil y puntajes.")
            boton_turno.config(text="Partida terminada", bg="#9e9e9e", state="disabled")
            control["after_volver"] = window_mapa.after(2500, lambda: cerrar_mapa(volver_a_play=True))
        else:
            def ocultar_resultado():
                """
                Descripcion:
                    Ejecuta la logica correspondiente a ocultar
                    resultado dentro del flujo del juego.
                
                Entradas:
                    Ninguna.
                
                Salidas:
                    None: Ejecuta la accion y puede modificar el estado
                    interno, la interfaz o los datos relacionados.
                
                Restricciones:
                    - Requiere que los widgets, ventanas o callbacks
                    usados por la interfaz existan antes de ejecutarse.
                """
                if ventana_activa():
                    etiqueta_resultado.place_forget()
                    etiqueta_resultado.config(text="", bg=COLOR_PANEL, fg=COLOR_PANEL)
            control["after_ocultar_resultado"] = window_mapa.after(1300, ocultar_resultado)

    def detectar_resultado(estado):
        """
        Descripcion:
            Ejecuta la logica correspondiente a detectar resultado
            dentro del flujo del juego.
        
        Entradas:
            estado (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        vic_def = int(estado.get("rondas_ganadas_defensor", 0))
        vic_ata = int(estado.get("rondas_ganadas_atacante", 0))
        puntuacion = (vic_def, vic_ata)
        anterior = estado_ui["puntuacion_anterior"]
        ganador = estado.get("rol_ganador_ultima_ronda")

        if sum(puntuacion) > sum(anterior) and ganador in ("defensor", "atacante"):
            llave = (vic_def, vic_ata, ganador, bool(estado.get("partida_finalizada", False)))
            if llave not in estado_ui["resultados_mostrados"]:
                estado_ui["resultados_mostrados"].add(llave)
                mostrar_caja_resultado(
                    ganador,
                    partida_finalizada=bool(estado.get("partida_finalizada", False)),
                    ganador_partida=estado.get("rol_ganador_partida"),
                )

        estado_ui["puntuacion_anterior"] = puntuacion

    def sincronizar_fase_y_temporizador(estado):
        """
        Descripcion:
            Unico punto que decide en que fase visual esta la partida y
            cuantos segundos de preparación quedan. Usa siempre el campo
            "segundos_restantes_preparacion" que calcula el backend (la
            clase Partida, ya sea local o a traves del servidor), nunca
            un contador propio de la interfaz. Esto evita que el reloj
            del defensor y el del atacante se vean distintos entre los
            dos dispositivos.
        
        Entradas:
            estado (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        ronda = int(estado.get("numero_ronda", 1))
        fase_logica = estado.get("fase_ronda", FASE_ATAQUE_ATACANTE)
        partida_finalizada = bool(estado.get("partida_finalizada", False))

        estado_ui["partida_finalizada"] = partida_finalizada
        estado_ui["ronda"] = ronda
        estado_ui["victorias_defensor"] = int(estado.get("rondas_ganadas_defensor", 0))
        estado_ui["victorias_atacante"] = int(estado.get("rondas_ganadas_atacante", 0))

        if partida_finalizada:
            estado_ui["fase"] = "finalizada"
            actualizar_temporizador_label()
            return

        if fase_logica == FASE_COMBATE:
            if estado_ui["fase"] != FASE_COMBATE:
                escribir_evento("Inicia el combate. Ambos jugadores pueden seguir comprando.")
            estado_ui["fase"] = FASE_COMBATE
            actualizar_temporizador_label()
            if not modo_red and not control["combate_local_activo"]:
                iniciar_combate_local()
            return

        cambio_de_fase = estado_ui["fase"] != fase_logica
        estado_ui["fase"] = fase_logica
        segundos = estado.get("segundos_restantes_preparacion")
        if segundos is None:
            segundos = TIEMPO_PREPARACION_SEGUNDOS
        segundos_int = int(segundos)

        # Solo sincronizamos el contador si cambió la fase o hay un desfase grande (>2s)
        # Así el reloj local puede hacer tick sin que cada polling lo reinicie
        if cambio_de_fase or abs(estado_ui["segundos"] - segundos_int) > 2:
            estado_ui["segundos"] = segundos_int

        if cambio_de_fase and fase_logica == FASE_CONSTRUCCION_DEFENSOR:
            escribir_evento("El atacante quedó bloqueado. Ahora el defensor coloca sus defensas.")

        actualizar_temporizador_label()

        # Solo iniciamos/reiniciamos el reloj cuando cambia la fase,
        # no en cada ciclo de polling, para que el tick fluya normalmente
        if cambio_de_fase or control.get("after_timer") is None:
            iniciar_reloj_preparacion()

    def iniciar_reloj_preparacion():
        """
        Descripcion:
            Inicia el proceso asociado a iniciar reloj preparacion.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        cancelar_after("after_timer")
        control["after_timer"] = window_mapa.after(1000, tick_reloj_preparacion)

    def tick_reloj_preparacion():
        """
        Descripcion:
            Ejecuta la logica correspondiente a tick reloj preparacion
            dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not ventana_activa() or estado_ui["partida_finalizada"]:
            return
        if estado_ui["fase"] not in (FASE_ATAQUE_ATACANTE, FASE_CONSTRUCCION_DEFENSOR):
            return

        if estado_ui["segundos"] > 0:
            estado_ui["segundos"] -= 1
        actualizar_temporizador_label()

        if estado_ui["segundos"] <= 0:
            if not modo_red:
                # En modo local no hay servidor avanzando fases solo: lo
                # hace esta misma interfaz al llegar a 0.
                _, mensaje = app.resolver_preparacion_agotada()
                escribir_evento(mensaje)
                actualizar_vista()
            else:
                # En red el servidor avanza la fase con su propio reloj.
                # Pedimos el estado actualizado para sincronizar.
                cliente_red.obtener_estado()
                actualizar_vista()
            control["after_timer"] = window_mapa.after(500, tick_reloj_preparacion)
            return

        control["after_timer"] = window_mapa.after(1000, tick_reloj_preparacion)

    # -----------------------------------------------------------------
    # Catálogo y compra
    # -----------------------------------------------------------------

    def obtener_catalogo_compras():
        """
        Descripcion:
            Obtiene la informacion correspondiente a obtener catalogo
            compras para que otras partes del programa puedan
            utilizarla.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if rol_jugador == "atacante":
            return [{"tipo": "unidad", **unidad} for unidad in app.obtener_catalogo_unidades()]
        compras = [{"tipo": "torre", **torre} for torre in app.obtener_catalogo_torres()]
        compras.append({
            "tipo": "muro",
            "clave": "muro",
            "nombre": "Muro",
            "costo": 60,
            "vida": 220,
            "dano": 0,
            "alcance": 0,
            "habilidad": "bloqueo",
        })
        return compras

    def seleccionar_compra(compra):
        """
        Descripcion:
            Registra la seleccion correspondiente a seleccionar compra.
        
        Entradas:
            compra (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        seleccion_actual["tipo"] = compra["tipo"]
        seleccion_actual["clave"] = compra["clave"]
        seleccion_actual["nombre"] = compra["nombre"]
        if compra["tipo"] == "muro":
            detalle = f"❤{compra['vida']}"
        else:
            detalle = f"❤{compra['vida']}  ⚔{compra['dano']}"
        etiqueta_seleccion.config(text=f"Seleccionado: {compra['nombre']} ({detalle}) — ${compra['costo']}")
        for boton, compra_boton in botones_compra:
            boton.config(relief="sunken" if compra_boton is compra else "raised")

    def posicion_permitida_por_rol(fila, columna):
        """
        Descripcion:
            Ejecuta la logica correspondiente a posicion permitida por
            rol dentro del flujo del juego.
        
        Entradas:
            fila (object): Valor recibido por la funcion.
            columna (object): Valor recibido por la funcion.
        
        Salidas:
            tuple: Conjunto de valores resultantes de la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if fila == FILA_BASE:
            return False, "La base no se puede ocupar."
        if rol_jugador == "defensor" and fila not in FILAS_DEFENSOR:
            return False, "El defensor solo coloca defensas en la zona azul."
        if rol_jugador == "atacante" and fila not in FILAS_ATACANTE:
            return False, "El atacante solo coloca tropas en la zona naranja."
        return True, "Posición válida."

    def convertir_click_a_casilla(evento):
        """
        Descripcion:
            Ejecuta la logica correspondiente a convertir click a
            casilla dentro del flujo del juego.
        
        Entradas:
            evento (object): Valor recibido por la funcion.
        
        Salidas:
            tuple: Conjunto de valores resultantes de la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        columna = evento.x // ANCHO_CELDA
        fila = evento.y // ALTO_CELDA
        if fila < 0 or fila >= FILAS_TABLERO or columna < 0 or columna >= COLUMNAS_TABLERO:
            return None, None
        return fila, columna

    def datos_faccion_por_rol(rol):
        """
        Descripcion:
            Ejecuta la logica correspondiente a datos faccion por rol
            dentro del flujo del juego.
        
        Entradas:
            rol (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        nombre_faccion = faccion_defensor if rol == "defensor" else faccion_atacante
        return facciones_por_nombre.get(nombre_faccion, {})

    def color_proyectil(nombre_torre, rol="defensor"):
        """
        Descripcion:
            Ejecuta la logica correspondiente a color proyectil dentro
            del flujo del juego.
        
        Entradas:
            nombre_torre (object): Valor recibido por la funcion.
            rol (object): Valor recibido por la funcion. Valor opcional.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        datos_faccion = datos_faccion_por_rol(rol)
        color_base = datos_faccion.get("color_proyectil")
        if color_base:
            return color_base
        nombre = nombre_torre.lower()
        if "cañon" in nombre or "canon" in nombre:
            return "#ff7a00"
        if "hielo" in nombre:
            return "#00bcd4"
        if "soporte" in nombre:
            return "#9c27b0"
        return "#f2c200"

    def cargar_imagen_mapa(ruta, ancho_max=58, alto_max=34):
        """
        Descripcion:
            Ejecuta la logica correspondiente a cargar imagen mapa
            dentro del flujo del juego.
        
        Entradas:
            ruta (object): Valor recibido por la funcion.
            ancho_max (object): Valor recibido por la funcion. Valor
            opcional.
            alto_max (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not ruta or not os.path.exists(ruta):
            return None
        clave = (ruta, ancho_max, alto_max)
        if clave in imagenes_mapa:
            return imagenes_mapa[clave]
        imagen = tk.PhotoImage(master=window_mapa, file=ruta)
        factor = max(1, int(max(imagen.width() / ancho_max, imagen.height() / alto_max)))
        if factor > 1:
            imagen = imagen.subsample(factor, factor)
        imagenes_mapa[clave] = imagen
        return imagen

    def ruta_torre_faccion(nombre_torre):
        """
        Descripcion:
            Ejecuta la logica correspondiente a ruta torre faccion
            dentro del flujo del juego.
        
        Entradas:
            nombre_torre (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        nombre = nombre_torre.lower()
        datos_faccion = datos_faccion_por_rol("defensor")
        if "pesada" in nombre or "cañon" in nombre or "canon" in nombre:
            return datos_faccion.get("torre_pesada")
        if "especial" in nombre or "hielo" in nombre or "soporte" in nombre:
            return datos_faccion.get("torre_especial")
        return datos_faccion.get("torre_normal")

    def ruta_unidad_faccion(nombre_unidad):
        """
        Descripcion:
            Ejecuta la logica correspondiente a ruta unidad faccion
            dentro del flujo del juego.
        
        Entradas:
            nombre_unidad (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        nombre = nombre_unidad.lower()
        datos_faccion = datos_faccion_por_rol("atacante")
        if "tanque" in nombre or "pesad" in nombre or "escudero" in nombre or "demoledor" in nombre:
            return datos_faccion.get("soldado_tanque")
        if "rap" in nombre or "ráp" in nombre or "explorador" in nombre:
            return datos_faccion.get("soldado_rapido")
        return datos_faccion.get("soldado_base")

    def centro_casilla(fila, columna):
        """
        Descripcion:
            Ejecuta la logica correspondiente a centro casilla dentro
            del flujo del juego.
        
        Entradas:
            fila (object): Valor recibido por la funcion.
            columna (object): Valor recibido por la funcion.
        
        Salidas:
            tuple: Conjunto de valores resultantes de la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        return (
            columna * ANCHO_CELDA + ANCHO_CELDA // 2,
            fila * ALTO_CELDA + ALTO_CELDA // 2,
        )

    def distancia(fila_a, columna_a, fila_b, columna_b):
        """
        Descripcion:
            Ejecuta la logica correspondiente a distancia dentro del
            flujo del juego.
        
        Entradas:
            fila_a (object): Valor recibido por la funcion.
            columna_a (object): Valor recibido por la funcion.
            fila_b (object): Valor recibido por la funcion.
            columna_b (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        return abs(fila_a - fila_b) + abs(columna_a - columna_b)

    def animar_proyectiles(estado):
        """
        Descripcion:
            Ejecuta la logica correspondiente a animar proyectiles
            dentro del flujo del juego.
        
        Entradas:
            estado (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not mostrar_proyectiles_activos() or not ventana_activa():
            return
        proyectiles = []
        for torre in estado.get("torres", []):
            objetivo = None
            for unidad in estado.get("unidades", []):
                if distancia(torre["fila"], torre["columna"], unidad["fila"], unidad["columna"]) <= torre.get("alcance", 0):
                    objetivo = unidad
                    break
            if objetivo is not None:
                x1, y1 = centro_casilla(torre["fila"], torre["columna"])
                x2, y2 = centro_casilla(objetivo["fila"], objetivo["columna"])
                color = color_proyectil(torre["nombre"], "defensor")
                proyectiles.append(cuadro_mapa.create_line(x1, y1, x2, y2, fill="#111111", width=12, arrow=tk.LAST))
                proyectiles.append(cuadro_mapa.create_line(x1, y1, x2, y2, fill="#ffffff", width=8, arrow=tk.LAST))
                proyectiles.append(cuadro_mapa.create_line(x1, y1, x2, y2, fill=color, width=5, arrow=tk.LAST))
                proyectiles.append(cuadro_mapa.create_oval(x2 - 11, y2 - 11, x2 + 11, y2 + 11, fill=color, outline="#111111", width=3))
                proyectiles.append(cuadro_mapa.create_oval(x2 - 5, y2 - 5, x2 + 5, y2 + 5, fill="#ffffff", outline=color, width=2))

        for unidad in estado.get("unidades", []):
            objetivo = next(
                (torre for torre in estado.get("torres", []) if torre["fila"] == unidad["fila"] - 1 and torre["columna"] == unidad["columna"]),
                None,
            )
            if objetivo is not None:
                x1, y1 = centro_casilla(unidad["fila"], unidad["columna"])
                x2, y2 = centro_casilla(objetivo["fila"], objetivo["columna"])
                color = color_proyectil("unidad", "atacante")
                proyectiles.append(cuadro_mapa.create_line(x1, y1, x2, y2, fill="#111111", width=10, dash=(8, 4)))
                proyectiles.append(cuadro_mapa.create_line(x1, y1, x2, y2, fill="#ffffff", width=7, dash=(8, 4)))
                proyectiles.append(cuadro_mapa.create_line(x1, y1, x2, y2, fill=color, width=4, dash=(8, 4)))

        if proyectiles:
            def borrar_proyectiles():
                """
                Descripcion:
                    Ejecuta la logica correspondiente a borrar
                    proyectiles dentro del flujo del juego.
                
                Entradas:
                    Ninguna.
                
                Salidas:
                    None: Ejecuta la accion y puede modificar el estado
                    interno, la interfaz o los datos relacionados.
                
                Restricciones:
                    - Requiere que los widgets, ventanas o callbacks
                    usados por la interfaz existan antes de ejecutarse.
                """
                if not ventana_activa():
                    return
                try:
                    for item in proyectiles:
                        cuadro_mapa.delete(item)
                except tk.TclError:
                    control["cerrando"] = True

            window_mapa.after(650, borrar_proyectiles)

    DURACION_DESTELLO_HABILIDAD = 0.15
    DURACION_MARCO_HABILIDAD = 3.2
    DURACION_TOTAL_HABILIDAD = 4.4  # vs. 0.65s-1s de un proyectil normal
    TAG_EFECTO_HABILIDAD = "efecto_habilidad_especial"

    def animar_habilidad_especial(rol_que_dispara, info_habilidad):
        """
        Descripcion:
            Activa el efecto visual de la habilidad especial sobre el
            tablero, claramente distinto de un disparo normal de torre o
            unidad, y registra el momento del disparo para poder mostrar
            después "hace cuántos segundos" se usó. El dibujo en sí lo
            hace _redibujar_efecto_habilidad_si_activo(), que se llama
            en cada actualizar_vista() para sobrevivir a que
            dibujar_zonas() borre todo el canvas en cada refresco
            (polling/combate).
        
        Entradas:
            rol_que_dispara (object): Valor recibido por la funcion.
            info_habilidad (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        momento_disparo[rol_que_dispara] = time.monotonic()
        efecto_habilidad_activo["rol"] = rol_que_dispara
        efecto_habilidad_activo["info"] = info_habilidad
        efecto_habilidad_activo["inicio"] = time.monotonic()
        efecto_habilidad_activo["duracion_total"] = DURACION_TOTAL_HABILIDAD
        _redibujar_efecto_habilidad_si_activo()
        # Sigue revisando el efecto incluso si nada más vuelve a llamar
        # actualizar_vista() durante un rato (por ejemplo, en preparación
        # sin polling de red), para que el marco parpadee y se borre solo.
        _tick_efecto_habilidad()

    def _tick_efecto_habilidad():
        """
        Descripcion:
            Ejecuta la logica correspondiente a  tick efecto habilidad
            dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        if not ventana_activa():
            return
        inicio = efecto_habilidad_activo["inicio"]
        duracion_total = efecto_habilidad_activo["duracion_total"]
        if inicio is None or duracion_total is None:
            return
        _redibujar_efecto_habilidad_si_activo()
        transcurrido = time.monotonic() - inicio
        if transcurrido < duracion_total + 0.3:
            window_mapa.after(180, _tick_efecto_habilidad)

    def _redibujar_efecto_habilidad_si_activo():
        """
        Descripcion:
            Vuelve a dibujar el efecto de habilidad especial sobre el
            canvas si todavía está dentro de su ventana de tiempo. Se
            debe llamar después de cualquier
            dibujar_zonas()/delete("all") para que la animación no se
            pierda en el siguiente refresco de red o de combate local.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Requiere una conexion, sala o mensaje valido cuando la
            operacion dependa de la red.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        if cuadro_mapa is None or not ventana_activa():
            return
        try:
            cuadro_mapa.delete(TAG_EFECTO_HABILIDAD)
        except tk.TclError:
            control["cerrando"] = True
            return

        rol_que_dispara = efecto_habilidad_activo["rol"]
        info_habilidad = efecto_habilidad_activo["info"]
        inicio = efecto_habilidad_activo["inicio"]
        if rol_que_dispara is None or info_habilidad is None or inicio is None:
            return

        transcurrido = time.monotonic() - inicio
        if transcurrido >= efecto_habilidad_activo["duracion_total"]:
            efecto_habilidad_activo["rol"] = None
            efecto_habilidad_activo["info"] = None
            efecto_habilidad_activo["inicio"] = None
            return

        color = info_habilidad.get("color", "#999999")
        tipo_efecto = info_habilidad.get("tipo_efecto", "generico")
        filas_de_alcance = info_habilidad.get("filas_de_alcance", 3)
        nombre_habilidad = info_habilidad.get("nombre", "Habilidad especial")

        if rol_que_dispara == "defensor":
            fila_origen = 0
            filas_objetivo = list(range(8, min(8 + filas_de_alcance, 11)))
        else:
            fila_origen = 10
            filas_objetivo = list(range(max(1, 7 - filas_de_alcance + 1), 8))

        columna_origen = COLUMNAS_TABLERO // 2
        x_origen, y_origen = centro_casilla(fila_origen, columna_origen)

        etiquetas = (TAG_EFECTO_HABILIDAD,)

        # --- Etapa 1 (primeros instantes): destello blanco de aviso ---
        if transcurrido < DURACION_DESTELLO_HABILIDAD:
            cuadro_mapa.create_rectangle(
                0, 0, ANCHO_TABLERO, ALTO_TABLERO,
                fill="#ffffff", outline="", stipple="gray25", tags=etiquetas,
            )

        # --- Marco grueso de color alrededor de TODO el tablero ---
        # Parpadea durante la mayor parte del efecto. Esto es exclusivo
        # de las habilidades especiales: ningún proyectil normal de
        # torre/unidad dibuja un marco así.
        mostrar_marco = (
            transcurrido < DURACION_MARCO_HABILIDAD
            and int(transcurrido / 0.22) % 2 == 0
        )
        if mostrar_marco:
            grosor_marco = 10
            cuadro_mapa.create_rectangle(
                grosor_marco // 2, grosor_marco // 2,
                ANCHO_TABLERO - grosor_marco // 2, ALTO_TABLERO - grosor_marco // 2,
                outline=color, width=grosor_marco, tags=etiquetas,
            )
            cuadro_mapa.create_rectangle(
                grosor_marco // 2 + 6, grosor_marco // 2 + 6,
                ANCHO_TABLERO - grosor_marco // 2 - 6, ALTO_TABLERO - grosor_marco // 2 - 6,
                outline="#ffffff", width=3, tags=etiquetas,
            )

        # Los efectos de impacto (overlay + explosiones + texto) solo se
        # muestran en la primera parte de la animación; el resto del
        # tiempo solo queda el marco parpadeante para avisar que hubo
        # un ataque especial reciente sin tapar el tablero.
        if transcurrido < DURACION_MARCO_HABILIDAD * 0.7:
            # Overlay de zona afectada (rectángulo coloreado semitransparente)
            if filas_objetivo:
                fila_min = min(filas_objetivo)
                fila_max = max(filas_objetivo)
                y_top = fila_min * ALTO_CELDA
                y_bot = (fila_max + 1) * ALTO_CELDA
                cuadro_mapa.create_rectangle(
                    0, y_top, ANCHO_TABLERO, y_bot,
                    fill=color, outline=color, width=4, stipple="gray50", tags=etiquetas,
                )

            # Efectos por casilla
            for fila_obj in filas_objetivo:
                for columna in range(COLUMNAS_TABLERO):
                    x_destino, y_destino = centro_casilla(fila_obj, columna)

                    if tipo_efecto == "gas":
                        radio = 26
                        cuadro_mapa.create_oval(
                            x_destino - radio, y_destino - radio // 2,
                            x_destino + radio, y_destino + radio // 2,
                            fill=color, outline="#004400", width=2, stipple="gray50", tags=etiquetas,
                        )
                    elif tipo_efecto == "flechas":
                        cuadro_mapa.create_line(
                            x_origen, y_origen, x_destino, y_destino,
                            fill=color, width=3, arrow=tk.LAST, tags=etiquetas,
                        )
                    elif tipo_efecto == "granadas":
                        medio_x = (x_origen + x_destino) / 2
                        medio_y = min(y_origen, y_destino) - 40
                        cuadro_mapa.create_line(
                            x_origen, y_origen, medio_x, medio_y, x_destino, y_destino,
                            fill=color, width=3, smooth=True, tags=etiquetas,
                        )
                        cuadro_mapa.create_oval(
                            x_destino - 14, y_destino - 14, x_destino + 14, y_destino + 14,
                            fill="#ff7a00", outline=color, width=2, tags=etiquetas,
                        )
                        cuadro_mapa.create_oval(
                            x_destino - 6, y_destino - 6, x_destino + 6, y_destino + 6,
                            fill="#ffee00", outline="", tags=etiquetas,
                        )
                    else:
                        # artilleria, mortero, fuego y generico
                        radio = 18
                        cuadro_mapa.create_oval(
                            x_destino - radio, y_destino - radio,
                            x_destino + radio, y_destino + radio,
                            fill=color, outline="#111111", width=2, tags=etiquetas,
                        )
                        cuadro_mapa.create_oval(
                            x_destino - radio // 2, y_destino - radio // 2,
                            x_destino + radio // 2, y_destino + radio // 2,
                            fill="#ffffff", outline="", tags=etiquetas,
                        )

            # Texto central grande con nombre de la habilidad y halo de fondo
            cx = ANCHO_TABLERO // 2
            cy = ALTO_TABLERO // 2
            etiqueta_quien = "¡DEFENSOR!" if rol_que_dispara == "defensor" else "¡ATACANTE!"
            texto_completo = f"💥 {etiqueta_quien} usa {nombre_habilidad} 💥"
            cuadro_mapa.create_rectangle(
                cx - 230, cy - 34, cx + 230, cy + 34,
                fill="#000000", outline=color, width=3, stipple="gray50", tags=etiquetas,
            )
            cuadro_mapa.create_text(
                cx + 2, cy + 2, text=texto_completo,
                fill="#000000", font=("Arial", 18, "bold"), tags=etiquetas,
            )
            cuadro_mapa.create_text(
                cx, cy, text=texto_completo,
                fill=color, font=("Arial", 18, "bold"), tags=etiquetas,
            )

        # Asegura que el efecto quede por encima de torres/unidades/muros
        # recién redibujados por dibujar_zonas()/dibujar_estado().
        try:
            cuadro_mapa.tag_raise(TAG_EFECTO_HABILIDAD)
        except tk.TclError:
            control["cerrando"] = True

    def comprar_en_casilla(evento):
        """
        Descripcion:
            Ejecuta la logica correspondiente a comprar en casilla
            dentro del flujo del juego.
        
        Entradas:
            evento (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if estado_ui["partida_finalizada"]:
            return
        if seleccion_actual["clave"] is None:
            escribir_evento("Primero selecciona una compra del panel izquierdo.")
            return

        estado_actual = _obtener_estado()
        fase_actual = estado_actual.get("fase_ronda", estado_ui.get("fase"))

        # Ambos jugadores pueden colocar sus piezas en cualquier momento

        fila, columna = convertir_click_a_casilla(evento)
        if fila is None:
            return

        permitido, mensaje = posicion_permitida_por_rol(fila, columna)
        if not permitido:
            escribir_evento(mensaje)
            return

        tipo = seleccion_actual["tipo"]
        if tipo == "torre":
            exito, mensaje = _accion_comprar_torre(seleccion_actual["clave"], fila, columna)
        elif tipo == "muro":
            exito, mensaje = _accion_comprar_muro(fila, columna)
        else:
            exito, mensaje = _accion_comprar_unidad(seleccion_actual["clave"], fila, columna)

        escribir_evento(mensaje)

        if exito:
            # Refresco inmediato: la pieza aparece en pantalla de inmediato
            actualizar_vista()
            window_mapa.update_idletasks()   # fuerza el redibujado antes del siguiente evento
            if modo_red:
                cliente_red.obtener_estado()
                window_mapa.after(80, actualizar_vista)
    def nombre_fase_preparacion(estado):
        """
        Descripcion:
            Ejecuta la logica correspondiente a nombre fase preparacion
            dentro del flujo del juego.
        
        Entradas:
            estado (object): Valor recibido por la funcion.
        
        Salidas:
            str: Texto generado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        fase = estado.get("fase_ronda", "")
        if fase == FASE_ATAQUE_ATACANTE:
            return "Preparación atacante: coloca tropas"
        if fase == FASE_CONSTRUCCION_DEFENSOR:
            return "Preparación defensor: coloca defensas"
        if fase == FASE_COMBATE:
            return "Combate en tiempo real"
        return "Preparación"

    def alternar_combate_click():
        """
        Descripcion:
            Boton manual "Forzar combate": solo tiene efecto util
            durante las fases de preparacion (salta el tiempo restante).
            Durante el combate no hace nada porque el combate ya avanza
            solo, tanto en red (servidor) como en local (after de
            Tkinter).
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if estado_ui["partida_finalizada"]:
            return
        if estado_ui["fase"] == FASE_COMBATE:
            escribir_evento("El combate ya está en curso, avanza automáticamente.")
            return
        escribir_evento("Forzando fin de la preparación...")
        if not modo_red:
            _, mensaje = app.resolver_preparacion_agotada()
            escribir_evento(mensaje)
            actualizar_vista()
        else:
            cliente_red.iniciar_combate()
            window_mapa.after(150, lambda: (cliente_red.obtener_estado(), actualizar_vista()))

    def usar_habilidad_click():
        """
        Descripcion:
            Maneja el clic del boton de habilidad especial. Cada jugador
            solo tiene un boton, correspondiente a su propio rol; la
            facción (y por lo tanto el efecto, costo y daño) la
            determina la clase Partida según lo elegido en el lobby,
            nunca la interfaz.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if estado_ui["partida_finalizada"]:
            return

        estado_actual = _obtener_estado()
        info_habilidad = estado_actual.get(
            "habilidad_defensor" if rol_jugador == "defensor" else "habilidad_atacante",
            {},
        )

        exito, mensaje = _accion_usar_habilidad_especial()
        escribir_evento(mensaje)

        if exito:
            animar_habilidad_especial(rol_jugador, info_habilidad)
            actualizar_vista()
            if modo_red:
                window_mapa.after(150, lambda: (cliente_red.obtener_estado(), actualizar_vista()))

    def _formatear_hace_tiempo(segundos):
        """
        Descripcion:
            Convierte segundos transcurridos en un texto corto y
            legible.
        
        Entradas:
            segundos (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        if segundos is None:
            return "nunca usada"
        segundos = max(0, int(segundos))
        if segundos < 60:
            return f"hace {segundos}s"
        minutos = segundos // 60
        resto = segundos % 60
        return f"hace {minutos}m {resto}s"

    def _segundos_desde_ultimo_uso(rol):
        """
        Descripcion:
            Calcula cuanto tiempo ha pasado desde el ultimo disparo de
            la habilidad especial de ese rol. Prioriza el
            timestamp_disparo que llega del servidor/logica
            (time.time(), confiable incluso si el jugador entra a una
            partida ya en curso); si no hay ninguno en el estado
            todavia, usa el reloj local como respaldo.
        
        Entradas:
            rol (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        estado_actual = _obtener_estado()
        clave = "habilidad_defensor" if rol == "defensor" else "habilidad_atacante"
        info = estado_actual.get(clave, {})
        ts_servidor = info.get("timestamp_disparo")
        if ts_servidor is not None:
            return time.time() - ts_servidor
        ts_local = momento_disparo.get(rol)
        if ts_local is not None:
            return time.monotonic() - ts_local
        return None

    def actualizar_boton_habilidad():
        """
        Descripcion:
            Refresca el texto y el estado (habilitado/deshabilitado) del
            boton de habilidad especial con la informacion mas reciente
            del estado de la partida: nombre real de la habilidad de la
            facción del jugador, costo y segundos de enfriamiento
            restantes. El "hace cuántos segundos" de la última habilidad
            usada (propia y del rival) se muestra en la segunda línea
            del marcador superior, ver actualizar_panel_estado().
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if boton_habilidad is None:
            return

        estado_actual = _obtener_estado()
        info_habilidad = estado_actual.get(
            "habilidad_defensor" if rol_jugador == "defensor" else "habilidad_atacante",
            {},
        )
        if not info_habilidad:
            return

        nombre = info_habilidad.get("nombre", "Habilidad especial")
        nombre_corto = nombre if len(nombre) <= 16 else nombre[:14] + "…"
        costo = info_habilidad.get("costo", 0)
        cooldown = info_habilidad.get("segundos_restantes_cooldown", 0)
        disponible = info_habilidad.get("disponible", False)

        if cooldown > 0:
            texto = f"💥 {nombre_corto}\n⏳{cooldown}s"
        else:
            texto = f"💥 {nombre_corto}\n${costo}"

        boton_habilidad.config(
            text=texto,
            state="normal" if disponible else "disabled",
            bg="#ff8a65" if disponible else "#cccccc",
        )

    def dibujar_zonas():
        """
        Descripcion:
            Ejecuta la logica correspondiente a dibujar zonas dentro del
            flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        cuadro_mapa.delete("all")
        fondo = imagen_fondo_mapa()
        if fondo is not None:
            cuadro_mapa.create_image(0, 0, image=fondo, anchor="nw")

        for fila in range(FILAS_TABLERO):
            y1 = fila * ALTO_CELDA
            y2 = y1 + ALTO_CELDA
            if fila == FILA_BASE:
                color = COLOR_BASE
            elif fila in FILAS_DEFENSOR:
                color = COLOR_DEFENSA
            else:
                color = COLOR_ATAQUE
            cuadro_mapa.create_rectangle(0, y1, ANCHO_TABLERO, y2, fill=color, outline="", stipple="gray25")

        if mostrar_cuadricula_activa():
            for x in range(0, ANCHO_TABLERO + 1, ANCHO_CELDA):
                cuadro_mapa.create_line(x, 0, x, ALTO_TABLERO, fill="#cccccc")
            for y in range(0, ALTO_TABLERO + 1, ALTO_CELDA):
                cuadro_mapa.create_line(0, y, ANCHO_TABLERO, y, fill="#cccccc")

        sprite_base_defensor = cargar_imagen_mapa(datos_faccion_por_rol("defensor").get("estructura_base"), 110, 38)
        if sprite_base_defensor is not None:
            cuadro_mapa.create_image(ANCHO_TABLERO // 2, ALTO_CELDA // 2 + 3, image=sprite_base_defensor)
        cuadro_mapa.create_text(ANCHO_TABLERO // 2, ALTO_CELDA // 2, text="BASE DEFENSOR", font=("Arial", 12, "bold"), fill="#9a0000")
        cuadro_mapa.create_text(10, ALTO_CELDA * 4, text="Zona defensor", angle=90, anchor="w", fill="#005b96", font=("Arial", 10, "bold"))
        cuadro_mapa.create_text(10, ALTO_CELDA * 9, text="Zona atacante", angle=90, anchor="w", fill="#b05a00", font=("Arial", 10, "bold"))

    def dibujar_barra_vida(x, y, vida, vida_maxima, ancho=48):
        """
        Descripcion:
            Ejecuta la logica correspondiente a dibujar barra vida
            dentro del flujo del juego.
        
        Entradas:
            x (object): Valor recibido por la funcion.
            y (object): Valor recibido por la funcion.
            vida (object): Valor recibido por la funcion.
            vida_maxima (object): Valor recibido por la funcion.
            ancho (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        vida_maxima = max(1, int(vida_maxima))
        vida = max(0, int(vida))
        ancho_vida = int((vida / vida_maxima) * ancho)
        cuadro_mapa.create_rectangle(x - ancho // 2, y, x + ancho // 2, y + 6, fill="#ffcdd2", outline="#111111")
        cuadro_mapa.create_rectangle(x - ancho // 2, y, x - ancho // 2 + ancho_vida, y + 6, fill="#43a047", outline="")

    def dibujar_estado(estado):
        """
        Descripcion:
            Ejecuta la logica correspondiente a dibujar estado dentro
            del flujo del juego.
        
        Entradas:
            estado (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        vida_base = estado.get("vida_base", 0)
        vida_maxima_base = estado.get("vida_maxima_base", 1)
        ancho_vida = int((vida_base / max(1, vida_maxima_base)) * (ANCHO_TABLERO - 40))
        cuadro_mapa.create_rectangle(20, 6, ANCHO_TABLERO - 20, 16, fill="#ffcdd2", outline="black")
        cuadro_mapa.create_rectangle(20, 6, 20 + ancho_vida, 16, fill="#e53935", outline="")
        cuadro_mapa.create_text(ANCHO_TABLERO - 24, 26, text=f"Base {vida_base}/{vida_maxima_base}", anchor="e", font=("Arial", 9, "bold"), fill="#7f0000")

        for muro in estado.get("muros", []):
            x, y = centro_casilla(muro["fila"], muro["columna"])
            img = imagen_muro()
            if img is not None:
                cuadro_mapa.create_image(x, y, image=img)
            else:
                cuadro_mapa.create_rectangle(x - 32, y - 12, x + 32, y + 12, fill="#8d6e63", outline="black", width=2)
                cuadro_mapa.create_text(x, y, text="MURO", font=("Arial", 8, "bold"), fill="white")
            dibujar_barra_vida(x, y + 15, muro.get("vida", 0), muro.get("vida_maxima", 1))

        for torre in estado.get("torres", []):
            x, y = centro_casilla(torre["fila"], torre["columna"])
            imagen_torre = cargar_imagen_mapa(ruta_torre_faccion(torre["nombre"]))
            if imagen_torre is not None:
                cuadro_mapa.create_image(x, y, image=imagen_torre)
            else:
                color = color_proyectil(torre["nombre"], "defensor")
                cuadro_mapa.create_rectangle(x - 20, y - 18, x + 20, y + 18, fill=color, outline="black", width=2)
                cuadro_mapa.create_text(x, y - 3, text="T", font=("Arial", 14, "bold"), fill="black")
            cuadro_mapa.create_text(x, y + 15, text=str(torre["vida"]), font=("Arial", 8, "bold"), fill="black")

        for unidad in estado.get("unidades", []):
            x, y = centro_casilla(unidad["fila"], unidad["columna"])
            imagen_unidad = cargar_imagen_mapa(ruta_unidad_faccion(unidad["nombre"]))
            if imagen_unidad is not None:
                cuadro_mapa.create_image(x, y, image=imagen_unidad)
            else:
                cuadro_mapa.create_oval(x - 20, y - 17, x + 20, y + 17, fill="#ff7043", outline="black", width=2)
                cuadro_mapa.create_text(x, y - 3, text="U", font=("Arial", 14, "bold"), fill="white")
            cuadro_mapa.create_text(x, y + 15, text=str(unidad["vida"]), font=("Arial", 8, "bold"), fill="white")

    def actualizar_panel_estado(estado):
        """
        Descripcion:
            Actualiza la informacion o el componente asociado a
            actualizar panel estado.
        
        Entradas:
            estado (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        texto_habilidad_defensor = _formatear_hace_tiempo(_segundos_desde_ultimo_uso("defensor"))
        texto_habilidad_atacante = _formatear_hace_tiempo(_segundos_desde_ultimo_uso("atacante"))
        etiqueta_marcador.config(
            text=(
                f"Rol: {rol_jugador.upper()} | Fase: {estado.get('fase_ronda', 'preparación')} | Ronda {estado.get('numero_ronda', 1)} | "
                f"Base {estado.get('vida_base', 0)}/{estado.get('vida_maxima_base', 0)}\n"
                f"💥 Habilidad defensor: {texto_habilidad_defensor}   |   "
                f"💥 Habilidad atacante: {texto_habilidad_atacante}"
            )
        )
        segundos_refuerzo = estado.get("segundos_refuerzo_atacante")
        texto = (
            "Reglas: 15 segundos de preparación. El atacante puede comprar tropas también durante el combate. "
            "Si sus unidades caen, tiene 5 segundos para colocar otra tropa si aún tiene dinero. "
            "El atacante gana la ronda si destruye la base. "
        )
        etiqueta_dinero_defensor.config(text=f"🪙 Defensor\n${estado.get('dinero_defensor', 0)}")
        etiqueta_dinero_atacante.config(text=f"🪙 Atacante\n${estado.get('dinero_atacante', 0)}")
        caja_informacion_contrincante.config(state="normal")
        caja_informacion_contrincante.delete("1.0", tk.END)
        caja_informacion_contrincante.insert(tk.END, texto)
        caja_informacion_contrincante.config(state="disabled")

    def _detectar_y_animar_habilidad_rival(estado):
        """
        Descripcion:
            Detecta si el rival usó su habilidad especial comparando el
            timestamp_disparo del estado con el último conocido. Si
            cambió, activa la animación en esta pantalla también (sin
            aplicar daño, ya que el servidor ya lo hizo).
        
        Entradas:
            estado (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        for rol_rival in ("defensor", "atacante"):
            if rol_rival == rol_jugador:
                continue  # Solo animamos el disparo del rival, el propio ya se animó al clicar
            clave = "habilidad_defensor" if rol_rival == "defensor" else "habilidad_atacante"
            info = estado.get(clave, {})
            if not info:
                continue
            ts = info.get("timestamp_disparo")
            if ts is None:
                continue
            if ultimo_timestamp_habilidad[rol_rival] != ts:
                ultimo_timestamp_habilidad[rol_rival] = ts
                # Solo animar si fue reciente (menos de 3 segundos)
                if info.get("recien_disparada", False):
                    animar_habilidad_especial(rol_rival, info)

    def actualizar_vista():
        """
        Descripcion:
            Actualiza la informacion o el componente asociado a
            actualizar vista.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        estado = _obtener_estado()
        if not estado:
            return
        ultimo_estado["datos"] = estado
        dibujar_zonas()
        dibujar_estado(estado)
        _redibujar_efecto_habilidad_si_activo()
        actualizar_panel_estado(estado)
        actualizar_marcador(estado)
        detectar_resultado(estado)
        sincronizar_fase_y_temporizador(estado)
        animar_proyectiles(estado)
        # Vuelve a subir el efecto de habilidad por encima de los
        # proyectiles normales recién dibujados, para que un disparo
        # de torre/unidad nunca tape el aviso de la habilidad especial.
        if cuadro_mapa is not None and ventana_activa():
            try:
                cuadro_mapa.tag_raise(TAG_EFECTO_HABILIDAD)
            except tk.TclError:
                control["cerrando"] = True
        actualizar_boton_habilidad()
        _detectar_y_animar_habilidad_rival(estado)

    # -----------------------------------------------------------------
    # Combate local y polling red
    # -----------------------------------------------------------------

    def iniciar_combate_local():
        """
        Descripcion:
            Inicia el proceso asociado a iniciar combate local.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if modo_red or estado_ui["partida_finalizada"]:
            return
        estado = app.obtener_estado_partida()
        if estado.get("fase_ronda") != "combate":
            return
        control["combate_local_activo"] = True
        boton_turno.config(text="Combate automático", bg="#90caf9")
        ejecutar_pulso_combate_local()

    def ejecutar_pulso_combate_local():
        """
        Descripcion:
            Ejecuta la logica correspondiente a ejecutar pulso combate
            local dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not ventana_activa() or not control["combate_local_activo"]:
            return
        resultado = app.ejecutar_combate()
        for evento in resultado.get("eventos", []):
            escribir_evento(evento)
        actualizar_vista()
        estado = app.obtener_estado_partida()
        if estado.get("fase_ronda") == "combate" and not estado.get("partida_finalizada"):
            control["after_combate"] = window_mapa.after(INTERVALO_COMBATE_LOCAL_MS, ejecutar_pulso_combate_local)
        else:
            control["combate_local_activo"] = False
            boton_turno.config(text="Esperando preparación", bg="#ffb74d")

    def iniciar_polling():
        """
        Descripcion:
            Inicia el proceso asociado a iniciar polling.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not modo_red:
            return
        tick_polling()

    def tick_polling():
        """
        Descripcion:
            Ejecuta la logica correspondiente a tick polling dentro del
            flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if not ventana_activa() or not modo_red:
            return
        try:
            estado = cliente_red.obtener_ultimo_estado_local()
            if estado:
                actualizar_vista()
        except Exception:
            pass
        control["after_polling"] = window_mapa.after(INTERVALO_POLLING_MS, tick_polling)

    # -----------------------------------------------------------------
    # WIDGETS
    # -----------------------------------------------------------------

    boton_volver = tk.Button(window_mapa, text="Volver", font=("Arial", 12, "bold"), width=10, height=2, bg="red", command=GoPlayR)
    boton_volver.place(x=20, y=20)

    etiqueta_marcador = tk.Label(window_mapa, text="", font=("Arial", 12, "bold"), width=70, height=2, relief="solid", bd=2, anchor="w", padx=14)
    etiqueta_marcador.place(x=160, y=20)
    caja_informacion_superior = etiqueta_marcador

    titulo = tk.Label(window_mapa, text="Mapa de batalla", font=("Arial", 24, "bold"))
    titulo.place(relx=0.5, y=112, anchor="center")

    etiqueta_dinero_defensor = tk.Label(window_mapa, text="🪙 Defensor\n$0", font=("Arial", 16, "bold"), width=11, height=2, bg="#d7ebff", fg="#0d47a1", relief="solid", bd=3)
    etiqueta_dinero_defensor.place(x=830, y=112)

    etiqueta_dinero_atacante = tk.Label(window_mapa, text="🪙 Atacante\n$0", font=("Arial", 16, "bold"), width=11, height=2, bg="#ffe3c2", fg="#bf4e00", relief="solid", bd=3)
    etiqueta_dinero_atacante.place(x=990, y=112)

    etiqueta_eventos = tk.Label(window_mapa, text="Eventos", font=("Arial", 13, "bold"), bg=COLOR_PANEL)
    etiqueta_eventos.place(x=35, y=175)

    caja_eventos = tk.Text(window_mapa, font=("Consolas", 10), width=35, height=13, relief="solid", bd=2, wrap="word")
    caja_eventos.config(state="disabled")
    caja_eventos.place(x=35, y=205)

    etiqueta_compras = tk.Label(window_mapa, text="Tropas" if rol_jugador == "atacante" else "Defensas", font=("Arial", 13, "bold"), bg=COLOR_PANEL)
    etiqueta_compras.place(x=35, y=445)

    etiqueta_seleccion = tk.Label(window_mapa, text="Seleccionado: nada", font=("Arial", 10, "bold"), width=34, anchor="w", bg=COLOR_PANEL)
    etiqueta_seleccion.place(x=35, y=472)

    for indice, compra in enumerate(obtener_catalogo_compras()):
        y_base = 500 + (indice * 34)
        if compra["tipo"] == "muro":
            descripcion = f"{compra['nombre']}  ${compra['costo']}  ❤{compra['vida']}"
        else:
            descripcion = (
                f"{compra['nombre']}  ${compra['costo']}  "
                f"❤{compra['vida']}  ⚔{compra['dano']}"
            )
        boton_compra = tk.Button(
            window_mapa,
            text=descripcion,
            font=("Arial", 9, "bold"),
            width=30,
            command=lambda c=compra: seleccionar_compra(c),
        )
        boton_compra.place(x=35, y=y_base)
        botones_compra.append((boton_compra, compra))

    etiqueta_temporizador = tk.Label(window_mapa, text=f"Preparación: {SEGUNDOS_PREPARACION_ROL}s", font=("Arial", 12, "bold"), width=26, bg="#fff3bf", fg="#173a59", relief="solid", bd=2)
    etiqueta_temporizador.place(x=70, y=634)
    etiqueta_cuenta = etiqueta_temporizador

    boton_turno = tk.Button(window_mapa, text="Forzar combate", font=("Arial", 9, "bold"), width=15, bg="#ffb74d", command=alternar_combate_click)
    boton_turno.place(x=35, y=664)

    boton_habilidad = tk.Button(
        window_mapa,
        text="💥 Habilidad",
        font=("Arial", 9, "bold"),
        width=15,
        height=2,
        bg="#cccccc",
        state="disabled",
        command=usar_habilidad_click,
    )
    boton_habilidad.place(x=185, y=664)

    etiqueta_tablero = tk.Label(window_mapa, text="Área del mapa", font=("Arial", 13, "bold"), bg=COLOR_PANEL)
    etiqueta_tablero.place(x=405, y=175)

    cuadro_mapa = tk.Canvas(window_mapa, width=ANCHO_TABLERO, height=ALTO_TABLERO, bg="white", relief="solid", bd=3, highlightthickness=0)
    cuadro_mapa.place(x=405, y=205)
    cuadro_mapa.bind("<Button-1>", comprar_en_casilla)

    etiqueta_resultado = tk.Label(window_mapa, text="", font=("Arial", 16, "bold"), width=30, height=2, relief="solid", bd=3)

    caja_informacion_contrincante = tk.Text(window_mapa, font=("Arial", 11), width=78, height=3, relief="solid", bd=2, wrap="word")
    caja_informacion_contrincante.config(state="disabled")
    caja_informacion_contrincante.place(x=405, y=650)

    # -----------------------------------------------------------------
    # Inicio
    # -----------------------------------------------------------------

    # Precarga de imágenes para que aparezcan de inmediato al hacer clic
    # (la primera carga de un PNG puede tomar unos ms; hacerlo aquí
    #  evita el parpadeo/retraso visible al colocar la primera unidad o torre)
    def _precargar_imagenes():
        """
        Descripcion:
            Ejecuta la logica correspondiente a  precargar imagenes
            dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
            - Funcion de apoyo interno; no se recomienda llamarla
            directamente desde otros modulos.
        """
        for faccion in (faccion_defensor, faccion_atacante):
            imagen_base()
            imagen_muro()
            imagen_fondo_mapa()
            for tipo in ("soldado", "rapido", "tanque"):
                imagen_unidad({"clave": tipo})
            for tipo in ("normal", "pesada", "especial"):
                imagen_torre({"clave": tipo, "nombre": tipo})
        try:
            window_mapa.update_idletasks()
        except tk.TclError:
            pass

    _precargar_imagenes()
    actualizar_vista()
    if modo_red:
        iniciar_polling()
    window_mapa.protocol("WM_DELETE_WINDOW", cerrar_ventana)
