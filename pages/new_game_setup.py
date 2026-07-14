import tkinter as tk

from pages.base_page import PlaceholderPage
from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR, BUTTON_FONT 
)

class NewGameSetup(PlaceholderPage):
    page_title = "New Game Setup"
    
    def build_content(self):
        # create two columns to seperate the settings
        self.content.columnconfigure(0, weight=1)
        self.content.columnconfigure(1, weight=1)
        
        # build the left side with the number of players and the team breakdown
        left = tk.Frame(self.content, bg=BG_COLOUR)
        left.grid(row=0, column=0, sticky="n", padx=20)
        
        tk.Label(left, text="Number of Players", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=(0, 5), anchor="w")
        self.num_of_players = tk.StringVar(value="Select...")
        players_menu = tk.OptionMenu(left, self.num_of_players, "2", "3", "4", command=self._on_selection_change)
        self._style_menu(players_menu)
        players_menu.pack(pady=(0, 20), fill="x")
        
        tk.Label(left, text="Team Breakdown", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=(0, 5), anchor="w")
        self.team_breakdown = tk.StringVar(value="Select...")
        teams_menu = tk.OptionMenu(left, self.team_breakdown, "1v1", "2v2", "1v1v1v1", command=self._on_selection_change)
        self._style_menu(teams_menu)
        teams_menu.pack(fill="x")
        
        # build the right side with the number of games and the continue button to the next menu
        right = tk.Frame(self.content, bg=BG_COLOUR)
        right.grid(row=0, column=1, sticky="n", padx=20)
        
        tk.Label(right, text="Number of Games", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=(0, 5), anchor="w")
        self.num_of_games = tk.StringVar(value="Select...")
        games_menu = tk.OptionMenu(right, self.num_of_games, "3", "5", "7", command=self._on_selection_change)
        self._style_menu(games_menu)
        games_menu.pack(pady=(0, 20), fill="x")
        
        self.continue_button = tk.Button(
            right, text="Continue", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, height=2, cursor="hand2",
            state="disabled",
            command=self._on_continue,
        )
        self.continue_button.pack(fill="x")
        
    # function to make it look sexy
    def _style_menu(self, menu):
        menu.config(
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, highlightthickness=0, cursor="hand2",
        )
        menu["menu"].config(bg=BUTTON_BG_COLOUR, fg=FG_COLOUR)
    
    def _on_selection_change(self, _=None):
        # retrieve the current selections and enable the continue button if all selections are made
        selections = (self.num_of_players.get(), self.team_breakdown.get(), self.num_of_games.get())
        state = "normal" if all(v != "Select..." for v in selections) else "disabled"
        self.continue_button.config(state=state)
        
    def _on_continue(self):
        pass