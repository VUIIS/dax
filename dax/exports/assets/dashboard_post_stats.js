
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

// force to clear initial options
updateStatsMeasuresOptions();
updateStatsXvariableOptions();
