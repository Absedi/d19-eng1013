#This module contains the code for the tunnel height detection
# Created By : Leway Wang
# Created Date: 27/8/2026
# version ='2.0'

#1:4 scale of US3, and US4
#Notes
#Write shutting function for all pins

#global Variables
overHeightLimitMax = 400.0
ultraSonicHeight = 50.0
timeoutUS = 800000
us3DistanceList = []
us4DistanceList = []

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


#Setting up call back function for US3
def us3_call_back(data):
    '''
    Callback function for US3,
    Data = [pin_type, trigger_pin, distance, timestamp]
    
    Parameters:
        Data input for US3
    Returns:
        Appends Distance to Array
        0
    '''
    
    us3DistanceList.append(data[2])
    return 0



#Setting up call back function for US4
def us4_call_back(data):
    '''
    Callback function for US4,
    Data = [pin_type, trigger_pin, distance, timestamp]

    Parameters:
        Data input for US4
    Returns:
        Appends Distance to Array
        0
    '''

    us4DistanceList.append(data[2])

#Initialising Pins for US3
board.set_pin_mode_sonar(us3PinDictionary["trig"],us3PinDictionary['echo'], timeout = timeoutUS, callback = us3_call_back)

#Initialising Pins for US4
board.set_pin_mode_sonar(us4PinDictionary["trig"],us4PinDictionary['echo'], timeout = timeoutUS, callback = us4_call_back )

#Verification for US3 and US4 
def us3us4Verification(us3Distance,us4Distance):
    '''
    Function is used to verify if US3 distance data is within
    an acceptable range around US4

    Parameters:
        us3Distance
        us4Distance
    Returns:
        A boolean, True for that it is within the range, false otherwise
    '''
    errorRange = 0.2
    if us3Distance > 0 and us4Distance > 0:
        if us3Distance > us4Distance - errorRange and us3Distance < us4Distance + errorRange:
            return True
        else:
            return False
    else:
        print("Error: Invalid Reading")
        return None

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
        overHeightLimit = input("Enter the overheight limit: ")/10 #Scaling Factor of 1:10
        if overHeightLimit == '':
            overHeightLimit = 40.0 #Default Value
            print("Over Height Limit defaults to 4m")
            break
        try:
            overHeightLimit = float(overHeightLimit)
            if overHeightLimit <= 2 or overHeightLimit >= overHeightLimitMax:
                print("Enter a valid float value - within 2 and 400")
                continue
            break
        except ValueError:
            print('Please enter a valid float value')
    overHeightLimit = ultraSonicHeight - overHeightLimit #Since the sensor is assumed placed ontop, the sensor will detect the distance between itself and the top of the truck
    
    try:
        while True: 
            try:
                us3CurrentDistance = us3DistanceList[-1]
                us4CurrentDistance = us4DistanceList[-1]
                print("US3 Distance in cm: " + str(us3CurrentDistance))
            except IndexError:
                print("Invalid Readings")
                continue #Next iteration
            withinRange = us3us4Verification(us3CurrentDistance,us4CurrentDistance)

            if withinRange == None:
                raise ValueError("Ultrasonic sensors not reading data") #Ultrasonic sensors are broken

            if withinRange:
                if us3CurrentDistance <= overHeightLimit: #idk why i need to switch this
                    board.digital_pin_write(tl3PinDictionary['greenLed'], 0)
                    board.digital_pin_write(tl3PinDictionary['redLed'], 1)
                else:
                    board.digital_pin_write(tl3PinDictionary['greenLed'], 1)
                    board.digital_pin_write(tl3PinDictionary['redLed'], 0)



    except KeyboardInterrupt:
        print("Shutting Down")
        board.shutdown()



if __name__ == "__main__":
    main()


