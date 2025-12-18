import json

class DataStorage:
    def __init__(self, filename='form_data.json'):
        self.filename = filename
        self.load_data()

    def load_data(self):
        try:
            with open(self.filename, 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = []

    def save_data(self):
        with open(self.filename, 'w') as file:
            json.dump(self.data, file)

    def add_entry(self, entry):
        self.data.append(entry)
        self.save_data()

    def get_all_entries(self):
        return self.data
