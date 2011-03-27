#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"

import SOAPpy
import config

class JiraEngine: 

	def __init__(self, login = config.jira_login, password = config.jira_password, \
			url = config.jira_endpoint, close_action_id = config.jira_close_action_id):
		self.__client = SOAPpy.SOAPProxy(url)
		self.__auth = self.__client.login(login, password)
		self.__close_action_id = close_action_id

	def getIssuesKeyAndAssigneeByFilter(self, jira_filter, resultCount = config.resultCount):

		return [(issue["key"], issue["assignee"]) \
			for issue in self.__client.getIssuesFromJqlSearch(self.__auth, \
				jira_filter, resultCount)]

	def close(self, issue_key):
		self.__client.progressWorkflowAction(self.__auth, issue_key, "2", \
				[{"id":"Comment", "values":["Accepted to master"]}])

#if __name__ == "__main__":
#	engine = JiraEngine()
#	print engine.getIssuesKeyAndAssigneeByFilter("project = 10420 AND issuetype = 1 AND status = 1 AND fixVersion = 13187 AND resolution = EMPTY ORDER BY key DESC")
#	engine.close("TST-18812")
