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

# Configuración de rondas
TIEMPO_ESPERA_RONDA = 15   # segundos antes de iniciar combate automático
RONDAS_PARA_GANAR = 3      # rondas necesarias para ganar la partida
BONO_GANADOR = 200         # dinero extra para ganador de ronda
BONO_PERDEDOR = 100        # dinero de consolación para perdedor de ronda


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
    seleccion_actual = {"tipo": None, "clave": None, "nombre": None}
    ultimo_estado = {"datos": {}}
    botones_compra = []
    control_combate = {"activo": False, "after_id": None, "cerrando": False}

    # Estado de rondas
    estado_rondas = {
        "ronda_actual": 1,
        "victorias_defensor": 0,
        "victorias_atacante": 0,
        "historial": [],          # lista de resultados: "defensor" o "atacante"
        "partida_terminada": False,
        "temporizador_id": None,
        "segundos_restantes": TIEMPO_ESPERA_RONDA,
        "fase": "espera",         # "espera", "combate", "resultado"
        "ultimo_resultado": None, # "ganaste_ronda", "perdiste_ronda", "ganaste_partida", "perdiste_partida"
    }

    preferencias = app.obtener_configuracion()
    mostrar_cuadricula = bool(preferencias.get("mostrar_cuadricula", True))
    mostrar_proyectiles = bool(preferencias.get("mostrar_proyectiles", True))

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
        if control_combate["after_id"] is not None:
            try:
                window_mapa.after_cancel(control_combate["after_id"])
            except tk.TclError:
                pass
            control_combate["after_id"] = None

    def detener_temporizador():
        if estado_rondas["temporizador_id"] is not None:
            try:
                window_mapa.after_cancel(estado_rondas["temporizador_id"])
            except tk.TclError:
                pass
            estado_rondas["temporizador_id"] = None

    def cerrar_mapa(volver_a_play=False):
        if control_combate["cerrando"]:
            return
        control_combate["cerrando"] = True
        detener_combate_programado()
        detener_temporizador()
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

    def mostrar_resultado_ronda(ganador_ronda, partida_terminada=False, ganador_partida=None):
        """Muestra la caja de resultado al jugador."""
        if not ventana_activa():
            return

        if partida_terminada:
            if ganador_partida == rol_jugador:
                texto = "¡GANASTE LA PARTIDA!"
                color_bg = "#1b5e20"
                color_fg = "white"
            else:
                texto = "PERDISTE LA PARTIDA"
                color_bg = "#b71c1c"
                color_fg = "white"
        else:
            if ganador_ronda == rol_jugador:
                texto = "¡GANASTE LA RONDA!"
                color_bg = "#2e7d32"
                color_fg = "white"
            else:
                texto = "PERDISTE LA RONDA"
                color_bg = "#c62828"
                color_fg = "white"

        try:
            etiqueta_resultado.config(
                text=texto,
                bg=color_bg,
                fg=color_fg,
            )
            etiqueta_resultado.lift()
        except tk.TclError:
            pass

    def ocultar_resultado():
        if not ventana_activa():
            return
        try:
            etiqueta_resultado.config(text="", bg="#f0f0f0", fg="#f0f0f0")
        except tk.TclError:
            pass

    def actualizar_marcador():
        if not ventana_activa():
            return
        try:
            etiqueta_marcador.config(
                text=(
                    f"Ronda {estado_rondas['ronda_actual']}  |  "
                    f"Defensor: {estado_rondas['victorias_defensor']}  "
                    f"Atacante: {estado_rondas['victorias_atacante']}  "
                    f"(primero en {RONDAS_PARA_GANAR} gana)"
                )
            )
        except tk.TclError:
            pass

    def actualizar_temporizador_label():
        if not ventana_activa():
            return
        try:
            seg = estado_rondas["segundos_restantes"]
            if estado_rondas["fase"] == "espera":
                etiqueta_temporizador.config(
                    text=f"⏱ Tiempo de colocación: {seg}s",
                    fg="#e65100" if seg <= 5 else "#333333"
                )
            elif estado_rondas["fase"] == "combate":
                etiqueta_temporizador.config(text="⚔ Combate en curso...", fg="#1565c0")
            else:
                etiqueta_temporizador.config(text="", fg="#333333")
        except tk.TclError:
            pass

    # ---- Lógica de rondas -----------------------------------------------

    def iniciar_siguiente_ronda():
        """Prepara la siguiente ronda: reinicia partida y temporizador."""
        if not ventana_activa():
            return
        ocultar_resultado()
        estado_rondas["fase"] = "espera"
        estado_rondas["segundos_restantes"] = TIEMPO_ESPERA_RONDA

        # Reiniciar la partida para la nueva ronda
        app.crear_partida(nombre_defensor, nombre_atacante)
        if rol_jugador == "atacante":
            app.iniciar_fase_ataque()

        actualizar_vista()
        actualizar_marcador()
        escribir_evento(f"─── Ronda {estado_rondas['ronda_actual']} iniciada ───")
        escribir_evento("Tienes 15 segundos para colocar tropas/defensas.")
        boton_turno.config(text="Iniciar combate", bg="#ffb74d", state="normal")
        iniciar_temporizador_espera()

    def iniciar_temporizador_espera():
        """Cuenta regresiva de 15 segundos. Si el atacante no inició, gana el defensor."""
        detener_temporizador()
        estado_rondas["segundos_restantes"] = TIEMPO_ESPERA_RONDA
        actualizar_temporizador_label()
        _tick_temporizador()

    def _tick_temporizador():
        if not ventana_activa():
            return
        if estado_rondas["fase"] != "espera":
            return
        if estado_rondas["segundos_restantes"] <= 0:
            # Tiempo agotado sin que el atacante iniciara combate → gana el defensor
            escribir_evento("¡Tiempo agotado! El atacante no actuó. Gana el DEFENSOR esta ronda.")
            _finalizar_ronda_por_tiempo()
            return
        actualizar_temporizador_label()
        estado_rondas["temporizador_id"] = window_mapa.after(1000, _tick_temporizador)
        estado_rondas["segundos_restantes"] -= 1

    def _finalizar_ronda_por_tiempo():
        """El atacante no actuó, el defensor gana la ronda."""
        detener_temporizador()
        estado_rondas["fase"] = "resultado"
        _registrar_victoria_ronda("defensor")

    def _registrar_victoria_ronda(ganador):
        """Registra quién ganó la ronda y verifica si la partida terminó."""
        estado_rondas["historial"].append(ganador)
        if ganador == "defensor":
            estado_rondas["victorias_defensor"] += 1
        else:
            estado_rondas["victorias_atacante"] += 1

        actualizar_marcador()

        # Determinar si la partida terminó
        vic_def = estado_rondas["victorias_defensor"]
        vic_ata = estado_rondas["victorias_atacante"]
        partida_terminada = vic_def >= RONDAS_PARA_GANAR or vic_ata >= RONDAS_PARA_GANAR

        if partida_terminada:
            ganador_partida = "defensor" if vic_def >= RONDAS_PARA_GANAR else "atacante"
            mostrar_resultado_ronda(ganador, partida_terminada=True, ganador_partida=ganador_partida)
            estado_rondas["partida_terminada"] = True
            boton_turno.config(text="Partida terminada", bg="#9e9e9e", state="disabled")
            escribir_evento(f"═══ PARTIDA TERMINADA ═══")
            if ganador_partida == "defensor":
                escribir_evento(f"¡El DEFENSOR gana la partida! ({vic_def}-{vic_ata})")
            else:
                escribir_evento(f"¡El ATACANTE gana la partida! ({vic_ata}-{vic_def})")
        else:
            mostrar_resultado_ronda(ganador)
            estado_rondas["ronda_actual"] += 1
            escribir_evento(f"Ronda ganada por: {ganador.upper()}")
            # Iniciar siguiente ronda automáticamente luego de 3 segundos
            window_mapa.after(3000, iniciar_siguiente_ronda)

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
        if estado_rondas["partida_terminada"]:
            return
        if estado_rondas["fase"] == "combate":
            escribir_evento("No puedes colocar durante el combate.")
            return
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
            exito, mensaje = app.comprar_torre(seleccion_actual["clave"], fila, columna)
        elif seleccion_actual["tipo"] == "muro":
            exito, mensaje = app.comprar_muro(fila, columna)
        else:
            exito, mensaje = app.comprar_unidad(seleccion_actual["clave"], fila, columna)
        escribir_evento(mensaje)
        actualizar_vista()

    def ejecutar_pulso_combate():
        if not ventana_activa():
            return False
        estado_antes = app.obtener_estado_partida()
        animar_proyectiles(estado_antes)
        resultado = app.ejecutar_combate()
        for evento in resultado.get("eventos", []):
            escribir_evento(evento)
        actualizar_vista()

        ronda_finalizada = resultado.get("ronda_finalizada", False)
        if ronda_finalizada:
            # Determinar ganador de la ronda según el estado
            estado_actual = app.obtener_estado_partida()
            vida_base = estado_actual.get("vida_base", 0)
            din_ata = estado_actual.get("dinero_atacante", 0)

            # Atacante destruyó la base → gana el atacante
            if vida_base <= 0:
                ganador_ronda = "atacante"
                escribir_evento("¡Base destruida! Gana el ATACANTE esta ronda.")
            else:
                # Atacante sin dinero suficiente para más tropas → gana el defensor
                ganador_ronda = "defensor"
                escribir_evento("El atacante no puede enviar más tropas. Gana el DEFENSOR esta ronda.")

            return False, ganador_ronda

        return True, None

    def ejecutar_combate_en_tiempo_real():
        if not control_combate["activo"] or not ventana_activa():
            return
        resultado_tuple = ejecutar_pulso_combate()
        if isinstance(resultado_tuple, tuple):
            continua, ganador_ronda = resultado_tuple
        else:
            continua, ganador_ronda = resultado_tuple, None

        if continua and control_combate["activo"]:
            control_combate["after_id"] = window_mapa.after(900, ejecutar_combate_en_tiempo_real)
        else:
            control_combate["activo"] = False
            control_combate["after_id"] = None
            estado_rondas["fase"] = "resultado"
            if ventana_activa():
                boton_turno.config(text="Iniciar combate", bg="#ffb74d")
            if ganador_ronda is not None:
                _registrar_victoria_ronda(ganador_ronda)

    def alternar_combate_click():
        if estado_rondas["partida_terminada"]:
            return
        if estado_rondas["fase"] == "resultado":
            return
        if control_combate["activo"]:
            detener_combate_programado()
            boton_turno.config(text="Iniciar combate", bg="#ffb74d")
            escribir_evento("Combate pausado.")
            return
        # El atacante inicia el combate → detener temporizador de espera
        detener_temporizador()
        estado_rondas["fase"] = "combate"
        actualizar_temporizador_label()
        control_combate["activo"] = True
        boton_turno.config(text="Pausar combate", bg="#90caf9")
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
        caja_informacion_contrincante.config(state="normal")
        caja_informacion_contrincante.delete("1.0", tk.END)
        caja_informacion_contrincante.insert(
            tk.END,
            "Colocación: defensor en zona azul; atacante en zona naranja. "
            "Haz clic en una compra y luego en una casilla válida. "
            "Al iniciar combate, la simulación avanza automáticamente en tiempo real.",
        )
        caja_informacion_contrincante.config(state="disabled")

    def actualizar_vista():
        estado = app.obtener_estado_partida()
        ultimo_estado["datos"] = estado
        dibujar_zonas()
        dibujar_estado(estado)
        actualizar_panel_estado(estado)

    # =========================================================
    # CONSTRUCCIÓN DE WIDGETS
    # =========================================================

    # --- Franja superior -------------------------------------------------
    boton_volver = tk.Button(window_mapa, text="Volver", font=("Arial", 12, "bold"), width=10, height=2, bg="red", command=GoPlayR)
    boton_volver.place(x=20, y=20)

    caja_informacion_superior = tk.Label(window_mapa, text="", font=("Arial", 12, "bold"), width=88, height=2, relief="solid", bd=2, anchor="w", padx=14)
    caja_informacion_superior.place(x=160, y=20)

    titulo = tk.Label(window_mapa, text="Mapa de batalla", font=("Arial", 24, "bold"))
    titulo.place(relx=0.5, y=95, anchor="center")

    # --- Marcador de rondas y temporizador --------------------------------
    etiqueta_marcador = tk.Label(
        window_mapa,
        text="",
        font=("Arial", 11, "bold"),
        fg="#333333",
        width=70,
        anchor="center",
    )
    etiqueta_marcador.place(relx=0.5, y=130, anchor="center")

    etiqueta_temporizador = tk.Label(
        window_mapa,
        text="",
        font=("Arial", 11, "bold"),
        fg="#e65100",
        width=30,
        anchor="center",
    )
    etiqueta_temporizador.place(relx=0.75, y=155, anchor="center")

    # --- Caja de resultado de ronda (visible solo al finalizar) -----------
    etiqueta_resultado = tk.Label(
        window_mapa,
        text="",
        font=("Arial", 18, "bold"),
        bg="#f0f0f0",
        fg="#f0f0f0",
        width=28,
        height=2,
        relief="flat",
        bd=0,
    )
    etiqueta_resultado.place(relx=0.5, y=700, anchor="center")

    # --- Columna izquierda: eventos e información ------------------------
    etiqueta_eventos = tk.Label(window_mapa, text="Eventos", font=("Arial", 13, "bold"))
    etiqueta_eventos.place(x=35, y=175)

    caja_eventos = tk.Text(window_mapa, font=("Consolas", 10), width=35, height=13, relief="solid", bd=2, wrap="word")
    caja_eventos.config(state="disabled")
    caja_eventos.place(x=35, y=205)

    # --- Columna izquierda inferior: compras -----------------------------
    etiqueta_compras = tk.Label(window_mapa, text="Tropas" if rol_jugador == "atacante" else "Defensas", font=("Arial", 13, "bold"))
    etiqueta_compras.place(x=35, y=445)

    etiqueta_seleccion = tk.Label(window_mapa, text="Seleccionado: nada", font=("Arial", 10, "bold"), width=34, anchor="w")
    etiqueta_seleccion.place(x=35, y=472)

    for indice, compra in enumerate(obtener_catalogo_compras()):
        y_base = 500 + (indice * 34)
        descripcion = f"{compra['nombre']}  ${compra['costo']}"
        boton_compra = tk.Button(window_mapa, text=descripcion, font=("Arial", 9, "bold"), width=28, command=lambda compra=compra: seleccionar_compra(compra))
        boton_compra.place(x=35, y=y_base)
        botones_compra.append((boton_compra, compra))

    boton_turno = tk.Button(window_mapa, text="Iniciar combate", font=("Arial", 11, "bold"), width=18, bg="#ffb74d", command=alternar_combate_click)
    boton_turno.place(x=95, y=660)

    # --- Zona derecha: tablero del mapa ----------------------------------
    etiqueta_tablero = tk.Label(window_mapa, text="Área del mapa", font=("Arial", 13, "bold"))
    etiqueta_tablero.place(x=405, y=175)

    cuadro_mapa = tk.Canvas(window_mapa, width=ANCHO_TABLERO, height=ALTO_TABLERO, bg="white", relief="solid", bd=3, highlightthickness=0)
    cuadro_mapa.place(x=405, y=205)
    cuadro_mapa.bind("<Button-1>", comprar_en_casilla)

    caja_informacion_contrincante = tk.Text(window_mapa, font=("Arial", 11), width=78, height=3, relief="solid", bd=2, wrap="word")
    caja_informacion_contrincante.config(state="disabled")
    caja_informacion_contrincante.place(x=405, y=650)

    # =========================================================
    # INICIO DEL JUEGO
    # =========================================================
    actualizar_vista()
    actualizar_marcador()
    escribir_evento("Partida creada. Selecciona una compra y una casilla.")
    escribir_evento(f"Tienes {TIEMPO_ESPERA_RONDA} segundos para colocar antes del combate.")
    iniciar_temporizador_espera()

    window_mapa.protocol("WM_DELETE_WINDOW", cerrar_ventana)