from socket import *
import json
import time
		
serverName = '127.0.0.1'
serverPort = 6000
clientSocket = socket(AF_INET, SOCK_DGRAM)
bufferSize = 2040
byte, count = -1, -1

def received_Data():
	rcv_base, seq, n = 0, 0, 5
	byte, countPacket = 0, 0 
	with open("clientText.txt", 'w') as f:
		# rcv_window does not contains lost packet sequence number and data
		rcv_window = {} # Use dictionary for performance O(1) to look up key-value.
		
		while True:
			data, serverAddress = clientSocket.recvfrom(bufferSize)
			#print data
			data = json.loads(data.decode())
			
			#with open("test.txt", 'w') as f2:
			#	f2.write(str(data))
			#print(str(data))
			seq = (int)(data.get("seq"))
			mesg = data.get("data")
			# If receives ending message from server
			if mesg == "y":
				break # Break the loop
			
			# Case1: Packet with sequence number within the rcv_base
			if seq >= rcv_base and seq <= (rcv_base+n-1):
				# a selective ACK packet is returned to the sender
				ACK = str(seq)
				print "ACK = ", ACK
				clientSocket.sendto(ACK, serverAddress)
				
				# If the packet was not previously received, it is buffered
				if seq not in rcv_window:			
					rcv_window[seq] = mesg
					
				# If this packet has a sequence number equal to the base of the receive window 	
				# then this packet, and any previously buffered and consecutively numbered
				# (beginning with rcv_base) packets are delivered to the upper layer. The receive
				# window is then moved forward by the number of packets delivered to the upper layer
				print "seq = ", seq
				print "rcv_base = ", rcv_base
				if seq == rcv_base:
					f.write(rcv_window[rcv_base])
					while True:
						if (rcv_base + 1) in rcv_window:
							rcv_base += 1 # increase base by 1
							f.write(rcv_window[rcv_base]) # write to file
							byte += len(mesg)
							countPacket += 1
						else:
							break
					
					rcv_base += 1 # Update rcv_base to the packet with smallest unack seq number
					
				byte += len(mesg)
				countPacket += 1
			# Case2: Packet with sequence nummber smaller than rcv_base
			elif seq >= (rcv_base-n) and seq <= (rcv_base-1):
				ACK = str(seq)
				clientSocket.sendto(ACK, serverAddress)
	# close the file	
	f.close() 
	
	return byte, countPacket
	
# Initilization phase...
request_Mesg = raw_input("Enter file name: ")
counter = 0
while(1):
	clientSocket.sendto(request_Mesg.decode(), (serverName,serverPort))
	clientSocket.settimeout(2)
	try:
		data, serverAddress = clientSocket.recvfrom(bufferSize)
		clientSocket.settimeout(None)
		print(data.encode())
		
		clientSocket.sendto("thanks",serverAddress)
		clientSocket.settimeout(10)
		try:
# Start receiving data from server
			byte, count = received_Data()
		except timeout as e:
			print "Cannot reach server!"
			
		break
		
	except timeout as err:
		counter += 1
		if counter >= 3:
			print "Request ", err, " ! Cannot reach server."
			break
	

print "Total of ", byte, " bytes received", ". Number of packets were received: ", count
print("Successful received data!")
clientSocket.close()
print("Connection closed...")


