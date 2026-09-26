#This module contains the code for the tunnel height detection
#Distances are measured in CM and have a 1:10 scale
# Created By : Leway Wang
# Created Date: 27/8/2026
# version ='3.0'

#1:10 scale of US3, and US4


#Variables
tunnelHeight = 40.0 #this is in 4 meters scaled down to cm 1:10
ultraSonicHeight = 50.0
errorRange = 0.5
ultraSonicTimeOut = 800000
pollingRate = 0.1
us3Distance = 0
us4Distance = 0

from pymata4 import pymata4
import time as t
board = pymata4.Pymata4()


tl3PinDictionary = {'redLed': 2, 'greenLed': 3 }
us3PinDictionary = {'trig': 4, 'echo': 5}
us4PinDictionary = {'trig': 6, 'echo': 7}


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
    if us3Distance >=ultraSonicHeight - errorRange:
        return False
    if us3Distance > 0 and us4Distance > 0:
        if us3Distance > us4Distance - errorRange and us3Distance < us4Distance + errorRange:
            return True
        else:
            return False
    else:
        print("Error: Invalid Reading")
        return False

def main():
    board.digital_pin_write(tl3PinDictionary['greenLed'], 1)
    '''
    Main Function, all code for tunnel height detection subsystem
    is ran here

    Parameters:
        None
    Returns:
        None
    '''

    #Validation statement for input overheight limit
    global overHeightLimit #Needs to be used in whole subsystem
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
        while True: 
            try:

                t.sleep(pollingRate)
                #print("US3 Distance in cm: " + str(us3CurrentDistance))
            except IndexError:
                print("Invalid Readings")
                t.sleep(pollingRate)
                continue #Next iteration
            withinRange = us3_us4_verification(us3Distance,us4Distance)
            
            if withinRange == None:
                print("Ultrasonic sensors not reading data") #Ultrasonic sensors are broken

            if withinRange:
                if us3Distance <= overHeightLimit: 
                    print("Us3 detects an object!")
                    board.digital_pin_write(tl3PinDictionary['greenLed'], 0)
                    board.digital_pin_write(tl3PinDictionary['redLed'], 1)
                else:
                    print("no object in range")
                    board.digital_pin_write(tl3PinDictionary['greenLed'], 1)
                    board.digital_pin_write(tl3PinDictionary['redLed'], 0)



    except KeyboardInterrupt:
        print("Shutting Down")
        shutdown_system()
        board.shutdown()



if __name__ == "__main__":
    main()


