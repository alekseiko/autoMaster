#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"

import SOAPpy
import config

#SOAPpy.Config.debug = 1

class JiraEngine: 

	def __init__(self, login = config.jira_login, password = config.jira_password, \
			url = config.jira_endpoint):
		self.__client = SOAPpy.SOAPProxy(url)
		self.__auth = self.__client.login(login, password)

	def getIssuesKeyAndAssigneeByFilter(self, jira_filter, resultCount = config.resultCount):

		return [(issue["key"], issue["assignee"]) \
			for issue in self.__client.getIssuesFromJqlSearch(self.__auth, \
				jira_filter, resultCount)]

	def processWorkflow(self, issue_key, workflow_name):
		action_id = self.__findWorkflowId(issue_key, workflow_name)

		self.__client.progressWorkflowAction(self.__auth, issue_key, \
				action_id, \
				[{"id":"Comment", "values":["Accepted to master"]}])

	def getFieldValue(self, issue_key, field_name):
		field_id = self.__findFieldId(issue_key, field_name)
		if field_id == None:
			return ""
		issue = self.__client.getIssue(self.__auth, issue_key)
		field_values =  issue["customFieldValues"]

		for value in field_values:
			if value["customfieldId"] == field_id:
				return value["values"][0]
		return ""

	def __findFieldId(self, issue_key, field_name):
		fields = self.__client.getFieldsForEdit(self.__auth, issue_key)

		for field in fields:
			if field["name"] == field_name:
				return field["id"]
		return None

	def __findWorkflowId(self, issue_key, workflow_name):
		actions = self.__client.getAvailableActions(self.__auth, issue_key)
		for action in actions:
			if action["name"].lower() == workflow_name.lower():
				return action["id"]
		raise JiraEngineError("Workflow %s isn't found" % workflow_name)
	
class JiraEngineError(Exception):
	
	def __init__(self, error):
		self.error = error

	def __str__(self):
		return repr(self.error)

#if __name__ == "__main__":
#	engine = JiraEngine()
#	print engine.getFieldValue("RAS-860", "Branch")
#	print engine.getIssuesKeyAndAssigneeByFilter("project = 10420 AND issuetype = 1 AND status = 1 AND fixVersion = 13187 AND resolution = EMPTY ORDER BY key DESC")
#	engine.processWorkflow("RAS-791", "close")
