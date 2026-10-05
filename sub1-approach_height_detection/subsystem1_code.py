"""
This module contains the code for approach height detection (subsystem 1)
Team: D19
Author: Pooja Sai Shruthika Medisetti
Created on: 05-10-2026
Version: 5.0
"""

import time
from pymata4 import pymata4

# pin configurations:
us1TrigPin = 2
us1EchoPin = 3
us2TrigPin = 9
us2EchoPin = 10

# traffic light pins (red, yellow, green)
tl1Pins = (5, 6, 7)
tl2Pins = (11, 12, 13)

# WL1 warning light pins (two yellow LEDs)
wl1Pins = (4, 8)

# PA1 buzzer pin (turns the 555 timer tone on/off)
pa1Pin = 14

# height of sensor above the ground (metres)
sensorMountHeight = 5.0

# scaling: 10cm sensor reading = 1m of height
scalingSensor = 10.0

# default overheight limit in metres
defaultOverheightLimit = 4.0

# traffic light timings (seconds)
yellowDurationSeconds = 1
redDurationSeconds = 30

# delay between looping (seconds)
loopDelaySeconds = 0.05

# WL1 LED flashing rate (at 2-3 Hz)
wl1FlashFrequencyHz = 2.5
wl1FlashHalfPeriodSeconds = 1 / (2 * wl1FlashFrequencyHz)

# digital pin states
pinOn = 1
pinOff = 0


def pins_setup(board):
    """
    Configures the pins for US1, US2, TL1, TL2, WL1 and PA1.

    Parameters:
    board (Pymata4): The connection to the Arduino (via pymata4)

    Returns:
    function has no return
    """
    # configuring US1 and US2
    board.set_pin_mode_sonar(us1TrigPin, us1EchoPin)
    board.set_pin_mode_sonar(us2TrigPin, us2EchoPin)

    # configuring every TL1, TL2 and WL1 LED as an output
    for pin in tl1Pins + tl2Pins + wl1Pins:
        board.set_pin_mode_digital_output(pin)

    # configuring PA1
    board.set_pin_mode_digital_output(pa1Pin)


def overheight_limit_setup():
    """
    Asks the user to enter the overheight limit in metres. If the user presses
    enter, the default limit of 4m is used. If the input
    is not positive and is 0, the user is asked again.

    Parameters:
    function has no parameters

    Returns:
    overheightLimit (float): The overheight limit in metres
    """
    while True:
        userInput = input(f"Enter overheight limit in metres (press Enter to set to default of {defaultOverheightLimit}m): ")

        # if user presses enter, limit is set to the default
        if userInput.strip() == "":
            return defaultOverheightLimit

        try:
            overheightLimit = float(userInput)
            if overheightLimit > 0:
                return overheightLimit
            print("The limit must be greater than 0m")
        except ValueError:
            print("Please enter a valid number")


def vehicle_height_detection(board, trigPin):
    """
    Calculates the height of the vehicle using data from US1/US2.

    Parameters:
    board (Pymata4): The connection to the Arduino (via pymata4)
    trigPin (int): The trigger pin number of the ultrasonic sensor to read from

    Returns:
    vehicleHeight (float): The calculated height of the vehicle in metres
    """
    distanceCm, readingTime = board.sonar_read(trigPin)

    # scaling sensor reading (cm) to the distance above the vehicle (m)
    heightAboveVehicle = distanceCm / scalingSensor
    return sensorMountHeight - heightAboveVehicle


def print_overheight_alert(vehicleHeight):
    """
    Prints an alert to the console with the detected vehicle height from US1 and the date/time of detection.

    Parameters:
    vehicleHeight (float): The detected height of the overheight vehicle in metres

    Returns:
    function has no return
    """
    print(f"ALERT! Overheight vehicle of {vehicleHeight:.2f}m detected by US1 at {time.ctime()}")


def set_light(board, lightPins, colour):
    """
    Turns on the LED of given colour and turns off LEDs of other two colours.

    Parameters:
    board (Pymata4): The connection to the Arduino (via pymata4)
    lightPins (tuple): The (red, yellow, green) pin numbers of TL1 or TL2
    colour (str): The colour to show: "red", "yellow" or "green"

    Returns:
    function has no return
    """
    redPin, yellowPin, greenPin = lightPins
    board.digital_write(redPin, pinOn if colour == "red" else pinOff)
    board.digital_write(yellowPin, pinOn if colour == "yellow" else pinOff)
    board.digital_write(greenPin, pinOn if colour == "green" else pinOff)


def update_light(board, lightPins, colour, timer, triggered):
    """
    Runs a traffic light's overheight sequence: green to yellow when triggered,
    then red after yellowDurationSeconds, then green after redDurationSeconds.

    Parameters:
    board (Pymata4): The connection to the Arduino (via pymata4)
    lightPins (tuple): The (red, yellow, green) pin numbers of TL1 or TL2
    colour (str): The light's current colour
    timer (float): The time (from time.time()) of the light's last colour change
    triggered (bool): True if an overheight vehicle was just detected for this light

    Returns:
    colour (str): The light's colour after the update
    timer (float): The time of the light's last colour change
    """
    timeElapsed = time.time() - timer

    if colour == "green" and triggered:
        newColour = "yellow"
    elif colour == "yellow" and timeElapsed >= yellowDurationSeconds:
        newColour = "red"
    elif colour == "red" and timeElapsed >= redDurationSeconds:
        newColour = "green"
    else:
        return colour, timer

    set_light(board, lightPins, newColour)
    return newColour, time.time()


def update_wl1(board, tl1Colour, tl2Colour):
    """
    Flashes two yellow WL1 LEDs at 2.5Hz while TL1 or TL2 is not
    green. Both LEDs are off once TL1 and TL2 are both green.

    Parameters:
    board (Pymata4): The connection to the Arduino (via pymata4)
    tl1Colour (str): The current colour of TL1
    tl2Colour (str): The current colour of TL2

    Returns:
    function has no return
    """
    firstLedPin, secondLedPin = wl1Pins

    if tl1Colour == "green" and tl2Colour == "green":
        firstLedOn = False
        secondLedOn = False
    else:
        # first LED lights on for halfway through one flash
        firstLedOn = int(time.time() / wl1FlashHalfPeriodSeconds) % 2 == 0
        # second LED lights on for the other half of one flash
        secondLedOn = not firstLedOn

    board.digital_write(firstLedPin, pinOn if firstLedOn else pinOff)
    board.digital_write(secondLedPin, pinOn if secondLedOn else pinOff)


def update_pa1(board, tl1Colour, tl2Colour):
    """
    Turns on the PA1 buzzer tone while TL1 or TL2 is not green. PA1 is off
    once TL1 and TL2 are both green.

    Parameters:
    board (Pymata4): The connection to the Arduino (via pymata4)
    tl1Colour (str): The current colour of TL1
    tl2Colour (str): The current colour of TL2

    Returns:
    function has no return
    """
    if tl1Colour == "green" and tl2Colour == "green":
        board.digital_write(pa1Pin, pinOff)
    else:
        board.digital_write(pa1Pin, pinOn)


def turn_off_all_lights(board):
    """
    Turns off every LED used by TL1, TL2 and WL1, and the PA1 buzzer.

    Parameters:
    board (Pymata4): The connection to the Arduino (via pymata4)

    Returns:
    function has no return
    """
    for pin in tl1Pins + tl2Pins + wl1Pins:
        board.digital_write(pin, pinOff)

    board.digital_write(pa1Pin, pinOff)


def main():
    """
    Main loop for approach height detection. Sets up the board and pins, gets
    the overheight limit from the user, then continues to use US1/US2 to detect
    overheight vehicles and coordinates TL1/TL2/WL1/PA1 accordingly until exited 
    with KeyboardInterrupt.

    Parameters:
    function has no parameters

    Returns:
    function has no return
    """
    board = pymata4.Pymata4()

    try:
        pins_setup(board)

        overheightLimit = overheight_limit_setup()

        # both traffic lights are green until an overheight vehicle is detected
        tl1Colour, tl1Timer = "green", time.time()
        tl2Colour, tl2Timer = "green", time.time()
        set_light(board, tl1Pins, tl1Colour)
        set_light(board, tl2Pins, tl2Colour)

        # whether each sensor is already detecting the overheight vehicle 
        us1WasOverheight = False
        us2WasOverheight = False

        while True:
            us1Height = vehicle_height_detection(board, us1TrigPin)
            us2Height = vehicle_height_detection(board, us2TrigPin)

            us1Overheight = us1Height > overheightLimit
            us2Overheight = us2Height > overheightLimit

            # a vehicle is only newly detected when it has not been detected already by the same sensor
            us1NewDetection = us1Overheight and not us1WasOverheight
            us2NewDetection = us2Overheight and not us2WasOverheight

            if us1NewDetection:
                print_overheight_alert(us1Height)

            # US1 triggers TL1. US2 triggers TL2 also TL1 if US1 is not detecting an overheight vehicle.
            tl1Triggered = us1NewDetection or (us2NewDetection and not us1Overheight)
            tl2Triggered = us2NewDetection

            tl1Colour, tl1Timer = update_light(board, tl1Pins, tl1Colour, tl1Timer, tl1Triggered)
            tl2Colour, tl2Timer = update_light(board, tl2Pins, tl2Colour, tl2Timer, tl2Triggered)

            update_wl1(board, tl1Colour, tl2Colour)
            update_pa1(board, tl1Colour, tl2Colour)

            # whether each sensor is currently detecting an overheight vehicle, 
            # to be able to tell if vehicles are newly detected in the next check
            us1WasOverheight = us1Overheight
            us2WasOverheight = us2Overheight

            time.sleep(loopDelaySeconds)

    except KeyboardInterrupt:
        print("Exiting approach height detection")
        turn_off_all_lights(board)
        board.shutdown()


if __name__ == "__main__":
    main()
