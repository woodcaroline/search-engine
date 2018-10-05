#
#
# ---------------------------- HOW TO USE FOUNDIT -------------------------------
# Run the application and visit http://localhost:8080/ to access the server
# Enter your search query in the search box and press "search" to see results
#
#

from bottle.bottle import route, run, template, static_file, request
import search_handler


historic_keywords = dict()  # Global variable to store every word entered by the user since server launch


#
# '/' is the landing page where the search is entered
#
@route('/')
def index():
    return template('index.html', results=dict(), historic_results=dict())


#
# Receive search query entered by the user, then display results
#
@route('/', method='POST')
def form_handler():
    # Get search query submitted by user
    query = request.forms.get('keywords')

    # Display current & historic results on index page
    unique_keywords = search_handler.parse_user_query(query)

    global historic_keywords
    top_20_keywords = search_handler.most_searched_keywords(unique_keywords, historic_keywords)

    return template('index.html', results=unique_keywords, historic_results=top_20_keywords)


#
# Serve static CSS files
#
@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./static')


#
# Run the server
#
run(host='localhost', port=8080, debug=True)
