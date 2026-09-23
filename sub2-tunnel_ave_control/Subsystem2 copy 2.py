# This module contains the code for the tunnel control avenue
# Created By : Manit Kalra
# Created Date: 21/9/2026
# Version ='5.0'

from pymata4 import pymata4
import time




board = pymata4.Pymata4()
#tL4RedLed = 0 # shift register pins associated with traffic lights 4 and 5
#tL4YellowLed = 1
#tL4GreenLed = 2
#tL5RedLed = 3
#tL5YellowLed = 4
#tL5GreenLed = 5
#PLRed = 6
#PLGreen = 7
clockPin = 11
dataPin = 13
latchPin = 12
pB = 10
pLRedFlashing = 9
A3 = 3

redRedGreen = 137
yellowRedRed = 74
redGreenRed = 97
redYellowRed = 81
greenRedRed = 76
redRedFlashingRed = 9
daylightLevelCuttoffInput = 512


pLGreenTime = 3
pLFlashingRedTime = 2




#configure pins
board.set_pin_mode_digital_output(pB)
board.digital_pin_write(pB,0)
board.set_pin_mode_digital_output(clockPin)
board.set_pin_mode_digital_output(dataPin)
board.set_pin_mode_digital_output(latchPin)
board.set_pin_mode_digital_input(pB)
board.set_pin_mode_digital_output(pLRedFlashing)
board.set_pin_mode_analog_input(A3)


def lights(tL4,tL5,pL):
    """
    takes the state of every light and turns on and off the corresponding leds
    parameters
    tL4 :"green", "yellow", or "red"(str)
    tL5 :"green", "yellow", or "red"(str)
    pL : "red", "green", or "flashing red"(str)

    returns
    None
    """
    lightValue = 0
    if tL4 == "red":
        lightValue+=1
    elif tL4 == "yellow":
        lightValue+=2
    elif tL4 == "green":
        lightValue += 4
    if tL5 == "red":
        lightValue+=8
    elif tL5 == "yellow":
        lightValue+=16
    elif tL5 == "green":
        lightValue += 32
    if pL == "red":
        lightValue += 64
        board.digital_pin_write(pLRedFlashing,0)
    elif pL == "green":
        lightValue += 128
        board.digital_pin_write(pLRedFlashing,0)
    elif pL == "flashing red":
        board.digital_pin_write(pLRedFlashing,1)
        lightValue+=0
    elif pL == "off":
        lightValue +=0

    board.digital_pin_write(latchPin,0)
    for i in range(7,-1,-1):
        state = (lightValue >> i) & 1
        board.digital_pin_write(clockPin,0)
        board.digital_pin_write(dataPin,state)
        board.digital_pin_write(clockPin,1)
    board.digital_pin_write(latchPin,1)


def change_state(changeIndex):
    """
    Look up the (tL4, tL5) colour pair for a given state index.
 
    Parameters
    changeIndex :
    The state number to transition to (1-5). Each index corresponds
    to a fixed pair of traffic-light colours(int):
 
    Returns
    tL4 = "green", "yellow", or "red"(str)
    tL5 = "green", "yellow", or "red"(str)
    """
    if changeIndex == yellowRedRed:
        return "yellow","red"
    elif changeIndex == redGreenRed:
        return "red","green"
    elif changeIndex == redYellowRed:
        return "red","yellow"
    elif changeIndex == greenRedRed:
        return "green","red"
    elif changeIndex == redRedGreen or changeIndex == redRedFlashingRed:
        return "red","red"
    else:
        print("Invalid")
        return

def R1(tL4, tL5,pL):
    """
    Run the pedestrian-crossing sequence. 
 
    Parameters
    tL4 :"green", "yellow", or "red"(str)
    tL5 :"green", "yellow", or "red"(str)
    pL : "red"(str)
 
    Returns
    tL4 = "green"(str)
    tL5 = "red"(str)
    """
    print("Initiating R1 sequence")
    time.sleep(2)
    if tL5 != "red":
        tL4, tL5 = change_state(redYellowRed)
        lights(tL4,tL5,pL)
        time.sleep(3)
        tL4,tL5 = change_state(redRedGreen)
        lights(tL4,tL5,pL)
    else:
        tL4, tL5 = change_state(yellowRedRed)
        lights(tL4,tL5,pL)
        time.sleep(3)
        tL4,tL5 = change_state(redRedGreen)
        lights(tL4,tL5,pL)
    pL = "green"
    lights(tL4,tL5,pL)
    time.sleep(pLGreenTime)
    pL = "flashing red"
    lights(tL4,tL5,pL)
    time.sleep(pLFlashingRedTime)
    pL = "red"
    lights(tL4,tL5,pL)
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
    if board.analog_read(A3)<=512:
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
    yellowTime = 3
    tL4 = "green" #Initial state for traffic light 4 and 5
    tL5 = "red"
    pL = "red"
    lights(tL4,tL5,pL)
    while True:
        try: 
            tL4GreenTime,tL5GreenTime = day_night_cycle()
            pL = "red"
            if tL4 == "green" and tL5 == "red":
                end = time.time()
                if end - start >= tL4GreenTime:
                    start = time.time()
                    tL4, tL5 = change_state(yellowRedRed)
                    print(tL4+ "     "+ tL5)
                    lights(tL4,tL5,pL)
            if tL4 == "yellow" and tL5 == "red":
                end = time.time()
                if end - start >= yellowTime:
                    start = time.time()
                    tL4, tL5 = change_state(redGreenRed)
                    print(tL4+ "     "+ tL5) 
                    lights(tL4,tL5,pL)   
            if tL4 == "red" and tL5 == "green":
                end = time.time()
                if end - start >= tL5GreenTime:
                    start = time.time()
                    tL4, tL5 = change_state(redYellowRed)
                    print(tL4+ "     "+ tL5) 
                    lights(tL4,tL5,pL) 
            if tL4 == "red" and tL5 == "yellow":
                end = time.time()
                if end - start >= yellowTime:
                    start = time.time()
                    tL4, tL5 = change_state(greenRedRed)
                    print(tL4+ "     "+ tL5) 
                    lights(tL4,tL5,pL)
            if board.digital_read(pB)[0] == 1:
                timeBetweenR1End = time.time()
                print(timeBetweenR1Start)
                print(timeBetweenR1End)
                if timeBetweenR1End-timeBetweenR1Start>=30:
                    tL4, tL5 = R1(tL4,tL5,pL)
                    timeBetweenR1Start = time.time()
                    lights(tL4,tL5,pL)
                else: 
                    print(f"{30 - (timeBetweenR1End - timeBetweenR1Start):.0f} seconds till pedestrian light sequence can be initiated again")
        except KeyboardInterrupt:
            board.shutdown()
            break    
            
                
if __name__ == '__main__':

    main()

