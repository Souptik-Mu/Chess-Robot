// Row pins
const uint8_t rowPins[8] = {23, 22, 21, 19, 18, 17, 16, 15};
// Shift register pins (cols)
const uint8_t greenDataPin = 33;
const uint8_t greenClockPin = 32;
const uint8_t redDataPin = 13;
const uint8_t redClockPin = 12;
//buttons
const uint8_t buttonE = 14;
const uint8_t buttonW = 27;
const uint8_t buttonB = 26;
const uint8_t buttonH = 25;


bool lastButtonWState = HIGH;
bool lastButtonBState = HIGH;
bool lastButtonHState = HIGH;



bool green[8][8] = {
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1}
};

bool red[8][8] = {
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1},
    {1,1,1,1,1,1,1,1}
};
void updateDisplayMatrix() {
  for(uint8_t row = 0; row < 8; row++){
      uint8_t greenByte = 0 ,redByte = 0;

    for (int col = 0; col < 8; col++) {
      redByte   |= (red[row][col]   << (7 - col));
      greenByte |= (green[row][col] << (7 - col));
    }
    shiftOut(greenDataPin, greenClockPin, MSBFIRST, greenByte);
    shiftOut(redDataPin  , redClockPin  , MSBFIRST, redByte  );

    digitalWrite(rowPins[row], HIGH);
    delayMicroseconds(1000); 
    digitalWrite(rowPins[row], LOW);

  }

}

void clear(){
  for(int i = 0; i < 8; i++){
    for(int j = 0; j < 8; j++){
      green[i][j] = 0;
      red[i][j] = 0;
    }
  }
}
void handleButtonW() {
    Serial.println("request");

    while (Serial.available() == 0);  // Wait for move
    String move = Serial.readStringUntil('\n');
    move.trim();
    if(move == "non")
    {
      for(int i = 0; i < 8; i++)
        for(int j = 0; j < 8; j++)
          green[i][j] = 1;  //!?? should be red but somehow it works. 
    }
    else
    {
      int fromRow = move.charAt(2) - 'a';
      int fromCol = 8 - (move.charAt(3) - '0');
      int toRow = move.charAt(0) - 'a';
      int toCol = 8 - (move.charAt(1) - '0');

      red[fromRow][fromCol] = 1; // ekhaneo ulto a6
      green[toRow][toCol] = 1;
    }
}

void handleButtonB() {
  clear();
  Serial.println("read");
}

void handleButtonH() {
    Serial.println("help");

    while (Serial.available() == 0);  // Wait for move
    String moves = Serial.readStringUntil('\n');
    moves.trim();
    if(moves == "non")
    {
      for(int i = 0; i < 8; i++)
        for(int j = 0; j < 8; j++)
          green[i][j] = 1;  //!?? should be red but somehow it works. 
    }
    else
    {
      int srcRow = moves.charAt(0) - 'a';
      int srcCol = 8 - (moves.charAt(1) - '0');
      green[srcRow][srcCol] = 1; //! ulto a6, should be red. circuit works.

      for(int i = 2; i < moves.length() ; i += 2)
      {
        int dstRow = moves.charAt(i) - 'a';
        int dstCol = 8 - (moves.charAt(i+1) - '0');
          red[dstRow][dstCol] = 1;   //! should be green in board.
      }
    }
}
 
void setup() {
  Serial.begin(115200);

  for (int i = 0; i < 8; i++) {
    pinMode(rowPins[i], OUTPUT);
    digitalWrite(rowPins[i], LOW);
  }
  pinMode(greenDataPin, OUTPUT);
  pinMode(greenClockPin, OUTPUT);
  pinMode(redDataPin, OUTPUT);
  pinMode(redClockPin, OUTPUT);

  pinMode(buttonW,INPUT_PULLUP);
  pinMode(buttonB,INPUT_PULLUP);
  pinMode(buttonH,INPUT_PULLUP);

  //attachInterrupt(digitalPinToInterrupt(buttonW), handleButtonW, FALLING);
  //attachInterrupt(digitalPinToInterrupt(buttonB), handleButtonB, FALLING);

}

void loop() {

  updateDisplayMatrix();
  //delay(10); //100 (recomended value)
  //Serial.println(digitalRead(buttonW));

  bool readingW = digitalRead(buttonW);
  if (readingW != lastButtonWState) {
      if (lastButtonWState == HIGH && readingW == LOW) {
        handleButtonW();
        delay(200);
    }
  }
  lastButtonWState = readingW;

  // --- BUTTON B ---
  bool readingB = digitalRead(buttonB);
  if (readingB != lastButtonBState) {
      if (lastButtonBState == HIGH && readingB == LOW) {
        handleButtonB();
        delay(200);
    }
  }
  lastButtonBState = readingB;

  bool readingH = digitalRead(buttonH);
  if (readingH != lastButtonBState) {
      if (lastButtonHState == HIGH && readingH == LOW) {
        handleButtonH();
        delay(200);
    }
  }
  lastButtonHState = readingH;
  
}




