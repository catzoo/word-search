import datetime

import blessed
from word_search import WordSearch

# TODO: Stop Game when all words are found
# TODO: Add Loading screen
# TODO: Maybe add in arrows for the grid. Or at least let the user know how big the grid is
# TODO: Add in a save / load


class Game:
    def __init__(self, word_search: WordSearch):
        self.word_search = word_search
        self.terminal = blessed.Terminal()

        self.keys = {
            # code - (method, args)
            "w": (self._move, 0, -1),   # Up
            "s": (self._move, 0, 1),    # Down
            "a": (self._move, -1, 0),   # Left
            "d": (self._move, 1, 0),    # Right
            " ": (self._select, ),      # Enter
            "r": (self._move_words, -1),
            "f": (self._move_words, 1)
        }

        self.positions = {
            # "part": [[x, y], [x, y]]
            #          x, y to x, y
            "grid": [],
            "words": [],
            "info": [],
            "timer": []
        }

        # The mapper that been resized. This helps with calculating if the user is at the end and off setting
        self.current_mapper = {"mapper": [[]], "top": "", "side_spacing": 0}

        # TODO: Maybe allow custom colors to coordinates. So, don't have a lot of lists for each color
        #   {[x, y]: string from terminal.color}
        self.found_coords = []
        self.select = []
        self.cursor = [0, 0]
        self.off_set = [0, 0]

        # TODO: Remove selected_word and use self.info
        self.selected_word = ""
        self.selected_coords = []

        self.word_rows = []
        self.word_offset = 0

        self.info = ""
        
        self.started = datetime.datetime.now()

        self.window_too_small = False

    def _draw_line(self, a_x, a_y, b_x, b_y):
        """
        Draws a line between two points (a -> b)

        :param a_x: x coordinate of a
        :param a_y: y coordinate of a
        :param b_x: x coordinate of b
        :param b_y: y coordinate of b

        :return: list of coordinates
        """

        # This is a bit confusing and hard to read. Mainly because all variables used are single letter
        # Variables used -
        # m         - Slope
        # x, y      - Coordinates
        # b         - Y-intercept or X-intercept
        # a_, b_    - Coordinates of A point / B point (a -> b)
        #
        # Equations used -
        # y = mx + b                        - to find y (used in x for loop)
        # x = (y - b) / m                   - to find x (used in y for loop)
        # m = (b_y - a_y) / (b_x - a_x)     - finding the slope
        # b = -(m * x) + y                  - finding the y-intercept
        try:
            # Getting the slope
            m = (b_y - a_y) / (b_x - a_x)
        except ZeroDivisionError:
            m = None

        if m is None:
            # Slope is undefined, grabbing the x-intercept
            b = a_x
        else:
            # Getting the y-intercept
            b = -(m * b_x) + b_y

        coords = []

        # Flipping the coordinates if a is greater than b
        # Doing this for the for loops. Range won't work if first value is greater than the second value
        if a_y > b_y:
            a_y, b_y = b_y, a_y

        if a_x > b_x:
            a_x, b_x = b_x, a_x

        # Finding y values for x
        if m is not None:
            for x in range(a_x, b_x + 1):
                y = round(m * x + b)
                coords.append([x, y])

        # Finding x values for y
        if m != 0:
            for y in range(a_y, b_y + 1):
                if m is None:
                    # its a vertical line. x = x-intercept
                    x = b
                else:
                    x = round((y - b) / m)

                # Adding the coord to the coords list.
                # Checking if the coord is already in the list. Then put it in order.
                # This is mainly so we can easily grab the word that was selected.
                cord = [x, y]
                if cord not in coords:
                    added = False
                    for k, c in enumerate(coords):
                        if c[0] >= cord[0]:
                            # TODO: Clean this up. It's a bit messy
                            if m is None or m > 0:
                                if c[1] >= cord[1]:
                                    coords = coords[:k] + [cord] + coords[k:]
                                    added = True
                                    break
                            elif m < 0:
                                if c[1] <= cord[1]:
                                    coords = coords[:k] + [cord] + coords[k:]
                                    added = True
                                    break

                    if added is False:
                        coords.append(cord)

        # self.info = str(m)

        return coords

    def _resize_mapper(self):
        # Grabbing the number of spaces for the column and row numbers
        side_spacing = len(str(self.word_search.height - 1)) + 2
        top_spacing = len(str(self.word_search.width - 1)) + 1

        # max coordinates the grid can expand to
        max_coord = [
            # dividing terminal.width by 2 since each letter is spaced out taking up 2 spaces.
            self.off_set[0] + (round(self.terminal.width / 2)) - side_spacing + 1,
            self.off_set[1] + self.terminal.height - top_spacing - 7
        ]

        # Grabbing a copy of the mapper resized or basically cutting some letters out to fit on the screen
        # depending on off_set
        mapper = []
        for row in self.word_search.mapper[self.off_set[1]:max_coord[1]]:
            row = row[self.off_set[0]:max_coord[0]]
            mapper.append(row)

        if not mapper:
            # Terminal is too small to fit the grid
            self.window_too_small = True
            return
        else:
            self.window_too_small = False

        # Creating the column numbers
        top = [[]]
        for x in range(len(mapper[0])):
            x += self.off_set[0]
            x = str(x)
            while len(x) > len(top):
                top.append([' ' for _ in range(len(top[0]))])

            for k, v in enumerate(x):
                top[k].append(v)

        # Adding space if its not the same as top spacing
        while len(top) < top_spacing - 1:
            top.append([' ' for _ in range(len(top[0]))])

        # Turning the top bar into a string
        top = top[::-1]  # Reversing the top bar

        top_string = ""
        for line in top:
            top_string += " " * side_spacing
            top_string += f"{' '.join(line)}\n"

        top_string += "\n"

        self.positions['grid'] = [
            [0, 0],
            [
                len(top[0]) * 2 + side_spacing,
                len(mapper) + top_spacing
            ]
        ]

        # Setting the current_mapper
        self.current_mapper = {
            "mapper": mapper,
            "top": top_string,
            "side_spacing": side_spacing
        }

    def _get_coord(self, relation, offset):
        """
        Grabs the starting coordinate depending on relation and offset.
        Made this since the code is used more than once. Also to make it more readable with a method rather
        than multiple statements.

        :param relation:    str             - name of coordinate to go by in self.positions
        :param offset:      list or tuple   - x, y to offset the relation
        :return:            list            - x, y coordinates
        """
        relation = self.positions[relation][1]
        # returning the starting coordinate
        return [
            relation[0] + offset[0],
            relation[1] + offset[1]
        ]

    def _grab_grid(self):
        string = self.current_mapper["top"]

        if self.select:
            self.selected_coords = self._draw_line(*self.cursor, *self.select)

            # Grabbing the world that is selected
            selected_word = ""
            for coord in self.selected_coords:
                selected_word += self.word_search.mapper[coord[1]][coord[0]]
            self.selected_word = selected_word
        else:
            self.selected_coords = []
            self.selected_word = ""

        for i, row in enumerate(self.current_mapper["mapper"]):
            y = i + self.off_set[1]
            string += self.terminal.ljust(str(y), self.current_mapper["side_spacing"])

            for x, val in enumerate(row):
                x += self.off_set[0]
                if [x, y] == self.cursor:
                    # Highlighting the cursor
                    string += self.terminal.reverse(val)
                elif [x, y] in self.selected_coords:
                    # user is selecting between two coordinates
                    string += self.terminal.white_on_green(val)
                elif [x, y] in self.found_coords:
                    # Highlighting the found words
                    string += self.terminal.white_on_blue(val)
                else:
                    string += val
                string += " "
            string += "\n"

        return self.terminal.move_xy(0, 0) + string

    def _set_words(self):
        self.word_rows = []
        width = self.terminal.width - 2  # subtract 2 to give room to add the arrows

        rows = [[]]
        cur_width = 0

        for word in self.word_search.words:
            word_width = len(word) + 2

            # Checking if the word is found
            if self.word_search.words[word][2]:
                word = self.terminal.white_on_blue(word)

            # Adding the word by checking if it can fit in the current row
            if width <= cur_width + word_width:
                rows.append([word])
                cur_width = word_width
            else:
                rows[-1].append(word)
                cur_width += word_width

        for r in rows:
            self.word_rows.append(", ".join(r))

        # Checking if the offset is outside. Just in case the screen was resized
        if self.word_offset > len(self.word_rows) - 1:
            self.word_offset = 0

    def _grab_words(self):
        coord = list(self.positions["timer"][0])
        coord[1] += 2

        max_rows = (self.terminal.height - coord[1]) - 1

        if max_rows >= len(self.word_rows):
            rows = self.word_rows
        else:
            rows = self.word_rows[self.word_offset:max_rows + self.word_offset]
            # Adding the arrows
            # Checking if there are any words hidden above
            if self.word_offset > 0:
                width = self.terminal.width - len(rows[0])
                rows[0] += self.terminal.rjust("▲", width)

            # Checking if there are anymore words hidden on the bottom
            if len(self.word_rows) - self.word_offset > max_rows:
                width = self.terminal.width - len(rows[-1])
                rows[-1] += self.terminal.rjust("▼", width)

        string = "\n".join(rows)

        self.positions['words'] = [
            (*coord,),
            (coord[0], coord[1] + len(rows))
        ]

        return self.terminal.move_xy(*coord) + string

    def _grab_info(self):
        # TODO: Make this return "" if the info is empty
        coord = self._get_coord("timer", (1, 0))
        max_x = self.terminal.width - coord[0]

        if self.selected_word:
            info = f"Selected Word: {self.selected_word} | {self.selected_word[::-1]}"
        else:
            info = " "

        # info = self.info

        if len(info) >= max_x:
            info = info[0: max_x - 4]
            info += "..."

        self.positions['info'] = [
            (*coord,),
            (coord[0] + len(info), coord[1])
        ]

        return self.terminal.move_xy(*coord) + info + self.terminal.clear_eol

    def _update_timer(self):
        coord = self._get_coord("grid", (0, 1))
        coord[0] = 0

        time_since = datetime.datetime.now() - self.started
        time_since = str(time_since).split('.')[0] + " |"

        self.positions['timer'] = [
            (*coord,),
            (coord[0] + len(time_since), coord[1])
        ]
        return self.terminal.move_xy(*coord) + str(time_since)

    def _print(self, grid=False):
        """
        Prints the game to the terminal
        :param grid:   bool    - If true, it'll clear the terminal and update everything
        :return:       None
        """
        if self.window_too_small:
            print(self.terminal.move_xy(0, 0) + "Screen is too small.")
            return
        
        string = ""

        if grid:
            string += self.terminal.clear() + self._grab_grid()

        # Don't like the two if statements. But it needs to be in order
        string += self._update_timer()

        if grid:
            string += self._grab_info()
            string += self._grab_words()

        print(string)

    def _move(self, t_x, t_y):
        def check(number, min_num, max_num, adding):
            number += adding
            return min_num <= number < max_num

        # Setting t_x, t_y with args tuple. To allow to check it in the for loop below
        args = (t_x, t_y)
        mapper = self.current_mapper['mapper']
        # Max coord of resized mapper
        max_coord = [len(mapper[0]), len(mapper)]
        # Max coord of mapper
        extended_mapper = [self.word_search.width, self.word_search.height]

        # This is a bit unreadable. Mostly did it this way to only need to type it once rather than two if statements.
        # This basically checks for both x, y in cursor. Also checks it with the above list's x, y
        for k, v in enumerate(self.cursor):
            # Checking if the coordinate isn't outside the resized mapper grid
            if check(v, self.off_set[k], max_coord[k] + self.off_set[k], args[k]):
                # Its still inside, move the cursor
                self.cursor[k] += args[k]

            # Checking if the coordinate isn't outside the grid
            elif check(v, 0, extended_mapper[k], args[k]):
                # Its still inside, need to off_set then resize
                self.off_set[k] += args[k]
                self._resize_mapper()
                # Moving the cursor
                self.cursor[k] += args[k]

    def _move_words(self, offset):
        self.word_offset += offset

        if self.word_offset < 0:
            self.word_offset = 0

        elif self.word_offset >= len(self.word_rows):
            self.word_offset = len(self.word_rows) - 1

    def _select(self):
        if self.select:
            # TODO: if its already found, don't add coordinates
            found = self.word_search.answer(*self.cursor, *self.select)
            if not found:
                found = self.word_search.answer(*self.select, *self.cursor)

            if found:
                self.found_coords += self.selected_coords
                self._set_words()

            self.select = []
        else:
            self.select = list(self.cursor)

    def start(self):
        while True:
            current_size = (self.terminal.width, self.terminal.height)
            with self.terminal.fullscreen(), self.terminal.cbreak(), self.terminal.hidden_cursor():
                self._resize_mapper()
                self._set_words()
                self._print(grid=True)
                val = ''
                while val.lower() != 'q':
                    val = self.terminal.inkey(timeout=1)

                    if val in self.keys:
                        run, args = self.keys[val][0], self.keys[val][1:]
                        run(*args)
                        # self.found_coords = self._draw_line(5, 5, *self.cursor)
                        self._print(grid=True)
                    else:
                        self._print(grid=False)
                    if current_size != (self.terminal.width, self.terminal.height):
                        break
            if val == 'q':
                break
            self.cursor = list(self.off_set)

    def load_key_config(self):
        pass
