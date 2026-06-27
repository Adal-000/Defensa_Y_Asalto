#=======================================#
# Archivo para mostrar el mapa del juego
#=======================================#

import os
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
COLOR_PANEL = "#f7f7f7"
COLOR_TEXTO = "#222222"

TIEMPO_PREPARACION_SEGUNDOS = 15
INTERVALO_POLLING_MS = 250
INTERVALO_COMBATE_LOCAL_MS = 750
RONDAS_PARA_GANAR = 3


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
    "torre arquera": "normal",
    "arquera": "normal",
    "torre cañon": "pesada",
    "torre canon": "pesada",
    "cañon": "pesada",
    "canon": "pesada",
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
    Descripción:
        Crea la ventana jugable del mapa. Mantiene la lógica sincronizada
        con el servidor cuando hay red y usa la lógica local de app.py
        cuando se abre sin conexión.
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
    faccion_jugador = datos_partida.get("faccion") or ""
    catalogo_facciones = app.obtener_catalogo_facciones()
    facciones_por_nombre = {faccion["nombre"]: faccion for faccion in catalogo_facciones}
    faccion_defensor = faccion_jugador if rol_jugador == "defensor" else "España"
    faccion_atacante = faccion_jugador if rol_jugador == "atacante" else "EE.UU"
    imagenes_mapa = {}
    seleccion_actual = {"tipo": None, "clave": None, "nombre": None}
    ultimo_estado = {"datos": {}}
    botones_compra = []
    control_combate = {"activo": False, "after_id": None, "cuenta_id": None, "cerrando": False, "red_iniciado": False}

    nombre_defensor = nombre_usuario if rol_jugador == "defensor" else "Defensor"
    nombre_atacante = nombre_usuario if rol_jugador == "atacante" else "Atacante"

    if not modo_red:
        app.crear_partida(nombre_defensor, nombre_atacante)

    seleccion_actual = {"tipo": None, "clave": None, "nombre": None}
    botones_compra = []
    imagenes = {}
    ultimo_estado = {"datos": {}}
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
        "fase": "preparacion",
        "segundos": TIEMPO_PREPARACION_SEGUNDOS,
        "ronda": 1,
        "victorias_defensor": 0,
        "victorias_atacante": 0,
        "partida_finalizada": False,
        "temporizador_enviado": set(),
        "resultados_mostrados": set(),
        "puntuacion_anterior": (0, 0),
    }

    # -----------------------------------------------------------------
    # Utilidades generales
    # -----------------------------------------------------------------

    def ventana_activa():
        if control["cerrando"]:
            return False
        try:
            return bool(window_mapa.winfo_exists())
        except tk.TclError:
            control["cerrando"] = True
            return False

    def cancelar_after(clave):
        if control.get(clave) is not None:
            try:
                window_mapa.after_cancel(control[clave])
            except tk.TclError:
                pass
            control[clave] = None

    def detener_todo():
        control["combate_local_activo"] = False
        for clave in ("after_polling", "after_timer", "after_combate", "after_volver", "after_ocultar_resultado"):
            cancelar_after(clave)

    def cerrar_mapa(volver_a_play=False):
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
        cerrar_mapa(volver_a_play=True)

    def cerrar_ventana():
        cerrar_mapa()
        cerrar_todo()

    def escribir_evento(texto):
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
        if not os.path.isdir(carpeta):
            return None
        palabra = palabra.lower()
        for raiz, _, archivos in os.walk(carpeta):
            for archivo in archivos:
                if archivo.lower().endswith((".png", ".gif")) and palabra in archivo.lower():
                    return os.path.join(raiz, archivo)
        return None

    def buscar_primer_png(carpeta):
        if not os.path.isdir(carpeta):
            return None
        for raiz, _, archivos in os.walk(carpeta):
            for archivo in archivos:
                if archivo.lower().endswith((".png", ".gif")):
                    return os.path.join(raiz, archivo)
        return None

    def cargar_photoimage(ruta, ancho_max=None, alto_max=None, ajustar_exactamente=False):
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
        clave = unidad.get("clave") or ""
        if clave:
            return clave
        return CLAVE_UNIDAD_POR_NOMBRE.get(str(unidad.get("nombre", "")).lower(), "soldado")

    def clave_torre(torre):
        clave = torre.get("clave") or ""
        if clave in ("normal", "pesada", "especial"):
            return clave
        return CLAVE_TORRE_POR_NOMBRE.get(str(torre.get("nombre", "")).lower(), "normal")

    def imagen_unidad(unidad):
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
        faccion = obtener_faccion_por_rol("defensor")
        llave = ("base", faccion)
        if llave in imagenes:
            return imagenes[llave]
        carpeta_faccion = obtener_carpeta_faccion("estructuras", faccion)
        ruta = buscar_archivo_por_nombre(carpeta_faccion, "principal")
        imagenes[llave] = cargar_photoimage(ruta, 80, 44)
        return imagenes[llave]

    def imagen_muro():
        llave = ("muro",)
        if llave not in imagenes:
            ruta = buscar_primer_png(os.path.join(RUTA_IMAGENES, "muros"))
            imagenes[llave] = cargar_photoimage(ruta, 70, 28)
        return imagenes[llave]

    def imagen_fondo_mapa():
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
        if modo_red:
            estado = cliente_red.obtener_ultimo_estado_local()
            return estado if estado else {}
        return app.obtener_estado_partida()

    def _accion_comprar_torre(clave, fila, columna):
        if modo_red:
            return cliente_red.comprar_torre(clave, fila, columna)
        return app.comprar_torre(clave, fila, columna)

    def _accion_comprar_muro(fila, columna):
        if modo_red:
            return cliente_red.comprar_muro(fila, columna)
        return app.comprar_muro(fila, columna)

    def _accion_comprar_unidad(clave, fila, columna):
        if modo_red:
            return cliente_red.comprar_unidad(clave, fila, columna)
        return app.comprar_unidad(clave, fila, columna)

    def _accion_iniciar_combate(numero_ronda):
        if modo_red:
            return cliente_red.iniciar_combate()
        return app.resolver_preparacion_agotada()

    # -----------------------------------------------------------------
    # Marcador, temporizador y resultados
    # -----------------------------------------------------------------

    def actualizar_marcador(estado=None):
        estado = estado or _obtener_estado()
        ronda = estado.get("numero_ronda", estado_ui["ronda"])
        vic_def = estado.get("rondas_ganadas_defensor", estado_ui["victorias_defensor"])
        vic_ata = estado.get("rondas_ganadas_atacante", estado_ui["victorias_atacante"])
        para_ganar = estado.get("rondas_para_ganar_partida", RONDAS_PARA_GANAR)
        etiqueta_marcador.config(
            text=f"Ronda {ronda} | Defensor {vic_def} - {vic_ata} Atacante | gana el primero en {para_ganar}"
        )

    def actualizar_temporizador_label(texto_extra=""):
        fase = estado_ui["fase"]
        if estado_ui["partida_finalizada"]:
            etiqueta_temporizador.config(text="Partida finalizada", fg="#444444")
        elif fase == "combate":
            etiqueta_temporizador.config(text="⚔ Combate en tiempo real", fg="#1565c0")
        else:
            seg = estado_ui["segundos"]
            etiqueta_temporizador.config(
                text=texto_extra or f"⏱ Preparación: {seg}s",
                fg="#c45100" if seg <= 5 else "#333333",
            )

    def mostrar_caja_resultado(ganador_ronda, partida_finalizada=False, ganador_partida=None):
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
                if ventana_activa():
                    etiqueta_resultado.place_forget()
                    etiqueta_resultado.config(text="", bg=COLOR_PANEL, fg=COLOR_PANEL)
            control["after_ocultar_resultado"] = window_mapa.after(1300, ocultar_resultado)

    def detectar_resultado(estado):
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

    def reiniciar_temporizador_si_cambio_ronda(estado):
        ronda = int(estado.get("numero_ronda", 1))
        fase_logica = estado.get("fase_ronda", "")
        partida_finalizada = bool(estado.get("partida_finalizada", False))
        combate_red = False
        datos_red = obtener_ultimos_datos_red()
        if isinstance(datos_red, dict):
            combate_red = bool(datos_red.get("combate_activo", False))

        estado_ui["partida_finalizada"] = partida_finalizada
        estado_ui["ronda"] = ronda
        estado_ui["victorias_defensor"] = int(estado.get("rondas_ganadas_defensor", 0))
        estado_ui["victorias_atacante"] = int(estado.get("rondas_ganadas_atacante", 0))

        if partida_finalizada:
            estado_ui["fase"] = "finalizada"
            cancelar_after("after_timer")
            actualizar_temporizador_label()
            return

        if fase_logica == "combate" or combate_red:
            estado_ui["fase"] = "combate"
            cancelar_after("after_timer")
            actualizar_temporizador_label()
            return

        if estado_ui["fase"] != "preparacion" or estado_ui.get("ronda_timer") != ronda:
            estado_ui["fase"] = "preparacion"
            estado_ui["ronda_timer"] = ronda
            estado_ui["segundos"] = TIEMPO_PREPARACION_SEGUNDOS
            iniciar_temporizador_preparacion()

    def iniciar_temporizador_preparacion():
        cancelar_after("after_timer")
        actualizar_temporizador_label()
        control["after_timer"] = window_mapa.after(1000, tick_temporizador_preparacion)

    def tick_temporizador_preparacion():
        if not ventana_activa() or estado_ui["partida_finalizada"]:
            return
        if estado_ui["fase"] != "preparacion":
            return

        estado_ui["segundos"] -= 1
        actualizar_temporizador_label()

        if estado_ui["segundos"] <= 0:
            numero_ronda = estado_ui["ronda"]
            if numero_ronda not in estado_ui["temporizador_enviado"]:
                estado_ui["temporizador_enviado"].add(numero_ronda)
                escribir_evento("Tiempo de preparación terminado. El combate inicia si hay tropas; si no, gana el defensor.")
                _accion_iniciar_combate(numero_ronda)
                if not modo_red:
                    actualizar_vista()
                    estado = _obtener_estado()
                    if estado.get("fase_ronda") == "combate":
                        iniciar_combate_local()
            return

        control["after_timer"] = window_mapa.after(1000, tick_temporizador_preparacion)

    # -----------------------------------------------------------------
    # Catálogo y compra
    # -----------------------------------------------------------------

    def obtener_catalogo_compras():
        if rol_jugador == "atacante":
            return [{"tipo": "unidad", **unidad} for unidad in app.obtener_catalogo_unidades()]
        compras = [{"tipo": "torre", **torre} for torre in app.obtener_catalogo_torres()]
        compras.append({
            "tipo": "muro",
            "clave": "muro",
            "nombre": "Muro",
            "costo": 60,
            "vida": 100,
            "dano": 0,
            "alcance": 0,
            "habilidad": "bloqueo",
        })
        return compras

    def seleccionar_compra(compra):
        seleccion_actual["tipo"] = compra["tipo"]
        seleccion_actual["clave"] = compra["clave"]
        seleccion_actual["nombre"] = compra["nombre"]
        etiqueta_seleccion.config(text=f"Seleccionado: {compra['nombre']}")
        for boton, compra_boton in botones_compra:
            boton.config(relief="sunken" if compra_boton is compra else "raised")

    def posicion_permitida_por_rol(fila, columna):
        if fila == FILA_BASE:
            return False, "La base no se puede ocupar."
        if rol_jugador == "defensor" and fila not in FILAS_DEFENSOR:
            return False, "El defensor solo coloca defensas en la zona azul."
        if rol_jugador == "atacante" and fila not in FILAS_ATACANTE:
            return False, "El atacante solo coloca tropas en la zona naranja."
        return True, "Posición válida."

    def convertir_click_a_casilla(evento):
        columna = evento.x // ANCHO_CELDA
        fila = evento.y // ALTO_CELDA
        if fila < 0 or fila >= FILAS_TABLERO or columna < 0 or columna >= COLUMNAS_TABLERO:
            return None, None
        return fila, columna

    def datos_faccion_por_rol(rol):
        nombre_faccion = faccion_defensor if rol == "defensor" else faccion_atacante
        return facciones_por_nombre.get(nombre_faccion, {})

    def color_proyectil(nombre_torre, rol="defensor"):
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
        nombre = nombre_torre.lower()
        datos_faccion = datos_faccion_por_rol("defensor")
        if "pesada" in nombre or "cañon" in nombre or "canon" in nombre:
            return datos_faccion.get("torre_pesada")
        if "especial" in nombre or "hielo" in nombre or "soporte" in nombre:
            return datos_faccion.get("torre_especial")
        return datos_faccion.get("torre_normal")

    def ruta_unidad_faccion(nombre_unidad):
        nombre = nombre_unidad.lower()
        datos_faccion = datos_faccion_por_rol("atacante")
        if "tanque" in nombre or "pesad" in nombre or "escudero" in nombre or "demoledor" in nombre:
            return datos_faccion.get("soldado_tanque")
        if "rap" in nombre or "ráp" in nombre or "explorador" in nombre:
            return datos_faccion.get("soldado_rapido")
        return datos_faccion.get("soldado_base")

    def centro_casilla(fila, columna):
        return (
            columna * ANCHO_CELDA + ANCHO_CELDA // 2,
            fila * ALTO_CELDA + ALTO_CELDA // 2,
        )

    def distancia(fila_a, columna_a, fila_b, columna_b):
        return abs(fila_a - fila_b) + abs(columna_a - columna_b)

    def animar_proyectiles(estado):
        if not mostrar_proyectiles or not ventana_activa():
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
                if not ventana_activa():
                    return
                try:
                    for item in proyectiles:
                        cuadro_mapa.delete(item)
                except tk.TclError:
                    control_combate["cerrando"] = True

            window_mapa.after(650, borrar_proyectiles)

    def comprar_en_casilla(evento):
        if estado_ui["partida_finalizada"]:
            return
        if seleccion_actual["clave"] is None:
            escribir_evento("Primero selecciona una compra del panel izquierdo.")
            return
        if rol_jugador == "defensor" and estado_ui["fase"] == "combate":
            escribir_evento("El defensor no coloca defensas durante el combate.")
            return

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

    def nombre_fase_preparacion(estado):
        fase = estado.get("fase_ronda", "")
        if fase == "ataque_atacante":
            return "Preparación atacante: coloca tropas"
        if fase == "construccion_defensor":
            return "Preparación defensor: coloca defensas"
        if fase == "combate":
            return "Combate en tiempo real"
        return "Preparación"

    def nombre_fase_preparacion(estado):
        fase = estado.get("fase_ronda", "")
        if fase == "ataque_atacante":
            return "Preparación atacante: coloca tropas"
        if fase == "construccion_defensor":
            return "Preparación defensor: coloca defensas"
        if fase == "combate":
            return "Combate en tiempo real"
        return "Preparación"

    def nombre_fase_preparacion(estado):
        fase = estado.get("fase_ronda", "")
        if fase == "ataque_atacante":
            return "Preparación atacante: coloca tropas"
        if fase == "construccion_defensor":
            return "Preparación defensor: coloca defensas"
        if fase == "combate":
            return "Combate en tiempo real"
        return "Preparación"

    def ejecutar_pulso_combate():
        if not ventana_activa():
            return False
        estado_antes = obtener_estado_visible()
        animar_proyectiles(estado_antes)
        if modo_red:
            if not control_combate["red_iniciado"]:
                _exito, mensaje = cliente_red.iniciar_combate()
                escribir_evento(mensaje)
                control_combate["red_iniciado"] = True
            cliente_red.obtener_estado()
            actualizar_vista()
            estado_actual = obtener_estado_visible()
            return not estado_actual.get("partida_finalizada", False)
        else:
            resultado = app.ejecutar_combate()
        for evento in resultado.get("eventos", []):
            escribir_evento(evento)
        actualizar_vista()
        if resultado.get("fase_ronda") == "construccion_defensor":
            control_combate["activo"] = False
            etiqueta_cuenta.config(text="Preparación defensor: 45s", fg="#173a59")
            actualizar_cuenta_regresiva(45)
            return False
        return not resultado.get("ronda_finalizada", False)

    def ejecutar_combate_en_tiempo_real():
        if not control_combate["activo"] or not ventana_activa():
            return
        continua = ejecutar_pulso_combate()
        if continua and control_combate["activo"]:
            control_combate["after_id"] = window_mapa.after(900, ejecutar_combate_en_tiempo_real)
        else:
            control_combate["activo"] = False
            control_combate["after_id"] = None
            if ventana_activa():
                if etiqueta_cuenta.cget("text") != "Preparación defensor: 45s":
                    etiqueta_cuenta.config(text="Combate finalizado", fg="#1b5e20")

    # -----------------------------------------------------------------
    # Dibujo del mapa
    # -----------------------------------------------------------------

    def actualizar_cuenta_regresiva(segundos_restantes):
        if not ventana_activa() or control_combate["activo"]:
            return
        if segundos_restantes <= 0:
            control_combate["cuenta_id"] = None
            iniciar_combate_automatico()
            return
        estado_actual = obtener_estado_visible()
        etiqueta_cuenta.config(
            text=f"{nombre_fase_preparacion(estado_actual)}: {segundos_restantes}s",
            fg="#b05a00" if segundos_restantes <= 10 else "#173a59",
        )
        control_combate["cuenta_id"] = window_mapa.after(
            1000, lambda: actualizar_cuenta_regresiva(segundos_restantes - 1)
        )

    def distancia(fila_a, columna_a, fila_b, columna_b):
        return abs(fila_a - fila_b) + abs(columna_a - columna_b)

    def color_proyectil(nombre_torre):
        nombre = str(nombre_torre).lower()
        if "cañon" in nombre or "canon" in nombre:
            return "#ff7a00"
        if "hielo" in nombre:
            return "#00bcd4"
        if "soporte" in nombre:
            return "#9c27b0"
        return "#f2c200"

    def dibujar_zonas():
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

        for x in range(0, ANCHO_TABLERO + 1, ANCHO_CELDA):
            cuadro_mapa.create_line(x, 0, x, ALTO_TABLERO, fill="#a9a9a9")
        for y in range(0, ALTO_TABLERO + 1, ALTO_CELDA):
            cuadro_mapa.create_line(0, y, ANCHO_TABLERO, y, fill="#a9a9a9")

        base = imagen_base()
        x_base, y_base = centro_casilla(0, COLUMNAS_TABLERO // 2)
        if base is not None:
            cuadro_mapa.create_image(x_base, y_base + 2, image=base)
        else:
            cuadro_mapa.create_text(x_base, y_base, text="BASE", font=("Arial", 13, "bold"), fill="#9a0000")

        sprite_base_defensor = cargar_imagen_mapa(datos_faccion_por_rol("defensor").get("estructura_base"), 110, 38)
        if sprite_base_defensor is not None:
            cuadro_mapa.create_image(ANCHO_TABLERO // 2, ALTO_CELDA // 2 + 3, image=sprite_base_defensor)
        cuadro_mapa.create_text(ANCHO_TABLERO // 2, ALTO_CELDA // 2, text="BASE DEFENSOR", font=("Arial", 12, "bold"), fill="#9a0000")
        cuadro_mapa.create_text(10, ALTO_CELDA * 4, text="Zona defensor", angle=90, anchor="w", fill="#005b96", font=("Arial", 10, "bold"))
        cuadro_mapa.create_text(10, ALTO_CELDA * 9, text="Zona atacante", angle=90, anchor="w", fill="#b05a00", font=("Arial", 10, "bold"))

    def dibujar_barra_vida(x, y, vida, vida_maxima, ancho=48):
        vida_maxima = max(1, int(vida_maxima))
        vida = max(0, int(vida))
        ancho_vida = int((vida / vida_maxima) * ancho)
        cuadro_mapa.create_rectangle(x - ancho // 2, y, x + ancho // 2, y + 6, fill="#ffcdd2", outline="#111111")
        cuadro_mapa.create_rectangle(x - ancho // 2, y, x - ancho // 2 + ancho_vida, y + 6, fill="#43a047", outline="")

    def dibujar_estado(estado):
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
        datos_red = obtener_ultimos_datos_red()
        usuarios = datos_red.get("usuarios_por_rol", {}) if isinstance(datos_red, dict) else {}
        fase = estado.get("fase_ronda", "preparacion")
        modo_txt = "🌐 Red" if modo_red else "💻 Local"
        caja_informacion_superior.config(
            text=(
                f"Rol: {rol_jugador.upper()} | Fase: {estado.get('fase_ronda', 'preparación')} | Ronda {estado.get('numero_ronda', 1)} | "
                f"Base {estado.get('vida_base', 0)}/{estado.get('vida_maxima_base', 0)}"
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

    def actualizar_vista():
        estado = _obtener_estado()
        if not estado:
            return
        ultimo_estado["datos"] = estado
        dibujar_zonas()
        dibujar_estado(estado)
        actualizar_panel_estado(estado)
        actualizar_marcador(estado)
        detectar_resultado(estado)
        reiniciar_temporizador_si_cambio_ronda(estado)
        animar_proyectiles(estado)

    # -----------------------------------------------------------------
    # Combate local y polling red
    # -----------------------------------------------------------------

    def iniciar_combate_local():
        if modo_red or estado_ui["partida_finalizada"]:
            return
        estado = app.obtener_estado_partida()
        if estado.get("fase_ronda") != "combate":
            return
        control["combate_local_activo"] = True
        boton_turno.config(text="Combate automático", bg="#90caf9")
        ejecutar_pulso_combate_local()

    def ejecutar_pulso_combate_local():
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
        if not modo_red:
            return
        tick_polling()

    def tick_polling():
        if not ventana_activa() or not modo_red:
            return
        try:
            estado = cliente_red.obtener_ultimo_estado_local()
            if estado:
                actualizar_vista()
        except Exception:
            pass
        control["after_polling"] = window_mapa.after(INTERVALO_POLLING_MS, tick_polling)

    def alternar_combate_click():
        if estado_ui["partida_finalizada"]:
            return
        estado = _obtener_estado()
        numero_ronda = int(estado.get("numero_ronda", estado_ui["ronda"]))
        if estado.get("fase_ronda") == "combate":
            escribir_evento("El combate ya está en curso.")
            return
        exito, mensaje = _accion_iniciar_combate(numero_ronda)
        escribir_evento(mensaje)
        if not modo_red:
            actualizar_vista()
            if app.obtener_estado_partida().get("fase_ronda") == "combate":
                iniciar_combate_local()

    # -----------------------------------------------------------------
    # WIDGETS
    # -----------------------------------------------------------------

    boton_volver = tk.Button(window_mapa, text="Volver", font=("Arial", 12, "bold"), width=10, height=2, bg="red", command=GoPlayR)
    boton_volver.place(x=20, y=20)

    caja_informacion_superior = tk.Label(window_mapa, text="", font=("Arial", 12, "bold"), width=70, height=2, relief="solid", bd=2, anchor="w", padx=14)
    caja_informacion_superior.place(x=160, y=20)

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
        descripcion = f"{compra['nombre']}  ${compra['costo']}"
        boton_compra = tk.Button(
            window_mapa,
            text=descripcion,
            font=("Arial", 9, "bold"),
            width=28,
            command=lambda c=compra: seleccionar_compra(c),
        )
        boton_compra.place(x=35, y=y_base)
        botones_compra.append((boton_compra, compra))

    boton_turno = tk.Button(window_mapa, text="Forzar combate", font=("Arial", 11, "bold"), width=18, bg="#ffb74d", command=alternar_combate_click)
    boton_turno.place(x=95, y=660)

    etiqueta_tablero = tk.Label(window_mapa, text="Área del mapa", font=("Arial", 13, "bold"), bg=COLOR_PANEL)
    etiqueta_tablero.place(x=405, y=175)

    cuadro_mapa = tk.Canvas(window_mapa, width=ANCHO_TABLERO, height=ALTO_TABLERO, bg="white", relief="solid", bd=3, highlightthickness=0)
    cuadro_mapa.place(x=405, y=205)
    cuadro_mapa.bind("<Button-1>", comprar_en_casilla)

    caja_informacion_contrincante = tk.Text(window_mapa, font=("Arial", 10), width=80, height=3, relief="solid", bd=2, wrap="word")
    caja_informacion_contrincante.config(state="disabled")
    caja_informacion_contrincante.place(x=405, y=650)

    # -----------------------------------------------------------------
    # Inicio
    # -----------------------------------------------------------------

    actualizar_vista()
    escribir_evento(f"Partida iniciada en modo {'red' if modo_red else 'local'}.")
    escribir_evento("Selecciona una compra y haz clic en una casilla válida.")
    escribir_evento("Regla principal: 15s de preparación, luego combate automático.")
    iniciar_polling()
    iniciar_temporizador_preparacion()

    window_mapa.protocol("WM_DELETE_WINDOW", cerrar_ventana)
