from time import time

class SyncReport:
    def __init__(self):
        self.timer = { 'start': time(), 'end': None, 'elapsed_seconds': None }
        self.created_count = 0
        self.updated_count = 0
        self.unchanged_count = 0
        self.error_count = 0

    def start_timer(self):
        self.timer = { 'start': time(), 'end': None }

    def stop_timer(self) -> int:
        self.timer['end'] = time()

        return int(self.timer['end'] - self.timer['start'])

    def __str__(self):
        elapsed_seconds = self.stop_timer()
        elapsed_format = f"{elapsed_seconds} second(s)" if elapsed_seconds < 60 else f"{round(elapsed_seconds / 60, 1)} minute(s)"
        report_values = f"created: {self.created_count}, updated: {self.updated_count}, unchanged: {self.unchanged_count}, in error: {self.error_count}"

        return f"Synchronization finished in {elapsed_format}. {report_values}"
