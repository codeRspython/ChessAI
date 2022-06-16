import pygame as p
import os
import Engine

p.init()

WIN_WIDTH = WIN_HEIGHT = 512
DIMENSION = 8
SQ_SIZE = WIN_WIDTH // DIMENSION
MAX_FPS = 15
IMGS = {}
ICON = p.image.load(os.path.join("imgs", "icon.png"))

def loadImages ():
    pieces = ['wp', 'wK', 'wN', 'wB', 'wQ', 'wR', 'bp', 'bK', 'bN', 'bB', 'bQ', 'bR']
    for piece in pieces:
        IMGS[piece] = p.image.load(os.path.join("imgs", piece + ".png"))

def drawBoard(win):
    colors = [p.Color('light gray'), p.Color('dark gray')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(win, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(win, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                win.blit(IMGS[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawGameState(win, gs):
    drawBoard(win)
    drawPieces(win, gs.board)

def main():
    win = p.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = p.time.Clock()
    win.fill(p.Color('White'))
    p.display.set_caption('Chess AI')
    p.display.set_icon(ICON)
    gs = Engine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    sq_selected = () # Tuple (r, c)
    playerClicks = [] # 2 Tuples
    loadImages()
    
    run = True

    while run:
        for event in p.event.get():
            if event.type == p.QUIT:
                run = False
                p.quit()
                quit()
            elif event.type == p.MOUSEBUTTONDOWN:
                loc = p.mouse.get_pos()
                c = loc[0] // SQ_SIZE
                r = loc[1] // SQ_SIZE
                if sq_selected == (r, c):
                    sq_selected = ()
                    playerClicks = []
                else:
                    sq_selected = (r, c)
                    playerClicks.append(sq_selected)
                if len(playerClicks) == 2:
                    move = Engine.Move(playerClicks[0], playerClicks[1], gs.board)
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                        sqSelected = ()
                        playerClicks = []
                    else:
                        playerClicks = [sq_selected]
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    gs.undoMove()
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(win, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
        

if __name__ == '__main__':
    main()