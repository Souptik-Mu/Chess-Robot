import cv2 as cv
import numpy as np

class VedioCrop :
    def __init__(self , sizeX :int = 800, sixeY :int = 800 ) : 
        self._points : list[tuple[int,int]] = []
        self._sX = sizeX
        self._sY = sixeY
        self._copy = None
        self._ready = False
        self.win = "Select Corners Clockwise"
    
    def _onClick(self, event, x, y, flags, param ):
        if event == cv.EVENT_LBUTTONDOWN :
            
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
        if not self._ready :
            return image
        
        rect = np.array( corners , dtype="float32")
        dst = np.array([ [0, 0], 
                         [self._sX - 1, 0], 
                         [self._sX - 1, self._sY - 1], 
                         [0, self._sY - 1] ],             dtype="float32")
        
        matrix = cv.getPerspectiveTransform(rect , dst) # gets transforms
        return cv.warpPerspective(image , matrix , (self._sX,self._sY) ) #apply transform to wrap

    # public functions
    
    def getCroppedFrame(self, frame :cv.typing.MatLike) -> cv.typing.MatLike :
        return self._cropImage( frame , self._points )   
    
    def setSelection(self, frame :cv.typing.MatLike) -> None:
        self._points.clear()
        self._ready = False
        self._copy = frame.copy()
        cv.imshow( self.win , self._copy )
        cv.setMouseCallback( self.win, self._onClick)
        return

    def getSelection(self, frame :cv.typing.MatLike) -> cv.typing.MatLike :
        self.setSelection(frame)
        cv.waitKey()
        return self._cropImage( frame , self._points )  



####################################################################################################################
''' #############            Additional function for image fintering and detection                ############## '''
####################################################################################################################



def _select(frame :cv.typing.MatLike ,x :int ,y :int, square_size :int = 100) -> cv.typing.MatLike :
    '''Gets the full board and "slices" a specific square and returns it'''
    x_start = x * square_size
    y_start = y * square_size
    square = frame[y_start:y_start + square_size, x_start:x_start + square_size]
    #cv.imshow(f"SQUARE({x},{y})",square)
    return square

def _getMask(frame :cv.typing.MatLike) -> tuple[ cv.typing.MatLike , cv.typing.MatLike ] : #white,black
    '''Returns 2 masked images of board where one has only white another has black pices marked as white spots'''
    hsvImg = cv.cvtColor(frame,cv.COLOR_BGR2HSV)
    lowerBound_white = np.array([0,30,0])
    lowerBound_black = np.array([40,40,0])
    upperBound = np.array([179,255,255]) # same for boath

    blackPices = cv.inRange(hsvImg, lowerBound_black, upperBound)   
 
    whitePices =255- (cv.inRange(hsvImg, lowerBound_white, upperBound)) 

    return whitePices , blackPices

def getValue(frame :cv.typing.MatLike) -> list[list[str]] :       #use to get pices in board (only reads the colours and outs a 2d list)
    White , Black = _getMask(frame)
    threshold = 0.2
    Board_status = []
    for Y in range(8):
        row = []
        for X in range(8):
            Iw = _select(White, X,Y)
            Ib = _select(Black, X,Y)

            if (cv.countNonZero(Iw)/Iw.size) > threshold :
                row.append('W')
            elif (cv.countNonZero(Ib)/Ib.size) > threshold :
                row.append('B')
            else :
                row.append('_')

        Board_status.append(row)
    return Board_status

def drawGrid(image :cv.typing.MatLike ,gridColor :cv.typing.Scalar,  board_size :int = 800) -> cv.typing.MatLike :   # use to display the board with grid
    '''Returns image with drawn grid on it'''
    square_size = board_size // 8
    for i in range(1, 8):
        cv.line(image, (i * square_size, 0), (i * square_size, board_size), gridColor , 2)
        cv.line(image, (0, i * square_size), (board_size, i * square_size), gridColor , 2)
    return image

#example
if __name__ == "__main__" :
    cap = cv.VideoCapture(0)
    w = VedioCrop()

   
    while True: 
        _ , frame = cap.read()
        frame = w.getCroppedFrame(frame)

            #user controls
        key = cv.waitKey(1) & 0xFF
        match key :
            case x if x == ord('x') :      #crop vedio frame
                w.setSelection(frame)
            case q if q == ord('q'):      #quit
                break
            case c if c == ord('c') :     #get board detection result in current frame
                brd=getValue(frame)
                print("\nBoard pices colour pos:")
                [print(i) for i in brd ]
            case _ : pass
        

        cv.imshow("Display", drawGrid( frame, (0, 255, 0) ))    #display every frame with cropped board with grid

    cap.release()
    cv.destroyAllWindows()