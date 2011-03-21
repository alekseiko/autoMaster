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

		return stdout_value	

	def push(self, remote_path, local_branch, remote_branch)
		command = "git push %s %s:%s" % (remote_path, local_branch, remote_branch)
		
		self.__exec(command)

	def fetch(self, remote_path, refs_name):
		command = "git fetch " + remote_path
		# add refs definition
		command += " +refs/heads/*:refs/remotes/%s/*" % refs_name
		
		self.__exec(command)

	def cherry_pick(self, from_sha):
		command = "git cherry-pick %s" % from_sha

		self.__exec(command)


	def search(self, regexp):
		""" return list of lists sha-> commit time in UNIX timestamp """
		command = "git log --grep='" + regexp +"' --pretty=format:%H_%ct"

		# split commit shas to list
		return [ line.split("_") \
				for line in self.__exec(command).split("\n")]

	
	def checkout(self, sha, branch_name = None):
		command = "git checkout"
		
		if branch_name is not None:
			command += " -b " + branch_name

		command += " " + sha

		self.__exec(command)
			
	def reset(self, sha, isHard = False):
		command = "git reset"
		if isHard:
			command = command + " --hard"
		command = command + " " + sha
		
		self.__exec(command)

class GitEngineError(Exception):
	
	def __init__(self, status, error):
		self.status = status
		self.error = error

	def __str__(self):
		return repr(self.status + " " + self.error)

if __name__ == "__main__":
	engine = GitEngine()
#	engine.reset("HEAD^")
#	print engine.search("1")
#	engine.checkout(engine.search("h")[1], "test1")
	engine.checkout("test/master", "test3000")
#	engine.cherry_pick("test1")
#	engine.fetch("git://github.com/teamurko/Cube.git", "cube")
