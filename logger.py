#!/usr/bin/env python

__author__ = "aleksei.kornev@gmail.com (Aleksei Kornev)"

import logging
import logging.handlers

LOG_FILENAME = "robo.log"
LOGGER_LEVEL = logging.DEBUG
LOGGER_FORMAT = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOGGER_HANDLER = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20971520, backupCount=5)
LOGGER_HANDLER.setFormatter(LOGGER_FORMAT)

def get_logger(name):
	logger =  logging.getLogger(name)
	logger.setLevel(LOGGER_LEVEL)	
	logger.addHandler(LOGGER_HANDLER)
	return logger
