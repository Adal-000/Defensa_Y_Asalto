#=======================================#
# Archivo para mostrar el mapa del juego
#=======================================#

import tkinter as tk

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
COLOR_DEFENSA = "#e8f2ff"
COLOR_ATAQUE = "#fff0df"
COLOR_BASE = "#ffe0e0"
COLOR_BORDE = "#666666"


def mapa(root, GoPlay, cerrar_todo, configurar_ventana, obtener_datos_partida=None):
    """
    Descripción:
        Crea una pantalla de mapa jugable. El usuario elige una pieza
        en el panel de compras y luego hace clic en una casilla válida
        del tablero para colocar tropas o defensas. La lógica oficial
        de dinero, compras, posiciones ocupadas y combate se ejecuta
        mediante aplicacion.app.
    """

    window_mapa = tk.Toplevel(root)
    configurar_ventana(window_mapa, "Mapa")
    datos_partida = obtener_datos_partida() if obtener_datos_partida is not None else {}
    rol_jugador = datos_partida.get("rol") or "defensor"
    nombre_usuario = datos_partida.get("usuario") or datos_partida.get("jugador") or "Jugador"
    nombre_defensor = nombre_usuario if rol_jugador == "defensor" else "Defensor"
    nombre_atacante = nombre_usuario if rol_jugador == "atacante" else "Atacante"
    cliente_red = datos_partida.get("cliente_red")
    modo_red = cliente_red is not None and getattr(cliente_red, "conectado", False)
    seleccion_actual = {"tipo": None, "clave": None, "nombre": None}
    ultimo_estado = {"datos": {}}
    botones_compra = []
    control_combate = {"activo": False, "after_id": None, "cuenta_id": None, "cerrando": False, "red_iniciado": False}

    preferencias = app.obtener_configuracion()
    mostrar_cuadricula = bool(preferencias.get("mostrar_cuadricula", True))
    mostrar_proyectiles = bool(preferencias.get("mostrar_proyectiles", True))

    if modo_red:
        cliente_red.obtener_estado()
    else:
        app.crear_partida(nombre_defensor, nombre_atacante)
        if rol_jugador == "atacante":
            app.iniciar_fase_ataque()

    def ventana_activa():
        if control_combate["cerrando"]:
            return False
        try:
            return bool(window_mapa.winfo_exists())
        except tk.TclError:
            control_combate["cerrando"] = True
            return False

    def detener_combate_programado():
        control_combate["activo"] = False
        for clave_after in ("after_id", "cuenta_id"):
            if control_combate[clave_after] is None:
                continue
            try:
                window_mapa.after_cancel(control_combate[clave_after])
            except tk.TclError:
                pass
            control_combate[clave_after] = None

    def cerrar_mapa(volver_a_play=False):
        if control_combate["cerrando"]:
            return
        control_combate["cerrando"] = True
        detener_combate_programado()
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
            if not caja_eventos.winfo_exists():
                return
            caja_eventos.config(state="normal")
            caja_eventos.insert(tk.END, f"• {texto}\n")
            caja_eventos.see(tk.END)
            caja_eventos.config(state="disabled")
        except tk.TclError:
            control_combate["cerrando"] = True

    def obtener_catalogo_compras():
        if rol_jugador == "atacante":
            return [
                {"tipo": "unidad", **unidad}
                for unidad in app.obtener_catalogo_unidades()
            ]
        compras = [
            {"tipo": "torre", **torre}
            for torre in app.obtener_catalogo_torres()
        ]
        compras.append({
            "tipo": "muro",
            "clave": "muro",
            "nombre": "Muro",
            "costo": 50,
            "vida": 160,
            "dano": 0,
            "alcance": 0,
            "habilidad": "bloqueo",
        })
        return compras

    def seleccionar_compra(compra):
        if not ventana_activa():
            return
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
            return False, "El defensor solo puede colocar en la zona azul."
        if rol_jugador == "atacante" and fila not in FILAS_ATACANTE:
            return False, "El atacante solo puede colocar tropas en la zona naranja."
        return True, "Posición válida."

    def convertir_click_a_casilla(evento):
        columna = evento.x // ANCHO_CELDA
        fila = evento.y // ALTO_CELDA
        if fila < 0 or fila >= FILAS_TABLERO or columna < 0 or columna >= COLUMNAS_TABLERO:
            return None, None
        return fila, columna

    def color_proyectil(nombre_torre):
        nombre = nombre_torre.lower()
        if "cañon" in nombre or "canon" in nombre:
            return "#ff7a00"
        if "hielo" in nombre:
            return "#00bcd4"
        if "soporte" in nombre:
            return "#9c27b0"
        return "#f2c200"

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
                color = color_proyectil(torre["nombre"])
                proyectiles.append(cuadro_mapa.create_line(x1, y1, x2, y2, fill=color, width=4, arrow=tk.LAST))
                proyectiles.append(cuadro_mapa.create_oval(x2 - 6, y2 - 6, x2 + 6, y2 + 6, fill=color, outline="black"))

        for unidad in estado.get("unidades", []):
            objetivo = next(
                (torre for torre in estado.get("torres", []) if torre["fila"] == unidad["fila"] - 1 and torre["columna"] == unidad["columna"]),
                None,
            )
            if objetivo is not None:
                x1, y1 = centro_casilla(unidad["fila"], unidad["columna"])
                x2, y2 = centro_casilla(objetivo["fila"], objetivo["columna"])
                proyectiles.append(cuadro_mapa.create_line(x1, y1, x2, y2, fill="#d32f2f", width=3, dash=(5, 3)))

        if proyectiles:
            def borrar_proyectiles():
                if not ventana_activa():
                    return
                try:
                    for item in proyectiles:
                        cuadro_mapa.delete(item)
                except tk.TclError:
                    control_combate["cerrando"] = True

            window_mapa.after(450, borrar_proyectiles)

    def comprar_en_casilla(evento):
        if seleccion_actual["clave"] is None:
            escribir_evento("Primero selecciona una compra del panel izquierdo.")
            return
        fila, columna = convertir_click_a_casilla(evento)
        if fila is None:
            return
        permitido, mensaje = posicion_permitida_por_rol(fila, columna)
        if not permitido:
            escribir_evento(mensaje)
            return

        if seleccion_actual["tipo"] == "torre":
            if modo_red:
                exito, mensaje = cliente_red.comprar_torre(seleccion_actual["clave"], fila, columna)
            else:
                exito, mensaje = app.comprar_torre(seleccion_actual["clave"], fila, columna)
        elif seleccion_actual["tipo"] == "muro":
            if modo_red:
                exito, mensaje = cliente_red.comprar_muro(fila, columna)
            else:
                exito, mensaje = app.comprar_muro(fila, columna)
        else:
            if modo_red:
                exito, mensaje = cliente_red.comprar_unidad(seleccion_actual["clave"], fila, columna)
            else:
                exito, mensaje = app.comprar_unidad(seleccion_actual["clave"], fila, columna)
        escribir_evento(mensaje)
        if modo_red:
            cliente_red.obtener_estado()
        actualizar_vista()

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
                etiqueta_cuenta.config(text="Combate finalizado", fg="#1b5e20")

    def iniciar_combate_automatico():
        if control_combate["activo"]:
            return
        control_combate["activo"] = True
        etiqueta_cuenta.config(text="Combate iniciado", fg="#1b5e20")
        escribir_evento("Tiempo de preparación terminado. Combate iniciado automáticamente.")
        ejecutar_combate_en_tiempo_real()

    def actualizar_cuenta_regresiva(segundos_restantes):
        if not ventana_activa() or control_combate["activo"]:
            return
        if segundos_restantes <= 0:
            control_combate["cuenta_id"] = None
            iniciar_combate_automatico()
            return
        etiqueta_cuenta.config(
            text=f"Preparación: {segundos_restantes}s",
            fg="#b05a00" if segundos_restantes <= 10 else "#173a59",
        )
        control_combate["cuenta_id"] = window_mapa.after(
            1000, lambda: actualizar_cuenta_regresiva(segundos_restantes - 1)
        )

    def alternar_combate_click():
        if control_combate["activo"]:
            detener_combate_programado()
            etiqueta_cuenta.config(text="Combate pausado", fg="#b05a00")
            escribir_evento("Combate pausado.")
            return
        control_combate["activo"] = True
        etiqueta_cuenta.config(text="Combate iniciado", fg="#1b5e20")
        escribir_evento("Combate en tiempo real iniciado.")
        ejecutar_combate_en_tiempo_real()

    def dibujar_zonas():
        cuadro_mapa.delete("all")
        for fila in range(FILAS_TABLERO):
            y1 = fila * ALTO_CELDA
            y2 = y1 + ALTO_CELDA
            if fila == FILA_BASE:
                color = COLOR_BASE
            elif fila in FILAS_DEFENSOR:
                color = COLOR_DEFENSA
            else:
                color = COLOR_ATAQUE
            cuadro_mapa.create_rectangle(0, y1, ANCHO_TABLERO, y2, fill=color, outline="")

        if mostrar_cuadricula:
            for x in range(0, ANCHO_TABLERO + 1, ANCHO_CELDA):
                cuadro_mapa.create_line(x, 0, x, ALTO_TABLERO, fill="#cccccc")
            for y in range(0, ALTO_TABLERO + 1, ALTO_CELDA):
                cuadro_mapa.create_line(0, y, ANCHO_TABLERO, y, fill="#cccccc")

        cuadro_mapa.create_text(ANCHO_TABLERO // 2, ALTO_CELDA // 2, text="BASE", font=("Arial", 13, "bold"), fill="#9a0000")
        cuadro_mapa.create_text(10, ALTO_CELDA * 4, text="Zona defensor", angle=90, anchor="w", fill="#005b96", font=("Arial", 10, "bold"))
        cuadro_mapa.create_text(10, ALTO_CELDA * 9, text="Zona atacante", angle=90, anchor="w", fill="#b05a00", font=("Arial", 10, "bold"))

    def dibujar_estado(estado):
        vida_base = estado.get("vida_base", 0)
        vida_maxima_base = estado.get("vida_maxima_base", 1)
        ancho_vida = int((vida_base / max(1, vida_maxima_base)) * (ANCHO_TABLERO - 40))
        cuadro_mapa.create_rectangle(20, 6, ANCHO_TABLERO - 20, 16, fill="#ffcdd2", outline="black")
        cuadro_mapa.create_rectangle(20, 6, 20 + ancho_vida, 16, fill="#e53935", outline="")

        for muro in estado.get("muros", []):
            x, y = centro_casilla(muro["fila"], muro["columna"])
            cuadro_mapa.create_rectangle(x - 32, y - 12, x + 32, y + 12, fill="#8d6e63", outline="black", width=2)
            cuadro_mapa.create_text(x, y, text="MURO", font=("Arial", 8, "bold"), fill="white")

        for torre in estado.get("torres", []):
            x, y = centro_casilla(torre["fila"], torre["columna"])
            color = color_proyectil(torre["nombre"])
            cuadro_mapa.create_rectangle(x - 20, y - 18, x + 20, y + 18, fill=color, outline="black", width=2)
            cuadro_mapa.create_text(x, y - 3, text="T", font=("Arial", 14, "bold"), fill="black")
            cuadro_mapa.create_text(x, y + 13, text=str(torre["vida"]), font=("Arial", 8, "bold"), fill="black")

        for unidad in estado.get("unidades", []):
            x, y = centro_casilla(unidad["fila"], unidad["columna"])
            cuadro_mapa.create_oval(x - 20, y - 17, x + 20, y + 17, fill="#ff7043", outline="black", width=2)
            cuadro_mapa.create_text(x, y - 3, text="U", font=("Arial", 14, "bold"), fill="white")
            cuadro_mapa.create_text(x, y + 13, text=str(unidad["vida"]), font=("Arial", 8, "bold"), fill="white")

    def actualizar_panel_estado(estado):
        caja_informacion_superior.config(
            text=(
                f"Rol: {rol_jugador.upper()} | Ronda {estado.get('numero_ronda', 1)} | "
                f"Defensor ${estado.get('dinero_defensor', 0)} | "
                f"Atacante ${estado.get('dinero_atacante', 0)} | "
                f"Base {estado.get('vida_base', 0)}/{estado.get('vida_maxima_base', 0)}"
            )
        )
        etiqueta_dinero_defensor.config(text=f"Defensor\n${estado.get('dinero_defensor', 0)}")
        etiqueta_dinero_atacante.config(text=f"Atacante\n${estado.get('dinero_atacante', 0)}")
        caja_informacion_contrincante.config(state="normal")
        caja_informacion_contrincante.delete("1.0", tk.END)
        caja_informacion_contrincante.insert(
            tk.END,
            "Colocación: defensor en zona azul; atacante en zona naranja. "
            "Haz clic en una compra y luego en una casilla válida. "
            "El contador inicia el combate automáticamente cuando termina la preparación.",
        )
        caja_informacion_contrincante.config(state="disabled")

    def actualizar_vista():
        estado = obtener_estado_visible()
        ultimo_estado["datos"] = estado
        dibujar_zonas()
        dibujar_estado(estado)
        actualizar_panel_estado(estado)

    def obtener_estado_visible():
        if modo_red:
            estado_red = cliente_red.obtener_ultimo_estado_local()
            if estado_red is None:
                return ultimo_estado["datos"]
            return estado_red
        return app.obtener_estado_partida()

    def refrescar_estado_red():
        if not modo_red or not ventana_activa():
            return
        cliente_red.obtener_estado()
        actualizar_vista()
        window_mapa.after(500, refrescar_estado_red)

    # --- Franja superior -------------------------------------------------
    boton_volver = tk.Button(window_mapa, text="Volver", font=("Arial", 12, "bold"), width=10, height=2, bg="red", command=GoPlayR)
    boton_volver.place(x=20, y=20)

    caja_informacion_superior = tk.Label(window_mapa, text="", font=("Arial", 12, "bold"), width=88, height=2, relief="solid", bd=2, anchor="w", padx=14)
    caja_informacion_superior.place(x=160, y=20)

    titulo = tk.Label(window_mapa, text="Mapa de batalla", font=("Arial", 24, "bold"))
    titulo.place(relx=0.5, y=95, anchor="center")

    etiqueta_dinero_defensor = tk.Label(window_mapa, text="Defensor\n$0", font=("Arial", 15, "bold"), width=12, height=2, bg="#d7ebff", fg="#0d47a1", relief="solid", bd=2)
    etiqueta_dinero_defensor.place(x=870, y=75)

    etiqueta_dinero_atacante = tk.Label(window_mapa, text="Atacante\n$0", font=("Arial", 15, "bold"), width=12, height=2, bg="#ffe3c2", fg="#bf4e00", relief="solid", bd=2)
    etiqueta_dinero_atacante.place(x=1010, y=75)

    # --- Columna izquierda: eventos e información ------------------------
    etiqueta_eventos = tk.Label(window_mapa, text="Eventos", font=("Arial", 13, "bold"))
    etiqueta_eventos.place(x=35, y=125)

    caja_eventos = tk.Text(window_mapa, font=("Consolas", 10), width=35, height=14, relief="solid", bd=2, wrap="word")
    caja_eventos.config(state="disabled")
    caja_eventos.place(x=35, y=155)
    escribir_evento("Partida creada. Selecciona una compra y una casilla.")

    # --- Columna izquierda inferior: compras -----------------------------
    etiqueta_compras = tk.Label(window_mapa, text="Tropas" if rol_jugador == "atacante" else "Defensas", font=("Arial", 13, "bold"))
    etiqueta_compras.place(x=35, y=435)

    etiqueta_seleccion = tk.Label(window_mapa, text="Seleccionado: nada", font=("Arial", 10, "bold"), width=34, anchor="w")
    etiqueta_seleccion.place(x=35, y=462)

    for indice, compra in enumerate(obtener_catalogo_compras()):
        y_base = 490 + (indice * 34)
        descripcion = f"{compra['nombre']}  ${compra['costo']}"
        boton_compra = tk.Button(window_mapa, text=descripcion, font=("Arial", 9, "bold"), width=28, command=lambda compra=compra: seleccionar_compra(compra))
        boton_compra.place(x=35, y=y_base)
        botones_compra.append((boton_compra, compra))

    etiqueta_cuenta = tk.Label(window_mapa, text="Preparación: 45s", font=("Arial", 13, "bold"), width=22, bg="#fff3bf", fg="#173a59", relief="solid", bd=2)
    etiqueta_cuenta.place(x=70, y=650)

    # --- Zona derecha: tablero del mapa ----------------------------------
    etiqueta_tablero = tk.Label(window_mapa, text="Área del mapa", font=("Arial", 13, "bold"))
    etiqueta_tablero.place(x=405, y=125)

    cuadro_mapa = tk.Canvas(window_mapa, width=ANCHO_TABLERO, height=ALTO_TABLERO, bg="white", relief="solid", bd=3, highlightthickness=0)
    cuadro_mapa.place(x=405, y=155)
    cuadro_mapa.bind("<Button-1>", comprar_en_casilla)

    caja_informacion_contrincante = tk.Text(window_mapa, font=("Arial", 11), width=78, height=3, relief="solid", bd=2, wrap="word")
    caja_informacion_contrincante.config(state="disabled")
    caja_informacion_contrincante.place(x=405, y=600)

    actualizar_vista()
    if modo_red:
        refrescar_estado_red()
    actualizar_cuenta_regresiva(45)
    window_mapa.protocol("WM_DELETE_WINDOW", cerrar_ventana)
