import json
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from pages.base_page import PlaceholderPage
from config import (
    BG_COLOUR, FG_COLOUR, BUTTON_BG_COLOUR, BUTTON_HOVER_BG_COLOUR, BUTTON_FONT , GAME_CARD_FONT
)

class NewGameDraft(PlaceholderPage):
    page_title = "Game Draft"
    
    GRID_COLUMNS = 6
    CARD_IMAGE_SIZE = (100, 100)
    TRAY_IMAGE_SIZE = (50, 50)
    IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "images"
    
    def build_content(self):
        # setup the grid container to hold the available games
        grid_container = tk.Frame(self.content, bg=BG_COLOUR)
        grid_container.pack(fill="both", expand=True, pady=(0,20))
        
        # create a canvas and scrollbar to make the grid scrollable
        self.grid_canvas = tk.Canvas(grid_container, bg=BG_COLOUR, highlightthickness=0)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Vertical.TScrollbar", background=BUTTON_BG_COLOUR, troughcolor=BG_COLOUR,
            bordercolor=BG_COLOUR, arrowcolor=FG_COLOUR, lightcolor=BUTTON_BG_COLOUR, darkcolor=BUTTON_BG_COLOUR,
        )

        scrollbar = ttk.Scrollbar(
            grid_container, orient="vertical", command=self.grid_canvas.yview,
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
    def _make_card(self, parent, game, size, on_click):
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
        name_label = tk.Label(card, text=game["name"], font=GAME_CARD_FONT, bg=BUTTON_BG_COLOUR, fg=FG_COLOUR, wraplength=size[0])
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
            card = self._make_card(self.selected_games_frame, game, self.TRAY_IMAGE_SIZE, self._unpick_game)
            card.grid(row=0, column=i, padx=8, pady=8)
        
        self.start_button.config(state="normal" if len(self.picked) >= self.num_games_needed else "disabled")
        
    def _pick_game(self, game):
        print(self.num_games_needed, len(self.picked))
        if len(self.picked) >= self.num_games_needed:
            return
        self.picked.append(game)
        self._refresh_grid()
        self._refresh_selected_games()
        
    def _unpick_game(self, game):
        self.picked.remove(game)
        self._refresh_grid()
        self._refresh_selected_games()
    
    # function to display an error message in the grid if loading fails
    def _show_load_error(self, message):
        tk.Label(self.games_grid_frame, text=message, font=BUTTON_FONT, bg=BG_COLOUR, fg=FG_COLOUR, wraplength=500).pack(pady=40)
    
    def _on_start(self):
        self.controller.shared_data["draft_pool"] = self.picked
        self.controller.show_frame("FirstGamePageNameHere")