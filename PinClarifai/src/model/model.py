"""Models and database functions """

from flask_sqlalchemy import SQLAlchemy 



db = SQLAlchemy()


# Model definitions

class User(db.Model):
    """User of PinStyle app; pin token is a pin username"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer,
                        # autoincrement=True,
                        db.Sequence("users_user_id_seq"),
                        primary_key=True)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False) #PW hashed
    gender = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True) # can consider storing as strings
    size = db.Column(db.String(64), nullable=True) #selector for XS, small, medium, large
    pant_size = db.Column(db.Integer, nullable=True) #in inches; may be an extra column
    shoe_size = db.Column(db.Float, nullable=True) #US shoe sizes
    pinterest_token = db.Column(db.String(100), nullable=True) #REPURPOSE to be pinterest username

    bookmarks = db.relationship('Bookmark') #relationship to bookmark

  
    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id={} email={}>".format(self.user_id,
                                               self.email)



class Bookmark(db.Model): #rename to bookmarks intermediary table / association
    """Table of all user *saved* listings returned by ShopStyle"""

    __tablename__ = "bookmarks"

    bookmark_id = db.Column(db.Integer,
                          # autoincrement=True,
                            db.Sequence("bookmarks_bookmark_id_seq"),
                          primary_key=True)
    user_id = db.Column(db.Integer,
                         db.ForeignKey('users.user_id'))
   
    item_listing_id = db.Column(db.Integer, db.ForeignKey('itemresults.item_listing_id'), nullable=False) #list of listings saved

    user = db.relationship('User')
    itemresult = db.relationship('ItemResult')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Bookmark bookmark_id={} item_listing_id={}".format(self.bookmark_id,
                                                                    self.item_listing_id)

class ItemResult(db.Model):
    """Table of all Items saved; will not have duplicate listings/items"""

    __tablename__ = "itemresults"

    item_listing_id = db.Column(db.Integer, primary_key=True) #SHOPSTyle provides unique primary keys
    db.ForeignKey('bookmarks.item_listing_id')

    listing_title = db.Column(db.String(2000), nullable=False)

    listing_url = db.Column(db.String(2000), nullable=False)
    listing_image = db.Column(db.String(2000), nullable=False) #image URL of image
    listing_price = db.Column(db.Float, nullable=True)
    listing_brand = db.Column(db.String(2000), nullable=True)


    bookmarks = db.relationship('Bookmark') 

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Item item_listing_id={} listing_title={}".format(self.item_listing_id, self.listing_title)


def example_data():
    """Create some sample data."""

    # In case this is run more than once, empty out existing data
    #User.query.delete()

    ann = User(email='ann@test.com', password='123', gender='Female', age=25, size='Small', pant_size=36, shoe_size=38)
    bo = User(email='bo@test.com', password='456', gender='Female', age=20, size='Medium', pant_size=28, shoe_size=37, pinterest_token='booboo')


    db.session.add_all([ann,bo])
    db.session.commit()


# Helper functions

def connect_to_db(app ):
    """Connect the database to our Flask app."""

    # Configure to PostgreSQL database
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///pintest'
    from src.config import config
    conf = config()
    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=conf['user'], pw=conf['password'], url=conf['host'],
                                                                   db=conf['database'])

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":

    from app import app
    connect_to_db(app)

    print("Connected to DB.")
