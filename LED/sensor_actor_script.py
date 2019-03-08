# import RPi.GPIO as GPIO

#------------------------------------------------------------------------
#Start importData Script
#import database at localhost
import MySQLdb
global plantState
#global reif

db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="runmysql",  # your password
                     db="planta")        # name of the data base

# you must create a Cursor object. It will let
#  you execute all the queries you need
cur = db.cursor()

#-------------------------------------------------------

# import RPi.GPIO as GPIO
import os
import sys
import termios
import tty
import pigpio
import time
from thread import start_new_thread

os.system("sudo pigpiod")



# DEFINE RASPBERRY PINS-----------------------------------------------------
RED_PIN   = 17 # RED_PIN is on GPIO.PIN 17 
GREEN_PIN = 22  # GREEN_PIN is on GPIO.PIN 22 
BLUE_PIN  = 24  # BLUE_PIN is on GPIO.PIN 24 

# Number of color changes per step (more is faster, less is slower). You also can use 0.X floats.
STEPS     = 0.05
# execute terminal command and start pigpiod

# Define colors
bright = 40
r = 0.0
g = 0.0
b = 0.0

brightChanged = False
abort = False
state = True
raiseColor = 0
yellow = False

pi = pigpio.pi()

def updateColor(color, step):
    color += step
    # print ("update color")
    if color > 255:
        return 255
    if color < 0:
        return 0
        
    return color

# set Lightsfunction
def setLights(pin, brightness):
    realBrightness = int(int(brightness) * (float(bright) / 255.0))
    pi.set_PWM_dutycycle(pin, realBrightness)


def checkKey():
    global bright
    global brightChanged
    global state
    global abort
    global yellow
    global raiseColor

raiseColor = 0
    
def startLedStrip():
    global bright
    global brightChanged
    global state
    global abort
    global yellow
    global raiseColor
    global r
    global g
    global b


while True:
    #make lightwave-effect for 5 secs
    t_end = time.time() + 5
    while time.time() < t_end:
        if state and not brightChanged:
            # light go out
            if raiseColor == 0:
                r = updateColor(r, -STEPS)
                setLights(RED_PIN, r)
                r = updateColor(r, -STEPS)
                setLights(RED_PIN, r)
                g = updateColor(g, -STEPS)
                setLights(GREEN_PIN, g)
                b = updateColor(b, -0.5 * STEPS)
                setLights(BLUE_PIN, g)
                #print ("\n", r)
                if g <= 5:
                    raiseColor = 1
                    # print ("raiseColor = 1")
            #light go on
            if raiseColor == 1:
                r = updateColor(r, STEPS)
                setLights(RED_PIN, r)
                r = updateColor(r, STEPS)
                setLights(RED_PIN, r)
                #print ("yellow =", r ,g)
                g = updateColor(g, STEPS)
                setLights(GREEN_PIN, g)
                b = updateColor(b, 0.5 * STEPS)
                setLights(BLUE_PIN, g)
                if g >= 100:
                    raiseColor = 0
                    # print ("only r--")
                    
    print ("\n >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 5 sec are over")
    #setLights(RED_PIN, 0)
    #setLights(GREEN_PIN, 0)
    #setLights(BLUE_PIN, 0)

    checkPlantState()


def checkPlantState():
     while round(time.time) % 5:
        cur.execute("SELECT Status FROM anbau ORDER BY PrimKey DESC LIMIT 1")
        # print all the first cell of all th rows
        plantState = cur.fetchall()[0][0]
        if plantState == "reif":
            setGrowLight(True)
            print ("Reif + Bewegung")
            print ("==============================", plantState)
        else:
            setGrowLight(False)
            print ("==============================", plantState)
    

   
        
####################### VENTILATOR SCRIPT START
def startVentilator(): 
    #import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    ## spreche GPIO pin 14 an
    relais = 14
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relais, GPIO.OUT)
    
    #print ("\n set Relais to LOW to start Ventilator")
    GPIO.output(relais, GPIO.LOW)
    time.sleep(5)
    
    #print ("\n set Relais to HIGH to stop Ventilator")
    GPIO.output(relais, GPIO.HIGH)   
####################### VENTILATOR SCRIPT END

####################### STOP GROWLIGHT SCRIPT START
def setGrowLight(not_active): 
    #import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    ## spreche GPIO pin 15 an
    relais = 15
    print('\n xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx stop growlight!')
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relais, GPIO.OUT)
    
    if not_active:
        print ("\n set Relais to LOW to start Ventilator")
        GPIO.output(relais, GPIO.LOW)
    
    else:
        print ("\n set Relais to HIGH to stop Ventilator")
        GPIO.output(relais, GPIO.HIGH)   
####################### STOP GROWLIGHT SCRIPT END



####### START PIR
import RPi.GPIO as GPIO
SENSOR_PIN = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

print ("\n Bereit")




    
   

#if reif == True:
#    start_new_thread(stopGrowLight, ())
#    print('\n reif == true, stop growlight!')

def mein_callback(channel):
    # Start ventilator (relais).
    start_new_thread(startVentilator, ())
    # Start Light
    start_new_thread(startLedStrip, ())
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<", plantState)
    
   

# if sensor detects motion, start mein_callback function to start ventilator and light strip 
try:
    GPIO.add_event_detect(SENSOR_PIN , GPIO.RISING, callback=mein_callback)
    print ("\n waiting")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    print "Beende..."
GPIO.cleanup()
########### END PIR 
 
print ("Aborting...")

setLights(RED_PIN, 0)
setLights(GREEN_PIN, 0)
setLights(BLUE_PIN, 0)

time.sleep(0.5)

pi.stop()#





