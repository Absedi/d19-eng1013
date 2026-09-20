from pymata4 import pymata4
import time




board = pymata4.Pymata4()
#tl4RedLed = 0 # shift register pins associated with traffic lights 4 and 5
#tl4YellowLed = 1
#tl4GreenLed = 2
#tl5RedLed = 3
#tl5YellowLed = 4
#tl5GreenLed = 5
#PLRed = 6
#PLGreen = 7
clockPin = 11
dataPin = 13
latchPin = 12
pB = 1
A0 = 7

redRedGreen = 137
yellowRedRed = 74
redGreenRed = 97
redYellowRed = 81
greenRedRed = 76
redRedRed = 73
daylightLevelCuttoffInput = 512





#configure pins
board.set_pin_mode_digital_output(pB)
board.digital_pin_write(pB,0)
board.set_pin_mode_digital_output(clockPin)
board.set_pin_mode_digital_output(dataPin)
board.set_pin_mode_digital_output(latchPin)
board.set_pin_mode_digital_input(pB)
board.set_pin_mode_analog_input(A0)


def lights(tL4,tL5,pL):
    """
    parameters
    tL4

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
    elif pL == "green":
        lightValue += 128
    elif pL == "off":
        lightValue +=0

    board.digital_pin_write(latchPin,0)
    for i in range(7,-1,-1):
        state = (lightValue >> i) & 1
        board.digital_pin_write(clockPin,0)
        board.digital_pin_write(dataPin,state)
        board.digital_pin_write(clockPin,1)
    board.digital_pin_write(latchPin,1)
    print("lightsing")

#state 1, tl4 is green, tl5 is red(20s)
#state 2, tl4 is yellow, tl5 is red(3s)
#state 3, tl4 is red, tl5 is green(10s)
#state 4, tl4 is red, tl5 is yelloe(3s)
#state 5, tl4 and tl5 are red(5s(3s for PB to be green, 2s for PB to flash red))

def change_state(changeIndex):
    """
    Look up the (tl4, tl5) colour pair for a given state index.
 
    Parameters
    changeIndex :
    The state number to transition to (1-5). Each index corresponds
    to a fixed pair of traffic-light colours(int):
 
    Returns
    tl4 = "green", "yellow", or "red"(str)
    tl5 = "green", "yellow", or "red"(str)
    """
    if changeIndex == yellowRedRed:
        return "yellow","red"
    elif changeIndex == redGreenRed:
        return "red","green"
    elif changeIndex == redYellowRed:
        return "red","yellow"
    elif changeIndex == greenRedRed:
        return "green","red"
    elif changeIndex == redRedGreen or changeIndex == redRedRed:
        return "red","red"
    else:
        print("Invalid")
        return

def R1(tl4, tl5,pL):
    """
    Run the pedestrian-crossing sequence.
 
    Called when the pedestrian push-button is pressed. Brings both
    traffic lights to red, gives the pedestrian light a green "walk"
    phase, then a flashing red "don't walk" warning phase, before
    handing control back to the normal traffic-light cycle.
 
    Parameters
    tl4 :Current colour state of traffic light 4 ("green", "yellow",
        or "red").(str)
    tl5 :Current colour state of traffic light 5 ("green", "yellow",
        or "red").(str)
    pL : Current colour state of pedestrian light("red"). (str)
 
    Returns
    tl4 = "green"(str)
    tl5 = "red"(str)
    """
    print("Initiating R1 sequence")
    time.sleep(2)
    if tl5 != "red":
        tl4, tl5 = change_state(yellowRedRed)
        lights(tl4,tl5,pL)
        time.sleep(3)
        tl4,tl5 = change_state(redRedGreen)
        lights(tl4,tl5,pL)
    else:
        tl4, tl5 = change_state(redYellowRed)
        lights(tl4,tl5,pL)
        time.sleep(3)
        tl4,tl5 = change_state(redRedGreen)
        lights(tl4,tl5,pL)
    pL = "green"
    lights(tl4,tl5,pL)
    time.sleep(3)
    pL = "red"
    lights(tl4,tl5,pL)
    flashingTimeStart = time.time()
    flashingTimeEnd = time.time()
    while flashingTimeEnd-flashingTimeStart<2:
        
        time.sleep(0.1)
        pL = "off"
        lights(tl4,tl5,pL)
        time.sleep(0.1)
        pL = "red"
        lights(tl4,tl5,pL)
        flashingTimeEnd = time.time()
    return "green","red"
    
def day_night_cycle():
    if board.analog_read(A0)<=512:
        return 30,5
    else:
        return 20,10


        
def main():
    start = time.time()
    timeBetweenR1Start = 0
    yellowTime = 3
    tl4 = "green" #Initial state for traffic light 4 and 5
    tl5 = "red"
    while True:
        try: 
            tl4GreenTime,tl5GreenTime = day_night_cycle()
            pL = "red"
            if tl4 == "green" and tl5 == "red":
                end = time.time()
                if end - start >= tl4GreenTime:
                    start = time.time()
                    tl4, tl5 = change_state(yellowRedRed)
                    print(tl4+ "     "+ tl5)
                    lights(tl4,tl5,pL)
            if tl4 == "yellow" and tl5 == "red":
                end = time.time()
                if end - start >= yellowTime:
                    start = time.time()
                    tl4, tl5 = change_state(redGreenRed)
                    print(tl4+ "     "+ tl5) 
                    lights(tl4,tl5,pL)   
            if tl4 == "red" and tl5 == "green":
                end = time.time()
                if end - start >= tl5GreenTime:
                    start = time.time()
                    tl4, tl5 = change_state(redYellowRed)
                    print(tl4+ "     "+ tl5) 
                    lights(tl4,tl5,pL) 
            if tl4 == "red" and tl5 == "yellow":
                end = time.time()
                if end - start >= yellowTime:
                    start = time.time()
                    tl4, tl5 = change_state(greenRedRed)
                    print(tl4+ "     "+ tl5) 
                    lights(tl4,tl5,pL)
            if board.digital_read(pB)[0] == 1:
                timeBetweenR1End = time.time()
                if timeBetweenR1End-timeBetweenR1Start>=30:
                    tl4, tl5 = R1(tl4,tl5,pL)
                    timeBetweenR1Start = time.time()
                else: 
                    print(f"{30 - (timeBetweenR1End - timeBetweenR1Start):.0f} seconds till pedestrian light sequence can be initiated again")
        except KeyboardInterrupt:
            board.shutdown()
            break    
            
                
if __name__ == '__main__':

    main()

