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
        # If num of cells equals the count, all cells are mines
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
        # If cell is in sentence, remove cell from sentence and lower count by 1
        copy_cells = self.cells.copy()
        for sentence_cell in self.cells:
            if sentence_cell == cell:
                copy_cells.remove(sentence_cell)
                self.count -= 1
                if self.count < 0:
                    print("ERROR", self)
        self.cells = copy_cells.copy()
        # Check sentence for new inferences

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If cell is in sentence, remove cell from sentence but leave count as is
        copy_cells = self.cells.copy()
        for sentence_cell in self.cells:
            if sentence_cell == cell:
                copy_cells.remove(sentence_cell)
        self.cells = copy_cells.copy()


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

    def check_sentence(self, sentence):
        """
        Checks if any safes or mines can be added 
        from the given sentence and adds them.
        """
        # Add any known safes
        known_safes = sentence.known_safes()
        if known_safes:
            for safe_cell in known_safes:
                self.mark_safe(safe_cell)
            return True

        # Add any known mine cells to mines
        known_mines = sentence.known_mines()
        if known_mines:
            for mine_cell in known_mines:
                self.mark_mine(mine_cell)
            return True
        
        # If no knowns
        return False


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
       
       # Mark cell as safe and add it to moves made
        self.mark_safe(cell)
        self.moves_made.add(cell)

        # Get surrounding cells to make new sentence, not including any known safes
        surrounding = []
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Add to surrounding if cell in bounds and not in known safes
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) not in self.safes:
                        surrounding.append((i, j))

        new_sentence = Sentence(surrounding, count)
        print(new_sentence)
        # Add to knowledge if the sentence is not all safes or mines
        if not self.check_sentence(new_sentence):
            self.knowledge.append(new_sentence)

        # Loop through knowledge and add any new sentences which can be inferred
        while True:
            loopA = False
            # First loop through knowledge base and check for any new known safes, mines, or empty sentences
            while True:
                loopB = False
                for sentence in self.knowledge:
                    # If there are any knowns, mark them all and remove now empty sentence from knowledge, and loop again
                    if self.check_sentence(sentence):
                        self.knowledge.remove(sentence)
                        loopB = True
                   # if len(sentence.cells) == 0 and sentence in self.knowledge:
                  #      self.knowledge.remove(sentence)
                if not loopB:
                    break
            
            # Get list of all sets in knowledge for reference
            sets = []
            for sentence in self.knowledge:
                sets.append(sentence.cells)

            # Check for inferred sentences
            length = len(self.knowledge)
            for i in range(length):
                for j in range(i + 1, length):
                    sentence_A = self.knowledge[i]
                    sentence_B = self.knowledge[j]
                    # See if sentence_A is found within sentence_B, and infer new sentence if so
                    if sentence_A.cells.issubset(sentence_B.cells):
                        inferred_cells = list(sentence_B.cells - sentence_A.cells)
                        inferred_count = sentence_B.count - sentence_A.count
                        inferred_sentence = Sentence(inferred_cells, inferred_count)
                        if inferred_sentence.cells not in sets:
                            self.knowledge.append(inferred_sentence)
                            loopA = True       
                    # Check subset vice-versa
                    if sentence_B.cells.issubset(sentence_A.cells):
                        inferred_cells = list(sentence_A.cells - sentence_B.cells)
                        inferred_count = sentence_A.count - sentence_B.count
                        inferred_sentence = Sentence(inferred_cells, inferred_count)
                        if inferred_sentence.cells not in sets:
                            self.knowledge.append(inferred_sentence)
                            loopA = True
            if not loopA:
                break

        print ("Mines", self.mines)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # Get all the possible safe moves that are not in moves_made
        possible_moves = []
        for move in self.safes:
            if move not in self.moves_made:
                possible_moves.append(move)

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
        
        # Get all possible moves in a list
        possible_moves = []

        # Check every cell in board
        for i in range(self.height):
            for j in range(self.width):
                move = (i, j)
                if move not in self.moves_made and move not in self.mines:
                    possible_moves.append(move)
        
        # Randomly select a possible move
        if possible_moves:
            return random.choice(possible_moves)
        else:
            return None
