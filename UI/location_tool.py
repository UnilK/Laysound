import tkinter as tk
import math

import UI.canvas_styles as css

import UI.config as config

class LocationTool(tk.Frame):

	def __init__(self, parent, **kwargs):
		tk.Frame.__init__(self, parent, css.grey1Frame, **kwargs)
		
		self.parent = parent
		self.mainFrame = self.parent.parent
		
		self.canvasChanged = True
		self.canvasViewChanged = True

		self.B1State = False
		self.B3State = False
		self.invertMove = False

		self.mousePosition = [0, 0]
		self.ldotSize = 15
		self.ldotMinSize = 7
		self.ldotMaxSize = 30
		self.showLabels = "hidden"

		# 1 pixel = initialScale distance units
		self.scrollSpeed = 1.1
		self.initialScale = 0.01
		self.scrollMin = 1e-10*self.initialScale
		self.scrollMax = 1e10*self.initialScale
		self.scale = self.initialScale
		self.offset = [-2, -2]

		self.enableRotate = False
		self.rotateSpeed = 1/256
		self.ldotMove = [0, 0]
		self.ldotRotate = 0

		self.gridLinePool = []

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
		
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
		
		self.origin = self.canvas.create_oval(
				0, 0, 0, 0,
				fill = "#777",
				width = 0
				)

		self.dummyTop = self.canvas.create_line(
				0, 0, 0, 0,
				tags = ("topTag"),
				state = "hidden"
				)
		
		self.canvas.grid(column=0, row=0, sticky="nwse")
	
		self.canvas.bind("<Configure>", self.refresh_canvas)
		self.canvas.bind("<Motion>", self.track_mouse)

		self.canvas.bind("<Button-1>", lambda x: self.B1_config(event=x, state=True))
		self.canvas.bind("<Button-3>", lambda x: self.B3_config(event=x, state=True))
		self.canvas.bind("<ButtonRelease-1>", lambda x: self.B1_config(event=x, state=False))
		self.canvas.bind("<ButtonRelease-3>", lambda x: self.B3_config(event=x, state=False))

		self.canvas.bind("<Button-4>", lambda x: self.zoom(event=x, zoomIn=False))	
		self.canvas.bind("<Button-5>", lambda x: self.zoom(event=x, zoomIn=True))

		self.scaleIndicator = self.canvas.create_text(
				10, 10,
				anchor = "nw",
				text = "scale: 10^0",
				fill = "#ddd",
				font = css.helvetica14
				)
		
	##################### Utility functions & misc ##########################

	def B1_config(self, event, state):
		self.B1State = state
		self.parent.focus_set()
	
	def B3_config(self, event, state):
		self.B3State = state
		self.parent.focus_set()

	def refresh_canvas(self, event=None):
		self.canvasChanged = True
		self.canvasViewChanged = True

	def track_mouse(self, event):
		
		px, py = self.mousePosition
		cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
		self.mousePosition = [cx, cy]

		if self.B1State:
			self.move_canvas(cx-px, cy-py)
		if self.B3State:
			self.drag_ldot(cx-px, cy-py)

	def to_bottom(self, tagOrId):
		self.canvas.tag_lower(tagOrId, "bottomTag")
		self.canvas.tag_lower("bottomTag", tagOrId)
	
	def to_top(self, tagOrId):
		self.canvas.tag_raise(tagOrId, "topTag")
		self.canvas.tag_raise("topTag", tagOrId)

	######################### View control ###########################

	def zoom(self, event, zoomIn):

		[x, y] = self.mousePosition

		xCenter = self.offset[0]+(x*self.scale)
		yCenter = self.offset[1]+(y*self.scale)

		if zoomIn:
			self.scale = min(self.scale*self.scrollSpeed, self.scrollMax)
		else:
			self.scale = max(self.scale/self.scrollSpeed, self.scrollMin)

		self.offset = [
				xCenter-(x*self.scale),
				yCenter-(y*self.scale)
				]

		self.refresh_canvas()

	def move_canvas(self, dx, dy):

		if self.invertMove:
			dx = -dx
			dy = -dy

		self.offset[0] -= dx*self.scale
		self.offset[1] -= dy*self.scale

		self.refresh_canvas()

	####################### Ldot interaction ##########################

	def unselect_ldot(self):

		self.canvas.itemconfigure(
				"selectedLdotLdot",
				self.parent.selectedLdot.normalStyle,
				)
		
		self.canvas.itemconfigure(
				"selectedLdotText",
				self.parent.selectedLdot.ldotTextStyle,
				)
		
		self.canvas.dtag("all", "selectedLdot")
		self.canvas.dtag("all", "selectedLdotLdot")
		self.canvas.dtag("all", "selectedLdotText")

	def select_ldot(self, ldot):
		
		self.ldotMove = [0, 0]
		self.ldotRotate = 0
		
		self.canvas.addtag_withtag("selectedLdot", ldot.tag)
		self.canvas.addtag_withtag("selectedLdotLdot", ldot.tag+"Ldot")
		self.canvas.addtag_withtag("selectedLdotText", ldot.tag+"Text")
		
		self.canvas.itemconfigure(
				"selectedLdotLdot",
				ldot.selectedStyle
				)
		
		self.to_top("selectedLdot")


	def create_ldot(self, ldot):
		
		self.canvas.create_oval(
				0, 0, 0, 0,
				ldot.normalStyle,
				tags=(ldot.tag, ldot.tag+"Ldot")
				)

		self.canvas.create_text(
				0, 0,
				ldot.ldotTextStyle,
				text=ldot.ldotType+ldot.tag,
				anchor="nw",
				state=self.showLabels,
				tags=(ldot.tag, ldot.tag+"Text", "Text")
				)
		
		self.canvas.tag_bind(
				ldot.tag, "<Button-1>",
				lambda x: self.parent.select_ldot(event=x, ldot=ldot)
				)
		
		self.canvas.tag_bind(
				ldot.tag, "<Button-3>",
				lambda x: self.parent.bind_ldot(event=x, ldot=ldot)
				)
		
		self.to_top(ldot.tag)
		

	def delete_ldot(self, ldot):
		self.canvas.delete(ldot.tag)

	
	def drag_ldot(self, dx, dy):

		if self.parent.selectedLdot != None and self.parent.record:

			if self.enableRotate:
				self.ldotRotate += dx*self.rotateSpeed
			else:
				self.ldotMove[0] += dx*self.scale
				self.ldotMove[1] += dy*self.scale

			self.canvasChanged = True
	
	def switch_labels(self):
		if self.showLabels == "normal":
			self.showLabels = "hidden"
			self.canvas.itemconfigure("Text", state="hidden")
		else:
			self.showLabels = "normal"
			self.canvas.itemconfigure("Text", state="normal")
		
		self.canvasChanged = True


	####################### Rendering functions #######################

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

	def render_sized_grid(self, *args):
		
		(xdim, ydim, xend, yend, xoff, yoff, gridSize, lineiter, color, thickness) = args
		xiter = gridSize*(math.ceil(xoff/gridSize))-xoff
		yiter = gridSize*(math.ceil(yoff/gridSize))-yoff
		
		while xiter < xend:
			
			x = xiter/self.scale
			self.draw_grid_line(lineiter, x, -5, x, ydim+5, color, thickness)
			lineiter += 1
			xiter += gridSize

		while yiter < yend:
			
			y = yiter/self.scale
			self.draw_grid_line(lineiter, -5, y, xdim+5, y, color, thickness)
			lineiter += 1
			yiter += gridSize

		return lineiter

	
	def render_grid(self, *args):

		(xoff, yoff, scale) = args

		self.canvas.itemconfigure("line", state="hidden")

		xdim = self.canvas.winfo_width()
		ydim = self.canvas.winfo_height()

		xend = xdim*self.scale
		yend = ydim*self.scale

		logScale = math.log(scale/self.initialScale)/math.log(10)

		smallGridSize = math.exp(math.log(10)*math.floor(logScale))
		bigGridSize = math.exp(math.log(10)*math.ceil(logScale))
	
		self.canvas.itemconfigure(
				self.scaleIndicator,
				text = "scale: 10^"+str(math.ceil(logScale))
				)

		lineiter = 0

		if (xend+yend)/smallGridSize <= 40:
			lineiter = self.render_sized_grid(
					xdim, ydim, xend, yend, xoff, yoff,
					smallGridSize, lineiter, "#666", 1
					)

		self.render_sized_grid(
				xdim, ydim, xend, yend, xoff, yoff,
				bigGridSize, lineiter, "#777", 2
				)


		self.canvas.tag_raise(self.origin, "line")

		self.canvas.coords(
				self.origin,
				-xoff/scale-5, -yoff/scale-5, -xoff/scale+5, -yoff/scale+5
				)

	def render(self):

		time = self.parent.timestamp
		renderOrder = []

		scale = self.scale
		[xoff, yoff] = self.offset

		if self.canvasViewChanged:
			self.render_grid(xoff, yoff, scale)

		if self.parent.selectedLdot != None and self.parent.record:

			if (
					self.parent.selectedLdot.beginTime <= time
					and self.parent.selectedLdot.endTime > time
					):
				
				x0, y0, r0 = self.parent.selectedLdot.get_relative(time-1)
				x1, y1, r1 = self.parent.selectedLdot.get_relative(time)

				if self.parent.timeFlow:
					self.parent.selectedLdot.set_relative_location(
							time, x0+self.ldotMove[0], y0-self.ldotMove[1])
					
					self.parent.selectedLdot.set_relative_rotation(
							time, r0+self.ldotRotate)

				else:
					self.parent.selectedLdot.set_relative_location(
							time, x1+self.ldotMove[0], y1-self.ldotMove[1])

					self.parent.selectedLdot.set_relative_rotation(
							time, r1+self.ldotRotate)
				
				self.parent.toolBar.positionChanged = True

				self.ldotMove[0] = 0;
				self.ldotMove[1] = 0;
				self.ldotRotate = 0

		visited = {}

		for ldot in config.project.ldots:
			if ldot.beginTime <= time and ldot.endTime > time and not ldot.isHidden:
				self.canvas.itemconfigure(ldot.tag+"Ldot", state="normal")
				renderOrder.append((ldot.priority(time, visited), ldot))
			else:
				self.canvas.itemconfigure(ldot.tag, state="hidden")

		renderOrder.sort(key=lambda tup: tup[0])
		
		ldotScale = max(
				self.ldotMinSize,
				min(self.ldotMaxSize, self.ldotSize*(1-0.1*math.log(scale/self.initialScale)))
				)

		for tup in renderOrder:

			tup[1].render_point(time)
			x, y, r = tup[1].get_absolute(time)

			x = (x-xoff)/scale
			y = (-y-yoff)/scale

			self.canvas.coords(
					tup[1].tag+"Ldot",
					x-ldotScale, y-ldotScale,
					x+ldotScale, y+ldotScale
					)
			
			if self.showLabels == "normal":
				self.canvas.coords(
						tup[1].tag+"Text",
						x+1.1*ldotScale, y-1.1*ldotScale
						)
		
		if self.showLabels == "normal" and len(config.project.ldots) > 0:
			self.to_top("Text")
		
		self.to_top(self.scaleIndicator)
