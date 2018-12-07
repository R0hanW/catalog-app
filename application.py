from flask import (
Flask,
render_template,
url_for,
session as login_session,
make_response,
flash,
jsonify,
request,
redirect)
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from databaseSetup import Category, Item, User, Base
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
import requests

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db',
                        connect_args={'check_same_thread':False},
                        poolclass = StaticPool)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
open('clientSecrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = 'Catalog App'

#homepage shows both categories and the most recently added items
@app.route('/')
def homepage():
    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by("id desc").limit(10)
    return render_template('home.html', categories = categories, latestItems = latestItems, login_session = login_session)

#shows all items in a specific category
@app.route('/catalog/<string:categoryName>/items')
def showCategory(categoryName):
    category = session.query(Category).filter_by(name = categoryName).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    categories = session.query(Category).all()
    return render_template('categoryItems.html', categories = categories, category = category, items = items, login_session = login_session)

#creates new item
@app.route('/catalog/<string:categoryName>/items/new', methods = ['GET', 'POST'])
def newItem(categoryName):
    #make sure user has permission to edit item
    if 'username' not in login_session:
        return redirect(url_for('login'))

    #create item if post request is received
    if request.method == 'POST':
        category = session.query(Category).filter_by(name = request.form['category']).one()
        user =  session.query(User).filter_by(email = login_session['email']).one()
        newItem = Item(name = request.form['name'], description = request.form['description'], category = category, user = user)
        session.add(newItem)
        session.commit()
        flash("New item has been added!")
        #redirect to the category where the item has been added
        return redirect(url_for('homepage'))

    return render_template('newItem.html', category = categoryName)

#shows description of specific item
@app.route('/catalog/<string:category>/<string:itemName>')
def showItem(itemName, category):
    category = session.query(Category).filter_by(name = category).first()
    item = session.query(Item).filter_by(name = itemName, category = category).first()
    return render_template('item.html', item = item, login_session = login_session)

@app.route('/catalog/<string:categoryName>/<string:itemName>/edit', methods = ['GET', 'POST'])
def editItem(itemName, categoryName):
    category = session.query(Category).filter_by(name = categoryName).first()
    item = session.query(Item).filter_by(name = itemName, category = category).first()
    #make sure user has permission to edit item
    if 'username' not in login_session:
        return redirect(url_for('login'))

    #check if user owns Items
    print(login_session['email'])
    print(item.user.email)
    if item.user.email != login_session['email']:
        flash("you must own this item to edit it")
        return redirect(url_for('homepage'))

    #edit item to knew name if function receives a post request
    if request.method == 'POST':
        item.name = request.form['name']
        session.add(item)
        session.commit()
        flash("%s's name has been changed to %s!" % (itemName, item.name))
        return redirect(url_for('homepage'))
    return render_template('editItem.html', itemName = itemName, category = category)

@app.route('/catalog/<string:category>/<string:itemName>/delete', methods = ['GET', 'POST'])
def deleteItem(itemName, category):
    category = session.query(Category).filter_by(name = category).first()
    item = session.query(Item).filter_by(name = itemName, category = category).first()
    #make sure user has permission to delete item
    if 'username' not in login_session:
        return redirect(url_for('login'))

    #check if user owns items
    if item.user.email != login_session['email']:
        flash("you must own this item to edit it")
        return redirect(url_for('homepage'))

    #delete item if function receives a POST request
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("%s has been deleted!" % itemName)
        return redirect(url_for('homepage'))
    return render_template('deleteItem.html', item= item)

#webpage that provides a list of all the items and information about them in JSON format
@app.route('/catalog/<string:categoryName>/<string:itemName>/json')
def catalogItemsJSON(categoryName, itemName):
    category = session.query(Category).filter_by(name = categoryName).one()
    item = session.query(Item).filter_by(name = itemName).all()
    categories = session.query(Category).all()
    return jsonify(Item=[i.serialize for i in item])

#webpage that allows user to login/create an account
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE = state)

#logs user in using their google account
@app.route("/gconnect", methods = ['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('clientSecrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    if data.get('error') != None:
        response = make_response(json.dumps('Unable to get user data'), 400)
        response.headers['Content-Type'] = 'application/json'
    print(data)
    if data.get('name') != None:
        login_session['username'] = data['name']
    else:
        login_session['username'] = data['email']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #see if user exists, if not, make a new one
    if getUserID(login_session['email']) == None:
        createUser(login_session)
    userID = getUserID(login_session['email'])
    flash("now logged in as %s" % login_session['username'])
    print("done!")
    return "User logged in"

#logs out user from the webpage
@app.route("/gdisconnect")
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You have now been logged out")
        return redirect(url_for('homepage'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

def getUserInfo(userID):
    user = session.query(User).filter_by(id = userID).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

if __name__ == "__main__":
    app.secret_key = "yx8MMTdStReWaWu0r1jQHQ1N"
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
