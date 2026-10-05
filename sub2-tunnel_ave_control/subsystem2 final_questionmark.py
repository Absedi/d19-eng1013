from pymata4 import pymata4
import time




board = pymata4.Pymata4()
tL4RedLedBit = 1 # shift register pins associated with traffic lights 4 and 5
tL4YellowLedBit = 2
tL4GreenLedBit = 4
tL5RedLedBit = 8
tL5YellowLedBit = 16
tL5GreenLedBit = 32
plRedBit = 64
plGreenBit = 128


clockPin = 11
dataPin = 13
latchPin = 12
pushButtonPin = 5
pLRedFlashing = 9
ldrPin = 3

redRedGreen = 137
yellowRedRed = 74
redGreenRed = 97
redYellowRed = 81
greenRedRed = 76
redRedFlashingRed = 9
daylightLevelCuttoffInput = 512


pLGreenTime = 3
pLFlashingRedTime = 2
yellowTime = 3
slowDownLoopTime = 0.01
waitBeforeInitiatingR1 = 2
spamPreventionTime = 1




#configure pins
board.set_pin_mode_digital_output(clockPin)
board.set_pin_mode_digital_output(dataPin)
board.set_pin_mode_digital_output(latchPin)
board.set_pin_mode_digital_input(pushButtonPin)
board.set_pin_mode_digital_output(pLRedFlashing)
board.set_pin_mode_analog_input(ldrPin)


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


def print_light_state(trafficLight4, trafficLight5):
    """
    Prints the current, labelled state of traffic light 4 and traffic light 5.

    Parameters
    trafficLight4 :"green", "yellow", or "red"(str)
    trafficLight5 :"green", "yellow", or "red"(str)

    Returns
    None
    """
    print(f"Traffic Light 4: {trafficLight4}     Traffic Light 5: {trafficLight5}")


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
        trafficLight4,trafficLight5 = "yellow","red"
    elif changeIndex == redGreenRed:
        trafficLight4,trafficLight5 = "red","green"
    elif changeIndex == redYellowRed:
        trafficLight4,trafficLight5 = "red","yellow"
    elif changeIndex == greenRedRed:
        trafficLight4,trafficLight5 = "green","red"
    elif changeIndex == redRedGreen or changeIndex == redRedFlashingRed:
        trafficLight4,trafficLight5 = "red","red"
    else:
        print("Invalid")
        return

    print_light_state(trafficLight4,trafficLight5)
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
    time.sleep(waitBeforeInitiatingR1)
    if trafficLight5 != "red":
        trafficLight4, trafficLight5 = change_state(redYellowRed)
        lights(trafficLight4,trafficLight5,pedestrianLight)
        time.sleep(yellowTime)
        trafficLight4,trafficLight5 = change_state(redRedGreen)
        lights(trafficLight4,trafficLight5,pedestrianLight)
    else:
        trafficLight4, trafficLight5 = change_state(yellowRedRed)
        lights(trafficLight4,trafficLight5,pedestrianLight)
        time.sleep(yellowTime)
        trafficLight4,trafficLight5 = change_state(redRedGreen)
        lights(trafficLight4,trafficLight5,pedestrianLight)
    pedestrianLight = "green"
    lights(trafficLight4,trafficLight5,pedestrianLight)
    time.sleep(pLGreenTime)
    pedestrianLight = "flashing red"
    lights(trafficLight4,trafficLight5,pedestrianLight)
    time.sleep(pLFlashingRedTime)
    pedestrianLight = "red"
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
    """
    if board.analog_read(ldrPin)[0]>=daylightLevelCuttoffInput:
        return 30,5
    else:
        return 20,10


        
def main():
    """
    Controls the entire traffic light system

    Parameters
    None

    Returns
    None
    
    """
    start = time.time()
    timeBetweenR1Start = -30
    pedestrianLightCooldownTime = 30
    lastCooldownPrint = 0
    trafficLight4 = "green" #Initial state for traffic light 4 and 5 and pedestrianLight
    trafficLight5 = "red"
    pedestrianLight = "red"
    print_light_state(trafficLight4,trafficLight5) #print the initial state
    lights(trafficLight4,trafficLight5,pedestrianLight)
    while True:
        try: 
            tL4GreenTime,tL5GreenTime = day_night_cycle()
            pedestrianLight = "red"
            if trafficLight4 == "green" and trafficLight5 == "red":
                end = time.time()
                if end - start >= tL4GreenTime:
                    start = time.time()
                    trafficLight4, trafficLight5 = change_state(yellowRedRed)
                    lights(trafficLight4,trafficLight5,pedestrianLight)
            if trafficLight4 == "yellow" and trafficLight5 == "red":
                end = time.time()
                if end - start >= yellowTime:
                    start = time.time()
                    trafficLight4, trafficLight5 = change_state(redGreenRed)
                    lights(trafficLight4,trafficLight5,pedestrianLight)   
            if trafficLight4 == "red" and trafficLight5 == "green":
                end = time.time()
                if end - start >= tL5GreenTime:
                    start = time.time()
                    trafficLight4, trafficLight5 = change_state(redYellowRed)
                    lights(trafficLight4,trafficLight5,pedestrianLight) 
            if trafficLight4 == "red" and trafficLight5 == "yellow":
                end = time.time()
                if end - start >= yellowTime:
                    start = time.time()
                    trafficLight4, trafficLight5 = change_state(greenRedRed)
                    lights(trafficLight4,trafficLight5,pedestrianLight)
            time.sleep(slowDownLoopTime)
            if board.digital_read(pushButtonPin)[0] != 0:
                timeBetweenR1End = time.time()
                if timeBetweenR1End-timeBetweenR1Start>=pedestrianLightCooldownTime:
                    trafficLight4, trafficLight5 = r1_sequence(trafficLight4,trafficLight5,pedestrianLight)
                    timeBetweenR1Start = time.time()
                    lights(trafficLight4,trafficLight5,pedestrianLight)
                elif time.time() - lastCooldownPrint > spamPreventionTime: 
                    lastCooldownPrint = time.time()
                    print(f"{pedestrianLightCooldownTime - (timeBetweenR1End - timeBetweenR1Start):.0f} seconds till pedestrian light sequence can be initiated again")
        except KeyboardInterrupt:
            board.shutdown()
            break    
            
                
if __name__ == '__main__':

    main()