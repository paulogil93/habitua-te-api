from app import db

class User(db.Model):
    __tablename__ = "users"

    ############# Table fields #############

    id = db .Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    profile_pic = db.Column(db.Text)
    api_key = db.Column(db.Text, unique=True, nullable=False)
    start_date = db.Column(db.Date)

    ############# Relationships #############

    events = db.relationship("Event", secondary="likes")

    ############# Methods #############

    def __init__(self, name, email, profile_pic, api_key, start_date):
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.api_key = api_key
        self.start_date = start_date
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    @staticmethod
    def get_all():
        return User.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '{id:'+str(self.id)+', name:'+self.name+' , email:'+self.email+', joined:'+self.start_date+', profile_pic:'+self.profile_pic+'}'

class Event(db.Model):
    __tablename__ = "events"

    ############# Table fields #############

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    picture = db.Column(db.Text)
    event_type = db.Column(db.String(20), nullable=False)

    ############# Relationships #############

    users = db.relationship("User", secondary="likes")

    ############# Methods #############

    def __init__(self, title, description, date, time, picture, event_type):
        self.title = title
        self.description = description
        self.date = date
        self.time = time
        self.picture = picture
        self.event_type = event_type

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Event.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    def __repr__(self):
        return '<Event: {}>'.format(self.title)

class Product(db.Model):
    __tablename__ = "products"

    ############# Table fields #############

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete="CASCADE"))
    name = db.Column(db.String(50), unique=True, nullable=False)
    proof = db.Column(db.Numeric(4,2))
    country = db.Column(db.String(25))
    description = db.Column(db.Text, nullable=False)
    picture = db.Column(db.Text)
    available = db.Column(db.Boolean, server_default='t', default=True)
    price = db.Column(db.Numeric(3,2), nullable=False)

    ############# Relationship #############

    category = db.relationship("Category", backref=db.backref("products", cascade="all, delete-orphan"))

    ############# Methods #############

    def __init__(self, name, description, category_id, proof, country, picture, available, price):
        self.name = name
        self.description = description
        self.category_id = category_id
        self.proof = proof
        self.country = country
        self.picture = picture
        self.available = available
        self.price = price
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Product.query.all()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '{id:'+str(self.id)+', name:'+str(self.name)+' , description:'+str(self.description)+', category_id:'+self.category_id+', proof:'+self.proof+', country:'+self.country+', picture:'+self.picture+', available:'+self.available+', price:'+self.price+'}'

class Category(db.Model):
    __tablename__ = "categories"

    ############# Table fields #############

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    url = db.Column(db.Text)

    ############# Methods #############

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Category.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Category {}>'.format(self.name)

class Like(db.Model):
    __tablename__ = "likes"

    ############# Table fields #############

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    ############# Relationship #############

    user = db.relationship("User", backref=db.backref("likes", cascade="all, delete-orphan"))
    event = db.relationship("Event", backref=db.backref("likes", cascade="all, delete-orphan"))

    ############# Methods #############

    def __init__(self, user_id, event_id):
        self.user_id = user_id
        self.event_id = event_id
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Like.query.all()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<Likes {}>'.format(self.body)

class Attend(db.Model):
    __tablename__ = "attends"

    ############# Table fields #############

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    will_go = db.Column(db.String(15))

    ############# Relationship #############

    user = db.relationship("User", backref=db.backref("attends", cascade="all, delete-orphan"))
    event = db.relationship("Event", backref=db.backref("attends", cascade="all, delete-orphan"))

    ############# Methods #############

    def __init__(self, user_id, event_id, will_go):
        self.user_id = user_id
        self.event_id = event_id
        self.will_go = will_go

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Attend.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        return '{id:'+str(self.id)+', user_id:'+str(self.user_id)+' , event_id:'+str(self.event_id)+', will_go:'+self.will_go+'}'

class Favourite(db.Model):
    __tablename__ = 'favourites'

    ############# Table fields #############

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

    ############# Relationship #############

    user = db.relationship("User", backref=db.backref("favourites", cascade="all, delete-orphan"))
    product = db.relationship("Product", backref=db.backref("favourites", cascade="all, delete-orphan"))

    ############# Methods #############

    def __init__(self, user_id, product_id):
        self.user_id = user_id
        self.product_id = product_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Favourite.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '{id:'+str(self.id)+', user_id:'+self.user_id+' , product_id:'+self.product_id+'}'

class ApiKey(db.Model):
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text, unique=True, nullable=False)

    def __init__(self, key):
        self.key = key

    @staticmethod
    def get_all():
        return ApiKey.query.all()

    def __repr__(self):
        return 'Key {}>'.format(self.key)