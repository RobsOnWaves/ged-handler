class MongoDbGed:

    def __init__(self, address: str, user: str, password: str):
        self.address = address
        self.user = user
        self.password = password

    def whoami(self):
        print(self.user)

