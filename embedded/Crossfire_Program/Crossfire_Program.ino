//ENGR 421 Team 4
//2013

//Written by Dean Reading



/*******************************************************************************************/
// Changelog
/*******************************************************************************************
 * Version control can now be handled by GitHub...
 *
 * Version 0.2
 * Included a timeout when waiting for a character.
 * Added the sendMessage function to communicate with laptop.
 * Added in error messages for invalid command IDs, shooter numbers and angles.
 * Added in lower and upper limits to the angles that can be used. 
 * 
 * 
 * Version 0.1
 * Includes command receiving and execution, with 'Aim' and 'Shoot' commands.
 * <angle> input is a byte that should range from 0 to 180, with 90 being pointing forward.
 * All DC motor pins are set up and PWM is created.
 * setShooterAngle, releaseBall and checkSolenoids functions are included.
 * 'GO' & 0x80 is sent to indicate game start.
 *
 * 
 */

/*
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 // Pre-Start
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 */


// Pins
/*******************************************************************************************/
//Motors
#define pinMotor1 5
#define pinMotor2 2
#define pinMotor3 3

#define pinServo1 46
#define pinServo2 45
#define pinServo3 44

#define pinSolenoid1 4
#define pinSolenoid2 6
#define pinSolenoid3 7

//Interface Panel
#define pinPot A0

#define pinLEDY1 26
#define pinLEDY2 24
#define pinLEDY3 22

#define pinLEDR 30
#define pinLEDB 32
#define pinLEDG 28

#define pinButton1 20
#define pinButton2 19
#define pinButton3 18

#define pinConfig1 17
#define pinConfig2 21


// Programmable Parameters
/*******************************************************************************************/
#define DEBUG 1 //Defining DEBUG turns ON debugging messages

#define killMsgSend 0 //Prevents the arduino from sending the functional messages to the laptop

#define commsTimeout 200 //The maximum time that a received serial command can take, in mS

#define ballReleaseTime1 35 //The time that the solenoid needs to be activated for to release a ball, in mS
#define ballReleaseTime2 28
#define ballReleaseTime3 35

//#define ballReleaseInt floor((ballReleaseTime1*125)/8) //The number of 64uS needed to get to ballReleaseTime


#define angleLowest 30 //The minimum allowable angle
#define angleHighest 150 //The maximum allowable angle

#define motorLevel1 255 //PWM levls for the motors
#define motorLevel2 255
#define motorLevel3 255

#define offset1 -3 //offset angles for each servo
#define offset2 -4
#define offset3 0

// Libraries & Objects
/*******************************************************************************************/
#include <Servo.h>
Servo servo1; //Declare 3 instances of servo objects
Servo servo2;
Servo servo3;

//Function Prototypes
void sendMessage (byte CMD,byte in1 = 255, byte in2 = 255, byte in3 = 255);

// Constants
/*******************************************************************************************/
byte commandLength[255]; //The number of data bytes for each command type for serial comms
const byte solenoidPins[] = {
  0,pinSolenoid1,pinSolenoid2,pinSolenoid3}; //A map for the solenoid pins
const byte motorPins[] = {
  0,pinMotor1,pinMotor2,pinMotor3}; //A map for the solenoid pins
const byte ledPinsY[] = {
  0,pinLEDY1,pinLEDY2,pinLEDY3}; //A map for the yellow LEDs
const byte ledPins[] = {
  0,pinLEDR,pinLEDB,pinLEDG}; //A map for the R B and G LEDs
const byte buttonPins[] = {
  0,pinButton1,pinButton2,pinButton3}; //A map for the three momentary buttons

const byte OCIE4[] = {
  0, OCIE4A, OCIE4B, OCIE4C}; //A map for the locations of the output compare interrupt enable bit locations
volatile byte *ptrOCR4H[] = {
  0, &OCR4AH, &OCR4BH, &OCR4CH}; //Maps for the locations of the high and low output compare value byte locations
volatile byte *ptrOCR4L[] = {
  0, &OCR4AL, &OCR4BL, &OCR4CL};
volatile boolean buttonPressed[] = {
  0, 0, 0, 0};
unsigned long lastButtonPress; //Saves the last time that a button was pressed

const byte motorLevel[] = {
  0,motorLevel1,motorLevel2,motorLevel3}; //Individual PWM signal levels for each motor
#define mStoInt(x) ((unsigned int) floor((x*125)/8)) //The number of 64uS needed to get to ballReleaseTime
const unsigned int ballReleaseInt[] = {
  0, mStoInt(ballReleaseTime1), mStoInt(ballReleaseTime2), mStoInt(ballReleaseTime3)};
char offset[] = {
  0,offset1,offset2,offset3}; //servo offsets


// Global Variables
/*******************************************************************************************/
byte commandID=0;
byte bytesRemaining; //
char buffer[5];
unsigned long timer; //A multi-purpose timer

unsigned long ballReleaseTimer[4]; //Saves when the last ball was released.
boolean ballReleasing[] = {
  0,0,0,0}; //Indicates whether we are in the process of releasing a ball

/*
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 // Setup
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 */
void setup(){

  // Constants
  /*******************************************************************************************/
  commandLength[1]=2;
  commandLength[2]=1;
  commandLength[3]=2;

  commandLength[0x80]=0;
  commandLength[0xE0]=1;
  commandLength[0xE1]=1;
  commandLength[0xE2]=2;

  // Timer Setup
  /*******************************************************************************************/
  //Set timer 4 to Normal mode, clock prescaler of 1024, other parameters
  TCCR4A = B00000000;
  TCCR4B = B00000101;
  interrupts(); //Enable interrupts
  //NOTE: This must be run BEFORE using delaying commangs.  If this is run after a certain
  //amount of time, the interrupts don't function correctly.

  // Pin Modes and Setup
  /*******************************************************************************************/
  for (byte i=1;i<4;i++){
    pinMode(motorPins[i],OUTPUT);
    pinMode(solenoidPins[i],OUTPUT);

    analogWrite(motorPins[i],motorLevel[i]); //Set the PWM signal for the motor
    digitalWrite(solenoidPins[i],LOW); //Ensure the solenoid is low

    pinMode(ledPins[i],OUTPUT); //Set the LED pins as outputs
    pinMode(ledPinsY[i],OUTPUT);
    pinMode(buttonPins[i],INPUT_PULLUP); //Set the button pins as inputs pulled high
  }

  //Set the config switch pins as inputs pulled high
  pinMode(pinConfig1,INPUT_PULLUP);
  pinMode(pinConfig2,INPUT_PULLUP);

  // Button Interrupts
  /*******************************************************************************************/
  attachInterrupt(3,ISR_B1,LOW); //Pin 20
  attachInterrupt(4,ISR_B2,LOW); //Pin 19
  attachInterrupt(5,ISR_B3,LOW); //Pin 18

  // Other Setup Code
  /*******************************************************************************************/
  Serial.begin(9600);
  Serial.setTimeout(commsTimeout);
#if DEBUG==1
  Serial.println("Arduino Start");
#endif


  //Attach the servo objects
  servo1.attach(pinServo1,429,2571); //Include the maximum and minimum pulse widths.
  servo2.attach(pinServo2,429,2571);
  servo3.attach(pinServo3,429,2571);


  //Run a test pattern on the LEDs


  float num = 200; //mS
  for (byte i=0;i<6;i++){
    for (byte z=1;z<4;z++){
      digitalWrite(ledPinsY[z],HIGH);
      delay(num);
      num=num*0.93;
      digitalWrite(ledPinsY[z],LOW);
    }
    for (byte z=3;z>0;z--){
      digitalWrite(ledPins[z],HIGH);
      delay(num);
      num=num*0.93;
      digitalWrite(ledPins[z],LOW);
    }
  }




  //Set all servos to 90 degrees
  servo1.write(90+offset[1]);
  servo2.write(90+offset[2]);
  servo3.write(90+offset[3]);

  //Wait until 'Game Start' button is pressed
  //add here later
  //Send 'Game Start' message to laptop
  sendMessage(0x80);

}


/*
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 // Loop
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 */
void loop(){
  checkSerial(); //Check for incoming commands, and execute them


  checkButtons();

}

/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*checkButtons
/*******************************************************************************************/
void checkButtons(){
  for (byte i=1; i<4; i++) {
    if (buttonPressed[i]==1) {
      buttonPressed[i]=0;
      //Only accept the button press if there hasn't been one in the last 100mS
      if ((millis()-lastButtonPress)>100){
        lastButtonPress=millis();
        //Perform Action Here
        releaseBall(i);
      }
    }
  } 
}
/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*checkSerial
/*******************************************************************************************/
void checkSerial(){
  if (Serial.available()) {
    //Search for the initization sequence
    if (Serial.read()=='G'){
      timer=millis()+commsTimeout;
      while (!Serial.available()){ //Wait until another character is available
        if (millis()>timer) { //Exit the loop if we don't receive another character
          break;
        }
      } 
      if (Serial.peek()=='O'){
        Serial.read(); //Remove the 'O' from the serial buffer.
        //Initialization Sequence detected!

#if DEBUG==1
        Serial.println("'G O' found!");
#endif

        timer=millis()+commsTimeout;
        while (!Serial.available()){ //Wait until another character is available
          if (millis()>timer) { //Exit the loop if we don't receive another character
            break;
          }
        } 
        commandID=Serial.read(); //This byte is the command ID

        //Now, read the required number of data bytes into the array 'buffer'
        Serial.readBytes(buffer,commandLength[commandID]);

        //Execute the command
        executeCommand();
      }
    }
  }
}


/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*executeCommand
/*******************************************************************************************/
//This function executes whatever the necessary action is, as told by the command and data
//received through serial comms
void executeCommand(){
  switch (commandID){
  case 1:
    //Aim shooter <db1> to angle defined by <db2>
    setShooterAngle(buffer[0],(byte) buffer[1]);
    break;
  case 2:
    //Release a ball on shooter <db1>
    releaseBall(buffer[0]);
    break;
  case 3:
    //Change servo angle offset
    offset[buffer[0]]=(char) buffer[1]; //Changed to a signed byte
  default:
#if DEBUG==1
    Serial.print("Unrecognized command ID: ");
    Serial.println(commandID);
#endif
    //Send error feedback to laptop
    sendMessage(0xE0,commandID);
    digitalWrite(ledPinsY[1],HIGH); //Light up the error LED
  }
}

/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*setShooterAngle
/*******************************************************************************************/
//This function changes the servo signal for shooter <shooterNum> to the angle defined by 
// <angle>.  <angle> is a byte that ranges from 180, which maps from 900 to 2100 mS.
void setShooterAngle(byte shooterNum, byte angle){

  //  unsigned int output =   (((unsigned int) angle-1)*137)/29+900; // 137/29 = 4.724 = 1200/254, the scaling factor to get to uS

#if DEBUG==1
  Serial.print("Setting shooter ");
  Serial.print(shooterNum);
  Serial.print(" to ");
  Serial.println(angle);
#endif


  //Set the servo output.  Use a switch statement to use the correct servo object.
  if (angle<angleLowest || angle>angleHighest) {
    //The angle is invalid! Don't move the shooter, and send error feedback
    sendMessage(0xE2,shooterNum,angle);
    digitalWrite(ledPinsY[3],HIGH); //Light up the error LED
  }
  else{
    //Apply the angle offset
    angle += offset[shooterNum];
    switch (shooterNum) {
    case 1:
      servo1.write(angle);
      break;
    case 2:
      servo2.write(angle);
      break;
    case 3:
      servo1.write(angle);
      break;
    default:
#if DEBUG==1
      Serial.print("Unrecognized shooter Num: ");
      Serial.println(shooterNum);
#endif
      //Send unrecognized shooter num feedback to laptop
      sendMessage(0xE1,shooterNum);
      digitalWrite(ledPinsY[2],HIGH); //Light up the error LED
    }
  }
}

/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*releaseBall
/*******************************************************************************************/
//This function releases one BB (hopefully) from shooter <shooterNum>
void releaseBall(byte shooterNum) {

#if DEBUG==1
  Serial.print("Releasing ball from shooter: ");
  Serial.println(shooterNum);
#endif
  if (shooterNum<1 || shooterNum>3) { //Check that the shooter number is valid
#if DEBUG==1
    Serial.print("Unrecognized shooter Num: ");
    Serial.println(shooterNum);
#endif
    //Send unrecognized shooter num feedback to laptop
    sendMessage(0xE1,shooterNum);
  }
  else {
    digitalWrite(solenoidPins[shooterNum],HIGH); //Activate the solenoid: open the passage
    digitalWrite(ledPins[shooterNum],HIGH); //Turn on the respective LED

    //With interrupts, set the timed interrupt
    timedInterrupt(shooterNum, ballReleaseInt[shooterNum]); //Should be 547 for 35mS
  }
}


/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*timedInterrupt
/*******************************************************************************************/
//timerNum tells whether to use Output Compare A, B or C (for shooters 1, 2 or 3)
//time tells the amount of time to set it for, in multiples of 62 uS. 547 gives 35mS.
void timedInterrupt(byte timerNum, unsigned int time){

  //Grab the current count from the timer
  unsigned int count = TCNT4L; //Read the low byte first;
  count += TCNT4H*256;
  //Add the time we wish to find
  
  count += time; //Set the the value entered

  //Set the value of count into the output compare registers
  *ptrOCR4H[timerNum] = count>>8; //High byte first
  *ptrOCR4L[timerNum] = count; //The low byte

  //Turn on interrupts for output compare on the required timer
  TIMSK4 |= _BV(OCIE4[timerNum]);

}

/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*sendMessage
/*******************************************************************************************/
//This function sends commands to the laptop.  It has optional inputs.
void sendMessage (byte CMD,byte in1, byte in2, byte in3) {
#if killMsgSend==0
  Serial.print("GO");
  if (commandLength[CMD]>0){
    Serial.print(in1);
    if (commandLength[CMD]>1){
      Serial.print(in2);
      if (commandLength[CMD]>2){
        Serial.print(in3);
      }
    }
  }
  Serial.println(); //Print a new line character
#endif
}

/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*Timer Interrupt Service Routines
/*******************************************************************************************/
ISR(TIMER4_COMPA_vect){
  //Turn off the interrupts
  TIMSK4 &= 255 - _BV(OCIE4A);

  digitalWrite(solenoidPins[1],LOW); //Deactivate the solenoid: close the BB passage
  digitalWrite(ledPins[1],LOW); //Turn off the respective LED
#if DEBUG==1
  Serial.println("Deactivating solenoid: 1");
#endif
}

ISR(TIMER4_COMPB_vect){
  //Turn off the interrupts
  TIMSK4 &= 255 - _BV(OCIE4B);

  digitalWrite(solenoidPins[2],LOW); //Deactivate the solenoid: close the BB passage
  digitalWrite(ledPins[2],LOW); //Turn off the respective LED
#if DEBUG==1
  Serial.println("Deactivating solenoid: 2");
#endif
}

ISR(TIMER4_COMPC_vect){
  //Turn off the interrupts
  TIMSK4 &= 255 - _BV(OCIE4C);

  digitalWrite(solenoidPins[3],LOW); //Deactivate the solenoid: close the BB passage
  digitalWrite(ledPins[3],LOW); //Turn off the respective LED
#if DEBUG==1
  Serial.println("Deactivating solenoid: 3");
#endif
}


/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*Button Interrupt Service Routines
/*******************************************************************************************/
void ISR_B1(){
  buttonPressed[1]=1;
}

void ISR_B2(){
  buttonPressed[2]=1;
}

void ISR_B3(){
  buttonPressed[3]=1;
}


