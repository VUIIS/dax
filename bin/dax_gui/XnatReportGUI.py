#!/usr/bin/env python3

import GUI_utils as GU
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def report():
    project_id = project_entry.get()
    format_id = format_entry.get()
    fo_var_id = fo_var_entry.get()

    add_comm = ""

    if not project_id and not fo_var_id:
        messagebox.showerror("No Project", "Project ID is required!")
    
    frame.focus_force()
    file_id = filedialog.asksaveasfilename(title="Path to a csv file to save report. Not required.")
    if file_id:
        add_comm = add_comm + f" -c {file_id}"

    if format_id:
        add_comm = add_comm + f" --format {format_id}"

    if fo_var_id:
        full_comm = f"Xnatreport --printformat"
    else:
        XR_comm = f"Xnatreport -p {project_id}"
        full_comm = XR_comm + add_comm

    # Run actual command and output results to text box
    COM = GU.CommandDisplay
    result = COM.run(full_comm)
    COM.output(output_text,result)


if __name__ == "__main__":
    WIN = GU.Window
    # Create/Size the main window
    root = WIN.create_window(tk.Tk(),"XNAT Report")
    frame = WIN.create_frame(root)

    # Add input fields - Project
    WIN.add_label(frame,"Single or list of project IDs on XNAT separated by comma.")
    WIN.add_label(frame,"Project(s):")
    project_entry = WIN.input_box(frame)

    # Add input fields - Format
    WIN.add_label(frame,"Header for the CSV. Format: variable names separated by comma. Not required.")
    WIN.add_label(frame,"Format:")
    format_entry = WIN.input_box(frame)

    # Add checkbutton - Print Format Variables
    fo_var_entry = tk.IntVar()
    WIN.check_box(frame,"Check to print available var names for --format. Not required.",fo_var_entry)

    # Create text box for terminal output
    output_text = WIN.terminal(root)

    # Button creation and start_download call
    tk.Button(frame,fg="#033769",bg="lightgrey",text="Run Xnat Report",command=report).pack(pady=20)

    # Keep window open
    root.mainloop()