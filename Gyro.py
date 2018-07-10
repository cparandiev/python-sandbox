import smbus			#import SMBus module of I2C
import sys
from twilio.rest import Client
from time import sleep          
from math import atan, sqrt, pow, degrees, fabs

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

def calculate_angle(x, y, z):
   return degrees(atan(x / sqrt(pow(y,2) + pow(z,2))))


def send_sms(text, firstime):	
	account_sid = 'AC5a212b36e7e30bfd3556e5387e875c36'
	auth_token = 'd2bbb88bb40f3bbf908ef2819cc81de2'
	client = Client(account_sid, auth_token)

	if(firstime):
		message = client.messages.create(body=text, from_='+17027665831', to='+359877768626')
	
	print(text)


def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

print (" Reading Data of Gyroscope and Accelerometer")

init = True
Xi = 0
Yi = 0
Zi = 0
#initial package position 

Xp = float(sys.argv[1])
Yp = float(sys.argv[2])
Zp = float(sys.argv[3])
#package pattern position

sleep(10)
#wait to setup the initial package position

firstime = True

while True:
	
	#Read Accelerometer raw value
	acc_x = read_raw_data(ACCEL_XOUT_H)
	acc_y = read_raw_data(ACCEL_YOUT_H)
	acc_z = read_raw_data(ACCEL_ZOUT_H)
	
	#Read Gyroscope raw value
	gyro_x = read_raw_data(GYRO_XOUT_H)
	gyro_y = read_raw_data(GYRO_YOUT_H)
	gyro_z = read_raw_data(GYRO_ZOUT_H)
	
	#Full scale range +/- 250 degree/C as per sensitivity scale factor
	Ax = acc_x/16384.0
	Ay = acc_y/16384.0
	Az = acc_z/16384.0
	
	Gx = gyro_x/131.0
	Gy = gyro_y/131.0
	Gz = gyro_z/131.0
	
	Xt = calculate_angle(Ax, Ay, Az)
	Yt = calculate_angle(Ay, Ax, Az)
	Zt = calculate_angle(Az, Ay, Ax)
	#real time package position

	if(init):
		Xi = Xt
		Yi = Yt
		Zi = Zt
		init = False

	if(fabs(Xt - Xi) > fabs(Xp)):
		send_sms("X axis exceed the limit with value: %.2f" %fabs(Xt - Xi), firstime)
		firstime = False
	if(fabs(Xt + Xi) > fabs(Xp)):
		send_sms("X axis exceed the limit with value: %.2f" %fabs(Xt + Xi), firstime)
		firstime = False

	if(fabs(Yt - Yi) > fabs(Yp)):
		send_sms("Y axis exceed the limit with value: %.2f" %fabs(Yt - Yi), firstime)
		firstime = False
	if(fabs(Yt + Yi) > fabs(Yp)):
		send_sms("Y axis exceed the limit with value: %.2f" %fabs(Yt + Yi), firstime)
		firstime = False

	if(fabs(Zt - Zi) > fabs(Zp)):
		send_sms("Z axis exceed the limit with value: %.2f" %fabs(Zt - Zi), firstime)
		firstime = False
	if(fabs(Zt + Zi) > fabs(Zp)):
		send_sms("Z axis exceed the limit with value: %.2f" %fabs(Zt + Zi), firstime)
		firstime = False
	sleep(1)
