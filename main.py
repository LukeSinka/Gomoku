import random, sys, pygame, time, copy
from pygame.locals import *

FPS = 10 # frames per second to update the screen
WINDOWWIDTH = 1080 # width of the program's window, in pixels
WINDOWHEIGHT = 665 # height in pixels
SPACESIZE = 35 # width & height of each space on the board, in pixels
BOARDWIDTH = 19 # how many columns of spaces on the game board
BOARDHEIGHT = 19 # how many rows of spaces on the game board

WHITE_TILE = 'WHITE_TILE' # an arbitrary but unique value
BLACK_TILE = 'BLACK_TILE' # an arbitrary but unique value
EMPTY_SPACE = 'EMPTY_SPACE' # an arbitrary but unique value
ANIMATIONSPEED = 25 # integer from 1 to 100, higher is faster animation

# Amount of space on the left & right side (XMARGIN) or above and below
# (YMARGIN) the game board, in pixels.
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

#              R    G    B
WHITE      = (255, 255, 255)
BLACK      = (  0,   0,   0)
GREEN      = (  0, 155,   0)
BRIGHTBLUE = (  0,  50, 255)
BROWN      = (174,  94,   0)

TEXTBGCOLOR1 = BRIGHTBLUE
TEXTBGCOLOR2 = GREEN
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE


# deals with GUI, not the actual game
def main():
    # the global keyword makes these variables have global scope, but we only want these defined as soon as we initiate the game
    global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE

    pygame.init() # initiates a pygame instance (only one pygame instance permitted per program)
    # draw the main board, using pygame functions
    MAINCLOCK = pygame.time.Clock() # set up a clock
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT)) # initiates the GUI at correct size
    pygame.display.set_caption('Gomoku') # the text that displays to the window manager
    FONT = pygame.font.Font('freesansbold.ttf', 16) # define font used
    BIGFONT = pygame.font.Font('freesansbold.ttf', 32)

    # Set up the background image.
    boardImage = pygame.image.load('flippyboard.png')
    # Use smoothscale() to stretch the board image to fit the entire board:
    boardImage = pygame.transform.smoothscale(boardImage, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE)) # overwrites the image w/ the smoothed version
    boardImageRect = boardImage.get_rect() # get the Rect object from the Surface object
    boardImageRect.topleft = (XMARGIN, YMARGIN) # set the margin values on the Rectangle for the window
    BGIMAGE = pygame.image.load('flippybackground.png')
    # Use smoothscale() to stretch the background image to fit the entire window:
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
    
    # drawing the board over the background
    # blit(source, dest, area=None, special_flags=0) -> Rect
    # source is BGIIMAGE which is the background
    # dest is boardImage which is the board
    # area is boardImageRect which is a Rect object
    BGIMAGE.blit(boardImage, boardImageRect)

    # Run the main game.
    while True:
        if runGame() == False:
            pygame.quit()
            sys.exit()
            #break

# Plays a single game of Gomoku each time this function is called.
def runGame():
    # Reset the board and game.
    mainBoard = getNewBoard()

    # Draw the starting board and ask the player what color they want.
    # we allow the player who chooses color to go first
    drawBoard(mainBoard)
    color = enterPlayerTile()
    
    # Make the Surface and Rect objects for the "New Game"
    newGameSurf = FONT.render('New Game', True, TEXTCOLOR, TEXTBGCOLOR2)
    newGameRect = newGameSurf.get_rect()
    newGameRect.topright = (WINDOWWIDTH - 8, 10)

    #Creates the instructions, pygame doesn't support multiline text easily
    InstructionsSurf1 = FONT.render("Instructions:Click on", True, TEXTCOLOR, TEXTBGCOLOR2)
    InstructionsRect1 = InstructionsSurf1.get_rect()
    InstructionsRect1.topleft = (8, 10)
    
    InstructionsSurf2 = FONT.render("the line intersections", True, TEXTCOLOR, TEXTBGCOLOR2)
    InstructionsRect2 = InstructionsSurf2.get_rect()
    InstructionsRect2.topleft = (8, 28)
    
    InstructionsSurf3 = FONT.render("to lay a piece.", True, TEXTCOLOR, TEXTBGCOLOR2)
    InstructionsRect3 = InstructionsSurf3.get_rect()
    InstructionsRect3.topleft = (8, 46)
    
    InstructionsSurf4 = FONT.render("First to 5 in a row wins!", True, TEXTCOLOR, TEXTBGCOLOR2)
    InstructionsRect4 = InstructionsSurf3.get_rect()
    InstructionsRect4.topleft = (8, 64)
 
    while True: # main game loop
        if boardIsFull(mainBoard):
            break

        # Keep looping until the player clicks on a valid space.
        movexy = None
        while movexy == None:
            boardToDraw = mainBoard
            checkForQuit()

            for event in pygame.event.get(): # event handling loop
                if event.type == MOUSEBUTTONUP:
                    # Handle mouse click events
                    mousex, mousey = event.pos
                    if newGameRect.collidepoint( (mousex, mousey) ):
                        # Start a new game
                        return True
                    
                    # movexy is set to a two-item tuple XY coordinate, or None value
                    movexy = getSpaceClicked(mousex, mousey)
                    if movexy != None and not isValidMove(mainBoard, color, movexy[0], movexy[1]):
                        movexy = None

            # Draw the game board.
            drawBoard(boardToDraw)
            pygame.draw.rect(DISPLAYSURF,(0,155,0),(10,10,180,70))

            # Draw the player's turn.
            drawInfo(boardToDraw, color)
            # Draw the "New Game"
            DISPLAYSURF.blit(newGameSurf, newGameRect)
            DISPLAYSURF.blit(InstructionsSurf1,InstructionsRect1)
            DISPLAYSURF.blit(InstructionsSurf2,InstructionsRect2)
            DISPLAYSURF.blit(InstructionsSurf3,InstructionsRect3)
            DISPLAYSURF.blit(InstructionsSurf4,InstructionsRect4)

            MAINCLOCK.tick(FPS)
            pygame.display.update()

        # Make the move, Check if anyone has won
        makeMove(mainBoard, color, movexy[0], movexy[1])
        winnerColor = checkWin(mainBoard)
        
        #If A player has won, displays win message
        if(winnerColor != None):
            if winnerColor == WHITE_TILE:
                text = 'Congratulations White!  You beat Black.'
            else:
                text = 'Congratulations Black!  You beat White.'
                
            
            textSurf = FONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
            textRect = textSurf.get_rect()
            textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
            break

        #If nobody won, switches turn to the other player   
        color = WHITE_TILE if color == BLACK_TILE else BLACK_TILE

    # Display the "Play again?" text with Yes and No buttons.
    text2Surf = BIGFONT.render('Play again?', True, TEXTCOLOR, TEXTBGCOLOR1)
    text2Rect = text2Surf.get_rect()
    text2Rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 50)

    # Makes "Yes" button(As option to above question(Play Again?)).
    yesSurf = BIGFONT.render('Yes', True, TEXTCOLOR, TEXTBGCOLOR1)
    yesRect = yesSurf.get_rect()
    yesRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 90)

    # Make "No" button(*As option to above question).
    noSurf = BIGFONT.render('No', True, TEXTCOLOR, TEXTBGCOLOR1)
    noRect = noSurf.get_rect()
    noRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 90)

    while True:
        # Process events until the user clicks on Yes or No.
        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if yesRect.collidepoint( (mousex, mousey) ):
                    return True
                elif noRect.collidepoint( (mousex, mousey) ):
                    return False
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(text2Surf, text2Rect)
        DISPLAYSURF.blit(yesSurf, yesRect)
        DISPLAYSURF.blit(noSurf, noRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)

# Did Not Change From Original Code
def translateBoardToPixelCoord(x, y):
    return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)


def animateTileChange(tileColor, additionalTile):
    # Draw the additional tile that was just laid down. 
    #First checks to see which colour tile to animate
    if tileColor == WHITE_TILE:
        additionalTileColor = WHITE
    else:
        additionalTileColor = BLACK
    additionalTileX, additionalTileY = translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
    #Uses built in pygame.draw.circle() function
    pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2) - 4)
    pygame.display.update()

    for rgbValues in range(0, 255, int(ANIMATIONSPEED * 2.55)):
        if rgbValues > 255:
            rgbValues = 255
        elif rgbValues < 0:
            rgbValues = 0
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        checkForQuit()


def drawBoard(board):
    """
    Place background image, draw gridlines, and black & white piece
    """
     # Draw background of board.
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())

    # Draw grid lines of the board.
    for i in range(BOARDWIDTH):
        # Draw the horizontal lines.
        x = (i * (SPACESIZE)) + XMARGIN + (SPACESIZE / 2) #Modified to offset gridlines so that pieces are placed on line intersections
        y = YMARGIN
        endy = y + (BOARDHEIGHT * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (x, y), (x, endy))
    for i in range(BOARDHEIGHT):
        # Draw the vertical lines.
        x = XMARGIN
        y = (i * SPACESIZE) + YMARGIN + (SPACESIZE / 2) #Modified to offset gridlines
        endx = x + (BOARDWIDTH * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (x, y), (endx, y))

    # Draw the black & white pieces
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            centerx, centery = translateBoardToPixelCoord(x, y)
            if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
                if board[x][y] == WHITE_TILE:
                    tileColor = WHITE
                else:
                    tileColor = BLACK
                pygame.draw.circle(DISPLAYSURF, tileColor, (centerx, centery), int(SPACESIZE / 2) - 4)

# Did Not Change From Original Code
def getSpaceClicked(mousex, mousey):
    """
    Converts the coordinates of mouse click to the tile
    return (x, y) or None
    """
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if mousex > x * SPACESIZE + XMARGIN and \
               mousex < (x + 1) * SPACESIZE + XMARGIN and \
               mousey > y * SPACESIZE + YMARGIN and \
               mousey < (y + 1) * SPACESIZE + YMARGIN:
                return (x, y)
    return None


# draws text at the bottomleft corner of the screen to display who's turn it is
def drawInfo(board, color):
    scoreSurf = FONT.render("%s's Turn" % "White" if color == WHITE_TILE else "%s's Turn" % "Black", True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomleft = (10, WINDOWHEIGHT - 5)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def boardIsFull(board):
    """
    Checks if every space(line intersection) on the board is occupied by a piece, if it executes 
    the entire for loop it will return true, and the code that calls it will end the game
    """
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == EMPTY_SPACE:
                return False
    return True

# Did Not Change From Original Code
def getNewBoard():
    """
    Creates a brand new, empty board data structure.
    returns a 2D list of 'EMPTY_SPACE'
    [0].[0]  [1].[0] 
    [0].[1]  [1].[1]
    [0].[2]  [1].[2]
    """
    board = []
    for i in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)
    # [EMPTY_SPACE] means that we append each string as an item in list
    
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = EMPTY_SPACE

    return board


def isValidMove(board, tile, xstart, ystart):
    # Returns False if the player's move is invalid - this occurs in Gomoku if the place is already occuppied(or if the user is attempting to place a tile not on the board). 
    if board[xstart][ystart] != EMPTY_SPACE or not isOnBoard(xstart, ystart):
        return False
    return True

# Did Not Change From Original Code
def isOnBoard(x, y):
    # Returns True if the coordinates are located on the board.
    return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT


# Win condition
def checkWin(board):
    """
    checks for 5 consecutive pieces of same color horizontally, vertically or diagonally
    returns WHITE_TILE if white wins, BLACK_TILE if black wins, None if neither
    """
    WIN_CONSECUTIVE = 5
     
    # checking left right for each row
    consecutives = 1 # counter of how many tiles of i has there been
    for y in range(BOARDHEIGHT):
        for x in range(1,BOARDWIDTH):
            if board[x][y] == board[x - 1][y] and board[x][y] != EMPTY_SPACE:
                consecutives += 1
                if consecutives >= WIN_CONSECUTIVE and board[x][y] != EMPTY_SPACE:
                    return board[x][y]
            else:
                consecutives = 1
     
    # checking top down on each column
    consecutives = 1 
    for x in range(BOARDWIDTH):
        for y in range(1,BOARDHEIGHT):
            if board[x][y] == board[x][y - 1] and board[x][y] != EMPTY_SPACE:
                consecutives += 1
                if consecutives >= 5 and board[x][y] != EMPTY_SPACE:
                    return board[x][y]
            else:
                i = EMPTY_SPACE
                consecutives = 1
     
    # topleft-bottomright diagonals are those where x++, y++ that offset from 
    # the true diagonal, by an amount such that the total length of diagonal is 
    # >=5
     
    # topleft-bottomright diagonals
    for offset in range(BOARDWIDTH - (WIN_CONSECUTIVE-1)):
        # offset along the x-axis        
        consecutives = 1
        x = offset + 1
        # +1 because indexing x - 1
        y = 1 
        
        #Checks every diagonal to the upper right of the central diagonal(topleft-bottomright)
        while (x < BOARDWIDTH and y < BOARDHEIGHT):
            if board[x][y] == board[x - 1][y - 1]and board[x][y]!=EMPTY_SPACE :
                consecutives += 1
                if consecutives >= WIN_CONSECUTIVE and board[x][y] != EMPTY_SPACE:
                    return board[x][y]
            else:
                consecutives = 1
            x += 1
            y += 1

        # offset along the y-axis
        consecutives = 1 
        x = 1
        y = offset + 1
        #Checks every diagonal to the bottom left of the central diagonal(topleft-bottomright)
        while (x < BOARDWIDTH and y < BOARDHEIGHT):
            if board[x][y] == board[x - 1][y - 1]and board[x][y]!=EMPTY_SPACE :
                consecutives += 1
                if consecutives >= WIN_CONSECUTIVE and board[x][y] != EMPTY_SPACE:
                    return board[x][y]
            else:
                consecutives = 1
            x += 1
            y += 1
     
    # topright-bottomleft diagonals
    for offset in range(BOARDWIDTH - (WIN_CONSECUTIVE-2)):
        # offset along the x-axis
        consecutives = 1
        x = BOARDWIDTH - (offset + 2)
        y = 1
        #Checks every diagonal to the upper left of the central diagonal(topleft-bottomright)
        while (0 <= x and y < (BOARDHEIGHT - 1)):
            if board[x][y] == board[x + 1][y - 1]:
                consecutives += 1
                #print (consecutives,"/n")
                if consecutives >= WIN_CONSECUTIVE and board[x][y] != EMPTY_SPACE:
                    return board[x][y]
            else:
                consecutives = 1
            x -= 1
            y += 1

        # offset along y-axis
        consecutives = 1
        x = (BOARDWIDTH-2)
        y = offset + 1

        #Checks every diagonal to the bottom right of the central diagonal(topright-bottomleft)
        while (0 < x and y <= (BOARDHEIGHT - 1)):
            if board[x][y] == board[x + 1][y - 1] and board[x][y] != EMPTY_SPACE:
                consecutives += 1
                if consecutives >= WIN_CONSECUTIVE and board[x][y] != EMPTY_SPACE:
                    return board[x][y]
            else:
                consecutives = 1
            x -= 1
            y += 1

    return None

# Did Not Change From Original Code
def enterPlayerTile():
    """
    Interface to ask for which color user wants to play as.
    returns WHITE_TILE if player is white and goes first, BLACK_TILE otherwise
    OUTDATED:
    [WHITE_TILE, BLACK_TILE] if player is White
    [BLACK_TILE, WHITE_TILE] if player is Black
    """
    
    # Create the text.
    textSurf = FONT.render('Do you want to be white or black? (you will go first)', True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

    xSurf = BIGFONT.render('White', True, TEXTCOLOR, TEXTBGCOLOR1)
    xRect = xSurf.get_rect()
    xRect.center = (int(WINDOWWIDTH / 2) - 60, int(WINDOWHEIGHT / 2) + 40)

    oSurf = BIGFONT.render('Black', True, TEXTCOLOR, TEXTBGCOLOR1)
    oRect = oSurf.get_rect()
    oRect.center = (int(WINDOWWIDTH / 2) + 60, int(WINDOWHEIGHT / 2) + 40)

    while True:
        # Keep looping until the player has clicked on a color.
        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if xRect.collidepoint( (mousex, mousey) ):
                    return WHITE_TILE
                elif oRect.collidepoint( (mousex, mousey) ):
                    return BLACK_TILE

        # Draw the screen.
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(xSurf, xRect)
        DISPLAYSURF.blit(oSurf, oRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)


# Place tile on the board
def makeMove(board, tile, x, y):
    board[x][y] = tile
    animateTileChange(tile, (x, y))
    return True

#Did not change from original code
# Checks if the player quits
def checkForQuit():
    for event in pygame.event.get((QUIT, KEYUP)): # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

#Did not change from original code
# if called directly, will run the main function
if __name__ == '__main__':
    main()
