import tkinter as tk

from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR, PAGE_TITLE_FONT, BUTTON_FONT 
)

class PlaceholderPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOUR)
        self.controller = controller
        
        # header row to keep everything properly spaced across the top
        header = tk.Frame(self, bg=BG_COLOUR)
        header.pack(fill="x", pady=(20, 10), padx=20)
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=1)
        header.columnconfigure(2, weight=1)
        
        # set title of the page
        title = tk.Label(header, text=self.page_title, font=PAGE_TITLE_FONT, bg=BG_COLOUR, fg=FG_COLOUR)
        title.grid(row=0, column=1)
        
        # create a back button to return to the previous menu
        back_button = tk.Button(
            header, text="<<", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, width=4, height=1, cursor="hand2",
            command=lambda: controller.show_frame("MainMenu"),
        )
        back_button.grid(row=0, column=2, sticky="e")
        
        # content frame to be overwritten by each page
        self.content = tk.Frame(self, bg=BG_COLOUR)
        self.content.pack(fill="both", expand=True, padx=40, pady=20)
        
        self.build_content()
        
    # function to be overridden by the actual pages
    def build_content(self):
        pass