"""
servidor.py - Servidor HTTP de JobTrack.

Sirve la página (definida en interfaz.py) y expone la API REST que usa el
navegador, apoyándose en database.py para los datos:

    GET    /api/proyectos              lista de proyectos (con nº de ofertas)
    POST   /api/proyectos              crea un proyecto
    GET    /api/proyectos/<id>         datos de un proyecto
    PUT    /api/proyectos/<id>         modifica un proyecto
    DELETE /api/proyectos/<id>         borra un proyecto y sus ofertas
    GET    /api/proyectos/<id>/ofertas ofertas del proyecto
    POST   /api/proyectos/<id>/ofertas crea una oferta en el proyecto
    POST   /api/ofertas/<id>/mover     mueve o copia la oferta a otro proyecto
                                       ({"proyecto_id": n, "copiar": bool})
    PUT    /api/ofertas/<id>           modifica una oferta
    DELETE /api/ofertas/<id>           borra una oferta
"""
import database
from config import (HOST, RUTA_MOVER_OFERTA, RUTA_OFERTA, RUTA_OFERTAS_PROYECTO,
                    RUTA_PROYECTOS, BaseHTTPRequestHandler, ThreadingHTTPServer,
                    json)
from interfaz import pagina_html

NO_ENCONTRADO = {"error": "No encontrado"}
PROYECTO_NO_EXISTE = {"error": "El proyecto no existe"}


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
        elif m := RUTA_PROYECTOS.match(self.path):
            if not m.group(1):
                return self._json(200, database.listar_proyectos())
            p = database.obtener_proyecto(int(m.group(1)))
            self._json(200, p) if p else self._json(404, PROYECTO_NO_EXISTE)
        elif m := RUTA_OFERTAS_PROYECTO.match(self.path):
            ofertas = database.listar(int(m.group(1)))
            self._json(200, ofertas) if ofertas is not None else self._json(404, PROYECTO_NO_EXISTE)
        else:
            self._json(404, NO_ENCONTRADO)

    def do_POST(self):
        try:
            if (m := RUTA_PROYECTOS.match(self.path)) and not m.group(1):
                return self._json(201, database.crear_proyecto(self._leer_json()))
            if m := RUTA_OFERTAS_PROYECTO.match(self.path):
                oferta = database.crear(int(m.group(1)), self._leer_json())
                return self._json(201, oferta) if oferta else self._json(404, PROYECTO_NO_EXISTE)
            if m := RUTA_MOVER_OFERTA.match(self.path):
                return self._json(200, database.mover(int(m.group(1)), self._leer_json()))
            self._json(404, NO_ENCONTRADO)
        except LookupError as e:
            self._json(404, {"error": str(e)})
        except ValueError as e:
            self._json(400, {"error": str(e)})

    def do_PUT(self):
        try:
            if (m := RUTA_PROYECTOS.match(self.path)) and m.group(1):
                res = database.actualizar_proyecto(int(m.group(1)), self._leer_json())
                return self._json(200, res) if res else self._json(404, PROYECTO_NO_EXISTE)
            if m := RUTA_OFERTA.match(self.path):
                res = database.actualizar(int(m.group(1)), self._leer_json())
                return self._json(200 if res else 404, res or {"error": "No existe"})
            self._json(404, NO_ENCONTRADO)
        except ValueError as e:
            self._json(400, {"error": str(e)})

    def do_DELETE(self):
        if (m := RUTA_PROYECTOS.match(self.path)) and m.group(1):
            database.borrar_proyecto(int(m.group(1)))
        elif m := RUTA_OFERTA.match(self.path):
            database.borrar(int(m.group(1)))
        else:
            return self._json(404, NO_ENCONTRADO)
        self._json(200, {"ok": True})


def crear_servidor(puerto):
    """Devuelve el servidor listo para `serve_forever()`. Lanza OSError si el puerto está ocupado."""
    return ThreadingHTTPServer((HOST, puerto), Handler)
