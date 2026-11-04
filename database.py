"""
database.py - Acceso a la base de datos SQLite de JobTrack.

Contiene la creación de las tablas (proyectos y ofertas), la migración de bases
de datos antiguas, la validación de los datos y las operaciones de listar,
crear, actualizar y borrar proyectos y ofertas.

Cada oferta pertenece a un proyecto de búsqueda (columna proyecto_id); las
ofertas no se comparten entre proyectos, pero todo vive en el mismo jobtrack.db.
"""
from config import (CAMPOS, CAMPOS_PROYECTO, DB_PATH, ESTADOS, FORMATO_FECHA,
                    NOMBRE_PROYECTO_MIGRADO, REMOTO, sqlite3)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS proyectos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                fecha_inicio TEXT NOT NULL,
                creado TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
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
                creado TEXT DEFAULT CURRENT_TIMESTAMP,
                proyecto_id INTEGER REFERENCES proyectos(id) ON DELETE CASCADE
            )
            """
        )
        _migrar(conn)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ofertas_proyecto ON ofertas(proyecto_id)")


def _migrar(conn):
    """Adapta bases de datos creadas antes de existir los proyectos.

    1. Añade la columna proyecto_id a la tabla ofertas si no la tiene.
    2. Si hay ofertas sin proyecto, crea el proyecto «Búsqueda inicial» y las
       asigna a él. Su fecha de inicio es la fecha de aplicación más antigua
       (o, si no hay ninguna, el día en que se registró la primera oferta).
    """
    columnas = {r["name"] for r in conn.execute("PRAGMA table_info(ofertas)")}
    if "proyecto_id" not in columnas:
        conn.execute("ALTER TABLE ofertas ADD COLUMN proyecto_id INTEGER "
                     "REFERENCES proyectos(id) ON DELETE CASCADE")

    if conn.execute("SELECT 1 FROM ofertas WHERE proyecto_id IS NULL LIMIT 1").fetchone():
        cur = conn.execute(
            """
            INSERT INTO proyectos (nombre, fecha_inicio) VALUES (?, COALESCE(
                (SELECT MIN(NULLIF(fecha_aplicacion, '')) FROM ofertas WHERE proyecto_id IS NULL),
                (SELECT date(MIN(creado)) FROM ofertas WHERE proyecto_id IS NULL),
                date('now', 'localtime')))
            """,
            (NOMBRE_PROYECTO_MIGRADO,),
        )
        conn.execute("UPDATE ofertas SET proyecto_id=? WHERE proyecto_id IS NULL", (cur.lastrowid,))


# --- Validación ---

def limpiar(datos):
    """Valida y normaliza los datos de una oferta recibidos del navegador."""
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


def limpiar_proyecto(datos):
    """Valida y normaliza los datos de un proyecto recibidos del navegador."""
    out = {k: str(datos.get(k, "") or "").strip() for k in CAMPOS_PROYECTO}
    if not out["nombre"]:
        raise ValueError("El nombre del proyecto es obligatorio.")
    if not FORMATO_FECHA.fullmatch(out["fecha_inicio"]):
        raise ValueError("La fecha de inicio es obligatoria y debe tener formato AAAA-MM-DD.")
    return out


# --- Proyectos ---

# Total de ofertas y una columna n_<estado> con el recuento de cada estado.
# ESTADOS son constantes de config.py, no datos del usuario: es seguro insertarlas en el SQL.
_SELECT_PROYECTO = f"""
    SELECT p.*, COUNT(o.id) AS num_ofertas,
           {', '.join(f"COUNT(CASE WHEN o.estado = '{e}' THEN 1 END) AS n_{e}" for e in ESTADOS)}
    FROM proyectos p LEFT JOIN ofertas o ON o.proyecto_id = p.id
"""


def _proyecto(row):
    """Convierte la fila en dict, agrupando los recuentos en por_estado = {estado: n}."""
    d = dict(row)
    d["por_estado"] = {e: d.pop(f"n_{e}") for e in ESTADOS}
    return d


def listar_proyectos():
    with db() as conn:
        rows = conn.execute(_SELECT_PROYECTO + " GROUP BY p.id ORDER BY p.fecha_inicio DESC, p.id DESC").fetchall()
    return [_proyecto(r) for r in rows]


def obtener_proyecto(pid):
    with db() as conn:
        row = conn.execute(_SELECT_PROYECTO + " WHERE p.id=? GROUP BY p.id", (pid,)).fetchone()
    return _proyecto(row) if row else None


def crear_proyecto(datos):
    d = limpiar_proyecto(datos)
    with db() as conn:
        cur = conn.execute("INSERT INTO proyectos (nombre, fecha_inicio) VALUES (?, ?)",
                           (d["nombre"], d["fecha_inicio"]))
    return obtener_proyecto(cur.lastrowid)


def actualizar_proyecto(pid, datos):
    d = limpiar_proyecto(datos)
    with db() as conn:
        conn.execute("UPDATE proyectos SET nombre=?, fecha_inicio=? WHERE id=?",
                     (d["nombre"], d["fecha_inicio"], pid))
    return obtener_proyecto(pid)


def borrar_proyecto(pid):
    """Borra el proyecto y todas sus ofertas."""
    with db() as conn:
        conn.execute("DELETE FROM ofertas WHERE proyecto_id=?", (pid,))
        conn.execute("DELETE FROM proyectos WHERE id=?", (pid,))


# --- Ofertas ---

def _existe_proyecto(conn, pid):
    return conn.execute("SELECT 1 FROM proyectos WHERE id=?", (pid,)).fetchone() is not None


def listar(pid):
    """Ofertas de un proyecto, o None si el proyecto no existe."""
    with db() as conn:
        if not _existe_proyecto(conn, pid):
            return None
        rows = conn.execute("SELECT * FROM ofertas WHERE proyecto_id=? "
                            "ORDER BY fecha_aplicacion DESC, id DESC", (pid,)).fetchall()
    return [dict(r) for r in rows]


def crear(pid, datos):
    """Crea una oferta en el proyecto indicado. Devuelve None si el proyecto no existe."""
    d = limpiar(datos)
    with db() as conn:
        if not _existe_proyecto(conn, pid):
            return None
        cur = conn.execute(
            f"INSERT INTO ofertas ({', '.join(CAMPOS)}, proyecto_id) "
            f"VALUES ({', '.join('?' * len(CAMPOS))}, ?)",
            [d[c] for c in CAMPOS] + [pid],
        )
        return dict(conn.execute("SELECT * FROM ofertas WHERE id=?", (cur.lastrowid,)).fetchone())


def actualizar(oid, datos):
    """Actualiza una oferta. No permite cambiarla de proyecto."""
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


def mover(oid, datos):
    """Mueve o copia una oferta a otro proyecto.

    datos = {"proyecto_id": <destino>, "copiar": bool}
      - mover:  la oferta cambia de proyecto (mismo id, desaparece del origen).
      - copiar: se crea una oferta nueva en el destino con los mismos datos;
                la original se queda en su proyecto. Las dos son independientes.
    Devuelve la oferta resultante (la movida o la copia nueva).
    Lanza LookupError si la oferta o el proyecto destino no existen y
    ValueError si los datos no son válidos.
    """
    try:
        destino = int(datos.get("proyecto_id"))
    except (TypeError, ValueError):
        raise ValueError("Hay que indicar el proyecto de destino.")
    copiar = bool(datos.get("copiar"))
    with db() as conn:
        oferta = conn.execute("SELECT proyecto_id FROM ofertas WHERE id=?", (oid,)).fetchone()
        if not oferta:
            raise LookupError("La oferta no existe.")
        if not _existe_proyecto(conn, destino):
            raise LookupError("El proyecto de destino no existe.")
        if oferta["proyecto_id"] == destino:
            raise ValueError("La oferta ya está en ese proyecto.")
        if copiar:
            cols = ", ".join(CAMPOS)
            cur = conn.execute(f"INSERT INTO ofertas ({cols}, proyecto_id) "
                               f"SELECT {cols}, ? FROM ofertas WHERE id=?", (destino, oid))
            oid = cur.lastrowid
        else:
            conn.execute("UPDATE ofertas SET proyecto_id=? WHERE id=?", (destino, oid))
        return dict(conn.execute("SELECT * FROM ofertas WHERE id=?", (oid,)).fetchone())
