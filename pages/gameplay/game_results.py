import math
import tkinter as tk

from pages.base_page import PlaceholderPage
from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR,
    BUTTON_FONT, POSITIVE_COLOUR, NEGATIVE_COLOUR,
    TEAM_HEADER_FONT, ROSTER_FONT, PAGE_TITLE_FONT,
    TEAM1_COLOUR, TEAM2_COLOUR, TEAM3_COLOUR, TEAM4_COLOUR,
)

TEAM_COLOURS = (TEAM1_COLOUR, TEAM2_COLOUR, TEAM3_COLOUR, TEAM4_COLOUR)

class GameResults(PlaceholderPage):
    page_title = "Game Results"

    def build_content(self):
        # subtitle to show the winner
        self.winner_label = tk.Label(
            self.content, text="", font=PAGE_TITLE_FONT, bg=BG_COLOUR, fg=FG_COLOUR
        )
        self.winner_label.pack(pady=(0, 20))

        # create frame for the fun facts of the game
        self.facts_frame = tk.Frame(self.content, bg=BG_COLOUR)
        self.facts_frame.pack(fill="x", pady=(0, 20))

        # team roster cards that show the round deltas
        self.teams_frame = tk.Frame(self.content, bg=BG_COLOUR)
        self.teams_frame.pack(fill="x", pady=(0, 20))

        # bottom action button to continue or end game
        self.action_button = tk.Button(
            self.content, text="Continue", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, width=20, height=2, cursor="hand2",
            command=self._on_action,
        )
        self.action_button.pack()
        
    # function to refresh the whole page whenever it is entered
    def on_show(self):
        data = self.controller.shared_data
        self.team_names = data.get("team_names", ())
        self.teams = data.get("teams", {})
        self.player_stats = data.get("player_stats", {})
        self.snapshot = data.get("round_stats_snapshot", {})
        self.game_wins = data.get("game_wins", {})
        self.total_rounds = data.get("num_of_games", 0)
        self.round_winner = data.get("round_winner")

        # round deltas to show how much each player moved this round
        self.round_deltas = {
            name: dict(self.snapshot.get(name, {"positive": 0, "negative": 0}))
            for name in data.get("player_names", [])
        }

        # refresh all of the page elements
        self._refresh_winner_label()
        self._refresh_facts()
        self._refresh_teams()
        self._refresh_action_button()
        
    # function to update the subtitle with the round winner
    def _refresh_winner_label(self):
        idx   = list(self.team_names).index(self.round_winner)
        colour = TEAM_COLOURS[idx] if idx < len(TEAM_COLOURS) else FG_COLOUR
        self.winner_label.config(text=f"{self.round_winner} wins!", fg=colour)
    
    # function to build the fun-fact sentences
    def _refresh_facts(self):
        for widget in self.facts_frame.winfo_children():
            widget.destroy()

        # yo he giving top bru no shot
        top_givers, giver_pts = self._players_with_most("positive")
        top_receivers, receiver_pts = self._players_with_most("negative")

        # display the player(s) that gave out the most points
        if top_givers:
            names = " & ".join(top_givers)
            verb  = "gave out" if len(top_givers) == 1 else "both gave out"
            tk.Label(
                self.facts_frame,
                text=f"{names} {verb} the most points this round with +{giver_pts}",
                font=ROSTER_FONT, bg=BG_COLOUR, fg=POSITIVE_COLOUR,
            ).pack(pady=2)

        # display the player(s) that received the most points
        if top_receivers:
            names = " & ".join(top_receivers)
            verb  = "received" if len(top_receivers) == 1 else "both received"
            tk.Label(
                self.facts_frame,
                text=f"{names} {verb} the most points this round with -{receiver_pts}",
                font=ROSTER_FONT, bg=BG_COLOUR, fg=NEGATIVE_COLOUR,
            ).pack(pady=2)

    # function to find the player with the highest delta for a given stat key
    def _players_with_most(self, key):
        best_value = 0
        for delta in self.round_deltas.values():
            if delta[key] > best_value:
                best_value = delta[key]
        if best_value == 0:
            return [], 0
        names = [n for n, d in self.round_deltas.items() if d[key] == best_value]
        return names, best_value

    # function to build the team roster cards showing this round's deltas
    def _refresh_teams(self):
        for widget in self.teams_frame.winfo_children():
            widget.destroy()

        # reset column weights so old team counts don't bleed over
        for col in range(4):
            self.teams_frame.columnconfigure(col, weight=0)

        # iterate through all of the teams
        for i, team_name in enumerate(self.team_names):
            self.teams_frame.columnconfigure(i, weight=1)
            team_colour = TEAM_COLOURS[i] if i < len(TEAM_COLOURS) else FG_COLOUR

            # wins badge next to the team name
            wins = self.game_wins.get(team_name, 0)
            wins_needed = math.ceil(self.total_rounds / 2)
            header_text = f"{team_name}  ({wins}/{wins_needed})"

            # boc for the player names to be housed
            box = tk.Frame(self.teams_frame, bg=BUTTON_BG_COLOUR)
            box.grid(row=0, column=i, padx=10, sticky="nsew")
            tk.Label(
                box, text=header_text, font=TEAM_HEADER_FONT,
                bg=BUTTON_BG_COLOUR, fg=team_colour
            ).pack(pady=(10, 10))

            # create the team rosters
            roster = tk.Frame(box, bg=BUTTON_BG_COLOUR)
            roster.pack(padx=15, pady=(0, 15), fill="x")
            roster.columnconfigure(0, weight=1)
            roster.columnconfigure(1, weight=0)
            roster.columnconfigure(2, weight=0)

            # iterate through the players of the team and create the name labels along with their points
            for row, player in enumerate(self.teams.get(team_name, [])):
                delta = self.round_deltas.get(player, {"positive": 0, "negative": 0})
                positive = delta["positive"]
                negative = delta["negative"]

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

    # function to decide whether the button says "Continue" or "End Game"
    def _refresh_action_button(self):
        wins_needed = self.controller.shared_data.get("wins_needed") or math.ceil(self.total_rounds / 2)

        # check whether any team has hit the win threshold
        champion = next((t for t in self.team_names if self.game_wins.get(t, 0) >= wins_needed), None)

        # if they have hit the threshold, end the game
        if champion:
            self.action_button.config(text="End Game", fg="#e74c3c", activeforeground="#e74c3c", command=self._on_end_game)
        else:
            self.action_button.config(text="Continue", fg=FG_COLOUR, activeforeground=FG_COLOUR, command=self._on_action)

    # function to continue back to game select for the next round
    def _on_action(self):
        self.controller.show_frame("GameSelect")

    # function to go to the final screen once a winner is crowned
    def _on_end_game(self):
        self.controller.show_frame("GameOver")