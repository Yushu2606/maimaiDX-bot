import shelve


class Database:
    def __init__(self, name: str):
        self.name = name
        self.db = shelve.open(f"./data/{self.name}")

    def __enter__(self):
        return self

    def set(self, key: str, value: any) -> None:
        self.db[key] = value

    def get(self, key) -> any:
        return self.db.get(key)

    def __exit__(self, atype, value, trace) -> None:
        self.db.close()
