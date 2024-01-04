import Adafruit_PCA9685
from time import sleep
import time



class CServoControl:

    def __init__(self):

        # Alternatively specify a different address and/or bus:

        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)



        # Configure min and max servo pulse lengths

        self.servo_min = 150  # Min pulse length out of 4096

        self.servo_max = 600  # Max pulse length out of 4096

        self.servo_mid = int((self.servo_min+self.servo_max)/2)



        self.current_x = self.servo_mid

        self.current_y = self.servo_mid



        # Set frequency to 60hz, good for servos.

        self.pwm.set_pwm_freq(60)







        # Default Pan/Tilt for the camera in degrees. I have set it up to roughly point at my face location when it starts the code.

        # Camera range is from 0 to 180. Alter the values below to determine the starting point for your pan and tilt.

        self.cam_pan = 40

        self.cam_tilt = 20



        #self.pwm.set_pwm(0, 0, self.servo_mid)

        #self.pwm.set_pwm(1, 0, self.servo_mid)

        



    def TEST_servo(self):

        # Move servo on channel O between extremes.

        self.pwm.set_pwm(0, 0, self.servo_min)

        time.sleep(1)

        self.pwm.set_pwm(0, 0, self.servo_mid)



        time.sleep(3)

        self.pwm.set_pwm(0, 0, self.servo_max)



        time.sleep(1)



        self.pwm.set_pwm(0, 0, self.current_x)



        



    # Helper function to make setting a servo pulse width simpler.

    def set_servo_pulse(self, channel, pulse):



        if pulse < self.servo_min:

            pulse = self.servo_min

        if pulse > self.servo_max:

            pulse = self.servo_max

        pulse_length = 1000000    # 1,000,000 us per second

        pulse_length //= 60       # 60 Hz

        print('{0}us per period'.format(pulse_length))

        pulse_length //= 4096     # 12 bits of resolution

        print('{0}us per bit'.format(pulse_length))

        pulse *= 1000

        pulse //= pulse_length

        self.pwm.set_pwm(channel, 0, pulse)





    def pan(self, p):

        # global current_x

        self.current_x += p

        # if p > 0:

        #     current_x += 1

        # else:

        #     current_x -= 1

        if self.current_x < self.servo_min:

            self.current_x = self.servo_min

        if self.current_x > self.servo_max:

            self.current_x = self.servo_max



        # set_servo_pulse(0, current_x)

        self.pwm.set_pwm(4, 0, self.current_x)

        print("pan1:", self.current_x)



    def tilt(self, t):



        self.current_y += t

        # if p > 0:

        #     current_x += 1

        # else:

        #     current_x -= 1

        if self.current_y < self.servo_min:

            self.current_y = self.servo_min

        if self.current_y > self.servo_max:

            self.current_y = self.servo_max



        # set_servo_pulse(0, current_x)

        self.pwm.set_pwm(5, 0, self.current_y)

        print("tilt:", self.current_y)



        



    def convertAngle2Pulse(self, angle):

        # 0 -> 150

        # 90 -> 375

        # 180 -> 600



        # 서보 값 반대로 회전




        pulse = (((self.servo_max - self.servo_min) / 180) * angle) + self.servo_min





        if pulse > self.servo_max: pulse = self.servo_max

        if pulse < self.servo_min: pulse = self.servo_min





        return int(pulse)





    def setMotorAngle(self, num, angle, before):       # 각 서보 모터 채널별각도를 설정, num:채널 번호, angle: 각도
        pulse = self.convertAngle2Pulse(angle)
        be=self.convertAngle2Pulse(before)
        self.current=be
        if pulse <self.current : fit = -25
        else: fit =25
        #if angle==90:self.pwm.set_pwm(num,0,375)
        while self.current != pulse:
            if abs(self.current-pulse)<abs(fit):
                self.current=pulse
            else:
                self.current += fit
                
            if self.current < self.servo_min:
                self.current=self.servo_min
            if self.current>self.servo_max:
                self.current=self.servo_max
                
            self.pwm.set_pwm(num,0,self.current)
            #print("Angle:",angle, "Pulse:",pulse,"num:",num,"current:",self.current_x)
            sleep(0.09)   
        #print("Angle:",angle, "Pulse:",pulse,"num:",num)
        

if __name__ == "__main__":

    obj = CServoControl()



    # for ix in range(5):

    #     obj.setMotorAngle(ix, 90)



    obj.setMotorAngle(1, 30)       # 1번 채널을 30도로 설정

    obj.setMotorAngle(2, 30)

    obj.setMotorAngle(3, 30)

        

        

        

        


