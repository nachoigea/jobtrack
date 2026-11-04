"""
interfaz.py - Interfaz web de JobTrack (HTML + CSS + JS en una sola página).

`pagina_html()` devuelve la página lista para enviar al navegador, con las
listas de estados y modalidades de config.py ya insertadas.
"""
from config import ESTADOS, REMOTO, json

HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JobTrack</title>
<style>
  :root {
    --bg: #f5f6f8; --card: #ffffff; --text: #1d2330; --muted: #6b7385; --line: #e4e7ee;
    --accent: #4f46e5; --accent-soft: #eef0ff; --danger: #dc2626;
    --c-visto: #64748b;     --b-visto: #eef1f5;
    --c-solicitado: #2563eb; --b-solicitado: #e6efff;
    --c-respuesta: #b45309;  --b-respuesta: #fef3c7;
    --c-entrevista: #7c3aed; --b-entrevista: #f1e8ff;
    --c-oferta: #15803d;     --b-oferta: #dcfce7;
    --c-rechazada: #b91c1c;  --b-rechazada: #fee2e2;
    --shadow: 0 1px 2px rgba(16,24,40,.06), 0 4px 16px rgba(16,24,40,.05);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #12141a; --card: #1b1e27; --text: #e8eaf0; --muted: #98a0b3; --line: #2a2f3b;
      --accent: #818cf8; --accent-soft: #23264a; --danger: #f87171;
      --c-visto: #aab4c5;     --b-visto: #2a2f3b;
      --c-solicitado: #7db0ff; --b-solicitado: #1e2b47;
      --c-respuesta: #fbbf24;  --b-respuesta: #3a2f12;
      --c-entrevista: #c4a1ff; --b-entrevista: #2d2347;
      --c-oferta: #4ade80;     --b-oferta: #14341f;
      --c-rechazada: #fca5a5;  --b-rechazada: #3b1a1a;
      --shadow: none;
    }
  }
  * { box-sizing: border-box; }
  [hidden] { display: none !important; }
  body { margin: 0; background: var(--bg); color: var(--text);
         font: 15px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
  .wrap { max-width: 1280px; margin: 0 auto; padding: 28px 20px 60px; }
  header { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
  h1 { margin: 0; font-size: 26px; letter-spacing: -.02em; }
  h1 span { color: var(--accent); }
  .sub { color: var(--muted); font-size: 14px; margin-top: 2px; }
  button { font: inherit; cursor: pointer; border-radius: 10px; border: 1px solid var(--line);
           background: var(--card); color: var(--text); padding: 9px 14px; }
  button:hover { border-color: var(--accent); }
  button.primary { background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }
  button.primary:hover { filter: brightness(1.08); }
  button.icon { padding: 6px 9px; border-color: transparent; background: transparent; color: var(--muted); }
  button.icon:hover { background: var(--accent-soft); color: var(--accent); }
  button.icon.del:hover { background: var(--b-rechazada); color: var(--danger); }

  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin: 22px 0 18px; }
  .stat { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px;
          box-shadow: var(--shadow); cursor: pointer; transition: transform .1s, border-color .1s; }
  .stat:hover { transform: translateY(-1px); border-color: var(--accent); }
  .stat.active { border-color: var(--accent); background: var(--accent-soft); }
  .stat .n { font-size: 24px; font-weight: 700; }
  .stat .l { font-size: 12.5px; color: var(--muted); }

  .toolbar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }
  input, select, textarea { font: inherit; color: var(--text); background: var(--card);
         border: 1px solid var(--line); border-radius: 10px; padding: 9px 12px; width: 100%; }
  input:focus, select:focus, textarea:focus { outline: 2px solid var(--accent-soft); border-color: var(--accent); }
  .toolbar input { flex: 1 1 260px; width: auto; }
  .toolbar select { width: auto; }

  .table-card { background: var(--card); border: 1px solid var(--line); border-radius: 16px;
                box-shadow: var(--shadow); overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; min-width: 980px; }
  th { text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted);
       padding: 12px 14px; border-bottom: 1px solid var(--line); white-space: nowrap; }
  td { padding: 12px 14px; border-bottom: 1px solid var(--line); vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  tbody tr:hover { background: color-mix(in srgb, var(--accent-soft) 45%, transparent); }
  .puesto { font-weight: 600; }
  .empresa { color: var(--muted); font-size: 14px; }
  .tag { display: inline-block; font-size: 12px; padding: 2px 8px; border-radius: 999px;
         background: var(--accent-soft); color: var(--accent); margin-top: 4px; }
  .obs { color: var(--muted); font-size: 14px; max-width: 260px; white-space: pre-wrap; word-break: break-word; }
  .nowrap { white-space: nowrap; }
  .estado { appearance: none; -webkit-appearance: none; border: none; border-radius: 999px; width: auto;
            font-size: 13px; font-weight: 600; padding: 5px 12px; cursor: pointer; }
  .empty { text-align: center; color: var(--muted); padding: 50px 20px; }
  .empty b { display: block; color: var(--text); font-size: 17px; margin-bottom: 4px; }

  dialog { border: 1px solid var(--line); border-radius: 18px; background: var(--card); color: var(--text);
           padding: 0; width: min(640px, 94vw); box-shadow: 0 20px 60px rgba(0,0,0,.3); }
  dialog::backdrop { background: rgba(10,12,20,.55); backdrop-filter: blur(2px); }
  form { padding: 22px; }
  form h2 { margin: 0 0 16px; font-size: 20px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 14px; }
  .grid .full { grid-column: 1 / -1; }
  label { display: block; font-size: 12.5px; color: var(--muted); margin-bottom: 4px; font-weight: 600; }
  .actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 18px; }
  .err { color: var(--danger); font-size: 14px; margin-top: 10px; min-height: 1em; }

  /* --- Pantalla de proyectos --- */
  .volver { padding: 4px 0; border: none; background: none; color: var(--muted); font-size: 14px; margin-bottom: 6px; }
  .volver:hover { color: var(--accent); }
  .titulo-proyecto { display: flex; align-items: center; gap: 4px; }
  .cab-acciones { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
  .cab-acciones button { white-space: nowrap; }
  .conmutador { display: inline-flex; border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
  .conmutador button { border: none; border-radius: 0; padding: 9px 12px; color: var(--muted); }
  .conmutador button + button { border-left: 1px solid var(--line); }
  .conmutador button.activo { background: var(--accent-soft); color: var(--accent); font-weight: 600; }

  /* Tarjeta de proyecto. Modo cuadrícula: info + acciones arriba, resumen debajo. */
  .proyectos { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(300px, 100%), 1fr)); gap: 14px; margin-top: 24px; }
  .proyecto { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px;
              box-shadow: var(--shadow); cursor: pointer; transition: transform .1s, border-color .1s;
              display: grid; grid-template-columns: minmax(0, 1fr) auto; grid-template-areas: "info acciones" "resumen resumen";
              gap: 12px 8px; align-items: start; }
  .proyecto:hover { transform: translateY(-1px); border-color: var(--accent); }
  .proyecto .info { grid-area: info; min-width: 0; }
  .proyecto .acciones { grid-area: acciones; display: flex; }
  .proyecto .resumen { grid-area: resumen; min-width: 0; display: flex; flex-direction: column; gap: 10px; }
  .proyecto .nombre { font-weight: 700; font-size: 17px; word-break: break-word; }
  .proyecto .meta { color: var(--muted); font-size: 14px; margin-top: 2px; }
  .proyecto .meta b { color: var(--text); }

  /* Modo lista: una fila por proyecto (info | resumen | acciones) */
  .proyectos.modo-lista { grid-template-columns: minmax(0, 1fr); gap: 10px; }
  .modo-lista .proyecto { grid-template-columns: minmax(180px, 1fr) minmax(0, 2.2fr) auto;
                          grid-template-areas: "info resumen acciones"; align-items: center; padding: 12px 16px; }
  .modo-lista .leyenda { display: flex; flex-wrap: wrap; gap: 4px 16px; }
  @media (max-width: 760px) {
    .modo-lista .proyecto { grid-template-columns: minmax(0, 1fr) auto; grid-template-areas: "info acciones" "resumen resumen"; }
  }

  /* Barra apilada: un segmento por estado, separados por 2px */
  .barra { display: flex; gap: 2px; height: 10px; }
  .barra span { border-radius: 3px; min-width: 4px; }
  .barra.vacia { background: var(--line); border-radius: 3px; }
  .leyenda { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 14px; font-size: 13px; }
  .leyenda .item { display: flex; align-items: center; gap: 6px; color: var(--muted); white-space: nowrap; }
  .leyenda .item i { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .leyenda .item b { color: var(--text); margin-left: auto; font-variant-numeric: tabular-nums; }
  .modo-lista .leyenda .item b { margin-left: 0; }
  .leyenda .item.cero { opacity: .45; }

  /* Diálogo de mover/copiar y aviso flotante */
  .nota { color: var(--muted); font-size: 13.5px; margin: 10px 0 0; }
  #mover-oferta { margin: -8px 0 16px; color: var(--muted); }
  #mover-oferta b { color: var(--text); }
  .aviso { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); z-index: 10;
           background: var(--text); color: var(--bg); padding: 10px 18px; border-radius: 10px;
           font-size: 14px; box-shadow: 0 6px 24px rgba(0,0,0,.25); max-width: 90vw; }
  .proyectos-vacio { background: var(--card); border: 1px dashed var(--line); border-radius: 16px; margin-top: 24px; }
  @media (max-width: 560px) { .grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<!-- Vista 1: lista de proyectos de búsqueda (pantalla de inicio) -->
<div class="wrap" id="vista-proyectos" hidden>
  <header>
    <div>
      <h1>Job<span>Track</span></h1>
      <div class="sub">Tus proyectos de búsqueda de empleo</div>
    </div>
    <div class="cab-acciones">
      <div class="conmutador" role="group" aria-label="Modo de vista">
        <button id="modo-cuadricula" title="Vista en cuadrícula" onclick="cambiarModo('cuadricula')">▦ Cuadrícula</button>
        <button id="modo-lista" title="Vista en lista" onclick="cambiarModo('lista')">☰ Lista</button>
      </div>
      <button class="primary" onclick="abrirFormProyecto()">+ Crear proyecto</button>
    </div>
  </header>
  <div class="proyectos" id="proyectos"></div>
  <div class="empty proyectos-vacio" id="proyectos-vacio" hidden>
    <b>Todavía no hay proyectos</b>
    Crea un proyecto para cada tipo de puesto o época de búsqueda.<br><br>
    <button class="primary" onclick="abrirFormProyecto()">+ Crear proyecto</button>
  </div>
</div>

<!-- Vista 2: ofertas de un proyecto -->
<div class="wrap" id="vista-ofertas" hidden>
  <header>
    <div>
      <button class="volver" onclick="location.hash = ''">← Proyectos</button>
      <div class="titulo-proyecto">
        <h1 id="nombre-proyecto"></h1>
        <button class="icon" title="Editar proyecto" onclick="abrirFormProyecto(proyecto)">✎</button>
      </div>
      <div class="sub" id="resumen"></div>
    </div>
    <div style="display:flex; gap:10px">
      <button onclick="exportarCSV()">Exportar CSV</button>
      <button class="primary" onclick="abrirForm()">+ Nueva oferta</button>
    </div>
  </header>

  <div class="stats" id="stats"></div>

  <div class="toolbar">
    <input id="q" type="search" placeholder="Buscar por puesto, empresa, lugar, notas…" oninput="render()">
    <select id="orden" onchange="render()">
      <option value="fecha_desc">Más recientes primero</option>
      <option value="fecha_asc">Más antiguas primero</option>
      <option value="empresa">Empresa (A-Z)</option>
      <option value="estado">Por estado</option>
    </select>
  </div>

  <div class="table-card">
    <table>
      <thead><tr>
        <th>Puesto / Empresa</th><th>Localización</th><th>Salario</th><th>Fecha</th>
        <th>Estado</th><th>Vía</th><th>Observaciones</th><th></th>
      </tr></thead>
      <tbody id="filas"></tbody>
    </table>
    <div class="empty" id="vacio" hidden></div>
  </div>
</div>

<dialog id="dlg">
  <form id="form" onsubmit="guardar(event)">
    <h2 id="titulo-form">Nueva oferta</h2>
    <div class="grid">
      <div class="full"><label>Puesto *</label><input id="f-puesto" required></div>
      <div><label>Empresa *</label><input id="f-empresa" required></div>
      <div><label>Localización</label><input id="f-localizacion" placeholder="Ciudad, país"></div>
      <div><label>Modalidad</label><select id="f-remoto"></select></div>
      <div><label>Salario</label><input id="f-salario" placeholder="Ej. 35-40k €/año"></div>
      <div><label>Fecha de aplicación</label><input id="f-fecha" type="date"></div>
      <div><label>Estado</label><select id="f-estado"></select></div>
      <div class="full"><label>Vía de aplicación</label>
        <input id="f-via" list="vias" placeholder="Email, web de la empresa, LinkedIn…">
        <datalist id="vias">
          <option>Email</option><option>Web de la empresa</option><option>LinkedIn</option>
          <option>InfoJobs</option><option>Indeed</option><option>Referido</option><option>Otra</option>
        </datalist>
      </div>
      <div class="full"><label>Observaciones</label><textarea id="f-obs" rows="3"
        placeholder="Contacto, enlace a la oferta, próximos pasos…"></textarea></div>
    </div>
    <div class="err" id="err"></div>
    <div class="actions">
      <button type="button" onclick="dlg.close()">Cancelar</button>
      <button class="primary" type="submit">Guardar</button>
    </div>
  </form>
</dialog>

<dialog id="dlg-proyecto">
  <form onsubmit="guardarProyecto(event)">
    <h2 id="titulo-form-proyecto">Nuevo proyecto</h2>
    <div class="grid">
      <div class="full"><label>Nombre (tipo de puesto) *</label>
        <input id="p-nombre" required placeholder="Ej. Desarrollador backend, Prácticas verano 2026…"></div>
      <div><label>Fecha de inicio *</label><input id="p-fecha" type="date" required></div>
    </div>
    <div class="err" id="err-proyecto"></div>
    <div class="actions">
      <button type="button" onclick="dlgProyecto.close()">Cancelar</button>
      <button class="primary" type="submit">Guardar</button>
    </div>
  </form>
</dialog>

<dialog id="dlg-mover">
  <form onsubmit="event.preventDefault()">
    <h2>Mover a otro proyecto</h2>
    <p id="mover-oferta"></p>
    <label>Proyecto de destino</label>
    <select id="mover-destino"></select>
    <p class="nota"><b>Mover</b>: la búsqueda pasa al otro proyecto y desaparece de este.<br>
      <b>Copiar</b>: se queda aquí y se crea una copia independiente en el otro proyecto.</p>
    <div class="err" id="err-mover"></div>
    <div class="actions">
      <button type="button" onclick="dlgMover.close()">Cancelar</button>
      <button type="button" onclick="ejecutarMover(true)">Copiar</button>
      <button type="button" class="primary" onclick="ejecutarMover(false)">Mover</button>
    </div>
  </form>
</dialog>

<div class="aviso" id="aviso" role="status" hidden></div>

<script>
const ESTADOS = __ESTADOS__;
const REMOTO = __REMOTO__;
const ETIQUETA = { visto: "Visto, sin solicitar", solicitado: "Solicitado",
  respuesta: "Respuesta recibida", entrevista: "Entrevista", oferta: "Oferta recibida", rechazada: "Rechazada" };
const CORTA = { visto: "Vistos", solicitado: "Solicitadas", respuesta: "Con respuesta",
  entrevista: "Entrevistas", oferta: "Ofertas", rechazada: "Rechazadas" };

let proyectos = [];       // lista de proyectos (pantalla de inicio)
let proyecto = null;      // proyecto abierto actualmente
let ofertas = [];         // ofertas del proyecto abierto
let filtro = "todos";
let editId = null;
let editProyectoId = null;
const dlg = document.getElementById("dlg");
const dlgProyecto = document.getElementById("dlg-proyecto");
const dlgMover = document.getElementById("dlg-mover");
let otrosProyectos = [];  // proyectos a los que se puede mover una oferta del proyecto abierto
let moverOferta = null;   // oferta que se está moviendo/copiando

const $ = id => document.getElementById(id);
function el(tag, props = {}, ...hijos) {
  const e = document.createElement(tag);
  Object.assign(e, props);
  hijos.flat().forEach(h => e.append(h));
  return e;
}

async function api(metodo, url, cuerpo) {
  const r = await fetch(url, { method: metodo, headers: { "Content-Type": "application/json" },
    body: cuerpo ? JSON.stringify(cuerpo) : undefined });
  const datos = await r.json();
  if (!r.ok) throw new Error(datos.error || "Error");
  return datos;
}

function fmtFecha(f) {
  if (!f) return "—";
  const [y, m, d] = f.split("-");
  return `${d}/${m}/${y}`;
}

const hoy = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);

// --- Navegación: "#/proyecto/<id>" abre un proyecto; cualquier otra cosa, la lista ---

async function router() {
  dlg.close(); dlgProyecto.close(); dlgMover.close();
  const m = location.hash.match(/^#\/proyecto\/(\d+)$/);
  if (m) await abrirProyecto(Number(m[1]));
  else await mostrarProyectos();
}

function mostrarVista(id) {
  $("vista-proyectos").hidden = id !== "vista-proyectos";
  $("vista-ofertas").hidden = id !== "vista-ofertas";
  window.scrollTo(0, 0);
}

// --- Proyectos ---

async function mostrarProyectos() {
  proyecto = null;
  document.title = "JobTrack";
  proyectos = await api("GET", "/api/proyectos");
  renderProyectos();
  mostrarVista("vista-proyectos");
}

// Modo de vista de la lista de proyectos ("cuadricula" | "lista"), recordado en el navegador
let modo = localStorage.getItem("jobtrack.modo") === "lista" ? "lista" : "cuadricula";

function cambiarModo(m) {
  modo = m;
  localStorage.setItem("jobtrack.modo", m);
  renderProyectos();
}

// Barra apilada con la proporción de ofertas en cada estado
function barraEstados(p) {
  const total = p.num_ofertas;
  if (!total) return el("div", { className: "barra vacia", title: "Sin ofertas todavía" });
  return el("div", { className: "barra", role: "img",
      ariaLabel: ESTADOS.map(e => `${CORTA[e]}: ${p.por_estado[e]}`).join(", ") },
    ESTADOS.filter(e => p.por_estado[e]).map(e => {
      const n = p.por_estado[e];
      const s = el("span", { title: `${CORTA[e]}: ${n} (${Math.round(n / total * 100)}%)` });
      s.style.flexGrow = n;
      s.style.background = `var(--c-${e})`;
      return s;
    }));
}

// Leyenda: punto de color + nombre del estado + número (los estados a 0 se atenúan)
function leyendaEstados(p) {
  return el("div", { className: "leyenda" }, ESTADOS.map(e => {
    const n = p.por_estado[e];
    const punto = el("i");
    punto.style.background = `var(--c-${e})`;
    return el("div", { className: "item" + (n ? "" : " cero") }, punto, CORTA[e], el("b", { textContent: n }));
  }));
}

function renderProyectos() {
  $("modo-cuadricula").classList.toggle("activo", modo === "cuadricula");
  $("modo-lista").classList.toggle("activo", modo === "lista");
  const cont = $("proyectos");
  cont.classList.toggle("modo-lista", modo === "lista");
  cont.replaceChildren(...proyectos.map(p => {
    const accion = (texto, titulo, clase, fn) => el("button", { className: "icon " + clase, title: titulo,
      textContent: texto, onclick: e => { e.stopPropagation(); fn(p); } });
    return el("div", { className: "proyecto", onclick: () => { location.hash = `#/proyecto/${p.id}`; } },
      el("div", { className: "info" },
        el("div", { className: "nombre", textContent: p.nombre }),
        el("div", { className: "meta" }, `Desde el ${fmtFecha(p.fecha_inicio)} · `,
          el("b", { textContent: p.num_ofertas }), p.num_ofertas === 1 ? " oferta" : " ofertas")),
      el("div", { className: "acciones" },
        accion("✎", "Editar proyecto", "", abrirFormProyecto),
        accion("🗑", "Eliminar proyecto", "del", eliminarProyecto)),
      el("div", { className: "resumen" }, barraEstados(p), leyendaEstados(p)));
  }));
  cont.hidden = !proyectos.length;
  $("proyectos-vacio").hidden = proyectos.length > 0;
}

function abrirFormProyecto(p) {
  editProyectoId = p ? p.id : null;
  $("titulo-form-proyecto").textContent = p ? "Editar proyecto" : "Nuevo proyecto";
  $("err-proyecto").textContent = "";
  $("p-nombre").value = p?.nombre ?? "";
  $("p-fecha").value = p?.fecha_inicio ?? hoy();
  dlgProyecto.showModal();
  $("p-nombre").focus();
}

async function guardarProyecto(ev) {
  ev.preventDefault();
  const datos = { nombre: $("p-nombre").value, fecha_inicio: $("p-fecha").value };
  try {
    if (editProyectoId) {
      const p = await api("PUT", `/api/proyectos/${editProyectoId}`, datos);
      dlgProyecto.close();
      if (proyecto) { proyecto = p; render(); } else await mostrarProyectos();
    } else {
      const p = await api("POST", "/api/proyectos", datos);
      dlgProyecto.close();
      location.hash = `#/proyecto/${p.id}`;   // al crear un proyecto se entra directamente en él
    }
  } catch (e) { $("err-proyecto").textContent = e.message; }
}

async function eliminarProyecto(p) {
  const aviso = p.num_ofertas
    ? `Se borrarán también sus ${p.num_ofertas} ${p.num_ofertas === 1 ? "oferta" : "ofertas"}. Esta acción no se puede deshacer.`
    : "El proyecto no tiene ofertas.";
  if (!confirm(`¿Eliminar el proyecto «${p.nombre}»?\n\n${aviso}`)) return;
  await api("DELETE", `/api/proyectos/${p.id}`);
  await mostrarProyectos();
}

// --- Ofertas del proyecto abierto ---

async function abrirProyecto(id) {
  try { proyecto = await api("GET", `/api/proyectos/${id}`); }
  catch { location.hash = ""; return; }   // el proyecto no existe: volver a la lista
  otrosProyectos = (await api("GET", "/api/proyectos")).filter(p => p.id !== proyecto.id);
  filtro = "todos";
  $("q").value = "";
  await cargar();
  mostrarVista("vista-ofertas");
}

async function cargar() {
  ofertas = await api("GET", `/api/proyectos/${proyecto.id}/ofertas`);
  render();
}

function renderStats() {
  const cont = $("stats");
  cont.replaceChildren();
  const tarjeta = (clave, n, etiqueta) => {
    const s = el("div", { className: "stat" + (filtro === clave ? " active" : ""), onclick: () => {
      filtro = clave; render(); } },
      el("div", { className: "n", textContent: n }), el("div", { className: "l", textContent: etiqueta }));
    cont.append(s);
  };
  tarjeta("todos", ofertas.length, "Todas");
  ESTADOS.forEach(e => tarjeta(e, ofertas.filter(o => o.estado === e).length, CORTA[e]));
}

function render() {
  renderStats();
  const q = $("q").value.trim().toLowerCase();
  let lista = ofertas.filter(o => (filtro === "todos" || o.estado === filtro) &&
    (!q || [o.puesto, o.empresa, o.localizacion, o.via, o.observaciones, o.salario]
      .join(" ").toLowerCase().includes(q)));

  const orden = $("orden").value;
  const fecha = o => o.fecha_aplicacion || "";
  lista.sort((a, b) => {
    if (orden === "fecha_asc") return fecha(a).localeCompare(fecha(b)) || a.id - b.id;
    if (orden === "empresa") return a.empresa.localeCompare(b.empresa, "es");
    if (orden === "estado") return ESTADOS.indexOf(a.estado) - ESTADOS.indexOf(b.estado);
    return fecha(b).localeCompare(fecha(a)) || b.id - a.id;
  });

  document.title = `${proyecto.nombre} · JobTrack`;
  $("nombre-proyecto").textContent = proyecto.nombre;
  $("resumen").textContent = `Desde el ${fmtFecha(proyecto.fecha_inicio)} · ` + (ofertas.length
    ? `${lista.length} de ${ofertas.length} ofertas mostradas` : "Aún no has registrado ofertas");

  const tbody = $("filas");
  tbody.replaceChildren();
  lista.forEach(o => tbody.append(fila(o)));

  const vacio = $("vacio");
  vacio.hidden = lista.length > 0;
  if (!lista.length) {
    vacio.replaceChildren(
      el("b", { textContent: ofertas.length ? "Nada coincide con el filtro" : "Todavía no hay ofertas" }),
      document.createTextNode(ofertas.length ? "Prueba a cambiar la búsqueda o el filtro."
        : "Pulsa «+ Nueva oferta» para registrar la primera."));
  }
}

function selectEstado(o) {
  const s = el("select", { className: "estado", title: "Cambiar estado" });
  ESTADOS.forEach(e => s.append(el("option", { value: e, textContent: ETIQUETA[e], selected: e === o.estado })));
  const pintar = () => { s.style.color = `var(--c-${s.value})`; s.style.background = `var(--b-${s.value})`; };
  pintar();
  s.onchange = async () => {
    try { await api("PUT", `/api/ofertas/${o.id}`, { ...o, estado: s.value }); await cargar(); }
    catch (e) { alert(e.message); }
  };
  return s;
}

function fila(o) {
  const tr = el("tr");
  tr.append(
    el("td", {}, el("div", { className: "puesto", textContent: o.puesto }),
                 el("div", { className: "empresa", textContent: o.empresa })),
    el("td", {}, el("div", { textContent: o.localizacion || "—" }),
                 el("span", { className: "tag", textContent: o.remoto })),
    el("td", { className: "nowrap", textContent: o.salario || "—" }),
    el("td", { className: "nowrap", textContent: fmtFecha(o.fecha_aplicacion) }),
    el("td", {}, selectEstado(o)),
    el("td", { textContent: o.via || "—" }),
    el("td", { className: "obs", textContent: o.observaciones }),
    el("td", { className: "nowrap" },
      el("button", { className: "icon", title: "Editar", textContent: "✎", onclick: () => abrirForm(o) }),
      // "Mover" solo aparece si hay otros proyectos a los que llevar la oferta
      otrosProyectos.length
        ? el("button", { className: "icon", title: "Mover", ariaLabel: "Mover", textContent: "⇄", onclick: () => abrirMover(o) })
        : [],
      el("button", { className: "icon del", title: "Eliminar", textContent: "🗑", onclick: () => eliminar(o) }))
  );
  return tr;
}

function abrirForm(o) {
  editId = o ? o.id : null;
  $("titulo-form").textContent = o ? "Editar oferta" : "Nueva oferta";
  $("err").textContent = "";
  $("f-remoto").replaceChildren(...REMOTO.map(r => el("option", { value: r, textContent: r })));
  $("f-estado").replaceChildren(...ESTADOS.map(e => el("option", { value: e, textContent: ETIQUETA[e] })));
  $("f-puesto").value = o?.puesto ?? "";
  $("f-empresa").value = o?.empresa ?? "";
  $("f-localizacion").value = o?.localizacion ?? "";
  $("f-remoto").value = o?.remoto ?? "Presencial";
  $("f-salario").value = o?.salario ?? "";
  $("f-fecha").value = o ? o.fecha_aplicacion : hoy();
  $("f-estado").value = o?.estado ?? "solicitado";
  $("f-via").value = o?.via ?? "";
  $("f-obs").value = o?.observaciones ?? "";
  dlg.showModal();
  $("f-puesto").focus();
}

async function guardar(ev) {
  ev.preventDefault();
  const datos = {
    puesto: $("f-puesto").value, empresa: $("f-empresa").value, localizacion: $("f-localizacion").value,
    remoto: $("f-remoto").value, salario: $("f-salario").value, fecha_aplicacion: $("f-fecha").value,
    estado: $("f-estado").value, via: $("f-via").value, observaciones: $("f-obs").value,
  };
  try {
    if (editId) await api("PUT", `/api/ofertas/${editId}`, datos);
    else await api("POST", `/api/proyectos/${proyecto.id}/ofertas`, datos);
    dlg.close();
    await cargar();
  } catch (e) { $("err").textContent = e.message; }
}

async function eliminar(o) {
  if (!confirm(`¿Eliminar «${o.puesto}» en ${o.empresa}?`)) return;
  await api("DELETE", `/api/ofertas/${o.id}`);
  await cargar();
}

function exportarCSV() {
  const cols = ["puesto", "empresa", "localizacion", "remoto", "salario", "fecha_aplicacion", "estado", "via", "observaciones"];
  const esc = v => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const csv = [cols.join(","), ...ofertas.map(o => cols.map(c => esc(o[c])).join(","))].join("\n");
  const a = el("a", { href: URL.createObjectURL(new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8" })),
                      download: `jobtrack-${proyecto.nombre.replace(/[^\p{L}\p{N}-]+/gu, "_")}.csv` });
  a.click();
}

// --- Mover / copiar una oferta a otro proyecto ---

function abrirMover(o) {
  moverOferta = o;
  $("mover-oferta").replaceChildren(el("b", { textContent: o.puesto }), ` en ${o.empresa}`);
  $("mover-destino").replaceChildren(...otrosProyectos.map(p =>
    el("option", { value: p.id, textContent: `${p.nombre} (desde el ${fmtFecha(p.fecha_inicio)})` })));
  $("err-mover").textContent = "";
  dlgMover.showModal();
  $("mover-destino").focus();
}

async function ejecutarMover(copiar) {
  const destino = otrosProyectos.find(p => p.id === Number($("mover-destino").value));
  try {
    await api("POST", `/api/ofertas/${moverOferta.id}/mover`, { proyecto_id: destino.id, copiar });
    dlgMover.close();
    await cargar();
    avisar(`«${moverOferta.puesto}» ${copiar ? "copiada" : "movida"} a «${destino.nombre}»`);
  } catch (e) { $("err-mover").textContent = e.message; }
}

let temporizadorAviso;
function avisar(texto) {
  const a = $("aviso");
  a.textContent = texto;
  a.hidden = false;
  clearTimeout(temporizadorAviso);
  temporizadorAviso = setTimeout(() => { a.hidden = true; }, 3500);
}

[dlg, dlgProyecto, dlgMover].forEach(d => d.addEventListener("click", e => { if (e.target === d) d.close(); }));
window.addEventListener("hashchange", router);
router();
</script>
</body>
</html>
"""


def pagina_html():
    return (HTML
            .replace("__ESTADOS__", json.dumps(ESTADOS))
            .replace("__REMOTO__", json.dumps(REMOTO, ensure_ascii=False)))
