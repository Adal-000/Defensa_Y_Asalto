#=======================================#
# Archivo para ver puntajes de otros
#=======================================#

import tkinter as tk

from aplicacion import app

COLOR_FONDO = "#18202b"
COLOR_TARJETA = "#243244"
COLOR_PRIMARIO = "#1f4e79"
COLOR_SECUNDARIO = "#f6b73c"
COLOR_BORDE = "#f6b73c"
COLOR_TEXTO_SUAVE = "#b8c7d9"


def puntajes(root, GoPerfil, cerrar_todo, configurar_ventana,
             obtener_usuario_actual):
    """
    Descripcion:
        Crea la ventana de puntajes del jugador y puntajes mundiales.
    
    Entradas:
        root (object): Valor recibido por la funcion.
        GoPerfil (object): Valor recibido por la funcion.
        cerrar_todo (object): Valor recibido por la funcion.
        configurar_ventana (object): Valor recibido por la funcion.
        obtener_usuario_actual (object): Valor recibido por la funcion.
    
    Salidas:
        None: Ejecuta la accion y puede modificar el estado interno, la
        interfaz o los datos relacionados.
    
    Restricciones:
        - Los parametros recibidos deben respetar el tipo y el formato
        esperado por la funcion.
        - Requiere que los widgets, ventanas o callbacks usados por la
        interfaz existan antes de ejecutarse.
    """

    window_puntajes = tk.Toplevel(root)
    configurar_ventana(window_puntajes, "Puntajes")
    window_puntajes.configure(bg=COLOR_FONDO)

    def GoPerfilR():
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoPerfilR.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        window_puntajes.destroy()
        GoPerfil()

    def crear_tarjeta(parent, x, y, ancho, alto, titulo, color_titulo=COLOR_PRIMARIO):
        """
        Descripcion:
            Crea y configura el elemento asociado a crear tarjeta para
            usarlo dentro del juego o la interfaz.
        
        Entradas:
            parent (object): Valor recibido por la funcion.
            x (object): Valor recibido por la funcion.
            y (object): Valor recibido por la funcion.
            ancho (object): Valor recibido por la funcion.
            alto (object): Valor recibido por la funcion.
            titulo (object): Valor recibido por la funcion.
            color_titulo (object): Valor recibido por la funcion. Valor
            opcional.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        tarjeta = tk.Frame(
            parent,
            bg=COLOR_TARJETA,
            highlightbackground=COLOR_BORDE,
            highlightthickness=2,
        )
        tarjeta.place(x=x, y=y, width=ancho, height=alto)

        encabezado = tk.Label(
            tarjeta,
            text=titulo,
            bg=color_titulo,
            fg="white",
            font=("Arial", 18, "bold"),
            anchor="center",
            pady=10,
        )
        encabezado.pack(fill="x")
        return tarjeta

    def crear_metrica(parent, titulo, valor, color, columna):
        """
        Descripcion:
            Crea y configura el elemento asociado a crear metrica para
            usarlo dentro del juego o la interfaz.
        
        Entradas:
            parent (object): Valor recibido por la funcion.
            titulo (object): Valor recibido por la funcion.
            valor (object): Valor recibido por la funcion.
            color (object): Valor recibido por la funcion.
            columna (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        cuadro = tk.Frame(parent, bg="#31445c", highlightbackground=color, highlightthickness=2)
        cuadro.grid(row=0, column=columna, padx=10, pady=18, sticky="nsew")
        tk.Label(cuadro, text=titulo, bg="#31445c", fg=COLOR_TEXTO_SUAVE, font=("Arial", 11, "bold")).pack(pady=(10, 2))
        tk.Label(cuadro, text=str(valor), bg="#31445c", fg=color, font=("Arial", 28, "bold")).pack(pady=(0, 8))
        return cuadro

    def medalla(posicion):
        """
        Descripcion:
            Ejecuta la logica correspondiente a medalla dentro del flujo
            del juego.
        
        Entradas:
            posicion (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        if posicion == 1:
            return "🥇"
        if posicion == 2:
            return "🥈"
        if posicion == 3:
            return "🥉"
        return f"{posicion}."

    def crear_tabla_ranking(parent, titulo, ranking, clave_victorias, fila_inicial):
        """
        Descripcion:
            Crea y configura el elemento asociado a crear tabla ranking
            para usarlo dentro del juego o la interfaz.
        
        Entradas:
            parent (object): Valor recibido por la funcion.
            titulo (object): Valor recibido por la funcion.
            ranking (object): Valor recibido por la funcion.
            clave_victorias (object): Valor recibido por la funcion.
            fila_inicial (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        tk.Label(parent, text=titulo, bg=COLOR_TARJETA, fg="#f5f7fb", font=("Arial", 15, "bold"), anchor="w").grid(
            row=fila_inicial, column=0, columnspan=3, sticky="ew", padx=24, pady=(14, 6)
        )
        encabezados = ["#", "Jugador", "Victorias"]
        for columna, texto in enumerate(encabezados):
            tk.Label(parent, text=texto, bg="#dceaf7", fg="#173a59", font=("Arial", 11, "bold"), padx=8, pady=5).grid(
                row=fila_inicial + 1, column=columna, sticky="ew", padx=(24 if columna == 0 else 0, 24 if columna == 2 else 0)
            )

        if not ranking:
            tk.Label(parent, text="Sin jugadores registrados todavía.", bg=COLOR_TARJETA, fg=COLOR_TEXTO_SUAVE, font=("Arial", 11), anchor="w").grid(
                row=fila_inicial + 2, column=0, columnspan=3, sticky="ew", padx=24, pady=8
            )
            return

        for indice, jugador_ranking in enumerate(ranking, start=1):
            fila = fila_inicial + 1 + indice
            fondo = "#fff8e7" if indice == 1 else "#ffffff" if indice % 2 else "#f7f9fb"
            valores = [
                medalla(indice),
                jugador_ranking["nombre_usuario"],
                str(jugador_ranking[clave_victorias]),
            ]
            for columna, texto in enumerate(valores):
                tk.Label(parent, text=texto, bg=fondo, fg="black", font=("Arial", 11, "bold" if indice <= 3 else "normal"), padx=8, pady=5, anchor="w" if columna == 1 else "center").grid(
                    row=fila, column=columna, sticky="ew", padx=(24 if columna == 0 else 0, 24 if columna == 2 else 0)
                )

    boton_volver = tk.Button(
        window_puntajes,
        text="Volver",
        font=("Arial", 12, "bold"),
        width=10,
        height=2,
        bg="#e53935",
        fg="white",
        activebackground="#c62828",
        command=GoPerfilR,
    )
    boton_volver.place(x=24, y=24)

    titulo = tk.Label(
        window_puntajes,
        text="Puntajes",
        font=("Arial", 34, "bold"),
        bg=COLOR_FONDO,
        fg="#f5f7fb",
    )
    titulo.place(relx=0.5, y=72, anchor="center")

    subtitulo = tk.Label(
        window_puntajes,
        text="Revisa tus victorias y compara los mejores jugadores por rol.",
        font=("Arial", 13),
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO_SUAVE,
    )
    subtitulo.place(relx=0.5, y=112, anchor="center")

    tarjeta_mis_puntajes = crear_tarjeta(window_puntajes, 105, 160, 420, 390, "Mis puntajes")
    tarjeta_ranking = crear_tarjeta(window_puntajes, 585, 160, 470, 390, "Puntajes mundiales", COLOR_SECUNDARIO)

    nombre_usuario_actual = obtener_usuario_actual()
    datos_jugador = app.obtener_jugador(nombre_usuario_actual) if nombre_usuario_actual else None

    contenido_mis_puntajes = tk.Frame(tarjeta_mis_puntajes, bg=COLOR_TARJETA)
    contenido_mis_puntajes.pack(fill="both", expand=True, padx=18, pady=18)
    contenido_mis_puntajes.grid_columnconfigure(0, weight=1)
    contenido_mis_puntajes.grid_columnconfigure(1, weight=1)

    if datos_jugador is not None:
        total_victorias = datos_jugador["victorias_defensor"] + datos_jugador["victorias_atacante"]
        tk.Label(
            contenido_mis_puntajes,
            text=f"Jugador: {datos_jugador['nombre_usuario']}",
            bg=COLOR_TARJETA,
            fg="#f5f7fb",
            font=("Arial", 16, "bold"),
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        crear_metrica(contenido_mis_puntajes, "Defensor", datos_jugador["victorias_defensor"], "#1976d2", 0)
        crear_metrica(contenido_mis_puntajes, "Atacante", datos_jugador["victorias_atacante"], "#ef6c00", 1)
        tk.Label(
            contenido_mis_puntajes,
            text=f"Total de victorias: {total_victorias}",
            bg="#edf7ed",
            fg="#1b5e20",
            font=("Arial", 15, "bold"),
            pady=12,
        ).grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(18, 8))
        tk.Label(
            contenido_mis_puntajes,
            text="Gana rondas completas para sumar victorias en tu perfil.",
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO_SUAVE,
            font=("Arial", 11),
            wraplength=340,
            justify="center",
        ).grid(row=3, column=0, columnspan=2, pady=(12, 0))
    else:
        tk.Label(
            contenido_mis_puntajes,
            text="Inicia sesión para ver tus puntajes personales.",
            bg=COLOR_TARJETA,
            fg=COLOR_TEXTO_SUAVE,
            font=("Arial", 15, "bold"),
            wraplength=330,
            justify="center",
        ).pack(expand=True)

    contenido_ranking = tk.Frame(tarjeta_ranking, bg=COLOR_TARJETA)
    contenido_ranking.pack(fill="both", expand=True)
    contenido_ranking.grid_columnconfigure(0, minsize=58)
    contenido_ranking.grid_columnconfigure(1, weight=1)
    contenido_ranking.grid_columnconfigure(2, minsize=100)
    ventana_todos_ref = {"ventana": None}

    def abrir_todos_los_puntajes():
        """
        Descripcion:
            Ejecuta la logica correspondiente a abrir todos los puntajes
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
        ventana_abierta = ventana_todos_ref["ventana"]
        try:
            if ventana_abierta is not None and ventana_abierta.winfo_exists():
                ventana_abierta.lift()
                ventana_abierta.focus_force()
                return
        except tk.TclError:
            ventana_todos_ref["ventana"] = None

        ventana_todos = tk.Toplevel(window_puntajes)
        ventana_todos_ref["ventana"] = ventana_todos
        boton_ver_todos.config(state="disabled")
        ventana_todos.title("Todos los puntajes")
        ventana_todos.configure(bg=COLOR_FONDO)
        ventana_todos.geometry("620x520")

        def cerrar_todos_los_puntajes():
            """
            Descripcion:
                Cierra o libera los recursos asociados a cerrar todos
                los puntajes.
            
            Entradas:
                Ninguna.
            
            Salidas:
                None: Ejecuta la accion y puede modificar el estado
                interno, la interfaz o los datos relacionados.
            
            Restricciones:
                - Requiere que los widgets, ventanas o callbacks usados
                por la interfaz existan antes de ejecutarse.
            """
            ventana_todos_ref["ventana"] = None
            try:
                boton_ver_todos.config(state="normal")
            except tk.TclError:
                pass
            ventana_todos.destroy()

        ventana_todos.protocol("WM_DELETE_WINDOW", cerrar_todos_los_puntajes)
        tk.Label(ventana_todos, text="Todos los puntajes", font=("Arial", 22, "bold"), bg=COLOR_FONDO, fg="#f5f7fb").pack(pady=16)
        marco = tk.Frame(ventana_todos, bg=COLOR_TARJETA, highlightbackground=COLOR_BORDE, highlightthickness=2)
        marco.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        encabezados = ["#", "Jugador", "Def.", "Atq.", "Total"]
        for columna, texto in enumerate(encabezados):
            tk.Label(marco, text=texto, bg="#dceaf7", fg="#173a59", font=("Arial", 11, "bold"), padx=8, pady=6).grid(row=0, column=columna, sticky="ew")
        for columna in range(5):
            marco.grid_columnconfigure(columna, weight=1 if columna == 1 else 0)
        todos = app.obtener_todos_puntajes()
        if not todos:
            tk.Label(marco, text="Sin jugadores registrados todavía.", bg=COLOR_TARJETA, fg=COLOR_TEXTO_SUAVE, font=("Arial", 12)).grid(row=1, column=0, columnspan=5, pady=24)
        for indice, jugador in enumerate(todos, start=1):
            fondo = "#fff8e7" if indice == 1 else "#ffffff" if indice % 2 else "#f7f9fb"
            valores = [indice, jugador["nombre_usuario"], jugador["victorias_defensor"], jugador["victorias_atacante"], jugador["total_victorias"]]
            for columna, valor in enumerate(valores):
                tk.Label(marco, text=str(valor), bg=fondo, fg="black", font=("Arial", 10, "bold" if indice <= 5 else "normal"), padx=8, pady=5, anchor="w" if columna == 1 else "center").grid(row=indice, column=columna, sticky="ew")

    boton_ver_todos = tk.Button(tarjeta_ranking, text="Ver todos los puntajes", font=("Arial", 10, "bold"), bg="#dceaf7", command=abrir_todos_los_puntajes)
    boton_ver_todos.place(relx=0.5, rely=0.94, anchor="center")

    top_defensores = app.obtener_top_defensores()
    top_atacantes = app.obtener_top_atacantes()
    crear_tabla_ranking(contenido_ranking, "Mejores 5 defensores", top_defensores, "victorias_defensor", 0)
    crear_tabla_ranking(contenido_ranking, "Mejores 5 atacantes", top_atacantes, "victorias_atacante", 8)

    pie = tk.Label(
        window_puntajes,
        text="Los rankings se ordenan por la cantidad de victorias guardadas en jugadores.json.",
        font=("Arial", 10, "italic"),
        bg=COLOR_FONDO,
        fg=COLOR_TEXTO_SUAVE,
    )
    pie.place(relx=0.5, y=592, anchor="center")

    window_puntajes.protocol("WM_DELETE_WINDOW", cerrar_todo)
