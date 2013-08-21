R2S2 is a RSS Reader created as my final project for Hackbright Academy.

When it came time to select my project in July, the timing aligned with Google reader being "sunsetted." I was bummed about my favorite reader going away, but I was excited and empowered that with all my new coding skills - I could create my own! 

R2S2was written using Sqlite3, SQL Alchemy, Python, LXML parser, Flask, Jinja, WTForms, HTML and CSS.

R2S2 has many standard reader capabilities such as viewing all the blogs the user follows together chronologically, viewing feeds indivdually, easily adding/removing blog streams and automatically updating all your saved feeds with the up-to-date posts.

When a user goes to add a url to their blog stream, I've set this process up with LXML to locate a specific meta tag with in the web page that holds the link to the RSS XML information and will grab that link to do the parsing of the elements to be stored in the database. I was especially proud of this feature as it does not rely on perfect user input and many other readers do not offer this functionality.


Running R2S2


To run R2S2 locally, create virtual env and install the packages listed in the above requirements.txt file.

From there, running views.py will provide all user interaction to be functional and running add_atom.py in a seperate terminal window will automatically update the posts in each blog stream added.







