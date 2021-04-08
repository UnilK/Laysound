
class Settings():
	def __init__(
			self,
			defaultBrushSize=50, defaultBrushPower=0.01,
			defaultProject=None, defaultFrameRate=147,
			defaultFrameHeight=800, defaultFrameWidth=1200):

		self.defaultBrushSize = defaultBrushSize
		self.defaultBrushPower = defaultBrushPower
		self.defaultProject = defaultProject
		self.defaultFrameRate = defaultFrameRate
		self.defaultFrameHeight = defaultFrameHeight
		self.defaultFrameWidth = defaultFrameWidth

class Project():
	def __init__(self, name="unnamed_project", frameRate = 147, ldots=[]):

		self.name = name
		self.frameRate = frameRate
		self.ldots = ldots

def init():
	global settings, project
	settings = Settings()
	project = Project()

