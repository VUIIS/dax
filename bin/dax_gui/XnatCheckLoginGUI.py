#!/usr/bin/env python3

import GUI_utils as GU
import tkinter as tk


def check_login():
    host_id = host_entry.get()

    add_comm = ""

    if host_id:
        add_comm = f" --host {host_id}"

    # Build out command
    XCL_comm = f"XnatCheckLogin"
    full_comm = XCL_comm + add_comm

    # Run actual command and output results to text box
    COM = GU.CommandDisplay
    result = COM.run(full_comm)
    COM.output(output_text,result)


if __name__ == "__main__":
    WIN = GU.Window
    # Create/Size the main window
    root = WIN.create_window(tk.Tk(),"XNAT Check Login")
    frame = WIN.create_frame(root)

    # Add input fields - Host
    WIN.add_label(frame,"Host is not required. Environment variables will be checked if left blank.")
    WIN.add_label(frame,"Host:")
    host_entry = WIN.input_box(frame)

    # Create text box for terminal output
    output_text = WIN.terminal(root)

    # Button creation and start_download call
    tk.Button(frame,fg="#033769",bg="lightgrey",text="Check Login Information",command=check_login).pack(pady=20)

    # Keep window open
    root.mainloop()