#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"

import SOAPpy
import time
from optparse import OptionParser

import config

TIME_FORMAT = "%d%m%Y"
ISSUE_BY_PART_OF_NAME_JQL = "project = {0} AND summary ~ '{1}'" 
START_DATE_FIELD = "startDate"
TIME_SPENT_FIELD = "timeSpent"
COMMENT_FIELD = "comment"

class JiraEngine: 

	def __init__(self, login, password, url):
		self.__client = SOAPpy.SOAPProxy(url)
		self.__auth = self.__client.login(login, password)

	def addWorklogAndAutoAdjustRemainingEstimate(self, issue, createDate, \
				timeSpent, comment):

		dt_today = SOAPpy.dateTimeType(createDate)
		worklog = {START_DATE_FIELD:dt_today, \
				TIME_SPENT_FIELD:timeSpent, \
				COMMENT_FIELD:comment}

		result = self.__client.addWorklogAndAutoAdjustRemainingEstimate(self.__auth,
				issue, worklog)
		
	def getIssuesByPartOfName(self, partOfName, project = config.project, \
				resultCount = config.resultCount):

		return [(issue["key"], issue["summary"]) \
			for issue in self.__client.getIssuesFromJqlSearch(self.__auth, \
			ISSUE_BY_PART_OF_NAME_JQL.format(project, \
			partOfName), resultCount)]


	def getIssuesByFilter(self, jira_filter, resultCount = config.resultCount):

		return [(issue["key"], issue["summary"]) \
			for issue in self.__client.getIssuesFromJqlSearch(self.__auth, \
				jira_filter, resultCount)]
