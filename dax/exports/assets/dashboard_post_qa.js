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
