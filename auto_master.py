#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"


import config
from git_api import GitEngine
from git_api import GitEngineError
from jira_api import JiraEngine
from notify import NotifyEngine
from logger import get_logger 

MAIN_GIT= "origin"
ACCEPT_TO_MASTER_FILTER = "project=RAS and status = \"To Be Accepted\""
#ACCEPT_TO_MASTER_FILTER = "issuekey = \"RAS-571\""
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
		groupped_issues = self.__get_jira_issues_phase()
		#debug second phase
		LOGGER.debug("Issues: %s" % groupped_issues)
		success_issues = []
		for (issue_assignee, branch_groups) in groupped_issues.items(): 
			LOGGER.debug("Branch groups: %s", branch_groups)
			for branch in branch_groups:
				issue_keys = branch_groups[branch]
				if self.__accept_issue_phase(issue_keys, issue_assignee, branch):
					LOGGER.debug("Accept issue: %s" % issue_keys)
					success_issues += issue_keys

					if not config.is_bulk:
						break;

		LOGGER.debug("Success issues: %s" % success_issues)

		try:
			if success_issues:

				self.__git.push(config.repo_urls[self.__main_commiter], \
					self.__get_branches_name(MAIN_GIT)[1], \
					self.__accept_branch)

				for issue_key in success_issues:
					self.__jira.processWorkflow(issue_key, \
					config.jira_last_workflow)

		except GitEngineError:
			self.__note.notify(self.__main_commiter, "Push to server is Fail")
			LOGGER.error("Push is fail. Bulk = %s" % config.is_bulk)
		except:
			raise

		self.__send_notifications_phase()
		

	def __init_master_phase(self):
		LOGGER.debug("init phase")
		self.__get_changes(MAIN_GIT, config.def_branches[MAIN_GIT])

	def __get_jira_issues_phase(self):
		""" return groupped_issues["author"]["branch"] = issues  """
		issues = self.__jira.getIssuesKeyAndAssigneeByFilter(ACCEPT_TO_MASTER_FILTER)	

		groupped_issues = {}
		for (issue_key, issue_assigner) in issues:
			if not issue_assigner in groupped_issues:
				groupped_issues[issue_assigner] = {}

			branch = self.__get_branch(issue_assigner, issue_key)

			if not branch in groupped_issues[issue_assigner]:
				groupped_issues[issue_assigner][branch] = []
			
			groupped_issues[issue_assigner][branch].append(issue_key)
		
		return groupped_issues	

	def __accept_issue_phase(self, issue_keys, issue_assignee, branch):
		""" return true if task is accepted """
		LOGGER.debug("accept phase task: %s" % issue_keys)
		holder_name = issue_assignee

		accept_branch = self.__get_changes(holder_name, branch)

		main_branch = self.__get_branches_name(MAIN_GIT,\
				config.def_branches[MAIN_GIT])[1]		

		shas = None
		LOGGER.debug("Issue keys: %s" % issue_keys)
		for issue_key in issue_keys:
			sha_list = self.__git.search(issue_key, main_branch, accept_branch)
			if shas is None:
				shas = sha_list
			else:
				shas += sha_list

		LOGGER.debug("Shas: %s" % shas)
	
		if not shas:
			self.__note.notify(holder_name, "Commits for task %s wasn't found in you default branch" % issue_keys)
			LOGGER.error("Commits aren't found for task %s" % issue_keys)
			return False
		# sort shas by commit time
		shas.sort(key = lambda commitInfo: int(commitInfo[1]))

		# checkout local master branch
		self.__git.checkout(main_branch)
					
		commit_count = 0
		try:

			for sha, commitTime in shas:
				self.__git.cherry_pick(sha)
				commit_count+=1

		except GitEngineError:
			# reset to master
			self.__git.reset("HEAD~%d" % commit_count, True)		
			self.__note.notify(holder_name, "Conflicts until cherry-pick of task %s" % issue_keys)
			LOGGER.error("Cherry-pick conflict task %s" % issue_keys)
			return False

		return True

	def __send_notifications_phase(self):
		LOGGER.debug("Send phase")
		self.__note.send()
	
	def __get_branches_name(self, holder_name, branch):
		""" return tuple of branches(remote,local) for holder"""
		checkout_point =  (holder_name, branch) 
		return ("%s/%s" % checkout_point, "%s_%s" % checkout_point)

	def __get_branch(self, holder_name, issue_key = None):
		branch_name = ""
		if not issue_key is None:
			branch_name = self.__jira.getFieldValue(issue_key, config.jira_branch_field)

		if branch_name == "":
			branch_name = config.def_branches[holder_name]

		return branch_name

	def __get_changes(self, holder_name, branch):
		self.__git.fetch(config.repo_urls[holder_name], holder_name)
		
		(remote_branch, local_branch) = self.__get_branches_name(holder_name, branch)

		try:
			self.__git.checkout(remote_branch, local_branch)
		except GitEngineError:	
			# It means that the branch exists
			# And we need to checkout the branch and reset it to fetched branch with --hard
			self.__git.checkout(local_branch)
			self.__git.reset(remote_branch, True)

		return local_branch
		

if __name__ == "__main__":
	auto_master = AutoMaster()
	auto_master.main()
