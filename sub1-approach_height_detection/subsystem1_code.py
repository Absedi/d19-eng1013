"""
This module contains the code for approach height detection (subsystem 1)
Team: D19
Author: Pooja Sai Shruthika Medisetti
Created on: 31-08-2026
Version: 4.0
"""

import time
from pymata4 import pymata4

# pin configurations:
us1TrigPin = 2
us1EchoPin = 3

tl1RedPin = 5
tl1YellowPin = 6
tl1GreenPin = 7

us2TrigPin = 9
us2EchoPin = 10

tl2RedPin = 11
tl2YellowPin = 12
tl2GreenPin = 13

# height of sensor above the ground (metres)
sensorMountHeight = 5.0

# scaling: 10cm sensor reading = 1m of height
sensorCmPerMetre = 10.0

# default overheight limit in metres (spec 1.R4)
defaultOverheightLimit = 4.0

# traffic light timings in seconds (spec 1.R2 / 1.R3)
yellowDurationSeconds = 1
redDurationSeconds = 30

# delay between each pass of the main loop, in seconds
loopDelaySeconds = 0.05

# number of most recent readings averaged to filter sensor noise (spec 1.G4)
movingAverageWindowSize = 5

# digital pin states
pinOn = 1
pinOff = 0


def pins_setup(board):
    """
    Configures the pins for US1, US2, TL1 and TL2.

    Args:
    board (The connection to the Arduino (via pymata4))

    Returns:
    None
    """

    # configuring US1 and US2
    board.set_pin_mode_sonar(us1TrigPin, us1EchoPin)
    board.set_pin_mode_sonar(us2TrigPin, us2EchoPin)

    # configuring TL1 leds
    board.set_pin_mode_digital_output(tl1RedPin)
    board.set_pin_mode_digital_output(tl1YellowPin)
    board.set_pin_mode_digital_output(tl1GreenPin)

    # configuring TL2 leds
    board.set_pin_mode_digital_output(tl2RedPin)
    board.set_pin_mode_digital_output(tl2YellowPin)
    board.set_pin_mode_digital_output(tl2GreenPin)


def overheight_limit_setup():
    """
    The user is asked to enter the overheight limit in metres.
    If the user presses enter without providing any input, the default
    limit is used. If the input is not a valid positive number, the user
    is asked again.

    Args:
    None

    Returns:
    overheightLimit (float) - the height limit in metres
    """
    while True:
        userInput = input(f"Enter overheight limit in metres (press Enter to set to default of {defaultOverheightLimit}m): ")

        # if user presses enter, limit is set to the default
        if userInput.strip() == "":
            return defaultOverheightLimit

        try:
            overheightLimit = float(userInput)
        except ValueError:
            print("Invalid input. Please enter a number, e.g. 4.0")
            continue

        if overheightLimit <= 0:
            print("Invalid input. The limit must be greater than 0.")
            continue

        return overheightLimit


def vehicle_height_detection(board, trigPin):
    """
    Calculates the height of the vehicle using data from US1/US2

    Args:
    board (The connection to the Arduino (via pymata4))
    trigPin (the trigger pin number of the ultrasonic sensor to read from)

    Returns:
    vehicleHeight (float): the calculated height of the vehicle in metres
    """
    pinReading = board.sonar_read(trigPin)
    heightAboveVehicleCm = pinReading[0]

    # scaling sensor reading (cm) to height (m)
    heightAboveVehicle = heightAboveVehicleCm / sensorCmPerMetre
    vehicleHeight = sensorMountHeight - heightAboveVehicle
    return vehicleHeight


def moving_average(readings, newReading):
    """
    Filters noise from sensor using a moving average. The new reading is
    added to the list, the oldest reading is removed once the list is longer
    than movingAverageWindowSize, and the average of the list is returned.
    Until the list is full, the average of the readings collected so far is used.

    Args:
    readings (list): the recent readings for one sensor (updated in place)
    newReading (float): the latest reading from that sensor

    Returns:
    averageReading (float): the average of the recent readings
    """
    readings.append(newReading)

    # remove oldest reading once window is full
    if len(readings) > movingAverageWindowSize:
        readings.pop(0)

    averageReading = sum(readings) / len(readings)
    return averageReading


def print_overheight_alert(vehicleHeight, sensorName):
    """
    Prints an alert to the console of the detected
    vehicle height, the sensor that detected it, and the current date/time.

    Args:
    vehicleHeight (float): the detected height of the overheight vehicle in metres
    sensorName (string): the name of the sensor that detected the vehicle, e.g. "US1"

    Returns:
    None
    """

    # getting current time
    currentTime = time.ctime()

    print(f"ALERT! Overheight vehicle of {vehicleHeight:.2f}m detected by {sensorName} at {currentTime}")


def green_to_yellow(board, currentLight, timer, redPin, yellowPin, greenPin):
    """
    The chosen traffic light's current light is switched to yellow if it's currently green.

    Args:
    board (The connection to the Arduino (via pymata4))
    currentLight (the traffic light's current colour, as a string)
    timer (time.time() - the time when the last light change occurred)
    redPin, yellowPin, greenPin (change with TL1 or TL2's pin numbers)

    Returns:
    currentLight (updated to yellow, or stays as it was)
    timer (the time when the light change occurred)
    """
    if currentLight == "green":
        board.digital_write(greenPin, pinOff)
        board.digital_write(redPin, pinOff)
        board.digital_write(yellowPin, pinOn)
        return "yellow", time.time()
    return currentLight, timer


def yellow_to_red_to_green(board, currentLight, timer, redPin, yellowPin, greenPin):
    """
    Switches a light from one colour to the next once the required time has passed.
    Yellow for yellowDurationSeconds, then red for redDurationSeconds, then green.

    Args:
    board (The connection to the Arduino (via pymata4))
    currentLight (the light's current colour, as a string)
    timer (time.time() - the time when the last light change occurred)
    redPin, yellowPin, greenPin (change with TL1 or TL2's pin numbers)

    Returns:
    currentLight (updated light colour)
    timer (the time when the light change occurred)
    """
    # time elapsed since the last light change
    timeElapsed = time.time() - timer

    if currentLight == "yellow" and timeElapsed >= yellowDurationSeconds:
        board.digital_write(greenPin, pinOff)
        board.digital_write(yellowPin, pinOff)
        board.digital_write(redPin, pinOn)
        return "red", time.time()

    if currentLight == "red" and timeElapsed >= redDurationSeconds:
        board.digital_write(yellowPin, pinOff)
        board.digital_write(redPin, pinOff)
        board.digital_write(greenPin, pinOn)
        return "green", time.time()

    return currentLight, timer


def turn_off_all_lights(board):
    """
    Turns off every LED used by TL1 and TL2.

    Args:
    board (The connection to the Arduino (via pymata4))

    Returns:
    None
    """
    board.digital_write(tl1RedPin, pinOff)
    board.digital_write(tl1YellowPin, pinOff)
    board.digital_write(tl1GreenPin, pinOff)
    board.digital_write(tl2RedPin, pinOff)
    board.digital_write(tl2YellowPin, pinOff)
    board.digital_write(tl2GreenPin, pinOff)


def main():
    """
    This is the main loop for approach height detection.
    Sets up the board and pins, gets the overheight limit from the user, then
    continuously checks US1/US2 for overheight vehicles and updates TL1/TL2
    accordingly until the user exits with a KeyboardInterrupt.

    Args:
    None

    Returns:
    None
    """
    board = pymata4.Pymata4()

    try:
        pins_setup(board)

        overheightLimit = overheight_limit_setup()

        # green light is on all the time before overheight vehicle is detected
        board.digital_write(tl1GreenPin, pinOn)
        board.digital_write(tl2GreenPin, pinOn)

        tl1Light, tl1Timer = "green", time.time()
        tl2Light, tl2Timer = "green", time.time()

        # tracks whether each sensor currently sees an overheight vehicle
        us1Detected = False
        us2Detected = False

        # recent height readings for each sensor, used for the moving average
        us1Readings = []
        us2Readings = []

        while True:
            # heights are filtered with a moving average to reduce noise
            us1Height = moving_average(us1Readings, vehicle_height_detection(board, us1TrigPin))
            us2Height = moving_average(us2Readings, vehicle_height_detection(board, us2TrigPin))

            # for us1 detection
            if us1Height >= overheightLimit and not us1Detected:
                print_overheight_alert(us1Height, "US1")
                tl1Light, tl1Timer = green_to_yellow(board, tl1Light, tl1Timer, tl1RedPin, tl1YellowPin, tl1GreenPin)
                us1Detected = True
            elif us1Height < overheightLimit:
                us1Detected = False

            # for us2 detection
            if us2Height >= overheightLimit and not us2Detected:
                if not us1Detected:
                    # if us1 did not detect, TL1 and TL2 both run their sequences
                    tl1Light, tl1Timer = green_to_yellow(board, tl1Light, tl1Timer, tl1RedPin, tl1YellowPin, tl1GreenPin)
                    tl2Light, tl2Timer = green_to_yellow(board, tl2Light, tl2Timer, tl2RedPin, tl2YellowPin, tl2GreenPin)
                else:
                    # if us1 already detected, only TL2 runs its sequence
                    tl2Light, tl2Timer = green_to_yellow(board, tl2Light, tl2Timer, tl2RedPin, tl2YellowPin, tl2GreenPin)
                us2Detected = True
            elif us2Height < overheightLimit:
                us2Detected = False

            # advance each light's own timer independently every loop
            tl1Light, tl1Timer = yellow_to_red_to_green(board, tl1Light, tl1Timer, tl1RedPin, tl1YellowPin, tl1GreenPin)
            tl2Light, tl2Timer = yellow_to_red_to_green(board, tl2Light, tl2Timer, tl2RedPin, tl2YellowPin, tl2GreenPin)

            time.sleep(loopDelaySeconds)

    except KeyboardInterrupt:
        print("Exiting approach height detection...")

    finally:
        # always leave the pins off and close the connection cleanly
        turn_off_all_lights(board)
        board.shutdown()


if __name__ == "__main__":
    main()
