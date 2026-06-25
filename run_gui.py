"""Ejecuta la interfaz grafica del juego."""

import os
import sys

RUTA_SRC = os.path.join(os.path.dirname(__file__), "src")
if RUTA_SRC not in sys.path:
    sys.path.insert(0, RUTA_SRC)

from presentacion.interfaz.root import main


if __name__ == "__main__":
    main()
