import socket
import sys


# Return the socket object (or None if could not connect)
def setUpNetworkConnection(portListen, bufferTime):
	try:
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#server.bind((socket.gethostname(), portListen))
		server.bind(("128.12.232.95", portListen))
		server.listen(bufferTime)
		return server
	except:
		print "Unexpected error:", sys.exc_info()[0]
		return None