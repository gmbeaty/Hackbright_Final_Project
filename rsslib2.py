""" This exposes rss functions to be called from flask """
import feedparser

def rss_entry_to_html(entry):
	"""Takes the entries within a full feed and seperates them out""" 
	# want to use this function to populate my post table
	title = entry.title
	author = entry.author
	content = entry.description
	image = None #need to figure out how to access and will be a url
	url = entry.description.link
	timestamp = entry.published

	html = "<h3>%s</h3> <p>%s</p>" % (title, body)
	return html 

def rss_url_to_dict(path):
	""" rss url to dictionary"""
	#want to use this function to populate my feed table

	d = feedparser.parse(path)
	# return d 

	title = d.feed.title
	print title
	description = d.feed.description
	print description
	image = d.feed.image.url
	print image

	output = "<h1>%s</h1> <h2>%s</h2> " % (title, description) 
	for entry in d.entries:
		html = rss_entry_to_html(entry)
		output += html 
	return output

def url_to_xml_feed(url):
	pass
	#call out to the website using the url
	
	#return rss/xml feed information to be parsed

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