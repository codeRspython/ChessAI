import numpy as np

class GameState():
    def __init__(self):
        # Initialize the beginning state of a board
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
            ]

        # Initializing a dictionary where the move function of a piece can be accessed by typing the symbol for the piece
        self.moveFunctions = {'p': self.getPawnMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'R': self.getRookMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        # Initializing whose move it is in the beginning
        self.whiteToMove = True
        self.moveLog = []
        # Initializing the location of both kings in order to check for checks
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

    def makeMove(self, move):
        # Setting the square of the piece that moved empty
        self.board[move.startRow][move.startCol] = "--"
        # Moving the piece
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        # Update the location of the king
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        # Pawn Promotion
        if move.isPawnPromotion:
            color = 'w' if self.whiteToMove else 'b'
            self.board[move.endRow][move.endCol] = color + move.promotionChoice
        # Switching turns
        self.whiteToMove = not self.whiteToMove


    def undoMove(self):
        # Checking if there is a move to undo
        if len(self.moveLog) != 0:
            # Removing the last move
            move = self.moveLog.pop()
            # Reversing the squares
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # Reversing the turns
            self.whiteToMove = not self.whiteToMove
            # Updating the Kings' location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

    def getValidMoves(self):
        # Initializing all the directions a king might get attacked
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1))
        knightDirections = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        # Initializing a list of all the pseudolegal moves black can make
        moves = self.getPseudolegalMoves()
        # Initializing an empty list, which will contain only the valid moves in the end
        validMoves = []
        # Iterating through the list of blacks' moves (backwards, since we are removing items from it)
        for j in range(len(moves)-1, -1, -1):
            # Making the move --> now self.whiteToMove = True
            self.makeMove(moves[j])
            # Initializing the location of the king, the color of the enemy/ally and the directions from which a pawn can attack depending on which turn it is currently
            if not self.whiteToMove:
                startRow = self.whiteKingLocation[0]
                startCol = self.whiteKingLocation[1]
                enemyColor = 'b'
                allyColor = 'w'
                pawnDirections = [2, 3]
            else:
                startRow = self.blackKingLocation[0]
                startCol = self.blackKingLocation[1]
                enemyColor = 'w'
                allyColor = 'b'
                pawnDirections = [0, 1]
            # Iterating through all the directions
            for d in range(len(directions)):
                # Iterating through each possible square in this direction
                for i in range(1,8):
                    endRow = startRow + directions[d][0] * i
                    endCol = startCol + directions[d][1] * i
                    # Making sure the square is still on the board and not out of bounds
                    if 0 <= endRow < 8 and 0 <= endCol < 8:
                        endPiece = self.board[endRow][endCol]
                        color = endPiece[0]
                        type = endPiece[1]
                        # Checking if there is an enemy piece on the square that's not a king (since a king is never a danger to another king)
                        if color == enemyColor and type != 'K':
                            # If an enemy piece is on the square check if it's attacking the king from a direction it is really able to attack the king
                            if (0 <= d <= 3 and (type == 'B' or type == 'Q')) or \
                                (4 <= d <= 7 and (type == 'R' or type == 'Q')) or \
                                    ((d == pawnDirections[0] or d == pawnDirections[1]) and i == 1 and type == 'p'):
                                    # If after the move is made, a piece is actually attacking the king, remove this move as it has to be unvalid
                                    moves.remove(moves[j])
                                    break
                        elif color == allyColor:
                            break
                        else:
                            pass
                    else:
                        pass
            # Iterating through all the directions a knight might be able to attack the king
            for d in range(len(knightDirections)):
                endRow = startRow + knightDirections[d][0]
                endCol = startCol + knightDirections[d][1]
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                        endPiece = self.board[endRow][endCol]
                        color = endPiece[0]
                        type = endPiece[1]
                        if color == enemyColor and type == 'N':
                            moves.remove(moves[j])
            # Undoing the move in order to not mess up the current gamestate
            self.undoMove()
        # After all the unvalid moves have been removed, the validMoves list only contains the remaining moves, that are in fact valid
        validMoves = moves
        print('Legal moves: ' + str(len(moves)))
        return validMoves
      
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        # Switching turns in order to generate the opponents' moves
        self.whiteToMove = not self.whiteToMove
        # Generating the opponents' moves
        oppMoves = self.getValidMoves()
        # Switching back the turns
        self.whiteToMove = not self.whiteToMove
        # Iterating through each opponents' move
        for move in oppMoves:
            # If the endsquare of the move has the given coordinates, the given square is being attacked
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getPseudolegalMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        print('Pseudolegal moves: ' + str(len(moves)))
        return moves
    
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == '--':
                moves.append(Move((r,c), (r-1,c), self.board))
                if self.board[r-2][c] == '--' and r == 6:
                    moves.append(Move((r,c), (r-2,c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r,c), (r-1,c-1), self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c), (r-1,c+1), self.board))
        else:
            if self.board[r+1][c] == '--':
                moves.append(Move((r,c), (r+1, c), self.board))
                if self.board[r+2][c] == '--' and r == 1:
                    moves.append(Move((r,c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c), (r+1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c), (r+1, c+1), self.board))

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r,c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                         moves.append(Move((r,c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1)) # Up, Down, Left, Right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == '--':
                    moves.append(Move((r,c), (endRow, endCol), self.board))
                elif endPiece[0] == enemyColor:
                    moves.append(Move((r,c), (endRow, endCol), self.board))


class Move():
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.isPawnPromotion = True
        self.promotionChoice = 'Q'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.pieceMoved + ('x' if self.pieceCaptured != '--'  else '') + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]