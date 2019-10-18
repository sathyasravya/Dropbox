import socket
import os
import random
import re
from datetime import datetime
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter#process_pdf
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

from cStringIO import StringIO

def pdf_with_pro(pdf_name):

	# PDFMiner boilerplate
	term = "Programmer"
	rsrcmgr = PDFResourceManager()
	sio = StringIO()
	codec = 'utf-8'
	laparams = LAParams()
	device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
	interpreter = PDFPageInterpreter(rsrcmgr, device)

	# Extract text
	#pdf_name = "'" + pdf_name + "'"
	fp = file(pdf_name, 'rb')
	for page in PDFPage.get_pages(fp):
		interpreter.process_page(page)
	fp.close()

	# Get text from StringIO
	text = sio.getvalue()
	#print text
	if re.search(term, text):
		#print "hi"
		return 10

	# Cleanup
	device.close()
	sio.close()
	return 0



def create_port(socket):
	np = random.randint(1000, 9999)
	try:
		socket.bind((host, np))
	except:
		return create_port(socket)
	return np



def findpro(fyl):
	term = "Programmer"
	file = open(fyl, "r")
	for line in file:
		# print line
		line.strip().split('/n')
		if term in line:
			return 10
	file.close()
	return 0

def longlist(s):
	files = os.popen("find . -not -path '*/\.*' -type f").read().split('\n')
	if len(files) == 1:
		s.send("No Files Found")
		return
	try:
		for j in files:
			if re.search('.txt', j):
				#print j
				if j != "":
					k = j[2:]
					#k = '"'+ k + '"'
					#print k
					if findpro(k) == 10:
						j = '"'+ j + '"'
						cmd = "stat --printf 'name: %n \tSize: %s bytes\t Type: %F\t Timestamp:%z\n' " + j
						res = os.popen(cmd).read()
						print res
						s.send(res)
						if s.recv(1024) != "received":
							break
		s.send(" ")
		s.recv(1024)
		s.send("done")
	except:
		print "Bad Connection Error"
		return


def shortlist(s, inp):
	inp = inp.split()
	time1 = inp[2] + " " + inp[3]
	time2 = inp[4] + " " + inp[5]
	files = os.popen("find %s -newermt %s ! -newermt  %s -not -path '*/\.*' -type f" % (
		".", str('"' + time1 + '"'), str('"' + time2 + '"'))).read().split('\n')
	#print files
	if len(files) == 1:
		s.send("No Files Found")
		#s.recv(1024)
		s.send("done")
		return
	try:
		for j in files:
			if re.search('.pdf', j) or re.search('.txt', j):
				#print j
				if j != "":
					j = '"' + j + '"'
					cmd = "stat --printf 'name: %n \tSize: %s bytes\t Type: %F\t Timestamp:%z\n' " + j
					res = os.popen(cmd).read()
					s.send(res)
					if s.recv(1024) != "received":
						break
		s.send(" ")
		s.recv(1024)
		s.send("done")
		return
	except:
		print "Bad Connection Error"
		return


def verify(s, filenam, fl=True):
	filename = '"' + filenam + '"'
	cmd = "stat --printf '%z\n' " + filename
	t = os.popen(cmd).read().split('\n')[0]
	if t == "":
		s.send("No Such File")

	else:
		try:
			cmd = "cksum " + filename
			h = os.popen(cmd).read().split('\n')[0].split()[0]
			h = "checksum: " + h + "\n"
			t = "last modified: " + t
			res = [t, h]
			print h
			print t
			for i in res:
				s.send(i)
				if s.recv(1024) != "received":
					break

		except:
			print "Bad Connection Error"
			return
def verfy(s, filenam, fl=True):
	filename = '"' + filenam + '"'
	cmd = "stat --printf '%z\n' " + filename
	t = os.popen(cmd).read().split('\n')[0]
	if t == "":
		s.send("No Such File")

	else:
		try:
			cmd = "cksum " + filename
			h = os.popen(cmd).read().split('\n')[0].split()[0]
			h = "checksum: " + h + "\n"
			t = "last modified: " + t
			str = "file: " + filenam
			res = [str, t, h]
			for i in res:
				s.send(i)
				if s.recv(1024) != "received":
					break

		except:
			print "Bad Connection Error"
			return


def file_send(s, args):
	inp = args.split()
	flag = inp[1]
	filename = " ".join(inp[2:])
	err = os.popen('ls "' + filename + '"').read().split('\n')[0]
	if err == "":
		s.send("No Such File or Directory")
		return
	s.send("received")
	if flag == "UDP":
		ncs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		nport = create_port(ncs)
		s.send(str(nport))
		data, addr = ncs.recvfrom(1024)
		if data == "received":
			try:
				f = open(filename, "rb")
				byte = f.read(1024)
				while byte:
					ncs.sendto(byte, addr)
					data, addr = ncs.recvfrom(1024)
					if data != "received":
						break
					byte = f.read(1024)
				ncs.sendto("done", addr)
			except:
				print "Bad Connection Error"
				return

	elif flag == "TCP":
		try:
			f = open(filename, "rb")
			byte = f.read(1024)
			while byte:
				s.send(byte)
				if s.recv(1024) != "received":
					break
				byte = f.read(1024)
			s.send("done")
		except:
			print "Bad Connection Error"
			return
	else:
		print "Wrong Arguments"
		return
	hash = os.popen('md5sum "' + filename + '"').read().split()[0]
	s.send(hash)
	cmd = "stat --printf 'name: %n \tSize: %s bytes\t Timestamp:%z\n' " + filename
	res = os.popen(cmd).read()
	if s.recv(1024) == "sendme":
		s.send(res)
		print "Done"


def checkall(s):
	files = os.popen("find . -not -path '*/\.*' -type f").read().split('\n')
	for i in files:
		if i != "":
			verfy(s, i, False)
	s.send("done")


# Main Code

port = input("PORT: ")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "0.0.0.0"
try:
	s.bind((host, port))
except:
	print "Socket creation Error"
	exit(0)
s.listen(5)
shared = raw_input("FullPath of Shared Folder: ")

try:
	log = open("server_log.log", "a+")
except:
	print "Cannot Open Log file"
	exit(0)

if not os.path.exists(shared):
	print "No Such Folder"
	exit(0)
elif not os.access(shared, os.R_OK):
	print "No Privilleges"
	exit(0)
else:
	os.chdir(shared)

print "Directory changed"
print "Server is Up and Listening"
times = datetime.now().strftime("%I:%M%p %B %d, %Y")
log.write("********* Server Started at " + times + " *********\n\n")
while True:
	try:
		cs, addr = s.accept()
	except:
		s.close()
		print
		print "Bye"
		timel = datetime.now().strftime("%I:%M%p %B %d, %Y")
		log.write("\n********* Server Closed at " + timel + " *********\n\n")
		log.close()
		exit(0)
	cnt = 0
	time = datetime.now().strftime("%I:%M%p %B %d, %Y")
	print("Got a connection from %s" % str(addr))
	log.write("------- Got a connection from " + str(addr) + "at " + time + " -------\n Commands Executed:\n")
	while True:
		cnt += 1
		try:
			args = cs.recv(1024)
			log.write(str(cnt) + ". " + args + "\n")
		except:
			print "Connection closed to client"
			timel = datetime.now().strftime("%I:%M%p %B %d, %Y")
			log.write("------- Connection Closed at " + timel + " -------\n")
			break
		p = args.split()
		if len(p) == 0 or p[0] == "close":
			cs.close()
			print "Connection closed to client"
			timel = datetime.now().strftime("%I:%M%p %B %d, %Y")
			log.write("------- Connection Closed at " + timel + " -------\n")
			break
		elif p[0] == "IndexGet":
			if p[1] == "longlist":
				# long list
				longlist(cs) 
			elif len(p) == 6:
				shortlist(cs, args)
			elif p[1] == "shortlist":
				try:
					cs.send("Syntax error")
					cs.send("Input Format IndexGet shotlist date1 time1 date2 time2")
					cs.send("done")
				except:
					print "Connection Error"
					break
		elif p[0] == "FileHash":
			if p[1] == "verify":
				verify(cs, p[2])
				cs.send("done")
			elif p[1] == "checkall" and len(p) == 2:
				checkall(cs)
			else:
				try:
					cs.send("Invalid Arguments")
					cs.send("done")
				except:
					print "Connection Error"
					break
		elif p[0] == "FileDownload":
			file_send(cs, args)
		else:
		#   cs.send("Invalid Command")
			cs.send("done")
	cs.close()
