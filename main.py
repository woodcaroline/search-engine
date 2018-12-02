#
#
# ---------------------------- HOW TO USE FOUNDIT -------------------------------
# Run the application and visit http://localhost:8080/ to access the server
# Enter your search query in the search box and press "search" to see results
#
#

import bottle
from bottle import route, run, template, static_file, request, error
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
import httplib2
import math
from math import *
from autocorrect import spell
import search_handler


# ---------------------
# Beaker session setup
# ---------------------
from beaker.middleware import SessionMiddleware

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)


# -----------------
# Global variables
# -----------------

# Stores search history for users who have logged in previously
# Dictionary with key=user_email, value=list containing search history
search_history = dict()

# Stores search from user
query = None
redirected = False

# Used for pagination
page_number = 1
num_pages = 0


# ----------
# Home page
# ----------
@route('/', method='GET')
def index():

    # This is the homepage
    # User can either log in or browse in anonymous mode
    # ---------------------------------------------------

    # Get the session object from the environ
    session = request.environ.get('beaker.session')

    # Check to see if user is logged in
    if 'email' in session:
        logged_in = 1
        email = session['email']
    else:
        logged_in = 0

    # Process searches from user
    # --------------------------
    # Reset page number
    global page_number
    page_number = 1
    # Get search query
    global query
    query = request.query.keywords

    # If no search has been made yet, stay on index page
    if not query:
        # Logged in users get their info displayed
        if logged_in:
            recent_searches = search_handler.retrieve_search_history(query, email, search_history)
            return template('index.html', logged_in=logged_in, email=email, search_history=recent_searches)

        # Anonymous users get default page
        else:
            return template('index.html', logged_in=logged_in)

    # Once the user searches something, display results on a new page
    else:
        global redirected
        redirected = True
        bottle.redirect(str('/search'))


@route('/search', method="GET")
def search():
    # Get the session object from the environ
    session = request.environ.get('beaker.session')

    # Check to see if user is logged in
    if 'email' in session:
        logged_in = 1
        email = session['email']
    else:
        logged_in = 0

    # Process searches from user
    # --------------------------
    global query
    global redirected
    if not redirected:
        query = request.query.keywords
    redirected = False

    # -----

    # Spell check using Autocorrect library
    suggestion = list()  # List of suggested words based on user query
    for word in query.split():
        suggestion.append(spell(word))

    suggestion = ' '.join(word for word in suggestion)  # Convert to a string

    # If query was spelled correctly, don't try and suggest an alternative
    if query == suggestion:
        suggestion = None

    # -----

    # Evaluate mathematical expressions if detected
    math_result = 0
    if ("+" or "-" or "/" or "*" or "^" or "(" or ")" in query) or (any(char.isdigit() for char in query)):
        math_expr = True
        try:
            math_result = eval(query, {'sqrt': sqrt, 'pi': pi, 'log': log10, 'ln': log2,
                                       'sin': sin, 'cos': cos, 'tan': tan,
                                       'arcsin': asin, 'arccos': acos, 'arctan': atan,
                                       'e': e})
        except:
            math_expr = False

    # ------

    # Retrieve URLs from backend
    import crawler
    keyword_to_search = search_handler.parse_user_query(query)
    all_urls = crawler.get_results_db_multi(keyword_to_search)

    # Calculate number of pages needed to display these URLs (5 URLs per page)
    num_urls = len(all_urls)
    global num_pages
    num_pages = math.ceil(num_urls / 5)

    # Display the proper 5 URLs based on page number
    global page_number
    first_index = ((page_number - 1) * 5) + 1
    last_index = page_number * 5
    if last_index > len(all_urls) - 1:
        last_index = len(all_urls)
    urls = all_urls[first_index - 1:last_index]

    if logged_in:
        recent_searches = search_handler.retrieve_search_history(query, email, search_history)
        return template('search.html', urls=urls, query=query, search_history=recent_searches,
                        suggestion=suggestion, math_expr=math_expr, math_result=math_result,
                        logged_in=logged_in, email=email)
    else:
        return template('search.html', urls=urls, query=query,
                        suggestion=suggestion, math_expr=math_expr, math_result=math_result,
                        logged_in=logged_in)


# -------------------------------------------
# Quick redirect pages to update page number
# -------------------------------------------
@route('/prev_page', method="GET")
def prev_page():
    global page_number
    if page_number > 1:
        page_number = page_number - 1
    bottle.redirect(str('/search'))


@route('/next_page', method="GET")
def next_page():
    global page_number
    global num_pages
    if page_number < num_pages:
        page_number = page_number + 1
    bottle.redirect(str('/search'))


# ------------------
# Google login page
# ------------------
@route('/login', method='GET')
def login():

    # Google's oauth2client
    flow = flow_from_clientsecrets('client_secrets.json',
                                   scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
                                   redirect_uri='http://localhost:8080/redirect')
    uri = flow.step1_get_authorize_url()
    bottle.redirect(str(uri))
    return


# ----------------------
# Google Login redirect
# ----------------------
@route('/redirect')
def redirect_page():

    # Google's oauth2client
    code = request.query.get('code', '')

    flow = OAuth2WebServerFlow(client_id='764170719624-l7tbsa334trbjkg3lcg25a8uv4c9qe6v.apps.googleusercontent.com',
                               client_secret='Iq1HQBTp29giA4kGciKF30bH',
                               scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
                               redirect_uri='http://localhost:8080/redirect')

    credentials = flow.step2_exchange(code)
    token = credentials.id_token['sub']

    http = httplib2.Http()
    http = credentials.authorize(http)

    # Get user email
    from apiclient.discovery import build
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']

    # Get the session object from the environ
    session = request.environ.get('beaker.session')

    # Set the session variables (user info)
    session['email'] = user_email

    # Save the user's session for future logins
    session.save()

    # Redirect to index
    bottle.redirect(str('/'))

    return


# ------------
# Logout page
# ------------
@route('/logout', method='GET')
def logout():
    # Delete the session & redirect to index
    session = request.environ.get('beaker.session')
    session.delete()
    bottle.redirect(str('/'))
    return


# -----------
# Error page
# -----------
@error(404)
def error404(error):
    return template("error.html")


# -----------------------
# Serve static CSS files
# -----------------------
@route('/<filename:path>')
def send_static(filename):
    return static_file(filename, root='./static')


# ---------------
# Run the server
# ---------------
run(app=app)
