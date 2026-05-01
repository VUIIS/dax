#!/usr/bin/env python3

import GUI_utils as GU
import tkinter as tk
from tkinter import messagebox


def switch_status():
    project_id = project_entry.get()
    select_id = select_entry.get()
    txt_id = txt_entry.get()
    subject_id = subject_entry.get()
    session_id = session_entry.get()
    status_id = status_entry.get()
    frmr_status_id = frmr_status_entry.get()
    prc_type_id = prc_type_entry.get()
    nd_in_id = nd_in_entry.get()
    delete_id = delete_entry.get()
    qc_id = qc_entry.get()
    st_var_id = st_var_entry.get()
    regex_id = regex_entry.get()
    restart_id = restart_entry.get()
    rerun_id = rerun_entry.get()
    init_id = init_entry.get()
    rrdq_id = rrdq_entry.get()

    add_comm = ""

    if not project_id and not st_var_id:
        messagebox.showerror("No Project", "Project ID is required!")

    if select_id:
        add_comm = add_comm + f" --select {select_id}"

    if txt_id:
        add_comm = add_comm + f" -x {txt_id}"

    if subject_id:
        add_comm = add_comm + f" --subj {subject_id}"

    if session_id:
        add_comm = add_comm + f" --sess {session_id}"
    
    if status_id:
        add_comm = add_comm + f" -s {status_id}"

    if frmr_status_id:
        add_comm = add_comm + f" -f {frmr_status_id}"

    if prc_type_id:
        add_comm = add_comm + f" -t {prc_type_id}"

    if nd_in_id:
        add_comm = add_comm + f" -n {nd_in_id}"

    if delete_id:
        add_comm = add_comm + f" -d"

    if qc_id:
        add_comm = add_comm + f" --qc"

    if regex_id:
        add_comm = add_comm + f" --fullRegex"

    if restart_id:
        add_comm = add_comm + f" --restart"

    if rerun_id:
        add_comm = add_comm + f" --rerun"

    if init_id:
        add_comm = add_comm + f" --init"

    if rrdq_id:
        add_comm = add_comm + f" --rerundiskq"

    if st_var_id:
        full_comm = f"XnatSwitchProcessStatus --printstatus"
    else:
        XSPS_comm = f"XnatSwitchProcessStatus -p {project_id}"
        full_comm = XSPS_comm + add_comm

    # Run actual command and output results to text box
    COM = GU.CommandDisplay
    result = COM.run(full_comm)
    COM.output(output_text,result)


if __name__ == "__main__":
    WIN = GU.Window
    # Create/Size the main window
    root = WIN.create_window(tk.Tk(),"XNAT Switch Process Status")

    frame = GU.ScrollableFrame(root)
    for i in range(0):
        tk.Label(frame.scrollable_frame).pack()
    frame.pack(padx=30,pady=30)

    # Add input fields - Project
    WIN.add_label(frame.scrollable_frame,"Single or list of project IDs on XNAT separated by comma.")
    WIN.add_label(frame.scrollable_frame,"Project(s):")
    project_entry = WIN.input_box(frame.scrollable_frame)

    # Add input fields - Select
    WIN.add_label(frame.scrollable_frame,"Assessor label that you want to change the status.")
    WIN.add_label(frame.scrollable_frame,"Assessor Label:")
    select_entry = WIN.input_box(frame.scrollable_frame)

    # Add input fields - Text File
    WIN.add_label(frame.scrollable_frame,"File txt. Each line represents the label of the assessor which need to change status.")
    WIN.add_label(frame.scrollable_frame,"Text File:")
    txt_entry = WIN.input_box(frame.scrollable_frame)

    # Add input fields - Subject
    WIN.add_label(frame.scrollable_frame,"Change Status for only this subject/list of subjects.")
    WIN.add_label(frame.scrollable_frame,"Subject(s):")
    subject_entry = WIN.input_box(frame.scrollable_frame)

    # Add input fields - Session
    WIN.add_label(frame.scrollable_frame,"Change Status for only this session/list of sessions.")
    WIN.add_label(frame.scrollable_frame,"Session(s):")
    session_entry = WIN.input_box(frame.scrollable_frame)

    # Add input fields - Status
    WIN.add_label(frame.scrollable_frame,"Status you want to set on the Processes. E.G: 'NEED_TO_RUN'.")
    WIN.add_label(frame.scrollable_frame,"Status:")
    status_entry = WIN.input_box(frame.scrollable_frame)

    # Add input fields - Former Status
    WIN.add_label(frame.scrollable_frame,"Change assessors with this former status. E.G: 'JOB_FAILED'.")
    WIN.add_label(frame.scrollable_frame,"Former Status:")
    frmr_status_entry = WIN.input_box(frame.scrollable_frame)

    # Add input fields - Proctypes
    WIN.add_label(frame.scrollable_frame,"Assessor process type you want the status to changed.")
    WIN.add_label(frame.scrollable_frame,"Assessor Type:")
    prc_type_entry = WIN.input_box(frame.scrollable_frame)

    # Add input fields - NEED_INPUT
    WIN.add_label(frame.scrollable_frame,"Assessor process type that need to change to NEED_INPUTS because the assessors from -t you changed are inputs to those assessors.")
    WIN.add_label(frame.scrollable_frame,"Need Input:")
    nd_in_entry = WIN.input_box(frame.scrollable_frame)

    # Add checkbutton - Delete
    delete_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Delete the resources on the assessor. Not required.",delete_entry)

    # Add checkbutton - QC Status
    qc_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Change the quality control status on XNAT. Not required.",qc_entry)

    # Add checkbutton - Print Status Variables
    st_var_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Print status used by DAX to manage assessors. Not required.",st_var_entry)

    # Add checkbutton - Full Regex
    regex_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Use full regex for filtering data. Not required.",regex_entry)

    # Add checkbutton - Restart
    restart_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Restart the assessors by switching the status for all assessors found to NEED_TO_RUN and delete previous resources. Not required.",restart_entry)

    # Add checkbutton - Rerun
    rerun_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Rerun the assessors by switching status to NEED_TO_RUN for assessors that failed and delete previous resources. Not required.",rerun_entry)

    # Add checkbutton - Init
    init_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Init the assessors by switching status to NEED_INPUTS for assessors that have been set to NO_DATA. Not required.",init_entry)

    # Add checkbutton - Rerundiskq
    rrdq_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Rerun the assessor that have the status JOB_FAILED: switching status to NEED_INPUTS from JOB_FAILED and delete previous resources. Not required.",rrdq_entry)

    # Create text box for terminal output
    output_text = WIN.terminal(root)

    # Button creation and start_download call
    tk.Button(frame.scrollable_frame,fg="#033769",bg="lightgrey",text="Switch Status",command=switch_status).pack(pady=20)

    # Keep window open
    root.mainloop()