import json
import random
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from pages.base_page import PlaceholderPage
from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR, BUTTON_FONT, GAME_CARD_FONT, ROSTER_FONT,
    TEAM1_COLOUR, TEAM1_HIGHLIGHT_COLOUR, TEAM2_COLOUR, TEAM2_HIGHLIGHT_COLOUR,
    TEAM3_COLOUR, TEAM3_HIGHLIGHT_COLOUR, TEAM4_COLOUR, TEAM4_HIGHLIGHT_COLOUR
)

TEAM_COLOURS = (TEAM1_COLOUR, TEAM2_COLOUR, TEAM3_COLOUR, TEAM4_COLOUR)
TEAM_HIGHLIGHT_COLOURS = (TEAM1_HIGHLIGHT_COLOUR, TEAM2_HIGHLIGHT_COLOUR, TEAM3_HIGHLIGHT_COLOUR, TEAM4_HIGHLIGHT_COLOUR)

class NewGameDraft(PlaceholderPage):
    page_title = "Game Draft"
    
    GRID_COLUMNS = 6
    CARD_IMAGE_SIZE = (100, 100)
    TRAY_IMAGE_SIZE = (50, 50)
    TRAY_TEXT_WRAP = 120
    IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "images"
    
    def build_content(self):
        # create a label to indicate which team is drafting
        self.turn_label = tk.Label(self.content, text="", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR)

        # create a row of coloured team name labels to show the full draft order
        self.order_row = tk.Frame(self.content, bg=BG_COLOUR)
        
        # setup the grid container to hold the available games
        self.grid_container = tk.Frame(self.content, bg=BG_COLOUR)
        self.grid_container.pack(fill="both", expand=True, pady=(0,20))
        
        # create a canvas and scrollbar to make the grid scrollable
        self.grid_canvas = tk.Canvas(self.grid_container, bg=BG_COLOUR, highlightthickness=0)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Vertical.TScrollbar", background=BUTTON_BG_COLOUR, troughcolor=BG_COLOUR,
            bordercolor=BG_COLOUR, arrowcolor=FG_COLOUR, lightcolor=BUTTON_BG_COLOUR, darkcolor=BUTTON_BG_COLOUR,
        )

        scrollbar = ttk.Scrollbar(
            self.grid_container, orient="vertical", command=self.grid_canvas.yview,
            style="Custom.Vertical.TScrollbar",
        )
        self.grid_canvas.configure(yscrollcommand=scrollbar.set)

        self.grid_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # create a frame inside the canvas to hold the game cards
        self.games_grid_frame = tk.Frame(self.grid_canvas, bg=BG_COLOUR)
        self.grid_window = self.grid_canvas.create_window((0, 0), window=self.games_grid_frame, anchor="nw")

        # keep the scrollable region in sync with the frame's actual content size
        self.games_grid_frame.bind("<Configure>", lambda e: self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox("all")))
        
        # keep the inner frame's width matched to the canvas so cards wrap correctly
        self.grid_canvas.bind("<Configure>", lambda e: self.grid_canvas.itemconfig(self.grid_window, width=e.width))

        # mouse wheel only scrolls this canvas while the cursor is over it
        self.grid_canvas.bind("<Enter>", lambda e: self.grid_canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.grid_canvas.bind("<Leave>", lambda e: self.grid_canvas.unbind_all("<MouseWheel>"))
            
        # label and create the bottom frame to hold the selected games
        tk.Label(self.content, text="Selected Games:", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR).pack(anchor="w")
        self.selected_games_frame = tk.Frame(self.content, bg=BUTTON_BG_COLOUR, height=130)
        self.selected_games_frame.pack(fill="x", pady=(5, 20))
        self.selected_games_frame.pack_propagate(False)
        
        # create the start button to move to begin the game
        self.start_button = tk.Button(
            self.content, text="Start Game", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, width=20, height=2, cursor="hand2",
            state="disabled", command=self._on_start,
        )
        self.start_button.pack()
        
    # function to reload the games every time the page is entered
    def on_show(self):
        self.num_games_needed = self.controller.shared_data.get("num_of_games", 3)
        self.games = self._load_games()
        
        self.picked = []
        self._image_cache = {}
        
        # determine whether it is a neutral draft or not
        self.neutral_draft = self.controller.shared_data.get("neutral_draft", True)
        self.team_names = self.controller.shared_data.get("team_names", ("Team 1", "Team 2"))
 
        if not self.neutral_draft:
            num_teams = len(self.team_names)

            # randomize the draft order
            self.draft_order = list(range(num_teams))
            random.shuffle(self.draft_order)

            # distribute all the picks for the draft leaving the leftovers for the earlier teams
            base, rem = divmod(self.num_games_needed, num_teams)
            self.team_quota = [0] * num_teams
            for i, team_idx in enumerate(self.draft_order):
                self.team_quota[team_idx] = base + (1 if i < rem else 0)
            self.team_picks = [[] for _ in range(num_teams)]

            # the team that picks last in the draft gets first choice when playing
            self.controller.shared_data["choosing_team"] = self.draft_order[-1]

            # index the current position of the draft
            self.draft_pos = 0
            self.current_team = self.draft_order[self.draft_pos]
            self.turn_label.pack(fill="x", pady=(0, 10), before=self.grid_container)
            self.order_row.pack(pady=(0, 10), before=self.grid_container)
            self._update_turn_label()
            self._update_order_row()
        else:
            self.turn_label.pack_forget()
            self.order_row.pack_forget()
        
        self._refresh_grid()
        self._refresh_selected_games()
    
    # function to handle mouse wheel scrolling for the canvas    
    def _on_mousewheel(self, event):
        self.grid_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # function to load the games from the JSON file and handle errors
    def _load_games(self):
        path = Path(__file__).resolve().parent.parent.parent / "data" / "games.json"
        try:
            with open(path, "r") as f:
                games = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._show_load_error(f"Error loading games from {path}. Please ensure the file exists and is valid JSON.")
            return []
        
        # check if the loaded data is a list and not empty
        if not isinstance(games, list) or not games:
            self._show_load_error(f"No games found in {path}. Please ensure the file contains a list of games.")
            return []
        
        games.sort(key=lambda g: g.get("name", "").lower())
        
        return games
    
    # function to load images from the cache or disk
    def _load_image(self, image_path, size):
        if not image_path:
            return None
        
        # check if the image is already cached
        cache_key = (image_path, size)
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
        
        full_image_path = self.IMAGES_DIR / image_path
        if not full_image_path.exists():
            return None
        
        # otherwise load the image from disk and cache it
        try:
            image = Image.open(full_image_path).resize(size)
            photo = ImageTk.PhotoImage(image)
            self._image_cache[cache_key] = photo
            return photo
        except (FileNotFoundError, OSError) as e:
            return None
    
    # function to create a card for each game in the grid
    def _make_card(self, parent, game, size, on_click, wraplength=None):
        if wraplength is None:
            wraplength = size[0]
        
        # create a frame for the card and load the image
        card = tk.Frame(parent, bg=BUTTON_BG_COLOUR, cursor="hand2")
        photo = self._load_image(game.get("image"), size)
        if photo:
            img_label = tk.Label(card, image=photo, bg=BUTTON_BG_COLOUR)
            img_label.image = photo
        else:
            img_label = tk.Label(card, text="No\nImage", width=size[0] // 8, height=size[1] // 16, bg=BUTTON_HOVER_BG_COLOUR, 
                                 fg=FG_COLOUR, font=GAME_CARD_FONT)
        img_label.pack(padx=5, pady=(0, 5))
        
        # create a label for the game name and bind the click event to the card
        name_label = tk.Label(card, text=game["name"], font=GAME_CARD_FONT, bg=BUTTON_BG_COLOUR, fg=FG_COLOUR, wraplength=wraplength)
        name_label.pack(padx=5, pady=(0, 5))
        
        for widget in (card, img_label, name_label):
            widget.bind("<Button-1>", lambda e: on_click(game))
        
        return card
    
    # function to refresh the grid of available games
    def _refresh_grid(self):
        # reset the current grid of games
        for widget in self.games_grid_frame.winfo_children():
            widget.destroy()
        
        # filter out the games that have already been picked
        picked_games = {g["name"] for g in self.picked}
        available_games = [g for g in self.games if g["name"] not in picked_games]
        
        # display all the available games remaining in the grid
        for i, game in enumerate(available_games):
            row, col = divmod(i, self.GRID_COLUMNS)
            self.games_grid_frame.columnconfigure(col, weight=1)
            card = self._make_card(self.games_grid_frame, game, self.CARD_IMAGE_SIZE, self._pick_game)
            card.grid(row=row, column=col, padx=10, pady=10)
    
    # function to refresh the bottom row of selected games    
    def _refresh_selected_games(self):
        # reset the current tray of selected games
        for widget in self.selected_games_frame.winfo_children():
            widget.destroy()
        
        # display all the selected games in the tray
        for i, game in enumerate(self.picked):
            team_index = self._team_index_for_game(game)
            
            # create the game card normally if it's a neutral draft
            if team_index is None:
                card = self._make_card(self.selected_games_frame, game, self.TRAY_IMAGE_SIZE, self._unpick_game, wraplength=self.TRAY_TEXT_WRAP)
                card.grid(row=0, column=i, padx=8, pady=8)
            # otherwise, add a highlight to the game card for either team
            else:
                highlight_colour = TEAM_HIGHLIGHT_COLOURS[team_index] if team_index < len(TEAM_HIGHLIGHT_COLOURS) else BUTTON_BG_COLOUR
                wrapper = tk.Frame(self.selected_games_frame, bg=highlight_colour)
                card = self._make_card(wrapper, game, self.TRAY_IMAGE_SIZE, self._unpick_game, wraplength=self.TRAY_TEXT_WRAP)
                card.pack(padx=4, pady=4)
                wrapper.grid(row=0, column=i, padx=8, pady=8)
                
            
        self.start_button.config(state="normal" if len(self.picked) >= self.num_games_needed else "disabled")
        
    # function to build the display text of the drafting team
    def _update_turn_label(self):
        if self.neutral_draft:
            return
 
        # check if every team has hit their quota
        if all(len(self.team_picks[i]) >= self.team_quota[i] for i in range(len(self.team_names))):
            self.turn_label.config(text="Draft complete", fg=FG_COLOUR)
            return
 
        # update the display of the drafting team
        team_name = self.team_names[self.current_team]
        team_colour = TEAM_COLOURS[self.current_team] if self.current_team < len(TEAM_COLOURS) else FG_COLOUR
        if len(self.team_picks[self.current_team]) >= self.team_quota[self.current_team]:
            self.turn_label.config(text=f"{team_name}'s draft is full", fg=team_colour)
        else:
            self.turn_label.config(text=f"{team_name} is picking...", fg=team_colour)

     # function to rebuild the coloured draft order indicator
    def _update_order_row(self):
        for widget in self.order_row.winfo_children():
            widget.destroy()

        # iterate through each of the teams to the draft order status
        for pos, team_idx in enumerate(self.draft_order):
            team_name = self.team_names[team_idx]
            team_colour = TEAM_COLOURS[team_idx] if team_idx < len(TEAM_COLOURS) else FG_COLOUR

            # dim the colour if the team is done drafting
            is_done = len(self.team_picks[team_idx]) >= self.team_quota[team_idx]
            label_colour = BUTTON_BG_COLOUR if is_done else team_colour

            tk.Label(
                self.order_row, text=team_name, font=ROSTER_FONT,
                bg=BG_COLOUR, fg=label_colour,
            ).pack(side="left")

            # add an arrow between entries but not after the last one
            if pos < len(self.draft_order) - 1:
                tk.Label(
                    self.order_row, text="  →  ", font=ROSTER_FONT,
                    bg=BG_COLOUR, fg=FG_COLOUR,
                ).pack(side="left")
 
    # function to find which team picked a given game
    def _team_index_for_game(self, game):
        if self.neutral_draft:
            return None
        for team_index, team_picks in enumerate(self.team_picks):
            if game in team_picks:
                return team_index
        return None
 
    # function to move to the next team's turn
    def _advance_turn(self):
        num_teams = len(self.team_names)
        # step forward through the draft order
        for step in range(1, num_teams + 1):
            self.draft_pos = (self.draft_pos + 1) % num_teams
            candidate = self.draft_order[self.draft_pos]
            if len(self.team_picks[candidate]) < self.team_quota[candidate]:
                self.current_team = candidate
                return
        
    # function to pick the game and assign it to the bottom tray
    def _pick_game(self, game):
        if len(self.picked) >= self.num_games_needed:
            return
        
        # add the game 
        if not self.neutral_draft:
            team = self.current_team
            if len(self.team_picks[team]) >= self.team_quota[team]:
                return
            self.team_picks[team].append(game)
        
        self.picked.append(game)
        self._refresh_grid()
        self._refresh_selected_games()
    
        if not self.neutral_draft:
            self._advance_turn()
            self._update_turn_label()
            self._update_order_row()
    
    # function to remove the game from the bottom row
    def _unpick_game(self, game):
        self.picked.remove(game)
        
        if not self.neutral_draft:
            # find which team owned this pick, restore it and rewind the draft position to match
            for team_index, team_picks in enumerate(self.team_picks):
                if game in team_picks:
                    team_picks.remove(game)
                    self.current_team = team_index
                    # rewind the draft position so it points back to the correct team
                    self.draft_pos = self.draft_order.index(team_index)
                    break
            self._update_turn_label()
            self._update_order_row()
        
        self._refresh_grid()
        self._refresh_selected_games()
    
    # function to display an error message in the grid if loading fails
    def _show_load_error(self, message):
        tk.Label(self.games_grid_frame, text=message, font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR, wraplength=500).pack(pady=40)
    
    def _on_start(self):
        self.controller.shared_data["draft_pool"] = self.picked
        self.controller.show_frame("GameSelect")