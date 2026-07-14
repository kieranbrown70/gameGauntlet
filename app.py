import tkinter as tk

from config import BG_COLOUR, WINDOW_TITLE, WINDOW_SIZE
from pages.main_menu import MainMenu
from pages.new_game_setup import NewGameSetup
from pages.how_to_play import HowToPlay
from pages.edit_rules import EditRules
from pages.add_game import AddGame

class App(tk.Tk):
    """
    This controlls the application window and holds each other page in a stack
    To add more pages, add to the tuple below
    """
    
    PAGES = (MainMenu, NewGameSetup, HowToPlay, EditRules, AddGame)
    
    def __init__(self):
        # make da window
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.configure(bg=BG_COLOUR)
        self.minsize(900, 600)
        
        # creating the stack for the pages to populate to allow easy switching
        container = tk.Frame(self, bg=BG_COLOUR)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # populate the stack with all of the pages
        self.frames = {}
        for PageClass in self.PAGES:
            frame = PageClass(parent=container, controller=self)
            self.frames[PageClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("MainMenu")
        
    def show_frame(self, page_name: str):
        frame = self.frames[page_name]
        frame.tkraise()