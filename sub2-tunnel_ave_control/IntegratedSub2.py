#This module contains the code for the tunnel height detection
#Distances are measured in CM and have a 1:10 scale
# Created By : Leway Wang and Manit Kalra
# Created Date: 27/8/2026
# version ='3.0'

#1:10 scale of US3, and US4


#Variables
tunnelHeight = 40.0 #this is in 4 meters scaled down to cm 1:10
ultraSonicHeight = 50.0
errorRange = 3
ultraSonicTimeOut = 500000
pollingRate = 0.1
us3Distance = 0
us4Distance = 0


us3ValidState = 0
tL4RedLedBit = 2**1 # shift register pins associated with traffic lights 4 and 5
tL4YellowLedBit = 2**2
tL4GreenLedBit = 2**3
tL5RedLedBit = 2**4
tL5YellowLedBit = 2**5
tL5GreenLedBit = 2**6
plRedBit = 2**0
plGreenBit = 2**7

#Pin
clockPin = 13
dataPin = 11
latchPin = 12
pushButtonPin = 9
pLRedFlashing = 10
ldrPin = 4

redRedGreen = tL4RedLedBit + tL5RedLedBit + plGreenBit
yellowRedRed = tL4YellowLedBit + tL5RedLedBit + plRedBit
redGreenRed = tL4RedLedBit + tL5GreenLedBit + plRedBit
redYellowRed = tL4RedLedBit + tL5YellowLedBit + plRedBit
greenRedRed = tL4GreenLedBit + tL5RedLedBit + plRedBit
redRedRed = tL4RedLedBit + tL5RedLedBit + plRedBit
daylightLevelCuttoffInput = 50


pLGreenTime = 3
pLFlashingRedTime = 2
yellowTime = 3
slowDownLoopTime = 0.01
waitBeforeInitiatingR1 = 2
spamPreventionTime = 1
daylightSwitchAntiSpam = 1

from pymata4 import pymata4
import time as t
board = pymata4.Pymata4()


tl3PinDictionary = {'redLed': 2, 'greenLed': 3 }
us3PinDictionary = {'trig': 4, 'echo': 5}
us4PinDictionary = {'trig': 6, 'echo': 7}

#Initialise Pins
board.set_pin_mode_digital_output(clockPin)
board.set_pin_mode_digital_output(dataPin)
board.set_pin_mode_digital_output(latchPin)
board.set_pin_mode_digital_input(pushButtonPin)
board.set_pin_mode_digital_output(pLRedFlashing)
board.set_pin_mode_analog_input(ldrPin)
#Initialising Pins for TL3
for key, pins in tl3PinDictionary.items():
    print(key + " Was initialised for tl3")
    board.set_pin_mode_digital_output(pins)

def shutdown_system():
    '''
    Writes all output pins to zero

    Parameters:
        None
    Returns;
        None
    '''
    board.digital_pin_write(tl3PinDictionary['greenLed'],0 )
    board.digital_pin_write(tl3PinDictionary['redLed'],0)
#Setting up call back function for US3
def us3_call_back(dataUs3):
    '''
    Callback function for US3, appends distance reading to us3 array
    Data = [pin_type, trigger_pin, distance, timestamp]
    
    Parameters:
        Data input for US3
    Returns:
        None
    '''
    global us3Distance
    us3Distance = dataUs3[2] 
    


def lights(trafficLight4,trafficLight5,pedestrianLight):
    """
    takes the state of every light and turns on and off the corresponding leds
    parameters
    trafficLight4 :"green", "yellow", or "red"(str)
    trafficLight5 :"green", "yellow", or "red"(str)
    pedestrianLight : "red", "green", or "flashing red"(str)

    returns
    None
    """
    lightValue = 0
    if trafficLight4 == "red":
        lightValue+=tL4RedLedBit
    elif trafficLight4 == "yellow":
        lightValue+=tL4YellowLedBit
    elif trafficLight4 == "green":
        lightValue += tL4GreenLedBit
    if trafficLight5 == "red":
        lightValue+=tL5RedLedBit
    elif trafficLight5 == "yellow":
        lightValue+=tL5YellowLedBit
    elif trafficLight5 == "green":
        lightValue += tL5GreenLedBit
    if pedestrianLight == "red":
        lightValue += plRedBit
        board.digital_pin_write(pLRedFlashing,0)
    elif pedestrianLight == "green":
        lightValue += plGreenBit
        board.digital_pin_write(pLRedFlashing,0)
    elif pedestrianLight == "flashing red":
        board.digital_pin_write(pLRedFlashing,1)
        lightValue+=plRedBit
    elif pedestrianLight == "off":
        lightValue +=0

    board.digital_pin_write(latchPin,0)
    for i in range(7,-1,-1):
        state = (lightValue >> i) & 1
        board.digital_pin_write(clockPin,0)
        board.digital_pin_write(dataPin,state)
        board.digital_pin_write(clockPin,1)
    board.digital_pin_write(latchPin,1)


def print_light_state(trafficLight4, trafficLight5, pedestrianLight):
    """
    Prints the current, labelled state of traffic light 4 and traffic light 5.

    Parameters
    trafficLight4 :"green", "yellow", or "red"(str)
    trafficLight5 :"green", "yellow", or "red"(str)
    pedestrianLight: "green", "red", or "flashing red"(str)
    Returns
    None
    """
    print(f"Traffic Light 4: {trafficLight4}     Traffic Light 5: {trafficLight5}       Pedestrian Light: {pedestrianLight}")


def change_state(changeIndex):
    """
    Look up the (trafficLight4, trafficLight5) colour pair for a given state index,
    and print the resulting, labelled light state.
 
    Parameters
    changeIndex :
    The state number to transition to (1-5). Each index corresponds
    to a fixed pair of traffic-light colours(int):
 
    Returns
    trafficLight4 = "green", "yellow", or "red"(str)
    trafficLight5 = "green", "yellow", or "red"(str)
    """
    if changeIndex == yellowRedRed:
        trafficLight4,trafficLight5, pedestrianLight = "yellow","red","red"
    elif changeIndex == redGreenRed:
        trafficLight4,trafficLight5,pedestrianLight = "red","green","red"
    elif changeIndex == redYellowRed:
        trafficLight4,trafficLight5,pedestrianLight = "red","yellow","red"
    elif changeIndex == greenRedRed:
        trafficLight4,trafficLight5,pedestrianLight = "green","red","red"
    elif changeIndex == redRedGreen:
        trafficLight4,trafficLight5,pedestrianLight = "red","red","green"
    elif changeIndex == redRedRed:
                trafficLight4,trafficLight5,pedestrianLight = "red","red","red"
    else:
        print("Invalid")
        return
    lights(trafficLight4,trafficLight5,pedestrianLight)
    print_light_state(trafficLight4,trafficLight5, pedestrianLight)
    return trafficLight4,trafficLight5

def r1_sequence(trafficLight4, trafficLight5,pedestrianLight):
    """
    Run the pedestrian-crossing sequence. 
 
    Parameters
    trafficLight4 :"green", "yellow", or "red"(str)
    trafficLight5 :"green", "yellow", or "red"(str)
    pedestrianLight : "red"(str)
 
    Returns
    trafficLight4 = "green"(str)
    trafficLight5 = "red"(str)
    """
    print("Initiating R1 sequence")
    pauseStart = t.time()
    pauseEnd = t.time()
    while pauseEnd - pauseStart<waitBeforeInitiatingR1:
        pauseEnd = t.time()
        t.sleep(slowDownLoopTime)
    if trafficLight5 != "red":
        trafficLight4, trafficLight5 = change_state(redYellowRed)
        yellowStart = t.time()
        yellowEnd = t.time()
        while yellowEnd - yellowStart<yellowTime:
            yellowEnd = t.time()
            t.sleep(slowDownLoopTime)
        trafficLight4,trafficLight5 = change_state(redRedGreen)
        t.sleep(slowDownLoopTime)
    else:
        trafficLight4, trafficLight5 = change_state(yellowRedRed)
        yellowStart = t.time()
        yellowEnd = t.time()
        while yellowEnd - yellowStart<yellowTime:
            yellowEnd = t.time()
            t.sleep(slowDownLoopTime)
        trafficLight4,trafficLight5 = change_state(redRedGreen)
    plGreenStart = t.time()
    plGreenEnd= t.time()
    while plGreenEnd - plGreenStart<pLGreenTime:
        plGreenEnd = t.time()
        t.sleep(slowDownLoopTime)
    pedestrianLight = "flashing red"
    lights(trafficLight4,trafficLight5,pedestrianLight)
    print_light_state(trafficLight4,trafficLight5,pedestrianLight)
    plFlashingRedStart = t.time()
    pLFlashingRedEnd = t.time()
    while pLFlashingRedEnd- plFlashingRedStart<pLFlashingRedTime:
        pLFlashingRedEnd = t.time()
        t.sleep(slowDownLoopTime)
    change_state(redRedRed)
    lights(trafficLight4,trafficLight5,pedestrianLight)
    return "green","red"
    
def day_night_cycle():
    """
    Reads the output from the light dependant resistpr and decides whether to run the day or the night cyclr
    
    parameters
    None
    
    Returns
    tL4GreenTime = 30 for night cycle, 20 for day (int)
    tL5GreenTime = 5 for night cycle, 10 for day (int)  
    cycle = "red" or "green"(str)  
    """
    if board.analog_read(ldrPin)[0]>=daylightLevelCuttoffInput:
        return 30,5,"night"
    else:
        return 20,10,"day"


        

#Setting up call back function for US4
def us4_call_back(dataUs4):
    '''
    Callback function for US4, appends distance reading to us3 array
    Data = [pin_type, trigger_pin, distance, timestamp]

    Parameters:
        Data input for US4
    Returns:
        None
    '''
    global us4Distance
    us4Distance = dataUs4[2] 

#Initialising Pins for US3
board.set_pin_mode_sonar(us3PinDictionary["trig"],us3PinDictionary['echo'], timeout = ultraSonicTimeOut, callback = us3_call_back)

#Initialising Pins for US4
board.set_pin_mode_sonar(us4PinDictionary["trig"],us4PinDictionary['echo'], timeout = ultraSonicTimeOut, callback = us4_call_back )

#Verification for US3 and US4 
def us3_us4_verification(us3Distance,us4Distance):
    '''
    Function is used to verify if US3 distance data is within
    an acceptable range around US4

    Parameters:
        us3Distance
        us4Distance
    Returns:
        A boolean, True for that it is within the range, false otherwise
    '''

    if us3Distance > 0 and us4Distance > 0:
        if abs(us3Distance - us4Distance) <= errorRange:
            return True
        else:
            return False
    else:
        print("Error: Invalid Reading")
        print(us3Distance)
        print(us4Distance)
        return False

def main():
    '''
    Main Function, all code for tunnel height detection subsystem
    is ran here

    Parameters:
        None
    Returns:
        None
    '''
    board.digital_pin_write(tl3PinDictionary['greenLed'], 1)


    timeBetweenR1Start = -30
    pedestrianLightCooldownTime = 30
    lastCooldownPrint = 0
    trafficLight4 = "green" #Initial state for traffic light 4 and 5 and pedestrianLight
    trafficLight5 = "red"
    pedestrianLight = "red" 
    print_light_state(trafficLight4,trafficLight5, pedestrianLight) #print the initial state
    lights(trafficLight4,trafficLight5,pedestrianLight)
    tL4GreenTime,tL5GreenTime,cycle =  day_night_cycle()
    timeBetweenDaylightSwitchStart = 0
    #Validation statement for input overheight limit
    global overHeightLimit #Needs to be used in whole subsystem
    overrideActive = False
    while True:
        overHeightLimit = input("Enter the overheight limit in meters: ") #Scaling Factor of 1:10
        if overHeightLimit == '':
            overHeightLimit = tunnelHeight #Default Value
            print("Over Height Limit defaults to 4m")
            break
        try:
            overHeightLimit = float(overHeightLimit)*10
            if overHeightLimit < 0 or overHeightLimit > tunnelHeight:
                print("Enter a valid float value - within 0 and 4 meters")
                continue
            break
        except ValueError:
            print('Please enter a valid float value')
    overHeightLimit = ultraSonicHeight - overHeightLimit #Since the sensor is assumed placed ontop, the sensor will detect the distance between itself and the top of the truck
    
    try:
        start = t.time()
        while True: 
            try:

                t.sleep(pollingRate)
               
            except IndexError:
                print("Invalid Readings")
                t.sleep(pollingRate)
                continue #Next iteration
            withinRange = us3_us4_verification(us3Distance,us4Distance)

            #print("US3: " + str(us3Distance) + ", US4: " + str(us4Distance) + ", Verfication:" + str(withinRange))
            if withinRange == None:
                print("Ultrasonic sensors not reading data") #Ultrasonic sensors are broken

    
            if withinRange and us3Distance <= overHeightLimit:
                board.digital_pin_write(tl3PinDictionary['greenLed'], 0)
                board.digital_pin_write(tl3PinDictionary['redLed'], 1)
                us3ValidState = 1

            elif withinRange and us3Distance > overHeightLimit:
                board.digital_pin_write(tl3PinDictionary['greenLed'], 1)
                board.digital_pin_write(tl3PinDictionary['redLed'], 0)
                us3ValidState = 0

            else:
                board.digital_pin_write(tl3PinDictionary['greenLed'], 1)
                board.digital_pin_write(tl3PinDictionary['redLed'], 0)    
                us3ValidState = 0


            if us3ValidState == 1:
                if not overrideActive:  # only act on the transition into override
                    overrideActive = True
                    trafficLight4, trafficLight5 = change_state(redRedRed)
                t.sleep(slowDownLoopTime)
                continue  # skip the normal cycle and the pedestrian button

            if overrideActive:  # vehicle just cleared, so resume the normal cycle
                overrideActive = False
                trafficLight4, trafficLight5 = change_state(greenRedRed)
                start = t.time()


            pedestrianLight = "red"
            if trafficLight4 == "green" and trafficLight5 == "red":
                end = t.time()
                if end - start >= tL4GreenTime:
                    start = t.time()
                    trafficLight4, trafficLight5 = change_state(yellowRedRed)
            if trafficLight4 == "yellow" and trafficLight5 == "red":
                end = t.time()
                if end - start >= yellowTime:
                    start = t.time()
                    trafficLight4, trafficLight5 = change_state(redGreenRed)
            if trafficLight4 == "red" and trafficLight5 == "green":
                end = t.time()
                if end - start >= tL5GreenTime:
                    start = t.time()
                    trafficLight4, trafficLight5 = change_state(redYellowRed)
            if trafficLight4 == "red" and trafficLight5 == "yellow":
                end = t.time()
                if end - start >= yellowTime:
                    start = t.time()
                    trafficLight4, trafficLight5 = change_state(greenRedRed)
            t.sleep(slowDownLoopTime)
            if board.digital_read(pushButtonPin)[0] != 0:
                timeBetweenR1End = t.time()
                if timeBetweenR1End-timeBetweenR1Start>=pedestrianLightCooldownTime:
                    trafficLight4, trafficLight5 = r1_sequence(trafficLight4,trafficLight5,pedestrianLight)
                    timeBetweenR1Start = t.time()
                    start = t.time()
                    lights(trafficLight4,trafficLight5,pedestrianLight)
                elif t.time() - lastCooldownPrint > spamPreventionTime: 
                    lastCooldownPrint = t.time()
                    print(f"{pedestrianLightCooldownTime - (timeBetweenR1End - timeBetweenR1Start):.0f} seconds till pedestrian light sequence can be initiated again")
            oldTl4GreenTime = tL4GreenTime
            tL4GreenTime,tL5GreenTime,cycle = day_night_cycle()
            if oldTl4GreenTime !=tL4GreenTime:
                timeBetweenDaylightSwitchEnd = t.time()
                if timeBetweenDaylightSwitchEnd-timeBetweenDaylightSwitchStart>daylightSwitchAntiSpam:
                    print(f"switched to {cycle} cycle")
                    timeBetweenDaylightSwitchStart = t.time()



            # ... your existing 4 state-machine blocks and push button code here ...

    except KeyboardInterrupt:
        print("Shutting Down")
        shutdown_system()
        board.shutdown()



if __name__ == "__main__":
    main()


