import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If num of cells is equal to the count, all cells are mines
        if len(self.cells) == self.count:
            return self.cells
            
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If count is zero, all cells are safe
        if self.count == 0:
            return self.cells
            
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Filter out the cell that is known to be a mine and lower count by 1
        if cell in self.cells:
            self.cells = set(filter(lambda x:x!=cell, self.cells))
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Filter out the cell that is known to be safe
        self.cells = set(filter(lambda x:x!=cell, self.cells))

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Get surrounding cells for new sentence
        surrounding = []
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Add to surrounding if cell in bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    surrounding.append((i, j))
        # Add new sentence to knowledge
        self.knowledge.append(Sentence(surrounding, count))

        while True:
            loop = False
            # Check knowledge for sentences with known mines or safes
            for sentence in self.knowledge:
                # Check for known safes
                if sentence.count == 0:
                    self.knowledge.remove(sentence)
                    for cell in sentence.cells:
                        self.mark_safe(cell)
                # Check for known mines:
                elif sentence.count == len(sentence.cells):
                    self.knowledge.remove(sentence)
                    for cell in sentence.cells:
                        self.mark_mine(cell)

            # Remove known safes or mines from remaining sentences
            for sentence in self.knowledge:
                to_remove = [] # List to track which cells to remove
                for cell in sentence.cells:
                    # Check known safes
                    if cell in self.safes:
                        to_remove.append(cell)
                        loop = True
                    # Check known mines
                    elif cell in self.mines:
                        to_remove.append(cell)
                        sentence.count -= 1
                        loop = True
                # Remove cells
                sentence.cells = set(filter(lambda x:x not in to_remove, sentence.cells))

            # Infer any new sentences
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1.cells.issubset(sentence2.cells):
                        inferred_sentence = Sentence((sentence2.cells - sentence1.cells), (sentence2.count - sentence1.count))
                        if len(inferred_sentence.cells) > 0 and inferred_sentence not in self.knowledge:
                            self.knowledge.append(inferred_sentence)
                            loop = True
            # If changes have been made to knowledge, loop again
            if not loop:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Possible moves are moves that are known safes and not already made
        possible_moves = list(filter(lambda x:x not in self.moves_made, list(self.safes)))
        # Make random choice, or return none if no safe moves
        if possible_moves:
            return random.choice(possible_moves)
        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_moves = []
        for i in range(self.height):
            for j in range(self.width):
                move = (i, j)
                if move not in self.moves_made and move not in self.mines:
                    possible_moves.append(move)
        # Make random choice, or return none if no safe moves
        if possible_moves:
            return random.choice(possible_moves)
        else:
            return None
            