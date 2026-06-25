#=======================================#
# Archivo para inicio de sesion y registro
#=======================================#

import tkinter as tk
from tkinter import messagebox

import app


def login(root, GoMain, cerrar_todo, configurar_ventana, establecer_usuario_actual):
    """
    Descripción:
        Crea la ventana de inicio de sesión y registro. Es la primera
        ventana que ve el jugador antes de entrar al menú principal.

    Entradas:
        root: ventana raíz oculta.
        GoMain: función para abrir el menú principal una vez que el
            jugador inició sesión correctamente.
        cerrar_todo: función para cerrar completamente el programa.
        configurar_ventana: función que centra y configura la ventana.
        establecer_usuario_actual: función que guarda en root.py el
            nombre de usuario que inició sesión, para que las demás
            ventanas (Perfil, Play) sepan quién está jugando.

    Salidas:
        No retorna ningún valor.

    Restricciones:
        No se puede entrar al menú principal sin iniciar sesión o
        registrarse primero.
    """

    window_login = tk.Toplevel(root)
    configurar_ventana(window_login, "Iniciar sesión")

    titulo = tk.Label(
        window_login,
        text="Defensa y Asalto",
        font=("Arial", 32, "bold")
    )
    titulo.place(relx=0.5, rely=0.18, anchor="center")

    contenedor = tk.Frame(window_login)
    contenedor.place(relx=0.5, rely=0.45, anchor="center")

    etiqueta_usuario = tk.Label(contenedor, text="Usuario:", font=("Arial", 14))
    etiqueta_usuario.grid(row=0, column=0, sticky="e", padx=10, pady=10)

    campo_usuario = tk.Entry(contenedor, font=("Arial", 14), width=22)
    campo_usuario.grid(row=0, column=1, padx=10, pady=10)

    etiqueta_contrasena = tk.Label(contenedor, text="Contraseña:", font=("Arial", 14))
    etiqueta_contrasena.grid(row=1, column=0, sticky="e", padx=10, pady=10)

    campo_contrasena = tk.Entry(contenedor, font=("Arial", 14), width=22, show="*")
    campo_contrasena.grid(row=1, column=1, padx=10, pady=10)

    etiqueta_mensaje = tk.Label(window_login, text="", font=("Arial", 13), fg="red")
    etiqueta_mensaje.place(relx=0.5, rely=0.62, anchor="center")

    def intentar_iniciar_sesion():
        """
        Descripción:
            Lee los campos de usuario y contraseña, valida el inicio
            de sesión con la lógica del juego y, si es correcto,
            guarda el usuario actual y pasa al menú principal.
        """
        usuario = campo_usuario.get().strip()
        contrasena = campo_contrasena.get().strip()

        exito, mensaje = app.validar_login(usuario, contrasena)

        if exito:
            establecer_usuario_actual(usuario)
            window_login.destroy()
            GoMain()
        else:
            etiqueta_mensaje.config(text=mensaje)

    def intentar_registrarse():
        """
        Descripción:
            Lee los campos de usuario y contraseña y registra un
            nuevo jugador con la lógica del juego, mostrando el
            resultado de la operación.
        """
        usuario = campo_usuario.get().strip()
        contrasena = campo_contrasena.get().strip()

        exito, mensaje = app.registrar_jugador(usuario, contrasena)

        if exito:
            messagebox.showinfo("Registro exitoso", mensaje)
        etiqueta_mensaje.config(text=mensaje, fg="green" if exito else "red")

    boton_ingresar = tk.Button(
        window_login,
        text="Iniciar sesión",
        font=("Arial", 14, "bold"),
        width=16,
        height=2,
        bg="lightgreen",
        command=intentar_iniciar_sesion
    )
    boton_ingresar.place(relx=0.5, rely=0.74, anchor="center")

    boton_registrar = tk.Button(
        window_login,
        text="Registrarse",
        font=("Arial", 12, "bold"),
        width=14,
        height=1,
        bg="lightblue",
        command=intentar_registrarse
    )
    boton_registrar.place(relx=0.5, rely=0.84, anchor="center")

    window_login.protocol("WM_DELETE_WINDOW", cerrar_todo)
