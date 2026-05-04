#!/usr/bin/env python3

import os
import subprocess
import tkinter as tk
from tkinter import ttk


class Window(object):
    def create_window(self,title):
        self.geometry('1280x1280')
        self.configure(bg="#033769")
        self.title(title)
        # self.attributes('-topmost',True)
        # self.lift()
        return self
    
    def create_frame(self):
        frame = tk.Frame(self,width=620,height=620)
        frame.pack(padx=30,pady=30)
        frame.configure(bg="lightgrey")
        return frame
    
    def add_main_button(self,txt,cmd):
        button = tk.Button(self,fg="#033769",bg="lightgrey",text=txt,command=lambda: os.system(f"python {cmd}")).pack(pady=20)
        return button
    
    def add_label(self,txt):
        label = tk.Label(self,text=txt).pack(pady=5)
        return label
    
    def input_box(self):
        entry = tk.Entry(self)
        entry.pack(pady=5,padx=100)
        return entry
    
    def check_box(self,txt,flag):
        check_box = tk.Checkbutton(self,text=txt,variable=flag)
        check_box.pack()
        return check_box
    
    def terminal(self):
        term = tk.Text(self,wrap="word",height=200,width=300)
        term.pack(padx=10,pady=10)
        return term
    

class ScrollableFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        canvas = tk.Canvas(self,width=1000,height=620)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class CommandDisplay(object):
    def run(self):
        res = subprocess.run(self,shell=True,capture_output=True,text=True)
        return res
    
    def output(self,result):
        self.delete("1.0",tk.END)
        self.insert(tk.END,result.stdout)