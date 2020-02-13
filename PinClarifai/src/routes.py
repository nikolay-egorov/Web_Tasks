import json

import requests
from clarifai.rest import ClarifaiApp
from flask import Flask, session, redirect, render_template, request, flash, url_for, jsonify, Blueprint

from src.model.model import User, db, ItemResult, Bookmark
from src.util import get_fashion_pins, get_user_pins_given_board, get_user_pins_no_board, ClarifaiResults, ClarifaiColor, \
    check_clothing_type, ShopStyle_Retry

c_app = ClarifaiApp(api_key='ee241c88e4b945d3847e8ae8139a8bcf')
c_model = c_app.models.get(model_id="e0be3b9d6a454f0493ac3a30784001ff")
color_model = c_app.models.get(model_id="eeed0b6733a644cea07cf4c60f87ebb7")


main_route = Blueprint('route', __name__, template_folder='/templates')



@main_route.route('/', methods=['GET'])
def get_homepage():
    """Show homepage for non-logged in users. Only show for users who are logged out/do not have account"""
    if session.get("user_id"):
        return redirect("/search")
    else:
        return render_template("homepage.html")


@main_route.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("registration.html")


@main_route.route('/register', methods=['POST'])
def register_user():
    """Process registration."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"].encode('utf-8')
    pinterest_token = request.form["pin-username"]
    age = request.form["age"]
    if (age != ''):
        age = int(age)
    gender = request.form["gender"]
    size = request.form["size"]
    pant_size = request.form["pant_size"] # Convert to US
    if (pant_size != ''):
        pant_size = int(request.form.get("pant_size")) - 10

    shoe_size = request.form["shoe_size"]
    if (shoe_size != ''):
        shoe_size = float(request.form["shoe_size"])-32 # Convert to US

    from app import bcrypt
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')  # encrypting
    new_user = User(email=email, password=pw_hash, pinterest_token=pinterest_token, age=age, gender=gender, size=size,
                    pant_size=pant_size, shoe_size=shoe_size)

    user = User.query.filter_by(email=email).first()
    if user:
        flash("User already exists")
        return redirect("/login")
    db.session.add(new_user)  # specific to the DB session not flask session - to confirm
    db.session.commit()

    session["user_id"] = User.query.filter_by(
        email=new_user.email).first().user_id  # make sure user gets into session once they register
    session["pin_username"] = User.query.filter_by(email=new_user.email).first().pinterest_token

    flash("User {} added.".format(email))
    return redirect("/search")


@main_route.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login.html")


@main_route.route('/login', methods=['POST'])
def login_process():
    """Process login"""

    email = request.form["email"]
    password = request.form["password"].encode('utf-8')

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Oops! Please log in!")
        return redirect("/login")

    print(password)

    print(user.password)
    # password.encode("utf-8")
    from app import bcrypt

    try:
        bcrypt.check_password_hash(user.password, password)
    except:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id  # session ID will be BIG
    session["pin_username"] = user.pinterest_token
    session["gender"] = user.gender
    print(session["gender"])
    flash("Logged in")
    return redirect("/search".format(user.user_id))


@main_route.route('/logout')
def logout():
    """Log out user."""

    del session["user_id"]

    del session["pin_username"]

    if session.get("board"):
        del session["board"]

    del session["gender"]
    flash("Logged Out.")
    return redirect("/")


@main_route.route('/search', methods=['GET', 'POST'])
def user_search():
    if request.method == 'GET':
        # regardless of whether orn ot there is user in session, give option to select size
        if session.get("user_id"):  # if there is a user in the session
            user_id = session.get("user_id")
            user = User.query.filter_by(user_id=user_id).first()  # create user object

            if not session.get("pin_username"):  # if user has not provided a pinterest username
                fashion_pins = get_fashion_pins()  # this is a list of dicts;

                return render_template("search.html", fashion_pins=fashion_pins, user=user)
            if session.get("pin_username"):  # if user has pin username
                try:
                    board = request.args.get("board-name")
                    if not board:  # if no board inputted in form
                        board = session.get('board')
                        user_pins = get_user_pins_given_board(session["pin_username"], board)
                    else:  # if a board IS indeed inputted in form
                        session['board'] = board  # add board into session dictionary
                        user_pins = get_user_pins_given_board(session["pin_username"], board)


                except:
                    user_pins = get_user_pins_no_board(session["pin_username"])  # pulls all pins for that user

                return render_template("search.html", fashion_pins=user_pins,
                                       user=user)

        else:  # if no user ID in session
            fashion_pins = get_fashion_pins()
            return render_template("search.html", fashion_pins=fashion_pins)

    if request.method == 'POST':
        # try:
        imageURL = request.form.get('image_URL')  # get image URL from the form
        pin_description = request.form.get("image_desc")
        json.dumps(pin_description)

        clarifai_concepts = None

        try:
            clarifai_concepts = ClarifaiResults(imageURL,
                                                pin_description,
                                                c_model)  # put pin_description in once it works; currently returns none
            print(clarifai_concepts)
        except:
            print("Clarifai API failed to return concept results")
            flash("Clarifai API failed to return concept results")
        try:
            clarifai_color = ClarifaiColor(
                imageURL, color_model)  # pass in imageURL to clarifai color model; get string of color name back
            print(clarifai_color)
        except:
            print("Clarifai API failed to return color result")
            flash("Clarifai API failed to return color result")
        if clarifai_concepts is not None and clarifai_color is not None:  # if there is a concept list returned; pass those to the function

            user_size = request.form.get("size")  # grab elemnts from the search html form
            user_pant_size = request.form.get("pant_size")
            if (user_pant_size != ''):
                user_pant_size = int(request.form.get("pant_size")) - 10
            user_shoe_size = request.form.get("shoe_size")
            if (user_shoe_size != ''):
                user_shoe_size = float(user_shoe_size) - 32
            clothing_type = check_clothing_type(clarifai_concepts)  # pass in clarifai concepts to check the type

            if clothing_type == "pant":
                size = user_pant_size
            elif clothing_type == "shoe":
                size = user_shoe_size
            else:
                size = user_size

            gender = request.form.get("gender_choice")

            if gender == "Male":
                if "man" or "men" not in clarifai_concepts:
                    clarifai_concepts.insert(0, 'man')
            else:
                if "woman" or "women" not in clarifai_concepts:
                    clarifai_concepts.insert(0, 'woman')

            try:
                shop_data = ShopStyle_Retry(clarifai_concepts, clarifai_color, size)
                print("*****SHOP DATA RETRY RESULTS HERE ******************")
                # print shop_data
                print(shop_data)  # data is a list
                return redirect(url_for('route.show_results', results=json.dumps(shop_data)))

            except:
                print("Shopstyle API failed to return results")
                flash("ShopStyle API failed to return results")
        else:
            print("Nothing returned any")
            return redirect('/search')
    else:
        print("No process could happen! SadFace :( ")
        return redirect('/search')


@main_route.route('/results', methods=['GET'])  # 'make GET & POST conditional'
def show_results():
    """display search results on the results page"""

    results = json.loads(request.args.get('results'))  # changes to list of dicts

    brand_set = set()  # create a set for brands; take out blank brands and remove duplicates
    for result in results:
        if result["brand"]:  # include blanks in set
            brand_set.add(result["brand"])
    print(brand_set)

    # import pdb; pdb.set_trace()

    return render_template("results.html", results=results, enumerate=enumerate,
                           brand_set=brand_set)


@main_route.route('/get-item-info', methods=['GET'])
def get_info():
    """Uses listing ID of saved Item to make API call to get the rest of Item info"""
    listing_info = request.args.get('listing_data')  # get listing data from ID
    # print listing_info
    request_str = 'http://api.shopstyle.com/api/v2/products/' + str(listing_info) + '?pid=uid2384-40566372-99'
    # print request_str
    shop_api_data = requests.get(request_str)  # not sure if redundant
    shop_api_data = shop_api_data.json()

    return jsonify(shop_api_data)  # ['results'][0])


@main_route.route('/add-bookmark.json', methods=['POST'])
def save_result():
    """handle users saving bookmark result, with JSON data from get-item-info route"""
    # print request
    listing_data = request.get_json()

    print(type(listing_data))  # should be string; it is type UNICODE

    shop_id = listing_data['id']

    # Check if listing already in DB?
    listing = ItemResult.query.filter(ItemResult.item_listing_id == shop_id).first()

    # if listing it's not there in ItemResult, create it!
    if not listing:
        listing = ItemResult(item_listing_id=listing_data["id"],
                             listing_title=listing_data["name"],
                             listing_url=listing_data["clickUrl"],
                             listing_image=listing_data["image"]["sizes"]["Best"]["url"],
                             listing_price=listing_data["price"])  # check this
        # listing_brand=listing_data["brand"]["name"]) # not going to use price $ label here; #
        db.session.add(listing)
        db.session.commit()


    bookmark = Bookmark.query.filter(Bookmark.item_listing_id == shop_id).first()
    if not bookmark:
        bookmark = Bookmark(item_listing_id=listing.item_listing_id,
                            user_id=session["user_id"])
        db.session.add(bookmark)
        db.session.commit()


    return redirect('/bookmarks')  # what does the viewfunction actually return here


@main_route.route('/delete-bookmark.json', methods=['POST'])
def delete_result():
    listing_data = request.get_json()

    print(type(listing_data))  # should be string; it is type UNICODE

    shop_id = listing_data['id']


    ItemResult.query.filter(ItemResult.item_listing_id == shop_id).delete()
    Bookmark.query.filter(Bookmark.item_listing_id == shop_id).delete()

    db.session.commit()
    return redirect('/bookmarks')

@main_route.route('/bookmarks', methods=['GET'])
def view_bookmarks():
    """display the search results that the user has saved"""
    user_id = session.get('user_id')  # grab user ID from session
    user_bookmarks = Bookmark.query.filter_by(user_id=user_id).all()  # get all bookmarks for 1 user
    # print user_bookmarks

    listing_list = []  # dictionary of listings, with listing_ID as key and other attributes like price as values
    for item in user_bookmarks:
        item_id = item.item_listing_id
        listing_list.append(
            ItemResult.query.filter_by(item_listing_id=item_id).first())  # put each full object into lilsting_list

    return render_template('bookmarks.html', listing_list=listing_list)  # pass list of objects to jinja
