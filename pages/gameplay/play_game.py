import json
from pathlib import Path
 
import tkinter as tk
 
from pages.base_page import PlaceholderPage
from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR,
    BUTTON_FONT, PAGE_TITLE_FONT, GOLD_OUTLINE_COLOUR,
)
 
# action types
ACTION_SELF_NEGATIVE = 0
ACTION_NORMAL        = 1 
ACTION_FINISH_DRINK  = 2

FINISH_DRINK_VALUE = 15

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
        
        # create the are for the actions to populate
        self.actions_frame = tk.Frame(top, bg=BG_COLOUR)
        self.actions_frame.pack(fill="both", expand=True)
 
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
 
        # pull player names for the dropdowns
        self.player_names = data.get("player_names", [])
 
        # initialise player_stats if this is the first time through
        if "player_stats" not in data:
            data["player_stats"] = {}
        for name in self.player_names:
            if name not in data["player_stats"] or not isinstance(data["player_stats"][name], dict):
                data["player_stats"][name] = {"positive": 0, "negative": 0}
 
        # load the rules for this game
        self._rules = self._load_rules(game_name)
 
        # reset selection state
        self._selected_action = None
        self.assignment_row.pack_forget()
        self.selected_label.config(text="")
 
        # rebuild the action columns
        self._build_action_columns()
 
        # populate the dropdowns
        self._rebuild_dropdown(self.done_by_menu,  self.done_by_var,  self.player_names)
        self._rebuild_dropdown(self.given_to_menu, self.given_to_var, self.player_names)
    
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
 
        is_positive = action_type in (ACTION_NORMAL, ACTION_FINISH_DRINK)
 
        # wrapper provides the gold border for positive actions
        if is_positive:
            wrapper = tk.Frame(parent, bg=GOLD_OUTLINE_COLOUR, padx=2, pady=2)
        else:
            wrapper = tk.Frame(parent, bg=BG_COLOUR, padx=2, pady=2)
        wrapper.pack(fill="x", pady=3)
 
        # build the button label which includes sip count and a marker for finish-drink
        if action_type == ACTION_FINISH_DRINK:
            display = f"{name}  [{value} ★]"
        else:
            display = f"{name}  [{value}]"
 
        # create the button itself
        btn = tk.Button(
            wrapper, text=display, font=BUTTON_FONT,
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
 
        data = self.controller.shared_data
        stats = data["player_stats"]
 
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
 
    # function to remove the highlight on a button
    def _clear_button_highlights(self):
        for btn, wrapper in self._action_buttons:
            btn.config(bg=BUTTON_BG_COLOUR)
 
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
 
    # function to end the current game and to go to a stats screen
    # TODO: Implement this shi
    def _on_end_game(self):
        self.controller.show_frame("StatScreen")
    