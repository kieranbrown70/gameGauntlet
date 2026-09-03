import json
import math
from pathlib import Path
 
import tkinter as tk
 
from pages.base_page import PlaceholderPage
from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR,
    BUTTON_FONT, GOLD_OUTLINE_COLOUR, POSITIVE_COLOUR, NEGATIVE_COLOUR,
    TEAM1_COLOUR, TEAM2_COLOUR, TEAM3_COLOUR, TEAM4_COLOUR,
    TEAM_HEADER_FONT, ROSTER_FONT, RULE_FONT
)

# action types
ACTION_SELF_NEGATIVE = 0
ACTION_NORMAL        = 1 
ACTION_FINISH_DRINK  = 2

FINISH_DRINK_VALUE = 15

TEAM_COLOURS = (TEAM1_COLOUR, TEAM2_COLOUR, TEAM3_COLOUR, TEAM4_COLOUR)

class PlayGame(PlaceholderPage):
    # setup the title to be overwritten and the number of columns for the actions
    page_title = "Game"
    ACTION_COLUMNS = 3
    
    def build_content(self):
        # grab the title label that PlaceholderPage created so we can update it later
        self._title_label = self._find_title_label()
        
        # create the current game label and the action columns
        top = tk.Frame(self.content, bg=BG_COLOUR)
        top.pack(fill="both", expand=True)
        
        # create the area for the actions to populate
        self.actions_frame = tk.Frame(top, bg=BG_COLOUR)
        self.actions_frame.pack(fill="both", expand=True)
 
        # create player stats frame sitting below the action buttons
        self.teams_frame = tk.Frame(top, bg=BG_COLOUR)
        self.teams_frame.pack(fill="x", pady=(10, 0))
 
        # create the row for the point assignment and to end the game
        bottom = tk.Frame(self.content, bg=BG_COLOUR)
        bottom.pack(fill="x", pady=(10, 0))
 
        # assignment row that is hidden until an action is selected
        self.assignment_row = tk.Frame(bottom, bg=BG_COLOUR)
        self.assignment_row.pack(pady=(0, 10))
 
        # dropdown for the player who has done the action
        done_by_frame = tk.Frame(self.assignment_row, bg=BG_COLOUR)
        done_by_frame.pack(side="left", padx=(0, 20))
        tk.Label(done_by_frame, text="Done by:", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(anchor="w")
        self.done_by_var = tk.StringVar(value="Name")
        self.done_by_menu = tk.OptionMenu(done_by_frame, self.done_by_var, "Name")
        self._style_menu(self.done_by_menu)
        self.done_by_menu.pack()
 
        # dropdown for the player to give the enemy points to (this is hidden when the action is 0)
        self.given_to_frame = tk.Frame(self.assignment_row, bg=BG_COLOUR)
        self.given_to_frame.pack(side="left", padx=(0, 20))
        tk.Label(self.given_to_frame, text="Given to:", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(anchor="w")
        self.given_to_var = tk.StringVar(value="Name")
        self.given_to_menu = tk.OptionMenu(self.given_to_frame, self.given_to_var, "Name")
        self._style_menu(self.given_to_menu)
        self.given_to_menu.pack()
 
        # confirmation button to give the points to a player
        self.give_point_button = tk.Button(
            self.assignment_row, text="Give Point", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, height=2, padx=16, cursor="hand2",
            command=self._on_give_point,
        )
        self.give_point_button.pack(side="left", padx=(0, 20))
 
        # hide the assignment row until something is selected
        self.assignment_row.pack_forget()
        
        # indicator for the selected action
        self.selected_label = tk.Label(bottom, text="", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR)
        self.selected_label.pack(pady=(0, 6))
 
        # button to end the game
        self.end_game_button = tk.Button(
            bottom, text="End Game", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg="#e74c3c",
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground="#e74c3c",
            relief="flat", bd=0, width=20, height=2, cursor="hand2",
            command=self._on_end_game,
        )
        self.end_game_button.pack(pady=(0, 4))
 
        # winner selection row — revealed only when the end game button is clicked
        self.winner_row = tk.Frame(bottom, bg=BG_COLOUR)

        # create the frame for the winner selection
        winner_label_frame = tk.Frame(self.winner_row, bg=BG_COLOUR)
        winner_label_frame.pack(side="left", padx=(0, 20))
        tk.Label(winner_label_frame, text="Who won?", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(anchor="w")
        self.winner_var = tk.StringVar(value="Select...")
        self.winner_menu = tk.OptionMenu(winner_label_frame, self.winner_var, "Select...")
        self._style_menu(self.winner_menu)
        self.winner_menu.pack()

        # create a button to confirm the winner
        self.confirm_winner_button = tk.Button(
            self.winner_row, text="Confirm", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, height=2, padx=16, cursor="hand2",
            command=self._on_confirm_winner,
        )
        self.confirm_winner_button.pack(side="left")
 
        # internal state
        self._selected_action = None
        self._action_buttons  = []
    
    # function to keep up the lifecycle of the game
    def on_show(self):
        data = self.controller.shared_data
 
        # update the page title to the current game name
        current_game = data.get("current_game", {})
        game_name = current_game.get("name", "Game") if isinstance(current_game, dict) else "Game"
        if self._title_label:
            self._title_label.config(text=game_name)
 
        # pull player/team names for the dropdowns and for the stats
        self.player_names = data.get("player_names", [])
        self.team_names = data.get("team_names", ())
        self.teams = data.get("teams", {})
        self.game_wins = data.get("game_wins", {})
        self.wins_needed = data.get("wins_needed") or math.ceil(len(data.get("draft_pool", [])) / 2)
        
        # populate the winner dropdown with the current team names
        self._rebuild_team_dropdown(
            self.winner_menu,
            self.winner_var,
            self.team_names
        )
        
        # initialise player_stats if this is the first time through
        if "player_stats" not in data:
            data["player_stats"] = {}
        for name in self.player_names:
            if name not in data["player_stats"] or not isinstance(data["player_stats"][name], dict):
                data["player_stats"][name] = {"positive": 0, "negative": 0}
 
        # track only this round's activity by starting at 0
        self._round_stats = {name: {"positive": 0, "negative": 0} for name in self.player_names}
 
        # load the rules for this game
        self._rules = self._load_rules(game_name)
 
        # reset selection state
        self._selected_action = None
        self.assignment_row.pack_forget()
        self.winner_row.pack_forget()
        self.selected_label.config(text="")
 
        # rebuild the action columns and the team stats
        self._build_action_columns()
        self._refresh_roster()

        # remove any traces from a previous visit before adding a fresh one
        for trace_id in self.done_by_var.trace_info():
            self.done_by_var.trace_remove(trace_id[0], trace_id[1])
 
        # create a quick lookup to determine who is on which team
        self._team_lookup = {
            player: team_name
            for team_name, players in self.teams.items()
            for player in players
        }

        # populate the done by field with everyone then update given to
        self._rebuild_dropdown(self.done_by_menu, self.done_by_var, self.player_names)
        self.done_by_var.trace_add("write", self._on_done_by_change)
    
    # function to build the columns to house the various actions
    def _build_action_columns(self):
        # reset the current columns to be rebuilt
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
        self._action_buttons = []
 
        # if there are no rules found let the user know
        if not self._rules:
            tk.Label(self.actions_frame, text="No rules found for this game.",font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(pady=40)
            return
 
        # distribute rules as evenly as possible across the columns
        num_cols = self.ACTION_COLUMNS
        total = len(self._rules)
        base, rem = divmod(total, num_cols)
        # first remainder columns get one extra rule
        col_sizes  = [base + (1 if i < rem else 0) for i in range(num_cols)]
 
        # iterate through the columns and create frames for each of the actions
        rule_iter = iter(self._rules)
        for col_idx, size in enumerate(col_sizes):
            self.actions_frame.columnconfigure(col_idx, weight=1)
            col_frame = tk.Frame(self.actions_frame, bg=BG_COLOUR)
            col_frame.grid(row=0, column=col_idx, sticky="n", padx=10, pady=(0, 10))
 
            for _ in range(size):
                try:
                    rule = next(rule_iter)
                except StopIteration:
                    break
                self._make_action_button(col_frame, rule)
    
    # function to make the action buttons that populate the column's we have made
    def _make_action_button(self, parent, rule):
        # assign values from the rule given from the JSON
        name, value, action_type = rule
 
        border_colour = {
            ACTION_SELF_NEGATIVE: NEGATIVE_COLOUR,
            ACTION_NORMAL:        POSITIVE_COLOUR,
            ACTION_FINISH_DRINK:  GOLD_OUTLINE_COLOUR,
        }.get(action_type, BG_COLOUR)
  
        # wrapper provides the correct colour border for the actions
        wrapper = tk.Frame(parent, bg=border_colour, padx=2, pady=2)
        wrapper.pack(fill="x", pady=3)
 
        # build the button label which includes sip count and a marker for finish-drink
        if action_type == ACTION_FINISH_DRINK:
            display = f"{name}  [{value} ★]"
        else:
            display = f"{name}  [{value}]"
 
        # create the button itself
        btn = tk.Button(
            wrapper, text=display, font=RULE_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, anchor="w", padx=10, pady=6,
            cursor="hand2", wraplength=300,
            command=lambda r=rule, b=None, w=wrapper: self._on_action_select(r, btn, w),
        )
        # fix the forward-reference: re-assign command with the real btn object
        btn.config(command=lambda r=rule, b=btn, w=wrapper: self._on_action_select(r, b, w))
        btn.pack(fill="x")
 
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BUTTON_HOVER_BG_COLOUR))
        btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BUTTON_BG_COLOUR))
 
        self._action_buttons.append((btn, wrapper))
    
    # function to run when an action is clicked
    def _on_action_select(self, rule, clicked_btn, clicked_wrapper):
        name, value, action_type = rule
        self._selected_action = rule
 
        # update the selected label
        if action_type == ACTION_FINISH_DRINK:
            desc = f"Selected: {name}  (Finish your drink +{FINISH_DRINK_VALUE} / -{FINISH_DRINK_VALUE})"
        elif action_type == ACTION_NORMAL:
            desc = f"Selected: {name}  (+{value} / -{value})"
        else:
            desc = f"Selected: {name}  (-{value})"
        self.selected_label.config(text=desc)
 
        # highlight the clicked button, reset all others
        for btn, wrapper in self._action_buttons:
            is_positive = btn == clicked_btn
            pass
 
        # dim all and highlight selected
        self._highlight_selected(clicked_btn)
 
        # show or hide "Given to:" based on action type
        if action_type == ACTION_SELF_NEGATIVE:
            self.given_to_frame.pack_forget()
        else:
            if not self.given_to_frame.winfo_ismapped():
                self.given_to_frame.pack(side="left", padx=(0, 20), before=self.give_point_button)
 
        # make the assignment row visible
        if not self.assignment_row.winfo_ismapped():
            self.assignment_row.pack(pady=(0, 10), before=self.selected_label)
    
    # function to dim the rest of the action buttons when one is selected
    def _highlight_selected(self, selected_btn):
        for btn, wrapper in self._action_buttons:
            if btn is selected_btn:
                btn.config(bg=BUTTON_HOVER_BG_COLOUR)
            else:
                btn.config(bg=BUTTON_BG_COLOUR)
 
    # function to activate when points are given out
    def _on_give_point(self):
        if self._selected_action is None:
            return
 
        name, value, action_type = self._selected_action
        doer = self.done_by_var.get()
        receiver = self.given_to_var.get()
 
        stats = self._round_stats
 
        # make sure doer is a real player
        if doer not in stats:
            return
 
        # doer only gets negative points
        if action_type == ACTION_SELF_NEGATIVE:
            stats[doer]["negative"] += value
 
        # doer gains positive, receiver gains negative
        elif action_type == ACTION_NORMAL:
            stats[doer]["positive"] += value
            if receiver in stats and receiver != doer:
                stats[receiver]["negative"] += value
 
        # doer gains the positive finish drink value, receiver gains the negative
        elif action_type == ACTION_FINISH_DRINK:
            stats[doer]["positive"] += FINISH_DRINK_VALUE
            if receiver in stats and receiver != doer:
                stats[receiver]["negative"] += FINISH_DRINK_VALUE
 
        # reset selection after giving points
        self._selected_action = None
        self.selected_label.config(text=f"✓ Point given for: {name}")
        self.assignment_row.pack_forget()
        self._clear_button_highlights()
        self._refresh_roster()
 
    # function to remove the highlight on a button
    def _clear_button_highlights(self):
        for btn, wrapper in self._action_buttons:
            btn.config(bg=BUTTON_BG_COLOUR)
 
    # function to update given_to with only opponents of the selected done by player
    def _on_done_by_change(self, *_):
        doer = self.done_by_var.get()
        doer_team = self._team_lookup.get(doer)

        # checking which players to add to the dropdown
        if doer_team:
            opponents = [p for p in self.player_names if self._team_lookup.get(p) != doer_team]
        else:
            opponents = [p for p in self.player_names if p != doer]

        self._rebuild_dropdown(self.given_to_menu, self.given_to_var, opponents)
 
    # function to redraw the team roster section with current point totals
    def _refresh_roster(self):
        for widget in self.teams_frame.winfo_children():
            widget.destroy()

        # reset any existing column weights
        for col in range(4):
            self.teams_frame.columnconfigure(col, weight=0)

        stats = self._round_stats

        # iterate through all of the teams
        for i, team_name in enumerate(self.team_names):
            # prepare formatting based on the team selected
            self.teams_frame.columnconfigure(i, weight=1)
            team_colour = TEAM_COLOURS[i] if i < len(TEAM_COLOURS) else FG_COLOUR

            wins = self.game_wins.get(team_name, 0)
            header_text = f"{team_name}  ({wins}/{self.wins_needed})"

            # create the frame for the team name
            box = tk.Frame(self.teams_frame, bg=BUTTON_BG_COLOUR)
            box.grid(row=0, column=i, padx=10, sticky="nsew")
            tk.Label(box, text=header_text, font=TEAM_HEADER_FONT, bg=BUTTON_BG_COLOUR, fg=team_colour).pack(pady=(8, 8))

            # populate the player names below the team name
            roster = tk.Frame(box, bg=BUTTON_BG_COLOUR)
            roster.pack(padx=15, pady=(0, 12), fill="x")
            roster.columnconfigure(0, weight=1)
            roster.columnconfigure(1, weight=0)
            roster.columnconfigure(2, weight=0)

            # iterate through the players on the team and display their points
            for row, player in enumerate(self.teams.get(team_name, [])):
                player_stats = stats.get(player, {"positive": 0, "negative": 0})
                positive = player_stats.get("positive", 0)
                negative = player_stats.get("negative", 0)

                tk.Label(roster, text=player, font=ROSTER_FONT, bg=BUTTON_BG_COLOUR, fg=FG_COLOUR, anchor="w").grid(
                    row=row, column=0, sticky="ew", pady=2)
                tk.Label(roster, text=f"+{positive}", font=ROSTER_FONT, bg=BUTTON_BG_COLOUR, fg=POSITIVE_COLOUR, anchor="e").grid(
                    row=row, column=1, sticky="e", padx=(10, 0), pady=2)
                tk.Label(roster, text=f"-{negative}", font=ROSTER_FONT, bg=BUTTON_BG_COLOUR, fg=NEGATIVE_COLOUR, anchor="e").grid(
                    row=row, column=2, sticky="e", padx=(6, 0), pady=2)
 
    # function to load all of the rules from the JSON file
    def _load_rules(self, game_name):
        path = Path(__file__).resolve().parent.parent.parent / "data" / "games.json"
        try:
            with open(path, "r") as f:
                all_games = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
        for game in all_games:
            if game.get("name") == game_name:
                return game.get("rules", [])
        return []
    
    # function to make it look sexc
    def _style_menu(self, menu):
        menu.config(
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, highlightthickness=0, cursor="hand2")
        menu["menu"].config(bg=BUTTON_BG_COLOUR, fg=FG_COLOUR)
    
    # function to teplace the options in a tk.OptionMenu with a fresh list
    def _rebuild_dropdown(self, menu, var, names):
        dropdown = menu["menu"]
        dropdown.delete(0, "end")
        for name in names:
            dropdown.add_command(label=name, command=lambda v=name: var.set(v))
        var.set(names[0] if names else "Name")
    
    # function to walk the widget tree to find the title label
    def _find_title_label(self):
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Label):
                        return grandchild
        return None
 
    # function to reveal the winner selection row when the end game button is clicked
    def _on_end_game(self):
        if not self.winner_row.winfo_ismapped():
            self.winner_row.pack(pady=(8, 0))

    # function to record the chosen winner and navigate to the next page
    def _on_confirm_winner(self):
        winner = self.winner_var.get()
        team_names = self.controller.shared_data.get("team_names", ())
        if winner not in team_names:
            return

        data = self.controller.shared_data

        # capture the round stats for game results page to display
        data["round_stats_snapshot"] = self._round_stats

        # flush round stats into the cumulative totals
        cumulative = data.setdefault("player_stats", {})
        for name, delta in self._round_stats.items():
            if name not in cumulative or not isinstance(cumulative[name], dict):
                cumulative[name] = {"positive": 0, "negative": 0}
            cumulative[name]["positive"] += delta["positive"]
            cumulative[name]["negative"] += delta["negative"]

        data["round_winner"] = winner

        # update the per-team game-win counter
        game_wins = data.setdefault("game_wins", {t: 0 for t in team_names})
        game_wins[winner] = game_wins.get(winner, 0) + 1

        # append this result to the running round log for game over to display
        game_name = data.get("current_game", {}).get("name", "Unknown")
        data.setdefault("round_results", []).append({"game": game_name, "winner": winner})

        self.controller.show_frame("GameResults")

    # function to populate a team-name dropdown
    def _rebuild_team_dropdown(self, menu, var, team_names):
        dropdown = menu["menu"]
        dropdown.delete(0, "end")
        for name in team_names:
            dropdown.add_command(label=name, command=lambda v=name: var.set(v))
        var.set(team_names[0] if team_names else "Select...")
    