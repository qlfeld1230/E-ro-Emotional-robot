# import RPi.GPIO as GPIO
# import time
# 
# button_pin = 17
# 
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# 
# try:
#     while True:
#         input_state = GPIO.input(button_pin)
#                 
#         if input_state == False:
#             print("button pushed")
#         
#         time.sleep(0.2)
# except KeyboardInterrupt:
#     pass
# 
# GPIO.cleanup()

from CServoControlsmoo import CServoControl
from CStt import CStt

import random
import time
import threading
import RPi.GPIO as GPIO
import pandas as pd
servo = CServoControl()     # [서보모터 제어 인스턴스]
        
try:
    while True:
        motor_seq = {}
        servo.setMotorAngle(5,110,90)
        print("processing")
        for i in range(0,2):
            servo.setMotorAngle(0,60,90)
            servo.setMotorAngle(2,120,90)
            time.sleep(0.15)
            servo.setMotorAngle(0,120,60)
            servo.setMotorAngle(2,60,120)
            time.sleep(0.15)
            servo.setMotorAngle(0,90,120)
            servo.setMotorAngle(2,90,60)
                         
except KeyboardInterrupt:
    pass
       