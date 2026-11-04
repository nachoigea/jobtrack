"""
database.py - Acceso a la base de datos SQLite de JobTrack.

Contiene la creación de la tabla, la validación de los datos y las
operaciones de listar, crear, actualizar y borrar ofertas.
"""
from config import CAMPOS, DB_PATH, ESTADOS, FORMATO_FECHA, REMOTO, sqlite3


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ofertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                puesto TEXT NOT NULL,
                empresa TEXT NOT NULL,
                localizacion TEXT DEFAULT '',
                remoto TEXT DEFAULT 'Presencial',
                salario TEXT DEFAULT '',
                fecha_aplicacion TEXT DEFAULT '',
                estado TEXT DEFAULT 'solicitado',
                via TEXT DEFAULT '',
                observaciones TEXT DEFAULT '',
                creado TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def limpiar(datos):
    """Valida y normaliza los datos recibidos del navegador."""
    out = {k: str(datos.get(k, "") or "").strip() for k in CAMPOS}
    if not out["puesto"] or not out["empresa"]:
        raise ValueError("El puesto y la empresa son obligatorios.")
    if out["estado"] not in ESTADOS:
        out["estado"] = "solicitado"
    if out["remoto"] not in REMOTO:
        out["remoto"] = "Presencial"
    if out["fecha_aplicacion"] and not FORMATO_FECHA.fullmatch(out["fecha_aplicacion"]):
        raise ValueError("La fecha debe tener formato AAAA-MM-DD.")
    return out


def listar():
    with db() as conn:
        rows = conn.execute("SELECT * FROM ofertas ORDER BY fecha_aplicacion DESC, id DESC").fetchall()
    return [dict(r) for r in rows]


def crear(datos):
    d = limpiar(datos)
    with db() as conn:
        cur = conn.execute(
            f"INSERT INTO ofertas ({', '.join(CAMPOS)}) VALUES ({', '.join('?' * len(CAMPOS))})",
            [d[c] for c in CAMPOS],
        )
        return dict(conn.execute("SELECT * FROM ofertas WHERE id=?", (cur.lastrowid,)).fetchone())


def actualizar(oid, datos):
    d = limpiar(datos)
    with db() as conn:
        conn.execute(
            f"UPDATE ofertas SET {', '.join(c + '=?' for c in CAMPOS)} WHERE id=?",
            [d[c] for c in CAMPOS] + [oid],
        )
        row = conn.execute("SELECT * FROM ofertas WHERE id=?", (oid,)).fetchone()
    return dict(row) if row else None


def borrar(oid):
    with db() as conn:
        conn.execute("DELETE FROM ofertas WHERE id=?", (oid,))
