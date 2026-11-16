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
