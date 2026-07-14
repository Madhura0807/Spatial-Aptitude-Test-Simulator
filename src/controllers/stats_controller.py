"""
stats_controller.py
Thin convenience wrapper around DatabaseManager statistics queries, used by
the Result / Previous Scores / Leaderboard screens.
"""


class StatsController:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_user_statistics(self, user_id):
        return self.db.get_statistics(user_id)

    def get_previous_scores(self, user_id):
        return self.db.get_previous_scores(user_id)

    def get_leaderboards(self):
        return {
            "highest_score": self.db.get_leaderboard_highest_score(),
            "fastest_completion": self.db.get_leaderboard_fastest(),
            "best_accuracy": self.db.get_leaderboard_best_accuracy(),
        }

    def get_achievements(self, user_id):
        return self.db.get_achievements(user_id)
