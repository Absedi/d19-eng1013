from pymata4 import pymata4
import time


board = pymata4.Pymata4()
TL4RedLed = 1
TL4YellowLed = 2
TL4GreenLed = 3
TL5RedLed = 4
TL5YellowLed = 5
TL5GreenLed = 6
PLRed = 7
PLGreen = 8
PB = 9

board.set_pin_mode_digital_output(TL4RedLed)
board.set_pin_mode_digital_output(TL4YellowLed)
board.set_pin_mode_digital_output(TL4GreenLed)
board.set_pin_mode_digital_output(TL5RedLed)
board.set_pin_mode_digital_output(TL5YellowLed)
board.set_pin_mode_digital_output(TL5GreenLed)
board.set_pin_mode_digital_output(PLRed)
board.set_pin_mode_digital_output(PLGreen)
board.set_pin_mode_digital_input(PB)


#state 1, TL4 is green, TL5 is red(20s)
#state 2, TL4 is yellow, TL5 is red(3s)
#state 3, TL4 is red, TL5 is green(10s)
#state 4, TL4 is red, TL5 is yelloe(3s)

def change_state(changeIndex):
    match changeIndex:
        case 1:
            return "yellow","red"
        case 2:
            return "red","green"
        case 3:
            return "red","yellow"
        case 4:
            return "green","red"
        case 5:
            return "red","red"


def R1(TL4, TL5):
    print("Initiating R1 sequence")
    time.sleep(2)
    if TL5 != "red":
        TL4, TL5 = change_state(1)
        lights(TL4,TL5)
        time.sleep(3)
        TL4,TL5 = change_state(5)
        lights(TL4,TL5)
    else:
        TL4, TL5 = change_state(3)
        lights(TL4,TL5)
        time.sleep(3)
        TL4,TL5 = change_state(5)
        lights(TL4,TL5)
    board.digital_pin_write(PLGreen,1)
    board.digital_pin_write(PLRed,0)
    time.sleep(3)
    board.digital_pin_write(PLGreen,0)
    board.digital_pin_write(PLRed,1)
    flashingTimeStart = time.time()
    flashingTimeEnd = time.time()
    while flashingTimeEnd-flashingTimeStart<2:
        board.digital_pin_write(PLRed,0)
        time.sleep(0.1)
        board.digital_pin_write(PLRed,1)
        time.sleep(0.1)
        flashingTimeEnd = time.time()
    board.digital_pin_write(PLRed,1)
    return "green","red"
    

def lights(TL4,TL5):
    match TL4:
        case "green":
            board.digital_pin_write(TL4GreenLed,1)
            board.digital_pin_write(TL4YellowLed,0)
            board.digital_pin_write(TL4RedLed,0)
        case "yellow":
            board.digital_pin_write(TL4GreenLed,0)
            board.digital_pin_write(TL4YellowLed,1)
            board.digital_pin_write(TL4RedLed,0)
        case "red":
            board.digital_pin_write(TL4GreenLed,0)
            board.digital_pin_write(TL4YellowLed,0)
            board.digital_pin_write(TL4RedLed,1)
    match TL5:
        case "green":
            board.digital_pin_write(TL5GreenLed,1)
            board.digital_pin_write(TL5YellowLed,0)
            board.digital_pin_write(TL5RedLed,0)
        case "yellow":
            board.digital_pin_write(TL5GreenLed,0)
            board.digital_pin_write(TL5YellowLed,1)
            board.digital_pin_write(TL5RedLed,0)
        case "red":
            board.digital_pin_write(TL5GreenLed,0)
            board.digital_pin_write(TL5YellowLed,0)
            board.digital_pin_write(TL5RedLed,1)




        
start = time.time()
TL4 = "green"
TL5 = "red"
board.digital_pin_write(PLRed,1)
board.digital_pin_write(PLGreen,0)
while True:
    try:
        if TL4 == "green" and TL5 == "red":
            end = time.time()
            if end - start >= 2:
                start = time.time()
                TL4, TL5 = change_state(1)
                print(TL4+ "     "+ TL5)
        if TL4 == "yellow" and TL5 == "red":
            end = time.time()
            if end - start >= 3:
                start = time.time()
                TL4, TL5 = change_state(2)
                print(TL4+ "     "+ TL5)    
        if TL4 == "red" and TL5 == "green":
            end = time.time()
            if end - start >= 1:
                start = time.time()
                TL4, TL5 = change_state(3)
                print(TL4+ "     "+ TL5)   
        if TL4 == "red" and TL5 == "yellow":
            end = time.time()
            if end - start >= 3:
                start = time.time()
                TL4, TL5 = change_state(4)
                print(TL4+ "     "+ TL5) 
        lights(TL4,TL5)
        if board.digital_pin_read(PB)[0] == 1:
            TL4, TL5 = R1(TL4,TL5)
        
            
        
    except KeyboardInterrupt:

        break

    lights(TL4,TL5)




     
    
    

    

    