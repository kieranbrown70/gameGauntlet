import tkinter as tk

from pages.base_page import PlaceholderPage
from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR, BUTTON_FONT 
)

PLAYERS_TO_TEAMS = {
    "2": ["1v1"],
    "3": ["1v1v1"],
    "4": ["2v2", "1v1v1v1"],
}

TEAMS_TO_PLAYERS = {
    "1v1": "2",
    "1v1v1": "3",
    "2v2": "4",
    "1v1v1v1": "4",
}

DEFAULT_TEAM_FOR_PLAYERS = {
    "2": "1v1",
    "3": "1v1v1",
    "4": "2v2",
}

class NewGameSetup(PlaceholderPage):
    page_title = "New Game Setup"
    
    def build_content(self):
        # create two columns to seperate the settings
        self.content.columnconfigure(0, weight=1)
        self.content.columnconfigure(1, weight=1)
        
        # build the left side with the number of players and the team breakdown
        self._syncing = False
        self._ui_ready = False
        left = tk.Frame(self.content, bg=BG_COLOUR)
        left.grid(row=0, column=0, sticky="n", padx=20)
        
        tk.Label(left, text="Number of Players", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=(0, 5), anchor="w")
        self.num_of_players = tk.StringVar(value="Select...")
        self.players_menu = tk.OptionMenu(left, self.num_of_players, "2", "3", "4", command=self._on_players_change)
        self._style_menu(self.players_menu)
        self.players_menu.pack(pady=(0, 20), fill="x")
        
        tk.Label(left, text="Team Breakdown", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=(0, 5), anchor="w")
        self.team_breakdown = tk.StringVar(value="Select...")
        self.teams_menu = tk.OptionMenu(left, self.team_breakdown, "1v1", "1v1v1", "2v2", "1v1v1v1", command=self._on_teams_change)
        self._style_menu(self.teams_menu)
        self.teams_menu.pack(fill="x")
        
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
        self._ui_ready = True
        
    # function to make it look sexy
    def _style_menu(self, menu):
        menu.config(
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, highlightthickness=0, cursor="hand2",
        )
        menu["menu"].config(bg=BUTTON_BG_COLOUR, fg=FG_COLOUR)
    
    # function to rebuild the team breakdown options based on another selection 
    def _rebuild_menu(self, menu, var, options, command):
        dropdown = menu["menu"]
        dropdown.delete(0, "end")
        for option in options:
            dropdown.add_command(label=option, command=lambda v=option: self._select(var, v, command))
        
    # function to handle any changes in the number of players
    def _select(self, var, value, command):
        var.set(value)
        command(value)
    
    # function to handle any changes in the number of players
    def _on_players_change(self, players):
        if not self._ui_ready or self._syncing:
            return
        self._syncing = True
        
        # rebuild the team breakdown options based on the number of players
        valid_teams = PLAYERS_TO_TEAMS[players]
        self._rebuild_menu(self.teams_menu, self.team_breakdown, valid_teams, self._on_teams_change)

        if self.team_breakdown.get() not in valid_teams:
            self.team_breakdown.set(DEFAULT_TEAM_FOR_PLAYERS[players])
        
        self._syncing = False
        self._on_selection_change()
        
    # function to handle any changes in the team breakdown
    def _on_teams_change(self, teams):
        if not self._ui_ready or self._syncing:
            return
        self._syncing = True

        # rebuild the number of players options based on the team breakdown        
        valid_players = TEAMS_TO_PLAYERS[teams]
        self.num_of_players.set(valid_players)
        
        valid_teams = PLAYERS_TO_TEAMS[valid_players]
        self._rebuild_menu(self.teams_menu, self.team_breakdown, valid_teams, self._on_teams_change)
        self.team_breakdown.set(teams)
        
        self._syncing = False
        self._on_selection_change()
    
    # function to handle the changes in setting selection
    def _on_selection_change(self, _=None):
        # retrieve the current selections and enable the continue button if all selections are made
        selections = (self.num_of_players.get(), self.team_breakdown.get(), self.num_of_games.get())
        state = "normal" if all(v != "Select..." for v in selections) else "disabled"
        self.continue_button.config(state=state)
        
    def _on_continue(self):
        self.controller.shared_data["num_of_players"] = int(self.num_of_players.get())
        self.controller.shared_data["team_breakdown"] = self.team_breakdown.get()
        self.controller.shared_data["num_of_games"] = int(self.num_of_games.get())
        self.controller.show_frame("NewGameTeam")