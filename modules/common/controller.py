"""
Contains the main controller object for ByWaf.

"""

# Import Modules
import glob
import imp
import sys
import os
import readline
import re
import socket
import commands
import time
import subprocess
import hashlib
from subprocess import Popen, PIPE


# try to find and import the settings.py config file
if os.path.exists("/etc/bywaf/settings.py"):
	try:
		sys.path.append("/etc/bywaf/")
		import settings

		# check for a few updated values to see if we have a new or old settings.py file
		try:
			settings.BYWAF_PATH
		except AttributeError:
			#os.system('clear')
			print '\n========================================================================='
			print ' New major ByWaf version installed'
			print '========================================================================='
			print '\n [*] Manually run: bash %s -s' % os.path.abspath("setup/setup.sh")
			sys.exit()

	except ImportError:
		print "\n [!] ERROR #1: run %s manually\n" % (os.path.abspath("./config/update.py"))
		sys.exit()
elif os.path.exists("./config/settings.py"):
	try:
		sys.path.append("./config")
		import settings
	except ImportError:
		print "\n [!] ERROR #2: run %s manually\n" % (os.path.abspath("./config/update.py"))
		sys.exit()
else:
	# if the file isn't found, try to run the update script
	#os.system('clear')
	print '\n========================================================================='
	print ' ByWaf First Run Detected...'
	print '========================================================================='
	print '\n [*] Manually run: bash %s -s' % os.path.abspath("setup/setup.sh")
	sys.exit()


from os.path import join, basename, splitext
from modules.common import messages
from modules.common import helpers
from modules.common import completers


class Controller:
	"""
	Principal controller object that's instantiated.

	Loads all payload modules dynamically from ./modules/payloads/* and
	builds store the instantiated payload objects in self.payloads.
	has options to list languages/payloads, manually set payloads,
	generate code, and provides the main interactive
	menu that lists payloads and allows for user ineraction.
	"""

	def __init__(self, langs = None, oneRun=True):
		self.payloads = list()
		# a specific payload, so we can set it manually
		self.payload = None
		self.payloadname = None
		# restrict loaded modules to specific languages
		self.langs = langs

		# oneRune signifies whether to only generate one payload, as we would
		# if being invoked from external code.
		# defaults to True, so bywaf.py needs to manually specific "False" to
		# ensure an infinite loop
		self.oneRun = oneRun

		self.outputFileName = ""

		self.commands = [   ("use","Use a specific payload"),
		                    ("info","Information on a specific payload"),
		                    ("list","List available payloads"),
		                    ("update","Update ByWaf to the latest version"),
		                    ("exit","Exit ByWaf")]

		self.payloadCommands = [    ("set","Set a specific option value"),
		                            ("info","Show information about the payload"),
		                            ("options","Show payload's options"),
		                            ("run","Run payload"),
		                            ("back","Go to the main menu"),
		                            ("exit","exit ByWaf")]

		self.LoadPayloads()


	def LoadPayloads(self):
		"""
		Crawl the module path and load up everything found into self.payloads.
		"""

		# crawl up to 5 levels down the module path
		for x in xrange(1,5):
			# make the folder structure the key for the module

			d = dict( (path[path.find("payloads")+9:-3], imp.load_source( "/".join(path.split("/")[3:])[:-3],path )  ) for path in glob.glob(join(settings.BYWAF_PATH+"/modules/payloads/" + "*/" * x,'[!_]*.py')) )

			# instantiate the payload stager
			for name in d.keys():
				module = d[name].Payload()
				self.payloads.append( (name, module) )

		# sort payloads by their key/path name
		self.payloads = sorted(self.payloads, key=lambda x: (x[0]))


	def ListPayloads(self):
		"""
		Prints out available payloads in a nicely formatted way.
		"""

		print helpers.color("\n [*] Available Payloads:\n")
		lastBase = None
		x = 1
		for (name, payload) in self.payloads:
			parts = name.split("/")
			if lastBase and parts[0] != lastBase:
				print ""
			lastBase = parts[0]
			print "\t%s)\t%s" % (x, '{0: <24}'.format(name))
			x += 1
		print ""


	def UpdateVeil(self, interactive=True):
		"""
		Updates ByWaf by invoking git pull on the OS

		"""
		print "\n Updating ByWaf via git...\n"
		updatecommand = ['git', 'pull']
		updater = subprocess.Popen(updatecommand, cwd=settings.BYWAF_PATH, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		updoutput, upderr = updater.communicate()

		if interactive:
			raw_input(" [>] ByWaf updated, press any key to continue.")


	def PayloadOptions(self, payload):
		print helpers.color("\n Required Options:\n")

		print " Name\t\t\tCurrent Value\tDescription"
		print " ----\t\t\t-------------\t-----------"

		# sort the dictionary by key before we output, so it looks nice
		for key in sorted(self.payload.required_options.iterkeys()):
			print " %s\t%s\t%s" % ('{0: <16}'.format(key), '{0: <8}'.format(payload.required_options[key][0]), payload.required_options[key][1])

		print ""

	def PayloadInfo(self, payload, showTitle=True, showInfo=True):
		"""
		Print out information about a specified payload.

		payload = the payload object to print information on
		showTitle = whether to show the Veil title
		showInfo = whether to show the payload information bit

		"""
		if showTitle:
			if settings.TERMINAL_CLEAR != "false": messages.title()

		if showInfo:
			# extract the payload class name from the instantiated object, then chop off the load folder prefix
			payloadname = "/".join(str(str(payload.__class__)[str(payload.__class__).find("payloads"):]).split(".")[0].split("/")[1:])

			print helpers.color(" Payload information:\n")
			print "\tName:\t\t" + payloadname
			print "\tLanguage:\t" + payload.language
			print "\tRating:\t\t" + payload.rating

			if hasattr(payload, 'shellcode'):
				if self.payload.shellcode.customshellcode:
					print "\tShellcode:\t\tused"

			# format this all nice-like
			print helpers.formatLong("Description:", payload.description)

		# if required options were specified, output them
		if hasattr(self.payload, 'required_options'):
			self.PayloadOptions(self.payload)

	def SetPayload(self, payloadname, options):
		"""
		Manually set the payload for this object with specified options.

		"""

		# iterate through the set of loaded payloads, trying to find the specified payload name
		for (name, payload) in self.payloads:

			if payloadname.lower() == name.lower():

				# set the internal payload variable
				self.payload = payload
				self.payloadname = name

			# did they enter a number rather than the full payload?
			elif payloadname.isdigit() and 0 < int(payloadname) <= len(self.payloads):
				x = 1
				for (name, pay) in self.payloads:
					# if the entered number matches the payload #, use that payload
					if int(payloadname) == x:
						self.payload = pay
						self.payloadname = name
					x += 1

		print " Payload: %s\n" % helpers.color(self.payloadname)

		# if payload is found, then go ahead
		if self.payload:

			# options['customShellcode'] = "\x00..."
			if 'customShellcode' in options:
				self.payload.shellcode.setCustomShellcode(options['customShellcode'])
			# options['required_options'] = {"compile_to_exe" : ["Y", "Compile to an executable"], ...}
			if 'required_options' in options:
				try:
					for k,v in options['required_options'].items():
						self.payload.required_options[k] = v
				except:
					print helpers.color("\n [!] Internal error #4.", warning=True)
			# options['msfvenom'] = ["windows/meterpreter/reverse_tcp", ["LHOST=192.168.1.1","LPORT=443"]
			if 'msfvenom' in options:
				if hasattr(self.payload, 'shellcode'):
					self.payload.shellcode.SetPayload(options['msfvenom'])
				else:
					print helpers.color("\n [!] Internal error #3: This module does not use msfvenom!", warning=True)
					sys.exit()

			if not self.ValidatePayload(self.payload):

				print helpers.color("\n [!] WARNING: Not all required options filled\n", warning=True)
				self.PayloadOptions(self.payload)
				print ''
				sys.exit()

		# if a payload isn't found, then list available payloads and exit
		else:

			print helpers.color(" [!] Invalid payload selected\n\n", warning=True)
			self.ListPayloads()
			sys.exit()


	def ValidatePayload(self, payload):
		"""
		Check if all required options are filled in.

		Returns True if valid, False otherwise.
		"""

		# don't worry about shellcode - it validates itself


		# validate required options if present
		if hasattr(payload, 'required_options'):
			for key in sorted(self.payload.required_options.iterkeys()):
				if payload.required_options[key][0] == "":
					return False

		return True


	def GeneratePayload(self):
		"""
		Calls self.payload.generate() to generate payload code.

		Returns string of generated payload code.
		"""
		return self.payload.generate()

	def PayloadMenu(self, payload, showTitle=True, args=None):
		"""
		Main menu for interacting with a specific payload.

		payload = the payload object we're interacting with
		showTitle = whether to show the main Veil title menu

		Returns the output of OutputMenu() (the full path of the source file or compiled .exe)
		"""

		comp = completers.PayloadCompleter(self.payloadCommands, self.payload)
		readline.set_completer_delims(' \t\n;')
		readline.parse_and_bind("tab: complete")
		readline.set_completer(comp.complete)

		# show the title if specified
		if showTitle:
			if settings.TERMINAL_CLEAR != "false": messages.title()

		# extract the payload class name from the instantiated object
		# YES, I know this is a giant hack :(
		# basically need to find "payloads" in the path name, then build
		# everything as appropriate
		payloadname = "/".join(str(str(payload.__class__)[str(payload.__class__).find("payloads"):]).split(".")[0].split("/")[1:])
		print "\n Payload: " + helpers.color(payloadname) + " loaded\n"

		self.PayloadInfo(payload, showTitle=False, showInfo=False)
		messages.helpmsg(self.payloadCommands, showTitle=False)

		choice = ""
		while choice == "":

			while True:

				choice = raw_input(" [%s>>]: " % payloadname).strip()

				if choice != "":

					parts = choice.strip().split()
					cmd = parts[0].lower()

					# display help menu for the payload
					if cmd == "info":
						self.PayloadInfo(payload)
						choice = ""
					if cmd == "help":
						messages.helpmsg(self.payloadCommands)
						choice = ""
					# head back to the main menu
					if cmd == "main" or cmd == "back" or cmd == "home":
						#finished = True
						return ""
						#self.MainMenu()
					if cmd == "exit" or cmd == "end" or cmd == "quit":
						raise KeyboardInterrupt
					# Update ByWaf via git
					if cmd == "update":
						self.UpdateVeil()
					# set specific options
					if cmd == "set":

						# catch the case of no value being supplied
						if len(parts) == 1:
							print helpers.color(" [!] ERROR: no value supplied\n", warning=True)

						else:

							option = parts[1].upper()
							value = "".join(parts[2:])

							#### VALIDATION ####

							# validate RHOST
							if option == "RHOST":
								if '.' in value:
									hostParts = value.split(".")

									if len(hostParts) > 1:

										# if the last chunk is a number, assume it's an IP address
										if hostParts[-1].isdigit():
											# do a regex IP validation
											if not re.match(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",value):
												print helpers.color("\n [!] ERROR: Bad IP address specified.\n", warning=True)
											else:
												try:
													payload.required_options[option][0] = value
													print " [i] %s => %s" % (option, value)
												except KeyError:
													print helpers.color("\n [!] ERROR #1: Specify LHOST value in the following screen.\n", warning=True)
												except AttributeError:
													print helpers.color("\n [!] ERROR #2: Specify LHOST value in the following screen.\n", warning=True)

										# assume we've been passed a domain name
										else:
											if helpers.isValidHostname(value):
												payload.required_options[option][0] = value
												print " [i] %s => %s" % (option, value)
											else:
												print helpers.color("\n [!] ERROR: Bad hostname specified.\n", warning=True)

									else:
										print helpers.color("\n [!] ERROR: Bad IP address or hostname specified.\n", warning=True)

								elif ':' in value:
									try:
										socket.inet_pton(socket.AF_INET6, value)
										payload.required_options[option][0] = value
										print " [i] %s => %s" % (option, value)
									except socket.error:
										print helpers.color("\n [!] ERROR: Bad IP address or hostname specified.\n", warning=True)
										value = ""

								else:
									print helpers.color("\n [!] ERROR: Bad IP address or hostname specified.\n", warning=True)
									value = ""

							# validate RPORT
							if option  == "RPORT":
								try:
									if int(value) <= 0 or int(value) >= 65535:
										print helpers.color("\n [!] ERROR: Bad port number specified.\n", warning=True)
									else:
										try:
											payload.required_options[option][0] = value
											print " [i] %s => %s" % (option, value)
										except KeyError:
											print helpers.color("\n [!] ERROR: Specify LPORT value in the following screen.\n", warning=True)
										except AttributeError:
											print helpers.color("\n [!] ERROR: Specify LPORT value in the following screen.\n", warning=True)
								except ValueError:
									print helpers.color("\n [!] ERROR: Bad port number specified.\n", warning=True)

							# set the specific option value if not validation done
							else:
								try:
									payload.required_options[option][0] = value
									print " [*] %s => %s" % (option, value)
								except:
									print helpers.color(" [!] ERROR: Invalid value specified.\n", warning=True)
									cmd = ""
									
							# validate URL
							'''
							Using URLparse to validate url and detect parameters and paths
							'''
							if option  == "URL":
								try:
									if value == "":
										print helpers.color("\n [!] ERROR: Bad url specified.\n", warning=True)
									else:
										try:
											payload.required_options[option][0] = value
											print " [i] %s => %s" % (option, value)
										except KeyError:
											print helpers.color("\n [!] ERROR: Specify URL value in the following screen.\n", warning=True)
										except AttributeError:
											print helpers.color("\n [!] ERROR: Specify URL value in the following screen.\n", warning=True)
								except ValueError:
									print helpers.color("\n [!] ERROR: Bad url specified.\n", warning=True)
							
							# set the specific option value if not validation done
							else:
								try:
									payload.required_options[option][0] = value
									print " [*] %s => %s" % (option, value)
								except:
									print helpers.color(" [!] ERROR: Invalid value specified.\n", warning=True)
									cmd = ""							

					# generate the payload
					if cmd == "generate" or cmd == "gen" or cmd == "run" or cmd == "go" or cmd == "do" or cmd == "make":

						# make sure all required options are filled in first
						if self.ValidatePayload(payload):

							#finished = True
							# actually execute the payload
							try:
								payload.generate()
								print helpers.color("\n [*] Execution completed! ;)\n", status=True)

							except:
								print helpers.color("\n [*] Something went wrong\n", warning=True)

						else:
							print helpers.color("\n [!] WARNING: not all required options filled\n", warning=True)

					if cmd == "options":
						# if required options were specified, output them
						if hasattr(self.payload, 'required_options'):
							self.PayloadOptions(self.payload)


	def MainMenu(self, showMessage=True, args=None):
		"""
		Main interactive menu for payload generation.

		showMessage = reset the screen and show the greeting message [default=True]
		oneRun = only run generation once, returning the path to the compiled executable
		    used when invoking the framework from an external source
		"""

		self.outputFileName = ""
		cmd = ""

		try:
			while cmd == "" and self.outputFileName == "":

				# set out tab completion for the appropriate modules on each run
				# as other modules sometimes reset this
				comp = completers.MainMenuCompleter(self.commands, self.payloads)
				readline.set_completer_delims(' \t\n;')
				readline.parse_and_bind("tab: complete")
				readline.set_completer(comp.complete)

				if showMessage:
					# print the title, where we are, and number of payloads loaded
					if settings.TERMINAL_CLEAR != "false": messages.title()
					print " Main Menu\n"
					print "\t" + helpers.color(str(len(self.payloads))) + " payloads loaded\n"
					messages.helpmsg(self.commands, showTitle=False)
					showTitle=False

				cmd = raw_input(' [ByWaf>>]: ').strip()

				# handle our tab completed commands
				if cmd.startswith("help"):
					if settings.TERMINAL_CLEAR != "false": messages.title()
					print " Main Menu\n"
					print "\t" + helpers.color(str(len(self.payloads))) + " payloads loaded\n"
					messages.helpmsg(self.commands, showTitle=False)
					showTitle=False					
					cmd = ""
					showMessage=False

				elif cmd.startswith("use"):

					if len(cmd.split()) == 1:
						if settings.TERMINAL_CLEAR != "false": messages.title()
						self.ListPayloads()
						showMessage=False
						cmd = ""

					elif len(cmd.split()) == 2:

						# pull out the payload/number to use
						p = cmd.split()[1]

						# if we're choosing the payload by numbers
						if p.isdigit() and 0 < int(p) <= len(self.payloads):
							x = 1
							for (name, pay) in self.payloads:
								# if the entered number matches the payload #, use that payload
								if int(p) == x:
									self.payload = pay
									self.payloadname = name
									self.outputFileName = self.PayloadMenu(self.payload, args=args)
								x += 1

						# else choosing the payload by name
						else:
							for (payloadName, pay) in self.payloads:
								# if we find the payload specified, kick off the payload menu
								if payloadName == p:
									self.payload = pay
									self.payloadname = payloadName
									self.outputFileName = self.PayloadMenu(self.payload, args=args)

						cmd = ""
						if settings.TERMINAL_CLEAR != "false": showMessage = True

					# error catchings if not of form [use BLAH]
					else:
						cmd = ""
						showMessage=False

				elif cmd.startswith("update"):
					self.UpdateVeil()
					if settings.TERMINAL_CLEAR != "false": showMessage = True
					cmd = ""

				elif cmd.startswith("info"):

					if len(cmd.split()) == 1:
						if settings.TERMINAL_CLEAR != "false": showMessage = True
						cmd = ""

					elif len(cmd.split()) == 2:

						# pull out the payload/number to use
						p = cmd.split()[1]

						# if we're choosing the payload by numbers
						if p.isdigit() and 0 < int(p) <= len(self.payloads):
							x = 1
							for (name, pay) in self.payloads:
								# if the entered number matches the payload #, use that payload
								if int(p) == x:
									self.payload = pay
									self.payloadname = name
									self.PayloadInfo(self.payload)
								x += 1

						# else choosing the payload by name
						else:
							for (payloadName, pay) in self.payloads:
								# if we find the payload specified, kick off the payload menu
								if payloadName == p:
									self.payload = pay
									self.payloadname = payloadName
									self.PayloadInfo(self.payload)

						cmd = ""
						showMessage=False

					# error catchings if not of form [use BLAH]
					else:
						cmd = ""
						showMessage=False

				elif cmd.startswith("list") or cmd.startswith("ls"):

					if len(cmd.split()) == 1:
						if settings.TERMINAL_CLEAR != "false": messages.title()
						self.ListPayloads()

					cmd = ""
					showMessage=False

				elif cmd.startswith("exit") or cmd.startswith("q"):
					if self.oneRun:
						# if we're being invoked from external code, just return
						# an empty string on an exit/quit instead of killing everything
						return ""
					else:
						print helpers.color("\n [!] Exiting...\n", warning=True)
						sys.exit()

				# select a payload by just the number
				elif cmd.isdigit() and 0 < int(cmd) <= len(self.payloads):
					x = 1
					for (name, pay) in self.payloads:
						# if the entered number matches the payload #, use that payload
						if int(cmd) == x:
							self.payload = pay
							self.payloadname = name
							self.outputFileName = self.PayloadMenu(self.payload, args=args)
						x += 1
					cmd = ""
					if settings.TERMINAL_CLEAR != "false": showMessage = True

				# if nothing is entered
				else:
					cmd = ""
					showMessage=False

				# if we're looping forever on the main menu (Veil.py behavior)
				# reset the output filname to nothing so we don't break the while
				if not self.oneRun:
					self.outputFileName = ""

			return self.outputFileName

		# catch any ctrl + c interrupts
		except KeyboardInterrupt:
			if self.oneRun:
				# if we're being invoked from external code, just return
				# an empty string on an exit/quit instead of killing everything
				return ""
			else:
				print helpers.color("\n\n [!] Exiting...\n", warning=True)
				sys.exit()
