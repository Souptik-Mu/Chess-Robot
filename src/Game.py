import chess
import random

class ChessGame :
    def __init__(self):
        self.board = chess.Board()
    
    def updateBoard(self, changed_squares : list[str]) -> tuple[chess.Move|None , bool] :
        """Returns a move if found, and if the move is valid or not"""
        src = None
        dst = None

        if len(changed_squares) == 2 :
            # Determine which square holds the piece belonging to the current player.
            for square in changed_squares:
                sq = chess.parse_square(square)
                piece = self.board.piece_at(sq)
                if piece is not None and piece.color == self.board.turn:
                    src = square
                else:
                    dst = square
            
        try :
            move = self.board.find_move(chess.parse_square(src),chess.parse_square(dst))
        except chess.IllegalMoveError :
            move = None
            
        print("found move raw :",move) 
        
        if self.board.is_legal(move) :
            #self.board.push(move)
            return (move,True) 
    
        return (move,False)
    
    def getHelp(self, changed_squares : list[str]) -> str :
        """Returns a move if found, and if the move is valid or not"""

        if len(changed_squares) != 1 :
            return ""
        
        square = changed_squares[0]
        sq = chess.parse_square(square)
        piece = self.board.piece_at(sq)
        if piece is None or piece.color != self.board.turn:
            return ""
        
        retStr = square
        for move in self.board.legal_moves:
            if move.from_square == sq:
                retStr += chess.square_name(move.to_square)
        print("Possible moves for square", square, ":", retStr)
        return retStr        

    def getNextMove(self) -> (chess.Move | None) :
        legal_moves = list(self.board.legal_moves)

        allowed_moves = list(filter(
            lambda move:    move.promotion is None and
                            not self.board.is_castling(move) and
                            not self.board.is_en_passant(move) ,
            legal_moves
        ))

        if allowed_moves:
            best_move = random.choice(allowed_moves)
            print(f"Generated Move: {best_move}")
            return best_move
        else:
            return None