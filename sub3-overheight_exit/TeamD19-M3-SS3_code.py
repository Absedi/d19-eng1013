# This module contains the code for the over height exit
# Created By : Millie Blank
# Created Date: 26/8/2026
# Version ='7.0'

from pymata4 import pymata4
import time

board = pymata4.Pymata4()

# set polling rate
pollingRate = 0.1 # seconds

# Set pins for TL6
redTL6Pin = 7
yellowTL6Pin = 6
greenFlashPin = 5
greenTL6Pin = 4

# Configure pins
board.set_pin_mode_digital_output(redTL6Pin)
board.set_pin_mode_digital_output(yellowTL6Pin)
board.set_pin_mode_digital_output(greenTL6Pin)
board.set_pin_mode_digital_output(greenFlashPin)
print("Digital pin initialisation complete.")

# Declare variables to hold TL6 traffic time data
greenWait = 5 # num of seconds for light to remain green
yellowWait = 3 # num of seconds for light to remain yellow

# Set pins for US5
triggerPin = 3
echoPin = 2

# Declare variables to hold US5 data, 10:1 scale
maxVehicleHeight = 40 # cm
heightUS5 = 50 # cm, physical vertical height of US5

# Global variables
overheightVehicle = False
redLightOn = True
yellowLightOn = False
greenSolidOn = False
greenFlashOn = False
greenStart = 0
yellowStart = 0

def us5_callback(data):
    """
    Callback function that executes automatically when sonar data arrives.
    
    Parameters:
    data: list containing [pin_type, trigger_pin_number, distance_value (in cm), raw_time_stamp]

    Returns:
    None
    """
    global heightUS5, overheightVehicle
    distance = data[2]
    
    if heightUS5 - distance > maxVehicleHeight:
        overheightVehicle = True
    else:
        overheightVehicle = False


def main():
    '''
    Main function; handles the traffic light sequence for TL6, which depends on whether or not US5 detects an overheight vehicle.
    
    Parameters:
    None
    
    Returns:
    None
    '''

    global greenSolidOn, redLightOn, yellowLightOn, greenFlashOn, greenStart, yellowStart
    global overheightVehicle
    
    board.digital_write(redTL6Pin, 1) # Set TL6 to red at the beginning
    board.digital_write(greenTL6Pin, 0)
    board.digital_write(greenFlashPin, 0)

    # Configure pin mode as sonar
    board.set_pin_mode_sonar(triggerPin, echoPin, timeout=900000, callback=us5_callback)
    time.sleep(0.5) # small sleep to allow sonar to be configured correctly
    print("Trigger and echo pin initialisation complete.\nStarting program.")

    while True:
        if overheightVehicle == True and greenSolidOn == False: # US5 first detects an overheight vehicle
            board.digital_write(redTL6Pin, 0) # red light off
            redLightOn = False
            board.digital_write(yellowTL6Pin, 0) # yellow light off
            yellowLightOn = False
            board.digital_write(greenTL6Pin, 1) # green light on
            greenStart = time.time() # records the time that the green light turns on
            greenSolidOn = True

        elif overheightVehicle == False and greenSolidOn == True: # if vehicle leaves during solid green, go to yellow
            if (time.time() - greenStart >= greenWait):
                board.digital_write(greenTL6Pin, 0) # green light off
                greenSolidOn = False

                board.digital_write(yellowTL6Pin, 1) # yellow light on
                yellowStart = time.time()
                yellowLightOn = True

        elif overheightVehicle == False and yellowLightOn == True: # if TL6 is yellow, wait 3s then turn red
            if (time.time() - yellowStart >= yellowWait):
                board.digital_write(yellowTL6Pin, 0) # yellow light off
                yellowLightOn = False
                board.digital_write(redTL6Pin, 1) # red light on
                redLightOn = True

        if overheightVehicle == True and greenFlashOn == False: # if green light has been on for 5s seconds, flash green light
            if (time.time() - greenStart >= greenWait): # check if green light has been on for 5 secs on more 
                board.digital_write(greenTL6Pin, 0) # solid green light off
                greenSolidOn = False
                board.digital_write(greenFlashPin, 1) # green flash on
                greenFlashOn = True

        if overheightVehicle == False and greenFlashOn == True: # if vehicle leaves during flash, go straight to red
            board.digital_write(greenFlashPin, 0)
            greenFlashOn = False
            board.digital_write(greenTL6Pin, 0) # solid green light off
            greenSolidOn = False
            board.digital_write(yellowTL6Pin, 0) # yellow light off
            yellowLightOn = False
            board.digital_write(redTL6Pin, 1) # red light on
            redLightOn = True

        time.sleep(pollingRate) # wait then check again   

  
if __name__ == "__main__":
    try:
        main()   
    except KeyboardInterrupt:
        print("User Keyboard Interrupt - Exiting.") 
    finally: # finally block contains code that will run no matter what happens in the preceding try/except code
        board.shutdown() 
        print("\nBoard shut down successful.")   