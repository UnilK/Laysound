import math
import random

# - Mom can we have css?
# - We have css at home
# css at home:

import UI.canvas_styles as css

import UI.config as config

class LocationData():

	def __init__(
			self, beginTime, endTime, tag, xpos=0, ypos=0, slot=0, bind=None, isHidden=False,
			ldotType=None, absoluteLocation=None, relativeLocation=None, bindTimeLine=None):

		self.beginTime = beginTime
		self.endTime = endTime
		self.length = endTime-beginTime

		self.normalStyle = css.default
		self.selectedStyle = css.selectedStyle
		self.ldotTextStyle = css.defaultLdotTextStyle
		self.barTextStyle = css.defaultBarTextStyle

		self.isRendered = False
		self.isHidden = isHidden
		self.ldotType = ldotType
		self.tag = tag
		self.slot = slot

		if absoluteLocation == None:
			self.absoluteLocation = [[0, 0, 0]]
		else:
			self.absoluteLocation = absoluteLocation

		if relativeLocation == None:
			self.relativeLocation = [[xpos, ypos, 0]]
		else:
			self.relativeLocation = relativeLocation

		if bindTimeLine == None:
			self.bindTimeLine = [[beginTime, endTime, bind]]	
		else:
			self.bindTimeLine = bindTimeLine

	def binary_search(self, timestamp):
		
		"""
		self.bindTimeLine is sorted by the first entry in the tuple,
		begin_timestamp. binary_search(timestamp) returns the largest
		i for which bindTimeLine[i][0] <= timestamp applies, or
		len(bindTimeLine)-1 if no such i exists.
		"""

		left, mid, right = 0, 0, len(self.bindTimeLine)-1
		
		while left < right:
			
			mid = (left+right)//2
			
			if self.bindTimeLine[mid+1][0] <= timestamp:
				left = mid+1
			else:
				right = mid
		
		return left

	def priority(self, timestamp, visited):
		
		if self.tag in visited:
			return visited[self.tag]
		
		parent = self.bindTimeLine[self.binary_search(timestamp)][2]
		
		if parent == None:
			visited[self.tag] = 0
		else:
			visited[self.tag] = -1
			visited[self.tag] = parent.priority(timestamp, visited)+1
		
		return visited[self.tag]

	def add_bind(self, begin, end, target):
			
		addPoint = self.binary_search(begin)

		while addPoint+1 < len(self.bindTimeLine) and self.bindTimeLine[addPoint+1][1] <= end:
			self.bindTimeLine.pop(addPoint+1)

		if self.bindTimeLine[addPoint][1] > end:
			self.bindTimeLine.insert(addPoint, self.bindTimeLine[addPoint].copy())

		if self.bindTimeLine[addPoint][0] < begin:
			self.bindTimeLine.insert(addPoint, self.bindTimeLine[addPoint].copy())
			addPoint += 1

		if addPoint > 0:
			self.bindTimeLine[addPoint-1][1] = min(
					self.bindTimeLine[addPoint-1][1],
					begin
					)

		if addPoint+1 < len(self.bindTimeLine):
			self.bindTimeLine[addPoint+1][0] = max(
					self.bindTimeLine[addPoint+1][0],
					end
					)

		self.bindTimeLine[addPoint] = [begin, end, target]
	
	def delete_bind(self, timestamp):

		self.bindTimeLine.pop(self.binary_search(timestamp))
		if len(self.bindTimeLine) == 0:
			self.bindTimeLine.append([0, 0, None])
	
	def seek_and_destroy(self, ldotTag):

		index = len(self.bindTimeLine)-1

		while index >= 0:
			if (
					self.bindTimeLine[index][2] != None
					and self.bindTimeLine[index][2].tag == ldotTag
					):

				self.bindTimeLine.pop(index)
			index -= 1

		if len(self.bindTimeLine) == 0:
			self.bindTimeLine.append([0, 0, None])
		

	def retime(self, beginTime, endTime):
		
		self.length = max(1, endTime-beginTime)
		self.beginTime = beginTime
		self.endTime = max(self.beginTime+1, endTime)

		self.initialize_route()

	def get_absolute(self, timestamp):
		return self.absoluteLocation[
				max(0, min(timestamp-self.beginTime, len(self.absoluteLocation)-1))
				]
	
	def get_relative(self, timestamp):
		return self.relativeLocation[
				max(0, min(timestamp-self.beginTime, len(self.relativeLocation)-1))
				]

	def render_point(self, timestamp):
		
		relativeTime = max(0, min(timestamp-self.beginTime, len(self.absoluteLocation)-1))
		rx, ry, rr = self.get_relative(relativeTime)

		parentPos = self.binary_search(timestamp)
		
		if self.bindTimeLine[parentPos][2] != None:

			x, y, r = self.bindTimeLine[parentPos][2].get_absolute(
					min(self.bindTimeLine[parentPos][1]-1,
						max(timestamp, self.bindTimeLine[parentPos][0])
						)
					)

			self.absoluteLocation[relativeTime][0] = x+rx*math.cos(r*math.pi)-ry*math.sin(r*math.pi)
			self.absoluteLocation[relativeTime][1] = y+ry*math.cos(r*math.pi)+rx*math.sin(r*math.pi)
			self.absoluteLocation[relativeTime][2] = r+rr
		
		else:
			
			self.absoluteLocation[relativeTime][0] = rx
			self.absoluteLocation[relativeTime][1] = ry
			self.absoluteLocation[relativeTime][2] = rr

	def initialize_route(self):
		pass

	def set_relative_rotation(self, timestamp, r):
		relativeTime = max(0, min(timestamp-self.beginTime, len(self.relativeLocation)-1))
		self.relativeLocation[relativeTime][2] = r

	def set_absolute_rotation(self, timestamp, r):
		cx, cy, cr = self.get_absolute(timestamp)
		rx, ry, rr = self.get_relative(timestamp)
		nr = rr+r-cr
		self.set_relative_rotation(timestamp, nr)

	def set_relative_location(self, timestamp, x, y):
		pass

	def set_absolute_location(self, timestamp, x, y):
		cx, cy, cr = self.get_absolute(timestamp)
		rx, ry, rr = self.get_relative(timestamp)
		nx, ny = rx+x-cx, ry+y-cy
		self.set_relative_location(timestamp, nx, ny)


class StaticRoute(LocationData):
	def __init__(self, **kwargs):
		LocationData.__init__(self, **kwargs)

		self.ldotType = "static"
		
		self.normalStyle = css.staticRouteNormal
		self.selectedStyle = css.selectedStyle
		self.barTextStyle = css.staticRouteBarTextStyle

		self.initialize_route()

	def initialize_route(self, begin=None, end=None):
		if begin == None:
			if self.length < len(self.absoluteLocation):
				self.absoluteLocation = self.absoluteLocation[:self.length]
			while(len(self.absoluteLocation) < self.length):
				self.absoluteLocation.append(self.absoluteLocation[-1].copy())

	def set_relative_location(self, timestamp, x, y):
		self.relativeLocation[0][0] = x
		self.relativeLocation[0][1] = y

class FreeRoute(LocationData):
	def __init__(self, **kwargs):
		LocationData.__init__(self, **kwargs)
		
		self.ldotType = "free"

		self.normalStyle = css.freeRouteNormal
		self.selectedStyle = css.selectedStyle
		self.barTextStyle = css.freeRouteBarTextStyle
		
		self.initialize_route()

	def initialize_route(self, begin=None, end=None):
		
		if begin == None:
			
			if self.length < len(self.absoluteLocation):
				self.relativeLocation = self.relativeLocation[:self.length]
				self.absoluteLocation = self.absoluteLocation[:self.length]

			while(len(self.absoluteLocation) < self.length):
				self.relativeLocation.append(self.relativeLocation[-1].copy())
				self.absoluteLocation.append(self.absoluteLocation[-1].copy())

	def set_relative_location(self, timestamp, x, y):
		relativeTime = max(0, min(timestamp-self.beginTime, len(self.relativeLocation)-1))
		self.relativeLocation[relativeTime][0] = x
		self.relativeLocation[relativeTime][1] = y



class CircleRoute(LocationData):
	def __init__(self, radius=1, rotation=0, rotationSpeed=1, **kwargs):
		LocationData.__init__(self, **kwargs)

		self.ldotType = "circle"
		
		self.normalStyle = css.circleRouteNormal
		self.selectedStyle = css.selectedStyle
		self.barTextStyle = css.circleRouteBarTextStyle

		self.radius = radius
		self.rotation = rotation
		self.rotationSpeed = rotationSpeed

		self.initialize_route()

	def set_relative_rotation(self, timestamp, r):
		pass

	def initialize_route(self, begin=None, end=None):
		
		if begin == None:
			
			if self.length < len(self.absoluteLocation):
				self.absoluteLocation = self.absoluteLocation[:self.length]

			while(len(self.absoluteLocation) < self.length):
				self.absoluteLocation.append(self.absoluteLocation[-1].copy())

	def get_relative(self, timestamp):
		relativeTime = max(0, min(timestamp-self.beginTime, len(self.absoluteLocation)-1))
		return 	[
				self.radius*math.cos(
					math.pi*(self.rotation
							+(self.rotationSpeed*relativeTime)/config.project.frameRate)),
				self.radius*math.sin(
					math.pi*(self.rotation
							+(self.rotationSpeed*relativeTime)/config.project.frameRate)),
				0
				]

	def set_relative_location(self, timestamp, x, y):
		relativeTime = max(0, min(timestamp-self.beginTime, len(self.absoluteLocation)-1))
			
		self.radius = math.sqrt(x*x+y*y)
		
		if(x == 0):
			x = 1e-9
	
		self.rotation = (math.atan(y/x)/math.pi
				-self.rotationSpeed*relativeTime/config.project.frameRate)
		
		if(x < 0):
			self.rotation += 1




class StraightRoute(LocationData):
	def __init__(self, direction=0, speed=1, **kwargs):
		LocationData.__init__(self, **kwargs)
		
		self.ldotType = "straight"
		
		self.normalStyle = css.straightRouteNormal
		self.selectedStyle = css.selectedStyle
		self.barTextStyle = css.straightRouteBarTextStyle
		
		self.direction = direction
		self.speed = speed

		self.initialize_route()

	def set_relative_rotation(self, timestamp, r):
		pass

	def initialize_route(self, begin=None, end=None):
		
		if begin == None:
			
			if self.length < len(self.absoluteLocation):
				self.absoluteLocation = self.absoluteLocation[:self.length]

			while(len(self.absoluteLocation) < self.length):
				self.absoluteLocation.append(self.absoluteLocation[-1].copy())

	def get_relative(self, timestamp):
		relativeTime = max(0, min(timestamp-self.beginTime, len(self.absoluteLocation)-1))
		return 	[
				math.cos(math.pi*self.direction)*self.speed*relativeTime/config.project.frameRate,
				math.sin(math.pi*self.direction)*self.speed*relativeTime/config.project.frameRate,
				0
				]

	def set_relative_location(self, timestamp, x, y):
		relativeTime = max(0, min(timestamp-self.beginTime, len(self.absoluteLocation)-1))
		
		if(relativeTime == 0):
			return

		if(x == 0):
			x = 1e-9
	
		self.speed = (math.sqrt(x*x+y*y)*config.project.frameRate)/relativeTime
		self.direction = (math.atan(y/x)/math.pi)
		
		if(x < 0):
			self.direction += 1


class SoundSource(LocationData):
	def __init__(self, sourceInfo, **kwargs):
		LocationData.__init__(self, **kwargs)
		
		self.ldotType = "source"

		self.normalStyle = css.soundSourceNormal
		self.selectedStyle = css.selectedStyle
		self.barTextStyle = css.soundSourceBarTextStyle
		self.sourceInfo = sourceInfo

		self.initialize_route()

	def initialize_route(self, begin=None, end=None):
		# static point
		if begin == None:
			if self.length < len(self.absoluteLocation):
				self.absoluteLocation = self.absoluteLocation[:self.length]
			while(len(self.absoluteLocation) < self.length):
				self.absoluteLocation.append(self.absoluteLocation[-1].copy())

	def set_relative_location(self, timestamp, x, y):
		# static point
		self.relativeLocation[0][0] = x
		self.relativeLocation[0][1] = y
	
	def retime(self, beginTime, endTime):
		
		if beginTime != self.beginTime:
			self.beginTime = beginTime
			self.endTime = self.beginTime+self.length
		elif endTime != self.endTime:
			self.endTime = endTime
			self.beginTime = self.endTime-self.length

		self.initialize_route()


class Listener(LocationData):
	def __init__(self, channel=0, damperProfile=None, **kwargs):
		LocationData.__init__(self, **kwargs)

		self.ldotType = "listener"
		
		self.channel = channel

		if damperProfile == None:
			self.damperProfile = [0]*256
		else:
			self.damperProfile = damperProfile

		self.normalStyle = css.listenerNormal
		self.selectedStyle = css.selectedStyle
		self.barTextStyle = css.listenerBarTextStyle

		self.initialize_route()

	def initialize_route(self, begin=None, end=None):
		# static point
		if begin == None:
			if self.length < len(self.absoluteLocation):
				self.absoluteLocation = self.absoluteLocation[:self.length]
			while(len(self.absoluteLocation) < self.length):
				self.absoluteLocation.append(self.absoluteLocation[-1].copy())

	def set_relative_location(self, timestamp, x, y):
		# static point
		self.relativeLocation[0][0] = x
		self.relativeLocation[0][1] = y
	
	def retime(self, beginTime, endTime):

		for ldot in config.project.ldots:
			if ldot.ldotType == "listener":
				ldot.local_retime(beginTime, endTime)
	
	def local_retime(self, beginTime, endTime):
		
		self.length = max(1, endTime-beginTime)
		self.beginTime = 0
		self.endTime = self.length

		self.initialize_route()
