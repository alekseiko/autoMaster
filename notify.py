#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"


import config
from smtplib import SMTP
from email.mime.text import MIMEText

class NotifyEngine: 

	def __init__(self):
		self.__notes = []
		self.__transports = [GmailTransport()]

	def notify(self, who, note):
		""" who is repository holder name  """
		self.__notes.append((who, note))

	def send(self):
		for (who, note) in self.__notes:
			for trans in self.__transports:
				trans.send(who, note)

class GmailTransport:
	
	def __init__(self, host = config.email_host, \
				port = config.email_port, from_email = config.from_email, \
				login = config.email_login, password = config.email_password):
		self.__host = host
		self.__port = port
		self.__from_email = from_email
		self.__login = login
		self.__password = password

	def send(self, to, msg_body):
		to_email = config.holders_to_email[to]
		
		msg = MIMEText(msg_body)		
		msg["Subject"] = config.email_subject
		msg["From"] = self.__from_email
		msg["To"] = to_email

		server = SMTP(self.__host, self.__port)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login(self.__login, self.__password)
		server.sendmail(self.__from_email, to_email, msg.as_string())
		server.close()

#if __name__ == "__main__":
#	gmail = GmailTransport()
#	gmail.send("akornev", "Hi i am the robot. Gmail transport works. Thanks :-)")
#	engine = NotifyEngine()
#	engine.notify("akornev", "All are fine")
#	engine.notify("akornev", "Hey All are fine")
#	engine.send()
