import cv2 as cv
import numpy as np


class Camera :       #Access the camera, crops the vedio
    def __init__(self, camera : cv.VideoCapture  ,sizeX :int = 800, sixeY :int = 800 ) : 
        self._camera  = camera  #Access camera
        self._sX = sizeX
        self._sY = sixeY
        self._copy = None
        self._ready = False
        self._points : list[tuple[int,int]] = []
        self.win = "Select Corners Clockwise"
    
    def _onClick(self, event, x, y, flags, param ):
        if event == cv.EVENT_LBUTTONDOWN :
            self._copy = self._copy.copy()
            cv.circle(self._copy, (x,y) , 10, (255,0,0), 1)
            self._points.append((x,y))
            cv.imshow( self.win, self._copy )
            #print(self._points)   

            if len(self._points) == 4 :
                #print("All corners are selected")
                self._ready = True
                cv.destroyWindow("Select Corners Clockwise")
                return
        return

    def _cropImage(self , image :cv.typing.MatLike , corners :list[tuple[int,int]] ) -> cv.typing.MatLike :    
        if not self._ready or len(corners) != 4:
            return image
        rect = np.array( corners , dtype="float32")
        dst = np.array([ [0, 0], 
                         [self._sX - 1, 0], 
                         [self._sX - 1, self._sY - 1], 
                         [0, self._sY - 1] ],             dtype="float32")
        
        matrix = cv.getPerspectiveTransform(rect , dst) # gets transforms
        return cv.warpPerspective(image , matrix , (self._sX,self._sY) ) #apply transform to wrap

    # public functions

    def clearSelection(self) :
        self._points.clear()
        self._ready = False 
    
    def setSelection(self) -> None:
        self.clearSelection()
        _ , self._copy = self._camera.read()
        cv.imshow( self.win , self._copy )
        cv.setMouseCallback( self.win, self._onClick)
        return
    
    def getCurrentFrame(self) -> cv.typing.MatLike  :
        _,frame =self._camera.read()
        if _ :         
            return self._cropImage( frame , self._points ) 

    #PUBLIC 
def hex2bgr(hex_color: str) -> tuple:
    if(not hex_color.startswith('#')):
        hex_color = "#A6A6A6"
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError("Hex color must be in the format RRGGBB")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)

def drawGrid(image :cv.typing.MatLike ,gridColor :cv.typing.Scalar,  sizeX :int , sizeY :int) -> cv.typing.MatLike :   # use to display the board with grid
    '''Returns image with drawn grid on it'''
    #square_size = board_size // 8
    gridColor = hex2bgr(gridColor)  # Convert hex color to BGR tuple
    X = sizeX // 8
    Y = sizeY // 8
    for i in range(1, 8):
        cv.line(image, (i * X, 0), (i * X, sizeY), gridColor , 1)
        cv.line(image, (0, i * Y), (sizeX, i * Y), gridColor , 1)
    return image

def getVal(stored_frame :cv.typing.MatLike, current_frame :cv.typing.MatLike) -> list[str] : 
    """ Compare the current frame with the stored frame and return a list of changed squares.   """
    if stored_frame is None:
        return []
    else:
        # Compute absolute difference between stored and current frame
        diff = cv.absdiff(stored_frame, current_frame)
        gray_diff = cv.cvtColor(diff, cv.COLOR_BGR2GRAY)
        _, thresh = cv.threshold(gray_diff, 30, 255, cv.THRESH_BINARY)
        
        # Divide the board into 8x8 squares and check each square
        board_size = current_frame.shape[0]  # assuming board is square
        square_size = board_size // 8
        
        changed_squares = []
        for i in range(8):
            for j in range(8):
                square = thresh[i*square_size:(i+1)*square_size, j*square_size:(j+1)*square_size]   #sclicing squares
                # Mark square if the ratio of changed pixels is above threshold
                if cv.countNonZero(square) / (square_size * square_size) > 0.13:
                    rank = 8 - i
                    file = chr(ord('a') + j)
                    square_name = f"{file}{rank}"
                    changed_squares.append(square_name)

        print("Changed squares:", changed_squares)
        return changed_squares
        