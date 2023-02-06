import random
import json


class OutOfBounds(Exception):
    """This is raised when x, y is outside mapper"""
    pass


class WordSearch:
    # Configuration Variables
    __empty_char = "."                 # Empty char. Will be used to determine if a position on the map is empty
    __letters = (ord('a'), ord('z'))   # Will help determine the range for random characters (97(a) -> 122(z) for UTF-8)

    def __init__(self):
        self.mapper = None  # Will keep track of the grid of characters. Note (y, x) not (x, y)
        self.words = {      # Keep track of words that have been placed in mapper
            # 'word': ((x,y), (x,y), bool) # Word is located at (x, y) to (x, y) and if the user found the word (bool)
        }

    @property
    def width(self):
        return len(self.mapper[0])

    @property
    def height(self):
        return len(self.mapper)

    def _for_range(self, x, y, t_x, t_y, to_range):
        """
        A Basic for loop that keeps track of the position (x, y).
        The parameters are kind of confusing.

        x, y are the starting position.
        t_x, t_y is how much to increase x, y every loop. Basically, changing position every time
        to_range is how far to go with x, y.

        For example, if you wanted to go in a line to the right, 10 spaces, starting at 0,0. You would do:

        _for_range(0, 0, 1, 0, 10)

        ^ This will start at 0, 0. Increase x by 1 every loop, and go to 10 spaces

        This will also raise OutOfBounds if x or y is outside mapper

        :param x:           Starting x
        :param y:           Starting y
        :param t_x:         Increase x by t_x
        :param t_y:         Increase y by t_y
        :param to_range:    How far to go

        yields x, y, number
        """
        max_x = self.width - 1
        max_y = self.height - 1

        for number in range(to_range):
            if x < 0 or y < 0 or max_x < x or max_y < y:
                # x or y is outside mapper. Raise OutOfBounds error
                raise OutOfBounds()

            yield x, y, number
            x += t_x
            y += t_y

    def _grab_char(self, x, y):
        return self.mapper[y][x]

    def _grab_range(self, x, y, t_x, t_y, to_range):
        string = ""
        for x, y, _ in self._for_range(x, y, t_x, t_y, to_range):
            # Using _grab_char just in case __mapper changes
            string += self._grab_char(x, y)

        return string

    def _set_char(self, x, y, char):
        self.mapper[y][x] = char

    def _set_range(self, x, y, t_x, t_y, string):
        for x, y, number in self._for_range(x, y, t_x, t_y, len(string)):
            # Using _set_char just in case __mapper changes
            self._set_char(x, y, string[number])

    def _check_word(self, x, y, t_x, t_y, word):
        """
        This checks if the word can be added to x, y, t_x, t_y
        For more information about the parameters, check _for_range's documentation

        :return: bool, if the word can be there or not
        """
        if t_x == 0 and t_y == 0:
            return False

        try:
            # Grabbing the word that is in the range
            grab = self._grab_range(x, y, t_x, t_y, len(word))
        except OutOfBounds:
            return False

        check = True
        for num, char in enumerate(grab):
            if char != self.__empty_char and char != word[num]:
                check = False

        return check

    def _expand_y(self, to_range):
        """
        Expands the map by height.

        Note: The first row will need some data (since this uses len(self.__mapper[0])
        :param to_range: How far to expand
        :return:
        """
        row = [self.__empty_char for _ in range(len(self.mapper[0]))]
        for _ in range(to_range):
            self.mapper.append(list(row))  # Grabbing a copy of the row rather than the reference

    def _expand_x(self, to_range):
        """
        Expands the map by width

        Note: The first row needs to be there (either empty list or has some data)
        :param to_range: How far to expand
        :return:
        """
        for row in self.mapper:
            for _ in range(to_range):
                row.append(self.__empty_char)

    def _expand_mapper(self, width, height):
        """
        Expands the mapper by both x / y. This is good to use if mapper hasn't been setup yet.
        :param width:  How wide to expand by
        :param height: How high to expand
        :return:
        """
        if self.mapper is None:
            # Setting up the mapper since a row hasn't been made yet
            self.mapper = [[]]
            # Subtracting by one since mapper has one row already
            height -= 1

        self._expand_x(width)
        self._expand_y(height)

    def extra_words(self, words, min_word_width=3):
        """
        Searches through the whole mapper looking for extra words.

        Note, this is inefficient, it will take a while to go through everything.

        :param words:           list, dict, what words to look for
        :param min_word_width:  int, the min word's width. This is so it doesn't return one letter words
        :return:                dict -- {'word': (x, y, t_x, t_y)} -- Words that was found
        """
        # TODO: Maybe have it check min / width so it knows the range. Rather than just guessing and waiting for
        #   OutOfBounds exception

        extra = {  # will contain the extra words found
            # 'word': (x, y, t_x, t_y)
        }
        height, width = len(self.mapper), len(self.mapper[0])
        x, y = 0, 0
        while y < height:
            # grabbing t_x and t_y. Easier to keep track with for loops
            for t_x in range(-1, 2):
                for t_y in range(-1, 2):
                    if t_x == 0 and t_y == 0:
                        break
                    to_range = min_word_width
                    # grabbing the word
                    while True:
                        try:
                            word = self._grab_range(x, y, t_x, t_y, to_range)
                        except OutOfBounds:
                            break
                        else:
                            if word in words:
                                extra[word] = (x, y, t_x, t_y)
                            to_range += 1
            if x >= width:
                x = 0
                y += 1
            else:
                x += 1

        return extra

    @classmethod
    def generate(cls, words=None, height=10, width=10, num_of_words=10, min_word_width=3, extend_by=5,
                 add_letters=True):
        """
        Create the word search game
        :param words: List of words to use
        ----- configuration -----
        :param height:              height to start with
        :param width:               width to start with
        :param num_of_words:        number of words to add
        :param min_word_width:      minimum length for words
        :param extend_by:           When there is no room, how much to expand by (x and y)
        :param add_letters:         Add random letters to empty spaces or not. This is mostly used for debugging.
                                    Could also be used to see which is the best configuration.

        :return: WordSearch
        """
        if height <= 0 or width <= 0 or num_of_words <= 0 or min_word_width <= 0 or extend_by <= 0:
            raise ValueError("All parameters must be greater than 0")

        self = cls()

        # Creating the mapper
        self._expand_mapper(width, height)

        # Grabbing random words depending on num_of_words
        words_list = []
        while len(words_list) < num_of_words:
            temp = random.choice(words)
            if len(temp) >= min_word_width and temp not in words_list:
                words_list.append(temp)

        # Adding the words to __mapper
        while len(words_list) != 0:
            # Grabbing the word
            word = words_list[0]
            # Positions will contain random possible positions for the word
            positions = [
                # (x, y, t_x, t_y)
            ]
            for _ in range(19999):
                x, y = random.randrange(0, len(self.mapper[0])), random.randrange(0, len(self.mapper))
                t_x, t_y = random.randint(-1, 1), random.randint(-1, 1)

                if self._check_word(x, y, t_x, t_y, word):
                    # if (x, y, t_x, t_y) not in positions:
                    positions.append((x, y, t_x, t_y))

            if positions:
                # pos = (x, y, t_x, t_y)
                # Grabbing a random position from the list
                pos = random.choice(positions)
                # Adding the word to the mapper
                self._set_range(*pos, string=word)
                end_pos = (
                    pos[0] + pos[2] * (len(word) - 1),
                    pos[1] + pos[3] * (len(word) - 1)
                )
                # Adding the word to __words to be used to check where the word is at
                self.words[word] = [(pos[0], pos[1]), end_pos, False]
                # Done with the word, remove it
                words_list.pop(0)
            else:
                # Word can't fit. Expand the mapper
                self._expand_mapper(extend_by, extend_by)

        if add_letters:
            for y, row in enumerate(self.mapper):
                for x, letter in enumerate(row):
                    if letter == self.__empty_char:
                        char = random.randint(self.__letters[0], self.__letters[1])
                        self._set_char(x, y, chr(char))

        return self

    @classmethod
    def generate_json(cls, filename, **kwargs):
        """
        Create the word search game with .json file.
        This was made to open a .json file in https://github.com/dwyl/english-words

        This uses generate to create the word search game.
        Just opens the file and gives it to generate as words

        :param filename:  str, name of file to open
        :param kwargs:    **kwargs given to WordSearch.generate
        :return:          WordSearch
        """
        with open(filename, 'r') as fp:
            words = list(json.load(fp))

        return cls.generate(words, **kwargs)

    def answer(self, x, y, s_x, s_y):
        """
        Find a word on the grid

        :param x:       Starting x
        :param y:       Starting y
        :param s_x:     Ending x
        :param s_y:     Ending y
        :return:        found    - bool, if the word is at the coordinates / user found it
        """
        for k, v in self.words.items():
            if v[0] == (x, y) and v[1] == (s_x, s_y):
                v[2] = True
                return True
        return False

    def to_string(self):
        # this is a bit confusing statement. Basically, its getting the width of the number and adding it by 2
        # This is for the row numbers on the side. Reason why its converting how many rows into a string is because
        # its trying to grab the width of that number. This will be used to add space between the mapper and numbers
        string_space = len(str(len(self.mapper))) + 2

        # Creating the top numbers
        top = [[]]  # This will contain lines of string
        for x in range(len(self.mapper[0])):
            x = str(x)
            if len(x) != len(top):
                top.append([' ' for _ in range(len(top[0]))])

            for k, v in enumerate(x):
                top[k].append(v)

        top = top[::-1]
        string = ""
        for line in top:
            string += " " * string_space
            string += f"{' '.join(line)}\n"

        string += "\n"
        for number, line in enumerate(self.mapper):
            string += str(number).ljust(string_space)
            string += f"{' '.join(line)}\n"

        string += f"\n{', '.join(self.words)}"

        return string
