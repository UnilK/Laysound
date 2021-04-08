import tkinter as tk
from tkinter import filedialog
import time
import math
import random

from UI.location_data import *
from UI.tool_bar import ToolBar
from UI.time_line import TimeLine
from UI.location_tool import LocationTool
import UI.canvas_styles as css

import pathlib
import subprocess

import UI.config as config

class RecordPage(tk.Frame):
	def __init__(self, parent, **kwargs):
		tk.Frame.__init__(self, parent, css.grey1Frame, **kwargs)
		
		self.parent = parent
		self.mainFrame = parent

		self.selectedLdot = None
		self.bindEnabled = False

		self.record = False
		self.timeFlow = False
		self.clockSwitch = True

		self.syncTime = 0
		self.syncFrame = 0

		self.frameRate = 147
		self.timestamp = 0

		self.parent = parent
		self.toolBar = ToolBar(self, width=400)
		self.locationTool = LocationTool(self)
		self.timeLine = TimeLine(self, height=200)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)

		self.timeLine.grid(row=0, column=0, columnspan=2, sticky="nwe")
		self.toolBar.grid(row=1, column=1, sticky="nes")
		self.locationTool.grid(row=1, column=0, sticky="wsne")
		
		self.bind("<Key>", lambda x: self.key_down(event=x))
		self.bind("<KeyRelease>", lambda x: self.key_up(event=x))

		self.syncTime = time.time()
		self.after(0, self.clock)

	##################### Utility functions #####################################

	def key_down(self, event):

		if event.keysym == "Shift_L":
			self.locationTool.invertMove = True
			self.timeLine.invertMove = True
		elif event.keysym == "Control_L":
			self.timeLine.enableBarMove = True
			self.locationTool.enableRotate = True
		elif event.keysym == "b" or event.keysym == "B":
			self.bindEnabled = True
		elif event.keysym == "f" or event.keysym == "F":
			self.unselect_ldot()
		elif event.keysym == "r" or event.keysym == "R":
			self.switch_record()
		elif event.keysym == "h" or event.keysym == "H":
			self.switch_ldot_hide()
		elif event.keysym == "l" or event.keysym == "L":
			self.locationTool.switch_labels()
		elif event.keysym == "space":
			self.switch_time_flow()

	def key_up(self, event):
		if event.keysym == "Shift_L":
			self.locationTool.invertMove = False
			self.timeLine.invertMove = False
		elif event.keysym == "Control_L":
			self.timeLine.enableBarMove = False
			self.locationTool.enableRotate = False
		elif event.keysym == "b" or event.keysym == "B":
			self.bindEnabled = False
	
	def tag_number(self):
		
		number = str(self.parent.ldotCount)
		self.parent.ldotCount += 1
		while len(number) < 4:
			number = "0"+number
		return "#"+number

	def new_ldot_update(self):

		self.timeLine.create_ldot(config.project.ldots[len(config.project.ldots)-1])
		self.locationTool.create_ldot(config.project.ldots[len(config.project.ldots)-1])
		self.timeLine.canvasChanged = True
		self.locationTool.canvasChanged = True
	
	########################## Misc #########################################

	def switch_time_flow(self):
			
		if self.timeFlow:
			self.timeFlow = False
			self.toolBar.switchTimeFlowButton.configure(text = "Start")
		else:
			self.syncTime = time.time()
			self.syncFrame = 0
			self.timeFlow = True
			self.toolBar.switchTimeFlowButton.configure(text = "Stop")

	def switch_record(self):

		if self.record:
			self.record = False
			self.toolBar.switchRecordButton.configure(text = "Record")
		else:
			self.record = True
			self.toolBar.switchRecordButton.configure(text = "Stop")
			self.timeLine.ldotMove[0] = self.timeLine.timeMove
	
	############################ Clock ##################################

	def clock(self):

		self.syncFrame += 1
		
		if self.toolBar.sizeChanged:
			self.toolBar.change_width()
			self.toolBar.sizeChanged = False
		
		if self.toolBar.boxSizeChanged:
			self.toolBar.change_box_height()
			self.toolBar.boxSizeChanged = False
		
		if self.timeLine.sizeChanged:
			self.timeLine.change_height()
			self.timeLine.sizeChanged = False
	
		if self.timeFlow:
			self.timestamp += 1
			self.locationTool.canvasChanged = True
			self.timeLine.canvasChanged = True
			self.toolBar.positionChanged = True

		if self.toolBar.damperChangeDirection != 0:
			self.toolBar.toolbox_change_dampering()

		if self.timeLine.canvasChanged:
			self.timeLine.render()
			self.timeLine.canvasChanged = False

		if self.locationTool.canvasChanged:
			self.locationTool.render()
			self.locationTool.canvasChanged = False
			self.locationTool.canvasViewChanged = False

		if self.toolBar.timeLineChanged:
			self.toolBar.toolbox_time_update()
			self.toolBar.timeLineChanged = False
			self.toolBar.positionChanged = True

		if self.toolBar.bindsChanged:
			self.toolBar.toolbox_bind_update()
			self.toolBar.bindsChanged = False
			self.toolBar.positionChanged = True

		if self.toolBar.positionChanged:
			self.toolBar.toolbox_position_update()
			self.toolBar.positionChanged = False

		if self.clockSwitch:
			self.after(
					round(
						1000*max(
							0,
							(1/self.frameRate)*self.syncFrame
							+self.syncTime-time.time()
							)
						),
					self.clock
					)

	######################## Ldot interaction ##########################

	def unselect_ldot(self, event=None):

		if self.selectedLdot != None:
			self.locationTool.unselect_ldot()
			self.timeLine.unselect_ldot()
			self.toolBar.unselect_ldot()
		
		self.selectedLdot = None

		self.locationTool.canvasChanged = True
		self.timeLine.canvasChanged = True
		self.toolBar.toolBoxChanged = True

	def select_ldot(self, ldot, event=None):
		
		self.unselect_ldot()
		self.selectedLdot = ldot

		self.locationTool.select_ldot(ldot)
		self.timeLine.select_ldot(ldot)
		self.toolBar.select_ldot(ldot)
		
		self.locationTool.canvasChanged = True
		self.timeLine.canvasChanged = True
		self.toolBar.toolBoxChanged = True

	def bind_ldot(self, ldot, event=None):
		
		if self.record and self.bindEnabled:
			if ldot == self.selectedLdot:
				ldot.delete_bind(self.timestamp)
			else:
				self.selectedLdot.add_bind(
						self.timestamp,
						self.timestamp+147,
						ldot
						)
			self.locationTool.canvasChanged = True
			self.toolBar.bindsChanged = True
	
	def delete_ldot(self, event=None):
		
		if self.selectedLdot != None:

			index = 0
			position = 0

			for ldot in config.project.ldots:
				if ldot == self.selectedLdot:
					# my problem with the hidden pointers approach:
					position = index+0
				else:
					ldot.seek_and_destroy(self.selectedLdot.tag)
				index += 1
			
			self.locationTool.delete_ldot(self.selectedLdot)
			self.timeLine.delete_ldot(self.selectedLdot)

			self.unselect_ldot()
			config.project.ldots.pop(position)

		self.locationTool.canvasChanged = True
		self.timeLine.canvasChanged = True
		self.toolBar.toolBoxChanged = True

	def switch_ldot_hide(self):
		if self.selectedLdot != None:
			if self.selectedLdot.isHidden:
				self.selectedLdot.isHidden = False
			else:
				self.selectedLdot.isHidden = True

			self.locationTool.canvasChanged = True
	
	def add_free_route(self):

		theta = 2*math.pi*random.random()

		config.project.ldots.append(
				FreeRoute(
					beginTime=self.timestamp,
					endTime=self.timestamp+self.frameRate*10,
					xpos=math.cos(theta),
					ypos=math.sin(theta),
					tag=self.tag_number(),
					slot=len(config.project.ldots),
					bind = self.selectedLdot
					)
				)
		
		self.new_ldot_update()
	
	def add_sound_source(self):

		fileIn = filedialog.askopenfilename(title="select source file", initialdir="audio")

		process = subprocess.run(["./lsapi", "probe", str(fileIn)], capture_output=True)
		
		info = process.stdout.decode().splitlines()

		if info[0] == "OK":

			infoDict = {}

			for i in range(1, len(info)):
				key, value = info[i].split(" ")
				if key != "channel_mask":
					infoDict[key] = int(value)
				else:
					infoDict[key] = str(value)

			infoDict["name"] = fileIn

			theta = 2*math.pi*random.random()

			length = infoDict["data_chunk_size"]/infoDict["byte_rate"]

			config.project.ldots.append(
					SoundSource(
						beginTime=self.timestamp,
						endTime=self.timestamp+math.ceil(147*length),
						xpos=math.cos(theta),
						ypos=math.sin(theta),
						tag=self.tag_number(),
						slot=len(config.project.ldots),
						bind = self.selectedLdot,
						sourceInfo = infoDict
						)
					)
		
			self.new_ldot_update()

		else:
			pass


	def add_listener(self):

		theta = 2*math.pi*random.random()

		config.project.ldots.append(
				Listener(
					beginTime=self.timestamp,
					endTime=self.timestamp+self.frameRate*10,
					xpos=math.cos(theta),
					ypos=math.sin(theta),
					tag=self.tag_number(),
					slot=len(config.project.ldots),
					bind = self.selectedLdot
					)
				)
		
		self.new_ldot_update()
