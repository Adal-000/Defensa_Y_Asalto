#=======================================#
# Archivo para manejo de configuracion
#=======================================#

import os
import tkinter as tk
from tkinter import filedialog, messagebox

from aplicacion import app

COLOR_FONDO = "#18202b"
COLOR_TARJETA = "#243244"
COLOR_PRIMARIO = "#1f4e79"
COLOR_BORDE = "#f6b73c"
COLOR_TEXTO = "#f5f7fb"
COLOR_SUAVE = "#b8c7d9"


def config(root, GoMain, cerrar_todo, configurar_ventana):
    """
    Descripcion:
        Crea la ventana de configuración con valores predeterminados de
        conexión para abrir Play.
    
    Entradas:
        root (object): Valor recibido por la funcion.
        GoMain (object): Valor recibido por la funcion.
        cerrar_todo (object): Valor recibido por la funcion.
        configurar_ventana (object): Valor recibido por la funcion.
    
    Salidas:
        None: Ejecuta la accion y puede modificar el estado interno, la
        interfaz o los datos relacionados.
    
    Restricciones:
        - Los parametros recibidos deben respetar el tipo y el formato
        esperado por la funcion.
        - Requiere que los widgets, ventanas o callbacks usados por la
        interfaz existan antes de ejecutarse.
    """

    window3 = tk.Toplevel(root)
    configurar_ventana(window3, "Config")
    window3.configure(bg=COLOR_FONDO)

    configuracion_actual = app.obtener_configuracion()
    ip_var = tk.StringVar(value=configuracion_actual["ip_servidor_predeterminada"])
    puerto_var = tk.StringVar(value=str(configuracion_actual["puerto_predeterminado"]))
    musica_var = tk.StringVar(value=configuracion_actual.get("ruta_musica", "") or app.obtener_ruta_musica_actual())

    def GoMainR():
        # Salir de Configuración ya NO detiene la música: solo el
        # botón "Detener" de esta misma ventana la apaga.
        """
        Descripcion:
            Maneja la navegacion de la interfaz hacia la pantalla o
            accion asociada a GoMainR.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        window3.destroy()
        GoMain()

    def crear_tarjeta(x, y, ancho, alto, titulo):
        """
        Descripcion:
            Crea y configura el elemento asociado a crear tarjeta para
            usarlo dentro del juego o la interfaz.
        
        Entradas:
            x (object): Valor recibido por la funcion.
            y (object): Valor recibido por la funcion.
            ancho (object): Valor recibido por la funcion.
            alto (object): Valor recibido por la funcion.
            titulo (object): Valor recibido por la funcion.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        tarjeta = tk.Frame(window3, bg=COLOR_TARJETA, highlightbackground=COLOR_BORDE, highlightthickness=2)
        tarjeta.place(x=x, y=y, width=ancho, height=alto)
        tk.Label(tarjeta, text=titulo, bg=COLOR_PRIMARIO, fg="white", font=("Arial", 16, "bold"), pady=8).pack(fill="x")
        return tarjeta


    def seleccionar_musica():
        """
        Descripcion:
            Registra la seleccion correspondiente a seleccionar musica.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        ruta = filedialog.askopenfilename(
            title="Selecciona música",
            filetypes=(
                ("Audio", "*.mp3 *.wav *.ogg"),
                ("Todos los archivos", "*.*"),
            ),
        )
        if ruta:
            musica_var.set(ruta)
            etiqueta_estado.config(text="Música seleccionada. Pulsa Reproducir para escucharla.", fg=COLOR_BORDE)

    def reproducir_musica():
        """
        Descripcion:
            Ejecuta la logica correspondiente a reproducir musica dentro
            del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        ruta = musica_var.get().strip()
        if not ruta:
            messagebox.showwarning("Música", "Primero selecciona un archivo de música.")
            return
        if not os.path.exists(ruta):
            messagebox.showwarning("Música", "El archivo seleccionado no existe.")
            return
        exito, mensaje = app.reproducir_musica(ruta)
        if not exito:
            messagebox.showwarning("Música", mensaje)
            etiqueta_estado.config(text=mensaje, fg="#ef9a9a")
            return
        etiqueta_estado.config(text="Reproduciendo música. Sigue sonando en todas las ventanas.", fg="#8ee08e")

    def detener_musica():
        """
        Descripcion:
            Detiene el proceso asociado a detener musica.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        app.detener_musica()
        etiqueta_estado.config(text="Música detenida.", fg=COLOR_SUAVE)

    def aplicar_configuracion():
        """
        Descripcion:
            Ejecuta la logica correspondiente a aplicar configuracion
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
        try:
            puerto = int(puerto_var.get())
        except ValueError:
            messagebox.showwarning("Puerto inválido", "El puerto debe ser un número entero.")
            return

        if puerto < 1 or puerto > 65535:
            messagebox.showwarning("Puerto inválido", "El puerto debe estar entre 1 y 65535.")
            return

        app.actualizar_configuracion(
            ip_servidor_predeterminada=ip_var.get().strip() or "127.0.0.1",
            puerto_predeterminado=puerto,
            ruta_musica=musica_var.get().strip(),
        )
        etiqueta_estado.config(text="Configuración aplicada para esta sesión.", fg="#8ee08e")

    def restablecer_configuracion():
        """
        Descripcion:
            Ejecuta la logica correspondiente a restablecer
            configuracion dentro del flujo del juego.
        
        Entradas:
            Ninguna.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        valores = app.restablecer_configuracion()
        ip_var.set(valores["ip_servidor_predeterminada"])
        puerto_var.set(str(valores["puerto_predeterminado"]))
        musica_var.set(valores.get("ruta_musica", "") or app.obtener_ruta_musica_actual())
        etiqueta_estado.config(text="Configuración restablecida. La música sigue sonando.", fg=COLOR_BORDE)

    boton_volver = tk.Button(
        window3,
        text="Volver",
        font=("Arial", 12, "bold"),
        width=10,
        height=2,
        bg="#e53935",
        fg="white",
        activebackground="#c62828",
        command=GoMainR,
    )
    boton_volver.place(x=24, y=24)

    titulo = tk.Label(window3, text="Configuración", font=("Arial", 34, "bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO)
    titulo.place(relx=0.5, y=70, anchor="center")

    subtitulo = tk.Label(
        window3,
        text="Ajusta los datos predeterminados para conectarte desde Play.",
        font=("Arial", 13),
        bg=COLOR_FONDO,
        fg=COLOR_SUAVE,
    )
    subtitulo.place(relx=0.5, y=112, anchor="center")

    tarjeta_red = crear_tarjeta(115, 170, 420, 300, "Conexión")
    contenido_red = tk.Frame(tarjeta_red, bg=COLOR_TARJETA)
    contenido_red.pack(fill="both", expand=True, padx=24, pady=24)

    tk.Label(contenido_red, text="IP predeterminada del servidor", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 12, "bold"), anchor="w").pack(fill="x")
    campo_ip = tk.Entry(contenido_red, textvariable=ip_var, font=("Arial", 12), width=28)
    campo_ip.pack(anchor="w", pady=(6, 18))

    tk.Label(contenido_red, text="Puerto predeterminado", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 12, "bold"), anchor="w").pack(fill="x")
    campo_puerto = tk.Entry(contenido_red, textvariable=puerto_var, font=("Arial", 12), width=12)
    campo_puerto.pack(anchor="w", pady=(6, 18))

    tk.Label(
        contenido_red,
        text="Estos valores se usan como sugerencia al abrir Play. No cambian las reglas de red del servidor.",
        bg=COLOR_TARJETA,
        fg=COLOR_SUAVE,
        font=("Arial", 10),
        wraplength=340,
        justify="left",
    ).pack(anchor="w", pady=(8, 0))

    boton_aplicar = tk.Button(window3, text="Aplicar", font=("Arial", 13, "bold"), width=14, bg="#81c784", command=aplicar_configuracion)
    tarjeta_musica = crear_tarjeta(620, 170, 450, 300, "Música")
    contenido_musica = tk.Frame(tarjeta_musica, bg=COLOR_TARJETA)
    contenido_musica.pack(fill="both", expand=True, padx=24, pady=24)

    tk.Label(contenido_musica, text="Archivo de música", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 12, "bold"), anchor="w").pack(fill="x")
    campo_musica = tk.Entry(contenido_musica, textvariable=musica_var, font=("Arial", 10), width=46)
    campo_musica.pack(anchor="w", pady=(6, 10))
    tk.Button(contenido_musica, text="Seleccionar desde explorador", font=("Arial", 11, "bold"), bg="#90caf9", command=seleccionar_musica).pack(anchor="w", pady=(0, 12))
    fila_musica = tk.Frame(contenido_musica, bg=COLOR_TARJETA)
    fila_musica.pack(anchor="w")
    tk.Button(fila_musica, text="Reproducir", font=("Arial", 11, "bold"), width=12, bg="#81c784", command=reproducir_musica).pack(side="left", padx=(0, 10))
    tk.Button(fila_musica, text="Detener", font=("Arial", 11, "bold"), width=12, bg="#ef9a9a", command=detener_musica).pack(side="left")
    tk.Label(contenido_musica, text="La ruta se guarda para esta sesión al pulsar Aplicar.", bg=COLOR_TARJETA, fg=COLOR_SUAVE, font=("Arial", 10), wraplength=380, justify="left").pack(anchor="w", pady=(18, 0))

    boton_aplicar.place(x=395, y=510)

    boton_restaurar = tk.Button(window3, text="Restablecer", font=("Arial", 13, "bold"), width=14, bg="#ffd54f", command=restablecer_configuracion)
    boton_restaurar.place(x=575, y=510)

    etiqueta_estado = tk.Label(window3, text="Los cambios aplican durante la sesión actual.", font=("Arial", 11, "bold"), bg=COLOR_FONDO, fg=COLOR_SUAVE)
    etiqueta_estado.place(relx=0.5, y=575, anchor="center")

    window3.protocol("WM_DELETE_WINDOW", cerrar_todo)
