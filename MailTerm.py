#Developer: developermind405@gmail.com
import smtplib,imapclient,sys,pyzmail,sqlite3,base64,os,threading,pygame
import subprocess as sub
pygame.mixer.init()
if os.path.isfile("alert.wav"):
	wave_sound = pygame.mixer.Sound("alert.wav")
else:
	print "Missing alert.wav"
from Crypto.Cipher import AES
import hashlib,random,string
sub.call("clear")
#########################################Waring Very Important####################
#####################IV
iv = '\xd3\xa8\xd9\x08<y\x04<\xb9\xbc\x8aa\x05\xb4+\xf4'

#######################################Function############################
def help():
	print "Command                       Discription"
	print "-----------------------------------------"
	print "--send                      send mail"
	print "--inbox                   Open Inbox"
	print "--init                  Initzial Email Data"
	print "--reset                Reset programm"

def randomKey():
	key = ""
	for i in range(5):
		t = random.choice(string.ascii_letters)
		key += t
	return hashlib.new("sha512", t).hexdigest()
def pad(str):
	while len(str)%16 != 0:
		str = str + " "
	return str

def enc(key,message,iv):
	message = pad(message)
	key = hashlib.sha256(str.encode(key))
	cipher = AES.new(key.digest(),AES.MODE_CBC,iv)
	return (cipher.encrypt(message),iv)

def dec(key, ciphertext,iv):
	key = hashlib.sha256(str.encode(key))
	cipher = AES.new(key.digest(),AES.MODE_CBC,iv)
	return cipher.decrypt(ciphertext)
def show_mail(number):
	global server
	message = server.fetch([number],["BODY[]","FLAGS"])
	pyz = pyzmail.PyzMessage.factory(message[number]["BODY[]"])
	su = pyz.get_subject()
	try:
		emnam = str(pyz.get_addresses("to")[0][0])
		em = str(pyz.get_addresses("to")[0][1])
		nam = str(pyz.get_addresses("from")[0][1])
		namenam = str(pyz.get_addresses("from")[0][0])
		c = pyz.get_addresses("cc")
		bcc = pyz.get_addresses("bcc")
		if c == []:
			c = "None"
		else:
			c = c[0]
		if bcc == []:
			bcc = "None"
		else:	
			bcc = bcc[0]
		newword  = ""
		txt = pyz.text_part.get_payload().decode(pyz.text_part.charset) 
		print
		print "                                  \x1b[37mEmail"
		print "-------------------------------------------------------------------------------"
		print "From: "+nam
		print "Name: " + namenam
		print "To: "+em
		print "Name: "+emnam
		print "Cc: " +c
		print "Bcc: " + bcc
		print 
		print txt
		print
		print "\x1b[39m"
	except:
		print "\x1b[31m[-]Email is a draft\x1b[39m" 
def jn():
	print "\x1b[31m[!]Warning the email is permanently deleted\x1b[34m\n"
	jn = raw_input("Delete? [j,n]: ")
	if jn.lower() == "j":
		return True
	else:
		return False
notify_alert = True
def notify():
	global notiy_alert,server
	alls = server.search(["ALL"])
	last = len(alls)
	while notify_alert:
		ser = imapclient.IMAPClient(imap, ssl=True)
		ser.login(email,base64.decodestring(password))
		dir = ser.select_folder("INBOX")
		alls = ser.search(["ALL"])
		if len(alls) > last:
			wave_sound.play()
			last = len(alls)
			server = imapclient.IMAPClient(imap, ssl=True)
			server.login(email,base64.decodestring(password))
			dir = server.select_folder("INBOX")
###########################################################################
if len(sys.argv) > 1:
	parameter = sys.argv[1]
	if parameter.startswith("--inbox"):
		if os.path.isfile("Mail.db"):
			print "                                  INBOX"		
			print "-----------------------------------------------------------------------"
			try:
				db = sqlite3.connect("Mail.db")
				cmd = db.cursor()
				email = str(cmd.execute("select Email from Data").fetchone()[0])
				passwd = open("Passwd", "r").read()
				key_load = str(cmd.execute("select Key from Data").fetchone()[0])
				password = dec(key_load,passwd,iv)
				imap = str(cmd.execute("select Imap from Data").fetchone()[0])
			except:
				print "\x1b[31m[-]Failed to load data\x1b[39m"
				sys.exit(0)	
			server = imapclient.IMAPClient(imap, ssl=True)
			try:
				server.login(email,base64.decodestring(password))
			except:
				print "Error: Less secure apps are still on or their password is wrong"
				sys.exit(0)
			dir = server.select_folder("INBOX")
			last_ = cmd.execute("select Last from Email").fetchone()			
			if last_:
				try:
					last = int(last_[0])
					now = int(dir[b"EXISTS"])
					delta = now - last
					print "\t\t\t    \x1b[33m[*]%i new email(s)\x1b[39m" % delta
					cmd.execute("delete from Email")
					db.commit()
					cmd.execute("insert into Email values('%i')" % now)
					db.commit()
				except:
					print "\x1b[31m[-]Error to load information from database\x1b[32m"
			else:
				now = int(dir[b"EXISTS"])
				cmd.execute("insert into Email values('%i')" % now)
				db.commit()
			inbx = True
			while inbx:
				command = raw_input("\x1b[39mINBOX#\x1b[34m ")
				if command.startswith("read "):
					try:
						print "\x1b[33m"
						fr_om = command.split("read ")[1]
						results = server.search(["FROM", fr_om])
						if len(results) > 0:
							print "Choose one of these numbers"
							for number in results:
								print number
							choose = int(raw_input("Number: "))
							try:
								if not choose in results:
									print "Email not exist!"
								else:
									try:
										show_mail(choose)
									except:
										print "Only numbers not str"
							except:
								print "Only int"
								
							
					except:
						print "Missing read <from>"
				elif command == "show all":
					print "\x1b[33m"
					all = server.search(["ALL"])
					print
					for i in all:
						print i
					print	

				elif command == "exit":
					notify_alert = False
					inbx = False
				elif command.startswith("search "):
					try:
						uid = command.split("search ")[1]
						result = server.gmail_search(uid)
						print "------------------------------"
						for i in result:
							print i
						print "------------------------------"
					except:
						print "Missing parameter Usage: search <Subject>"
				elif command.startswith("delete "):
					try:
						uid = int(command.split("delete ")[1])
						all = server.search(["ALL"])
						if uid in all:
							if jn():
								server.delete_messages(uid)
								server.expunge()
								now = len(server.search(["ALL"]))
								cmd.execute("delete from Email")
								db.commit()
								cmd.execute("insert into Email values('%i')" % now)
								db.commit()
					except:
						print "Only Number!"
					
				elif command.startswith("show "):
					uid = command.split("show ")[1]
					all = server.search(["ALL"])
					try:
						choose = int(uid)
						if choose in all:
							show_mail(choose)
						else:
							print "\x1b[31m[-]Mail not exist!\x1b[39m"
						
							
					except:
						print "Only numbers!"
				elif command.lower() == "help":
					print "Command                      Discription"
					print "----------------------------------------"
					print "show <number>             Show mail"
					print "show all                 Show all mails"
					print "delete <number>      Delete Mail"
					print "search              Search mail subject"
					print "read   <from>       read from sender"
					print "exit              logout"
					print "help              Show help message"
					print "notify on/off     Notify"
					print "clear         clear display"
				elif command.startswith("notify "):
					onoff = command.split("notify ")[1]
					if onoff == "on":
						notify_alert = True
						cthread = threading.Thread(target=notify)
						cthread.start()
						print "\x1b[33m[+]Notify on\x1b[39m"
					elif onoff == "off":
						notify_alert = False
						print "\x1b[33m[+]Notify off\x1b[39m"
					else:
						print "Missing parameter on/off"
				elif command == "clear":
					d = sub.call("clear") ; del d
				elif command == "send":
					try:
						db = sqlite3.connect("Mail.db")
						cmd = db.cursor()
						email = str(cmd.execute("select Email from Data").fetchone()[0])
						passwd = open("Passwd", "r").read()
						key_load = str(cmd.execute("select Key from Data").fetchone()[0])
						password = dec(key_load,passwd,iv)
						imap = str(cmd.execute("select Imap from Data").fetchone()[0])
						server = str(cmd.execute("select Server from Data").fetchone()[0]) 
					except:
						print "\x1b[31m[-]Failed to load data\x1b[39m"	
					smtp = smtplib.SMTP(server)
					smtp.starttls()
					smtp.login(email,base64.decodestring(password))
					to = raw_input("To: ")
					sub = raw_input("Subject: ")
					print 
					text = raw_input("Message: ")
					smtp.sendmail("spezialcoder@gmail.com", to,"Subject: {0}\n{1}".format(sub,text))
					smtp.quit()
					print "\x1b[32m			[+]Email Transfered"
						
					
			server.logout()
			print
			print "Shutdown MailTerm...."
			sys.exit(0)
				
			
		else:
			print "Missing DB"
			
			
	elif parameter == "--init":
		print
		print "Bsp: smtp.gmail.com:587"
		print 
		sm = raw_input("EmailServer: ")
		print 
		print "Bsp: imap.gmail.com"
		print
		im = raw_input("ImapServer: ")
		email = raw_input("Email: ")
		print
		print "Your password is very protected"
		print
		key_random = randomKey()
		(passwd,iv) = enc(key_random,base64.encodestring(raw_input("Password: ")),iv)
		if os.path.isfile("Mail.db"):
			db = sqlite3.connect("Mail.db")
			cmd = db.cursor()
			cmd.execute("delete from data")
			db.commit()
			cmd.execute("insert into data values('{0}','{1}','{2}','{3}')".format(email,str(key_random),sm,im))
			with open("Passwd", "w") as asdf:
				asdf.write(passwd)
				asdf.close()
			db.commit()
			sys.exit(0)
		
	elif parameter == "--send":
		if os.path.isfile("Mail.db"):
			try:
				db = sqlite3.connect("Mail.db")
				cmd = db.cursor()
				email = str(cmd.execute("select Email from Data").fetchone()[0])
				passwd = open("Passwd", "r").read()
				key_load = str(cmd.execute("select Key from Data").fetchone()[0])
				password = dec(key_load,passwd,iv)
				imap = str(cmd.execute("select Imap from Data").fetchone()[0])
				server = str(cmd.execute("select Server from Data").fetchone()[0]) 
			except:
				print "\x1b[31m[-]Failed to load data\x1b[39m"
				sys.exit(0)	
		else:
			print "Missing DB"
			sys.exit(0)
		smtp = smtplib.SMTP(server)
		smtp.starttls()
		smtp.login(email,base64.decodestring(password))
		to = raw_input("To: ")
		sub = raw_input("Subject: ")
		print 
		text = raw_input("Message: ")
		smtp.sendmail("spezialcoder@gmail.com", to,"Subject: {0}\n{1}".format(sub,text))
		smtp.quit()
		print "\x1b[32m			[+]Email Transfered"
	elif parameter == "--help":
		help()
		sys.exit(0)
	elif parameter == "--reset":
		try:
			os.unlink("Passwd")
		except:	
			print "Missing Password file"
		if os.path.isfile("Mail.db"):
			db = sqlite3.connect("Mail.db")
			cmd = db.cursor()
			cmd.execute("delete from Data")
		 	db.commit()
			cmd.execute("delete from Email")
			db.commit()
			db.close()
			print "\x1b[33m[+]Reset complete\x1b[39m"
			sys.exit(0)
		else:
			print "Missing Mail.db"
		
	else:
		help()
else:
	help()		
		

