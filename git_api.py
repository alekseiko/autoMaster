#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"


import config
import subprocess
import sys


class GitEngine: 

	def __init__(self, repo = config.repo_dir):
		self.__repo = repo

	def __exec(self, command):
		proc = subprocess.Popen(command, cwd = self.__repo, \
					 stderr = subprocess.PIPE, \
	                                 stdout = subprocess.PIPE, \
					 shell = True)
		try:
			stdout_value = proc.stdout.read().rstrip()
			stderr_value = proc.stderr.read().rstrip()
			status = proc.wait()
		finally:
			proc.stdout.close()
			proc.stderr.close()

		if status != 0:
			raise GitEngineError(status, stderr_value)		
		

	def fetch(self, remote_path):
		pass

	def cherry_pick(self, from_sha):
		pass

	def search(self, branch_name, regexp):
		pass
	
	def checkout(self, sha, branch_name = None):
		pass

	def reset(self, isHard, sha):
		command = "git reset"
		if isHard:
			command = command + " --hard"
		command = command + " " + sha
		
		return self.__exec(command)

class GitEngineError(Exception):
	
	def __init__(self, status, error):
		self.__status = status
		self.__error = error

	def __str__(self):
		return repr(self.__status + " " + self.__error)

if __name__ == "__main__":
	engine = GitEngine()
#	engine.reset(False, "HEAD^")
