"""
Descripcion:
    Modulo de pruebas basicas para la logica del Desarrollador 2 del
    proyecto "Defensa y Asalto de Base". Cubre registro, login,
    carga y guardado de jugadores, compra de torres y unidades,
    daño a unidades/torres/base, condiciones de victoria y ranking.

    Para ejecutar estas pruebas desde la raiz del proyecto:
        python -m unittest pruebas.test_logica -v
"""

import sys
import os
import unittest
import tempfile
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Logica"))

from jugador import Jugador
from base import Base
from torre import crear_torre_por_tipo
from unidad import crear_unidad_por_tipo
from muro import crear_muro
from combate import ejecutar_turno_de_combate
from partida import Partida
import archivos
import ranking


class PruebasJugadorYArchivos(unittest.TestCase):
    """
    Descripcion:
        Pruebas relacionadas con la clase Jugador y el sistema de
        archivos: registro, inicio de sesion, carga y guardado.
    """

    def setUp(self):
        """
        Descripcion:
            Prepara un archivo temporal de jugadores para que cada
            prueba se ejecute de forma aislada, sin afectar el
            archivo real del proyecto.

        Entradas:
            Ninguna.

        Salidas:
            None: Define self.carpeta_temporal y self.ruta_prueba.

        Restricciones:
            Ninguna.
        """
        self.carpeta_temporal = tempfile.mkdtemp()
        self.ruta_prueba = os.path.join(self.carpeta_temporal, "jugadores.json")

    def tearDown(self):
        """
        Descripcion:
            Elimina la carpeta temporal creada para las pruebas una
            vez que estas finalizan.

        Entradas:
            Ninguna.

        Salidas:
            None: Borra self.carpeta_temporal del disco.

        Restricciones:
            Ninguna.
        """
        shutil.rmtree(self.carpeta_temporal)

    def test_jugador_a_diccionario_y_desde_diccionario(self):
        """Verifica que un Jugador se pueda convertir a dict y reconstruir."""
        jugador_original = Jugador("ana", "clave1", 2, 3)
        datos = jugador_original.a_diccionario()
        jugador_reconstruido = Jugador.desde_diccionario(datos)

        self.assertEqual(jugador_original.nombre_usuario, jugador_reconstruido.nombre_usuario)
        self.assertEqual(jugador_original.victorias_defensor, jugador_reconstruido.victorias_defensor)
        self.assertEqual(jugador_original.victorias_atacante, jugador_reconstruido.victorias_atacante)

    def test_registro_de_jugador_exitoso(self):
        """Verifica que un jugador nuevo se registre correctamente."""
        exito, _ = archivos.registrar_jugador("carlos", "1234", self.ruta_prueba)
        self.assertTrue(exito)

        jugadores_guardados = archivos.cargar_jugadores(self.ruta_prueba)
        self.assertEqual(len(jugadores_guardados), 1)
        self.assertEqual(jugadores_guardados[0].nombre_usuario, "carlos")

    def test_registro_de_jugador_repetido_falla(self):
        """Verifica que no se pueda registrar dos veces el mismo usuario."""
        archivos.registrar_jugador("carlos", "1234", self.ruta_prueba)
        exito, mensaje = archivos.registrar_jugador("carlos", "otraclave", self.ruta_prueba)

        self.assertFalse(exito)
        self.assertIn("ya esta en uso", mensaje)

    def test_validar_login_correcto(self):
        """Verifica que el login funcione con credenciales correctas."""
        archivos.registrar_jugador("maria", "abcd", self.ruta_prueba)
        exito, _ = archivos.validar_login("maria", "abcd", self.ruta_prueba)
        self.assertTrue(exito)

    def test_validar_login_contrasena_incorrecta(self):
        """Verifica que el login falle si la contrasena es incorrecta."""
        archivos.registrar_jugador("maria", "abcd", self.ruta_prueba)
        exito, mensaje = archivos.validar_login("maria", "incorrecta", self.ruta_prueba)

        self.assertFalse(exito)
        self.assertIn("incorrecta", mensaje)

    def test_carga_y_guardado_de_jugadores(self):
        """Verifica que guardar y luego cargar jugadores preserve los datos."""
        lista_original = [Jugador("pedro", "clave", 1, 2)]
        archivos.guardar_jugadores(lista_original, self.ruta_prueba)

        lista_cargada = archivos.cargar_jugadores(self.ruta_prueba)

        self.assertEqual(len(lista_cargada), 1)
        self.assertEqual(lista_cargada[0].nombre_usuario, "pedro")
        self.assertEqual(lista_cargada[0].victorias_defensor, 1)

    def test_actualizar_victoria_incrementa_contador(self):
        """Verifica que actualizar_victoria incremente el contador correcto."""
        archivos.registrar_jugador("luisa", "clave", self.ruta_prueba)
        archivos.actualizar_victoria("luisa", "atacante", self.ruta_prueba)

        jugador_actualizado = archivos.buscar_jugador("luisa", self.ruta_prueba)
        self.assertEqual(jugador_actualizado.victorias_atacante, 1)


class PruebasTorresYUnidades(unittest.TestCase):
    """
    Descripcion:
        Pruebas relacionadas con la creacion de torres y unidades, y
        la aplicacion de dano sobre ellas.
    """

    def test_creacion_de_torre_valida(self):
        """Verifica que se pueda crear una torre por tipo valido."""
        torre = crear_torre_por_tipo("arquera", fila=1, columna=1)
        self.assertIsNotNone(torre)
        self.assertEqual(torre.nombre, "Torre Arquera")

    def test_creacion_de_torre_invalida(self):
        """Verifica que un tipo de torre invalido devuelva None."""
        torre = crear_torre_por_tipo("inexistente", fila=1, columna=1)
        self.assertIsNone(torre)

    def test_creacion_de_unidad_valida(self):
        """Verifica que se pueda crear una unidad por tipo valido."""
        unidad = crear_unidad_por_tipo("soldado", fila=5, columna=1)
        self.assertIsNotNone(unidad)
        self.assertEqual(unidad.nombre, "Soldado")

    def test_dano_a_torre_la_destruye(self):
        """Verifica que una torre se destruya al recibir dano suficiente."""
        torre = crear_torre_por_tipo("hielo", fila=1, columna=1)
        torre.recibir_dano(1000)
        self.assertTrue(torre.esta_destruida())

    def test_dano_a_unidad_la_elimina(self):
        """Verifica que una unidad se elimine al recibir dano suficiente."""
        unidad = crear_unidad_por_tipo("explorador", fila=1, columna=1)
        unidad.recibir_dano(1000)
        self.assertTrue(unidad.esta_eliminada())

    def test_dano_a_base_la_destruye(self):
        """Verifica que la base se marque como destruida al llegar a cero vida."""
        base = Base(vida_inicial=30)
        base.recibir_dano(30)
        self.assertTrue(base.fue_destruida())


class PruebasCombate(unittest.TestCase):
    """
    Descripcion:
        Pruebas relacionadas con la fase de combate entre torres,
        unidades y la base central.
    """

    def test_unidad_llega_y_dana_la_base(self):
        """Verifica que una unidad ubicada en la fila de la base la dane."""
        base = Base(vida_inicial=50)
        unidad = crear_unidad_por_tipo("demoledor", fila=0, columna=2)

        _, unidades_restantes = ejecutar_turno_de_combate([], [unidad], base, 0)

        self.assertLess(base.vida, 50)

    def test_torre_ataca_unidad_en_rango(self):
        """Verifica que una torre dane a una unidad dentro de su alcance."""
        torre = crear_torre_por_tipo("arquera", fila=3, columna=2)
        unidad = crear_unidad_por_tipo("soldado", fila=3, columna=2)

        torres_restantes, unidades_restantes = ejecutar_turno_de_combate(
            [torre], [unidad], Base(), 0
        )

        unidad_resultante = unidades_restantes[0] if unidades_restantes else None
        if unidad_resultante is not None:
            self.assertLess(unidad_resultante.vida, unidad.vida_maxima)

    def test_torre_hielo_congela_unidad(self):
        """Verifica que la habilidad de hielo congele una unidad en rango."""
        torre = crear_torre_por_tipo("hielo", fila=2, columna=2)
        unidad = crear_unidad_por_tipo("soldado", fila=2, columna=2)

        ejecutar_turno_de_combate([torre], [unidad], Base(), 0)

        self.assertTrue(unidad.congelada)

    def test_torre_canon_dana_varias_unidades(self):
        """Verifica que el canón use daño en área contra varias unidades."""
        torre = crear_torre_por_tipo("cañon", fila=3, columna=2)
        unidad_uno = crear_unidad_por_tipo("escudero", fila=3, columna=2)
        unidad_dos = crear_unidad_por_tipo("soldado", fila=3, columna=3)

        ejecutar_turno_de_combate([torre], [unidad_uno, unidad_dos], Base(), 0)

        self.assertLess(unidad_uno.vida, unidad_uno.vida_maxima)
        self.assertLess(unidad_dos.vida, unidad_dos.vida_maxima)

    def test_soldado_aplica_ataque_doble_a_base(self):
        """Verifica que la habilidad ataque doble haga daño adicional."""
        base = Base(vida_inicial=100)
        unidad = crear_unidad_por_tipo("soldado", fila=0, columna=1)

        ejecutar_turno_de_combate([], [unidad], base, 0)

        self.assertEqual(base.vida, 76)

    def test_muro_detiene_unidad_y_recibe_dano(self):
        """Verifica que un muro bloquee a la unidad y reciba daño."""
        base = Base(vida_inicial=100)
        muro = crear_muro(fila=9, columna=1)
        unidad = crear_unidad_por_tipo("soldado", fila=10, columna=1)

        _, unidades_restantes, muros_restantes = ejecutar_turno_de_combate(
            [], [unidad], base, 0, lista_muros=[muro]
        )

        self.assertEqual(unidades_restantes[0].fila, 9)
        self.assertLess(muros_restantes[0].vida, muros_restantes[0].vida_maxima)



class PruebasPartida(unittest.TestCase):
    """
    Descripcion:
        Pruebas relacionadas con la clase Partida: compra de torres
        y unidades, y condiciones de victoria.
    """

    def test_comprar_torre_con_dinero_suficiente(self):
        """Verifica que el defensor pueda comprar una torre si tiene dinero."""
        partida = Partida("defensor_prueba", "atacante_prueba")
        exito, _ = partida.comprar_torre("arquera", fila=2, columna=2)

        self.assertTrue(exito)
        self.assertEqual(len(partida.torres), 1)

    def test_comprar_torre_sin_dinero_suficiente_falla(self):
        """Verifica que no se pueda comprar una torre sin dinero suficiente."""
        partida = Partida("defensor_prueba", "atacante_prueba")
        partida.dinero_defensor = 10
        exito, _ = partida.comprar_torre("cañon", fila=2, columna=2)

        self.assertFalse(exito)

    def test_comprar_unidad_con_dinero_suficiente(self):
        """Verifica que el atacante pueda comprar una unidad si tiene dinero."""
        partida = Partida("defensor_prueba", "atacante_prueba")
        exito, _ = partida.comprar_unidad("soldado", fila=10, columna=1)

        self.assertTrue(exito)
        self.assertEqual(len(partida.unidades), 1)

    def test_defensor_gana_ronda_sin_unidades_atacantes(self):
        """Verifica que el defensor gane la ronda si el atacante no tiene unidades."""
        partida = Partida("defensor_prueba", "atacante_prueba")
        partida.dinero_atacante = 0

        resultado = partida.ejecutar_combate()

        self.assertTrue(resultado["ronda_finalizada"])
        self.assertEqual(partida.rondas_ganadas_defensor, 1)

    def test_atacante_gana_ronda_al_destruir_base(self):
        """Verifica que el atacante gane la ronda si destruye la base."""
        partida = Partida("defensor_prueba", "atacante_prueba")
        partida.base.vida = 1

        unidad_demoledora = crear_unidad_por_tipo("demoledor", fila=0, columna=1)
        partida.unidades.append(unidad_demoledora)

        resultado = partida.ejecutar_combate()

        self.assertTrue(resultado["ronda_finalizada"])
        self.assertEqual(partida.rondas_ganadas_atacante, 1)

    def test_comprar_muro_con_dinero_suficiente(self):
        """Verifica que el defensor pueda comprar un muro."""
        partida = Partida("defensor_prueba", "atacante_prueba")
        exito, _ = partida.comprar_muro(fila=4, columna=1)

        self.assertTrue(exito)
        self.assertEqual(len(partida.muros), 1)

    def test_no_permite_dos_defensas_en_misma_posicion(self):
        """Verifica que no se coloquen dos defensas en la misma casilla."""
        partida = Partida("defensor_prueba", "atacante_prueba")
        partida.comprar_torre("arquera", fila=2, columna=2)
        exito, _ = partida.comprar_muro(fila=2, columna=2)

        self.assertFalse(exito)

    def test_no_permite_unidad_fuera_del_tablero(self):
        """Verifica que una unidad fuera del tablero no pueda comprarse."""
        partida = Partida("defensor_prueba", "atacante_prueba")
        exito, _ = partida.comprar_unidad("soldado", fila=99, columna=1)

        self.assertFalse(exito)

    def test_atacante_gana_dinero_por_danar_base(self):
        """Verifica que el atacante reciba dinero al dañar la base."""
        partida = Partida("defensor_prueba", "atacante_prueba")
        partida.dinero_atacante = 0
        partida.unidades.append(crear_unidad_por_tipo("soldado", fila=0, columna=1))

        partida.ejecutar_combate()

        self.assertGreater(partida.dinero_atacante, 0)



class PruebasRanking(unittest.TestCase):
    """
    Descripcion:
        Pruebas relacionadas con la generacion de los rankings de
        mejores defensores y atacantes.
    """

    def setUp(self):
        """Prepara un archivo temporal con jugadores de prueba."""
        self.carpeta_temporal = tempfile.mkdtemp()
        self.ruta_prueba = os.path.join(self.carpeta_temporal, "jugadores.json")

        lista_jugadores = [
            Jugador("jugador_a", "clave", victorias_defensor=5, victorias_atacante=1),
            Jugador("jugador_b", "clave", victorias_defensor=2, victorias_atacante=8),
            Jugador("jugador_c", "clave", victorias_defensor=9, victorias_atacante=3),
        ]
        archivos.guardar_jugadores(lista_jugadores, self.ruta_prueba)

    def tearDown(self):
        """Elimina la carpeta temporal usada en las pruebas."""
        shutil.rmtree(self.carpeta_temporal)

    def test_top_defensores_ordenado_correctamente(self):
        """Verifica que el ranking de defensores este ordenado de mayor a menor."""
        top_defensores = ranking.obtener_top_defensores(self.ruta_prueba)

        self.assertEqual(top_defensores[0]["nombre_usuario"], "jugador_c")
        self.assertEqual(top_defensores[1]["nombre_usuario"], "jugador_a")

    def test_top_atacantes_ordenado_correctamente(self):
        """Verifica que el ranking de atacantes este ordenado de mayor a menor."""
        top_atacantes = ranking.obtener_top_atacantes(self.ruta_prueba)

        self.assertEqual(top_atacantes[0]["nombre_usuario"], "jugador_b")


if __name__ == "__main__":
    unittest.main()
