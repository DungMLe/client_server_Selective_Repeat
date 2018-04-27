from socket import *
import json
import time
import errno

class packets(object):
	def __init__(self,data, isReceived, time, seq, startTime):
		self.data = data
		self.isReceived = isReceived
		self.seq = seq
		self.timeOut = time
		self.startTime = startTime
		
	def setTimer(self, smallTimeOut):
		self.smallTimeOut = smallTimeOut
		self.timeOut -= self.smallTimeOut
		print "self.timeOut = ", str(self.timeOut), "seq = ", str(self.seq)
		if self.timeOut <= 0.0:
			return True
			
	def setStartTime(self,t):
		self.startTime = t
		
	def sampleTime(self):
		self.sampleTime = time.time() - self.startTime
		return self.sampleTime
			

n = 5		
def nextText(f, seq, send_base):
	text = ""
	if (seq >= send_base and seq <= (send_base+n-1)):
		text = f.read(bufferSize)
	
	return text
	
def calulateTimeOut(sampleRTT):
	global estimatedRTT
	global devRTT
	alpha, beta = 0.125, 0.25
	estimatedRTT = (1-alpha) * estimatedRTT + alpha * sampleRTT
	devRTT = (1 - beta) * devRTT + beta * abs(estimatedRTT-sampleRTT)
	timeOut = estimatedRTT + 4*devRTT
	return timeOut
	
def moveSendBase(send_base, send_window):
	while True:
		if (send_base + 1) in send_window and (send_window[send_base + 1].isReceived == True):
				send_base += 1 # increase base by 1
		else:
			break
	send_base += 1
	
	return send_base
	
def sendData(rcvMesg, timeOutInterval):
	send_base, seq, ack = 0, 0, 0
	smallTimeOut = 0
	isTimeOut = False
	global clientAddress
	
	send_window = {}
	#packets = []
	try:
		with open(rcvMesg, 'r') as f:
			newText = nextText(f, seq, send_base)
			send_window[seq] = packets(newText, False, timeOutInterval, seq, time.time())
			data = json.dumps({"seq":seq, "data": newText})
			while (newText):
				# Send n packets at the same time
				
				smallTimeOut = timeOutInterval/2
				print "Seq = ", str(seq)
				#if len(send_window) <= 5:
				serverSocket.sendto(data.encode(), clientAddress)
				
						
					
				if isTimeOut == True:
					if sequence in send_window:
						print "Resent Seq = ", str(sequence)
						send_window[sequence].setStartTime(time.time())
					
				
				seq += 1 # Increase sequence number by 1
				serverSocket.settimeout(smallTimeOut)
				try:
				# One of the packets is received...
					
					ack, clientAddress = serverSocket.recvfrom(bufferSize)
					serverSocket.settimeout(None)
							
					# The ack for the packet is received
					ACK = (int)(ack)
					print "ACK = ", ack
					send_window[ACK].isReceived = True
					# If packet's seq number is equal to send_base
					if ACK == send_base:
						sampleRTT = send_window[ACK].sampleTime()
						timeOutInterval = calulateTimeOut(sampleRTT)
						send_base = moveSendBase(send_base, send_window)
						print "send_base = ", send_base
						#del send_window[ACK]
						
					#send_window[ACK].isReceived = True
					if len(send_window) > 5:
						if ACK <= (send_base-1):
							del send_window[ACK]
						
				except timeout as e:
					print "Error: ", e 
					serverSocket.settimeout(None)
					for sequence in send_window:
						pac = send_window.get(sequence)
						if pac.isReceived == False:
							print "smallTimeOut = ", smallTimeOut
							isTimeOut = pac.setTimer(smallTimeOut)
							if isTimeOut == True:
								print "Time Out"
								data = json.dumps({"seq":pac.seq, "data": pac.data})
								#print "Resent Seq = ", str(sequence)
								break
					if isTimeOut == True:
						continue
				
				#if len(send_window) <= 5:
				# Create new text to send
				print "len_window = ", len(send_window)
				newText = nextText(f, seq, send_base)
				# packet will be sent and not acked
				send_window[seq] = packets(newText, False, timeOutInterval, seq, time.time())
				data = json.dumps({"seq":seq, "data": newText})
				#print newText
					
		f.close()	
		
	except IOError as e:
		print "Error is ", e
		print "File ", recvMesg, " is not found!"
		return False
		
	return True
	
serverPort = 6000
bufferSize = 1024
alpha, beta = 0.125, 0.25


while True:
	serverSocket = socket(AF_INET, SOCK_DGRAM)
	serverSocket.bind(('',serverPort))
	startTime, endTime, sampleRTT = 0, 0, 0
	estimatedRTT, devRTT, timeOutInterval = 0, 0.005, 0
	
	print "Server is ready to receive..."
	
	try:
		recvMesg, clientAddress = serverSocket.recvfrom(bufferSize)
	except Exception as e:
		time.sleep(0.01)
		continue

		
	print "Receiving request for: ", recvMesg.decode()
	
	# Initialization Phase...
	initMesg = "Server has acceptted connection. Sending data...!\n"
	serverSocket.sendto(initMesg.encode(), clientAddress)
	startTime = time.time()
	serverSocket.settimeout(2)
	try:
		rcvMesg, clientAddress = serverSocket.recvfrom(bufferSize)
		serverSocket.settimeout(0)
		endTime = time.time()
		# Calculated initial timeOutInterval
		sampleRTT = endTime - startTime
		estimatedRTT = sampleRTT
		timeOutInterval = estimatedRTT + 4*devRTT
		# Start to send data...
		if rcvMesg == "thanks":
			b = sendData(recvMesg, timeOutInterval)
		
		
		print(b)
		endMesg = json.dumps({"seq":0, "data": "y"})
		serverSocket.sendto(endMesg.encode(), clientAddress)
		
	except timeout as err:
		print "Session expired!"
		
	serverSocket.settimeout(0)
	#serverSocket.close()









	