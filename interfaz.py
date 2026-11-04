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
  @media (max-width: 560px) { .grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>Job<span>Track</span></h1>
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

<script>
const ESTADOS = __ESTADOS__;
const REMOTO = __REMOTO__;
const ETIQUETA = { visto: "Visto, sin solicitar", solicitado: "Solicitado",
  respuesta: "Respuesta recibida", entrevista: "Entrevista", oferta: "Oferta recibida", rechazada: "Rechazada" };
const CORTA = { visto: "Vistos", solicitado: "Solicitadas", respuesta: "Con respuesta",
  entrevista: "Entrevistas", oferta: "Ofertas", rechazada: "Rechazadas" };

let ofertas = [];
let filtro = "todos";
let editId = null;
const dlg = document.getElementById("dlg");

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

async function cargar() {
  ofertas = await api("GET", "/api/ofertas");
  render();
}

function fmtFecha(f) {
  if (!f) return "—";
  const [y, m, d] = f.split("-");
  return `${d}/${m}/${y}`;
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

  $("resumen").textContent = ofertas.length
    ? `${lista.length} de ${ofertas.length} ofertas mostradas` : "Aún no has registrado ofertas";

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
  const hoy = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  $("f-puesto").value = o?.puesto ?? "";
  $("f-empresa").value = o?.empresa ?? "";
  $("f-localizacion").value = o?.localizacion ?? "";
  $("f-remoto").value = o?.remoto ?? "Presencial";
  $("f-salario").value = o?.salario ?? "";
  $("f-fecha").value = o ? o.fecha_aplicacion : hoy;
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
    else await api("POST", "/api/ofertas", datos);
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
                      download: "jobtrack.csv" });
  a.click();
}

dlg.addEventListener("click", e => { if (e.target === dlg) dlg.close(); });
cargar();
</script>
</body>
</html>
"""


def pagina_html():
    return (HTML
            .replace("__ESTADOS__", json.dumps(ESTADOS))
            .replace("__REMOTO__", json.dumps(REMOTO, ensure_ascii=False)))
