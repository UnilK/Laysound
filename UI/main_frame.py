import tkinter as tk
from tkinter import scrolledtext

from UI.location_data import *
from UI.record_page import RecordPage
from UI.file_interaction import FileInteraction
import UI.canvas_styles as css

import UI.config as config

class HelpPage(tk.Frame):
	def __init__(self, parent, **kwargs):
		tk.Frame.__init__(self, parent, css.grey1Frame, **kwargs)
		self.parent = parent
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		self.helpText = "No help"

		with open("UI/help.txt", "r") as helpFile:
			self.helpText = helpFile.read()

		self.textBox = tk.scrolledtext.ScrolledText(
				self,
				background="#494949",
				foreground="#eee",
				font=css.helvetica14
				)
		
		self.textBox.grid(row=0, column=0, sticky="nwes")

		self.textBox.insert("insert", self.helpText)

		
class NavBar(tk.Frame):
	def __init__(self, parent, **kwargs):
		
		tk.Frame.__init__(self, parent, css.grey2Frame, **kwargs)
		self.parent = parent

		self.grid_rowconfigure(0, weight=1)
		
		self.helpPageButton = tk.Button(
				self, css.grey1Button, text="help",
				command=self.parent.switch_page)
		
		self.quickSaveButton = tk.Button(
				self,
				css.grey1Button,
				text="save",
				command=self.parent.fileInteraction.quicksave_project
				)
		
		self.saveButton = tk.Button(
				self,
				css.grey1Button,
				text="save as",
				command=self.parent.fileInteraction.save_project
				)
		
		self.quickLoadButton = tk.Button(
				self,
				css.grey1Button,
				text="quickload",
				command=self.parent.fileInteraction.quickload_project
				)
		
		self.loadButton = tk.Button(
				self,
				css.grey1Button,
				text="load",
				command=self.parent.fileInteraction.load_project
				)
		
		self.renderButton = tk.Button(
				self,
				css.grey1Button,
				text="render",
				command=self.parent.fileInteraction.render_project
				)
		
		self.quickSaveButton.grid(row=0, column=0, sticky="nw", pady=1)
		self.saveButton.grid(row=0, column=1, sticky="nw", pady=1)
		self.quickLoadButton.grid(row=0, column=2, sticky="nw", pady=1)
		self.loadButton.grid(row=0, column=3, sticky="nw", pady=1)
		self.renderButton.grid(row=0, column=4, sticky="nw", pady=1)

		self.helpPageButton.grid(row=0, column=5, sticky="nw", pady=1)



class MainFrame(tk.Frame):
	def __init__(self, parent, **kwargs):
		tk.Frame.__init__(self, parent, css.grey1Frame, **kwargs)
		self.parent = parent

		self.title = "Laysound"

		self.fileInteraction = FileInteraction(self)

		self.navBar = NavBar(self, width=700, height=60)
		self.recordPage = RecordPage(self)
		self.helpPage = HelpPage(self)
		self.currentPage = self.recordPage
		
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		
		self.navBar.grid(row=0, sticky="new")
		self.currentPage.grid(row=1, sticky="swen")
		
		self.grid(row=0, column=0, sticky="nwse")

		self.update_title()
	
	def update_title(self):
		self.parent.title(self.title+" - "+config.project.name)

	def switch_page(self):

		self.currentPage.grid_forget()
		
		if self.currentPage == self.recordPage:
			self.currentPage = self.helpPage
			self.navBar.helpPageButton.configure(text="back")
		
		elif self.currentPage == self.helpPage:
			self.currentPage = self.recordPage
			self.navBar.helpPageButton.configure(text="help")
		
		self.currentPage.grid(row=1, sticky="nswe")
	
	def safe_close(self):

		self.recordPage.clockSwitch = False

		if self.fileInteraction.renderThreadActive:
			self.fileInteraction.renderThread.join()

		self.parent.destroy()
		
