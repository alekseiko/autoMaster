#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"

import logging
import logging.config

logging.config.fileConfig("logging.conf")

def get_logger(name):
	return logging.getLogger(name)
