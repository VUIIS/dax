#!/usr/bin/env python3

import GUI_utils as GU
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def grab_info():
    project_id = project_entry.get()
    failed_id = failed_entry.get()
    running_id = running_entry.get()
    ig_un_id = ig_un_entry.get()
    ig_scan_id = ig_scan_entry.get()

    add_comm = ""

    if not project_id:
        messagebox.showerror("No Project", "Project ID is required!")

    if failed_id:
        add_comm = add_comm + f" -f"

    if running_id:
        add_comm = add_comm + f" -r"

    if ig_un_id:
        add_comm = add_comm + f" --ignoreUnusable"

    if ig_scan_id:
        add_comm = add_comm + f" --ignoreScans"
    
    XI_comm = f"Xnatinfo {project_id}"
    full_comm = XI_comm + add_comm

    # Run actual command and output results to text box
    COM = GU.CommandDisplay
    result = COM.run(full_comm)
    COM.output(output_text,result)


if __name__ == "__main__":
    WIN = GU.Window
    # Create/Size the main window
    root = WIN.create_window(tk.Tk(),"XNAT Info")
    root.attributes('-topmost',True)
    frame = WIN.create_frame(root)
    
    # Add input fields - Project
    WIN.add_label(frame,"Project:")
    project_entry = WIN.input_box(frame)

    # Add checkbutton - Failed Flag
    failed_entry = tk.IntVar()
    WIN.check_box(frame,"Check to print FAILED jobs. Not required.",failed_entry)

    # Add checkbutton - Running Flag
    running_entry = tk.IntVar()
    WIN.check_box(frame,"Check to print RUNNING jobs. Not required.",running_entry)

    # Add checkbutton - Ignore Unusable Flag
    ig_un_entry = tk.IntVar()
    WIN.check_box(frame,"Check to ignore unusable scans. Not required.",ig_un_entry)

    # Add checkbutton - Ignore Scans Flag
    ig_scan_entry = tk.IntVar()
    WIN.check_box(frame,"Check to ignore scans. Not required.",ig_scan_entry)

    # Create text box for terminal output
    output_text = WIN.terminal(root)

    # Button creation and start_download call
    tk.Button(frame,fg="#033769",bg="lightgrey",text="Check Project Information",command=grab_info).pack(pady=20)

    # Keep window open
    root.mainloop()