import tkinter as tk
import time
import math
import random

import canvas_styles as css

class TimeLine(tk.Frame):
	def __init__(self, parent, **kwargs):
		tk.Frame.__init__(self, parent, css.grey1Frame, **kwargs)
		
		self.parent = parent
		self.mainFrame = parent.parent
		
		self.frameRate = parent.frameRate

		self.borderMousePosition = [0, 0]
		self.borderB1State = False

		self.sizeChanged = False
		self.frameHeight = kwargs["height"]

		self.canvasMousePosition = [0, 0]
		self.canvasB1State = False
		self.canvasB3State = False

		self.enableBarMove = False
		self.dragDotGrabbed = False
		self.invertMove = False
		self.canvasChanged = True

		self.offset = [150, 50]
		self.slotSize = 26
		self.barSize = 11
		self.dragDotSize = 8
		self.timeCompress = 1
		self.scrollSpeed = 1.1
		self.timeMove = 0
		self.ldotMove = [0, 0]
		self.ldotTimeDrag = 0

		self.gridLinePool = []

		self.grid_propagate(False)
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(1, weight=1)
		
		self.border = tk.Frame(self, css.grey0Frame, height=10)
		self.border.bind("<Button-1>", lambda x: self.border_B1_config(event=x, state=True))
		self.border.bind("<ButtonRelease-1>", lambda x: self.border_B1_config(event=x, state=False))
		self.border.bind("<Motion>", self.border_track_mouse)

		self.canvas = tk.Canvas(
				self,
				background="#555",
				highlightthickness=0
				)

		self.dummyBottom = self.canvas.create_line(
				0, 0, 0, 0,
				tags = ("bottomTag"),
				state = "hidden"
				)


		self.timeIndicator = self.canvas.create_line(
				0, 0, 0, 0,
				fill = "#a85",
				width = 3
			)
		
		self.dragDot = self.canvas.create_oval(
				0, 0, 0, 0,
				css.dragDot,
				state = "hidden"
				)
		
		self.dummyTop = self.canvas.create_line(
				0, 0, 0, 0,
				tags = ("topTag"),
				state = "hidden"
				)
		
		self.scaleIndicator = self.canvas.create_text(
				10, 10,
				anchor = "nw",
				text = "scale: 10^0",
				fill = "#ddd",
				font = css.helvetica14
				)
		
		self.timestampIndicator = self.canvas.create_text(
				120, 10,
				anchor = "nw",
				text = "timestamp: 0",
				fill = "#ddd",
				font = css.helvetica14
				)
		

		self.canvas.tag_bind(
				self.dragDot,
				"<Button-3>", 
				lambda x: self.grab_drag_dot(event=x, state=True)
				)
		self.canvas.tag_bind(
				self.dragDot,
				"<ButtonRelease-3>", 
				lambda x: self.grab_drag_dot(event=x, state=False)
				)
		
		self.canvas.bind("<Button-1>", lambda x: self.canvas_B1_config(event=x, state=True))
		self.canvas.bind("<Button-3>", lambda x: self.canvas_B3_config(event=x, state=True))
		self.canvas.bind("<ButtonRelease-1>", lambda x: self.canvas_B1_config(event=x, state=False))
		self.canvas.bind("<ButtonRelease-3>", lambda x: self.canvas_B3_config(event=x, state=False))
		
		self.canvas.bind("<Button-4>", lambda x: self.zoom(event=x, zoomIn=False))	
		self.canvas.bind("<Button-5>", lambda x: self.zoom(event=x, zoomIn=True))
		
		self.canvas.bind("<Configure>", self.refresh_canvas)
		self.canvas.bind("<Motion>", self.canvas_track_mouse)
		
		self.canvas.grid(column=1, row=1, sticky="nesw")
		self.border.grid(column=0, row=2, columnspan=20, sticky="nwes")

	################## Utility functions & misc #####################

	def border_B1_config(self, event, state):
		self.borderB1State = state

	def canvas_B1_config(self, event, state):
		self.canvasB1State = state
		self.parent.focus_set()
	
	def canvas_B3_config(self, event, state):
		self.canvasB3State = state
		self.parent.focus_set()
	
	def refresh_canvas(self, event=None):
		self.canvasChanged = True
	
	def border_track_mouse(self, event):

		cx, cy = event.x+self.border.winfo_x(), event.y+self.border.winfo_y()
		
		if self.borderB1State:
			self.frameHeight = max(10, self.frameHeight+cy-self.borderMousePosition[1])
			self.sizeChanged = True

		self.borderMousePosition = [cx, cy]
	
	def canvas_track_mouse(self, event):
		
		px, py = self.canvasMousePosition
		cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		self.canvasMousePosition = [cx, cy]
	
		if self.canvasB1State:
			self.move_canvas(cx-px, cy-py)
		if self.dragDotGrabbed:
			self.drag_ldot_time(cx-px)
		elif self.canvasB3State:
			self.move_time(cx-px)
			if self.enableBarMove:
				self.drag_ldot(cx-px, cy-py)

	def grab_drag_dot(self, event, state):
		self.dragDotGrabbed = state

	def change_height(self):
		self.configure(height=self.frameHeight)
	
	def to_bottom(self, tagOrId):
		self.canvas.tag_lower(tagOrId, "bottomTag")
		self.canvas.tag_lower("bottomTag", tagOrId)
	
	def to_top(self, tagOrId):
		self.canvas.tag_raise(tagOrId, "topTag")
		self.canvas.tag_raise("topTag", tagOrId)

	################## Canvas view functions ########################

	def zoom(self, event, zoomIn):

		[x, y] = self.canvasMousePosition

		xCenter = (x*self.timeCompress)-self.offset[0]

		if zoomIn:
			self.timeCompress = min(self.timeCompress*self.scrollSpeed, 1e10)
		else:
			self.timeCompress = max(self.timeCompress/self.scrollSpeed, 1e-2)

		self.offset[0] = -xCenter+(x*self.timeCompress)

		self.canvasChanged = True
		
	def move_canvas(self, dx, dy):

		if self.invertMove:
			dx = -dx
			dy = -dy

		self.offset[0] += dx*self.timeCompress
		self.offset[1] += dy
		
		self.canvasChanged = True
	
	def move_time(self, dx):

		self.timeMove -= dx*self.timeCompress
		
		if self.timeMove < -1:
			self.parent.timestamp += math.ceil(self.timeMove)
			self.timeMove -= math.ceil(self.timeMove)
		elif self.timeMove > 1:
			self.parent.timestamp += math.floor(self.timeMove)
			self.timeMove -= math.floor(self.timeMove)

		self.canvasChanged = True
		self.parent.locationTool.canvasChanged = True
		self.parent.toolBar.positionChanged = True

	
	####################### Ldot interaction ########################

	def unselect_ldot(self):

		self.canvas.itemconfigure(self.dragDot, state="hidden")

		self.canvas.itemconfigure(
				"selectedLdotBar",
				self.parent.selectedLdot.normalStyle
				)
		
		self.canvas.itemconfigure(
				"selectedLdotText",
				self.parent.selectedLdot.barTextStyle
				)
		
		self.canvas.dtag("all", "selectedLdot")
		self.canvas.dtag("all", "selectedLdotBar")
		self.canvas.dtag("all", "selectedLdotText")

	def select_ldot(self, ldot):
		
		self.ldotMove = [self.timeMove, 0]
		
		self.canvas.addtag_withtag("selectedLdot", ldot.tag)
		self.canvas.addtag_withtag("selectedLdotBar", ldot.tag+"Bar")
		self.canvas.addtag_withtag("selectedLdotText", ldot.tag+"Text")
		self.canvas.itemconfigure(self.dragDot, state="normal")
		
		self.canvas.itemconfigure(
				"selectedLdotBar",
				ldot.selectedStyle
				)
		
		self.canvas.itemconfigure(
				"selectedLdotText",
				css.selectedBarTextStyle
				)

		self.to_top("selectedLdotBar")
		self.to_top("selectedLdotText")
		self.to_top(self.dragDot)
	
	def create_ldot(self, ldot):

		newLdot = self.canvas.create_rectangle(
				0, 0, 0, 0,
				ldot.normalStyle,
				tags=(ldot.tag, ldot.tag+"Bar")
				)
		
		newLdot = self.canvas.create_text(
				0, 0,
				ldot.barTextStyle,
				text=ldot.ldotType+ldot.tag,
				anchor="nw",
				tags=(ldot.tag, ldot.tag+"Text")
				)

		self.canvas.tag_bind(
				ldot.tag, "<Button-1>",
				lambda x: self.parent.select_ldot(event=x, ldot=ldot)
				)

		self.to_top(ldot.tag+"Bar")
		self.to_top(ldot.tag+"Text")

	def delete_ldot(self, ldot):
		self.canvas.delete(ldot.tag)

	def drag_ldot(self, dx, dy):

		if self.parent.selectedLdot != None:

			if self.parent.record:
				self.ldotMove[0] -= dx*self.timeCompress
			self.ldotMove[1] += dy

			if self.ldotMove[0] < -1:
				self.parent.selectedLdot.beginTime += math.ceil(self.ldotMove[0])
				self.parent.selectedLdot.endTime += math.ceil(self.ldotMove[0])
				self.ldotMove[0] -= math.ceil(self.ldotMove[0])
			elif self.ldotMove[0] > 1:
				self.parent.selectedLdot.beginTime += math.floor(self.ldotMove[0])
				self.parent.selectedLdot.endTime += math.floor(self.ldotMove[0])
				self.ldotMove[0] -= math.floor(self.ldotMove[0])

			self.parent.selectedLdot.slot += self.ldotMove[1]//self.slotSize
			self.ldotMove[1] -= (self.ldotMove[1]//self.slotSize)*self.slotSize
			
			self.canvasChanged = True
			self.parent.locationTool.canvasChanged = True
			self.parent.toolBar.timeLineChanged = True
	
	def drag_ldot_time(self, dx):

		if self.parent.record and self.parent.selectedLdot != None:

			self.ldotTimeDrag += dx*self.timeCompress

			ldot = self.parent.selectedLdot

			if self.ldotTimeDrag < -1:
				ldot.retime(
						ldot.beginTime,
						ldot.endTime+math.ceil(self.ldotTimeDrag)
						)
				self.ldotTimeDrag -= math.ceil(self.ldotTimeDrag)
			elif self.ldotTimeDrag > 1:
				ldot.retime(
						ldot.beginTime,
						ldot.endTime+math.floor(self.ldotTimeDrag)
						)
				self.ldotTimeDrag -= math.floor(self.ldotTimeDrag)

			self.canvasChanged = True
			self.parent.locationTool.canvasChanged = True
			self.parent.toolBar.timeLineChanged = True

	########################## rendering ###########################

	def draw_grid_line(self, *args):
		(i, x1, y1, x2, y2, color, thickness) = args

		if i >= len(self.gridLinePool):
			self.gridLinePool.append(self.canvas.create_line(0, 0, 0, 0, tags=("line")))
			self.to_bottom(self.gridLinePool[i])

		self.canvas.itemconfigure(
				self.gridLinePool[i],
				state="normal",
				fill=color,
				width=thickness
				)
		self.canvas.coords(self.gridLinePool[i], x1, y1, x2, y2)

	def render(self):

		time = self.parent.timestamp

		self.canvas.itemconfigure("line", state="hidden")

		xdim = self.canvas.winfo_width()
		ydim = self.canvas.winfo_height()
		xend = xdim*self.timeCompress
		
		logScale = math.log(self.timeCompress)/math.log(10)

		gridSize = self.frameRate*math.exp(math.log(10)*math.floor(logScale))
		if xend/gridSize > 30:
			logScale = math.ceil(logScale)
			gridSize = self.frameRate*math.exp(math.log(10)*logScale)

		xoff = self.offset[0]-time
		yoff = self.offset[1]

		lineiter = 0
		xiter = xoff-(math.floor(xoff/gridSize))*gridSize
		
		self.canvas.itemconfigure(
				self.scaleIndicator,
				text = "scale: 10^"+str(math.floor(logScale))
				)

		self.canvas.itemconfigure(
				self.timestampIndicator,
				text = "timestamp: "+str(time)
				)


		while xiter < xend:
			
			x = xiter/self.timeCompress
			self.draw_grid_line(lineiter, x, -5, x, ydim+5, "#666", 1)
			lineiter += 1
			xiter += gridSize

		renderOrder = []

		for ldot in self.mainFrame.ldots:
			
			xbegin = max(-200, (ldot.beginTime+xoff)/self.timeCompress)
			xend = min(xdim+200, (ldot.endTime+xoff)/self.timeCompress)

			self.canvas.coords(
					ldot.tag+"Bar",
					xbegin, ldot.slot*self.slotSize+self.barSize+yoff,
					xend, ldot.slot*self.slotSize-self.barSize+yoff
					)
			
			self.canvas.coords(
					ldot.tag+"Text",
					max(min(0, xend-200), xbegin)+5,
					ldot.slot*self.slotSize+yoff-self.barSize/2
					)
			
			if ldot == self.parent.selectedLdot:
				self.canvas.coords(
						self.dragDot,
						(ldot.endTime+xoff)/self.timeCompress-self.dragDotSize,
						ldot.slot*self.slotSize+yoff-self.dragDotSize,
						(ldot.endTime+xoff)/self.timeCompress+self.dragDotSize,
						ldot.slot*self.slotSize+yoff+self.dragDotSize
						)
		
		self.to_top(self.timeIndicator)
		self.to_top(self.timestampIndicator)
		self.to_top(self.scaleIndicator)

		self.canvas.coords(
				self.timeIndicator,
				(xoff+time)/self.timeCompress,
				-5,
				(xoff+time)/self.timeCompress,
				ydim+5
			)

