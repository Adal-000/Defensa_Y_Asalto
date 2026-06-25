#=======================================#
# Archivo para jugar
#=======================================#

import os
import queue
import socket
import sys
import threading
import tkinter as tk
from tkinter import messagebox

RUTA_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RUTA_RED = os.path.join(RUTA_PROYECTO, "Red")

if RUTA_RED not in sys.path:
    sys.path.append(RUTA_RED)

from cliente import ClientePartida, PUERTO_PREDETERMINADO
from protocolo import ACCION_CAMBIAR_FACCION, ACCION_ELEGIR_FACCION, ACCION_LISTO_LOBBY
from servidor import ServidorPartida


FACCIONES = ["Rusia", "España", "Italia", "EE.UU", "Alemania", "Francia"]
COLOR_FONDO = "#f0f0f0"
COLOR_PANEL = "#ffffff"
COLOR_BORDE = "#9a9a9a"
COLOR_SELECCION = "#b7d7ff"
COLOR_LISTO = "#1f8f3a"
COLOR_ALERTA = "#c40000"

LOBBY_LOCAL = {}

DATOS_PARTIDA = {
    "rol": "",
    "usuario": "",
    "faccion": "",
    "puerto": "",
    "modo": "red"
}


def obtener_datos_partida():
    """
    Devuelve los datos básicos de la partida seleccionada.
    Se usa desde root.py o desde el mapa.
    """
    return DATOS_PARTIDA.copy()


class AdaptadorClienteTkinter:
    """
    Descripción:
        Encapsula el cliente de red para que Tkinter procese los
        mensajes recibidos desde el hilo de escucha usando una cola.
    """

    def __init__(self, cola_mensajes):
        self.cola_mensajes = cola_mensajes
        self.cliente = ClientePartida(callback_mensaje=self._recibir_mensaje)

    def _recibir_mensaje(self, mensaje):
        self.cola_mensajes.put(mensaje)

    def conectar(self, host, usuario, rol, puerto):
        return self.cliente.conectar(host, usuario, puerto=puerto, rol=rol)

    def cerrar(self):
        self.cliente.cerrar()


def play(root, GoMain, GoMapa, cerrar_todo, configurar_ventana, obtener_usuario_actual):
    """
    Descripción:
        Crea una sola ventana de sala en red: arriba conserva las
        opciones de conexión y abajo muestra la selección visual de
        facción. La lógica oficial de red se mantiene en ClientePartida
        y ServidorPartida; esta pantalla solo agrega validaciones de
        interfaz para esperar dos jugadores, evitar facciones repetidas
        en la misma sala local y avanzar al mapa cuando ambos están
        listos.
    """

    window2 = tk.Toplevel(root)
    configurar_ventana(window2, "Play en red")
    window2.configure(bg=COLOR_FONDO)

    cola_mensajes = queue.Queue()
    adaptador = AdaptadorClienteTkinter(cola_mensajes)
    servidor_local = {"instancia": None, "hilo": None}
    estado_red = {
        "conectado": False,
        "jugadores_conectados": 0,
        "rol": "",
        "puerto": PUERTO_PREDETERMINADO,
        "usuario": obtener_usuario_actual() or "Invitado",
        "en_espera": False,
    }

    faccion_temporal = tk.StringVar(value="")
    facciones_ocupadas = {}
    listos_remotos = set()
    faccion_confirmada = tk.StringVar(value="")
    seleccion_bloqueada = tk.BooleanVar(value=False)
    listo_para_mapa = tk.BooleanVar(value=False)

    def obtener_clave_sala():
        return str(estado_red["puerto"])

    def obtener_datos_sala():
        clave = obtener_clave_sala()
        if clave not in LOBBY_LOCAL:
            LOBBY_LOCAL[clave] = {"facciones": {}, "listos": set()}
        return LOBBY_LOCAL[clave]

    def registrar_estado_local(listo=False):
        if not estado_red["conectado"] or not estado_red["rol"]:
            return
        sala = obtener_datos_sala()
        if faccion_confirmada.get():
            sala["facciones"][estado_red["rol"]] = faccion_confirmada.get()
        elif estado_red["rol"] in sala["facciones"]:
            del sala["facciones"][estado_red["rol"]]
        if listo:
            sala["listos"].add(estado_red["rol"])
        else:
            sala["listos"].discard(estado_red["rol"])

    def enviar_accion_lobby(accion, **datos):
        if adaptador.cliente.conectado:
            adaptador.cliente.enviar_accion(accion, **datos)

    def sincronizar_lobby_remoto(datos):
        facciones_ocupadas.clear()
        facciones_ocupadas.update(datos.get("facciones_lobby", {}))
        listos_remotos.clear()
        listos_remotos.update(datos.get("listos_lobby", []))
        sala = obtener_datos_sala()
        sala["facciones"] = facciones_ocupadas.copy()
        sala["listos"] = set(listos_remotos)

    def hay_dos_jugadores():
        return estado_red["jugadores_conectados"] >= 2

    def roles_necesarios_listos():
        sala = obtener_datos_sala()
        return {"defensor", "atacante"}.issubset(sala["listos"])

    def facciones_validas_en_sala():
        sala = obtener_datos_sala()
        facciones = sala["facciones"]
        if not {"defensor", "atacante"}.issubset(facciones):
            return False
        return facciones["defensor"] != facciones["atacante"]

    def faccion_esta_ocupada_por_otro(nombre_faccion):
        sala = obtener_datos_sala()
        for rol, faccion in sala["facciones"].items():
            if rol != estado_red["rol"] and faccion == nombre_faccion:
                return True
        return False

    def GoMainR():
        adaptador.cerrar()
        detener_servidor_local()
        window2.destroy()
        GoMain()

    def GoMapaR():
        DATOS_PARTIDA["rol"] = estado_red["rol"]
        DATOS_PARTIDA["usuario"] = estado_red["usuario"]
        DATOS_PARTIDA["faccion"] = faccion_confirmada.get()
        DATOS_PARTIDA["puerto"] = estado_red["puerto"]
        DATOS_PARTIDA["modo"] = "red"

        adaptador.cerrar()
        detener_servidor_local()
        window2.destroy()
        GoMapa()

    def detener_servidor_local():
        if servidor_local["instancia"] is not None:
            servidor_local["instancia"].detener()
            servidor_local["instancia"] = None
            servidor_local["hilo"] = None

    boton_volver = tk.Button(
        window2, text="Volver", font=("Arial", 12, "bold"), width=10,
        height=2, bg="red", command=GoMainR
    )
    boton_volver.place(x=10, y=8)

    titulo = tk.Label(window2, text="Play en red", font=("Arial", 28, "bold"), bg=COLOR_FONDO)
    titulo.place(relx=0.5, y=30, anchor="center")

    panel_superior = tk.Frame(window2, bg=COLOR_PANEL, relief="groove", bd=2, padx=12, pady=10)
    panel_superior.place(relx=0.5, y=82, anchor="center")

    variable_modo_conexion = tk.StringVar(value="crear_servidor")
    tk.Label(panel_superior, text="Modo:", font=("Arial", 11, "bold"), bg=COLOR_PANEL).grid(row=0, column=0, padx=4)
    tk.Radiobutton(panel_superior, text="Crear servidor", variable=variable_modo_conexion, value="crear_servidor", bg=COLOR_PANEL).grid(row=0, column=1, padx=4)
    tk.Radiobutton(panel_superior, text="Unirse a partida", variable=variable_modo_conexion, value="unirse_partida", bg=COLOR_PANEL).grid(row=0, column=2, padx=4)

    tk.Label(panel_superior, text="IP servidor:", font=("Arial", 11), bg=COLOR_PANEL).grid(row=1, column=0, padx=4)
    campo_ip = tk.Entry(panel_superior, font=("Arial", 11), width=15)
    campo_ip.insert(0, "127.0.0.1")
    campo_ip.grid(row=1, column=1, padx=4)

    tk.Label(panel_superior, text="Usuario:", font=("Arial", 11), bg=COLOR_PANEL).grid(row=1, column=2, padx=4)
    campo_usuario = tk.Label(panel_superior, text=obtener_usuario_actual() or "Invitado", font=("Arial", 11, "bold"), width=14, bg=COLOR_PANEL, relief="sunken", anchor="w")
    campo_usuario.grid(row=1, column=3, padx=4)

    tk.Label(panel_superior, text="Rol:", font=("Arial", 11), bg=COLOR_PANEL).grid(row=1, column=4, padx=4)
    variable_rol = tk.StringVar(value="defensor")
    tk.OptionMenu(panel_superior, variable_rol, "defensor", "atacante").grid(row=1, column=5, padx=4)

    tk.Label(panel_superior, text="Puerto:", font=("Arial", 11), bg=COLOR_PANEL).grid(row=1, column=6, padx=4)
    campo_puerto = tk.Entry(panel_superior, font=("Arial", 11), width=7)
    campo_puerto.insert(0, str(PUERTO_PREDETERMINADO))
    campo_puerto.grid(row=1, column=7, padx=4)

    etiqueta_conexion = tk.Label(window2, text="Sin conexión.", font=("Arial", 12, "bold"), fg="red", bg=COLOR_FONDO)
    etiqueta_conexion.place(relx=0.5, y=132, anchor="center")

    panel_facciones = tk.Frame(window2, bg=COLOR_FONDO)
    panel_facciones.place(relx=0.5, y=188, anchor="n")
    botones_faccion = {}

    texto_faccion = tk.Label(window2, text="Elige una facción", font=("Arial", 12, "bold"), width=34, height=2, relief="solid", bd=2, bg=COLOR_FONDO)
    texto_faccion.place(relx=0.5, y=158, anchor="center")

    texto_espera = tk.Label(window2, text="", font=("Arial", 11, "bold"), fg=COLOR_ALERTA, bg=COLOR_FONDO, width=24)
    texto_espera.place(x=900, y=575)

    caja_info_facciones = tk.Listbox(window2, font=("Consolas", 9), width=42, height=5)
    caja_info_facciones.place(x=250, y=535)

    caja_eventos = tk.Listbox(window2, font=("Consolas", 9), width=48, height=5)
    caja_eventos.place(x=595, y=535)

    def agregar_evento(texto):
        if texto:
            caja_eventos.insert(tk.END, texto)
            caja_eventos.yview(tk.END)

    def actualizar_info_facciones(texto=None):
        caja_info_facciones.delete(0, tk.END)
        if texto:
            caja_info_facciones.insert(tk.END, texto)
        if faccion_confirmada.get():
            caja_info_facciones.insert(tk.END, f"Tu facción: {faccion_confirmada.get()}")
        elif faccion_temporal.get():
            caja_info_facciones.insert(tk.END, f"Seleccionada: {faccion_temporal.get()}")
        else:
            caja_info_facciones.insert(tk.END, "Debe elegir una facción.")
        for rol, faccion in obtener_datos_sala()["facciones"].items():
            caja_info_facciones.insert(tk.END, f"{rol}: {faccion}")

    def refrescar_botones():
        for nombre_faccion, boton in botones_faccion.items():
            ocupada = faccion_esta_ocupada_por_otro(nombre_faccion)
            color = "#ffc7c7" if ocupada else COLOR_FONDO
            if nombre_faccion == faccion_temporal.get():
                color = COLOR_SELECCION
            boton.config(relief="sunken" if nombre_faccion == faccion_temporal.get() else "raised", bg=color)
        actualizar_info_facciones()

    def seleccionar_faccion(nombre_faccion):
        if not hay_dos_jugadores():
            texto_faccion.config(text="Esperando al contrincante", fg=COLOR_ALERTA)
            return
        if faccion_esta_ocupada_por_otro(nombre_faccion):
            texto_faccion.config(text="Facción ya elegida", fg=COLOR_ALERTA)
            actualizar_info_facciones("Facción ya elegida por el otro jugador.")
            return
        if seleccion_bloqueada.get():
            cambiar_faccion_click()
        faccion_temporal.set(nombre_faccion)
        texto_faccion.config(text=f"Facción {nombre_faccion}", fg="black")
        refrescar_botones()

    for indice, nombre_faccion in enumerate(FACCIONES):
        fila = indice // 3
        columna = indice % 3
        boton_faccion = tk.Button(
            panel_facciones,
            text=f"┌───────────────┐\n│   Bandera   │\n└───────────────┘\n{nombre_faccion}",
            font=("Arial", 12, "bold"), width=20, height=5,
            command=lambda faccion=nombre_faccion: seleccionar_faccion(faccion)
        )
        boton_faccion.grid(row=fila, column=columna, padx=24, pady=18)
        botones_faccion[nombre_faccion] = boton_faccion

    def elegir_faccion_click():
        if not hay_dos_jugadores():
            texto_faccion.config(text="Esperando al contrincante", fg=COLOR_ALERTA)
            agregar_evento("No se puede elegir facción hasta que haya 2 jugadores.")
            return
        if not faccion_temporal.get():
            texto_faccion.config(text="Elige una facción", fg=COLOR_ALERTA)
            return
        sala = obtener_datos_sala()
        for rol, faccion in sala["facciones"].items():
            if rol != estado_red["rol"] and faccion == faccion_temporal.get():
                texto_faccion.config(text="Facción ya elegida", fg=COLOR_ALERTA)
                agregar_evento("Facción ya elegida por el contrincante.")
                return
        faccion_confirmada.set(faccion_temporal.get())
        seleccion_bloqueada.set(True)
        listo_para_mapa.set(False)
        registrar_estado_local(False)
        enviar_accion_lobby(ACCION_ELEGIR_FACCION, faccion=faccion_confirmada.get())
        texto_faccion.config(text="Facción elegida", fg=COLOR_LISTO)
        refrescar_botones()

    def cambiar_faccion_click():
        seleccion_bloqueada.set(False)
        listo_para_mapa.set(False)
        faccion_confirmada.set("")
        registrar_estado_local(False)
        enviar_accion_lobby(ACCION_CAMBIAR_FACCION)
        texto_espera.config(text="")
        texto_faccion.config(text="Elige una facción" if not faccion_temporal.get() else f"Facción {faccion_temporal.get()}", fg="black")

    def iniciar_combate_click():
        if not hay_dos_jugadores():
            texto_faccion.config(text="Esperando al contrincante", fg=COLOR_ALERTA)
            return
        if not faccion_confirmada.get():
            texto_faccion.config(text="Elige una facción", fg=COLOR_ALERTA)
            return
        listo_para_mapa.set(True)
        estado_red["en_espera"] = True
        registrar_estado_local(True)
        enviar_accion_lobby(ACCION_LISTO_LOBBY)
        if facciones_validas_en_sala() and roles_necesarios_listos():
            GoMapaR()
            return
        texto_espera.config(text="Esperando jugador")
        agregar_evento("Listo. Esperando al contrincante.")

    def buscar_puerto_disponible(puerto_preferido):
        puertos_a_probar = [puerto_preferido] + list(range(5001, 5011)) + list(range(5050, 5061))
        revisados = []
        for puerto_candidato in puertos_a_probar:
            if puerto_candidato in revisados:
                continue
            revisados.append(puerto_candidato)
            try:
                socket_prueba = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_prueba.bind(("0.0.0.0", puerto_candidato))
                socket_prueba.close()
                return True, puerto_candidato, "Puerto disponible."
            except OSError:
                continue
        return False, puerto_preferido, "No se encontró un puerto disponible."

    def iniciar_servidor_local(puerto):
        if servidor_local["instancia"] is not None:
            return True, "Servidor local ya estaba iniciado."
        encontrado, puerto_final, mensaje = buscar_puerto_disponible(puerto)
        if not encontrado:
            return False, mensaje
        servidor = ServidorPartida(puerto=puerto_final)
        hilo = threading.Thread(target=servidor.iniciar, daemon=True)
        servidor_local["instancia"] = servidor
        servidor_local["hilo"] = hilo
        hilo.start()
        campo_puerto.delete(0, tk.END)
        campo_puerto.insert(0, str(puerto_final))
        return True, f"Servidor creado. Otro jugador puede unirse al puerto {puerto_final}."

    def conectar_cliente(host, usuario, rol, puerto):
        estado_red["puerto"] = puerto
        estado_red["usuario"] = usuario
        exito, mensaje = adaptador.conectar(host, usuario, rol, puerto)
        etiqueta_conexion.config(text=mensaje, fg="green" if exito else "red")
        agregar_evento(mensaje)
        if exito:
            estado_red["conectado"] = True
            adaptador.cliente.obtener_estado()

    def conectar_click():
        host = campo_ip.get().strip()
        usuario = estado_red["usuario"]
        rol = variable_rol.get().strip()
        try:
            puerto = int(campo_puerto.get())
        except ValueError:
            messagebox.showwarning("Puerto inválido", "El puerto debe ser un número entero.")
            return
        if variable_modo_conexion.get() == "crear_servidor":
            exito, mensaje = iniciar_servidor_local(puerto)
            etiqueta_conexion.config(text=mensaje, fg="green" if exito else "red")
            agregar_evento(mensaje)
            if not exito:
                return
            puerto = int(campo_puerto.get())
            window2.after(250, lambda: conectar_cliente("127.0.0.1", usuario, rol, puerto))
            return
        conectar_cliente(host, usuario, rol, puerto)

    boton_conectar = tk.Button(panel_superior, text="Continuar", font=("Arial", 11, "bold"), bg="lightgreen", command=conectar_click)
    boton_conectar.grid(row=1, column=8, padx=8)

    boton_cambiar_faccion = tk.Button(window2, text="Cambiar facción", font=("Arial", 12, "bold"), width=16, bg="#ffd36b", command=cambiar_faccion_click)
    boton_cambiar_faccion.place(x=55, y=535)

    boton_elegir_faccion = tk.Button(window2, text="Elegir facción", font=("Arial", 12, "bold"), width=16, bg="lightgreen", command=elegir_faccion_click)
    boton_elegir_faccion.place(x=55, y=585)

    boton_iniciar_combate = tk.Button(window2, text="Jugar", font=("Arial", 13, "bold"), width=18, height=2, bg="orange", command=iniciar_combate_click)
    boton_iniciar_combate.place(x=1030, y=545)

    def procesar_mensajes_red():
        while not cola_mensajes.empty():
            mensaje = cola_mensajes.get()
            texto = mensaje.get("mensaje", "")
            if texto:
                agregar_evento(texto)
            datos = mensaje.get("datos", {})
            if isinstance(datos, dict):
                estado_red["jugadores_conectados"] = int(datos.get("jugadores_conectados", estado_red["jugadores_conectados"]))
                estado_red["rol"] = datos.get("rol_cliente", datos.get("rol", estado_red["rol"]))
                sincronizar_lobby_remoto(datos)
                refrescar_botones()
                if hay_dos_jugadores():
                    etiqueta_conexion.config(text="Sala completa: 2 jugadores conectados.", fg="green")
                elif estado_red["conectado"]:
                    etiqueta_conexion.config(text="Conectado. Esperando al segundo jugador.", fg="orange")
            if estado_red["en_espera"] and facciones_validas_en_sala() and roles_necesarios_listos():
                GoMapaR()
        if window2.winfo_exists():
            window2.after(300, procesar_mensajes_red)

    def cerrar_ventana():
        adaptador.cerrar()
        detener_servidor_local()
        cerrar_todo()

    window2.after(300, procesar_mensajes_red)
    window2.protocol("WM_DELETE_WINDOW", cerrar_ventana)
