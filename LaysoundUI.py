import tkinter as tk

import random
import json

from UI.main_frame import MainFrame
import UI.config as config

if __name__ == "__main__":

	config.init()

	random.seed()

	with open("UI/default_settings.json", "w") as settingsFile:
		settingsFile.write(json.dumps(config.settings.__dict__, indent=4))
	
	with open("UI/default_settings.json", "r") as settingsFile:
		config.settings = config.Settings(**json.load(settingsFile))

	root = tk.Tk()

	root.geometry(
			str(config.settings.defaultFrameWidth)
			+"x"+str(config.settings.defaultFrameHeight))

	root.grid_columnconfigure(0, weight=1)
	root.grid_rowconfigure(0, weight=1)

	mainFrame = MainFrame(root)

	try:
		mainFrame.fileInteraction.load_project(config.settings.defaultProject)
	except:
		pass

	root.protocol("WM_DELETE_WINDOW", mainFrame.safe_close)
	root.mainloop()

