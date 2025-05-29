from src import * 
import cv2 as cv
import PIL.Image, PIL.ImageTk
import serial
import serial.tools.list_ports
import customtkinter as ctk
from tkinter import messagebox , BooleanVar


class Window(ctk.CTk):
    def __init__(self, camera: Camera):
        super().__init__()
        self.iconbitmap(resource_path("assets/ches.ico"))
        self.game = ChessGame()
        self.stored_frame = None
        # Set Theme
        ctk.set_appearance_mode("Dark")  # Light/Dark/System
        ctk.set_default_color_theme(resource_path("assets/Theme.json"))  # Theme color
        self.grid_color = ctk.ThemeManager.theme["CTkFrame"]["border_color"][0]    

        self.geometry("900x600")
        self.title("Chess Robot Interface")
        self.COMports = [port.device for port in serial.tools.list_ports.comports()]
        
        self.camera = camera
        self.ESP = None  # Serial connection to ESP
        
        self.create_widgets()
        self.OnEspInturrupt() # Start checking for ESP interrupts
    
    def create_widgets(self):
        self.controls = ctk.CTkFrame(self,height=100)
        self.controls.pack(side="top", fill="x", padx=10, pady=10)
        self.createControls()

        # Create Chessboard Frame
        self.displayBoard = chessBoardFrame(self)
        self.displayBoard.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Camera Display Frame
        self.camFrame = ctk.CTkFrame(self)
        self.camCanvas = ctk.CTkCanvas(self.camFrame)
        self.camCanvas.pack()
        self.camFrame.pack(fill="both", expand=True, padx=10, pady=10)

        # Move Log Frame
        self.moveLog = ChessMoveLog(self)
        self.moveLog.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)
        
        # Update Display
        self.displayBoard.updateDisplayBoard(self.game.board)
        self.updateCameraFeed()

    def createControls(self):   
        # Control Buttons
        self.select_butt = ctk.CTkButton(self.controls, text="Select Board", command=self.camera.setSelection)
        self.select_butt.pack(side="left", padx=5, pady=5)

        self.reset_butt = ctk.CTkButton(self.controls, text="Reset Camera", command=self.camera.clearSelection)
        self.reset_butt.pack(side="left", padx=5, pady=5)

        self.port_Select = ctk.CTkOptionMenu(self.controls, values=self.COMports , 
                                             variable= ctk.StringVar(value="Select Port"),command= self.setESP)
        self.port_Select.pack(side="left", padx=5, pady=5)

        self.loadFen = ctk.CTkButton(self.controls, text="FEN", command=self.loadFenString)
        self.loadFen.pack(side="left", padx=5, pady=5)

        #self.test_butt = ctk.CTkButton(self.controls, text="Test", command=self.GetMove)
        #self.test_butt.pack(side="left", padx=5, pady=5)
        self.resetgame = ctk.CTkButton(self.controls, text="Reset Game", command=self.gameReset)
        self.resetgame.pack(side="left", padx=5, pady=5)

        self.turn_switch_var = BooleanVar(value=True)
        self.turn_switch = ctk.CTkSwitch(self.controls, text="Turn", variable=self.turn_switch_var,
                                         onvalue=True, offvalue=False)
        
        
    def gameReset(self):
        self.game.board.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        self.displayBoard.updateDisplayBoard(self.game.board)
        self.moveLog.clear()

    def loadFenString(self):
        try:
            dialouge = ctk.CTkInputDialog(text="Enter FEN string:", title="FEN Input")
            fenString = dialouge.get_input()
            if not fenString:
                raise ValueError("FEN string cannot be empty")
            self.game.board.set_fen(fenString)
            self.displayBoard.updateDisplayBoard(self.game.board)
            self.moveLog.clear()
        except ValueError as e:
            print(f"Invalid FEN string: {e}")
            messagebox.showerror("Error", "Invalid FEN string.")

    def setESP(self, port):
        try:
            #self.ESP.close()
            self.ESP = serial.Serial(port, 115200)
            print(f"Connected to {port}")
        except serial.SerialException as e:
            print(f"Error connecting to {port}: {e}")

    def updateCameraFeed(self):
        frame = self.camera.getCurrentFrame()
        if frame is not None:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            frame = cv.resize(frame, (self.camCanvas.winfo_width(), self.camCanvas.winfo_height() ))
            frame = drawGrid(frame,self.grid_color, self.camCanvas.winfo_width(), self.camCanvas.winfo_height())  # Draw grid on the frame
            img = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))

            self.camCanvas.delete("all")
            self.camCanvas.create_image(0, 0, anchor="nw", image=img)
            self.camCanvas.camFeed = img  # Prevent garbage collection

        self.after(30, self.updateCameraFeed)  # Refresh every 30 ms

    def check_game_over(self):
        if self.game.board.is_game_over():    
            res = self.game.board.result()
            if res == "1/2-1/2":
                msg = "Draw"
            elif res == "1-0":
                msg = "White wins"
            elif res == "0-1":
                msg = "Black wins"
            else:
                msg = "Unknown result"
            showInfo("Game Over", f"Game over: {msg}!",command=self.gameReset)
    def OnEspInturrupt(self) : 
        if self.ESP is not None and self.ESP.is_open:
            try:
                if self.ESP.in_waiting > 0:
                    msg = self.ESP.readline().decode("utf-8", errors="replace").strip()
                    print("from ESP32: ", msg)
                    if msg == "request":
                        print("Requesting move...")
                        if self.GetMove() :
                            move_to_send = self.game.getNextMove()
                            if move_to_send:
                                self.moveLog.add_move(self.game.board.san(move_to_send), False)
                                self.game.board.push(move_to_send)
                                self.displayBoard.updateDisplayBoard(self.game.board)
                                self.ESP.write(move_to_send.uci().encode())
                                self.check_game_over()
                        else:
                            self.ESP.write("non".encode())
                            print("No valid move found")
                    if msg == "read":
                        self.updateFrame()
                    if msg == "help":
                        sqList = getVal(self.stored_frame, self.camera.getCurrentFrame())
                        destinations = self.game.getHelp(sqList)
                        if destinations == "":
                            self.ESP.write("non".encode())
                        else:
                            self.ESP.write(destinations.encode())
                    if msg == "resign":
                        showInfo("Game Over", f"White resigned: Black wins!",command=self.gameReset)
                        
            except serial.SerialException as e:
                print(f"Serial Error: {e}")
            
        self.after(200, self.OnEspInturrupt)
    
    def GetMove(self):
        ret = False
        try:
            if self.stored_frame is not None:
                sqList = getVal(self.stored_frame, self.camera.getCurrentFrame())
                move , isValid = self.game.updateBoard(sqList)
                if isValid and move is not None:
                    self.moveLog.add_move(self.game.board.san(move) , True)
                    self.game.board.push(move)
                    self.displayBoard.updateDisplayBoard(self.game.board)
                    print("Move found:", move)
                    ret = True
                    self.check_game_over()
                else:
                    raise ValueError("No valid move found")      
        except Exception as e:
            #messagebox.showerror("Error", "Failed to detect a valid move.")
            print(f"Error: {e}")
        finally:
            self.updateFrame()
            return ret
    
    def updateFrame(self):
        self.stored_frame = self.camera.getCurrentFrame()





if __name__ == "__main__":
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    cam = Camera(cap)
    win = Window(cam)
    win.mainloop()