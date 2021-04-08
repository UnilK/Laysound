import tkinter as tk

from location_data import *
from record_page import RecordPage
from file_page import FilePage
import canvas_styles as css



class HelpPage(tk.Frame):
	def __init__(self, parent, **kwargs):
		tk.Frame.__init__(self, parent, css.grey1Frame, **kwargs)
		self.parent = parent



class NavBar(tk.Frame):
	def __init__(self, parent, **kwargs):
		
		tk.Frame.__init__(self, parent, css.grey2Frame, **kwargs)
		self.parent = parent

		self.grid_rowconfigure(0, weight=1)
		
		self.recordPageButton = tk.Button(
				self, css.grey1Button, text="Record",
				command=lambda: self.parent.switch_page(self.parent.recordPage))

		self.filePageButton = tk.Button(
				self, css.grey1Button, text="File",
				command=lambda: self.parent.switch_page(self.parent.filePage))
		
		self.helpPageButton = tk.Button(
				self, css.grey1Button, text="Help",
				command=lambda: self.parent.switch_page(self.parent.helpPage))

		self.recordPageButton.grid(row=0, column=0, sticky="nw")
		self.filePageButton.grid(row=0, column=1, sticky="nw")
		self.helpPageButton.grid(row=0, column=2, sticky="nw")



class MainFrame(tk.Frame):
	def __init__(self, parent, **kwargs):
		tk.Frame.__init__(self, parent, css.grey1Frame, **kwargs)
		self.parent = parent

		self.ldots = []
		self.ldotCount = 0

		self.title = "DirectSound"
		self.currentName = "Untitled_project"
		self.currentProject = "saves/"+self.currentName+".json"

		self.navBar = NavBar(self, width=700, height=60)
		self.recordPage = RecordPage(self)
		self.filePage = FilePage(self)
		self.helpPage = HelpPage(self)
		self.currentPage = self.recordPage

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		
		self.navBar.grid(row=0, sticky="new")
		self.currentPage.grid(row=1, sticky="swen")
		
		self.grid(row=0, column=0, sticky="nwse")

		self.update_title()
	
	def update_title(self):
		self.parent.title(self.title+" - "+self.currentName)

	def switch_page(self, nextPage):

		if nextPage != self.currentPage:
			self.currentPage.grid_forget()
			self.currentPage = nextPage
			self.currentPage.grid(row=1, sticky="nswe")
	
	def safe_close(self):

		self.recordPage.clockSwitch = False

		if self.filePage.renderThreadActive:
			self.filePage.renderThread.join()

		self.parent.destroy()
		


if __name__ == "__main__":

	random.seed()

	root = tk.Tk()
	
	root.geometry("1200x800")

	root.grid_columnconfigure(0, weight=1)
	root.grid_rowconfigure(0, weight=1)
	
	mainFrame = MainFrame(root)

	root.protocol("WM_DELETE_WINDOW", mainFrame.safe_close)
	root.mainloop()

