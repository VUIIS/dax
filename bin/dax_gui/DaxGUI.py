#!/usr/bin/env python3

import GUI_utils as GU
import tkinter as tk

import XnatCheckLoginGUI
import XnatDownloadGUI
import XnatInfoGUI
import XnatReportGUI
import XnatSwitchProcessStatusGUI
import XnatUploadGUI


if __name__ == "__main__":
    WIN = GU.Window
    # Create/Size the main window
    root = WIN.create_window(tk.Tk(),"DAX Tools")
    frame = WIN.create_frame(root)
 
    # Button creation
    WIN.add_main_button(frame,"Check Login","XnatCheckLoginGUI.py")
    WIN.add_main_button(frame,"Download","XnatDownloadGUI.py")
    WIN.add_main_button(frame,"Info","XnatInfoGUI.py")
    WIN.add_main_button(frame,"Report","XnatReportGUI.py")
    WIN.add_main_button(frame,"Switch Process Status","XnatSwitchProcessStatusGUI.py")
    WIN.add_main_button(frame,"Upload","XnatUploadGUI.py")

    # Keep window open
    root.mainloop()