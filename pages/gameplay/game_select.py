import math
from pathlib import Path

import tkinter as tk
from PIL import Image, ImageTk

from pages.base_page import PlaceholderPage
from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR, BUTTON_FONT, GAME_CARD_FONT,
    TEAM1_COLOUR, TEAM1_HIGHLIGHT_COLOUR, TEAM2_COLOUR, TEAM2_HIGHLIGHT_COLOUR,
    TEAM3_COLOUR, TEAM3_HIGHLIGHT_COLOUR, TEAM4_COLOUR, TEAM4_HIGHLIGHT_COLOUR,
    POSITIVE_COLOUR, NEGATIVE_COLOUR, TEAM_HEADER_FONT, ROSTER_FONT,
)

TEAM_COLOURS           = (TEAM1_COLOUR, TEAM2_COLOUR, TEAM3_COLOUR, TEAM4_COLOUR)
TEAM_HIGHLIGHT_COLOURS = (TEAM1_HIGHLIGHT_COLOUR, TEAM2_HIGHLIGHT_COLOUR, TEAM3_HIGHLIGHT_COLOUR, TEAM4_HIGHLIGHT_COLOUR)

class GameSelect(PlaceholderPage):
    page_title = "Game Selection"
    
    GRID_COLUMNS = 6
    CARD_IMAGE_SIZE = (100, 100)
    IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "images"
    
    def build_content(self):
        # create a label for the round number and who's turn it is
        self.turn_label = tk.Label(self.content, text="", font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR)
        self.turn_label.pack(pady=(0, 10))
        
        # create the container for the games to choose for the next round
        self.grid_container = tk.Frame(self.content, bg=BG_COLOUR, height=230)
        self.grid_container.pack(fill="x", pady=(0, 20))
        self.grid_container.pack_propagate(False)
 
        # create the canvas for the grid of games
        self.grid_canvas = tk.Canvas(self.grid_container, bg=BG_COLOUR, highlightthickness=0)
        self.grid_canvas.pack(fill="both", expand=True)
        
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
        
        # side by side boxes showing each team's roster and their current stats
        self.teams_frame = tk.Frame(self.content, bg=BG_COLOUR)
        self.teams_frame.pack(fill="x", pady=(0, 20))
        
        # box to confirm the game that was chosen
        self.confirm_button = tk.Button(
            self.content, text="Confirm Selection", font=BUTTON_FONT,
            bg=BUTTON_BG_COLOUR, fg=FG_COLOUR,
            activebackground=BUTTON_HOVER_BG_COLOUR, activeforeground=FG_COLOUR,
            relief="flat", bd=0, width=20, height=2, cursor="hand2",
            state="disabled", command=self._on_confirm,
        )
        self.confirm_button.pack()
        
    # function to reload the interface whenever the page is reopened
    def on_show(self):
        data = self.controller.shared_data
        self.draft_pool = data.get("draft_pool", [])
        self.team_names = data.get("team_names", ("Team 1", "Team 2"))
        self.teams = data.get("teams", {})

        # first time through, set up the round tracking and everyone's stats
        data.setdefault("games_played", [])
        data.setdefault("choosing_team", 0)

        # make sure every player has a proper positive and negative entry
        player_stats = data.setdefault("player_stats", {})
        for name in data.get("player_names", []):
            if not isinstance(player_stats.get(name), dict):
                player_stats[name] = {"positive": 0, "negative": 0}

        self.games_played = data["games_played"]
        self.current_team = data["choosing_team"]
        self.player_stats = data["player_stats"]
        self.game_wins = data.get("game_wins", {})
        self.total_rounds = data.get("num_of_games", len(self.draft_pool))
        self.wins_needed = data.get("wins_needed") or math.ceil(self.total_rounds / 2)

        self._image_cache = {}
        self.selected_game = None
        self.selected_widgets = None
        self.confirm_button.config(state="disabled")

        self._refresh_teams()

        # if every round has already been drafted, show a wrap up state instead of the grid
        if len(self.games_played) >= self.total_rounds:
            self._show_complete()
            return

        self._refresh_grid()
        self._update_turn_label()
        
    # function to handle mouse wheel scrolling for the canvas    
    def _on_mousewheel(self, event):
        self.grid_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
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
        except (FileNotFoundError, OSError):
            return None
    
    # function to create a card for each game in the grid 
    def _make_card(self, parent, game):
        # create a frame for the card and load the image
        size = self.CARD_IMAGE_SIZE
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
        name_label = tk.Label(card, text=game["name"], font=GAME_CARD_FONT, bg=BUTTON_BG_COLOUR, fg=FG_COLOUR, wraplength=size[0])
        name_label.pack(padx=5, pady=(0, 5))
 
        widgets = (card, img_label, name_label)
        for widget in widgets:
            widget.bind("<Button-1>", lambda e: self._select_game(game, widgets))
 
        return card
    
    # function to refresh the grid of games still left to choose from
    def _refresh_grid(self):
        # reset the current grid of games
        for widget in self.games_grid_frame.winfo_children():
            widget.destroy()

        # filter out the games that have already been played
        played_names = {g["name"] for g in self.games_played}
        self.available_games = [g for g in self.draft_pool if g["name"] not in played_names]

        # display all the unplayed games in the grid
        for i, game in enumerate(self.available_games):
            row, col = divmod(i, self.GRID_COLUMNS)
            self.games_grid_frame.columnconfigure(col, weight=1)
            card = self._make_card(self.games_grid_frame, game)
            card.grid(row=row, column=col, padx=10, pady=10)
            
    # function to highlight the chosen game and enable the confirm button
    def _select_game(self, game, widgets):
        team_index = self.current_team if self.current_team < len(TEAM_HIGHLIGHT_COLOURS) else 0
        highlight = TEAM_HIGHLIGHT_COLOURS[team_index]
 
        # revert the previously selected card back to normal
        if self.selected_widgets:
            for widget in self.selected_widgets:
                widget.config(bg=BUTTON_BG_COLOUR)
 
        # if clicked again it, remove the highlight
        if self.selected_game == game["name"]:
            self.selected_game = None
            self.selected_widgets = None
            self.confirm_button.config(state="disabled")
            return
 
        # highlight the specified game
        for widget in widgets:
            widget.config(bg=highlight)
 
        self.selected_game = game["name"]
        self.selected_widgets = widgets
        self.confirm_button.config(state="normal")
        
    # function to build the roster boxes for each team along with their current stats
    def _refresh_teams(self):
        for widget in self.teams_frame.winfo_children():
            widget.destroy()
 
        # clear out any column weights left over from a previous team count
        for col in range(4):
            self.teams_frame.columnconfigure(col, weight=0)
 
        for i, team_name in enumerate(self.team_names):
            self.teams_frame.columnconfigure(i, weight=1)
            team_colour = TEAM_COLOURS[i] if i < len(TEAM_COLOURS) else FG_COLOUR
 
            wins = self.game_wins.get(team_name, 0)
            header_text = f"{team_name}  ({wins}/{self.wins_needed})"
 
            # create the frame for the team name
            box = tk.Frame(self.teams_frame, bg=BUTTON_BG_COLOUR)
            box.grid(row=0, column=i, padx=10, sticky="nsew")
            tk.Label(box, text=header_text, font=TEAM_HEADER_FONT, bg=BUTTON_BG_COLOUR, fg=team_colour).pack(pady=(8, 8))
 
            # create a frame for the player names within the team box
            roster = tk.Frame(box, bg=BUTTON_BG_COLOUR)
            roster.pack(padx=15, pady=(0, 15), fill="x")
            roster.columnconfigure(0, weight=1)
            roster.columnconfigure(1, weight=0)
            roster.columnconfigure(2, weight=0)
 
            # populate the player name frame with the player names and their scores 
            for row, player in enumerate(self.teams.get(team_name, [])):
                stats = self.player_stats.get(player, {"positive": 0, "negative": 0})
                positive = stats.get("positive", 0)
                negative = stats.get("negative", 0)
 
                tk.Label(roster, text=player, font=ROSTER_FONT, bg=BUTTON_BG_COLOUR, fg=FG_COLOUR, anchor="w").grid(
                    row=row, column=0, sticky="ew", pady=2)
                tk.Label(roster, text=f"+{positive}", font=ROSTER_FONT, bg=BUTTON_BG_COLOUR, fg=POSITIVE_COLOUR, anchor="e").grid(
                    row=row, column=1, sticky="e", padx=(10, 0), pady=2)
                tk.Label(roster, text=f"-{negative}", font=ROSTER_FONT, bg=BUTTON_BG_COLOUR, fg=NEGATIVE_COLOUR, anchor="e").grid(
                    row=row, column=2, sticky="e", padx=(6, 0), pady=2)
    
    # function to update the label showing the round number and whose turn it is to choose
    def _update_turn_label(self):
        round_num  = len(self.games_played) + 1
        team_index = self.current_team % len(self.team_names)
        team_name  = self.team_names[team_index]
        team_colour = TEAM_COLOURS[team_index] if team_index < len(TEAM_COLOURS) else FG_COLOUR
        self.turn_label.config(
            text=f"Round {round_num} of {self.total_rounds} \u2014 {team_name} is choosing...",
            fg=team_colour,
        )
 
    # function to lock in the chosen game and hand the round off to the game itself
    def _on_confirm(self):
        if not self.selected_game:
            return
        game = next(g for g in self.available_games if g["name"] == self.selected_game)
        data = self.controller.shared_data
        data["games_played"].append(game)
        data["current_game"] = game
 
        self.controller.show_frame("PlayGame")