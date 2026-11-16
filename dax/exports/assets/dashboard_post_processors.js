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
