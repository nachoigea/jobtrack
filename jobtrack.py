#!/usr/bin/env python3
"""
jobtrack.py - Punto de entrada de JobTrack (seguimiento de ofertas de trabajo).

Uso:
    python jobtrack.py            # abre http://127.0.0.1:8765 en el navegador
    python jobtrack.py --port 9000 --no-browser

Estructura:
    config.py    variables e imports compartidos
    database.py  base de datos SQLite (jobtrack.db)
    interfaz.py  página HTML/CSS/JS
    servidor.py  servidor HTTP + API
    jobtrack.py  este archivo: arranca todo
"""
import database
import servidor
from config import DB_PATH, HOST, PORT, argparse, threading, webbrowser


def main():
    ap = argparse.ArgumentParser(description="JobTrack - seguimiento de ofertas de trabajo")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--no-browser", action="store_true", help="no abrir el navegador automáticamente")
    args = ap.parse_args()

    database.init_db()
    try:
        server = servidor.crear_servidor(args.port)
    except OSError:
        print(f"No se pudo usar el puerto {args.port} (¿JobTrack ya está abierto?). "
              f"Prueba con: python jobtrack.py --port {args.port + 1}")
        return

    url = f"http://{HOST}:{args.port}"
    print(f"JobTrack funcionando en {url}  (Ctrl+C para cerrar)")
    print(f"Datos guardados en: {DB_PATH}")
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nJobTrack cerrado. Tus datos están guardados.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
