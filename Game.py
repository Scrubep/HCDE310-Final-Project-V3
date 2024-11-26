# Simple class called games that makes it simpler to access values that are given
# through the RAWG API.

class Game:
    def __init__(self, title, genre, image, description):
        self.title = title
        self.genre = genre
        self.image = image
        self.description = description