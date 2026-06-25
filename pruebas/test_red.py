"""
Descripcion:
    Pruebas basicas para la capa de red del proyecto. No abren una
    partida real en red; validan el protocolo JSON, el cliente sin
    conexion y la asignacion de roles del servidor.

    Para ejecutar estas pruebas desde la raiz del proyecto:
        python -m unittest pruebas.test_red -v
"""

import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Red"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Logica"))

from protocolo import (
    ACCION_COMPRAR_TORRE,
    ACCION_UNIRSE,
    ErrorProtocolo,
    convertir_a_json_linea,
    convertir_desde_json_linea,
    crear_mensaje,
    obtener_accion,
    obtener_entero,
)
from cliente import ClientePartida
from servidor import (
    FASE_COMBATE,
    FASE_ESPERANDO_JUGADORES,
    FASE_PREPARACION,
    ServidorPartida,
)
import archivos


class PruebasProtocoloRed(unittest.TestCase):
    """
    Descripcion:
        Pruebas relacionadas con la construccion y lectura de mensajes
        JSON usados por el cliente y el servidor.
    """

    def test_crear_mensaje_valido(self):
        """Verifica que se cree correctamente un mensaje permitido."""
        mensaje = crear_mensaje(ACCION_UNIRSE, usuario="ana")

        self.assertEqual(mensaje["accion"], ACCION_UNIRSE)
        self.assertEqual(mensaje["usuario"], "ana")

    def test_crear_mensaje_invalido_falla(self):
        """Verifica que una accion desconocida genere error."""
        with self.assertRaises(ErrorProtocolo):
            crear_mensaje("accion_inventada")

    def test_convertir_json_linea_y_reconstruir(self):
        """Verifica que un mensaje pueda viajar como texto JSON."""
        mensaje_original = crear_mensaje(
            ACCION_COMPRAR_TORRE,
            tipo_torre="arquera",
            fila=2,
            columna=3,
        )
        linea = convertir_a_json_linea(mensaje_original)
        mensaje_reconstruido = convertir_desde_json_linea(linea)

        self.assertEqual(mensaje_reconstruido["tipo_torre"], "arquera")
        self.assertEqual(mensaje_reconstruido["fila"], 2)

    def test_obtener_accion_y_entero(self):
        """Verifica lectura de accion y campos numericos."""
        mensaje = {"accion": ACCION_COMPRAR_TORRE, "fila": "4"}

        self.assertEqual(obtener_accion(mensaje), ACCION_COMPRAR_TORRE)
        self.assertEqual(obtener_entero(mensaje, "fila"), 4)


class PruebasClienteServidorRed(unittest.TestCase):
    """
    Descripcion:
        Pruebas basicas de clases cliente y servidor sin abrir sockets
        reales para evitar dependencia de red en las pruebas unitarias.
    """

    def test_cliente_no_envia_acciones_sin_conexion(self):
        """Verifica que el cliente avise si no esta conectado."""
        cliente = ClientePartida()
        exito, mensaje = cliente.comprar_torre("arquera", 2, 2)

        self.assertFalse(exito)
        self.assertIn("No hay conexion", mensaje)

    def test_servidor_asigna_roles_en_orden(self):
        """Verifica que el primer jugador sea defensor y el segundo atacante."""
        servidor = ServidorPartida()

        rol_uno = servidor._asignar_rol("jugador_uno")
        servidor.clientes_por_rol[rol_uno] = type("ClienteFalso", (), {"usuario": "jugador_uno"})()
        rol_dos = servidor._asignar_rol("jugador_dos")

        self.assertEqual(rol_uno, "defensor")
        self.assertEqual(rol_dos, "atacante")

    def test_cliente_guarda_resumen_de_red_recibido(self):
        """Verifica que el cliente guarde rol, fase y combate activo."""
        cliente = ClientePartida()
        mensaje = {
            "exito": True,
            "mensaje": "Estado actualizado.",
            "datos": {
                "rol_cliente": "defensor",
                "fase_actual": FASE_COMBATE,
                "combate_activo": True,
            },
        }

        cliente._procesar_mensaje_entrante(mensaje)
        resumen = cliente.obtener_resumen_red()

        self.assertEqual(resumen["rol"], "defensor")
        self.assertEqual(resumen["fase_actual"], FASE_COMBATE)
        self.assertTrue(resumen["combate_activo"])

    def test_servidor_valida_usuario_registrado(self):
        """Verifica que el servidor rechace usuarios no registrados."""
        carpeta_temporal = tempfile.mkdtemp()
        ruta_jugadores = os.path.join(carpeta_temporal, "jugadores.json")
        try:
            archivos.registrar_jugador("ana", "1234", ruta_jugadores)
            servidor = ServidorPartida(ruta_jugadores=ruta_jugadores)

            exito_ana, _ = servidor._usuario_puede_conectarse("ana")
            exito_luis, mensaje_luis = servidor._usuario_puede_conectarse("luis")

            self.assertTrue(exito_ana)
            self.assertFalse(exito_luis)
            self.assertIn("no existe", mensaje_luis)
        finally:
            shutil.rmtree(carpeta_temporal)

    def test_servidor_entrega_datos_estado_estandar(self):
        """Verifica que el servidor entregue fase, roles y estado de combate."""
        servidor = ServidorPartida(validar_usuarios=False)
        datos_iniciales = servidor._crear_datos_estado()

        self.assertEqual(datos_iniciales["fase_actual"], FASE_ESPERANDO_JUGADORES)
        self.assertFalse(datos_iniciales["partida_creada"])
        self.assertFalse(datos_iniciales["combate_activo"])

        servidor.partida = type("PartidaFalsa", (), {"partida_finalizada": False})()
        datos_preparacion = servidor._crear_datos_estado()
        self.assertEqual(datos_preparacion["fase_actual"], FASE_PREPARACION)

        servidor.combate_activo = True
        datos_combate = servidor._crear_datos_estado(resultado_combate={"eventos": []})
        self.assertEqual(datos_combate["fase_actual"], FASE_COMBATE)
        self.assertIn("resultado_combate", datos_combate)

    def test_servidor_reinicia_partida_si_no_quedan_clientes(self):
        """Verifica que la sala se limpie cuando todos se desconectan."""
        servidor = ServidorPartida(validar_usuarios=False)

        class ClienteFalso:
            def __init__(self):
                self.usuario = "ana"
                self.rol = "defensor"
                self.conectado = True

            def cerrar(self):
                self.conectado = False

        cliente = ClienteFalso()
        servidor.clientes_por_rol["defensor"] = cliente
        servidor.partida = object()
        servidor.combate_activo = True

        salida_temporal = io.StringIO()
        with contextlib.redirect_stdout(salida_temporal):
            servidor._desconectar_cliente(cliente)

        self.assertIsNone(servidor.clientes_por_rol["defensor"])
        self.assertIsNone(servidor.partida)
        self.assertFalse(servidor.combate_activo)


if __name__ == "__main__":
    unittest.main()
