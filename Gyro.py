import smbus			#import SMBus module of I2C
import sys
from twilio.rest import Client
from time import sleep          
from math import atan, sqrt, pow, degrees, fabs


#GPS definition
class GpsData:
  def __init__(self, date, latitude, longitude, speed, heading):
    self.date = date
    self.latitude = latitude
    self.longitude = longitude
    self.speed = speed
    self.heading = heading

class Counter:
    def __init__(self, value):
        self.value = value

c = Counter(-1)

gpsDataArray = [
    GpsData("1/4/2005 4:24:14 PM", 46.81006, -92.08174, 18, "SW"),
    GpsData("1/4/2005 4:24:15 PM", 46.81007, -92.08175, 18, "SW"),
    GpsData("1/4/2005 4:24:16 PM", 46.81009, -92.08176, 19, "SW"),
    GpsData("1/4/2005 4:24:17 PM", 46.81011, -92.08177, 18, "SW"),
    GpsData("1/4/2005 4:24:18 PM", 46.81012, -92.08178, 20, "SW"),
    GpsData("1/4/2005 4:24:19 PM", 46.81016, -92.08179, 18, "SW"),
    GpsData("1/4/2005 4:24:20 PM", 46.81019, -92.08180, 19, "SW"),
    GpsData("1/4/2005 4:24:21 PM", 46.81026, -92.08181, 18, "SW"),
    GpsData("1/4/2005 4:24:22 PM", 46.81027, -92.08182, 18, "SW"),
    GpsData("1/4/2005 4:24:23 PM", 46.81029, -92.08183, 18, "SW"),
    GpsData("1/4/2005 4:24:24 PM", 46.81031, -92.08184, 18, "SW"),
    GpsData("1/4/2005 4:24:25 PM", 46.81033, -92.08185, 21, "SW"),
    GpsData("1/4/2005 4:24:26 PM", 46.81036, -92.08186, 18, "SW"),
    GpsData("1/4/2005 4:24:27 PM", 46.81040, -92.08187, 18, "SW"),
    GpsData("1/4/2005 4:24:28 PM", 46.81045, -92.08188, 21, "SW"),
    GpsData("1/4/2005 4:24:29 PM", 46.81057, -92.08189, 18, "SW"),
    GpsData("1/4/2005 4:24:30 PM", 46.81058, -92.08190, 18, "SW"),
    GpsData("1/4/2005 4:24:31 PM", 46.81059, -92.08191, 18, "SW"),
    GpsData("1/4/2005 4:24:32 PM", 46.81060, -92.08192, 18, "SW"),
    GpsData("1/4/2005 4:24:33 PM", 46.81061, -92.08193, 18, "SW"),
    GpsData("1/4/2005 4:24:34 PM", 46.81062, -92.08194, 18, "SW")]

def get_GPS_location():
  c.value = c.value + 1
  if(c.value == 20):
	  c.value = 0

  return gpsDataArray[c.value]

#end of GPS definition

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
deleyToWait = float(sys.argv[4])
timeRangeForGPS = float(sys.argv[5])
#package pattern position

sleep(deleyToWait)
#wait to setup the initial package position

firstime = True
counter = 0

while True:
	#GPS section
	if((counter / 60) >= timeRangeForGPS):
		location = get_GPS_location()
		message = "Time: " + location.date + "| Latitude: ", location.latitude, "| Longtitude: " ,location.longitude, "| Speed: ", location.speed, "| Heading: ", location.heading
		send_sms( message )
		counter = 0

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
