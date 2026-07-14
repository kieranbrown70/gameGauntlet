import tkinter as tk

from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR, TITLE_FONT, BUTTON_FONT 
)

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOUR)
        self.controller = controller
        
        # create three rows to keep everything centred
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # setup background
        content = tk.Frame(self, bg=BG_COLOUR)
        content.grid(row=1, column=0)
        
        # create the main title
        title = tk.Label(content, text="Kab's Game Gauntlet", font=TITLE_FONT, bg=BG_COLOUR, fg=FG_COLOUR)
        title.pack(pady=(0, 40))
        
        button_names = [
            ("New Game", "NewGameSetup"),
            ("How to Play", "HowToPlay"),
            ("Edit Rules", "EditRules"),
            ("Add Game", "AddGame"),
        ]
        
        # create all of the buttons for the main menu
        for label, page_name in button_names:
            button = self._make_button(content, label, page_name)
            button.pack(pady=8)
        
    # function to create a button with extra style
    def _make_button(self, parent, label, page_name):
        button = tk.Button(
            parent, text=label, font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, width=22, height=2, cursor="hand2",
            command=lambda: self.controller.show_frame(page_name),
        )
        
        button.bind("<Enter>", lambda e: button.config(bg=BUTTON_HOVER_BG_COLOUR))
        button.bind("<Leave>", lambda e: button.config(bg=BUTTON_BG_COLOUR))
        return button
        