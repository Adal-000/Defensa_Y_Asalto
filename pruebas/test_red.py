"""
Descripcion:
    Pruebas basicas para la capa de red del proyecto. No abren una
    partida real en red; validan el protocolo JSON, el cliente sin
    conexion y la asignacion de roles del servidor.

    Para ejecutar estas pruebas desde la raiz del proyecto:
        python -m unittest pruebas.test_red -v
"""

import os
import sys
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
from servidor import ServidorPartida


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


if __name__ == "__main__":
    unittest.main()
