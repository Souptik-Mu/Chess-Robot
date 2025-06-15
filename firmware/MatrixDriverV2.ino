// Code with a secret mode to play snake

// Row pins
const uint8_t rowPins[8] = {23, 22, 21, 19, 18, 17, 16, 15};
// Shift register pins (cols)
const uint8_t greenDataPin = 33;
const uint8_t greenClockPin = 32;
const uint8_t redDataPin = 13;
const uint8_t redClockPin = 12;
//button pins
const uint8_t buttonW = 14;
const uint8_t buttonH = 27;
const uint8_t buttonR = 26;
const uint8_t buttonB = 25;
// SnakeGame Data (Hidden Mode)
bool SnakeMode = false;
int8_t dx = 0;  int8_t dy = 0;
uint8_t SnakeX[60]; uint8_t SnakeY[60];
uint8_t SnakeL = 0;
uint8_t FoodX;  uint8_t FoodY;
unsigned long lastMoveTime = 0;
//Button states
bool lastButtonWState = HIGH;
bool lastButtonHState = HIGH;
bool lastButtonRState = HIGH;
bool lastButtonBState = HIGH;


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
void SetPixel(int x, int y, bool r , bool g){
  green[x][y] = r;
  red[x][y] = g;
  //ulto a6
}
void SetAll(int R,int G){
  for(int i = 0; i < 8; i++){
    for(int j = 0; j < 8; j++){
      green[i][j] = R;
      red[i][j] = G;
    }
  }
}
void handleButtonW() {
    Serial.println("request");

    while (Serial.available() == 0);  // Wait for move
    String move = Serial.readStringUntil('\n');
    move.trim();

    if(move == "non")
      SetAll(1,0);
    else
    {
      int fromRow = move.charAt(2) - 'a';
      int fromCol = 8 - (move.charAt(3) - '0');
      int toRow = move.charAt(0) - 'a';
      int toCol = 8 - (move.charAt(1) - '0');

      SetPixel(fromRow, fromCol, false , true);
      SetPixel(toRow, toCol, true, false);
    }
}

void handleButtonB() {
  SetAll(0,0);
  Serial.println("read");
}

void handleButtonR() {
  SetAll(0,1);
  Serial.println("resign");
}

void handleButtonH() {
  Serial.println("help");

  while (Serial.available() == 0);  // Wait for move
  String moves = Serial.readStringUntil('\n');
  moves.trim();
  if(moves == "non")
    SetAll(1,0);  
  else
  {
    int srcRow = moves.charAt(0) - 'a';
    int srcCol = 8 - (moves.charAt(1) - '0');
    SetPixel(srcRow,srcCol, true , false); //should be red. circuit works.

    for(int i = 2; i < moves.length() ; i += 2)
    {
      int dstRow = moves.charAt(i) - 'a';
      int dstCol = 8 - (moves.charAt(i+1) - '0');
        SetPixel(dstRow,dstCol, false , true);//! should be green in board.
        
    }
  }
}

void ReadInput(){
  //Buttons are arranged Right to Left

    // ---- BUTTON W ---- (White)(RIGHT) [No-4]
  bool readingW = digitalRead(buttonW);
  if (readingW != lastButtonWState) {
      if (lastButtonWState == HIGH && readingW == LOW) {
        if(SnakeMode)
        {dx = 0; dy = +1;}
        else
          handleButtonW();
        delay(200);
    }
  }
  lastButtonWState = readingW;

  // ---- BUTTON H ---- (Help)(LEFT)  [No-3]
  bool readingH = digitalRead(buttonH);
  if (readingH != lastButtonHState) {
      if (lastButtonHState == HIGH && readingH == LOW) {
        if(SnakeMode)
        {dx = 0; dy = -1;}
        else
          handleButtonH();
        delay(200);
    }
  }
  lastButtonHState = readingH;

  // ---- BUTTON R ---- (Resign)(DOWN) [No-2]
  bool readingR = digitalRead(buttonR);
  if (readingR != lastButtonRState) {
      if (lastButtonRState == HIGH && readingR == LOW) {
        if(SnakeMode)
        {dx = -1; dy = 0;}
        else
          handleButtonR();
        delay(200);
    }
  }
  lastButtonRState = readingR;

  // ---- BUTTON B ---- (Black)(UP) [No-1]
  bool readingB = digitalRead(buttonB);
  if (readingB != lastButtonBState) {
      if (lastButtonBState == HIGH && readingB == LOW) {
        if(SnakeMode)
        {dx = +1; dy = 0;}
        else
          handleButtonB();
        delay(200);
    }
  }
  lastButtonBState = readingB;
}

void InitSnake(){
  digitalWrite(LED_BUILTIN, LOW);
  dx = 0; dy = 0;
  SnakeL = 2;
  FoodX = 6; FoodY = 4;

  SnakeX[0] = 4; SnakeY[0] = 3;
  SnakeX[1] = 3; SnakeY[1] = 3;

}
void GameLoop(){
  //Snake movement
  for(uint8_t i = SnakeL ; i > 0 ; i--){    //Make body follow head
    SnakeX[i] = SnakeX[i-1];
    SnakeY[i] = SnakeY[i-1];
  }
  SnakeX[0] = (SnakeX[0] + dx + 8) % 8;
  SnakeY[0] = (SnakeY[0] + dy + 8) % 8;
  //SnakeX[0] += dx;
  //SnakeY[0] += dy;

  //self collision check
  for(uint8_t i = SnakeL ; i > 0 ; i--){
    if( (SnakeX[0] == SnakeX[i]) && (SnakeY[0] == SnakeY[i]) ){
      //GameOver
      digitalWrite(LED_BUILTIN, HIGH);
      delay(3000);
      InitSnake();
      break;
    }
  }
  //food - collision check & genatation
  if( (SnakeX[0] == FoodX) && (SnakeY[0] == FoodY) ){ 
    SnakeL ++;
    FoodX = random(0,8);
    FoodY = random(0,8);
  }

  //draw screen
  SetAll(0,0);
  SetPixel(FoodX, FoodY, true, true); // draw food
  SetPixel(SnakeX[0], SnakeY[0], true, false); // draw head
  for(uint8_t i = SnakeL ; i > 0 ; i--) //draw body
    SetPixel(SnakeX[i], SnakeY[i], false , true);

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
  pinMode(buttonH,INPUT_PULLUP);
  pinMode(buttonR,INPUT_PULLUP);
  pinMode(buttonB,INPUT_PULLUP);

  if(digitalRead(buttonR) == LOW){ // Press the left most button while booting to enter snake mode
    SnakeMode = true;
    InitSnake();
  }
  //Serial.print("mode: ");
  //Serial.println(SnakeMode);
}

void loop() {
  updateDisplayMatrix();
  
  ReadInput();

  if(SnakeMode && ((dx ^ dy) != 0)){
    unsigned long now = millis();
    if (now - lastMoveTime >= 1000) {
      GameLoop(); // Move snake only at interval // getting same effect as yeild
      lastMoveTime = now;
    }
  }
  
  
}
