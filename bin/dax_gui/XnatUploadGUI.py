#!/usr/bin/env python3

import GUI_utils as GU
import tkinter as tk
from tkinter import filedialog


def upload():
    sess_id = sess_entry.get()
    report_id = report_entry.get()
    force_id = force_entry.get()
    del_id = del_entry.get()
    del_all_id = del_all_entry.get()
    no_ext_id = no_ext_entry.get()
    modal_id = modal_entry.get()

    add_comm = ""

    frame.focus_force()
    file_id = filedialog.askopenfilename(title="CSV file with the information for uploading data to XNAT.")
    if file_id:
        add_comm = add_comm + f" -c {file_id}"

    if sess_id:
        add_comm = add_comm + f" --sess {sess_id}"

    if report_id:
        add_comm = add_comm + f" --report"
    
    if force_id:
        add_comm = add_comm + f" --force"

    if del_id:
        add_comm = add_comm + f" --delete"

    if del_all_id:
        add_comm = add_comm + f" --deleteAll"

    if no_ext_id:
        add_comm = add_comm + f" --noextract"
    
    frame.focus_force()
    out_id = filedialog.asksaveasfilename(title="File path to store the script logs.")
    if out_id:
        add_comm = add_comm + f" -o {out_id}"

    frame.focus_force()
    bids_id = filedialog.askdirectory(title="BIDS Directory to convert to XNAT and then upload.")
    if bids_id:
        add_comm = add_comm + f" -b {bids_id}"

    if modal_id:
        full_comm = f"Xnatupload --printmodality"
    else:
        XU_comm = f"Xnatupload"
        full_comm = XU_comm + add_comm

    # Run actual command and output results to text box
    COM = GU.CommandDisplay
    result = COM.run(full_comm)
    COM.output(output_text,result)


if __name__ == "__main__":
    WIN = GU.Window
    # Create/Size the main window
    root = WIN.create_window(tk.Tk(),"XNAT Upload")

    frame = GU.ScrollableFrame(root)
    for i in range(0):
        tk.Label(frame.scrollable_frame).pack()
    frame.pack(padx=30,pady=30)

    # Add input fields - Session Type
    WIN.add_label(frame.scrollable_frame,"Session type on Xnat. Use printmodality to see the options. Not required.")
    WIN.add_label(frame.scrollable_frame,"Session Type:")
    sess_entry = WIN.input_box(frame.scrollable_frame)

    # Add checkbutton - Report
    report_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Print a report to verify inputs. Not required.",report_entry)

    # Add checkbutton - Force
    force_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Force the upload and remove previous resources. Not required.",force_entry)

    # Add checkbutton - Delete
    del_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Delete resource files prior to upload. Not required.",del_entry)

    # Add checkbutton - Delete All
    del_all_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Delete all resources in object prior to upload. Not required.",del_all_entry)

    # Add checkbutton - No Extract
    no_ext_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Do not extract the zip files on XNAT when uploading a folder. Not required.",no_ext_entry)

    # Add checkbutton - Print Modality
    modal_entry = tk.IntVar()
    WIN.check_box(frame.scrollable_frame,"Display the different modality available on XNAT for a session. Not required.",modal_entry)

    # Create text box for terminal output
    output_text = WIN.terminal(root)

    # Button creation and start_download call
    tk.Button(frame.scrollable_frame,fg="#033769",bg="lightgrey",text="Upload Data",command=upload).pack(pady=20)

    # Keep window open
    root.mainloop()