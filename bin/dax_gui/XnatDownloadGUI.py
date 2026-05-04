#!/usr/bin/env python3

import GUI_utils as GU
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def start_download():
    # Grab information
    project_id = project_entry.get()
    subject_id = subject_entry.get()
    session_id = session_entry.get()
    scan_id = scan_entry.get()
    scan_resource = scan_resource_entry.get()
    assessor_id = assessor_entry.get()
    assessor_resource = assessor_resource_entry.get()

    scan_comm = ""
    assessor_comm = ""

    if not project_id:
        messagebox.showerror("No Project", "Project ID is required!")

    if not subject_id:
        subject_id = 'all'

    if not session_id:
        session_id = 'all'

    if scan_id and not scan_resource:
        scan_comm = f" -s {scan_id} --rs all"
    elif not scan_id and scan_resource:
        scan_comm = f" -s all --rs {scan_resource}"
    elif scan_id and scan_resource:
        scan_comm = f" -s {scan_id} --rs {scan_resource}"

    if assessor_id and not assessor_resource:
        assessor_comm = f" -a {assessor_id} --ra all"
    elif not assessor_id and assessor_resource:
        assessor_comm = f" -a all --ra {assessor_resource}"
    elif assessor_id and assessor_resource:
        assessor_comm = f" -a {assessor_id} --ra {assessor_resource}"

    # Ask for download directory
    output_dir = filedialog.askdirectory(title="Select Output Directory")

    XD_comm = f"XnatDownload -p {project_id} -d {output_dir} --subj {subject_id} --sess {session_id}"

    # Build XnatDownload command
    full_comm = XD_comm + scan_comm + assessor_comm

    # Run actual command and output results to text box
    COM = GU.CommandDisplay
    result = COM.run(full_comm)
    COM.output(output_text,result)


if __name__ == "__main__":
    WIN = GU.Window
    # Create/Size the main window
    root = WIN.create_window(tk.Tk(),"XNAT Download")
    frame = WIN.create_frame(root)

    # Add input fields - Project ID
    WIN.add_label(frame,"Project ID:")
    project_entry = WIN.input_box(frame)

    # Add input fields - Subject ID 
    WIN.add_label(frame,"Subject ID:")
    subject_entry = WIN.input_box(frame)

    # Add input fields - Session ID
    WIN.add_label(frame,"Session ID:")
    session_entry = WIN.input_box(frame)

    # Add input field - Scan ID
    WIN.add_label(frame,"Scan ID:")
    scan_entry = WIN.input_box(frame)

    # Add input field - Scan Resource
    WIN.add_label(frame,"Scan Resources:")
    scan_resource_entry = WIN.input_box(frame)

    # Add input field - Assessor ID
    WIN.add_label(frame,"Assessor ID:")
    assessor_entry = WIN.input_box(frame)

    # Add input field - Assessor Resource
    WIN.add_label(frame,"Assessor Resource:")
    assessor_resource_entry = WIN.input_box(frame)

    # Create text box for terminal output
    output_text = WIN.terminal(root)

    # Button creation and start_download call
    tk.Button(frame,fg="#033769",bg="lightgrey",text="Select Output Directory and Start",command=start_download).pack(pady=20)

    # Keep window open
    root.mainloop()
