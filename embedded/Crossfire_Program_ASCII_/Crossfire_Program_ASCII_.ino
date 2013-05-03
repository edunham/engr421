//ENGR 421 Team 4
//2013

//Written by Dean Reading



/*******************************************************************************************/
// Changelog
/*******************************************************************************************
 * Version 0.1
 * 
 * 
 * 
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
#define pinMotor1 5
#define pinMotor2 2
#define pinMotor3 3

#define pinServo1 46
#define pinServo2 45
#define pinServo3 44

#define pinSolenoid1 255
#define pinSolenoid2 255
#define pinSolenoid3 255


// Parameters
/*******************************************************************************************/
#define DEBUG

#define commsTimeout 200 //The maximum time that a received serial command can take, in mS

#define ballReleaseTime 100 //The time that the solenoid needs to be activated for to release a ball, in mS

#define motorLevel1 255
#define motorLevel2 255
#define motorLevel3 255

// Libraries & Objects
/*******************************************************************************************/
#include <Servo.h>
Servo servo1; //Declare 3 instances of servo objects
Servo servo2;
Servo servo3;

// Constants
/*******************************************************************************************/
//const byte commandLength[] = {
//  0,2,1,0,0,0,0,0,0,0}; //The number of data bytes for each command type for serial comms\

byte commandLength[101];

const byte solenoidPins[] = {
  0,pinSolenoid1,pinSolenoid2,pinSolenoid3}; //A map for the solenoid pins
const byte motorPins[] = {
  0,pinMotor1,pinMotor2,pinMotor3}; //A map for the solenoid pins


// Global Variables
/*******************************************************************************************/
byte commandID=0;
byte bytesRemaining; //
char buffer[5];

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
  commandLength[32]=2;
  commandLength[92]=1;


  // Pin Modes and Setup
  /*******************************************************************************************/
  for (byte i=1;i<4;i++){
    pinMode(motorPins[i],OUTPUT);
    pinMode(solenoidPins[i],OUTPUT);

    analogWrite(motorPins[i],255);
    digitalWrite(solenoidPins[i],LOW);
  }



  // Other Setup Code
  /*******************************************************************************************/
  Serial.begin(9600);
  Serial.setTimeout(commsTimeout);
#ifdef DEBUG
  Serial.println("Arduino Start");
#endif


  //Attach the servo objects
  servo1.attach(pinServo1,900,2100); //Include the maximum and minimum pulse widths.
  servo2.attach(pinServo2,900,2100);
  servo3.attach(pinServo3,900,2100);


  //Wait until 'Game Start' button is pressed

  //add here later
  //Send 'Game Start' message to laptop
  Serial.print("GO");
  Serial.write(0x80); //Game start command


  //Set up the PWM DC motor control signals
  analogWrite(pinMotor1,motorLevel1);
  analogWrite(pinMotor2,motorLevel2);
  analogWrite(pinMotor3,motorLevel3);


  //Prototyping stuff DELETE ME!  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  analogWrite(pinMotor1,255);

//  setShooterAngle(1,128);
//  delay(2000);
//  setShooterAngle(1,255);
//  delay(2000);
//  setShooterAngle(1,1);
//  delay(2000);
//  setShooterAngle(1,128);


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

  //Check whether there are any solenoids that need to be deactivated
  for (byte i=1;i<4;i++){ //Check all 3 solenoids
    if (ballReleasing[i]==1){ //If a ball is currently being released
      if (millis()>ballReleaseTimer[i]){ //If enough time has passed
        digitalWrite(solenoidPins[i],LOW); //Deactivate the solenoid: close the passage
        ballReleasing[i]=0; //Indicate that the ball is no longer being released

#ifdef DEBUG
        Serial.print("Deactivating solenoid: ");
        Serial.println(i);
#endif
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
      while (!Serial.available()){
      } //Wait until another character is available
      if (Serial.read()=='O'){
        //Initialization Sequence detected!

#ifdef DEBUG
        Serial.println("'GO' found!");
#endif

        while (!Serial.available()){
        } //Wait until another character is available
        commandID=Serial.read(); //The next byte is the command ID

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
  case 32:
    //Aim shooter <db1> to angle defined by <db2>
    setShooterAngle(buffer[0]-48,(byte) buffer[1]);
    break;
  case 92:
    //Release a ball on shooter <db1>
    releaseBall(buffer[0]-48);
    break;
  default:
    Serial.print("Unrecognized command ID: ");
    Serial.println(commandID);
  }
}

/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*setShooterAngle
/*******************************************************************************************/
//This function changes the servo signal for shooter <shooterNum> to the angle defined by 
// <angle>.  <angle> is a byte that ranges from 180, which maps from 900 to 2100 mS.
void setShooterAngle(byte shooterNum, byte angle){
  
//  unsigned int output =   (((unsigned int) angle-1)*137)/29+900; // 137/29 = 4.724 = 1200/254, the scaling factor to get to uS

#ifdef DEBUG
  Serial.print("Setting shooter ");
  Serial.print(shooterNum);
  Serial.print(" to ");
  Serial.print(angle);
#endif

  //Set the servo output.  Use a switch statement to use the correct servo object.
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
    Serial.print("Unrecognized shooter Num: ");
    Serial.println(shooterNum);
  }
}

/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*releaseBall
/*******************************************************************************************/
//This function releases one BB (hopefully) from shooter <shooterNum>
void releaseBall(byte shooterNum) {

#ifdef DEBUG
  Serial.print("Releasing ball from shooter: ");
  Serial.println(shooterNum);
#endif

  digitalWrite(solenoidPins[shooterNum],HIGH); //Activate the solenoid: open the passage

  ballReleaseTimer[shooterNum]=millis()+ballReleaseTime; //Set the timer for deactivating the solenoid
  ballReleasing[shooterNum]=1; //Indicate that we are releasing a ball

}






