import tkinter as tk
from tkinter import filedialog

import math
from UI.location_data import *
import UI.canvas_styles as css

import subprocess
import threading
import time
import json
import copy

import UI.config as config

class FileInteraction():
	def __init__(self, parent):

		self.parent = parent

		self.ldotTypes = {
				"static": StaticRoute,
				"free": FreeRoute,
				"circle": CircleRoute,
				"straight": StraightRoute,
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
				"damperProfile": True,
				"radius": True,
				"rotation": True,
				"rotationSpeed": True,
				"direction": True,
				"speed": True
				}
		
		self.renderThread = threading.Thread(target=self.render_on_thread)
		self.renderThreadActive = False

	def	quicksave_project(self):
		
		with open(config.project.fileName, "w") as file_out:

			dummyProject = copy.copy(config.project.__dict__)
			dummyProject["ldots"] = [copy.copy(ldot.__dict__) for ldot in dummyProject["ldots"]]

			for ldot in dummyProject["ldots"]:

				removeList = []
				for key in ldot:
					if not self.doSave[key]:
						removeList.append(key)

				for key in removeList:
					ldot.pop(key)

				ldot["bindTimeLine"] = copy.copy(ldot["bindTimeLine"])
				
				for i in range(0, len(ldot["bindTimeLine"])):
					ldot["bindTimeLine"][i] = copy.copy(ldot["bindTimeLine"][i])
					if ldot["bindTimeLine"][i][2] != None:
						ldot["bindTimeLine"][i][2] = ldot["bindTimeLine"][i][2].tag

			file_out.write(json.dumps(dummyProject))

	def	save_project(self):
		
		fileOut = filedialog.asksaveasfilename(title="save as", initialdir="saves")

		if fileOut:
			
			if not fileOut.endswith(".json"):
				fileOut += ".json"
		
			config.project.fileName = fileOut		

			config.project.name = fileOut.split("/")[-1][0:-5]
			
			self.parent.update_title()

		self.quicksave_project()
		
	def quickload_project(self):
		
		self.parent.recordPage.unselect_ldot()
		
		try:
			with open(config.project.fileName, "r") as file_in:

				for ldot in config.project.ldots:
					self.parent.recordPage.locationTool.delete_ldot(ldot)
					self.parent.recordPage.timeLine.delete_ldot(ldot)
				
				config.project = config.Project(**json.load(file_in))
				
				config.project.ldots = [
						self.ldotTypes[
							ldot["ldotType"]](**ldot) for ldot in config.project.ldots
						]
				
				tagToLdot = {}
				
				for ldot in config.project.ldots:
					tagToLdot[ldot.tag] = ldot

				for ldot in config.project.ldots:
					for bind in ldot.bindTimeLine:
						if bind[2] != None:
							bind[2] = tagToLdot[bind[2]]
			
				for ldot in config.project.ldots:
					self.parent.recordPage.new_ldot_update(ldot)

		
		except FileNotFoundError:
			pass


	def load_project(self, fileIn=None):
		
		if fileIn== None:
			fileIn = filedialog.askopenfilename(title="load project", initialdir="saves")

		if fileIn:
			
			config.project.fileName = fileIn
			config.project.name = fileIn.split("/")[-1]

			if config.project.name.endswith(".json"):
				config.project.name = config.project.name[0:-5]

			self.parent.update_title()

		self.quickload_project()

	def render_on_thread(self):
		
		self.parent.navBar.renderButton.configure(state="disabled")
		self.renderThreadActive = True

		process = subprocess.run(
				[
					"./lsapi", 
					"render","instructions/"+config.project.name+".dsi",
					"-o", "renders/"+config.project.name+".wav"
				],
				capture_output=True
				)

		info = process.stdout.decode().splitlines()

		for bit in info:
			print(bit)
		
		self.renderThreadActive = False
		self.parent.navBar.renderButton.configure(state="normal")

	def render_project(self):

	
		process = subprocess.run(["ls", "./instructions"], capture_output=True)
		oldFiles = process.stdout.decode().splitlines()
	
		for oldFile in oldFiles:
			if oldFile.endswith(".dsi") or oldFile.endswith(".dsd"):
				process = subprocess.run(["rm", "instructions/"+oldFile])

		listeners = []
		sources = []

		for ldot in config.project.ldots:
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
		
		with open("instructions/"+config.project.name+".dsi", "w") as file_in:
			
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

				
				

