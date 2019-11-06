import os
import base64
#These file types will be ignored when parsing.
MEDIA_FILE_FORMAT = ['.jpg','.png', '.svg', '.ttf','.woff', '.woff2', '.eot', '.DS_Store']

class localfs():
	directory = None
	def __init__(self, directory):
		self.directory = directory
		self.all_content = []
	def read_all_files(self):
		if self.directory:
			try:
				for root, subFolders, files in os.walk(self.directory):
					for file_name in files:
						with open(os.path.join(root, file_name), 'r') as fin:
							if not any([file_type in file_name for file_type in MEDIA_FILE_FORMAT]):
								text = fin.read()
								base64_text = base64.b64encode(text)
								self.all_content.append({'path': os.path.join(root, file_name), 'content': base64_text }) 
			except Exception as e:
				print(e)
		return

#TODO Ignore image/media files to reduce bloat
