"""
This module contains the code for approach height detection (subsystem 1)
Team: D19
Author: Pooja Sai Shruthika Medisetti
Created on: 31-08-2026
Version: 4.0
"""

import time
from pymata4 import pymata4

#pin configurations:
US1_TRIG_PIN = 2
US1_ECHO_PIN = 3

TL1_RED_PIN = 5
TL1_YELLOW_PIN = 6
TL1_GREEN_PIN = 7

US2_TRIG_PIN = 9
US2_ECHO_PIN = 10

TL2_RED_PIN = 11
TL2_YELLOW_PIN = 12
TL2_GREEN_PIN = 13

#height of sensor above the ground
SENSOR_MOUNT_HEIGHT = 5.0

def pins_setup(board):
    """
    Pins from US1 and TL1 are configured

    Args:
    board (The connection to the Arduino (via pymata4))

    Returns:
    None
    """

    #configuring US1 and US2
    board.set_pin_mode_sonar(US1_TRIG_PIN, US1_ECHO_PIN)
    board.set_pin_mode_sonar(US2_TRIG_PIN, US2_ECHO_PIN)

    #configuring TL1 leds
    board.set_pin_mode_digital_output(TL1_RED_PIN)
    board.set_pin_mode_digital_output(TL1_YELLOW_PIN)
    board.set_pin_mode_digital_output(TL1_GREEN_PIN)

    #configuring TL2 leds
    board.set_pin_mode_digital_output(TL2_RED_PIN)
    board.set_pin_mode_digital_output(TL2_YELLOW_PIN)
    board.set_pin_mode_digital_output(TL2_GREEN_PIN)

def overheight_limit_setup():
    """
    The user is asked to enter the overheight limit in meters.
    Returns the overheight limit as entered, or as 4m 
    if user presses enter without providing input. 

    Args:
    None

    Returns:
    overheightLimit (float)- the height limit in metres
    """
    userInput = input("Enter overheight limit in metres (press Enter to set to default of 4.0m): ")

    #if user presses enter, limit is set to default of 4m
    if userInput == "":
        overheightLimit = 4.0
    else:
        overheightLimit = float(userInput)

    return overheightLimit

def vehicle_height_detection(board, trigPin):
    """
    Calculates the height of the vehicle using data from US1/US2

    Args:
    - board (The connection to the Arduino (via pymata4))
    - trigPin (the trigger pin number of the ultrasonic sensor to read from)

    Returns:
    - vehicleHeight (float): the calculated height of the vehicle in metres
    """
    pinReading = board.sonar_read(trigPin)
    heightAboveVehicleCm = pinReading[0]

    #scaling 10cm sensor reading = 1m height read
    heightAboveVehicle = heightAboveVehicleCm / 10.0  
    vehicleHeight = SENSOR_MOUNT_HEIGHT - heightAboveVehicle
    return vehicleHeight

def print_overheight_alert(vehicleHeight):
    """
    Prints an alert to the console of the detected
    vehicle height and the current date/time.

    Args:
    vehicleHeight (the detected height of the overheight vehicle in metres)

    Returns:
    None
    """

    #getting currect time
    currentTime = time.ctime()

    print(f"ALERT! Overheight vehicle of {vehicleHeight:.2f}m detected by US1 at {currentTime}")

def start_light(board, state, timer, redPin, yellowPin, greenPin):
    """
    Switches a light to yellow if it's currently green (idle). Non-blocking -
    returns immediately instead of waiting.

    Args:
    board (The connection to the Arduino (via pymata4))
    state (the light's current colour, as a string)
    timer (the time.time() value when the light last changed colour)
    redPin, yellowPin, greenPin (this light's pin numbers)

    Returns:
    (newState, newTimer) tuple
    """
    if state == "green":
        board.digital_write(greenPin, 0)
        board.digital_write(redPin, 0)
        board.digital_write(yellowPin, 1)
        return "yellow", time.time()
    return state, timer

def update_light(board, state, timer, redPin, yellowPin, greenPin):
    """
    Advances a light to its next colour once enough time has passed in its
    current colour. Call every loop iteration for each light.

    Args:
    board (The connection to the Arduino (via pymata4))
    state (the light's current colour, as a string)
    timer (the time.time() value when the light last changed colour)
    redPin, yellowPin, greenPin (this light's pin numbers)

    Returns:
    (newState, newTimer) tuple
    """
    elapsed = time.time() - timer

    if state == "yellow" and elapsed >= 1:
        board.digital_write(yellowPin, 0)
        board.digital_write(redPin, 1)
        return "red", time.time()

    if state == "red" and elapsed >= 30:
        board.digital_write(redPin, 0)
        board.digital_write(greenPin, 1)
        return "green", time.time()

    return state, timer

def main():
    board = pymata4.Pymata4()
    pins_setup(board)

    overheightLimit = overheight_limit_setup()

    #green light is on all the time before overheight vehicle is detected
    board.digital_write(TL1_GREEN_PIN, 1)
    board.digital_write(TL2_GREEN_PIN, 1)

    tl1State, tl1Timer = "green", time.time()
    tl2State, tl2Timer = "green", time.time()

    detection = True
    us1Detected = False
    us2Detected = False

    try:
        while detection == True:
            us1Height = vehicle_height_detection(board, US1_TRIG_PIN)
            us2Height = vehicle_height_detection(board, US2_TRIG_PIN)

            #for us1 detection
            if us1Height > overheightLimit and us1Detected == False:
                print_overheight_alert(us1Height)
                tl1State, tl1Timer = start_light(board, tl1State, tl1Timer, TL1_RED_PIN, TL1_YELLOW_PIN, TL1_GREEN_PIN)
                us1Detected = True
            elif us1Height <= overheightLimit:
                us1Detected = False

            #for us2 detection
            if us2Height > overheightLimit and us2Detected == False:
                if us1Detected == False:
                    #if us1 did not detect, TL1 and TL2 both start now
                    tl1State, tl1Timer = start_light(board, tl1State, tl1Timer, TL1_RED_PIN, TL1_YELLOW_PIN, TL1_GREEN_PIN)
                    tl2State, tl2Timer = start_light(board, tl2State, tl2Timer, TL2_RED_PIN, TL2_YELLOW_PIN, TL2_GREEN_PIN)
                elif us1Detected == True:
                    #us1 already detected - only TL2 starts
                    tl2State, tl2Timer = start_light(board, tl2State, tl2Timer, TL2_RED_PIN, TL2_YELLOW_PIN, TL2_GREEN_PIN)
                us2Detected = True
            elif us2Height <= overheightLimit:
                us2Detected = False

            #advance each light's own timer independently every loop
            tl1State, tl1Timer = update_light(board, tl1State, tl1Timer, TL1_RED_PIN, TL1_YELLOW_PIN, TL1_GREEN_PIN)
            tl2State, tl2Timer = update_light(board, tl2State, tl2Timer, TL2_RED_PIN, TL2_YELLOW_PIN, TL2_GREEN_PIN)

            time.sleep(0.05)

    except KeyboardInterrupt:
        board.digital_write(TL1_RED_PIN, 0)
        board.digital_write(TL1_YELLOW_PIN, 0)
        board.digital_write(TL1_GREEN_PIN, 0)
        board.digital_write(TL2_RED_PIN, 0)
        board.digital_write(TL2_YELLOW_PIN, 0)
        board.digital_write(TL2_GREEN_PIN, 0)
        board.shutdown()


if __name__ == "__main__":
    main()
