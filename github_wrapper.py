import github
from github import Github, Organization, PaginatedList

import logging
#These file types will be ignored when parsing.
MEDIA_FILE_FORMAT = ['.jpg','.png', '.svg', '.ttf','.woff', '.woff2', '.eot', '.DS_Store']

logger = logging.getLogger('github_wrapper')
logger.setLevel(logging.DEBUG)
log = logging.FileHandler('github_parser.log')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log.setFormatter(formatter)
logger.addHandler(log)


class github_wrapper(github.Github):
	__token = None # string
	organization = None # string
	all_content = [] # list[dict{string repository: name, readme: content, branches: list[dict{string Branch, Files list[dict{string file_path: base64_text}]}}]
	def __init__(self, token=None, organization=None):
		if token and organization:
			self.__token = token
			self.organization = organization
		else:
			return None

	def get_all_content(self):
		g = Github(self.__token)
		if self.organization:
			org = g.get_organization(self.organization)
			repo_collector = []
			logger.debug("begininng loop to get all repos for org %s" % org.name)
			for repo in org.get_repos():
				logger.debug("analyzing repo %s" % repo.name)
				try:
					readme = repo.get_readme().content
				except github.GithubException as e:
					logger.error(e)
				branches = repo.get_branches()
				branch_collector = []
				for branch in branches:
					logger.debug("analyzing branch %s" % branch.name)
					files = []
					commit = branch.commit.sha
					tree = repo.get_git_tree(commit, recursive=True)
					for element in tree.tree:
						if not any([file_type in element.path for file_type in MEDIA_FILE_FORMAT]):
							logger.debug("analyzing element %s" % element.path)
							if element.type == 'blob':
								content = repo.get_contents(element.path,ref=commit)
								files.append({element.path: content.content})
					branch_collector.append({branch.name: files})
				self.all_content.append({'repository': repo.name, 'readme':readme, 'branches': branch_collector})
				break
			#self.all_content = repo_collector
		else:
			logger.warning("No organization specified")
			return