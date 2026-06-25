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

    def mostrar_mensaje(mensaje, color="red"):
        """
        Descripción:
            Muestra un mensaje corto debajo de los campos de texto.

        Entradas:
            mensaje (str): texto que se desea mostrar.
            color (str): color del texto.
        """
        etiqueta_mensaje.config(text=mensaje, fg=color)

    def limpiar_campos():
        """
        Descripción:
            Limpia los campos de usuario y contraseña de la interfaz.
            Se usa principalmente después de un registro exitoso.
        """
        campo_usuario.delete(0, tk.END)
        campo_contrasena.delete(0, tk.END)
        campo_usuario.focus_set()

    def obtener_campos_validos():
        """
        Descripción:
            Lee los campos y verifica errores básicos antes de llamar
            a la lógica interna del programa.

        Salidas:
            tuple[str, str]: usuario y contraseña si ambos campos son válidos.
            None: si falta algún dato.
        """
        usuario = campo_usuario.get().strip()
        contrasena = campo_contrasena.get().strip()

        if not usuario and not contrasena:
            mostrar_mensaje("Ingrese usuario y contraseña.")
            campo_usuario.focus_set()
            return None

        if not usuario:
            mostrar_mensaje("Ingrese el nombre de usuario.")
            campo_usuario.focus_set()
            return None

        if not contrasena:
            mostrar_mensaje("Ingrese la contraseña.")
            campo_contrasena.focus_set()
            return None

        return usuario, contrasena

    def intentar_iniciar_sesion():
        """
        Descripción:
            Lee los campos de usuario y contraseña, valida el inicio
            de sesión con la lógica del juego y, si es correcto,
            guarda el usuario actual y pasa al menú principal.
        """
        datos = obtener_campos_validos()
        if datos is None:
            return

        usuario, contrasena = datos

        try:
            exito, mensaje = app.validar_login(usuario, contrasena)
        except PermissionError:
            messagebox.showerror(
                "Error de acceso",
                "No se tienen permisos para leer los datos de usuarios."
            )
            mostrar_mensaje("No se pudo acceder a los datos de usuarios.")
            return
        except OSError:
            messagebox.showerror(
                "Error de archivo",
                "No se pudo leer el archivo de usuarios. Intente nuevamente."
            )
            mostrar_mensaje("Error al leer los datos de usuarios.")
            return
        except Exception as error:
            messagebox.showerror(
                "Error inesperado",
                f"Ocurrió un problema al iniciar sesión: {error}"
            )
            mostrar_mensaje("No se pudo iniciar sesión en este momento.")
            return

        if exito:
            establecer_usuario_actual(usuario)
            window_login.destroy()
            GoMain()
        else:
            mostrar_mensaje(mensaje)
            campo_contrasena.delete(0, tk.END)
            campo_contrasena.focus_set()

    def intentar_registrarse():
        """
        Descripción:
            Lee los campos de usuario y contraseña y registra un
            nuevo jugador con la lógica del juego, mostrando el
            resultado de la operación.
        """
        datos = obtener_campos_validos()
        if datos is None:
            return

        usuario, contrasena = datos

        try:
            exito, mensaje = app.registrar_jugador(usuario, contrasena)
        except PermissionError:
            messagebox.showerror(
                "Error de acceso",
                "No se tienen permisos para guardar los datos de usuarios."
            )
            mostrar_mensaje("No se pudo guardar el usuario.")
            return
        except OSError:
            messagebox.showerror(
                "Error de archivo",
                "No se pudo escribir en el archivo de usuarios."
            )
            mostrar_mensaje("Error al guardar los datos de usuarios.")
            return
        except Exception as error:
            messagebox.showerror(
                "Error inesperado",
                f"Ocurrió un problema al registrar el usuario: {error}"
            )
            mostrar_mensaje("No se pudo completar el registro.")
            return

        if exito:
            messagebox.showinfo("Registro exitoso", mensaje)
            limpiar_campos()
            mostrar_mensaje("Registro exitoso. Ahora puede iniciar sesión.", "green")
        else:
            mostrar_mensaje(mensaje)
            if "contraseña" in mensaje.lower() or "contrasena" in mensaje.lower():
                campo_contrasena.focus_set()
            else:
                campo_usuario.focus_set()

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

    campo_usuario.focus_set()
    campo_usuario.bind("<Return>", lambda evento: campo_contrasena.focus_set())
    campo_contrasena.bind("<Return>", lambda evento: intentar_iniciar_sesion())
    window_login.protocol("WM_DELETE_WINDOW", cerrar_todo)
