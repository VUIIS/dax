'''Text templates for creating html/javascript'''


_MARKDOWN_CELL_RENDERER_JS = r"""
function markdownCellRenderer(params) {
  const v = params.value;
  if (v === null || v === undefined) return '';
  const s = String(v);
  const m = s.match(/^\[(.*)\]\((.*)\)$/);
  if (m) {
    const a = document.createElement('a');
    a.href = m[2];
    a.target = '_blank';
    a.rel = 'noopener';
    a.textContent = m[1];
    return a;
  }
  return s;
}
"""


# Main page with multiple tabs, including javascript function and listeners
main_html_template = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/tom-select@2.6.2/dist/css/tom-select.bootstrap5.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/ag-grid-community/dist/ag-grid-community.min.js"></script>
  <script src="https://cdn.plot.ly/plotly-4.0.0.min.js"></script>
  <script>
    (function () {
      var saved = localStorage.getItem("theme");
      var os = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      var theme = saved || os;
      document.documentElement.setAttribute("data-bs-theme", theme);
      document.documentElement.setAttribute("data-ag-theme-mode", theme+"-blue");
    })();
  </script>
  <style>
    .ag-grid {
      height: 400px;
      width: 100%;
    }
    .graph-grid {
      display: grid;
      grid-auto-flow: column;
      grid-auto-columns: max-content;
      overflow-x: auto;
      gap: 5px;
    }
    .graph-container {
      height: 400px;
      width: 400px;
      border: 1px solid #666666;
      border-radius: 10px;
      overflow: hidden;
    }
  </style>
</head>
<body>
  <div class="container-fluid p-3">
    <ul class="nav nav-tabs">TABBUTTONS</ul>
    <div class="tab-content pt-3">TABPANELS</div>
    <h5 align="center">garjus/dax dashboard</h5>
    <h6 align="center">Data Exported @ TIMESTAMP</h6>
    <div class="text-center"><button id="themetoggle" class="btn btn-outline-secondary">dark/light</button></div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/tom-select@2.6.2/dist/js/tom-select.complete.min.js"></script>
  <script>
    GRIDJS
    BUTTONJS
  </script>
</body>
</html>
'''


grid_js_template = '''
const columnDefs_ID = COLUMNS;

const rowData_ID =  ROWS;

const gridOptions_ID = {
  columnDefs: columnDefs_ID,
  rowData: rowData_ID,
  defaultColDef: {
    minWidth: 40,
    sortable: true,
    resizable: true,
    flex: 1,
    filter: true,
    cellDataType: "text",
  },
  autoSizeStrategy: {type: "fitCellContents"},
  onGridReady: (params) => {
    grid_instances["ID"].api = params.api;

    updateRowCounts(params.api, "ID_rowcount");

    const active_pane = document.querySelector(".tab-pane.active");
    if (active_pane && active_pane.id === "panel_ID") {
      params.api.autoSizeAllColumns();
      grid_instances["ID"].resized = true;
    }
  }
};

// Find the div for this grid
const gridElement_ID = document.querySelector("#grid_ID");

const gridApi_ID = agGrid.createGrid(gridElement_ID, gridOptions_ID);

function onButtonExport_ID() {
  const csvfilename = document.getElementById("csvinput_ID").value.trim()
  gridApi_ID.exportDataAsCsv({fileName: csvfilename});
}
'''


tab_button_active_html_template = '''
    <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#panel_ID">LABEL</button></li>
'''


tab_button_html_template = '''
    <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#panel_ID">LABEL</button></li>
'''


tab_panel_html_template = '''
    <div class="tab-pane" id="panel_ID">
      PANEL
      <div id="grid_ID" class="ag-grid"></div>
    </div>
'''


tab_panel_active_html_template = '''
    <div class="tab-pane active" id="panel_ID">
      PANEL
      <div id="grid_ID" class="ag-grid"></div>
    </div>
'''


csv_button_html_template = '''
    <div class="input-group mb-3" style="max-width: 400px;">
      <input id="csvinput_ID" type="text" class="form-control" placeholder="export_ID.csv"></input>
      <button class="btn btn-primary btn-sm" onclick="onButtonExport_ID()">EXPORT</button>
    </div>
'''


dropdown_js_template = '''
const select_ID = new TomSelect("#dropdown_ID", {
  allowEmptyOption: true,
  maxOptions: null,
  closeAfterSelect: true,
  //hideSelected: true,
  plugins: {
    "remove_button": {},
    "input_autogrow": {},
    //"checkbox_options": {
    //  "checkedClassNames": ["ts-checked"],
    //  "uncheckedClassNames": ["ts-unchecked"]
    //},
    "clear_button": {},
  }
});
'''


dropdown_html_template = '''
    <select id="dropdown_ID" multiple class="w-100 form-select form-select-md" placeholder="Select LABEL...">
      OPTIONS
    </select>
'''


dropdown_option_html_template = '''
    <option value="VALUE">LABEL</option>
'''


badge_html_template = '''
    <span id="ID" class="badge bg-secondary fs-5">0 rows</span>
'''


graph_html_template = '''
    <div id="graph_ID" class="graph-grid w-100"></div>
'''



pivot_bar_html_template = '''
    <ul class="nav nav-pills">PIVOTBUTTONS</ul>
'''


pivot_button_active_html_template = '''
    <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#pivot_ID">LABEL</button></li>
'''


pivot_button_html_template = '''
    <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#pivot_ID">LABEL</button></li>
'''


groupby_bar_html_template = '''
    <ul class="nav nav-pills flex-column">GROUPBYBUTTONS</ul>
'''


groupby_button_active_html_template = '''
    <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#groupby_ID">LABEL</button></li>
'''


groupby_button_html_template = '''
    <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#groupby_ID">LABEL</button></li>
'''


top_row_html_template = '''
    <div class="row">
      <div class="col-md-3 mb-4">
        FILTERS
      </div>
       <div class="col-md-2 mb-4">
        GROUPBYS
      </div>
      <div class="col-md-7 mb-4">
        GRAPHS
      </div>
    </div>
'''


qa_data_js_template = '''
const columnDefs_QA = COLUMNS;
const rowData_QA = ROWS;
'''


stats_data_js_template = '''
const columnDefs_STATS = COLUMNS;
const rowData_STATS = ROWS;
'''


data_dict_js_template = '''
const proc2stats = PROC2STATS;
const proj2procs = PROJ2PROCTYPES;
const proj2sesstypes = PROJ2SESSTYPES;
const proj2scantypes = PROJ2SCANTYPES;
'''
