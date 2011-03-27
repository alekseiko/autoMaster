#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"


import config
from git_api import GitEngine
from git_api import GitEngineError
from jira_api import JiraEngine
from notify import NotifyEngine
from logger import get_logger 

MAIN_GIT= "origin"
#ACCEPT_TO_MASTER_FILTER = "project=RAS and status = \"To Be Accepted\""
ACCEPT_TO_MASTER_FILTER = "issuekey = \"RAS-571\""
LOGGER = get_logger("auto_master")

class AutoMaster: 

	def __init__(self):
		self.__git = GitEngine()
		self.__jira = JiraEngine()
		self.__note = NotifyEngine()
		self.__main_commiter = config.main_commiter
		self.__accept_branch = config.accept_branch

	def main(self):
		# run first phase
		self.__init_master_phase()
		issues = self.__get_jira_issues_phase()
		#debug second phase
		LOGGER.debug("Issues: %s" %issues)
		success_issues = []
		for (issue_key, issue_assignee) in issues:
			if self.__accept_issue_phase(issue_key, issue_assignee):
				LOGGER.debug("Accept issue: %s" % issue_key)
				if not config.is_bulk:
					LOGGER.debug("Push single issue: %s" % issue_key)
					try:
						self.__git.push(config.repo_urls[self.__main_commiter], \
							config.def_branches[MAIN_GIT], \
							self.__accept_branch)

						self.__jira.close(issue_key)

					except GitEngineError:
						self.__note.notify(self.__main_commiter, "Push to server is Fail")
						LOGGER.error("Non bulk push is Fail")
						# if push is fail we will not accept anything more
						break
						
				else:
					success_issues.append(issue_key)

		LOGGER.debug("Success issues: %s" % success_issues)

		if config.is_bulk:
			try:
				self.__git.push(config.repo_urls[self.__main_commiter], \
					self.__get_branches_name(MAIN_GIT)[1], \
					self.__accept_branch)

				for issue_key in success_issues:
					self.__jira.close(issue_key)
			except:
				self.__note.notify(self.__main_commiter, "Push to server is Fail")
				LOGGER.error("Bulk push is fail")

		self.__send_notifications_phase()
		

	def __init_master_phase(self):
		LOGGER.debug("init phase")
		self.__get_changes(MAIN_GIT)

	def __get_jira_issues_phase(self):
		""" return list of tuples (issue key -> assignee) """
		return self.__jira.getIssuesKeyAndAssigneeByFilter(ACCEPT_TO_MASTER_FILTER)	

	def __accept_issue_phase(self, issue_key, issue_assignee):
		""" return true if task is accepted """
		LOGGER.debug("accept phase task: %s" % issue_key)
		holder_name = issue_assignee
		self.__get_changes(holder_name)
		shas = self.__git.search(issue_key)
		
		LOGGER.debug("Shas: %s" % shas)
	
		if not shas:
			self.__note.notify(holder_name, "Commits for task %s didn't find in you default branch" % issue_key)
			LOGGER.error("Commits isn't found for task %s" % issue_key)
			return False
		# sort shas by commit time
		shas.sort(key = lambda commitInfo: int(commitInfo[1]))

		# checkout local master branch
		self.__git.checkout(self.__get_branches_name(MAIN_GIT)[1])
					
		commit_count = 0
		try:

			for sha, commitTime in shas:
				self.__git.cherry_pick(sha)
				commit_count+=1

		except GitEngineError:
			# reset to master
			self.__git.reset("HEAD~%d" % commit_count, True)		
			self.__note.notify(holder_name, "Conflicts until cherry-pick of task %s" % issue_key)
			LOGGER.error("Cherry-pick conflict task %s" % issue_key)
			return False

		return True

	def __send_notifications_phase(self):
		LOGGER.debug("Send phase")
		self.__note.send()
	
	def __get_branches_name(self, holder_name):
		""" return tuple of branches(remote,local) for holder"""
		checkout_point =  (holder_name, config.def_branches[holder_name])
		return ("%s/%s" % checkout_point, "%s_%s" % checkout_point)

	def __get_changes(self, holder_name):
		self.__git.fetch(config.repo_urls[holder_name], holder_name)
		
		(remote_branch, local_branch) = self.__get_branches_name(holder_name)
		try:
			self.__git.checkout(remote_branch, local_branch)
		except GitEngineError:	
			# It means that the branch exists
			# And we need to checkout the branch and reset it to fetched branch with --hard
			self.__git.checkout(local_branch)
			self.__git.reset(remote_branch, True)
		

if __name__ == "__main__":
	auto_master = AutoMaster()
	auto_master.main()
