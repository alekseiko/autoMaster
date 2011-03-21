#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"

import SOAPpy
import config

class JiraEngine: 

	def __init__(self, login = config.jiraLogin, password = config.jiraPassword, \
			url = config.jiraEndpoint):
		self.__client = SOAPpy.SOAPProxy(url)
		self.__auth = self.__client.login(login, password)

	def getIssuesKeyAndAssigneeByFilter(self, jira_filter, resultCount = config.resultCount):

		return [(issue["key"], issue["assignee"]) \
			for issue in self.__client.getIssuesFromJqlSearch(self.__auth, \
				jira_filter, resultCount)]

	def close(self, issue_key):
		self.__client.updateIssue(self.__auth, issue_key, {"status":"Closed"})

#if __name__ == "__main__":
#	engine = JiraEngine()
#	print engine.getIssuesKeyAndAssigneeByFilter("project = 10420 AND issuetype = 1 AND status = 1 AND fixVersion = 13187 AND resolution = EMPTY ORDER BY key DESC")
