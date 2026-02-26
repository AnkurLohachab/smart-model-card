"""
Professional HTML Template for SMART Model Cards

Author: Ankur Lohachab
Department of Advanced Computing Sciences, Maastricht University
"""

def get_html_template(model_name: str, sections_html: str, created_at: str) -> str:
    """Generate complete HTML document with professional styling"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>SMART Model Card - {model_name}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --fg:#222;
      --muted:#666;
      --rule:#e6e6e6;
      --chip:#f8f8f8;
      --accent:#2563eb;
      --accent-weak:#eff6ff;
      --font-scale:1;
      --success:#10b981;
      --warning:#f59e0b;
      --danger:#ef4444;
    }}

    html,body{{background:#fff;color:var(--fg);margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;line-height:1.6;font-size:calc(16px * var(--font-scale))}}

    .container{{max-width:1400px;margin:0 auto;padding:2rem}}

    h1{{margin:0 0 1.5rem 0;font-size:2rem;color:var(--accent);border-bottom:3px solid var(--accent);padding-bottom:1rem}}
    h2{{border-bottom:2px solid var(--rule);padding-bottom:.5rem;margin-top:2rem;font-size:1.4rem;color:var(--fg)}}
    h3{{font-size:1.1rem;margin-top:1.5rem;color:var(--accent)}}

    .header{{text-align:center;margin-bottom:3rem;padding:2rem;background:linear-gradient(135deg, var(--accent-weak) 0%, #fff 100%);border-radius:12px}}
    .model-badge{{display:inline-block;background:var(--accent);color:#fff;padding:.5rem 1rem;border-radius:6px;font-size:.9rem;margin-top:.5rem}}

    /* Sticky TOC */
    .toc{{position:sticky;top:0;background:#fff;padding:1rem 0;z-index:50;border-bottom:2px solid var(--rule);margin-bottom:2rem;box-shadow:0 2px 4px rgba(0,0,0,.05)}}
    .toc-content{{display:flex;flex-wrap:wrap;gap:.5rem 1.5rem;align-items:center;justify-content:space-between}}
    .toc ol{{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:.5rem 1rem}}
    .toc a{{text-decoration:none;color:var(--fg);padding:6px 12px;border-radius:6px;font-size:.9rem;transition:all .2s}}
    .toc a:hover{{background:var(--accent-weak);color:var(--accent)}}
    .toc-controls{{display:flex;gap:.5rem}}

    .btn{{border:1px solid var(--rule);background:#fff;padding:6px 12px;border-radius:6px;cursor:pointer;font-size:.85rem;transition:all .2s}}
    .btn:hover{{background:var(--accent-weak);border-color:var(--accent)}}

    /* Sections */
    .section{{background:#fff;margin-bottom:1.5rem;padding:1.5rem;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.1);border-left:4px solid var(--accent)}}
    .section-toggle{{appearance:none;border:0;background:transparent;display:flex;align-items:center;gap:8px;font:inherit;padding:.25rem 0;cursor:pointer;color:inherit;width:100%;text-align:left}}
    .caret{{width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:8px solid var(--accent);transition:transform .2s}}
    .section.collapsed .caret{{transform:rotate(-90deg)}}
    .section.collapsed>:not(h2){{display:none}}

    /* Key-Value pairs */
    .kv{{margin:.75rem 0;display:grid;grid-template-columns:280px 1fr;gap:1rem;align-items:start}}
    .kv-label{{font-weight:600;color:var(--accent)}}
    .kv-value{{color:var(--fg)}}

    /* Tables */
    .table-wrap{{overflow-x:auto;margin:1rem 0;border-radius:8px;border:1px solid var(--rule)}}
    table{{border-collapse:separate;border-spacing:0;width:100%;font-size:.9rem}}
    th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid var(--rule)}}
    th{{background:var(--chip);font-weight:600;position:sticky;top:0;z-index:1}}
    tr:hover td{{background:var(--accent-weak)}}

    /* Search box */
    .search-box{{margin:1rem 0;padding:.5rem;border:1px solid var(--rule);border-radius:6px;width:100%;max-width:300px;font-size:.9rem}}

    /* Concept styling */
    .concept-card{{background:var(--chip);padding:1rem;border-radius:8px;border-left:4px solid var(--accent);margin:1rem 0}}
    .concept-id{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:white;padding:2px 6px;border-radius:4px;font-size:.85rem;border:1px solid var(--rule)}}

    /* Image zoom */
    .zoomable-img{{cursor:zoom-in;transition:transform .3s;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.1)}}
    .zoomable-img:hover{{transform:scale(1.02)}}
    .img-modal{{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.9);z-index:9999;justify-content:center;align-items:center}}
    .img-modal img{{max-width:95%;max-height:95%;cursor:zoom-out}}
    .img-modal.active{{display:flex}}

    /* Charts */
    .chart-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:1.5rem;margin:1.5rem 0}}
    .chart-card{{background:#fff;padding:1.5rem;border-radius:10px;box-shadow:0 2px 4px rgba(0,0,0,.1);border:1px solid var(--rule)}}
    .chart-card h4{{margin:0 0 1rem 0;font-size:1.1rem;color:var(--accent)}}
    .chart-container{{position:relative;height:300px}}

    /* Metrics cards */
    .metrics-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;margin:1rem 0}}
    .metric-card{{background:var(--chip);padding:1rem;border-radius:8px;border-left:4px solid var(--accent);text-align:center}}
    .metric-value{{font-size:2rem;font-weight:700;color:var(--accent)}}
    .metric-label{{font-size:.9rem;color:var(--muted);margin-top:.25rem}}

    /* List styling */
    ul{{padding-left:1.5rem}}
    li{{margin:.5rem 0}}

    .code{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--chip);padding:2px 6px;border-radius:4px;font-size:.9rem}}

    .timestamp{{color:var(--muted);font-size:.85rem;text-align:right;margin-top:2rem;padding-top:1rem;border-top:1px solid var(--rule)}}

    .badge{{display:inline-block;padding:4px 8px;border-radius:4px;font-size:.75rem;font-weight:600;text-transform:uppercase}}
    .badge-success{{background:var(--success);color:#fff}}
    .badge-warning{{background:var(--warning);color:#fff}}
    .badge-info{{background:var(--accent);color:#fff}}

    .info-icon{{display:inline-block;width:16px;height:16px;line-height:16px;text-align:center;background-color:#3498db;color:white;border-radius:50%;font-size:12px;font-weight:bold;margin-left:5px;cursor:help;position:relative}}
    .info-icon:hover::after{{content:attr(data-tooltip);position:absolute;left:25px;top:-5px;width:300px;padding:8px;background-color:#2c3e50;color:white;border-radius:4px;font-size:12px;font-weight:normal;z-index:1000;box-shadow:0 2px 8px rgba(0,0,0,.3);white-space:normal}}

    @media (max-width:900px){{
      .kv{{grid-template-columns:1fr;gap:.5rem}}
      .chart-grid{{grid-template-columns:1fr}}
      .metrics-grid{{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}}
    }}

    @media print{{
      .toc,.toc-controls,.btn{{display:none!important}}
      .section{{break-inside:avoid;box-shadow:none;border:1px solid var(--rule)}}
      .section.collapsed>:not(h2){{display:block}}
    }}
  </style>
</head>
<body>

<div class="container">
  <nav class="toc">
    <div class="toc-content">
      <div>
        <strong>Sections:</strong>
        <ol id="toc-list">
          <li><a href="#sec1">1. Model Details</a></li>
          <li><a href="#sec2">2. Intended Use</a></li>
          <li><a href="#sec3">3. Data & Factors</a></li>
          <li><a href="#sec4">4. Features & Outputs</a></li>
          <li><a href="#sec5">5. Performance</a></li>
          <li><a href="#sec6">6. Methodology</a></li>
          <li><a href="#sec7">7. Additional Info</a></li>
        </ol>
      </div>
      <div class="toc-controls">
        <button class="btn" onclick="expandAll()">Expand All</button>
        <button class="btn" onclick="collapseAll()">Collapse All</button>
        <button class="btn" onclick="zoomIn()">A+</button>
        <button class="btn" onclick="zoomOut()">A−</button>
      </div>
    </div>
  </nav>

  <div class="header">
    <h1>Medical AI Model Card</h1>
    <h2 style="border:none;padding:0;margin:.5rem 0">{model_name}</h2>
    <span class="model-badge">SMART Model Card v1.0</span>
  </div>

  {sections_html}

  <div class="timestamp">
    Generated: {created_at}
  </div>
</div>

<!-- Image zoom modal -->
<div class="img-modal" id="imgModal" onclick="closeImgModal()">
  <img id="modalImg" src="" alt="Zoomed image" />
</div>

<script>
// Collapsible sections
function toggleSection(btn) {{
  const section = btn.closest('.section');
  section.classList.toggle('collapsed');
  btn.setAttribute('aria-expanded', !section.classList.contains('collapsed'));
}}

function expandAll() {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('collapsed'));
}}

function collapseAll() {{
  document.querySelectorAll('.section').forEach(s => s.classList.add('collapsed'));
}}

// Text zoom
let fontSize = 1.0;
function zoomIn() {{
  fontSize = Math.min(1.5, fontSize + 0.1);
  document.documentElement.style.setProperty('--font-scale', fontSize);
}}
function zoomOut() {{
  fontSize = Math.max(0.8, fontSize - 0.1);
  document.documentElement.style.setProperty('--font-scale', fontSize);
}}

// Add toggle listeners
document.querySelectorAll('.section-toggle').forEach(btn => {{
  btn.addEventListener('click', () => toggleSection(btn));
}});

// Image zoom functionality
function openImgModal(imgSrc) {{
  document.getElementById('modalImg').src = imgSrc;
  document.getElementById('imgModal').classList.add('active');
}}

function closeImgModal() {{
  document.getElementById('imgModal').classList.remove('active');
}}

document.querySelectorAll('.zoomable-img').forEach(img => {{
  img.addEventListener('click', () => openImgModal(img.src));
}});

// Table search functionality
function filterTable(searchInput, tableId) {{
  const filter = searchInput.value.toUpperCase();
  const table = document.getElementById(tableId);
  const tr = table.getElementsByTagName('tr');

  for (let i = 1; i < tr.length; i++) {{
    let txtValue = tr[i].textContent || tr[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {{
      tr[i].style.display = '';
    }} else {{
      tr[i].style.display = 'none';
    }}
  }}

  // Reset pagination after filtering
  if (window.tablePaginationState && window.tablePaginationState[tableId]) {{
    window.tablePaginationState[tableId].currentPage = 1;
    updatePagination(tableId);
  }}
}}

// Table pagination functionality
window.tablePaginationState = {{}};

function initPagination(tableId, pageSize = 10) {{
  const table = document.getElementById(tableId);
  if (!table) return;

  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));

  window.tablePaginationState[tableId] = {{
    rows: rows,
    pageSize: pageSize,
    currentPage: 1,
    totalPages: Math.ceil(rows.length / pageSize)
  }};

  updatePagination(tableId);
}}

function updatePagination(tableId) {{
  const state = window.tablePaginationState[tableId];
  if (!state) return;

  const start = (state.currentPage - 1) * state.pageSize;
  const end = start + state.pageSize;

  // Show/hide rows based on current page
  state.rows.forEach((row, idx) => {{
    if (idx >= start && idx < end) {{
      row.style.display = '';
    }} else {{
      row.style.display = 'none';
    }}
  }});

  // Update pagination controls
  const paginationDiv = document.getElementById(`pagination-${{tableId}}`);
  if (paginationDiv) {{
    const prevDisabled = state.currentPage === 1 ? 'disabled' : '';
    const nextDisabled = state.currentPage === state.totalPages ? 'disabled' : '';

    paginationDiv.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:1rem;padding:0.75rem;background:var(--chip);border-radius:6px">
        <div>
          <button onclick="changePage('${{tableId}}', ${{state.currentPage - 1}})" ${{prevDisabled}}
                  style="padding:0.5rem 1rem;margin-right:0.5rem;cursor:pointer;border:1px solid var(--rule);border-radius:4px;background:white">
            ← Previous
          </button>
          <button onclick="changePage('${{tableId}}', ${{state.currentPage + 1}})" ${{nextDisabled}}
                  style="padding:0.5rem 1rem;cursor:pointer;border:1px solid var(--rule);border-radius:4px;background:white">
            Next →
          </button>
        </div>
        <div style="color:var(--muted)">
          Page ${{state.currentPage}} of ${{state.totalPages}} | Showing ${{start + 1}}-${{Math.min(end, state.rows.length)}} of ${{state.rows.length}} rows
        </div>
        <div>
          <label style="margin-right:0.5rem">Rows per page:</label>
          <select onchange="changePageSize('${{tableId}}', this.value)"
                  style="padding:0.5rem;border:1px solid var(--rule);border-radius:4px;cursor:pointer">
            <option value="10" ${{state.pageSize === 10 ? 'selected' : ''}}>10</option>
            <option value="25" ${{state.pageSize === 25 ? 'selected' : ''}}>25</option>
            <option value="50" ${{state.pageSize === 50 ? 'selected' : ''}}>50</option>
            <option value="100" ${{state.pageSize === 100 ? 'selected' : ''}}>100</option>
            <option value="9999" ${{state.pageSize === 9999 ? 'selected' : ''}}>All</option>
          </select>
        </div>
      </div>
    `;
  }}
}}

function changePage(tableId, newPage) {{
  const state = window.tablePaginationState[tableId];
  if (!state) return;

  if (newPage >= 1 && newPage <= state.totalPages) {{
    state.currentPage = newPage;
    updatePagination(tableId);
  }}
}}

function changePageSize(tableId, newSize) {{
  const state = window.tablePaginationState[tableId];
  if (!state) return;

  state.pageSize = parseInt(newSize);
  state.totalPages = Math.ceil(state.rows.length / state.pageSize);
  state.currentPage = 1;
  updatePagination(tableId);
}}

// Download table as CSV
function downloadTableAsCSV(tableId, filename) {{
  const table = document.getElementById(tableId);
  if (!table) return;

  let csv = [];
  const rows = table.querySelectorAll('tr');

  rows.forEach(row => {{
    const cols = row.querySelectorAll('td, th');
    const csvRow = [];
    cols.forEach(col => {{
      // Get text content and escape quotes
      let text = col.textContent.trim().replace(/"/g, '""');
      csvRow.push(`"${{text}}"`);
    }});
    csv.push(csvRow.join(','));
  }});

  const csvContent = csv.join('\\n');
  const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);

  link.setAttribute('href', url);
  link.setAttribute('download', filename || 'table_data.csv');
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}}

// Download data as JSON
function downloadAsJSON(data, filename) {{
  const jsonStr = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonStr], {{ type: 'application/json;charset=utf-8;' }});
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);

  link.setAttribute('href', url);
  link.setAttribute('download', filename || 'data.json');
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}}
</script>

</body>
</html>"""
