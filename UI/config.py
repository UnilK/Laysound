
class Settings():
	def __init__(
			self,
			defaultBrushSize=50, defaultBrushPower=0.01,
			defaultProject="saves/head.json", defaultFrameRate=147,
			defaultFrameHeight=800, defaultFrameWidth=1200):

		self.defaultBrushSize = defaultBrushSize
		self.defaultBrushPower = defaultBrushPower
		self.defaultFrameRate = defaultFrameRate
		self.defaultFrameHeight = defaultFrameHeight
		self.defaultFrameWidth = defaultFrameWidth
		self.defaultProject = defaultProject

class Project():
	def __init__(self, name="untitled_project", frameRate = 147, ldots=[]):

		self.name = name
		self.frameRate = frameRate
		self.ldots = ldots

def init():
	global settings, project
	settings = Settings()
	project = Project()

