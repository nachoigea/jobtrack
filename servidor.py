"""
servidor.py - Servidor HTTP de JobTrack.

Sirve la página (definida en interfaz.py) y expone la API REST que usa el
navegador (/api/ofertas), apoyándose en database.py para los datos.
"""
import database
from config import (HOST, RUTA_API, BaseHTTPRequestHandler,
                    ThreadingHTTPServer, json)
from interfaz import pagina_html


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silencia el log en consola
        pass

    def _json(self, codigo, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _leer_json(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = pagina_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif RUTA_API.match(self.path):
            self._json(200, database.listar())
        else:
            self._json(404, {"error": "No encontrado"})

    def do_POST(self):
        if not RUTA_API.match(self.path):
            return self._json(404, {"error": "No encontrado"})
        try:
            self._json(201, database.crear(self._leer_json()))
        except ValueError as e:
            self._json(400, {"error": str(e)})

    def do_PUT(self):
        m = RUTA_API.match(self.path)
        if not m or not m.group(1):
            return self._json(404, {"error": "No encontrado"})
        try:
            res = database.actualizar(int(m.group(1)), self._leer_json())
            self._json(200 if res else 404, res or {"error": "No existe"})
        except ValueError as e:
            self._json(400, {"error": str(e)})

    def do_DELETE(self):
        m = RUTA_API.match(self.path)
        if not m or not m.group(1):
            return self._json(404, {"error": "No encontrado"})
        database.borrar(int(m.group(1)))
        self._json(200, {"ok": True})


def crear_servidor(puerto):
    """Devuelve el servidor listo para `serve_forever()`. Lanza OSError si el puerto está ocupado."""
    return ThreadingHTTPServer((HOST, puerto), Handler)
