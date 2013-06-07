//ENGR 421 Team 4
//2013

//Written by Dean Reading



/*******************************************************************************************/
// Changelog
/*******************************************************************************************
 * Version control can now be handled by GitHub
 *
 * Version 1
 * Program written
 * Each shooter can be aimed
 * Each shooter can be fired
 * Each motor can be turned on or off
 * Instructions are printed at startup
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

// Parameters
/*******************************************************************************************/

#define commsTimeout 200 //The maximum time that a received serial command can take, in mS

#define ballReleaseTime1 35 //The time that the solenoid needs to be activated for to release a ball, in mS
#define ballReleaseTime2 28
#define ballReleaseTime3 24

#define motorLevel1 189 //PWM levls for the motors
#define motorLevel2 185
#define motorLevel3 187

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
const byte motorLevel[] = {
  0,motorLevel1,motorLevel2,motorLevel3}; //Individual PWM signal levels for each motor
const unsigned int ballReleaseTime[] = {
  0, ballReleaseTime1, ballReleaseTime2, ballReleaseTime3};
char offset[] = {
  0,offset1,offset2,offset3}; //servo offsets


// Global Variables
/*******************************************************************************************/
unsigned long timer; //A multi-purpose timer

char StringIn[10]; //Used to store serial characters in


unsigned long ballReleaseTimer[4]; //Saves when the last ball was released.
boolean ballReleasing[] = {
  0,0,0,0}; //Indicates whether we are in the process of releasing a ball

//For button pressing:
volatile boolean buttonPressed[] = {
  0, 0, 0, 0};
unsigned long lastButtonPress; //Saves the last time that a button was pressed

/*
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 // Setup
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 */
void setup(){


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

  Serial.println("Arduino Start");
  Serial.println(F("This program controls the three shooters from typed serial commands"));
  Serial.println(F("To set shooter shooter 3 to 111 degrees, type: '3 111'"));
  Serial.println(F("To shoot a ball on shooter 1, type: '1 s'"));
  Serial.println(F("To stop the motor on shooter 2, type: '2 x'"));
  Serial.println(F("To start the motor on shooter 2, type: '2 m'\n"));


  //Attach the servo objects
  servo1.attach(pinServo1,429,2571); //Include the maximum and minimum pulse widths.
  servo2.attach(pinServo2,429,2571);
  servo3.attach(pinServo3,429,2571);


  //Set all servos to 90
  servo1.write(90+offset[1]);
  servo2.write(90+offset[2]);
  servo3.write(90+offset[3]);

  interrupts(); //Allow interrupts
}


/*
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 // Loop
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
 */
void loop(){
  checkSerial(); //Check for incoming commands, and execute them

  checkSolenoids(); //Deactivates any solenoids when needed

  checkButtons(); //Check if any actions need to be performed based on buttons pressed

}


/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*checkSerial
/*******************************************************************************************/
void checkSerial(){
  //Check for input
  if (Serial.available()){
    delay(100);

    char FirstChar=Serial.read(); //Get the first character

    //Get the rest of the string, except for the '=' sign
    byte i=0;

    Serial.read(); //Waste one character
    while (Serial.available()){
      StringIn[i++]=Serial.read();
    }
    StringIn[i]='\0'; //String null terminator

    //Serial.println(StringIn);


    //Set the new value and print out the result to confirm
    switch (FirstChar) {
    case 'A':
    case 'a':
    case '1':

      executeCommand(1);
      break;

    case 'B':
    case 'b':
    case '2':
      executeCommand(2);
      break;

    case 'C':
    case 'c':
    case '3':
      executeCommand(3);
      break;

    default:
      Serial.println("First character not recognized");
    }


  }
}

/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*executeCommand
/*******************************************************************************************/
//This function executes whatever the necessary action is, as told by the command and data
//received through serial comms
void executeCommand(byte shooterNum){
  switch (StringIn[0]){
  case 'S':
  case 's':
    releaseBall(shooterNum);
    break;

  case 'M':
  case 'm':
    Serial.print("Turning on motor: ");
    Serial.println(shooterNum);
    analogWrite(motorPins[shooterNum],motorLevel[shooterNum]);
    break;

  case 'X':
  case 'x':
    Serial.print("Turning off motor: ");
    Serial.println(shooterNum);
    analogWrite(motorPins[shooterNum],0);
    break;

  default: //If the string isn't 's' or 'm', is it assumed ot be a number, corresponding to an angle
    setShooterAngle(shooterNum,atof(StringIn));

    //To change the motor level isntead of the servo angle:
    /*
    analogWrite(motorPins[shooterNum],atof(StringIn)); // #############################################################################
    Serial.print("Motor ");
    Serial.print(shooterNum);
    Serial.print(" set to ");
    Serial.println(atof(StringIn));
*/

  }
}


/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*setShooterAngle
/*******************************************************************************************/
//This function changes the servo signal for shooter <shooterNum> to the angle defined by 
// <angle>.  <angle> is a byte that ranges from 180, which maps from 900 to 2100 mS.
void setShooterAngle(byte shooterNum, byte angle){

  //  unsigned int output =   (((unsigned int) angle-1)*137)/29+900; // 137/29 = 4.724 = 1200/254, the scaling factor to get to uS


  Serial.print("Setting shooter ");
  Serial.print(shooterNum);
  Serial.print(" to ");
  Serial.println(angle);



  //Set the servo output.  Use a switch statement to use the correct servo object.

  //Apply the angle offset
  int out = angle + offset[shooterNum];
  switch (shooterNum) {
  case 1:
    servo1.write(out);
    break;
  case 2:
    servo2.write(out);
    break;
  case 3:
    servo3.write(out);
    break;
  default:

    Serial.print("Unrecognized shooter Num: ");
    Serial.println(shooterNum);
  }
}

/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*releaseBall
/*******************************************************************************************/
//This function releases one BB (hopefully) from shooter <shooterNum>
void releaseBall(byte shooterNum) {

  Serial.print("Releasing ball from shooter: ");
  Serial.println(shooterNum);

  if (shooterNum<1 || shooterNum>3) { //Check that the shooter number is valid
    Serial.print("Unrecognized shooter Num: ");
    Serial.println(shooterNum);

  }
  else{
    digitalWrite(solenoidPins[shooterNum],HIGH); //Activate the solenoid: open the passage

    ballReleaseTimer[shooterNum]=millis()+ballReleaseTime[shooterNum]; //Set the timer for deactivating the solenoid
    ballReleasing[shooterNum]=1; //Indicate that we are releasing a ball
  }
}


/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*checkSolenoids
/*******************************************************************************************/
//Check whether there are any solenoids that need to be deactivated
void checkSolenoids(){
  for (byte i=1;i<4;i++){ //Check all 3 solenoids
    if (ballReleasing[i]==1){ //If a ball is currently being released
      if (millis()>ballReleaseTimer[i]){ //If enough time has passed
        digitalWrite(solenoidPins[i],LOW); //Deactivate the solenoid: close the passage
        ballReleasing[i]=0; //Indicate that the ball is no longer being released

        Serial.print("Deactivating solenoid: ");
        Serial.println(i);

      }
    }
  }
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







