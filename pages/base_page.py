import tkinter as tk

from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR, PAGE_TITLE_FONT, BUTTON_FONT 
)

class PlaceholderPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOUR)
        self.controller = controller
        
        # set title of the page
        title = tk.Label(self, text=self.page_title, font=PAGE_TITLE_FONT, bg=BG_COLOUR, fg=FG_COLOUR)
        title.pack(pady=(40, 10))
        
        # placehoder text for the page that will get replaced
        placeholder = tk.Label(self, text="whateva change later", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR)
        placeholder.pack(pady=10)
        
        self.build_content()
        
        # create a back button to return to the previous menu
        back_button = tk.Button(
            self, text="<<", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, width=20, height=2, cursor="hand2",
            command=lambda: controller.show_frame("MainMenu"),
        )
        back_button.pack(side="bottom", pady=30)
        
    # function to be overridden by the actual pages
    def build_content(self):
        pass