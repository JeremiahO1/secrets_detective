import github_wrapper
from content_analyzer import analyzer
import logging
import yaml
from localfs_wrapper import localfs
def parse_input():
	with open("input.yaml", 'r') as stream:
		try:
			return yaml.load(stream)
			
		except yaml.YAMLError as exc:
			print(exc)
			return None


logger = logging.getLogger('secret_detective')
logger.setLevel(logging.DEBUG)
log = logging.FileHandler('github_parser.log')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log.setFormatter(formatter)
logger.addHandler(log)


if __name__ == '__main__':
	search = analyzer()
	options = None
	data = []
	if options == None:
		options = parse_input()
	if options != None:
		for item in options:
			if item['provider'] == 'github':
				if item['token']:
					ghub = github_wrapper.github_wrapper(token=item['token'],organization=item['organization'])
					ghub_content = ghub.get_all_content()
					for repo in ghub.all_content:
						for branch in repo['branches']:
							for name in branch:
								for item in branch[name]:
									for path in item:
										logger.debug("finding aws keys for %s and the content is %s" %(path, item[path]))
										content = item[path]
										search.find_AWS_keys(content=content, name=path)
			if item['provider'] == 'local-fs':
				a = localfs(item['folder'])
				a.read_all_files()
				for file in a.all_content:
					for check in item['analyze']:
						getattr(search, "%s" % check['filter'])(content=file['content'], name=file['path'], search=check['search'])
	else:
		logger.error("Something went wrong setting the options")
					
