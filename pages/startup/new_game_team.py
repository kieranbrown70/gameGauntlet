import tkinter as tk
import random

from pages.base_page import PlaceholderPage
from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR, BUTTON_FONT 
)

class NewGameTeam(PlaceholderPage):
    page_title = "Create Teams"
    
    def build_content(self):
        self.player_names = []
        self.team_names = []
        self.team_members = []
        
        # create a row for the randomize button and the player names to be entered
        self.players_row = tk.Frame(self.content, bg=BG_COLOUR)
        self.players_row.pack(pady=(0, 20))
        
        randomize_button = tk.Button(
            self.players_row, text="Randomize Teams", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, cursor="hand2",
            command=self._randomize_teams,
        )
        randomize_button.pack(side="left", padx=(0, 15))
        
        self.player_names_frame = tk.Frame(self.players_row, bg=BG_COLOUR)
        self.player_names_frame.pack(side="left")
        
        # team columns to be built dynamically based on the number of teams and players
        self.teams_frame = tk.Frame(self.content, bg=BG_COLOUR)
        self.teams_frame.pack(pady=(0, 20), fill="x")
        
        # check boxes to select the type of draft for the games
        self.neutral_draft = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self.content, text="Neutral Draft/Picks", variable=self.neutral_draft, font=BUTTON_FONT,
            bg=BG_COLOUR, fg=FG_COLOUR, selectcolor=BUTTON_BG_COLOUR, activebackground=BG_COLOUR,
            activeforeground=FG_COLOUR,
        ).pack(pady=(0, 20))
        
        # continue button to move to the next page
        self.continue_button = tk.Button(
            self.content, text="Continue", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, width=20, height=2, cursor="hand2",
            command=self._on_continue,
        )
        self.continue_button.pack()
        
    # function to rebuild the players and teams using the choices from the setup page
    def on_show(self):
        # retrieve the data from the previous page
        data = self.controller.shared_data
        num_of_players = int(data.get("num_of_players", 0))
        team_breakdown = data.get("team_breakdown", "1v1")
        
        # determine the number of teams and players per team based on the team breakdown
        segments = team_breakdown.split("v")
        self.num_of_teams = len(segments)
        self.players_per_team = int(segments[0]) if segments[0].isdigit() else num_of_players // max(self.num_of_teams, 1)
        
        # create the two teams for entry
        self._build_player_names(num_of_players)
        self._build_teams(self.num_of_teams, self.players_per_team)
    
    # function to create the player name entry fields
    def _build_player_names(self, num_of_players):
        # reset the current player names frame
        for widget in self.player_names_frame.winfo_children():
            widget.destroy()
        self.player_names = []
        
        # build the player name entry fields based on the number of players
        for i in range(num_of_players):
            entry = tk.Entry(self.player_names_frame, font=BUTTON_FONT, width=12, justify="center")
            entry.insert(0, f"Player{i + 1}")
            entry.pack(side="left", padx=5)
            self.player_names.append(entry)
    
    # function to create the team name entry fields
    def _build_teams(self, num_of_teams, players_per_team):
        # reset the current teams frame
        for widget in self.teams_frame.winfo_children():
            widget.destroy()
        self.team_names = []
        self.team_members = []
        
        # build the team columns based on the number of teams and players per team
        for col in range(num_of_teams):
            # configure the column to expand evenly
            self.teams_frame.columnconfigure(col, weight=1)
            column = tk.Frame(self.teams_frame, bg=BG_COLOUR)
            column.grid(row=0, column=col, padx=15, sticky="n")
            
            # populate the team name entry field
            team_name_entry = tk.Entry(column, font=BUTTON_FONT, width=16, justify="center")
            team_name_entry.insert(0, f"Team{col + 1}")
            team_name_entry.pack(pady=(0, 10))
            self.team_names.append(team_name_entry)
            
            # populate the player name entry fields for each team
            slots = []
            for i in range(players_per_team):
                slot = tk.Entry(column, font=BUTTON_FONT, width=16, justify="center")
                slot.pack(pady=3)
                slots.append(slot)
            self.team_members.append(slots)
    
    # function to randomize the players into the teams
    def _randomize_teams(self):
        # retrieve the player names from the entry fields and shuffle them
        names = [entry.get() for entry in self.player_names]
        random.shuffle(names)
        
        # populate the team member entry fields with the shuffled names
        i = 0
        for slots in self.team_members:
            for slot in slots:
                slot.delete(0, tk.END)
                if i < len(names):
                    slot.insert(0, names[i])
                    i += 1
                    
    def _on_continue(self):
        self.controller.shared_data["player_names"] = [entry.get() for entry in self.player_names]
        self.controller.shared_data["teams"] = {
            self.team_names[i].get(): [s.get() for s in self.team_members[i]]
            for i in range(len(self.team_names))
        }
        self.controller.shared_data["team_names"] = tuple(
            team_entry.get() for team_entry in self.team_names
        )
        self.controller.shared_data["neutral_draft"] = self.neutral_draft.get()
        self.controller.show_frame("NewGameDraft")
            
        
        