import json
from pathlib import Path

STATS_PATH = Path(__file__).resolve().parent.parent / "data" / "player_stats.json"

# function to read the json of player stats
def _load(path: Path) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# function to save the new stats to the json file
def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# function to create a new default entry for a new player
def _default_entry() -> dict:
    return {
        "rounds_played": 0,
        "games_played": 0,
        "all_time_positive": 0,
        "all_time_negative": 0,
        "records": [],
    }

# public function to call at the end of every round to update player stats
# increments the round count, adds to the point totals and updates any high scores
def record_round(player_names: list, round_stats: dict, game_name: str, path: Path = STATS_PATH) -> None:
    db = _load(path)

    for name in player_names:
        key = name.lower()
        entry = db.setdefault(key, _default_entry())

        delta = round_stats.get(name, {"positive": 0, "negative": 0})
        pos = delta.get("positive", 0)
        neg = delta.get("negative", 0)

        entry["rounds_played"] += 1
        entry["all_time_positive"] += pos
        entry["all_time_negative"] += neg

        # update records list — at most one "positive" and one "negative" entry per game
        _update_record(entry["records"], game_name, pos, "positive")
        _update_record(entry["records"], game_name, neg, "negative")

    _save(path, db)

# function to call at the end of every game to update and save player stats
def record_game(player_names: list, path: Path = STATS_PATH) -> None:
    db = _load(path)

    for name in player_names:
        key = name.lower()
        entry = db.setdefault(key, _default_entry())
        entry["games_played"] += 1

    _save(path, db)

# function to update the player records list with a new high score if needed
def _update_record(records: list, game_name: str, value: int, kind: str) -> None:
    # skip if no points were recorded
    if value == 0:
        return

    # check if there is already an entry for this game and if it's a new high score
    for i, record in enumerate(records):
        if record[0] == game_name and record[2] == kind:
            if value > record[1]:
                records[i] = [game_name, value, kind]
            return

    # no existing entry for this game + kind combination
    records.append([game_name, value, kind])

