// code to apply after creating grids
// Set functions to check if there is an external filter to be applied
// Set external filter function

if (true || grid_instances["qa"].api) {
  gridApi_qa.setGridOption(
    "isExternalFilterPresent", 
    () => (
      selected_qa_projects.length > 0 ||
      selected_qa_sesstypes.length > 0
    )
  );

  gridApi_qa.setGridOption(
    "doesExternalFilterPass",
    params => {
      return (
        selected_qa_projects.includes(params.data.PROJECT) &&
        (selected_qa_sesstypes.length === 0 || 
          selected_qa_sesstypes.includes(params.data.SESSTYPE)) 
      );
    }
  );

  // When projects changes, filter rows in grid
  select_qa_projects.on("change", function(values) {

    // Clear it
    selected_qa_projects.length = 0;

    // Set values
    selected_qa_projects.push(...values);

    qaPivot(cur_qa_pivot);

    // Update proctype options based on selected projects
    updateQAProcTypeOptions();

    // Update sesstype options based on selected projects
    updateQASessTypeOptions();

    // Update scantype options based on selected projects
    updateQAScanTypeOptions();

    // Trigger grid updates
    refreshGrid(gridApi_qa, "qa");
  });

  // When proctypes changes, update
  select_qa_proctypes.on("change", function(values) {

    // Clear it
    selected_qa_proctypes.length = 0;

    // Set values
    selected_qa_proctypes.push(...values);

    // Trigger grid updates
    qaPivot(cur_qa_pivot);
    refreshGrid(gridApi_qa, "qa");
  });

  // When sesstype changes, filter rows in grid
  select_qa_sesstypes.on("change", function(values) {

    // Clear it
    selected_qa_sesstypes.length = 0;

    // Set values
    selected_qa_sesstypes.push(...values);

    // Trigger grid update
    qaPivot(cur_qa_pivot);
    refreshGrid(gridApi_qa, "qa");
  });

  // When scantypes changes, update
  select_qa_scantypes.on("change", function(values) {

    // Clear it
    selected_qa_scantypes.length = 0;

    // Set values
    selected_qa_scantypes.push(...values);

    // Trigger grid update
    qaPivot(cur_qa_pivot);
    refreshGrid(gridApi_qa, "qa");
  });
}


if (true || grid_instances["stats"].api) {
  gridApi_stats.setGridOption(
    "isExternalFilterPresent", 
    () => (
      true
    )
  );

  gridApi_stats.setGridOption(
    "doesExternalFilterPass",
    params => {
      return (
        (selected_stats_projects.includes(params.data.PROJECT)) &&
        (selected_stats_sesstypes.length === 0 ||
          selected_stats_sesstypes.includes(params.data.SESSTYPE))
      );
    }
  );

  // When stats projects changes, filter rows in grid
  select_stats_projects.on("change", function(values) {

    // Clear it
    selected_stats_projects.length = 0;

    // Set values
    selected_stats_projects.push(...values);

    // Update proctype options based on selected projects
    updateStatsProcTypeOptions();

    // Update sesstype options based on selected projects
    updateStatsSessTypeOptions();

    // Trigger grid updates
    refreshGrid(gridApi_stats, "stats");

    // update graph
    updateStatsGraph(cur_stats_trace);
  });

  // When stats proctypes changes,
  select_stats_proctypes.on("change", function(values) {

    // Clear it
    selected_stats_proctypes.length = 0;

    // Set values
    selected_stats_proctypes.push(...values);

    // set options in measures and xvariable
    updateStatsMeasuresOptions();
    updateStatsXvariableOptions();

    statsPivot(cur_stats_pivot);


    // Trigger grid updates
    refreshGrid(gridApi_stats, "stats");

    // update graph
    updateStatsGraph(cur_stats_trace);
  });

  // When selected stats measures changes, update columns and change xvariable options
  select_stats_measures.on("change", function(values) {

    // Clear it
    selected_stats_measures.length = 0;

    // Set values
    selected_stats_measures.push(...values);

    // Trigger grid updates
    //refreshGrid(gridApi_stats, "stats");
    statsPivot(cur_stats_pivot);

    // update graph
    updateStatsGraph(cur_stats_trace);
  });

  // When stats sesstype changes, filter rows in grid
  select_stats_sesstypes.on("change", function(values) {

    // Clear it
    selected_stats_sesstypes.length = 0;

    // Set values
    selected_stats_sesstypes.push(...values);

    // Trigger grid update
    refreshGrid(gridApi_stats, "stats");

    // Set available options in Measures and Xvariable

    // update graph
    updateStatsGraph(cur_stats_trace);
  });


  select_stats_xvariable.on("change", function(values) {
    selected_stats_xvariable = values[0];
    statsPivot(cur_stats_pivot);
    updateStatsGraph(cur_stats_trace);
  });
}


if (true || grid_instances["analyses"].api) {
  gridApi_analyses.setGridOption(
    "isExternalFilterPresent", 
    () => (
      selected_analyses_projects.length > 0 ||
      selected_analyses_invest.length > 0 ||
      selected_analyses_status.length > 0
    )
  );

  gridApi_analyses.setGridOption(
    "doesExternalFilterPass",
    params => {
      return (
        (selected_analyses_projects.length === 0 ||
          selected_analyses_projects.includes(params.data.PROJECT)) &&
        (selected_analyses_invest.length === 0 ||
          selected_analyses_invest.includes(params.data.INVESTIGATOR)) &&
        (selected_analyses_status.length === 0 ||
          selected_analyses_status.includes(params.data.STATUS)) 
      );
    }
  );

  select_analyses_projects.on("change", function(values) {
    selected_analyses_projects.length = 0;
    selected_analyses_projects.push(...values);
    refreshGrid(gridApi_analyses, "analyses");
  });


  select_analyses_invest.on("change", function(values) {
    selected_analyses_invest.length = 0;
    selected_analyses_invest.push(...values);
    refreshGrid(gridApi_analyses, "analyses");
  });


  select_analyses_status.on("change", function(values) {
    selected_analyses_status.length = 0;
    selected_analyses_status.push(...values);
    refreshGrid(gridApi_analyses, "analyses");
  });
}


if (true || grid_instances["processors"].api) {
  gridApi_processors.setGridOption(
    "isExternalFilterPresent", 
    () => (
      selected_processors_projects.length > 0
    )
  );

  gridApi_processors.setGridOption(
    "doesExternalFilterPass",
    params => {
      return (
        selected_processors_projects.length === 0 || 
        selected_processors_projects.includes(params.data.PROJECT)
        );
    }
  );

  select_processors_projects.on("change", function(values) {
    selected_processors_projects.length = 0;
    selected_processors_projects.push(...values);
    refreshGrid(gridApi_processors, "processors");

    // Also update the plotly graph
    updateProcessorsGraph();
  });
}


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

// force to clear initial options
updateStatsMeasuresOptions();
updateStatsXvariableOptions();
