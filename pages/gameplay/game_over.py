import math
import tkinter as tk

from pages.base_page import PlaceholderPage
from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR,
    BUTTON_FONT, TITLE_FONT, POSITIVE_COLOUR, NEGATIVE_COLOUR,
    TEAM_HEADER_FONT, ROSTER_FONT,
    TEAM1_COLOUR, TEAM2_COLOUR, TEAM3_COLOUR, TEAM4_COLOUR,
)

TEAM_COLOURS = (TEAM1_COLOUR, TEAM2_COLOUR, TEAM3_COLOUR, TEAM4_COLOUR)


class GameOver(PlaceholderPage):
    page_title = "Game Over"

    def build_content(self):
        # set the title as the overall winner
        self.champion_label = tk.Label(self.content, text="", font=TITLE_FONT, bg=BG_COLOUR, fg=FG_COLOUR)
        self.champion_label.pack(pady=(20, 30))

        # team stat summary cards 
        self.teams_frame = tk.Frame(self.content, bg=BG_COLOUR)
        self.teams_frame.pack(fill="x", pady=(0, 30))

        # round-by-round history list
        tk.Label(self.content, text="Results", font=TEAM_HEADER_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(anchor="w", pady=(0, 6))
        self.history_frame = tk.Frame(self.content, bg=BG_COLOUR)
        self.history_frame.pack(fill="x", pady=(0, 30))

        # return to main menu
        tk.Button(
            self.content, text="Main Menu", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, width=20, height=2, cursor="hand2",
            command=lambda: self.controller.show_frame("MainMenu"),
        ).pack()

    # function to set up the page when reached
    def on_show(self):
        data = self.controller.shared_data
        self.team_names = data.get("team_names", ())
        self.teams = data.get("teams", {})
        self.player_stats = data.get("player_stats", {})
        self.game_wins = data.get("game_wins", {})
        self.total_rounds = data.get("num_of_games", 0)

        # check to see who won in the end
        wins_needed = self.controller.shared_data.get("wins_needed") or math.ceil(self.total_rounds / 2)
        champion = next((t for t in self.team_names if self.game_wins.get(t, 0) >= wins_needed), None)

        if champion and champion in self.team_names:
            idx = list(self.team_names).index(champion)
            colour = TEAM_COLOURS[idx] if idx < len(TEAM_COLOURS) else FG_COLOUR
            self.champion_label.config(text=f"{champion} wins the Gauntlet!", fg=colour)
        else:
            self.champion_label.config(text="Gauntlet complete!", fg=FG_COLOUR)

        self._refresh_teams()
        self._refresh_history()

    # function to display all the teams and the various player's stats
    def _refresh_teams(self):
        for widget in self.teams_frame.winfo_children():
            widget.destroy()

        for col in range(4):
            self.teams_frame.columnconfigure(col, weight=0)

        wins_needed = math.ceil(self.total_rounds / 2)

        # populate the team frame with all of the team's info
        for i, team_name in enumerate(self.team_names):
            self.teams_frame.columnconfigure(i, weight=1)
            team_colour = TEAM_COLOURS[i] if i < len(TEAM_COLOURS) else FG_COLOUR

            wins = self.game_wins.get(team_name, 0)
            header_text = f"{team_name}  ({wins}/{wins_needed})"

            box = tk.Frame(self.teams_frame, bg=BUTTON_BG_COLOUR)
            box.grid(row=0, column=i, padx=10, sticky="nsew")
            tk.Label(box, text=header_text, font=TEAM_HEADER_FONT,bg=BUTTON_BG_COLOUR, fg=team_colour).pack(pady=(10, 10))

            roster = tk.Frame(box, bg=BUTTON_BG_COLOUR)
            roster.pack(padx=15, pady=(0, 15), fill="x")
            roster.columnconfigure(0, weight=1)
            roster.columnconfigure(1, weight=0)
            roster.columnconfigure(2, weight=0)

            # populate the team's frame with each player's stats
            for row, player in enumerate(self.teams.get(team_name, [])):
                stats = self.player_stats.get(player, {"positive": 0, "negative": 0})
                positive = stats.get("positive", 0)
                negative = stats.get("negative", 0)

                tk.Label(
                    roster, text=player, font=ROSTER_FONT,
                    bg=BUTTON_BG_COLOUR, fg=FG_COLOUR, anchor="w"
                ).grid(row=row, column=0, sticky="ew", pady=2)
                tk.Label(
                    roster, text=f"+{positive}", font=ROSTER_FONT,
                    bg=BUTTON_BG_COLOUR, fg=POSITIVE_COLOUR, anchor="e"
                ).grid(row=row, column=1, sticky="e", padx=(10, 0), pady=2)
                tk.Label(
                    roster, text=f"-{negative}", font=ROSTER_FONT,
                    bg=BUTTON_BG_COLOUR, fg=NEGATIVE_COLOUR, anchor="e"
                ).grid(row=row, column=2, sticky="e", padx=(6, 0), pady=2)

    # function to build the round by round results list
    def _refresh_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        round_results = self.controller.shared_data.get("round_results", [])

        # iterate through each of the game rounds
        for i, entry in enumerate(round_results):
            game_name = entry.get("game", "Unknown")
            winner = entry.get("winner", "Unknown")

            # colour the winner name by their team index
            if winner in self.team_names:
                idx = list(self.team_names).index(winner)
                colour = TEAM_COLOURS[idx] if idx < len(TEAM_COLOURS) else FG_COLOUR
            else:
                colour = FG_COLOUR

            row = tk.Frame(self.history_frame, bg=BG_COLOUR)
            row.pack(fill="x", pady=2)

            tk.Label(
                row, text=f"Game {i + 1}  —  {game_name}", font=ROSTER_FONT,
                bg=BG_COLOUR, fg=FG_COLOUR, anchor="w",
            ).pack(side="left")
            tk.Label(
                row, text=winner, font=ROSTER_FONT,
                bg=BG_COLOUR, fg=colour, anchor="e",
            ).pack(side="right")