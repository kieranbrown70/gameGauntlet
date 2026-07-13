import tkinter as tk

class EditRules(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller