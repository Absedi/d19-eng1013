"""
This module contains the code for approach height detection (subsystem 1)
Team: D19
Author: Pooja Sai Shruthika Medisetti
Created on: 05-10-2026
Version: 6.0
"""

import time
from pymata4 import pymata4

# pin configurations:
us1TrigPin = 2
us1EchoPin = 3
us2TrigPin = 9
us2EchoPin = 10

# US5 (from subsystem 3) uses A1 and A2 as digital pins
us5TrigPin = 15
us5EchoPin = 16

# traffic light pins (red, yellow, green)
tl1Pins = (5, 6, 7)
tl2Pins = (11, 12, 13)

# WL1 warning light pins (two yellow LEDs)
wl1Pins = (4, 8)

# WL1 LED flashing rate (at 2-3 Hz)
wl1FlashFrequency = 2.5
# the two LEDs take turns, so each one is on for half of a flash
wl1Leds = 2
wl1FlashSequence = 1 / (wl1Leds * wl1FlashFrequency)

# PA1 buzzer pin (turns the 555 timer tone on/off), and uses A0 as a digital pin
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

# digital pin states
pinOn = 1
pinOff = 0


def pins_setup(board):
    """
    Configures the pins for US1, US2, US5, TL1, TL2, WL1 and PA1.

    Parameters:
    board (Pymata4): The connection to the Arduino (via pymata4)

    Returns:
    function has no return
    """
    # configuring US1 and US2
    board.set_pin_mode_sonar(us1TrigPin, us1EchoPin)
    board.set_pin_mode_sonar(us2TrigPin, us2EchoPin)

    # configuring US5
    board.set_pin_mode_sonar(us5TrigPin, us5EchoPin)

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
    Calculates the height of the vehicle using data from US1/US2/US5.

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


def update_light(board, lightPins, colour, timer, triggered, keepRed):
    """
    Runs a traffic light's overheight sequence: green to yellow when triggered,
    then red after yellowDurationSeconds, then green after redDurationSeconds
    (unless keepRed is True, in which case it stays red until released elsewhere).

    Parameters:
    board (Pymata4): The connection to the Arduino (via pymata4)
    lightPins (tuple): The (red, yellow, green) pin numbers of TL1 or TL2
    colour (str): The light's current colour
    timer (float): The time (from time.time()) of the light's last colour change
    triggered (bool): True if an overheight vehicle was just detected for this light
    keepRed (bool): True if the light must stay red until US5 releases it (1.I1)

    Returns:
    colour (str): The light's colour after the update
    timer (float): The time of the light's last colour change
    """
    timeElapsed = time.time() - timer

    if colour == "green" and triggered:
        newColour = "yellow"
    elif colour == "yellow" and timeElapsed >= yellowDurationSeconds:
        newColour = "red"
    elif colour == "red" and not keepRed and timeElapsed >= redDurationSeconds:
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
        firstLedOn = int(time.time() / wl1FlashSequence) % wl1Leds == 0
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
    overheight vehicles and coordinates TL1/TL2/WL1/PA1 accordingly. Once TL1/TL2
    turn red, they stay red until US5 sees the vehicle exit and US1/US2/US5 are
    all clear (1.I1). Runs until exited with KeyboardInterrupt.

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

        # whether TL1/TL2 are being held red until US5 releases them
        keepRed = False
        # whether US5 has detected the overheight vehicle exiting
        us5HasSeenVehicle = False

        while True:
            us1Height = vehicle_height_detection(board, us1TrigPin)
            us2Height = vehicle_height_detection(board, us2TrigPin)
            us5Height = vehicle_height_detection(board, us5TrigPin)

            us1Overheight = us1Height > overheightLimit
            us2Overheight = us2Height > overheightLimit
            us5Overheight = us5Height > overheightLimit

            # a vehicle is only newly detected when it has not been detected already by the same sensor
            us1NewDetection = us1Overheight and not us1WasOverheight
            us2NewDetection = us2Overheight and not us2WasOverheight

            if us1NewDetection:
                print_overheight_alert(us1Height)

            # US1 triggers TL1. US2 triggers TL2 also TL1 if US1 is not detecting an overheight vehicle.
            tl1Triggered = us1NewDetection or (us2NewDetection and not us1Overheight)
            tl2Triggered = us2NewDetection

            # keeping TL1 and TL2 from turning green again, waiting for US5 to detect a vehicle exiting
            if tl1Triggered or tl2Triggered:
                keepRed = True
                us5HasSeenVehicle = False

            tl1Colour, tl1Timer = update_light(board, tl1Pins, tl1Colour, tl1Timer, tl1Triggered, keepRed)
            tl2Colour, tl2Timer = update_light(board, tl2Pins, tl2Colour, tl2Timer, tl2Triggered, keepRed)

            # saves that US5 has detected a vehicle exiting.
            if keepRed and us5Overheight and not us5HasSeenVehicle:
                us5HasSeenVehicle = True

            # Once:
            # US5 has detected the vehicle exiting
            # and US1, US2 & US5 are all clear
            allClear = not (us1Overheight or us2Overheight or us5Overheight)
            if keepRed and us5HasSeenVehicle and allClear:
                tl1Colour, tl1Timer = "green", time.time()
                tl2Colour, tl2Timer = "green", time.time()
                set_light(board, tl1Pins, tl1Colour)
                set_light(board, tl2Pins, tl2Colour)
                keepRed = False
                us5HasSeenVehicle = False

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
