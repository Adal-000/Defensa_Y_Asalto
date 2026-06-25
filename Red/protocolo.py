"""
Descripcion:
    Protocolo de red para el modo multijugador LAN de "Defensa y
    Asalto de Base". Define acciones, tipos de respuesta y funciones
    para enviar mensajes JSON por sockets usando un mensaje por linea.

    Se mantiene simple para el curso de Introduccion a la Programacion:
    solo usa json, sockets y datos basicos de Python.
"""

import json

CODIFICACION = "utf-8"
SEPARADOR_MENSAJE = "\n"

ACCION_REGISTRAR = "registrar_jugador"
ACCION_LOGIN = "validar_login"
ACCION_UNIRSE = "unirse"
ACCION_COMPRAR_TORRE = "comprar_torre"
ACCION_COMPRAR_MURO = "comprar_muro"
ACCION_COMPRAR_UNIDAD = "comprar_unidad"
ACCION_INICIAR_COMBATE = "iniciar_combate"
ACCION_PAUSAR_COMBATE = "pausar_combate"
ACCION_EJECUTAR_COMBATE = "ejecutar_combate"
ACCION_OBTENER_ESTADO = "obtener_estado"
ACCION_ELEGIR_FACCION = "elegir_faccion"
ACCION_CAMBIAR_FACCION = "cambiar_faccion"
ACCION_LISTO_LOBBY = "listo_lobby"
ACCION_SALIR = "salir"
ACCION_DESCONECTAR = ACCION_SALIR
ACCION_PING = "ping"

TIPO_CONEXION = "conexion"
TIPO_RESULTADO = "resultado"
TIPO_ESTADO = "estado"
TIPO_ERROR = "error"
TIPO_EVENTO = "evento"
TIPO_RESPUESTA = "respuesta"

ROL_DEFENSOR = "defensor"
ROL_ATACANTE = "atacante"
ROLES_PERMITIDOS = {ROL_DEFENSOR, ROL_ATACANTE}
ROLES_VALIDOS = (ROL_DEFENSOR, ROL_ATACANTE)

ACCIONES_PERMITIDAS = {
    ACCION_REGISTRAR,
    ACCION_LOGIN,
    ACCION_UNIRSE,
    ACCION_COMPRAR_TORRE,
    ACCION_COMPRAR_MURO,
    ACCION_COMPRAR_UNIDAD,
    ACCION_INICIAR_COMBATE,
    ACCION_PAUSAR_COMBATE,
    ACCION_EJECUTAR_COMBATE,
    ACCION_OBTENER_ESTADO,
    ACCION_ELEGIR_FACCION,
    ACCION_CAMBIAR_FACCION,
    ACCION_LISTO_LOBBY,
    ACCION_SALIR,
    ACCION_PING,
}


class ErrorProtocolo(ValueError):
    """
    Descripcion:
        Error personalizado usado cuando un mensaje de red no cumple
        con el formato esperado del protocolo.

    Entradas:
        mensaje (str): Explicacion del error encontrado.

    Salidas:
        No retorna nada. Se utiliza como excepcion.

    Restricciones:
        - Debe usarse solamente para errores del formato del mensaje.
    """



def crear_mensaje(accion, **datos):
    """
    Descripcion:
        Crea un mensaje de accion para enviarlo desde un cliente hacia
        el servidor.

    Entradas:
        accion (str): Accion que se desea ejecutar en el servidor.
        **datos: Datos adicionales necesarios para la accion.

    Salidas:
        dict: Mensaje listo para enviarse como JSON.

    Restricciones:
        - accion debe estar dentro de ACCIONES_PERMITIDAS.
    """
    accion_normalizada = str(accion).strip().lower()

    if accion_normalizada not in ACCIONES_PERMITIDAS:
        raise ErrorProtocolo("La accion indicada no existe en el protocolo.")

    mensaje = {"accion": accion_normalizada}
    mensaje.update(datos)
    return mensaje



def crear_respuesta(tipo_o_exito, exito=True, mensaje="", estado=None, datos=None,
                    eventos=None, tipo=None):
    """
    Descripcion:
        Crea una respuesta estandar para enviarla desde el servidor a
        los clientes. Acepta el formato usado por el servidor
        (tipo, exito, mensaje) y tambien un formato simple
        (exito, mensaje) para pruebas.

    Entradas:
        tipo_o_exito (str | bool): Tipo de respuesta o exito directo.
        exito (bool | str): Exito de la accion. Si tipo_o_exito es
            booleano, este parametro se interpreta como mensaje.
        mensaje (str): Mensaje descriptivo para la interfaz o consola.
        estado (dict): Estado actual de la partida. Puede ser None.
        datos (dict): Datos adicionales. Puede ser None.
        eventos (list): Eventos de combate. Puede ser None.
        tipo (str): Tipo explicito cuando se usa el formato simple.

    Salidas:
        dict: Respuesta lista para enviarse como JSON.

    Restricciones:
        - tipo debe ser texto no vacio cuando se usa formato completo.
    """
    if isinstance(tipo_o_exito, bool):
        tipo_respuesta = tipo if tipo is not None else TIPO_RESPUESTA
        exito_respuesta = tipo_o_exito
        mensaje_respuesta = str(exito) if isinstance(exito, str) else mensaje
    else:
        tipo_respuesta = str(tipo_o_exito)
        exito_respuesta = bool(exito)
        mensaje_respuesta = mensaje

    respuesta = {
        "tipo": tipo_respuesta,
        "exito": exito_respuesta,
        "mensaje": mensaje_respuesta,
    }

    if estado is not None:
        respuesta["estado"] = estado

    if datos is not None:
        respuesta["datos"] = datos

    if eventos is not None:
        respuesta["eventos"] = eventos

    return respuesta



def convertir_a_json_linea(mensaje):
    """
    Descripcion:
        Convierte un diccionario de mensaje a texto JSON terminado en
        salto de linea.

    Entradas:
        mensaje (dict): Mensaje que se desea convertir.

    Salidas:
        str: Texto JSON con salto de linea final.

    Restricciones:
        - mensaje debe poder serializarse con json.dumps.
    """
    return json.dumps(mensaje, ensure_ascii=False) + SEPARADOR_MENSAJE



def serializar_mensaje(mensaje):
    """
    Descripcion:
        Convierte un diccionario de mensaje a bytes para enviarlo por
        socket.

    Entradas:
        mensaje (dict): Mensaje que se desea enviar.

    Salidas:
        bytes: Mensaje JSON codificado en UTF-8.

    Restricciones:
        - mensaje debe ser compatible con JSON.
    """
    return convertir_a_json_linea(mensaje).encode(CODIFICACION)



def convertir_desde_json_linea(linea):
    """
    Descripcion:
        Convierte una linea JSON recibida por red en un diccionario.

    Entradas:
        linea (str | bytes): Linea recibida por socket.

    Salidas:
        dict: Mensaje reconstruido.
        None: Si la linea viene vacia porque se cerro la conexion.

    Restricciones:
        - linea debe contener un JSON valido.
        - El JSON debe representar un diccionario.
    """
    if linea is None or linea == "":
        return None

    if isinstance(linea, bytes):
        linea = linea.decode(CODIFICACION)

    try:
        mensaje = json.loads(linea)
    except json.JSONDecodeError as error:
        raise ErrorProtocolo("El mensaje recibido no tiene formato JSON valido.") from error

    if not isinstance(mensaje, dict):
        raise ErrorProtocolo("El mensaje recibido debe ser un diccionario JSON.")

    return mensaje



def decodificar_linea(linea):
    """
    Descripcion:
        Alias de convertir_desde_json_linea para pruebas o modulos que
        usen nombres mas descriptivos.

    Entradas:
        linea (str | bytes): Linea recibida por socket.

    Salidas:
        dict: Mensaje reconstruido.

    Restricciones:
        - linea debe contener un JSON valido.
    """
    mensaje = convertir_desde_json_linea(linea)
    if mensaje is None:
        raise ErrorProtocolo("Mensaje vacio.")
    return mensaje



def enviar_mensaje(conexion, mensaje):
    """
    Descripcion:
        Envia un mensaje JSON por medio de un socket.

    Entradas:
        conexion (socket): Socket conectado hacia otro equipo.
        mensaje (dict): Mensaje que se desea enviar.

    Salidas:
        None: Escribe datos en el socket.

    Restricciones:
        - conexion debe estar abierta.
        - mensaje debe ser serializable a JSON.
    """
    conexion.sendall(serializar_mensaje(mensaje))



def recibir_mensaje(archivo_lectura):
    """
    Descripcion:
        Lee un mensaje JSON desde un archivo de lectura asociado a un
        socket, creado normalmente con socket.makefile("r").

    Entradas:
        archivo_lectura (TextIO): Flujo de lectura del socket.

    Salidas:
        dict: Mensaje recibido.
        None: Si la conexion fue cerrada.

    Restricciones:
        - archivo_lectura debe entregar una linea completa por mensaje.
    """
    linea = archivo_lectura.readline()

    if linea == "":
        return None

    return convertir_desde_json_linea(linea)



def obtener_accion(mensaje):
    """
    Descripcion:
        Obtiene y valida la accion incluida en un mensaje recibido.

    Entradas:
        mensaje (dict): Mensaje recibido por red.

    Salidas:
        str: Accion normalizada.

    Restricciones:
        - mensaje debe tener la llave "accion".
        - accion debe estar en ACCIONES_PERMITIDAS.
    """
    if not isinstance(mensaje, dict):
        raise ErrorProtocolo("El mensaje debe ser un diccionario.")

    accion = str(mensaje.get("accion", "")).strip().lower()
    if accion not in ACCIONES_PERMITIDAS:
        raise ErrorProtocolo("La accion recibida no existe en el protocolo.")

    return accion



def obtener_texto(mensaje, llave, obligatorio=True, valor_por_defecto=""):
    """
    Descripcion:
        Lee un campo de texto de un mensaje de red.

    Entradas:
        mensaje (dict): Mensaje recibido.
        llave (str): Nombre del campo que se desea leer.
        obligatorio (bool): Indica si el campo es requerido.
        valor_por_defecto (str): Valor usado si no es obligatorio y no existe.

    Salidas:
        str: Texto obtenido del mensaje.

    Restricciones:
        - Si obligatorio es True, el campo no puede venir vacio.
    """
    valor = str(mensaje.get(llave, valor_por_defecto)).strip()

    if obligatorio and valor == "":
        raise ErrorProtocolo(f"Falta el campo obligatorio: {llave}.")

    return valor



def obtener_entero(mensaje, llave, obligatorio=True, valor_por_defecto=0):
    """
    Descripcion:
        Lee un campo numerico entero de un mensaje de red.

    Entradas:
        mensaje (dict): Mensaje recibido.
        llave (str): Nombre del campo que se desea leer.
        obligatorio (bool): Indica si el campo es requerido.
        valor_por_defecto (int): Valor usado si no es obligatorio y no existe.

    Salidas:
        int: Numero entero obtenido del mensaje.

    Restricciones:
        - Si el valor no puede convertirse a entero, lanza ErrorProtocolo.
    """
    if llave not in mensaje:
        if obligatorio:
            raise ErrorProtocolo(f"Falta el campo obligatorio: {llave}.")
        return valor_por_defecto

    try:
        return int(mensaje[llave])
    except (TypeError, ValueError) as error:
        raise ErrorProtocolo(f"El campo {llave} debe ser un numero entero.") from error
