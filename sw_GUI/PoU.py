#!/usr/bin/python3

import sys,os
import time
from time import sleep
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter as tk
import serial
from serial.tools import list_ports as serLP
from multiprocessing import Process, Value, Array, Pool

# CUSTOM WAIT
def waitUntil(target_ts):
	while(time.time()<target_ts):
		sleep(0.0005) # 1ms resolution

# SERIAL CONNECT	
def ttyConnect():
	global entr_tty
	global tty_obj
	tty_obj=None
	global lsTTY
	local_stat = 0
	serID=entr_tty.curselection()
	serTarget=lsTTY[serID[0]]
	try:
		tty_obj = serial.Serial(serTarget, baudrate=115200, writeTimeout = 0)
	except:
		local_stat = 1
		butt_tty.configure(bg="red")
		butt_tty.configure(text="ERROR")
		print("ERROR connecting to "+serTarget)
	if(local_stat==0):
		butt_tty.configure(bg="green")
		butt_tty.configure(text="CONNECTED")
		butt_tty.configure(state=DISABLED)
		entr_tty.configure(state=DISABLED)
		print("CONNECTED to "+serTarget)

def ttySend():
	global entr_byte
	global tty_obj
	tty_arr = [int(entr_byte.get(),16)]
	try:
		tty_obj.write(tty_arr)
	except Exception as e:
		messagebox.showerror("Serial ERROR","Exception: "+repr(e),parent=rootW)

def ttyStroboP(): # Strobo wrapper
	global pt
	if(pt!=None):
		flagStop()
	pt = Process(target=ttyStrobo)
	pt.start()
	
def ttyStrobo():
	global pt
	import serial
	tty_arr0 = [0xFF,0x60,0xF3,0x0A]
	tty_arr1 = [0xFF,0x6F,0xF3,0x0A]
	tsleep = int(entr_strobo.get())/1000
	tsleepH = tsleep*float(entr_stroboT.get())
	tsleepL = tsleep-tsleepH
	target_ts=time.time()
	while(True):
		tty_obj.write(tty_arr1)
		target_ts+=tsleepH
		waitUntil(target_ts)
		tty_obj.write(tty_arr0)
		target_ts+=tsleepL
		waitUntil(target_ts)

def ttyCseqP(): # Organizer wrapper Loop
	global pt
	global pt
	if(pt!=None):
		flagStop()
	pt = Process(target=ttyCseq)
	pt.start()

def ttyCseq():
	import serial
	global isset_org
	target_ts=time.time()
	while(True):
		for istr in isset_org:
			if(istr[0]==1):
				tty_obj.write(istr[1])
			if(istr[0]==2):
				target_ts+=(istr[1]/1000)
				waitUntil(target_ts)

def ttyCseqOnceP(): # Organizer wrapper Once
	global pt
	if(pt!=None):
		flagStop()
	pt = Process(target=ttyCseqOnce)
	pt.start()

def ttyCseqOnce():
	import serial
	global pt
	global isset_org
	target_ts=time.time()
	for istr in isset_org:
		if(istr[0]==1):
			tty_obj.write(istr[1])
		if(istr[0]==2):
			target_ts+=(istr[1]/1000)
			waitUntil(target_ts)

def ttyQuattroP(): # unDostres4 wrapper
	global pt
	if(pt!=None):
		flagStop()
	pt = Process(target=ttyQuattro)
	pt.start()
	
def ttyQuattro():
	import serial
	tty_arr = [0xFF,0xFC,0x60,0x60,0x60,0x60,0xF3,0x0A]
	tsleep = 60/float(entr_quattro.get())
	target_ts=time.time()
	while(True):
		tty_arr = [0xFF,0xFC,0x6F,0x60,0x60,0x60,0xF3,0x0A]
		tty_obj.write(tty_arr)
		target_ts+=tsleep
		#sleep(tsleep)
		waitUntil(target_ts)
		tty_arr = [0xFF,0xFC,0x60,0x6F,0x60,0x60,0xF3,0x0A]
		tty_obj.write(tty_arr)
		target_ts+=tsleep
		#sleep(tsleep)
		waitUntil(target_ts)
		tty_arr = [0xFF,0xFC,0x60,0x60,0x6F,0x60,0xF3,0x0A]
		tty_obj.write(tty_arr)
		target_ts+=tsleep
		#sleep(tsleep)
		waitUntil(target_ts)
		tty_arr = [0xFF,0xFC,0x60,0x60,0x60,0x6F,0xF3,0x0A]
		tty_obj.write(tty_arr)
		target_ts+=tsleep
		#sleep(tsleep)
		waitUntil(target_ts)

def ttyPulseP(): # Pulse wrapper
	global pt
	if(pt!=None):
		flagStop()
	pt = Process(target=ttyPulse)
	pt.start()

def ttyPulse():
	target_ts=time.time()
	global pt
	import serial
	tty_arr = [0xFF,0x60,0xF3,0x0A]
	tsleep = 60/float(entr_pulse.get())
	tsleepOn=0.1*tsleep
	tsleepOff=0.9*tsleep
	while(True):
		tty_arr = [0xFF,0x6F,0xF3,0x0A]
		tty_obj.write(tty_arr)
		target_ts+=tsleepOn
		waitUntil(target_ts)
		tty_arr = [0xFF,0x60,0xF3,0x0A]
		tty_obj.write(tty_arr)
		target_ts+=tsleepOff
		waitUntil(target_ts)

def ttySetL(arrVal):
	global pt
	if(pt!=None):
		flagStop()
	arrData = arrVal.copy()
	v256=[]
	for idx in range(0, len(arrData)):
		p1=arrData[idx]//16
		p2=arrData[idx]-p1*16
		p1+=0x90
		p2+=0x90
		v256+=[p1,p2]
	try:
		tty_obj.write([0xFF]+v256+[0xF3,0x0A])
	except Exception as e:
		messagebox.showerror("Serial ERROR","Exception: "+repr(e),parent=rootW)

### STOP PROCEDURE ###
def flagStop():
	global pt
	if(pt!=None):
		pt.terminate()
		pt=None
	else:
		print("debug: no process running")
	# NOTE: The leading '0x0A' character is used to force exit from any incomplete previous serial stream
	tty_arr = [0x0A,0xFF,0x60,0x60,0x60,0x60,0x60,0x60,0xF3,0x0A]
	try:
		tty_obj.write(tty_arr)
	except Exception as e:
		messagebox.showerror("Serial ERROR","Exception: "+repr(e),parent=rootW)
	print("debug: STOP")

# Default settings
global pt
pt = None
relpath=os.path.dirname(sys.argv[0])

# LOAD CUSTOM ORGANIZER
global isset_org
isset_org = []
rcnt=0
try:
	orgpath = relpath+"/scheduler.ls"
	fobj = open(orgpath, "r")
	for orow in fobj:
		rcnt+=1
		oargs = orow.rstrip().split(" ")
		if(oargs[0]=="SEND"):
			seqb = []
			nseq = len(oargs)
			for i in range(1,nseq):
				seqb+=[int(oargs[i],16)]
			sset=(1,seqb)
			isset_org+=[sset]
		elif(oargs[0]=="WAIT"):
			sset=(2,float(oargs[1]))
			isset_org+=[sset]
		else:
			raise Exception("Token not valid")
except Exception as e:
	messagebox.showerror("Organizer Load ERROR","Row: "+str(rcnt)+"\nException: "+repr(e))

# MAIN WINDOW
global rootW
rootW = tk.Tk()
imglogo128=relpath+"/logo.png"
rootW.geometry("640x480")
rootW.title("Power over UART")
rootW.configure(bg='#007FFF')
try:
	imgF = Image.open(imglogo128)
	imgO = ImageTk.PhotoImage(imgF)
	imgL = tk.Label(rootW, image = imgO, bd = 0)
	imgL.place(x=256,y=350)
except Exception as e:
	messagebox.showerror("Logo Load ERROR","Exception: "+repr(e),parent=rootW)
	

# SECTION 1.1 : SERIAL
global lsTTY
lsTTY = []
for serOBJ in serLP.comports():
	if(serOBJ.hwid!="n/a"):
		lsTTY.append(serOBJ.device)
global entr_tty
entr_tty = tk.Listbox(rootW, selectmode=SINGLE, height=len(lsTTY))
for seritem in lsTTY:
	entr_tty.insert(END, seritem)
entr_tty.place(x=20,y=20,h=30,w=175)
global butt_tty
butt_tty = tk.Button(rootW,text="CONNECT",bg="#0000FF",fg="white",command=ttyConnect)
tk.Button(rootW,text="ERROR",bg="#FF0000",fg="white",command=ttyConnect)
butt_tty.place(x=210,y=20,h=30)

# SECTION 1.2 : EMPTY

# SECTION 2.1 : SEND BYTE
global byte_user
byte_user = StringVar(rootW, value="0xFF")
global entr_byte
entr_byte = tk.Entry(rootW, textvariable = byte_user)
entr_byte.place(x=20,y=70,h=30,w=175)
butt_byte = tk.Button(rootW,text="SEND",command=ttySend)
butt_byte.place(x=210,y=70,h=30,w=50)

# SECTION 2.2 A : SEND CUSTOM SEQUENCE LOOP
butt_cseq = tk.Button(rootW,text="CUST. LOOP",command=ttyCseqP)
butt_cseq.place(x=340,y=70,h=30,w=90)
# SECTION 2.2 B : SEND CUSTOM SEQUENCE ONCE
butt_cseq = tk.Button(rootW,text="CUST. ONCE",command=ttyCseqOnceP)
butt_cseq.place(x=440,y=70,h=30,w=90)

# SECTION 3.1 : BPM 1-2-3-4
global quattro_user
quattro_user = StringVar(rootW, value="120")
global entr_quattro
entr_quattro = tk.Entry(rootW, textvariable = quattro_user)
entr_quattro.place(x=20,y=120,h=30,w=175)
butt_quattro = tk.Button(rootW,text="QUATTRO",command=ttyQuattroP,bg="yellow")
butt_quattro.place(x=210,y=120,h=30)

# SECTION 3.2 : BPM Pulse
global pulse_user
pulse_user = StringVar(rootW, value="120")
global entr_pulse
entr_pulse = tk.Entry(rootW, textvariable = pulse_user)
entr_pulse.place(x=340,y=120,h=30,w=175)
butt_pulse = tk.Button(rootW,text="PULSE",command=ttyPulseP,bg="yellow")
butt_pulse.place(x=530,y=120,h=30)

# SECTION 4.1 : STROBO ms
global strobo_user
strobo_user = StringVar(rootW, value="150")
global stroboT_user
stroboT_user = StringVar(rootW, value="0.1")
global entr_strobo
entr_strobo = tk.Entry(rootW, textvariable = strobo_user)
entr_strobo.place(x=20,y=170,h=30,w=90)
global entr_stroboT
entr_stroboT = tk.Entry(rootW, textvariable = stroboT_user)
entr_stroboT.place(x=120,y=170,h=30,w=75)
butt_strobo = tk.Button(rootW,text="STROBO",command=ttyStroboP,bg="yellow")
butt_strobo.place(x=210,y=170,h=30)

# SECTION 4.2 : MISC COLORS
butt_miscR = tk.Button(rootW,command=lambda: ttySetL([0,255,0,0,0]),bg="#FF0000")
butt_miscR.place(x=340,y=170,h=30,w=30)
butt_miscO = tk.Button(rootW,command=lambda: ttySetL([0,255,127,0,255]),bg="#FF7F00")
butt_miscO.place(x=375,y=170,h=30,w=30)
butt_miscY = tk.Button(rootW,command=lambda: ttySetL([0,255,255,0,255]),bg="#FFFF00")
butt_miscY.place(x=410,y=170,h=30,w=30)
butt_miscG = tk.Button(rootW,command=lambda: ttySetL([0,0,255,0,0]),bg="#00FF00")
butt_miscG.place(x=445,y=170,h=30,w=30)
butt_miscC = tk.Button(rootW,command=lambda: ttySetL([0,0,255,255,0]),bg="#00FFFF")
butt_miscC.place(x=480,y=170,h=30,w=30)
butt_miscB = tk.Button(rootW,command=lambda: ttySetL([0,0,0,255,0]),bg="#0000FF")
butt_miscB.place(x=515,y=170,h=30,w=30)
butt_miscV = tk.Button(rootW,command=lambda: ttySetL([0,255,0,255,0]),bg="#FF00FF")
butt_miscV.place(x=550,y=170,h=30,w=30)
butt_miscW = tk.Button(rootW,command=lambda: ttySetL([255,255,255,255,255]),bg="#FFFFFF")
butt_miscW.place(x=585,y=170,h=30,w=30)

# SECTION -1 : STOP
butt_stop = tk.Button(rootW,text="STOP",command=flagStop,fg='white',bg='red')
butt_stop.place(x=20,y=270,h=30)


rootW.mainloop()
