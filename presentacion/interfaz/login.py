#=======================================#
# Archivo para inicio de sesion y registro
#=======================================#

import tkinter as tk
from tkinter import messagebox

from aplicacion import app

COLOR_FONDO = "#18202b"
COLOR_PANEL = "#243244"
COLOR_DORADO = "#f6b73c"
COLOR_TEXTO = "#f5f7fb"
COLOR_SUAVE = "#b8c7d9"
COLOR_ERROR = "#ff8a80"
COLOR_EXITO = "#9be28f"


def login(root, GoMain, cerrar_todo, configurar_ventana, establecer_usuario_actual):
    """
    Descripcion:
        Crea la ventana de inicio de sesión y registro con estilo de
        juego.
    
    Entradas:
        root (object): Valor recibido por la funcion.
        GoMain (object): Valor recibido por la funcion.
        cerrar_todo (object): Valor recibido por la funcion.
        configurar_ventana (object): Valor recibido por la funcion.
        establecer_usuario_actual (object): Valor recibido por la
        funcion.
    
    Salidas:
        None: Ejecuta la accion y puede modificar el estado interno, la
        interfaz o los datos relacionados.
    
    Restricciones:
        - Los parametros recibidos deben respetar el tipo y el formato
        esperado por la funcion.
        - Requiere que los widgets, ventanas o callbacks usados por la
        interfaz existan antes de ejecutarse.
    """

    window_login = tk.Toplevel(root)
    configurar_ventana(window_login, "Iniciar sesión")
    window_login.configure(bg=COLOR_FONDO)

    fondo = tk.Canvas(window_login, width=1150, height=700, bg=COLOR_FONDO, highlightthickness=0)
    fondo.place(x=0, y=0)
    for x in range(-200, 1150, 90):
        fondo.create_line(x, 0, x + 250, 700, fill="#202b3a", width=1)
    fondo.create_polygon(0, 700, 280, 500, 0, 380, fill="#22324a", outline="")
    fondo.create_polygon(1150, 700, 870, 500, 1150, 380, fill="#3a2630", outline="")

    panel = tk.Frame(window_login, bg=COLOR_PANEL, highlightbackground=COLOR_DORADO, highlightthickness=3)
    panel.place(relx=0.5, rely=0.5, anchor="center", width=520, height=470)

    titulo = tk.Label(panel, text="DEFENSA Y ASALTO", font=("Arial", 27, "bold"), bg=COLOR_PANEL, fg=COLOR_TEXTO)
    titulo.pack(pady=(34, 4))

    subtitulo = tk.Label(panel, text="Acceso del comandante", font=("Arial", 12, "bold"), bg=COLOR_PANEL, fg=COLOR_DORADO)
    subtitulo.pack(pady=(0, 28))

    formulario = tk.Frame(panel, bg=COLOR_PANEL)
    formulario.pack()

    etiqueta_usuario = tk.Label(formulario, text="Usuario", font=("Arial", 12, "bold"), bg=COLOR_PANEL, fg=COLOR_SUAVE, anchor="w")
    etiqueta_usuario.grid(row=0, column=0, sticky="w", padx=8, pady=(0, 5))

    campo_usuario = tk.Entry(formulario, font=("Arial", 14), width=27, relief="flat", bd=4)
    campo_usuario.grid(row=1, column=0, padx=8, pady=(0, 18), ipady=5)

    etiqueta_contrasena = tk.Label(formulario, text="Contraseña", font=("Arial", 12, "bold"), bg=COLOR_PANEL, fg=COLOR_SUAVE, anchor="w")
    etiqueta_contrasena.grid(row=2, column=0, sticky="w", padx=8, pady=(0, 5))

    campo_contrasena = tk.Entry(formulario, font=("Arial", 14), width=27, show="*", relief="flat", bd=4)
    campo_contrasena.grid(row=3, column=0, padx=8, pady=(0, 10), ipady=5)

    etiqueta_mensaje = tk.Label(panel, text="", font=("Arial", 11, "bold"), bg=COLOR_PANEL, fg=COLOR_ERROR, wraplength=390)
    etiqueta_mensaje.pack(pady=(8, 8))

    def estilo_boton(boton, color_base, color_hover):
        """
        Descripcion:
            Ejecuta la logica correspondiente a estilo boton dentro del
            flujo del juego.
        
        Entradas:
            boton (object): Valor recibido por la funcion.
            color_base (object): Valor recibido por la funcion.
            color_hover (object): Valor recibido por la funcion.
        
        Salidas:
            None: Ejecuta la accion y puede modificar el estado interno,
            la interfaz o los datos relacionados.
        
        Restricciones:
            - Los parametros recibidos deben respetar el tipo y el
            formato esperado por la funcion.
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
        """
        boton.bind("<Enter>", lambda _evento: boton.config(bg=color_hover, relief="sunken"))
        boton.bind("<Leave>", lambda _evento: boton.config(bg=color_base, relief="raised"))

    def mostrar_mensaje(mensaje, color=COLOR_ERROR):
        """
        Descripcion:
            Muestra o consulta el estado visible relacionado con mostrar
            mensaje.
        
        Entradas:
            mensaje (object): Valor recibido por la funcion.
            color (object): Valor recibido por la funcion. Valor
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
        etiqueta_mensaje.config(text=mensaje, fg=color)

    def limpiar_campos():
        """
        Descripcion:
            Ejecuta la logica correspondiente a limpiar campos dentro
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
        campo_usuario.delete(0, tk.END)
        campo_contrasena.delete(0, tk.END)
        campo_usuario.focus_set()

    def obtener_campos_validos():
        """
        Descripcion:
            Obtiene la informacion correspondiente a obtener campos
            validos para que otras partes del programa puedan
            utilizarla.
        
        Entradas:
            Ninguna.
        
        Salidas:
            object: Resultado calculado o recuperado por la operacion.
        
        Restricciones:
            - Requiere que los widgets, ventanas o callbacks usados por
            la interfaz existan antes de ejecutarse.
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
        Descripcion:
            Ejecuta la logica correspondiente a intentar iniciar sesion
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
        datos = obtener_campos_validos()
        if datos is None:
            return
        usuario, contrasena = datos
        try:
            exito, mensaje = app.validar_login(usuario, contrasena)
        except PermissionError:
            messagebox.showerror("Error de acceso", "No se tienen permisos para leer los datos de usuarios.")
            mostrar_mensaje("No se pudo acceder a los datos de usuarios.")
            return
        except OSError:
            messagebox.showerror("Error de archivo", "No se pudo leer el archivo de usuarios. Intente nuevamente.")
            mostrar_mensaje("Error al leer los datos de usuarios.")
            return
        except Exception as error:
            messagebox.showerror("Error inesperado", f"Ocurrió un problema al iniciar sesión: {error}")
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
        Descripcion:
            Ejecuta la logica correspondiente a intentar registrarse
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
        datos = obtener_campos_validos()
        if datos is None:
            return
        usuario, contrasena = datos
        try:
            exito, mensaje = app.registrar_jugador(usuario, contrasena)
        except PermissionError:
            messagebox.showerror("Error de acceso", "No se tienen permisos para guardar los datos de usuarios.")
            mostrar_mensaje("No se pudo guardar el usuario.")
            return
        except OSError:
            messagebox.showerror("Error de archivo", "No se pudo escribir en el archivo de usuarios.")
            mostrar_mensaje("Error al guardar los datos de usuarios.")
            return
        except Exception as error:
            messagebox.showerror("Error inesperado", f"Ocurrió un problema al registrar el usuario: {error}")
            mostrar_mensaje("No se pudo completar el registro.")
            return

        if exito:
            messagebox.showinfo("Registro exitoso", mensaje)
            limpiar_campos()
            mostrar_mensaje("Registro exitoso. Ahora puede iniciar sesión.", COLOR_EXITO)
        else:
            mostrar_mensaje(mensaje)
            if "contraseña" in mensaje.lower() or "contrasena" in mensaje.lower():
                campo_contrasena.focus_set()
            else:
                campo_usuario.focus_set()

    boton_ingresar = tk.Button(panel, text="⚔ Iniciar sesión", font=("Arial", 14, "bold"), width=22, height=2, bg="#d94b4b", fg="white", activebackground=COLOR_DORADO, bd=4, cursor="hand2", command=intentar_iniciar_sesion)
    boton_ingresar.pack(pady=(6, 12))
    estilo_boton(boton_ingresar, "#d94b4b", COLOR_DORADO)

    boton_registrar = tk.Button(panel, text="Crear comandante", font=("Arial", 11, "bold"), width=18, bg="#3f8cff", fg="white", activebackground=COLOR_DORADO, bd=3, cursor="hand2", command=intentar_registrarse)
    boton_registrar.pack()
    estilo_boton(boton_registrar, "#3f8cff", COLOR_DORADO)

    campo_usuario.focus_set()
    campo_usuario.bind("<Return>", lambda evento: campo_contrasena.focus_set())
    campo_contrasena.bind("<Return>", lambda evento: intentar_iniciar_sesion())
    window_login.protocol("WM_DELETE_WINDOW", cerrar_todo)
