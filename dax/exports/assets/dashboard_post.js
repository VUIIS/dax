// code to apply after creating grids
// Set functions to check if there is an external filter to be applied
// Set external filter function

// When tab changes, check if we have resized the grid on the tab, 
// we have to resize first time a tab is active
// because the grid is initially in a display none
// We add a listener to the tab toggle bootstrap that checks for resized
// Also, Listen for qa pivot click and trigger handler function
document.querySelectorAll('button[data-bs-toggle="tab"]').forEach((tabEl) => {
  tabEl.addEventListener('shown.bs.tab', (event) => {
    const target_id = event.target.getAttribute('data-bs-target').substring(1);

    // Handle grid switching when main tab changes
    let instance = '';

    if (target_id === "panel_analyses") {
      instance = grid_instances["analyses"];
    } else if (target_id === "panel_stats") {
      instance = grid_instances["stats"];
    } else if (target_id === "panel_processors") {
      instance = grid_instances["processors"];
    } else if (target_id === "panel_qa") {
      instance = grid_instances["qa"];
    }

    if (instance && instance.api && !instance.resized) {
      instance.api.autoSizeAllColumns();
      instance.resized = true;
    }

    // Handle pivots
    if (target_id === "pivot_qa_scans") {
      qaPivot('scans');
    } else if (target_id === "pivot_qa_assessors") {
      qaPivot('assessors');
    } else if (target_id === "pivot_qa_sessions") {
      qaPivot('sessions');
    } else if (target_id === "pivot_qa_subjects") {
      qaPivot('subjects');
    } else if (target_id === "pivot_qa_projects") {
      qaPivot('projects');
    } else if (target_id === "pivot_stats_assessors") {      
      statsPivot('assessors');
    } else if (target_id === "pivot_stats_sessions") {
      statsPivot('sessions');
    } else if (target_id === "pivot_stats_subjects") {
      statsPivot('subjects');
    } else if (target_id === "groupby_stats_project") {
      cur_stats_trace = 'project';
      updateStatsGraph('project');
    } else if (target_id === "groupby_stats_sesstype") {
      cur_stats_trace = 'sesstype';
      updateStatsGraph('sesstype');
    } else if (target_id === "groupby_stats_site") {
      cur_stats_trace = 'site';
      updateStatsGraph('site');
    } else if (target_id === "groupby_stats_all") {
      cur_stats_trace = 'all';
      updateStatsGraph('all');
    }
  });
});


const setTheme = (theme) => {
  // Set bootstrap to dark/light
  document.documentElement.setAttribute("data-bs-theme", theme);

  // Set ag-grid to dark/light
  document.documentElement.setAttribute("data-ag-theme-mode", theme+"-blue");

  // Apply dark/light to plotly theme
  

  // Save for next time
  localStorage.setItem("theme", theme);
};

// handle click on theme toggle button by switching between light and dark
document.querySelector("#themetoggle").addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-bs-theme");
  setTheme(current === "dark" ? "light" : "dark");
});
