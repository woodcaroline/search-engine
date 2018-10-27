#
#
# ---------------------------- HOW TO USE FOUNDIT -------------------------------
# Run the application and visit http://localhost:8080/ to access the server
# Enter your search query in the search box and press "search" to see results
#
#

import bottle
from bottle import route, run, template, static_file, request
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
import httplib2


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
    else:
        logged_in = 0

    # Process searches from user
    # --------------------------
    import search_handler
    query = request.query.keywords

    # Display current (& historic if logged in) results on index page
    current_keywords = search_handler.parse_user_query(query)

    # Logged in users get search history
    if logged_in:

        global search_history
        recent_keywords = search_handler.retrieve_search_history(current_keywords, session['email'], search_history)

        return template('index.html', results=current_keywords, historic_results=recent_keywords,
                        logged_in=logged_in,
                        email=session['email'])

    # Anonymous users only get current search results
    else:
        return template('index.html', results=current_keywords, logged_in=logged_in)


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
