""" This exposes rss functions to be called from flask """
import feedparser

path = "http://fortydaysofdating.com/feed/"

def rss_entry_to_html(entry):
	"""Takes the entries within a full feed and seperates them out""" 
	title = entry.title
	body = entry.content
	html = "<h3>%s</h3> <p>%s</p>" % (title, body)
	return html 

def rss_to_html(path):
	""" returns a html string given a path to a rss file"""
	d = feedparser.parse(path)
	print type(d)
	# encoded_d = d.encode('UTF-8')

	return d

# wont need this function when using flask
# this takes the information from the input path and writes it to a file
# def rss_to_html_file(input_path, output_path):
# 	html = rss_to_html(input_path) 
# 	encoded = html.encode('UTF-8') # deals with special chars
# 	with open(output_path, 'w') as f:

#     	 f.write(encoded)

# if __name__ == "__main__":
# 	"""Calls the functions within this .py doc"""
# 	from sys import argv
# 	import subprocess
# 	script, input_path, output_path = argv
# 	# html = rss_to_html(filename)
# 	rss_to_html_file(input_path, output_path)

# 	subprocess.call(["open", output_path])