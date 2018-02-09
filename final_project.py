#!/usr/bin/python
# IOT Security System -- Glen Anderson -- October 2015

import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import RPi.GPIO as GPIO
import time, datetime
import picamera
import sys, os
import signal
import MySQLdb as mdb
import threading
import subprocess

# GPIO setup #
GPIO.setmode(GPIO.BCM) # Pin numbering scheme setup #
GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # Button 2 (12) setup # 
GPIO.setup(8, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # PIR motion sensor (8) setup #
GPIO.setup(25, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Break Beam sensor #
GPIO.setup(20, GPIO.OUT, initial = GPIO.LOW) # Red LED setup #
GPIO.setup(21, GPIO.OUT, initial = GPIO.HIGH) # Green LED setup #
GPIO.setup(16, GPIO.OUT, initial = GPIO.LOW) # Blue LED setup #
GPIO.setup(24, GPIO.IN) # Hall setup #

# Setup database #
										    # password here
try:
	myConnection = mdb.connect("127.0.0.1", "root", "", "security_log")
	myCursor = myConnection.cursor()
except:
	print "\ncouldnt connct to db\n"
	GPIO.output(20, True)
	time.sleep(2)		
	sys.exit(0)

myCursor.execute("DROP TABLE IF EXISTS events")
myCursor.execute("CREATE TABLE events(num INT, pic_path VARCHAR(60), sensor VARCHAR(30), time VARCHAR(40))")
#myConnection.commit()

## Email setup ##

toaddr = ['glen_anderson@student.uml.edu']
usr = "theh0wl.au@gmail.com"
fromaddr = usr

server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()

#put email password here
server.login(usr , '')
#msg = "iasip test"
COMMASPACE = ', '



# Set up lock (no re-entry) so threaded callbacks block for access to camera 
lock = threading.Lock()
	
# Close nicely by releasing all resources #
def signal_handler(signal, frame):

	print "\n---------------\nSignal receieved."
	print "Closing camera..."
	myCamera.close()
	if myCamera.closed:
		print " Camera closed."
	print "Closing database..."
	myConnection.close()
	print" MySQL Database closed."
	print "Closing email server connection..."
	server.quit()
	print " SMTP connection closed."
	print "Now releasing GPIO ports..."		
	GPIO.cleanup()
	print " GPIO ports cleaned.\nNow exiting...\n"
	sys.exit(0)

# register sig handler with ctrl-c or kill #
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

####################
# Define Callbacks #
####################

# global used to keep track of number of events that were triggered
num_events = 0

def door(channel):

#	global myCursor
	global num_events
	num_events += 1

	sensor = "Hall effect"

	# Set up picture path with date/time stamp
	mystr  = "/var/www/pics/"
	time = datetime.datetime.now().strftime('%Y-%m-%d__%H:%M:%S')
	mystr += time
	mystr += ".jpg"
	mystr2 = "./pics/"
	mystr2 +=time
	mystr2 += ".jpg"

	print "\nDoor opened."
	print "Taking picture"
	print "Event num: %d \n" % num_events

	# create database entry and commit it
	myCursor.execute("INSERT INTO events(num, pic_path, sensor, time) VALUES (%s, %s, %s, %s)", (num_events, mystr2, sensor, time))
	myConnection.commit()

	# acquire lock before using camera
	lock.acquire(1)

	# Take picture #
	try:
		myCamera.capture(mystr, 'jpeg')
		myCamera._check_camera_open()

	except (PiCameraError, PiCameraValueError, PiCameraRuntimeError):
		print "camera error, couldn't take picture"
		GPIO.output(20, True)			
		sleep(2)

	# Send out email $
	msg = MIMEMultipart()
	msg['Subject'] = "Security Alert"
	msg['FROM'] = "theh0wl.au@gmail.com";
	msg['To'] = COMMASPACE.join(toaddr)

	text_in = "event from hall sensor detected at "
	text_in += time

#	text = MIMEText(" button detected event at ")
	text = MIMEText(text_in)

	msg.attach(text)
	
	#fp = open("./a.jpg", "rb")
	#img = MIMEImage(fp.read())
	#fp.close()
	img_data = open(mystr, 'rb').read()
	img = MIMEImage(img_data, name=os.path.basename(mystr))
	msg.attach(img)
	
	server.sendmail(fromaddr, toaddr, msg.as_string())
	# moved lock release to after email is sent to avoid errors


	lock.release()
	return

# Button callback function definition #
def button_pressed(channel):

	global num_events
	sensor = "button"
	num_events += 1

	# Set up picture path with date/time stamp
	mystr  = "/var/www/pics/"
	time = datetime.datetime.now().strftime('%Y-%m-%d__%H:%M:%S')
	mystr+= time
	mystr += ".jpg"
	mystr2 = "./pics/"
	mystr2 +=time
	mystr2 += ".jpg"

	print "\nButton pressed."
	print"Taking picture"
	print "Event num: %d \n" % num_events

	myCursor.execute("INSERT INTO events(num, pic_path, sensor, time) VALUES (%s, %s, %s, %s)", (num_events, mystr2, sensor, time))
	myConnection.commit()

	lock.acquire(1)
	# Take picture #
	try:
		myCamera.capture(mystr, 'jpeg')
		myCamera._check_camera_open()

	except (PiCameraError, PiCameraValueError, PiCameraRuntimeError):
		print "camera error, couldn't take picture"
		GPIO.output(20, True)			
		seep(2)

	
	# Send out email $
	msg = MIMEMultipart()
	msg['Subject'] = "Security Alert"
	msg['FROM'] = "theh0wl.au@gmail.com";
	msg['To'] = COMMASPACE.join(toaddr)

	text_in = "event from button detected at "
	text_in += time

#	text = MIMEText(" button detected event at ")
	text = MIMEText(text_in)

	msg.attach(text)
	
	#fp = open("./a.jpg", "rb")
	#img = MIMEImage(fp.read())
	#fp.close()
	img_data = open(mystr, 'rb').read()
	img = MIMEImage(img_data, name=os.path.basename(mystr))
	msg.attach(img)
	
	server.sendmail(fromaddr, toaddr, msg.as_string())
	# moved lock release to after email is sent to avoid errors
	lock.release()

	return

# PIR motion sensor callback function definition #
def motion_detected(channel):

	global num_events
	num_events += 1
	sensor = "PIR Motion"

	# Set up picture path with date/time stamp
	mystr  = "/var/www/pics/"
	time = datetime.datetime.now().strftime('%Y-%m-%d__%H:%M:%S')
	mystr += time
	mystr += ".jpg"
	mystr2 = "./pics/"
	mystr2 +=time
	mystr2 += ".jpg"

	print "\nMotion detected."
	print "Taking picture"
	print "Event num: %d \n" % num_events

	myCursor.execute("INSERT INTO events(num, pic_path, sensor, time) VALUES (%s, %s, %s, %s)", (num_events, mystr2, sensor, time))
	myConnection.commit()

	lock.acquire(1)
	# Take picture #
	try:
		myCamera._check_camera_open()
		myCamera.capture(mystr, 'jpeg')
	except (PiCameraError, PiCameraValueError, PiCameraRuntimeError):
		print "camera error, couldn't take picture"
		GPIO.output(20, True)			
		sleep(2)

	# Send out email $
	msg = MIMEMultipart()
	msg['Subject'] = "Security Alert"
	msg['FROM'] = "theh0wl.au@gmail.com";
	msg['To'] = COMMASPACE.join(toaddr)

	text_in = "event from PIR motion sensor detected at "
	text_in += time

#	text = MIMEText(" button detected event at ")
	text = MIMEText(text_in)

	msg.attach(text)
	
	#fp = open("./a.jpg", "rb")
	#img = MIMEImage(fp.read())
	#fp.close()
	img_data = open(mystr, 'rb').read()
	img = MIMEImage(img_data, name=os.path.basename(mystr))
	msg.attach(img)
	
	server.sendmail(fromaddr, toaddr, msg.as_string())
	# moved lock release to after email is sent to avoid errors
	lock.release()
	
	return

def walkthrough(channel):

	global num_events
	num_events += 1
	sensor = "Break-beam"

	# Set up picture path with date/time stamp
	mystr  = "/var/www/pics/"
	time = datetime.datetime.now().strftime('%Y-%m-%d__%H:%M:%S')
	mystr += time
	mystr += ".jpg"
	mystr2 = "./pics/"
	mystr2 +=time
	mystr2 += ".jpg"

	# display info to screen
	print "\nBeam passed through."
	print "Taking picture"
	print "Event num: %d \n" % num_events	

	# log event info into db
	myCursor.execute("INSERT INTO events(num, pic_path, sensor, time) VALUES (%s, %s, %s, %s)", (num_events, mystr2, sensor, time))
	myConnection.commit()

	lock.acquire(1)

	# Take picture #
	try:
		myCamera.capture(mystr, 'jpeg')
		myCamera._check_camera_open()

	except (PiCameraError, PiCameraValueError, PiCameraRuntimeError):
		print "camera error, couldn't take picture"
		GPIO.output(20, True)			
		seep(2)

	#lock.release
	
	# Send out email $
	msg = MIMEMultipart()
	msg['Subject'] = "Security Alert"
	msg['FROM'] = "theh0wl.au@gmail.com";
	msg['To'] = COMMASPACE.join(toaddr)

	text_in = "event from break-beam detected at "
	text_in += time

#	text = MIMEText(" button detected event at ")
	text = MIMEText(text_in)

	msg.attach(text)
	
	#fp = open("./a.jpg", "rb")
	#img = MIMEImage(fp.read())
	#fp.close()
	img_data = open(mystr, 'rb').read()
	img = MIMEImage(img_data, name=os.path.basename(mystr))
	msg.attach(img)
	
	server.sendmail(fromaddr, toaddr, msg.as_string())
	# moved lock release to after email is sent to avoid errors

	lock.release()

	return

##########
# End Callbacks #
##########

# Initialize camera #
myCamera = picamera.PiCamera()

# Camera capture options
myCamera.resolution = (1024, 768)
myCamera.awb_mode = 'auto'
myCamera.brightness = 50 
myCamera.contrast = 0
myCamera.drc_strength = 'off';
myCamera.exposure_compensation = 0
myCamera.exposure_mode = 'auto'
myCamera.flash_mode = 'off'
myCamera.image_denoise = True
#myCamera.image_effect = 'solarize'
myCamera.vflip = True
myCamera.hflip = True
myCamera.iso = 0
myCamera.saturation = 0
myCamera.sharpness = 7
myCamera.shutter_speed = 0

# Try to shut off camera LED
myCamera.led = False

# Threaded callback functions to wait for edges from sensors #
GPIO.add_event_detect(8, GPIO.RISING, callback = motion_detected)
GPIO.add_event_detect(12, GPIO.RISING, callback = button_pressed, bouncetime = 600)
GPIO.add_event_detect(25, GPIO.FALLING, callback = walkthrough, bouncetime = 600) # Break Beam #
GPIO.add_event_detect(24, GPIO.RISING, callback = door, bouncetime = 600) # Hall #

# keep alive for event detects #
print "\nSystem activated..."
while 1:
	time.sleep(100)

# After loop
print "\nYou shouldn't be here"
GPIO.output(20, TRUE)

