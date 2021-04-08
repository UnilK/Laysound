import tkinter as tk
import random
from UI.main_frame import MainFrame

if __name__ == "__main__":

	random.seed()

	root = tk.Tk()
	
	root.geometry("1200x800")

	root.grid_columnconfigure(0, weight=1)
	root.grid_rowconfigure(0, weight=1)
	
	mainFrame = MainFrame(root)

	root.protocol("WM_DELETE_WINDOW", mainFrame.safe_close)
	root.mainloop()

