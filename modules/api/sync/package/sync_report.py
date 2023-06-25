class SyncReport:
    def __init__(self):
        self.created_count = 0
        self.updated_count = 0
        self.unchanged_count = 0
        self.error_count = 0

    def __str__(self):
        report_values = f"created: {self.created_count}, updated: {self.updated_count}, unchanged: {self.unchanged_count}, in error: {self.error_count}"

        return f"Synchronization report. {report_values}"
