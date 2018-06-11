# Github Parser
## Using github api to search and find anti-patterns
To use first propogate the input.yaml file, and then at the command line enter 'python2.7 secret_detective.py'.

WORK IN PROGRESS

This tool implements two abstractions:
	- vcs wrapper to grab all information from a VCS api
	- content analyzer to apply filters to the content from vcs to determine if sensitive data is inside
The Secret Detective is an interface that can integrate both of those abstractions

![UML Diagram]
(https://github.com/stelligent/github_parser/blob/master/diagram.jpg)

