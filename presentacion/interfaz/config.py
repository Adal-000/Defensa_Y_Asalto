#=======================================#
# Archivo para manejo de configuracion
#=======================================#

import tkinter as tk
from tkinter import messagebox

from aplicacion import app

COLOR_FONDO = "#18202b"
COLOR_TARJETA = "#243244"
COLOR_PRIMARIO = "#1f4e79"
COLOR_BORDE = "#f6b73c"
COLOR_TEXTO = "#f5f7fb"
COLOR_SUAVE = "#b8c7d9"


def config(root, GoMain, cerrar_todo, configurar_ventana):
    """
    Descripción:
        Crea la ventana de configuración con preferencias de interfaz,
        mapa y valores predeterminados de conexión.
    """

    window3 = tk.Toplevel(root)
    configurar_ventana(window3, "Config")
    window3.configure(bg=COLOR_FONDO)

    configuracion_actual = app.obtener_configuracion()
    tema_var = tk.StringVar(value=configuracion_actual["tema"])
    cuadricula_var = tk.BooleanVar(value=configuracion_actual["mostrar_cuadricula"])
    proyectiles_var = tk.BooleanVar(value=configuracion_actual["mostrar_proyectiles"])
    ip_var = tk.StringVar(value=configuracion_actual["ip_servidor_predeterminada"])
    puerto_var = tk.StringVar(value=str(configuracion_actual["puerto_predeterminado"]))

    def GoMainR():
        window3.destroy()
        GoMain()

    def crear_tarjeta(x, y, ancho, alto, titulo):
        tarjeta = tk.Frame(window3, bg=COLOR_TARJETA, highlightbackground=COLOR_BORDE, highlightthickness=2)
        tarjeta.place(x=x, y=y, width=ancho, height=alto)
        tk.Label(tarjeta, text=titulo, bg=COLOR_PRIMARIO, fg="white", font=("Arial", 16, "bold"), pady=8).pack(fill="x")
        return tarjeta

    def aplicar_configuracion():
        try:
            puerto = int(puerto_var.get())
        except ValueError:
            messagebox.showwarning("Puerto inválido", "El puerto debe ser un número entero.")
            return

        if puerto < 1 or puerto > 65535:
            messagebox.showwarning("Puerto inválido", "El puerto debe estar entre 1 y 65535.")
            return

        app.actualizar_configuracion(
            tema=tema_var.get(),
            mostrar_cuadricula=cuadricula_var.get(),
            mostrar_proyectiles=proyectiles_var.get(),
            ip_servidor_predeterminada=ip_var.get().strip() or "127.0.0.1",
            puerto_predeterminado=puerto,
        )
        etiqueta_estado.config(text="Configuración aplicada para esta sesión.", fg="#8ee08e")

    def restablecer_configuracion():
        valores = app.restablecer_configuracion()
        tema_var.set(valores["tema"])
        cuadricula_var.set(valores["mostrar_cuadricula"])
        proyectiles_var.set(valores["mostrar_proyectiles"])
        ip_var.set(valores["ip_servidor_predeterminada"])
        puerto_var.set(str(valores["puerto_predeterminado"]))
        etiqueta_estado.config(text="Configuración restablecida.", fg=COLOR_BORDE)

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
        text="Ajusta opciones visuales del mapa y datos predeterminados de conexión.",
        font=("Arial", 13),
        bg=COLOR_FONDO,
        fg=COLOR_SUAVE,
    )
    subtitulo.place(relx=0.5, y=112, anchor="center")

    tarjeta_visual = crear_tarjeta(120, 160, 420, 300, "Visual y mapa")
    contenido_visual = tk.Frame(tarjeta_visual, bg=COLOR_TARJETA)
    contenido_visual.pack(fill="both", expand=True, padx=24, pady=20)

    tk.Label(contenido_visual, text="Tema de interfaz", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=(0, 6))
    tk.Radiobutton(contenido_visual, text="Claro", variable=tema_var, value="claro", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 11)).pack(anchor="w")
    tk.Radiobutton(contenido_visual, text="Oscuro", variable=tema_var, value="oscuro", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 11)).pack(anchor="w")

    tk.Label(contenido_visual, text="Mapa", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=(18, 6))
    tk.Checkbutton(contenido_visual, text="Mostrar cuadrícula del tablero", variable=cuadricula_var, bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 11)).pack(anchor="w")
    tk.Checkbutton(contenido_visual, text="Mostrar proyectiles durante el combate", variable=proyectiles_var, bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 11)).pack(anchor="w")

    tarjeta_red = crear_tarjeta(610, 160, 420, 300, "Conexión")
    contenido_red = tk.Frame(tarjeta_red, bg=COLOR_TARJETA)
    contenido_red.pack(fill="both", expand=True, padx=24, pady=20)

    tk.Label(contenido_red, text="IP predeterminada del servidor", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 12, "bold"), anchor="w").pack(fill="x")
    campo_ip = tk.Entry(contenido_red, textvariable=ip_var, font=("Arial", 12), width=28)
    campo_ip.pack(anchor="w", pady=(6, 16))

    tk.Label(contenido_red, text="Puerto predeterminado", bg=COLOR_TARJETA, fg=COLOR_TEXTO, font=("Arial", 12, "bold"), anchor="w").pack(fill="x")
    campo_puerto = tk.Entry(contenido_red, textvariable=puerto_var, font=("Arial", 12), width=12)
    campo_puerto.pack(anchor="w", pady=(6, 16))

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
    boton_aplicar.place(x=395, y=500)

    boton_restaurar = tk.Button(window3, text="Restablecer", font=("Arial", 13, "bold"), width=14, bg="#ffd54f", command=restablecer_configuracion)
    boton_restaurar.place(x=575, y=500)

    etiqueta_estado = tk.Label(window3, text="Los cambios aplican durante la sesión actual.", font=("Arial", 11, "bold"), bg=COLOR_FONDO, fg=COLOR_SUAVE)
    etiqueta_estado.place(relx=0.5, y=565, anchor="center")

    window3.protocol("WM_DELETE_WINDOW", cerrar_todo)
