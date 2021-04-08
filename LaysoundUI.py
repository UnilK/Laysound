import tkinter as tk

import random
import json

from UI.main_frame import MainFrame
import UI.settings as settings
import UI.project as project

if __name__ == "__main__":

	random.seed()

	settings.settings = settings.Settings()
	with open("UI/default_settings.json", "w") as settingsFile:
		settingsFile.write(json.dumps(settings.settings.__dict__, indent=4))
	
	with open("UI/default_settings.json", "r") as settingsFile:
		settings.settings = settings.Settings(**json.load(settingsFile))

	root = tk.Tk()

	root.geometry(
			str(settings.settings.defaultFrameWidth)
			+"x"+str(settings.settings.defaultFrameHeight))

	root.grid_columnconfigure(0, weight=1)
	root.grid_rowconfigure(0, weight=1)
	
	mainFrame = MainFrame(root)

	root.protocol("WM_DELETE_WINDOW", mainFrame.safe_close)
	root.mainloop()

