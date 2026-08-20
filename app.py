import tkinter as tk

from config import BG_COLOUR, WINDOW_TITLE, WINDOW_SIZE
from pages.main_menu import MainMenu
from pages.startup.new_game_setup import NewGameSetup
from pages.startup.new_game_team import NewGameTeam
from pages.startup.new_game_draft import NewGameDraft
from pages.gameplay.game_select import GameSelect
from pages.gameplay.play_game import PlayGame
from pages.how_to_play import HowToPlay
from pages.edit_rules import EditRules

class App(tk.Tk):
    """
    This controlls the application window and holds each other page in a stack
    To add more pages, add to the tuple below
    """
    
    PAGES = (MainMenu, NewGameSetup, NewGameTeam, NewGameDraft, GameSelect, PlayGame, HowToPlay, EditRules)
    
    def __init__(self):
        # make da window
        super().__init__()
        self.shared_data = {}
        self.history = []
        self.current_frame_name = None
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.configure(bg=BG_COLOUR)
        self.minsize(1100, 800)
        
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
    
    # function to display the objects on the page 
    def show_frame(self, page_name: str, add_to_history: bool = True):
        # remember where the last page was
        if add_to_history and self.current_frame_name is not None:
            self.history.append(self.current_frame_name)
        
        self.current_frame_name = page_name
        frame = self.frames[page_name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()
        
    # function help navigate back to the previous page that was open
    def go_back(self):
        if self.history:
            previous_page = self.history.pop()
        else:
            previous_page = "MainMenu"
        self.show_frame(previous_page, add_to_history=False)