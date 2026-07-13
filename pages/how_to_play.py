import tkinter as tk

class HowToPlay(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller