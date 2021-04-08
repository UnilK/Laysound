import tkinter as tk
from tkinter import filedialog

import math
from location_data import *
import canvas_styles as css

import subprocess
import threading
import time
import json
import copy

class FilePage(tk.Frame):
	def __init__(self, parent, **kwargs):
		tk.Frame.__init__(self, parent, css.grey1Frame, **kwargs)

		self.parent = parent
		self.mainFrame = parent

		self.ldotTypes = {
				"free": FreeRoute,
				"listener": Listener,
				"source": SoundSource
				}

		self.doSave = {
				"beginTime": True,
				"endTime": True,
				"length": False,
				"normalStyle": False,
				"selectedStyle": False,
				"ldotTextStyle": False,
				"barTextStyle": False,
				"isRendered": False,
				"isHidden": True,
				"ldotType": True,
				"tag": True,
				"slot": True,
				"absoluteLocation": True,
				"relativeLocation": True,
				"bindTimeLine": True,
				"sourceInfo": True,
				"channel": True,
				"damperProfile": True
				}
		
		self.renderThread = threading.Thread(target=self.render_on_thread)
		self.renderThreadActive = False

		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)

		self.buttonFrame = tk.Frame(self, css.grey1Frame)

		self.quickSaveButton = tk.Button(
				self.buttonFrame,
				css.grey1Button,
				text="save",
				command=self.quicksave_project
				)
		
		self.saveButton = tk.Button(
				self.buttonFrame,
				css.grey1Button,
				text="save as",
				command=self.save_project
				)
		
		self.quickLoadButton = tk.Button(
				self.buttonFrame,
				css.grey1Button,
				text="quickload",
				command=self.quickload_project
				)
		
		self.loadButton = tk.Button(
				self.buttonFrame,
				css.grey1Button,
				text="load",
				command=self.load_project
				)
		
		self.renderButton = tk.Button(
				self.buttonFrame,
				css.grey1Button,
				text="render",
				command=self.render_project
				)
		
		self.buttonFrame.grid(row=0, column=0, sticky="nwes")

		self.grid_rowconfigure(10, weight=1)
		self.grid_columnconfigure(0, weight=1)
		
		self.quickSaveButton.grid(row=0, column=0, sticky="nw")
		self.saveButton.grid(row=1, column=0, sticky="nw")
		self.quickLoadButton.grid(row=2, column=0, sticky="nw")
		self.loadButton.grid(row=3, column=0, sticky="nw")
		self.renderButton.grid(row=4, column=0, sticky="nw")

	def	quicksave_project(self):
		
		with open(self.parent.currentProject, "w") as file_out:
			save_list = [copy.copy(ldot.__dict__) for ldot in self.mainFrame.ldots]

			for ldot in save_list:

				removeList = []
				for key in ldot:
					if not self.doSave[key]:
						removeList.append(key)

				for key in removeList:
					ldot.pop(key)

				ldot["bindTimeLine"] = copy.deepcopy(ldot["bindTimeLine"])
				
				for i in range(0, len(ldot["bindTimeLine"])):
					if ldot["bindTimeLine"][i][2] != None:
						ldot["bindTimeLine"][i][2] = ldot["bindTimeLine"][i][2].tag

			file_out.write(json.dumps(save_list))

	def	save_project(self):
		
		fileOut = filedialog.asksaveasfilename(title="save as", initialdir="saves")

		if fileOut:
			
			self.parent.currentProject = fileOut+".json"
			self.parent.currentName = fileOut.split("/")[-1]

			self.parent.update_title()

		self.quicksave_project()
		
	def quickload_project(self):
		
		self.parent.recordPage.unselect_ldot()
		
		try:
			with open(self.parent.currentProject, "r") as file_in:
				
				newLdots = [self.ldotTypes[ldot["ldotType"]](**ldot) for ldot in json.load(file_in)]
				
				tagToLdot = {}
				
				for ldot in newLdots:
					tagToLdot[ldot.tag] = ldot

				for ldot in newLdots:
					for bind in ldot.bindTimeLine:
						if bind[2] != None:
							bind[2] = tagToLdot[bind[2]]
			
				
				for ldot in self.parent.ldots:
					self.parent.recordPage.locationTool.delete_ldot(ldot)
					self.parent.recordPage.timeLine.delete_ldot(ldot)
				
				self.parent.ldots = newLdots

				self.parent.ldots = []

				for ldot in newLdots:
					self.parent.ldots.append(ldot)
					self.parent.recordPage.new_ldot_update()

				self.parent.ldotCount = 0

				for ldot in self.parent.ldots:
					self.parent.ldotCount = max(self.parent.ldotCount, int(ldot.tag[1:])+1)
		
		except FileNotFoundError:
			pass


	def load_project(self):
		
		fileIn = filedialog.askopenfilename(title="load project", initialdir="saves")

		if fileIn:
			
			self.parent.currentProject = fileIn
			self.parent.currentName = fileIn.split("/")[-1]

			if self.parent.currentName.endswith(".json"):
				self.parent.currentName = self.parent.currentName[:-5]

			self.parent.update_title()

		self.quickload_project()

	def render_on_thread(self):
		
		self.renderButton.configure(state="disabled")
		self.renderThreadActive = True

		process = subprocess.run(
				[
					"./lsapi", 
					"-render","instructions/"+self.parent.currentName+".dsi",
					"-o", "renders/"+self.parent.currentName+".wav"
				],
				capture_output=True
				)

		info = process.stdout.decode().splitlines()

		for bit in info:
			print(bit)
		
		self.renderThreadActive = False
		self.renderButton.configure(state="normal")

	def render_project(self):

		listeners = []
		sources = []

		for ldot in self.parent.ldots:
			if ldot.ldotType == "listener":
				listeners.append(ldot)
			elif ldot.ldotType == "source":
				sources.append(ldot)

		for listener in listeners:

			with open("instructions/"+listener.ldotType+listener.tag+".dsd", "w") as file_in:
				
				file_in.write(str(len(listener.damperProfile))+" ")
				file_in.write(str(len(listener.absoluteLocation))+" ")
				file_in.write(str(listener.beginTime*300)+"\n")

				for num in listener.damperProfile:
					file_in.write(str(math.exp(-num))+"\n")

				for nums in listener.absoluteLocation:
					file_in.write(str(nums[0])+" "+str(nums[1])+" "+str(nums[2])+"\n")

		for source in sources:

			with open("instructions/"+source.ldotType+source.tag+".dsd", "w") as file_in:

				file_in.write("0 "+str(len(source.absoluteLocation))+" ")
				file_in.write(str(source.beginTime*300)+"\n")

				for nums in source.absoluteLocation:
					file_in.write(str(nums[0])+" "+str(nums[1])+" "+str(nums[2])+"\n")
		
		with open("instructions/"+self.parent.currentName+".dsi", "w") as file_in:
			
			file_in.write(str(len(listeners))+" "+str(len(sources))+"\n")

			for listener in listeners:
				file_in.write(
						str(listener.channel)
						+" instructions/"+listener.ldotType+listener.tag+".dsd\n"
						)

			for source in sources:
				file_in.write(
						source.sourceInfo["name"]
						+" instructions/"+source.ldotType+source.tag+".dsd\n"
						)

		self.renderThread = threading.Thread(target=self.render_on_thread)
		self.renderThread.start()

				
				

