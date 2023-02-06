import argparse
from game import Game
from word_search import WordSearch

parser = argparse.ArgumentParser(
    prog="main.py",
    description="Game about searching for words. When generating a new board, "
                "if the word doesn't fit then it'll extend the board. You can determine by how much by using --extend",
)

parser.add_argument("--width", "-W", type=int, default=10, help="min width of the game")
parser.add_argument("--height", "-H", type=int, default=10, help="min height of the game")
parser.add_argument("--words", "-w", type=int, default=10, dest="num_of_words", help="number of words. Default 10")
parser.add_argument("--extend", "-e", type=int, default=5, dest="extend_by",
                    help="When a word doesn't fit, it'll extend the board by amount")
parser.add_argument("-l", action="store_false", dest="add_letters",
                    help="Remove letters from the board. Exposing the added words.")

if __name__ == "__main__":
    arguments = parser.parse_args()
    try:
        word_search = WordSearch.generate_json("words_dictionary.json", **vars(arguments))
    except ValueError as e:
        print(e)
    else:
        game = Game(word_search).start()


