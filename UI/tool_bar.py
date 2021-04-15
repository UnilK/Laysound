import tkinter as tk
from tkinter import filedialog

import math
import random
import json

from UI.location_data import *
import UI.canvas_styles as css

import UI.config as config

class ToolBar(tk.Frame):
	def __init__(self, parent, **kwargs):
		tk.Frame.__init__(self, parent, css.grey1Frame, **kwargs)
		
		self.parent = parent
		self.mainFrame = parent.parent
		
		self.ldotCount = 0

		self.sizeChanged = False
		self.frameWidth = kwargs["width"]
		self.borderB1State = False
		self.borderMousePosition = []
		
		self.positionChanged = False
		self.timeLineChanged = False
		self.bindsChanged = False

		# toolbox spesific stuff
		self.damperChangeDirection = 0
		# toolBar stuff continues

		self.boxSizeChanged = False
		self.middleB1State = False
		self.middleMousePosition = []
		self.upperFrameHeight = 280
	
		self.toolboxes = {
				"static": ToolboxStatic,
				"free": ToolboxFree,
				"circle": ToolboxCircle,
				"straight": ToolboxStraight,
				"listener": ToolboxListener,
				"source": ToolboxSource
				}

		self.grid_propagate(False)
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(2, weight=1)

		self.border = tk.Frame(self, css.grey0Frame, width=10)
		self.border.bind("<Button-1>", lambda x: self.border_B1_config(event=x, state=True))
		self.border.bind("<ButtonRelease-1>", lambda x: self.border_B1_config(event=x, state=False))
		self.border.bind("<Motion>", self.border_track_mouse)

		self.border.grid(column=0, row=0, rowspan=3, sticky="news")

		self.upperFrame = tk.Frame(self, css.grey1Frame, height=self.upperFrameHeight)
		self.middleBorder = tk.Frame(self, css.grey0Frame, height=10)
		self.toolbox = None

		self.upperFrame.grid_propagate(False)
		self.upperFrame.grid_columnconfigure(0, weight=1)
		self.upperFrame.grid_rowconfigure(20, weight=1)
		
		self.middleBorder.bind(
				"<Button-1>",
				lambda x: self.middle_B1_config(event=x, state=True)
				)
		self.middleBorder.bind(
				"<ButtonRelease-1>",
				lambda x: self.middle_B1_config(event=x, state=False)
				)
		self.middleBorder.bind("<Motion>", self.middle_track_mouse)

		self.upperFrame.grid(column=1, row=0, sticky="news")
		self.middleBorder.grid(column=1, row=1, sticky="news")
		
		self.switchTimeFlowButton = tk.Button(
				self.upperFrame,
				css.grey1Button,
				text="Start",
				command=self.parent.switch_time_flow
				)

		self.switchRecordButton = tk.Button(
				self.upperFrame,
				css.grey1Button,
				text="Record",
				command=self.parent.switch_record
				)



		self.addStaticRouteButton = tk.Button(
				self.upperFrame,
				css.grey1Button,
				text="Static",
				command=self.parent.add_static_route
				)

		self.addFreeRouteButton = tk.Button(
				self.upperFrame,
				css.grey1Button,
				text="Freehand",
				command=self.parent.add_free_route
				)
		
		self.addCircleRouteButton = tk.Button(
				self.upperFrame,
				css.grey1Button,
				text="Circlular",
				command=self.parent.add_circle_route
				)
		
		self.addStraightRouteButton = tk.Button(
				self.upperFrame,
				css.grey1Button,
				text="Straight",
				command=self.parent.add_straight_route
				)

		self.addSoundSourceButton = tk.Button(
				self.upperFrame,
				css.grey1Button,
				text="Sound source",
				command=self.parent.add_sound_source
				)
		
		self.addListenerButton = tk.Button(
				self.upperFrame,
				css.grey1Button,
				text="Listener",
				command=self.parent.add_listener
				)

		self.switchTimeFlowButton.grid(column=0, row=1, sticky="nwse")
		self.switchRecordButton.grid(column=0, row=2, sticky="nwes")

		self.addStaticRouteButton.grid(column=0, row=5, sticky="nwes")
		self.addFreeRouteButton.grid(column=0, row=6, sticky="nwes")
		self.addCircleRouteButton.grid(column=0, row=7, sticky="nwes")
		self.addStraightRouteButton.grid(column=0, row=8, sticky="nwes")
		self.addSoundSourceButton.grid(column=0, row=9, sticky="nwes")
		self.addListenerButton.grid(column=0, row=10, sticky="nwes")

	######################### Utility functions ################################

	def border_B1_config(self, event, state):
		self.borderB1State = state

	def middle_B1_config(self, event, state):
		self.middleB1State = state
	
	def middle_track_mouse(self, event):

		cx, cy = event.x+self.middleBorder.winfo_x(), event.y+self.middleBorder.winfo_y()
		
		if self.middleB1State:
			self.upperFrameHeight = max(1, self.upperFrameHeight+cy-self.middleMousePosition[1])
			self.boxSizeChanged = True

		self.middleMousePosition = [cx, cy]

	def border_track_mouse(self, event):

		cx, cy = event.x+self.winfo_x(), event.y+self.winfo_y()
		
		if self.borderB1State:
			self.sizeChanged = True
			self.frameWidth = max(10, self.frameWidth-cx+self.borderMousePosition[0])

		self.borderMousePosition = [cx, cy]

	def change_width(self):
		self.configure(width=self.frameWidth)

	def change_box_height(self):
		self.upperFrame.configure(height=self.upperFrameHeight)
	
	def entry_key_action(self, event, flags=[]):
		
		if event.keysym == "Return":
			
			self.parent.focus_set()

			if "brushconfig" in flags:
				self.toolbox.change_brush()

			if "straightconfig" in flags:
				self.toolbox.set_config()
			
			if "circleconfig" in flags:
				self.toolbox.set_config()

			if "settime" in flags:
				self.toolbox.set_time()

			if "setposition" in flags:
				self.toolbox.set_position()


	def toolbox_position_update(self):
		if self.toolbox != None:
			self.toolbox.position_update()
	
	def toolbox_time_update(self):
		if self.toolbox != None:
			self.toolbox.time_update()
	
	def toolbox_bind_update(self):
		if self.toolbox != None:
			self.toolbox.bind_update()
	
	def toolbox_change_dampering(self):
		if self.toolbox != None and self.parent.selectedLdot.ldotType == "listener":
			self.toolbox.change_dampering()

	########################## toolbar selection ############################

	def unselect_ldot(self):
		self.toolbox.grid_forget()
		self.toolbox.destroy()
		self.toolbox = None

	def select_ldot(self, ldot):
		self.toolbox = self.toolboxes[ldot.ldotType](self, ldot)
		self.toolbox.grid(column=1, row=2, sticky="news")
		


class ToolboxTemplate(tk.Frame):	
	def __init__(self, parent, ldot, **kwargs):
		tk.Frame.__init__(self, parent, css.grey1Frame, **kwargs)
		
		self.ldot = ldot
		self.parent = parent
		self.recordPage = parent.parent

		self.bindBoxPool = []

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		self.scrollBar = tk.Scrollbar(self, css.scrollBar, orient="vertical", width=20)
		self.scrollBar.grid(column=1, row=0, sticky="sn")

		self.canvas = tk.Canvas(self, css.scrollCanvas)
		
		self.scrollBar.configure(command=self.canvas.yview)
		self.canvas.configure(yscrollcommand=self.scrollBar.set)
		self.canvas.grid(column=0, row=0, sticky="sewn")
				
		self.toolBox = tk.Frame(self.canvas, css.grey1Frame)	
		self.canvas.create_window(0, 0, window=self.toolBox, anchor="nw")

		self.canvas.tag_bind(
				"all", "<Button-4>", 
				lambda x: self.scroll_canvas(event=x, direction=-1)
				)	
		self.canvas.tag_bind(
				"all", "<Button-5>",
				lambda x: self.scroll_canvas(event=x, direction=1)
				)
		
		self.toolBox.grid_columnconfigure(4, weight=1)
		self.toolBox.grid_rowconfigure(20, weight=1)
		
		self.ldotLabel = tk.Label(
				self.toolBox,
				css.grey1BigLabel,
				text=ldot.ldotType+ldot.tag
				)

		self.hideButton = tk.Button(
				self.toolBox,
				css.grey1Button,
				text="O",
				command = self.parent.parent.switch_ldot_hide
				)

		self.deleteButton = tk.Button(
				self.toolBox,
				css.grey1Button,
				text="X",
				command = self.parent.parent.delete_ldot
				)
		
		self.ldotLabel.grid(row=0, column=0, padx=4, pady=4, sticky="nw")
		self.hideButton.grid(row=0, column=1, padx=50, pady=4, sticky="ne")
		self.deleteButton.grid(row=0, column=1, padx=4, pady=4, sticky="ne")

		self.beginVar = tk.IntVar(self)
		self.endVar = tk.IntVar(self)

		self.beginLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="begin timestamp:"
				)

		self.beginEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.beginVar
				)
		
		self.endLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="end timestamp:"
				)

		self.endEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.endVar
				)

		self.setTimeButton = tk.Button(
				self.toolBox,
				css.grey1Button,
				text="set Time",
				command=self.set_time
				)
		
		self.beginLabel.grid(row=1, column=0, padx=4, pady=4, sticky="nw")
		self.beginEntry.grid(row=1, column=1, padx=4, pady=4, sticky="nw")
		self.endLabel.grid(row=2, column=0, padx=4, pady=4, sticky="nw")
		self.endEntry.grid(row=2, column=1, padx=4, pady=4, sticky="nw")
		self.setTimeButton.grid(row=3, column=0, padx=4, pady=4, sticky="nw")
		
		self.beginEntry.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["settime"]))
		self.endEntry.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["settime"]))
		
		self.xVar = tk.DoubleVar(self)
		self.yVar = tk.DoubleVar(self)
		self.rotationVar = tk.DoubleVar(self)

		self.xLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="x position:"
				)

		self.xEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.xVar
				)
		
		self.yLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="y position:"
				)

		self.yEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.yVar
				)

		self.rotationLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="rotation :"
				)

		self.rotationEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.rotationVar
				)

		self.setPositionButton = tk.Button(
				self.toolBox,
				css.grey1Button,
				text="set position",
				command=self.set_position
				)
		
		self.xLabel.grid(row=4, column=0, padx=4, pady=4, sticky="nw")
		self.xEntry.grid(row=4, column=1, padx=4, pady=4, sticky="nw")
		self.yLabel.grid(row=5, column=0, padx=4, pady=4, sticky="nw")
		self.yEntry.grid(row=5, column=1, padx=4, pady=4, sticky="nw")
		self.rotationLabel.grid(row=6, column=0, padx=4, pady=4, sticky="nw")
		self.rotationEntry.grid(row=6, column=1, padx=4, pady=4, sticky="nw")
		self.setPositionButton.grid(row=7, column=0, padx=4, pady=4, sticky="nw")
		
		self.xEntry.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["setposition"]))
		self.yEntry.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["setposition"]))	
		self.rotationEntry.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["setposition"]))
		
		self.bindLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="binds:"
				)

		self.bindFrame = tk.Frame(self.toolBox, css.grey1Frame)
	
		self.bindLabel.grid(row=19, column=0, padx=4, pady=4, sticky="nw")
		self.bindFrame.grid(row=20, column=0, columnspan=3, padx=4, sticky="nw")

		self.parent.positionChanged = True
		self.parent.timeLineChanged = True
		self.parent.bindsChanged = True

	##################### view control #########################

	def scroll_canvas(self, event, direction):
		self.canvas.yview("scroll", direction, "units")

	##################### button actions #######################

	def set_time(self):
		try:
			begin, end = int(self.beginVar.get()), int(self.endVar.get())
			self.ldot.retime(begin, end)
		except (ValueError, tk._tkinter.TclError):
			pass
		
		self.parent.timeLineChanged = True
		self.recordPage.timeLine.canvasChanged = True
		self.recordPage.locationTool.canvasChanged = True

	def set_position(self):
		try:
			x, y = float(self.xVar.get()), float(self.yVar.get())
			r = float(self.rotationVar.get())
			self.ldot.set_absolute_location(self.recordPage.timestamp, x, y)
			self.ldot.set_absolute_rotation(self.recordPage.timestamp, r)
		except (ValueError, tk._tkinter.TclError):
			pass
		
		self.parent.positionChanged = True
		self.recordPage.locationTool.canvasChanged = True

	######################## updates ###########################
	
	def time_update(self):
		begin, end = self.ldot.beginTime, self.ldot.endTime
		self.beginVar.set(begin)
		self.endVar.set(end)

	def position_update(self):	
		x, y, r = self.ldot.get_absolute(self.recordPage.timestamp)
		self.xVar.set(x)
		self.yVar.set(y)
		self.rotationVar.set(r)
	
	def bind_update(self):

		boxRow = 0

		for box in self.bindBoxPool:
			box.grid_forget()

		index = 0

		for bind in self.ldot.bindTimeLine:
			if bind[2] != None:

				if boxRow >= len(self.bindBoxPool):
					self.bindBoxPool.append(
							BindBox(self.bindFrame, self, bind[0], bind[1], bind[2], index)
							)
				else:
					self.bindBoxPool[boxRow].setup(bind[0], bind[1], bind[2], index)

				self.bindBoxPool[boxRow].grid(row=boxRow, column=0, padx=6, pady=4, sticky="nwes")
				self.bindBoxPool[boxRow].update_idletasks()
				boxRow += 1
			index += 1
		
		self.bindFrame.update_idletasks()
		self.toolBox.update_idletasks()
		self.canvas.update_idletasks()
		self.update_idletasks()
		
		region = self.canvas.bbox("all")
		region = (region[0], region[1], region[2], region[3]+10)

		self.canvas.configure(scrollregion=region)

class BindBox(tk.Frame):
	def __init__(self, parent, toolbox, begin, end, ldot, index, **kwargs):
		tk.Frame.__init__(self, parent, css.grey3bindBox, **kwargs)
		
		self.toolbox = toolbox
		self.toolbar = toolbox.parent
		self.parentLdot = ldot
		self.bindedLdot = self.toolbox.ldot
		self.index = index

		self.beginVar = tk.IntVar(self)
		self.endVar = tk.IntVar(self)

		self.beginVar.set(begin)
		self.endVar.set(end)

		self.ldotLabel = tk.Label(
				self,
				css.grey3Label,
				text=self.parentLdot.ldotType+self.parentLdot.tag
				)

		self.upperBorder = tk.Frame(self, css.grey0Frame, height=10)
		self.beginLabel = tk.Label(self, css.grey3Label, text="b:")
		self.beginEntry = tk.Entry(self, css.entryStyle, textvariable=self.beginVar)
		self.endLabel = tk.Label(self, css.grey3Label, text="e:")
		self.endEntry = tk.Entry(self, css.entryStyle, textvariable=self.endVar)
		self.setTimeButton = tk.Button(self, css.grey1Button, text="set", command=self.set_time)
		self.deleteButton = tk.Button(self, css.grey1Button, text="X", command=self.delete_bind)
		self.lowerBorder = tk.Frame(self, css.grey0Frame, height=10)

		self.upperB1State = False
		self.lowerB1State = False
		self.upperMousePosition = 0
		self.lowerMousePosition = 0

		self.upperBorder.bind(
				"<Button-1>", lambda x: self.upper_B1_config(event=x, state=True)
				)
		self.upperBorder.bind(
				"<ButtonRelease-1>", lambda x: self.upper_B1_config(event=x, state=False)
				)
		self.upperBorder.bind("<Motion>", self.upper_track_mouse)

		self.lowerBorder.bind(
				"<Button-1>", lambda x: self.lower_B1_config(event=x, state=True)
				)
		self.lowerBorder.bind(
				"<ButtonRelease-1>", lambda x: self.lower_B1_config(event=x, state=False)
				)
		self.lowerBorder.bind("<Motion>", self.lower_track_mouse)

		self.upperBorder.grid(row=0, column=0, columnspan=3, sticky="ew")
		self.ldotLabel.grid(row=1, column=0, padx=4, pady=4, columnspan=2, sticky="nw")
		self.beginLabel.grid(row=2, column=0, padx=4, pady=4, sticky="nw")
		self.beginEntry.grid(row=2, column=1, padx=4, pady=4, sticky="nw")
		self.endLabel.grid(row=3, column=0, padx=4, pady=4, sticky="nw")
		self.endEntry.grid(row=3, column=1, padx=4, pady=4, sticky="nw")
		self.deleteButton.grid(row=2, column=2, padx=4, pady=4, sticky="nw")
		self.setTimeButton.grid(row=3, column=2, padx=4, pady=4, sticky="nw")
		self.lowerBorder.grid(row=4, column=0, columnspan=3, sticky="ew")

	##################### utility ################################

	def upper_B1_config(self, event, state):
		self.upperB1State = state
	
	def upper_track_mouse(self, event):
		if self.upperB1State:
			self.scroll_time("begin", event.y-self.upperMousePosition)

		self.upperMousePosition = event.y

	def lower_B1_config(self, event, state):
		self.lowerB1State = state
	
	def lower_track_mouse(self, event):
		if self.lowerB1State:
			self.scroll_time("end", event.y-self.lowerMousePosition)

		self.lowerMousePosition = event.y
	
	def setup(self, begin, end, ldot, index):
		self.parentLdot = ldot
		self.beginVar.set(begin)
		self.endVar.set(end)
		self.index = index
		self.ldotLabel.configure(text=self.parentLdot.ldotType+self.parentLdot.tag)

	############################### actions ###########################

	def set_time(self):
		
		try:
			begin, end = int(self.beginVar.get()), int(self.endVar.get())
			end = max(end, begin+1)
	
			self.delete_bind()
			self.bindedLdot.add_bind(begin, end, self.parentLdot)
		
		except (ValueError, tk._tkinter.TclError):
			pass
		
		self.toolbar.bindsChanged = True
		self.toolbar.parent.locationTool.canvasChanged = True

	def delete_bind(self):
		self.bindedLdot.delete_bind(self.bindedLdot.bindTimeLine[self.index][0])
		self.toolbar.bindsChanged = True
		self.toolbar.parent.locationTool.canvasChanged = True

	def scroll_time(self, side, amount):
		
		try:
			begin, end = int(self.beginVar.get()), int(self.endVar.get())
			nbegin, nend = 0, 0

			if side == "begin":
				nbegin = begin+amount
				nend = max(end, nbegin+1)
			if side == "end":
				nend = end+amount
				nbegin = min(begin, nend-1)

			self.beginVar.set(nbegin)
			self.endVar.set(nend)
		except (ValueError, tk._tkinter.TclError):
			pass



class ToolboxStatic(ToolboxTemplate):

	def __init__(self, parent, ldot, **kwargs):
		ToolboxTemplate.__init__(self, parent, ldot, **kwargs)



class ToolboxFree(ToolboxTemplate):

	def __init__(self, parent, ldot, **kwargs):
		ToolboxTemplate.__init__(self, parent, ldot, **kwargs)



class ToolboxCircle(ToolboxTemplate):

	def __init__(self, parent, ldot, **kwargs):
		ToolboxTemplate.__init__(self, parent, ldot, **kwargs)

		self.radiusVar = tk.StringVar(self)
		self.angleVar = tk.StringVar(self)
		self.rotationSpeedVar = tk.StringVar(self)

		self.radiusVar.set(self.ldot.radius)
		self.angleVar.set(self.ldot.rotation)
		self.rotationSpeedVar.set(self.ldot.rotationSpeed)

		self.radiusLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="radius:"
				)

		self.radiusEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.radiusVar
				)
		
		self.angleLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="initial angle:"
				)

		self.angleEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.angleVar
				)
		
		self.rotationSpeedLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="speed:"
				)

		self.rotationSpeedEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.rotationSpeedVar
				)
		
		self.radiusEntry.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["circleconfig"]))
		self.angleEntry.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["circleconfig"]))
		self.rotationSpeedEntry.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["circleconfig"]))
		
		self.radiusLabel.grid(row=10, column=0, padx=4, pady=4, sticky="nw")
		self.radiusEntry.grid(row=10, column=1, padx=4, pady=4, sticky="nw")
		self.angleLabel.grid(row=11, column=0, padx=4, pady=4, sticky="nw")
		self.angleEntry.grid(row=11, column=1, padx=4, pady=4, sticky="nw")
		self.rotationSpeedLabel.grid(row=12, column=0, padx=4, pady=4, sticky="nw")
		self.rotationSpeedEntry.grid(row=12, column=1, padx=4, pady=4, sticky="nw")

	def set_config(self):
		
		try:
			self.ldot.set_config(radius=float(self.radiusVar.get()))
		except ValueError:
			pass
		
		try:
			self.ldot.set_config(rotation=float(self.angleVar.get()))
		except ValueError:
			pass
		
		try:
			self.ldot.set_config(rotationSpeed=float(self.rotationSpeedVar.get()))
		except ValueError:
			pass
		
		self.radiusVar.set(self.ldot.radius)
		self.angleVar.set(self.ldot.rotation)
		self.rotationSpeedVar.set(self.ldot.rotationSpeed)

		self.parent.positionChanged = True
		self.recordPage.locationTool.canvasChanged = True



class ToolboxStraight(ToolboxTemplate):

	def __init__(self, parent, ldot, **kwargs):
		ToolboxTemplate.__init__(self, parent, ldot, **kwargs)
		
		self.directionVar = tk.StringVar(self)
		self.speedVar = tk.StringVar(self)

		self.directionVar.set(self.ldot.direction)
		self.speedVar.set(self.ldot.speed)

		self.directionLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="direction:"
				)

		self.directionEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.directionVar
				)
		
		self.speedLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="speed:"
				)

		self.speedEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.speedVar
				)
		
		self.directionEntry.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["straightconfig"]))
		self.speedEntry.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["straightconfig"]))
		
		self.directionLabel.grid(row=10, column=0, padx=4, pady=4, sticky="nw")
		self.directionEntry.grid(row=10, column=1, padx=4, pady=4, sticky="nw")
		self.speedLabel.grid(row=11, column=0, padx=4, pady=4, sticky="nw")
		self.speedEntry.grid(row=11, column=1, padx=4, pady=4, sticky="nw")

	def set_config(self):
		
		try:
			self.ldot.set_config(direction=float(self.directionVar.get()))
		except ValueError:
			pass
		
		try:
			self.ldot.set_config(speed=float(self.speedVar.get()))
		except ValueError:
			pass
		
		self.directionVar.set(self.ldot.direction)
		self.speedVar.set(self.ldot.speed)
		
		self.parent.positionChanged = True
		self.recordPage.locationTool.canvasChanged = True



class ToolboxListener(ToolboxTemplate):

	def __init__(self, parent, ldot, **kwargs):
		ToolboxTemplate.__init__(self, parent, ldot, **kwargs)

		self.damperChangeDirection = 0
		self.damperMousePosition = [0, 0]
		
		self.brushSize = 10
		self.brushPower = 0.005

		self.brushPowerVar = tk.StringVar(self)
		self.brushSizeVar = tk.StringVar(self)

		self.channelVar = tk.IntVar()
		self.channelVar.set(ldot.channel)

		self.channelLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="channel:"
				)

		self.channelEntry = tk.Entry(
				self.toolBox,
				css.entryStyle,
				textvariable=self.channelVar
				)

		self.setChannelButton = tk.Button(
				self.toolBox,
				css.grey1Button,
				text="set channel",
				command=self.set_channel
				)

		self.channelLabel.grid(row=10, column=0, padx=4, pady=4, sticky="nw")
		self.channelEntry.grid(row=10, column=1, padx=4, pady=4, sticky="nw")
		self.setChannelButton.grid(row=11, column=0, padx=4, pady=4, sticky="nw")
		
		self.damperDimensions = [360, 360]

		self.damperProfileLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="damper profile:"
				)

		self.brushSizeLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="brush size:"
				)
		
		self.brushPowerLabel = tk.Label(
				self.toolBox,
				css.grey1Label,
				text="brush power:"
				)

		self.brushSizeSpin = tk.Spinbox(
				self.toolBox,
				css.grey1SpinBox,
				increment=1,
				textvariable=self.brushSizeVar,
				command=self.change_brush
				)
		
		self.brushPowerSpin = tk.Spinbox(
				self.toolBox,
				css.grey1SpinBox,
				increment=0.001,
				textvariable=self.brushPowerVar,
				command=self.change_brush
				)
		
		self.brushSizeSpin.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["brushconfig"]))
		self.brushPowerSpin.bind("<Key>",
				lambda x: self.parent.entry_key_action(event=x, flags=["brushconfig"]))
		
		self.profileButtonFrame = tk.Frame(self.toolBox, css.grey1Frame)
		self.profileButtonFrame.grid_columnconfigure(5, weight=1)
		self.profileButtonFrame.grid_rowconfigure(1, weight=1)

		self.loadProfileButton = tk.Button(
				self.profileButtonFrame,
				css.grey1Button,
				text="load",
				command=self.load_profile
				)
		
		self.saveProfileButton = tk.Button(
				self.profileButtonFrame,
				css.grey1Button,
				text="save",
				command=self.save_profile
				)
		
		self.mirrorProfileButton = tk.Button(
				self.profileButtonFrame,
				css.grey1Button,
				text="mirror",
				command=self.mirror_profile
				)
		
		self.brushPowerVar.set(self.brushPower)
		self.brushSizeVar.set(self.brushSize)

		self.damperCanvas = tk.Canvas(
				self.toolBox,
				background="#555",
				highlightthickness=0,
				width=self.damperDimensions[0],
				height=self.damperDimensions[1]
				)

		self.damperCanvas.bind("<Motion>", self.damper_track_mouse)
		self.damperCanvas.bind(
				"<Button-1>", lambda x: self.damper_direction_config(event=x, direction=1))
		self.damperCanvas.bind(
				"<Button-3>", lambda x: self.damper_direction_config(event=x, direction=-1))
		self.damperCanvas.bind(
				"<ButtonRelease-1>", lambda x: self.damper_direction_config(event=x, direction=-1))
		self.damperCanvas.bind(
				"<ButtonRelease-3>", lambda x: self.damper_direction_config(event=x, direction=1))

		self.damperProfileLabel.grid(row=12, column=0, padx=4, pady=4, sticky="nw")
		
		self.brushSizeLabel.grid(row=13, column=0, padx=4, pady=4, sticky="nw")
		self.brushSizeSpin.grid(row=13, column=1, padx=4, pady=4, sticky="nw")
		
		self.brushPowerLabel.grid(row=14, column=0, padx=4, pady=4, sticky="nw")
		self.brushPowerSpin.grid(row=14, column=1, padx=4, pady=4, sticky="nw")
		
		self.profileButtonFrame.grid(row=15, column=0, columnspan=5, sticky="news")
		self.saveProfileButton.grid(row=0, column=0, padx=4, pady=4, sticky="nw")
		self.loadProfileButton.grid(row=0, column=1, padx=4, pady=4, sticky="nw")
		self.mirrorProfileButton.grid(row=0, column=2, padx=4, pady=4, sticky="nw")

		self.damperCanvas.grid(row=17, column=0, columnspan=2, padx=4, pady=4, sticky="nw")

		self.damperDotSize = 5
		self.damperDotList = [None]*256

		for index in range(0, 256):

			self.damperDotList[index] = self.damperCanvas.create_oval(
					0, 0, 0, 0,
					css.damperDotStyle
					)

			self.set_damper_dot(index, self.ldot.damperProfile[index])
	
			
		self.bindFrame.update_idletasks()
		self.toolBox.update_idletasks()
		self.canvas.update_idletasks()
		self.update_idletasks()
		
		region = self.canvas.bbox("all")
		region = (region[0], region[1], region[2], region[3]+10)
		self.canvas.configure(scrollregion=region)

	######################## utility ##############################

	def damper_direction_config(self, event=None, direction=0):
		self.damperChangeDirection += direction
		self.parent.damperChangeDirection = self.damperChangeDirection
	
	def damper_track_mouse(self, event):
		
		self.damperMousePosition = [
				self.damperCanvas.canvasx(event.x),
				self.damperCanvas.canvasy(event.y)
				]
	

	##################### damper profile interaction ##################

	def set_damper_dot(self, index, radius):
		
		radius = max(0, min(1, radius))
		self.ldot.damperProfile[index] = radius

		theta = 2*math.pi*index/256
		x = (self.damperDimensions[0]/2-20)*radius*math.cos(theta)+self.damperDimensions[0]/2
		y = (self.damperDimensions[1]/2-20)*radius*math.sin(theta)+self.damperDimensions[1]/2

		self.damperCanvas.coords(
				self.damperDotList[index],
				x-self.damperDotSize, y-self.damperDotSize,
				x+self.damperDotSize, y+self.damperDotSize
				)
		
	def change_dampering(self):
			
		x, y = self.damperMousePosition
			
		x -= self.damperDimensions[0]/2
		y -= self.damperDimensions[1]/2

		top = math.atan(y/(x+1e-9))
			
		if top*y < 0:
			top += math.pi

		if top < 0:
			top += 2*math.pi

		top = round((top/math.pi)*128)

		for index in range(-128, 128):
			
			pos = index/self.brushSize
			index = top+index

			if index < 0:
				index += 256
			elif index >= 256:
				index -= 256

			newRadius = (
					self.ldot.damperProfile[index]
					+math.exp(-pos*pos)*self.brushPower*self.damperChangeDirection
					)

			self.set_damper_dot(index, newRadius)

	def change_brush(self, event=None):
		
		try:
			self.brushSize = float(self.brushSizeVar.get())
			self.brushPower = float(self.brushPowerVar.get())
		except:
			pass
		
		self.brushSizeVar.set(self.brushSize)
		self.brushPowerVar.set(self.brushPower)
	
	def mirror_profile(self):
		
		oldProfile = self.ldot.damperProfile.copy()

		for i in range(0, 256):
			o = i+0
			i = 127-i
			if i < 0:
				i+=256
			self.ldot.damperProfile[i] = oldProfile[o]

		self.change_dampering()

		

	def save_profile(self):
		
		fileOut = filedialog.asksaveasfilename(title="save profile", initialdir="damperProfiles")

		if not fileOut.endswith(".dmp"):
			fileOut += ".dmp"

		if fileOut != "":
			with open(fileOut, "w") as file_out:
				file_out.write(json.dumps(self.ldot.damperProfile))

	def load_profile(self):
		
		fileIn = filedialog.askopenfilename(title="load profile", initialdir="damperProfiles")
		
		if fileIn != "":
			with open(fileIn, "r") as file_in:
				self.ldot.damperProfile = json.load(file_in)

			self.change_dampering()

	######################### misc ##############################


	def set_channel(self):

		try:
			self.ldot.channel = max(0, min(17, int(self.channelVar.get())))
		except (ValueError, tk._tkinter.TclError):
			pass

		self.channelVar.set(self.ldot.channel)


class ToolboxSource(ToolboxTemplate):

	def __init__(self, parent, ldot, **kwargs):
		ToolboxTemplate.__init__(self, parent, ldot, **kwargs)
