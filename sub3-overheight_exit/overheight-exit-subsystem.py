# This module contains the code for the over height exit
# Created By : Millie Blank
# Created Date: 26/8/2026
# Version ='5.0'

from pymata4 import pymata4
import time

board = pymata4.Pymata4()

# set polling rate
pollingRate = 0.1 # seconds

# Set pins for TL6
redTL6Pin = 8
yellowTL6Pin = 9
greenTL6Pin = 10

# Configure pins
board.set_pin_mode_digital_output(redTL6Pin)
board.set_pin_mode_digital_output(yellowTL6Pin)
board.set_pin_mode_digital_output(greenTL6Pin)
print("Digital pin initialisation complete.")

# Declare variables to hold TL6 traffic time data
greenWait = 5 # num of seconds for light to remain green
yellowWait = 3 # num of seconds for light to remain yellow

# Set pins for US5
triggerPin = 11
echoPin = 12

# Declare variables to hold US5 data, 10:1 scale
maxVehicleHeight = 40 # cm
heightUS5 = 50 # cm, physical vertical height of US5

# Global variables
overheightVeh = False
redLightOn = True
yellowLightOn = False
greenLightOn = False
greenStart = 0
yellowStart = 0

def US5_callback(data):
    """
    Callback function that executes automatically when sonar data arrives.
    
    Parameters:
    data: list containing [pin_type, trigger_pin_number, distance_value (in cm), raw_time_stamp]

    Returns:
    None
    """
    global heightUS5, overheightVeh
    distance = data[2]
    
    if heightUS5 - distance > maxVehicleHeight:
        overheightVeh = True
    else:
        overheightVeh = False


def main():
    '''
    Main function; handles the traffic light sequence for TL6, which depends on whether or not US5 detects an overheight vehicle.
    
    Parameters:
    None
    
    Returns:
    Nones
    '''

    global greenLightOn, redLightOn, yellowLightOn, greenStart, yellowStart
    global overheightVeh
    
    # Set TL6 to red at the beginning
    board.digital_write(redTL6Pin, 1)

    # Configure pin mode as sonar
    board.set_pin_mode_sonar(triggerPin, echoPin, timeout=900000, callback=US5_callback)
    time.sleep(0.5) # small sleep to allow sonar to be configured correctly
    print("Trigger and echo pin initialisation complete.\nStarting program.")

    while True:
        if overheightVeh == True and greenLightOn == False: # US5 first detects an overheight vehicle
            board.digital_write(redTL6Pin, 0) # red light off
            redLightOn = False
            board.digital_write(yellowTL6Pin, 0) # yellow light off
            yellowLightOn = False
            board.digital_write(greenTL6Pin, 1) # green light on
            greenStart = time.time() # records the time that the green light turns on
            greenLightOn = True

        elif overheightVeh == False and greenLightOn == True: # US5 no longer detects on overheight vehicle, but green light still on
            if (time.time() - greenStart >= greenWait):
                board.digital_write(greenTL6Pin, 0) # green light off
                greenLightOn = False
                board.digital_write(yellowTL6Pin, 1) # yellow light on
                yellowStart = time.time()
                yellowLightOn = True
                
        elif overheightVeh == False and yellowLightOn == True: # US5 no longer detects on overheight vehicle, but yellow light still on
            if (time.time() - yellowStart >= yellowWait):
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