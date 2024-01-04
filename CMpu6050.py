
'''
https://fishpoint.tistory.com/5306
        Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
	http://www.electronicwings.com
'''
import smbus			#import SMBus module of I2C
from time import sleep          #import

import time
class CMpu6050:
	def __init__(self):

		#some MPU6050 Registers and their Address
		self.PWR_MGMT_1   = 0x6B
		self.SMPLRT_DIV   = 0x19
		self.CONFIG       = 0x1A
		self.GYRO_CONFIG  = 0x1B
		self.INT_ENABLE   = 0x38
		self.ACCEL_XOUT_H = 0x3B
		self.ACCEL_YOUT_H = 0x3D
		self.ACCEL_ZOUT_H = 0x3F
		self.GYRO_XOUT_H  = 0x43
		self.GYRO_YOUT_H  = 0x45
		self.GYRO_ZOUT_H  = 0x47


	def MPU_Init(self):

		self.bus = smbus.SMBus(1)  # or bus = smbus.SMBus(0) for older version boards
		self.Device_Address = 0x68  # MPU6050 device address


		#write to sample rate register
		self.bus.write_byte_data(self.Device_Address, self.SMPLRT_DIV, 7)

		#Write to power management register
		self.bus.write_byte_data(self.Device_Address, self.PWR_MGMT_1, 1)

		#Write to Configuration register
		self.bus.write_byte_data(self.Device_Address, self.CONFIG, 0)

		#Write to Gyro configuration register
		self.bus.write_byte_data(self.Device_Address, self.GYRO_CONFIG, 24)

		#Write to interrupt enable register
		self.bus.write_byte_data(self.Device_Address, self.INT_ENABLE, 1)

	def read_raw_data(self, addr):
		#Accelero and Gyro value are 16-bit
			high = self.bus.read_byte_data(self.Device_Address, addr)
			low = self.bus.read_byte_data(self.Device_Address, addr+1)

			#concatenate higher and lower value
			value = ((high << 8) | low)

			#to get signed value from mpu6050
			if(value > 32768):
					value = value - 65536
			return value


		# print (" Reading Data of Gyroscope and Accelerometer")


	def getSensorTotal(self):
		(Ax, Ay, Az, Gx, Gy, Gz) = self.getSensor()
		# print(Ax, Ay, Az, Gx, Gy, Gz)
		total = abs(Gx) + abs(Gy) + abs(Gz)
		return total

	def getSensor(self):

		#Read Accelerometer raw value
		acc_x = self.read_raw_data(self.ACCEL_XOUT_H)
		acc_y = self.read_raw_data(self.ACCEL_YOUT_H)
		acc_z = self.read_raw_data(self.ACCEL_ZOUT_H)

		#Read Gyroscope raw value
		gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
		gyro_y = self.read_raw_data(self.GYRO_YOUT_H)
		gyro_z = self.read_raw_data(self.GYRO_ZOUT_H)

		#Full scale range +/- 250 degree/C as per sensitivity scale factor
		Ax = acc_x/16384.0
		Ay = acc_y/16384.0
		Az = acc_z/16384.0

		Gx = gyro_x/131.0
		Gy = gyro_y/131.0
		Gz = gyro_z/131.0


		# print ("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g" %Az)
		# sleep(0.01)
		return (Ax, Ay, Az, Gx, Gy, Gz)

		"""
		pi@raspberrypi:~/link/emot/test/mpu6050_test $ 
		pi@raspberrypi:~/link/emot/test/mpu6050_test $ python3 mpu6050_test.py 
		 Reading Data of Gyroscope and Accelerometer
		
		Gx=2.40 °/s 	Gy=19.82 °/s 	Gz=5.77 °/s 	Ax=0.26 g 	Ay=-0.05 g 	Az=1.17 g
		Gx=-0.63 °/s 	Gy=1.37 °/s 	Gz=0.27 °/s 	Ax=0.04 g 	Ay=-0.02 g 	Az=1.12 g
		Gx=0.37 °/s 	Gy=0.05 °/s 	Gz=-0.68 °/s 	Ax=0.07 g 	Ay=-0.03 g 	Az=1.08 g
		Gx=0.41 °/s 	Gy=0.06 °/s 	Gz=-0.31 °/s 	Ax=0.05 g 	Ay=-0.00 g 	Az=1.08 g
		Gx=0.84 °/s 	Gy=0.86 °/s 	Gz=-0.70 °/s 	Ax=0.03 g 	Ay=-0.01 g 	Az=1.08 g
		Gx=0.53 °/s 	Gy=0.05 °/s 	Gz=-0.28 °/s 	Ax=0.08 g 	Ay=0.01 g 	Az=1.10 g
		^CTraceback (most recent call last):
		  File "/home/pi/link/emot/test/mpu6050_test/mpu6050_test.py", line 83, in <module>
			sleep(0.1)
		
		"""



	def TEST_movingavg(self):
		self.arraynum = 20
		self.values = [0 for i in range(self.arraynum)]



		# tot = 0
		print(self.values)
		for ix in range(self.arraynum*100):
			tot = 0
			for jx in range(self.arraynum):
				self.updateValues(self.getSensorTotal())
				tot += self.values[jx]
			avg = tot / self.arraynum
			print(avg)



		# print(self.values)
		# print(max(self.values))





if __name__ == "__main__":
	obj = CMpu6050()
	obj.MPU_Init()

	# (Ax, Ay, Az, Gx, Gy, Gz) = obj.getSensor()
	# print(Ax, Ay, Az, Gx, Gy, Gz)
	# exit()
	# print(obj.detectSensor())   # 1: 약한 충격, 2: 강한 충격

	exit()
	while True:
		print(obj.getSensorTotal())
		continue
		(Ax, Ay, Az, Gx, Gy, Gz) = obj.getSensor()
		print (Ax, Ay, Az, Gx, Gy, Gz)


