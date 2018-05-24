import requests
import urllib2
import base64
import logging
from pprint import pprint
from requests.auth import HTTPBasicAuth
import re
import github
from github import Github, Organization, PaginatedList
import sys

README_THRESHOLD = 100
#These file types will be ignored when parsing.
MEDIA_FILE_FORMAT = ['.jpg','.png', '.svg', '.ttf','.woff', '.woff2', '.eot']

#TODO Use Sys Args to populate ORG
ORG = 'vocalocity'
logger = logging.getLogger('github_parser')
logger.setLevel(logging.DEBUG)
log = logging.FileHandler('github_parser.log')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log.setFormatter(formatter)
logger.addHandler(log)

if len(sys.argv) > 1:
	github_token = sys.argv[1]
else: 
	logger.critical("No Github Token specified") 
	print "Error View Logs"
	quit()


def decode_content(content):
	logger.debug('Starting to get_content for %s' % content.path)
	try:
		if content.type == 'file':
			return base64.b64decode(content.content)
	except Exception as e:
		logger.error('Not able to get content for %s' % content.path)
		return None

def evaluate_readme(readme):
	file = readme.content
	file_words = file.split()
	print "--------------------------------------------------------------\nChecking Readme for Repository: %s \n--------------------------------------------------------------" % readme.repository.name
	if len(file_words) < README_THRESHOLD:
		print "Warning: Readme is too short only %s words." % len(file_words)
	else:
		print "Pass: Readme has exceeded the threshold"
	return

def find_AWS_keys(content):
	logger.debug("Entering find_AWS_keys with %s" % content.name)
	file = decode_content(content)
	print "--------------------------------------------------------------\nChecking for AWS Keys in: %s \n--------------------------------------------------------------" % content.name
	if file:
		match_key_regex = re.compile('(A[K,S][A-Z,0-9]{11,20})')
		match_key = match_key_regex.findall(file)
		match_secret_regex = re.compile('(?:A[K,S][A-Z,0-9]{11,20}\W+(?:\w+\W+){0,6}?([\s,\',",=][\w/\\\\]{40,41}?)|([\s,\',",=][\w/\\\\]{40,41}?)\W+(?:\w+\W+){0,6}?A[K,S][A-Z,0-9]{11,20})')
		match_secret = match_secret_regex.findall(file)
		keys_found = []
		secrets_found = []
		if match_key:
			keys_found = match_key
		else:
			logger.debug("No AWS Access Keys Found")
		if match_secret:
			logger.debug("Found a Secret")
			for secret in match_secret:
				s = str(secret[0])
				remove_qoutes = s.replace("'","").replace('"','')
				secrets_found.append(remove_qoutes)
		else:
			logger.debug("No AWS Secret Keys Found")
		if match_key or secrets_found:
			print {'Keys':keys_found,'Secrets':secrets_found}
		else:
			logger.debug("No aws keys found")
			print 'Pass: No AWS keys found'
	else:
		logger.error("There was an error parsing %s" % content.name)
		print 'Error parsing %s' % content.name
	return

def find_passwords(content):
	logger.debug("Entering find_passwords with %s" % content.name)
	file = decode_content(content)
	print "--------------------------------------------------------------\nChecking for passwords in: %s \n--------------------------------------------------------------" % content.name
	if file:
		match_password_regex = re.compile('(.*[pPaAsSwWoOrRdD]{3,}\s*[=:\']\s*\S*)')
		match_password = match_password_regex.findall(file)
		passwords_found = []
		if match_password:
			passwords_found = match_password
			print {'Passwords':passwords_found}
		else:
			logger.debug("Pass: No passwords Found")
		
	else:
		logger.error("There was an error parsing %s" % content.name)
		print 'Error parsing %s' % content.name
	return

############# Begin searching ##################
g = Github(github_token)
organization = None
organization = g.get_organization(ORG)
for repo in organization.get_repos():
	try:
		print '#############################\n# Repository: %s #\n#############################' % repo.name
		readme = repo.get_readme()
		evaluate_readme(readme)
	except github.GithubException as e:
		logger.error(e)
	branches = repo.get_branches()
	for branch in branches:
		print '===========================\n Branch: %s \n===========================' % branch.name
		commit = branch.commit.sha
		print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n Commit: %s \n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~' % commit
		tree = repo.get_git_tree(commit, recursive=True)
		for element in tree.tree:
			if element.type == 'blob':
				content = repo.get_contents(element.path,ref=commit)
				if not any([file_type in element.path for file_type in MEDIA_FILE_FORMAT]):
					print "--------------Searching for Passwords---------------"
					find_passwords(content)
					print "--------------Searching for AWS Keys---------------"
					find_AWS_keys(content)

