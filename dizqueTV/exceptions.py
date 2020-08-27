class IncompleteSettingsError(Exception):
    def __init__(self):
        super().__init__("The provided settings are incomplete.")