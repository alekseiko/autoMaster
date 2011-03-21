#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"


import config
from smtplib import SMTP
from email.mime.text import MIMEText

class NotifyEngine: 

	def __init__(self):
		self.__notes = []
		self.__transports = [EmailTransport()]

	def notify(self, who, note):
		""" who is repository holder name  """
		self.__notes.append((who, note))

	def send(self):
		for (who, note) in self.__notes:
			for trans in self.__transports:
				trans.send(who, note)

class EmailTransport:
	
	def __init__(self, host = config.email_host, \
				port = config.email_port, from_email = config.from_email):
		self.__host = host
		self.__port = port
		self.__from_email = from_email

	def send(self, to, msg_body):
		to_email = config.holders_to_email[to]
		
		msg = MIMEText(msg_body)		
		msg["Subject"] = config.email_subject
		msg["From"] = self.__from_email
		msg["To"] = to_email

		server = SMTP(self.__host, self.__port)
		server.sendmail(self.__from_email, to_email, msg.as_string())
		server.quit()
