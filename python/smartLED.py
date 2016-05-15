# File: smartLED.py
# Author: Joe Polin
# Date: Jan 2016

# Desc: This is a simple python class that:
# 1. Finds a smart LED light bulb (sold by Lumen8, et al.) if it
#    is on the same network (TODO: Handle multiple bulbs)
# 2. Allows various modes of control, such as:
#	- Set color
# 	- Set warm light with given intensity

# TODO:
# Error-check arguments
# Sync/get time
# Automatically choose date when next time will occur
# Set speed for functions

# Imports
import sys
import socket
import re
import datetime, time

# Debugging
import pudb

# Constants
MYPORT = 48899
TCP_PORT = 5577
BUFFER_SIZE = 1024

# Helper function(s)
def cksum(b):
	return sum(b) % 256


# Generate 1-byte number that represents some combo of week-days
def generateRepeatDays(days):
	dayToVal = {"MON":2, "TUES":4, "WED":8, "THURS":16, "FRI":32, "SAT":64, "SUN":128}
	x = 0
	for d in days:
		if d in dayToVal.keys():
			x += dayToVal[d]
		else:
			print "Did not recognize: " + d
			print "Please use one of: " + str(dayToVal.keys())
	return x

class smartLED:

	# Initialize
	def __init__(self):
		# Find bulb(s) on network
		self.ip = self.findLED()
		# Open TCP connection with bulb
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.ip, TCP_PORT))

	# Broadcast a UDP message asking for bulbs. Wait for response(s)
	def findLED(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', 0))
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		# Ask for IP, MAC, etc...
		sock.sendto("HF-A11ASSISTHREAD", ('<broadcast>', MYPORT))
		data, addr = sock.recvfrom(BUFFER_SIZE)
		sock.close()
		# Parse
		ip, mac, mid = data.split(",")
		print "Found bulb at ", ip 
		return ip

	# Allow client to use 'with'
	def __enter__(self):
		return self

	# Cleanup
	def __exit__(self, exc_type, exc_value, traceback):
		self.sock.close()

	# Add checksum (unless not desired) and send
	def send(self, msg, addChecksum = True):
		if addChecksum:
			msg += [cksum(msg)]
		# print "msg of length " + str(len(msg)) + ":"
		# print msg
		self.sock.send(bytearray(msg))

	# Send packet to set alarm (alarm settings should be 84 bytes)
	def set_alarm_setting(self, alarm_settings):
		msg = [0x21] + alarm_settings + [0, 0x0f]
		self.send(msg)
		# There is a response for this
		self.listen()

	# Wait for response to msg (or until timeout in sec)
	def listen(self, timeout=2):
		self.sock.settimeout(timeout)
		try:
			data = self.sock.recv(BUFFER_SIZE)
			# print "Received: ", data.encode('hex')
			# Put into bytes
			reply_list = re.findall('..', data.encode('hex'))
			reply = [int(x, 16) for x in reply_list]
			return reply
		except socket.timeout:
			print "Warning: Was listening but timed out."

	# Turn on/off
	def turn_on(self):
		self.send([0x71, 0x23, 0x0f])

	def turn_off(self):
		self.send([0x71, 0x24, 0x0f])

	# Set light to RGB
	def set_color(self, red, green, blue):
		# Code for setting color/warm
		msg = [0x31]
		# Input color
		msg += [red, green, blue]
		# Warmth, remote/local
		msg += [0, 0xf0, 0x0f]
		# Set w/o waiting for response
		self.send(msg)

	# Set warm light with given intensity
	def set_warm(self, intensity):
		# Code for setting color/warm
		msg = [0x31]
		# Input color doesn't matter
		msg += [0,0,0]
		# Warmth, remote/local (note: diff from color)
		msg += [intensity, 0x0f, 0x0f]
		# Set w/o waiting for
		self.send(msg)

	# Query alarms
	def get_alarms(self):
		msg = [0x22, 0x2A, 0x2B, 0x0f]
		self.send(msg)
		reply = self.listen()
		# Remove first and last pairs of bytes; 84 remaining
		del(reply[:2])
		del(reply[-2:])
		return reply


	# 'Delete' alarm at index (if given int), indices (if given list), or all (if no args)
	def delete_alarm(self, idx=None):
		# Setting for a non-existent alarm
		del_alarm = [15] + [0 for x in range(0, 12)] + [15]
		# If just one arg, put into list
		if type(idx) is int:
			idx = [idx]
		# If all, then add all to list
		elif idx is None:
			idx = range(0,6)
		# Remove all alarms with index in idx
		current_alarm = self.get_alarms()
		for i in idx:
			if (i < 0 or i > 5):
				print "Cannot delete alarm " + str(i)
				continue
			current_alarm[14*i:14*(i+1)] = del_alarm
		self.set_alarm_setting(current_alarm)

	# Get index where we should add alarm
	def get_first_off_alarm(self, current_alarm):
		modes = current_alarm[::14]
		if 15 in modes:
			return modes.index(15)
		else:
			return None

	def add_alarm(self, mode="OFF", modeargs=None, hour=0, minute=0, second=0, repeatDays=0, exists=True, year=0, month=0, day=0):
		current_alarm = self.get_alarms()
		idx = self.get_first_off_alarm(current_alarm)
		if (idx is None):
			print "Cannot add any more alarms"
			return
		# Generate new alarm frame
		new_single_alarm = self.set_single_alarm(mode, modeargs, hour, minute, second, repeatDays, exists, year, month, day)
		# Put it into current
		new_alarm = current_alarm
		new_alarm[14*idx:14*(idx+1)] = new_single_alarm
		self.set_alarm_setting(new_alarm)

	# All date fields are 0 by default; app can't spec date
	def set_single_alarm(self, mode, modeargs, hour, minute, second, repeatDays, exists, year, month, day):
		# Byte 0: Exists (240 = yes, 15 = no)
		msg = [240 if exists else 15]
		# Byte 1-3: Year (2 digit form), month, day (0 means today?)
		msg += [year, month, day]
		# Byte 4-6: Hour (0-23), minute, second
		msg += [hour, minute, second]
		# Byte 7: Days to repeat (see generateRepeatDays())
		msg += [repeatDays]
		# Byte 8: Mode (0 for off, 39 for function, 97 for rgb/warm)
		modeMap = {"OFF":0, "FUNCTION":36, "WARM":97, "RGB":97}
		msg += [modeMap[mode]]
		## Function args in 4 bytes, followed by 240 for on and 15 for off
		# If function, put function type in first slot
		if (mode == "FUNCTION"):
			msg[-1] += modeargs # This is weird, but seems right
			msg += [0, 0, 0, 0, 240]
		# If RGB, modeargs should be a 3-vector
		elif (mode == "RGB"):
			msg += modeargs + [0, 240]
		# If warm, put intensity as arg 4
		elif (mode=="WARM"):
			msg += [0, 0, 0, modeargs, 240]
		# OFF or unknown
		else:
			msg += [0, 0, 0, 0, 15]
		return msg

	# manualTime should be of type datetime.datetime (empty does computer time)
	def sync_time(self, manualTime=None):
		if manualTime is None:
			t = datetime.datetime.today()
		else:
			t = manualTime
		# Build msg
		msg = [0x10, 0x14, t.year % 100, t.month, t.day, t.hour, t.minute, t.second]
		# Weekday (+1)
		msg += [t.weekday() + 1]
		# Local
		msg += [0, 0x0F]
		print msg
		self.send(msg)
		# There is a response
		self.listen()

	def get_time(self):
		msg = [0x11, 0x1A, 0x1B, 0x0f]
		self.send(msg)
		raw_time_response = self.listen()
		# Year 2-digit -> 4-digit (will only work until 2100)
		raw_time_response[3] += 2000 
		return (datetime.datetime(*raw_time_response[3:9]), raw_time_response[9])

	def get_status(self):
		msg = [0x81, 0x8A, 0x8B]
		self.send(msg)
		raw_status = self.listen()
		print raw_status
		# Parse and put into dict
		status = {}
		status["name"] = raw_status[1]
		if raw_status[2] == 0x23:
			status["power"] = 1
		else:
			status["power"] = 0
		status["mode"] = raw_status[3]
		status["speed"] = raw_status[5]
		status["warm"] = raw_status[9]
		status["cool"] = raw_status[7]
		return status


# Example(s)
if __name__ == "__main__":


	with smartLED() as led:
		led.turn_on()
		# led.turn_off()
	# Basic
		# led.set_color(255,0,0)
		# time.sleep(3)
		# led.set_color(0,0,255)
		# time.sleep(3)
		# led.set_warm(50)

	# A bit more fancy
		# duration = 10 # sec, total
		# for x in range(0,255):
		# 	led.set_warm(x)
		# 	time.sleep(duration/255.0)
	# 	led.turn_off()

	# Learning how to set alarm
		# msg = bytearray(led.get_alarms())
		# # Put into timestamped csv file
		# with open("alarms" + time.strftime('%Y_%m_%d__%H_%M_%S') + ".csv", "w") as f:
		# 	for idx, c in enumerate(msg):
		# 		# Check if new line
		# 		if idx % 14 == 0:
		# 			f.write('\n')
		# 		f.write(str(c) + ",")
				
	# 	Delete alarms
		# led.delete_alarm()

		# Set some alarms: set_single_alarm(self, mode="OFF", modeargs, hour=0, minute=0, second=0, repeatDays=0, exists=True, year=0, month=0, day=0)


		# A bunch of alarms
		# led.delete_alarm()
		# led.add_alarm("RGB", [255, 0, 0], 20, 30, 0, repeatDays=0xff)
		# led.add_alarm("WARM", 50, 23, 59, 0, repeatDays=0, year=16, month=1, day=9)
		# led.add_alarm("FUNCTION", 16, 4, 30, generateRepeatDays(["MON", "WED", "FRI", "SUN"]))

		# Set all 6 at 1 minute increments starting at:
		# led.delete_alarm()
		# startTime = [7,10] 
		# print "Sunrise starts at: " + str(startTime[0]) + ":" + str(startTime[1])
		# for x in range(0, 6): 
		#	intensity = int((x+1)**2 * 255.0/36.0)
		#	led.add_alarm("WARM", intensity, startTime[0], startTime[1]+x, 0, repeatDays=0xff)

		# led.set_warm(20)

		# Check the set/get time functions
		# led.sync_time(datetime.datetime(2016, 5, 8, 14, 2, 0))
		# print led.get_time()

		# print led.get_status()

