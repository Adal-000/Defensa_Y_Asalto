"""
Descripcion:
    Archivo principal del proyecto "Defensa y Asalto de Base". Sirve
    como punto de entrada para ejecutar el programa. Mientras el
    Desarrollador 1 conecta la interfaz grafica en Tkinter, este
    archivo permite probar la logica del Desarrollador 2 mediante
    una simulacion por consola.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "Logica"))

import app


def simular_partida_por_consola():
    """
    Descripcion:
        Ejecuta una simulacion sencilla por consola que registra dos
        jugadores de prueba, crea una partida entre ellos, realiza
        algunas compras de torres y unidades, y ejecuta varios
        turnos de combate mostrando el resultado en pantalla.

    Entradas:
        Ninguna.

    Salidas:
        None: Imprime en consola el progreso de la simulacion.

    Restricciones:
        Ninguna.
    """
    print("=== Defensa y Asalto de Base (simulacion de consola) ===\n")

    app.registrar_jugador("jugador_defensor", "clave123")
    app.registrar_jugador("jugador_atacante", "clave456")

    exito_login, mensaje_login = app.validar_login("jugador_defensor", "clave123")
    print(f"Login defensor: {mensaje_login}")

    estado_inicial = app.crear_partida("jugador_defensor", "jugador_atacante")
    print(f"\nPartida creada. Ronda {estado_inicial['numero_ronda']} iniciada.")
    print(f"Dinero defensor: {estado_inicial['dinero_defensor']}")
    print(f"Dinero atacante: {estado_inicial['dinero_atacante']}\n")

    exito, mensaje = app.comprar_torre("arquera", fila=3, columna=2)
    print(f"Compra de torre: {mensaje}")

    exito, mensaje = app.comprar_unidad("soldado", fila=10, columna=2)
    print(f"Compra de unidad: {mensaje}\n")

    numero_turno = 1
    while True:
        resultado_turno = app.ejecutar_combate()

        if not resultado_turno:
            break

        print(f"--- Turno {numero_turno} ---")
        for evento in resultado_turno["eventos"]:
            print(f"  {evento}")

        if resultado_turno["ronda_finalizada"]:
            estado = app.obtener_estado_partida()
            print(f"\nRonda finalizada. Marcador: "
                  f"defensor {estado['rondas_ganadas_defensor']} - "
                  f"atacante {estado['rondas_ganadas_atacante']}")

            if estado["partida_finalizada"]:
                print(f"\n¡{estado['ganador_partida']} gano la partida "
                      f"como {estado['rol_ganador_partida']}!")
                break

        numero_turno += 1
        if numero_turno > 40:
            print("\nSimulacion detenida por seguridad (demasiados turnos).")
            break

    print("\nTop defensores:", app.obtener_top_defensores())
    print("Top atacantes:", app.obtener_top_atacantes())


if __name__ == "__main__":
    simular_partida_por_consola()
