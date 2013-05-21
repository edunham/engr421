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
#define pinMotor1 5
#define pinMotor2 2
#define pinMotor3 3

#define pinServo1 46
#define pinServo2 45
#define pinServo3 44

#define pinSolenoid1 4
#define pinSolenoid2 6
#define pinSolenoid3 7



// Parameters
/*******************************************************************************************/
#define DEBUG 0 //Defining DEBUG turns ON debugging messages

#define killMsgSend 1 //Prevents the arduino from sending the functional messages to the laptop

#define commsTimeout 200 //The maximum time that a received serial command can take, in mS

#define ballReleaseTime 20 //The time that the solenoid needs to be activated for to release a ball, in mS

#define angleLowest 30 //The minimum allowable angle
#define angleHighest 150 //The maximum allowable angle

#define motorLevel1 255 //PWM levls for the motors
#define motorLevel2 255
#define motorLevel3 255

#define offset1 0 //offset angles for each servo
#define offset2 0
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
const byte motorLevel[] = {
  0,motorLevel1,motorLevel2,motorLevel3}; //Individual PWM signal levels for each motor
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

  // Pin Modes and Setup
  /*******************************************************************************************/
  for (byte i=1;i<4;i++){
    pinMode(motorPins[i],OUTPUT);
    pinMode(solenoidPins[i],OUTPUT);

    analogWrite(motorPins[i],motorLevel[i]); //Set the PWM signal
    digitalWrite(solenoidPins[i],LOW);
  }



  // Other Setup Code
  /*******************************************************************************************/
  Serial.begin(9600);
  Serial.setTimeout(commsTimeout);
#if DEBUG==1
  Serial.println("Arduino Start");
#endif


  //Attach the servo objects
  servo1.attach(pinServo1,545,2455); //Include the maximum and minimum pulse widths.
  servo2.attach(pinServo2,545,2455);
  servo3.attach(pinServo3,545,2455);


  //Wait until 'Game Start' button is pressed

  //add here later
  //Send 'Game Start' message to laptop
  sendMessage(0x80);


  //Prototyping stuff DELETE ME!  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  //analogWrite(pinMotor1,0);

  //    releaseBall(1);

  //  while (true) { //Cycle endlessly
  //    setShooterAngle(1,90);
  //    delay(1000);
  //    setShooterAngle(1,45);
  //    delay(1000);
  //    setShooterAngle(1,135);
  //    delay(1000);
  //  }

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
    //The angle is invalid! Don't move the shooter, and send feedback
    sendMessage(0xE2,shooterNum,angle);
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

    ballReleaseTimer[shooterNum]=millis()+ballReleaseTime; //Set the timer for deactivating the solenoid
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
#if DEBUG==1
        Serial.print("Deactivating solenoid: ");
        Serial.println(i);
#endif
      }
    }
  }
}


/*▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
/*sendMessage
/*******************************************************************************************/
//This function sends commands to the laptop.  It has optional inputs.
void sendMessage (byte CMD,byte in1, byte in2, byte in3) {
#if killMsgSend==1
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



