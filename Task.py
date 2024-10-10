class Task:
    def __init__(self, id, name, difficult, description):
        self.id = id
        self.name = name
        self.difficult = difficult
        self.description = description

    def get_info(self):
        return {"Id": self.id, "Name": self.name,
                "Difficult": self.difficult, "Description": self.description}

    def update(self, name=None, difficult=None, description=None):
        if name:
            self.name = name
        if difficult:
            self.difficult = difficult
        if description:
            self.description = description