import customtkinter as ctk
import PIL.Image, PIL.ImageTk
import chess
import sys, os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class chessBoardFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.state = None
        self.canvasSize = min(parent.winfo_width(), parent.winfo_height())
        self.canvasSize -= (self.canvasSize // 10)
        self.piece_images = []
        # Load Chess Piece Images
        self.chessPices= {
            'b':  PIL.Image.open(resource_path("assets/B_B.png")) ,
            'k':  PIL.Image.open(resource_path("assets/B_K.png")) ,
            'n':  PIL.Image.open(resource_path("assets/B_N.png")) ,
            'p':  PIL.Image.open(resource_path("assets/B_P.png")) ,
            'q':  PIL.Image.open(resource_path("assets/B_Q.png")) ,
            'r':  PIL.Image.open(resource_path("assets/B_R.png")) ,
            'B':  PIL.Image.open(resource_path("assets/W_B.png")) ,
            'K':  PIL.Image.open(resource_path("assets/W_K.png")) ,
            'N':  PIL.Image.open(resource_path("assets/W_N.png")) ,
            'P':  PIL.Image.open(resource_path("assets/W_P.png")) ,
            'Q':  PIL.Image.open(resource_path("assets/W_Q.png")) ,
            'R':  PIL.Image.open(resource_path("assets/W_R.png")) 
        }
        self.draw_board()
        self.bind("<Configure>", self.on_resize)

    def draw_board(self):
        # Create Chessboard Frame
        for x in range(8):
            ctk.CTkLabel(self, text=str(8 - x)+"  " ).grid(row=x + 1, column=0, padx=5)
            ctk.CTkLabel(self, text=chr(65 + x)).grid(row=9, column=x + 1)

        self.boardCanvas = ctk.CTkCanvas(self,height=self.canvasSize, width=self.canvasSize, bg="#f2cfa2")
        self.boardCanvas.grid(row=1, column=1, rowspan=8, columnspan=8)

    def on_resize(self, event):
        """Update canvasSize dynamically when the parent is resized."""
        self.canvasSize = min(self.winfo_width(), self.winfo_height())
        self.canvasSize -= (self.canvasSize // 10)
        self.boardCanvas.config(width=self.canvasSize, height=self.canvasSize)
        self.draw_board()
        self.updateDisplayBoard(self.state)  # Pass the current board state here
    
    def updateDisplayBoard(self, board: chess.Board):
        """Updates the chessboard display with the current board state."""
        self.boardCanvas.delete("all")
        self.state = board
        tileSize = self.canvasSize // 8
        data = board.__str__().split()

        for row in range(8):
            for col in range(8):
                colour = "#f2cfa2" if (row + col) % 2 else "#be8158"
                x1, y1 = col * tileSize, row * tileSize
                x2, y2 = x1 + tileSize, y1 + tileSize
                self.boardCanvas.create_rectangle(x1, y1, x2, y2, fill=colour, outline="black")
                sq = data[row * 8 + col]
                if sq != '.' and sq in self.chessPices:
                    img = self.chessPices[sq].resize((tileSize,tileSize))
                    imgTk = PIL.ImageTk.PhotoImage(img)
                    self.piece_images.append(imgTk)
                    self.boardCanvas.create_image(x1 + tileSize / 2, y1 + tileSize / 2, image=imgTk)


class ChessMoveLog(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
    
        self.text_widget = ctk.CTkTextbox(self, font=("Lucida Calligraphy", 16), spacing3=5)
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        self.text_widget.configure(state="disabled")

        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.text_widget.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.line_counter = 1  

    def add_move(self, move, is_white=True):
        """Add a white move to the log."""
        self.text_widget.configure(state="normal")  
        if is_white:
            self.text_widget.insert("end", f"{self.line_counter}.    {move}\t".expandtabs(10))
        else:
            self.text_widget.insert("end", f"{move}\n")
            self.line_counter += 1
        self.text_widget.configure(state="disabled")
        self.text_widget.see("end")

    def clear(self):
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")  # Clear all text
        self.text_widget.configure(state="disabled")
        self.line_counter = 1  # Reset the move counter

def showInfo(title, message, command=None):
    dialog = ctk.CTkToplevel()
    #dialog.geometry("300x200")
    dialog.title(title)
    
    icon_path = resource_path("assets/image.png")
    icon_image = ctk.CTkImage(light_image=PIL.Image.open(icon_path),
                                dark_image=PIL.Image.open(icon_path),
                                size=(40, 40))
    # Add extra spaces in the text (after the icon) to create a gap.
    spaced_message = "   " + message  
    label = ctk.CTkLabel(dialog, 
                    text=spaced_message, 
                    image=icon_image, 
                    compound="left", 
                    wraplength=250,
                    font=("Comic Sans MS", 16))
        
    label.pack(pady=10, padx=20)
    
    if command:
        button = ctk.CTkButton(dialog, text="OK", command=lambda: (command(), dialog.destroy()))
    else:
        button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
    button.pack(pady=20)
    
    # Make the dialog modal
    dialog.grab_set()
    dialog.wait_window()