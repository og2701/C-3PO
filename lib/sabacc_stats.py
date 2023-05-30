import json
from pathlib import Path

class Stats:
    def __init__(self, user_id):
        self.file_path = Path(f'stats/{user_id}.json')
        self.stats = self.load_stats()

    def load_stats(self):
        if self.file_path.exists():
            with self.file_path.open() as file:
                return json.load(file)
        else:
            return {"wins": 0, "losses": 0}

    def save_stats(self):
        with self.file_path.open('w') as file:
            json.dump(self.stats, file)

    def increment_wins(self):
        self.stats["wins"] += 1
        self.save_stats()

    def increment_losses(self):
        self.stats["losses"] += 1
        self.save_stats()

    def format_stats(self):
        return f"Wins: {self.stats['wins']} | Losses: {self.stats['losses']}"
