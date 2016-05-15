import sys, time
from socket import *



# Calculate 1-byte checksum
def cksum(b):
	return sum(b) % 256



# Get instruction for light with color rgb
def set_color(red, green, blue):
	# Code for setting color/warm
	msg = [0x31]
	# Input color
	msg += [red, green, blue]
	# Warmth, remote/local, and checksum
	msg += [0, 0xf0, 0x0f]
	msg += cksum(msg)

# Get instruction for warm light with given intensity
def set_warm(intensity):
	# Code for setting color/warm
	msg = [0x31]
	# Input color doesn't matter
	msg += [0,0,0]
	# Warmth, remote/local (note: diff from color), and checksum
	msg += [intensity, 0x0f, 0x0f]
	msg += cksum(msg)

if __name__ == "__main__":

	# Socket
	MYPORT = 48899
	s = socket(AF_INET, SOCK_DGRAM)
	s.bind(('', 0))
	s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

	# Ask for IP, MAC, etc...
	print "Sending..."
	s.sendto("HF-A11ASSISTHREAD", ('<broadcast>', MYPORT))
	print "Waiting..."
	data, addr = s.recvfrom(1024) # buffer size is 1024 bytes
	print "received message:", data

	s.close()

	# Parse
	ip, mac, mid = data.split(",")

	print "IP: ", ip

	# Now open TCP connection
	TCP_PORT = 5577
	BUFFER_SIZE = 1024

	s = socket(AF_INET, SOCK_STREAM)
	#s.bind(('', MYPORT))
	s.connect((ip, TCP_PORT))

	# Example message
	#msg = b'\x21\xf0\x00\x00\x00\x0b\x1e\x00\x3c\x00\xff\x00\x00\x00\xf0\xf0\x0f\x01\x06\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x0f\xf0\x0f\x01\x06\x0c\x05\x00\x00\x61\x7c\x7c\x00\x00\xf0\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0\x03'
	#msg = b'\x81\x8A\x8B\x96'
	# msg = b'\x71\x23\x0f\xA3' # Turn on
	# msg = b'\x71\x24\x0f\xA4' # Turn off

	# Make the light red (no response)
	msg = bytearray(b'\x31\x00\x00\x00\xf1\x0f\x0f')
	msg = simple_checksum(msg)
	# 0x31 163 118 60 00 f0 0f 85

	# Query
	# msg = b'\x81\x8A\x8B\x96'

	# Request time
	# msg = b'\x11\x1a\x1b\x0f\55'
	s.send(msg)
	# data = s.recv(BUFFER_SIZE)
	s.close()

	# print "received data:", data.encode('hex')

