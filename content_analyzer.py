import logging
import re
import base64
from commonregex import CommonRegex

README_THRESHOLD = 100

logger = logging.getLogger('github_parser')
logger.setLevel(logging.DEBUG)
log = logging.FileHandler('github_parser.log')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log.setFormatter(formatter)
logger.addHandler(log)
class analyzer:

	def base64_decode(self, content=None, name='Not Set'):
		logger.debug('Starting to get_content for %s' % name)
		if content:
			try:
				return base64.b64decode(content)
			except Exception as e:
				logger.error('Not able to get content for %s' % name)
				return None
		else:
			logger.error('No content provided')
			return None

	def evaluate_readme(self, readme, repository='Not Set', README_THRESHOLD=100, search=None):
		file = self.base64_decode(content=readme, name='readme')
		file_words = file.split()
		print "--------------------------------------------------------------\nChecking Readme for Repository: %s \n--------------------------------------------------------------" % repository
		if len(file_words) < README_THRESHOLD:
			print "Warning: Readme is too short; only %s words." % len(file_words)
		else:
			print "Pass: Readme has exceeded the threshold of %" % README_THRESHOLD
		return
#TODO Add Strict seach or Loose Search. Strict == current regex search. Loose Search would also include any match with "aws_secret" or "aws_key"
	def find_AWS_keys(self, content, name, search=None):
		logger.debug("Entering find_AWS_keys with %s" % name)
		file = self.base64_decode(content=content, name=name)
		print "--------------------------------------------------------------\nChecking for AWS Keys in: %s \n--------------------------------------------------------------" % name
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
			logger.error("There was an error parsing %s" % name)
			print 'Error parsing %s' % name
		return

	def find_passwords(self, content, name, search=None):
		logger.debug("Entering find_passwords with %s" % name)
		file = self.base64_decode(content=content, name=name)
		print "--------------------------------------------------------------\nChecking for passwords in: %s \n--------------------------------------------------------------" % name
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
			logger.error("There was an error parsing %s" % name)
			print 'Error parsing %s' % content.name
		return

	#TODO: Find PII
	def find_pii(self, content, name, search):
		logger.debug("Entering find_pii with %s" % name)
		file = self.base64_decode(content=content, name=name)
		print "--------------------------------------------------------------\nChecking for PII in: %s \n--------------------------------------------------------------" % name
		if file:
			parsed_text = CommonRegex(file)
		else:
			logger.warning("error with input for %s" % name)
		if parsed_text:
			for term in search:
				print term
				try:
					a = getattr(parsed_text, "%s" % term)
					if len(a)<1:
						print "None"
					else:
						print "Found Potential PII: %s" % a
				except AttributeError as ae:
					print "None"



	#TODO: S3 Source

	#TODO: find 

	#TODO: Find Cloudformation Templates - parse with cfn-nag
