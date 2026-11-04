"""
config.py - Variables de configuración e imports compartidos de JobTrack.

Aquí vive todo lo "global": rutas, puerto, listas de valores permitidos y los
imports de la librería estándar que usan el resto de módulos. Los demás
archivos hacen `from config import ...` en lugar de repetir los imports.
"""
# --- Imports compartidos (librería estándar, sin dependencias externas) ---
import argparse
import json
import re
import sqlite3
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# --- Rutas ---
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "jobtrack.db"  # los datos se guardan junto a los scripts

# --- Servidor ---
HOST = "127.0.0.1"
PORT = 8765
RUTA_PROYECTOS = re.compile(r"^/api/proyectos(?:/(\d+))?$")          # /api/proyectos[/<id>]
RUTA_OFERTAS_PROYECTO = re.compile(r"^/api/proyectos/(\d+)/ofertas$")  # ofertas de un proyecto
RUTA_OFERTA = re.compile(r"^/api/ofertas/(\d+)$")                     # una oferta concreta
RUTA_MOVER_OFERTA = re.compile(r"^/api/ofertas/(\d+)/mover$")         # mover/copiar a otro proyecto

# --- Modelo de datos ---
ESTADOS = ["visto", "solicitado", "respuesta", "entrevista", "oferta", "rechazada"]
REMOTO = ["Presencial", "Híbrido", "Remoto"]
CAMPOS = ["puesto", "empresa", "localizacion", "remoto", "salario",
          "fecha_aplicacion", "estado", "via", "observaciones"]
CAMPOS_PROYECTO = ["nombre", "fecha_inicio"]
FORMATO_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")
# Proyecto al que se asignan las ofertas de bases de datos anteriores a los proyectos
NOMBRE_PROYECTO_MIGRADO = "Búsqueda inicial"
