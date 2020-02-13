import requests


def ClarifaiResults(image_URL, pin_description="", c_model=None):
    """Get list of concepts from Clarifai *combined with Pinterest description; returns LIST of concepts"""
    unused = ['all', 'cool', 'is', 'relax', 'are', 'relaxed']
    if len(pin_description) > 0:
        c_concepts = pin_description.split()
        c_concepts = c_concepts[:2]  # no more than 4 keywords from pinterest

    else:
        c_concepts = []

    c_response = c_model.predict_by_url(url=image_URL)
    concepts = c_response['outputs'][0]['data']['concepts']

    # concept_sort = sorted(concepts, key=lambda k: k['value'])


    top_concept = [x['name'].split() for x in concepts[:2]] # find max top concepts to put into search query
    flatten = lambda x: [item for sublist in x for item in sublist]
    c_concepts += flatten(top_concept)
    print("Top concepts: ", c_concepts)

    new_concept_list = []  # remove duplicates & clean the concepts list
    for word in c_concepts:
        word = word.replace("'s", '')
        word = word.strip('|-=&#~+/,0123456789.')

        import re
        word = re.sub(r'(@\w*)|(`\w*)', "", word)
        # word = word.split(" ")
        word = word.lower()
        if word not in new_concept_list and len(word)>=2 and word not in unused:  # remove unneccessary spaces after the strip
            new_concept_list.append(word)

    if len(new_concept_list) > 6:  # make sure total search list not greater than 6 keywords
        new_concept_list = new_concept_list[:6]

    return new_concept_list


def check_clothing_type(clarifai_concepts):
    """Identify concepts in clarifai concepts to grab user size for appropriate clothing piece"""
    """[u'Romper', u'Midi Skirt', u'Blouse', u'Sarong', u'Kimonos', u'Skirt', u'Tunic',
     u'Knee Length Skirt', u'Kimono', u"Women's Shorts", u'Tube Top', u'Cardigan', 
     u'Maxi Skirt', u'Cocktail Dress', u'Dress', u'Halter Top', u"Women's Scarf", u'Jumpsuit']"""
    top_concepts = {'kimonos', 'cardigan', 'jumpsuit', 'dress', 'short', 'top'}
    pant_concepts = {'jeans', 'pants', 'shorts', 'slacks', 'capris', 'trousers', 'skirt'}
    shoe_concepts = {'shoe', 'boot', 'bootie', 'sneaker', 'slipper', 'heel', 'sandals', 'moccasin', 'toe', 'loafers',
                     'flats', 'oxford', 'platform', 'pumps'}


    commonwith1 = list(set(clarifai_concepts).intersection(top_concepts))
    if len(commonwith1) > 1:
        clarifai_concepts.remove(commonwith1[-1])

    commonwith2 = list(set(clarifai_concepts).intersection(pant_concepts))
    if len(commonwith2) > 1:
        clarifai_concepts.remove(commonwith2[0])


    # a =1
    # if len(common) > 0:
    #     #     clarifai_concepts.remove([x for x in common])

    for concept in clarifai_concepts:
        if concept in pant_concepts or (concept + 's') in pant_concepts:
            print('pant')
            return 'pant'
        elif concept in shoe_concepts or (concept + 's') in shoe_concepts:
            print('shoe')
            return 'shoe'

    print('top')
    return 'top'


def subtract(a, b):
    """Grab the brand name from Shopstyle by subtracting brandedName from unbrandedName"""
    return "".join(a.rsplit(b)).strip()


def ShopStyleResults(c_concepts, c_color='',
                     size=''):  # make sure to include size too
    """Construct ShopStyle API request using concepts extrated from Clarifai & Pinterest"""

    concept_set = set(c_concepts)  # change into set, remove duplicates even if coming from color
    concept_set.add(c_color)

    print("***SHOPSTYLE CONCEPT_SET FIRST PRINT ***")

    # api_request_str = "http://api.shopstyle.com/api/v2/products?pid=uid2384-40566372-99&offset=0&limit=20&sort=Popular&fts="
    api_request_str = "http://api.shopstyle.com/api/v2/products?pid=uid2384-40566372-99&offset=0&limit=30&sort=Popular&fts="
    for concept in concept_set:
        if concept != '':
            api_request_str += concept + '+'  # append all keywords to end of URL

    api_request_str += size.__str__()  # append size to end of the list

    print('Api request: ',api_request_str)  # debugging

    shop_request = requests.get(api_request_str)
    shop_data = shop_request.json()

    total_list = []
    for prop in shop_data["products"]:  # create the shop dictionary here
        shop_dict = {}

        shop_dict["id"] = prop["id"]
        shop_dict["name"] = prop["name"]
        shop_dict["priceLabel"] = prop["priceLabel"]
        shop_dict["price"] = prop["price"]
        shop_dict["image_url"] = prop["image"]["sizes"]["Best"]["url"]
        shop_dict["url"] = prop["clickUrl"]
        shop_dict["brand"] = subtract(prop["brandedName"], prop["unbrandedName"])  # call subtract function
        # if prop["brand"]:
        #     shop_dict["brand"] = prop["brand"]["name"]
        # else:
        #     shop_dict["brand"] = ""
        total_list.append(shop_dict)

    # import pdb; pdb.set_trace()

    return total_list  # returns list of dictionaries associated with shopstyle item


def ShopStyle_Retry(c_concepts, c_color, size):
    """Implement retry logic in case shopstyle doesn't return any results with initial query"""
    results = ShopStyleResults(c_concepts, c_color, size)  # results will be a list of dictionaries; if populated
    # print(results)
    retry_count = 0
    original_length = len(c_concepts)
    while len(results) == 0 and (retry_count <= (original_length + 2)):  # len(c_concepts): # if API returns 0
        if retry_count == 0:
            results = ShopStyleResults(c_concepts, c_color, size)
            retry_count += 1
            print(retry_count)
        elif retry_count == 1:
            results = ShopStyleResults(c_concepts, c_color)
            retry_count += 1
            print(retry_count)
        elif retry_count > 1:
            c_concepts = c_concepts[0:-1]  # splice off last word each time
            print(c_concepts)
            results = ShopStyleResults(c_concepts)
            retry_count += 1
            print(retry_count)

    return results


def ClarifaiColor(image_URL, color_model=None):
    """function to get 2nd maximum color name from Clarifai color model, as a string"""
    color_response = color_model.predict_by_url(url=image_URL)
    color_concepts = color_response['outputs'][0]['data']['colors']

    concept_sort = sorted(color_concepts, key=lambda k: k['value'])

    color_name = concept_sort[-1]['w3c']['name']  # take 2nd largest color value; index in to get the name

    for i in range(len(color_name) - 1, -1, -1):
        if color_name[i].isupper():  # if letter is uppercase
            last_upper_index = i
            break

    short_color = color_name[last_upper_index:].lower()

    return short_color  # returns a string of the short name of the color


def get_fashion_pins():
    """Make request to Pinterest to get my pins specifically; process to get to fields I need. Returns list of dictionaries"""
    r = requests.get(
        "https://api.pinterest.com/v3/pidgets/boards/melodychuchu/fashion/pins/")  # get my pins from fashion board
    melody_pins = r.json()

    pin_list = []  #

    for pin in melody_pins["data"][
        "pins"]:  # data is a list of dictionaries; each pin is a dictionary containinin all info about pin
        pin_dict = {}  # each pin will be individual dictionary
        pin_dict["id"] = pin["id"]
        pin_dict["description"] = pin["description"]
        pin_dict["dominant_color"] = pin["dominant_color"]
        pin_dict["link"] = pin["link"]
        pin_dict["image"] = pin["images"]["237x"]["url"]
        pin_list.append(pin_dict)  # append created filtered dictionaries into list

    return pin_list  # will change to return


def get_user_pins_no_board(p_username):  # may need to get pinterest username from DB. need to do board name conversion
    """Make request ot Pinterest to get **user** pins with provided board; process to get fields. Returns list of dictionaries where e/ dict is pin obejct"""
    pin_request_str = "https://api.pinterest.com/v3/pidgets/users/" + str(
        p_username) + "/pins/"  # get pins from fashion board
    r = requests.get(pin_request_str)
    user_pins = r.json()

    pin_list = []  # list of all pin dictionaries

    for pin in user_pins["data"][
        "pins"]:  # data is a list of dictionaries; each pin is a dictionary containinin all info about pin
        pin_dict = {}  # each pin will be individual dictionary
        pin_dict["id"] = pin["id"]
        pin_dict["description"] = pin["description"]
        pin_dict["dominant_color"] = pin["dominant_color"]
        pin_dict["link"] = pin["link"]
        pin_dict["image"] = pin["images"]["237x"]["url"]
        pin_list.append(pin_dict)  # append created filtered dictionaries into list

    return pin_list  # will change to return


def get_user_pins_given_board(p_username,
                              board):
    """Make request ot Pinterest to get **user** pins with provided board; process to get fields. Returns list of dictionaries where e/ dict is pin obejct"""
    board = board.replace(' ', '-')  # replace spaces with dashes
    pin_request_str = "https://api.pinterest.com/v3/pidgets/boards/" + str(p_username) + "/" + str(
        board) + "/pins/"  # get pins from fashion board
    r = requests.get(pin_request_str)
    user_pins = r.json()

    pin_list = []  # list of all pin dictionaries

    for pin in user_pins["data"][
        "pins"]:  # data is a list of dictionaries; each pin is a dictionary containing all info about pin
        pin_dict = {}  # each pin will be individual dictionary
        pin_dict["id"] = pin["id"]
        pin_dict["description"] = pin["description"]
        pin_dict["dominant_color"] = pin["dominant_color"]
        pin_dict["link"] = pin["link"]
        pin_dict["image"] = pin["images"]["237x"]["url"]
        pin_list.append(pin_dict)  # append created filtered dictionaries into list

    return pin_list  # will change to return


