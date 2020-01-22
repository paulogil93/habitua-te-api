from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort
from functools import wraps
from sqlalchemy import desc, asc, func
from datetime import date, datetime
from dateutil import parser
from operator import itemgetter
import hashlib
import json

# Local import
from instance.config import app_config

# Initializes SQLAlchemy
db = SQLAlchemy()

def create_app(config_name):
    # Prevents circular imports
    from app.models import User, Event, Product, Category, Like, Attend, ApiKey, Favourite

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    ####################################
    #      Authorization decorator     #
    ####################################

    def require_api_key(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            users = User.get_all()
            for user in users:
                if request.headers.get('X-Api-Key') and user.api_key == request.headers.get('X-Api-Key'):
                    return view_function(*args, **kwargs)
            keys = ApiKey.get_all()
            for api_key in keys:
                if request.headers.get('X-Api-Key') and api_key.key == request.headers.get('X-Api-Key'):
                    return view_function(*args, **kwargs)
            abort(401)
        return decorated_function

    def require_admin_key(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            keys = ApiKey.get_all()
            for api_key in keys:
                if request.headers.get('X-Api-Key') and api_key.key == request.headers.get('X-Api-Key'):
                    return view_function(*args, **kwargs)
            abort(401)
        return decorated_function

    ####################################
    #      User related endpoints      #
    ####################################

    @app.route('/api/v1/users/', methods=['GET'])
    @require_api_key
    def get_users():
        if request.method == 'GET':  # GET method
            users = User.get_all()
            results = []

            for user in users:
                obj = {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'profile_pic': user.profile_pic,
                    'start_date': convertDate(str(user.start_date)),
                    'api_key': user.api_key
                }
                results.append(obj)

            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/users/', methods=['POST'])
    @require_api_key
    def post_users():
        if request.method == 'POST':  # POST method
            
            users = User.get_all()
            name = request.args.get('name')
            email = request.args.get('email')
            profile_pic = request.args.get('profile_pic')

            for user in users:
                if user.email == email:
                    Response = jsonify({
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'profile_pic': user.profile_pic,
                        'start_date': convertDate(str(user.start_date))
                    })
                    Response.status_code = 200
                    return Response

            if name and email:
                user = User(name=name, email=email, profile_pic=profile_pic, api_key=generate_api_key(email), start_date=date.today())
                user.save()

                Response = jsonify({
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'profile_pic': profile_pic,
                    'start_date': convertDate(str(user.start_date))
                })
                Response.status_code = 201
                return Response
            else:
                # Raise an HTTPException with a 400 bad request status code
                abort(400)

    @app.route('/api/v1/users/<int:id>/', methods=['GET'])
    @require_api_key
    def get_user_by_id(id, **kwargs):
        user = User.query.filter_by(id=id).first()
        if not user:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # GET Method
        if request.method == 'GET':
            Response = jsonify({
                'id' : user.id,
                'name' : user.name,
                'email' : user.email,
                'profile_pic' : user.profile_pic,
                'start_date': convertDate(str(user.start_date))
            })
            Response.status_code = 200
            return Response

    @app.route('/api/v1/users/<int:id>/', methods=['PUT', 'DELETE'])
    @require_admin_key
    def user_manipulation(id, **kwargs):
        user = User.query.filter_by(id=id).first()

        if not user:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        # DELETE Method
        if request.method == 'DELETE':
            user.delete()
            return {
                'message' : "User {} deleted successfully.".format(user.id)
            }
        # PUT Method
        elif request.method == 'PUT':
            name = request.values.get('name')
            email = request.values.get('email')
            profile_pic = request.values.get('profile_pic')

            if name is not None:
                user.name = name
            if email is not None:
                user.email = email
            if profile_pic is not None:
                user.profile_pic = profile_pic
            user.save()

            response = jsonify({
                'id' : user.id,
                'name' : user.name,
                'email' : user.email,
                'profile_pic' : user.profile_pic,
                'start_date': convertDate(str(user.start_date))
            })
            response.status_code = 200
            return response
    
    ####################################
    #      Event related endpoints     #
    ####################################

    @app.route('/api/v1/events/', methods=['GET'])
    @require_admin_key
    def get_events():
        if request.method == 'GET': # GET method
            events = Event.get_all()
            results = []

            for event in events:
                obj = {
                    'id': event.id,
                    'title': event.title,
                    'description': event.description,
                    'date': str(event.date),
                    'time': str(event.time),
                    'picture': event.picture,
                    'event_type': event.event_type
                }
                results.append(obj)

            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/events/news/', methods=['GET'])
    @require_api_key
    def get_news():
        if request.method == 'GET': # GET method
            events = Event.query.filter_by(event_type='news').order_by(Event.date.desc())
            results = []

            for event in events:
                obj = {
                    'id': event.id,
                    'title' : event.title,
                    'description' : event.description,
                    'date' : str(event.date),
                    'time': str(event.time),
                    'picture' : event.picture,
                    'event_type': event.event_type
                }
                results.append(obj)

            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/events/event/', methods=['GET'])
    @require_api_key
    def get_filtered_events():
        if request.method == 'GET': # GET method
            events = Event.query.filter_by(event_type='event').order_by(Event.date.asc())
            results = []

            for event in events:
                present = datetime.now().date()

                obj = {
                    'id': event.id,
                    'title' : event.title,
                    'description' : event.description,
                    'date' : str(event.date),
                    'time': str(event.time),
                    'picture' : event.picture,
                    'event_type': event.event_type
                }
                
                if present < event.date:
                    results.append(obj)

            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/events/event/all/', methods=['GET'])
    @require_api_key
    def get_all_events():
        if request.method == 'GET': # GET method
            events = Event.query.filter_by(event_type='event').order_by(Event.date.desc())
            results = []

            for event in events:
                obj = {
                    'id': event.id,
                    'title' : event.title,
                    'description' : event.description,
                    'date' : str(event.date),
                    'time': str(event.time),
                    'picture' : event.picture,
                    'event_type': event.event_type
                }
                results.append(obj)

            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/events/', methods=['POST'])
    @require_admin_key
    def post_events():
        if request.method == 'POST': # POST method
            title = request.values.get('title')
            description = request.values.get('description')
            date = request.values.get('date')
            time = request.values.get('time')
            picture = request.values.get('picture')
            event_type = request.values.get('event_type')

            if title and description:
                event = Event(title=title, description=description, date=date, time=time, picture=picture, event_type=event_type)
                event.save()

                Response = jsonify({
                    'title' : event.title,
                    'description' : event.description,
                    'date' : str(event.date),
                    'time': str(event.time),
                    'picture' : event.picture,
                    'event_type': event.event_type
                })

                Response.status_code = 201
                return Response
            else:
                abort(400) # Raise an HTTPException with a 400 bad request status code

    @app.route('/api/v1/events/<int:id>/', methods=['GET'])
    @require_api_key
    def get_event_by_id(id, **kwargs):
        event = Event.query.filter_by(id=id).first()
        if not event:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # GET method
        if request.method == 'GET':
            Response = jsonify({
                'title' : event.title,
                'description' : event.description,
                'date' : event.date,
                'time': event.time,
                'picture' : event.picture,
                'event_type': event.event_type
            })

            Response.status_code = 200
            return Response

    @app.route('/api/v1/events/<int:id>/', methods=['PUT', 'DELETE'])
    @require_admin_key
    def event_manipulation(id, **kwargs):
        event = Event.query.filter_by(id=id).first()
        if not event:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # DELETE method
        if request.method == 'DELETE':
            event.delete()
            return {
                'message' : "Event {} deleted successfully.".format(event.id)
            }
        # PUT method
        elif request.method == 'PUT':
            title = request.values.get('title')
            description = request.values.get('description')
            date = request.values.get('date')
            time = request.values.get('time')
            picture = request.values.get('picture')
            event_type = request.values.get('event_type')

            if title is not None:
                event.title = title
            if description is not None:
                event.description = description
            if date is not None:
                event.date = date
            if time is not None:
                event.time = time
            if picture is not None:
                event.picture = picture
            if event_type is not None:
                event.event_type = event_type
            
            event.save()

            Response = jsonify({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'date': str(event.date),
                'time': str(event.time),
                'picture': event.picture,
                'event_type': event.event_type
            })

            Response.status_code = 200
            return Response

    ####################################
    #     Product related endpoints    #
    ####################################

    @app.route('/api/v1/products/', methods=['GET'])
    @require_api_key
    def get_products():
        if request.method == 'GET': # GET method
            products = Product.get_all()
            results = []

            for product in products:
                obj = {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'category_id': product.category_id,
                    'proof': str(product.proof),
                    'country': product.country,
                    'available': product.available,
                    'price': str(product.price),
                    'picture': product.picture
                }
                results.append(obj)
            
            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/products/', methods=['POST'])
    @require_admin_key
    def post_products():
        if request.method == 'POST': # POST method
            name = request.values.get('name')
            description = request.values.get('description')
            category_id = request.values.get('category_id')
            proof = request.values.get('proof')
            country = request.values.get('country')
            available = (request.values.get('available') == 'True')
            price = request.values.get('price')
            picture = request.values.get('picture')

            if category_id and name and description and price:
                product = Product(
                    name=name,
                    description=description,
                    category_id=category_id,
                    proof=proof,
                    country=country,
                    picture=picture,
                    available=available,
                    price=price
                )
                product.save()

                Response = jsonify({
                    'id' : product.id,
                    'name' : product.name,
                    'description' : product.description,
                    'category_id' : product.category_id,
                    'proof' : str(product.proof),
                    'country' : product.country,
                    'available' : product.available,
                    'price' : str(product.price),
                    'picture' : product.picture
                })
                Response.status_code = 201
                return Response

    @app.route('/api/v1/products/<int:id>/', methods=['GET'])
    @require_api_key
    def get_product_by_id(id, **kwargs):
        product = Product.query.filter_by(id=id).first()
        if not product:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # GET method
        if request.method == 'GET':
            Response = jsonify({
                'id' : product.id,
                'name' : product.name,
                'description' : product.description,
                'category_id' : product.category_id,
                'proof' : str(product.proof),
                'country' : product.country,
                'available' : product.available,
                'price' : str(product.price),
                'picture' : product.picture
            })
            Response.status_code = 200
            return Response

    @app.route('/api/v1/products/<int:id>/', methods=['PUT', 'DELETE'])
    @require_admin_key
    def products_manipulation(id, **kwargs):
        product = Product.query.filter_by(id=id).first()
        if not product:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # DELETE method
        if request.method == 'DELETE':
            product.delete()
            return {
                'message' : "Product {} deleted successfully.".format(product.id)
            }
        # PUT method
        elif request.method == 'PUT':
            name = request.values.get('name')
            description = request.values.get('description')
            category_id = request.values.get('category_id')
            proof = request.values.get('proof')
            country = request.values.get('country')
            available = (request.values.get('available') == 'True')
            price = request.values.get('price')
            picture = request.values.get('picture')

            if name is not None:
                product.name = name
            if description is not None:
                product.description = description
            if category_id is not None:
                product.category_id = category_id
            if proof is not None:
                product.proof = proof
            if country is not None:
                product.country = country
            if available is not None:
                product.available = available
            if price is not None:
                product.price = price
            if picture is not None:
                product.picture = picture

            product.save()

            Response = jsonify({
                'id' : product.id,
                'name' : product.name,
                'description' : product.description,
                'category_id' : product.category_id,
                'proof' : str(product.proof),
                'country' : product.country,
                'available' : product.available,
                'price' : str(product.price),
                'picture' : product.picture
            })
            Response.status_code = 200
            return Response

    ####################################
    #    Category related endpoints    #
    ####################################

    @app.route('/api/v1/categories/', methods=['GET'])
    @require_api_key
    def get_categories():
        if request.method == 'GET': # GET method
            categories = Category.get_all()
            results = []

            for category in categories:
                obj = {
                    'id' : category.id,
                    'name' : category.name,
                    'url': category.url
                }
                results.append(obj)
            
            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/categories/', methods=['POST'])
    @require_admin_key
    def post_category():
        if request.method == 'POST': # POST method
            name = request.values.get('name')
            url = request.values.get('url')

            if name and url:
                category = Category(name=name, url=url)
                category.save()

                Response = jsonify({
                    'id' : category.id,
                    'name' : category.name,
                    'url': category.url
                })
                Response.status_code = 201
                return Response

    @app.route('/api/v1/categories/<int:id>/', methods=['GET'])
    @require_api_key
    def get_category_by_id(id, **kwargs):
        category = Category.query.filter_by(id=id).first()
        if not category:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # GET method
        if request.method == 'GET':
            Response = jsonify({
                'id' : category.id,
                'name' : category.name,
                'url': category.url
            })
            Response.status_code = 200
            return Response
        
    @app.route('/api/v1/categories/<int:id>/', methods=['PUT', 'DELETE'])
    @require_admin_key
    def categories_manipulation(id, **kwargs):
        category = Category.query.filter_by(id=id).first()
        if not category:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # DELETE method
        if request.method == 'DELETE':
            Category.delete(category)
            return {
                'message' : "Category {} deleted successfully.".format(category.id)
            }
        # PUT method
        elif request.method == 'PUT':
            name = request.values.get('name')
            url = request.values.get('url')

            if name is not None:
                category.name = name
            if url is not None:
                category.url = url
            category.save()

            Response = jsonify({
                'id': category.id,
                'name': category.name,
                'url': category.url
            })
            Response.status_code = 200
            return Response

    @app.route('/api/v1/products/category/<int:id>', methods=['GET'])
    @require_api_key
    def get_products_by_category(id, **kwargs):
        category = Category.query.filter_by(id=id).first()
        results = []
        if not category:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # GET method
        if request.method == 'GET':
            products = Product.query.filter_by(category=category)
            
            for product in products:
                obj = {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'category_id': product.category_id,
                    'proof': str(product.proof),
                    'country': product.country,
                    'available': product.available,
                    'price': str(product.price),
                    'picture': product.picture
                }
                results.append(obj)
            
            Response = jsonify(results)
            Response.status_code = 200
            return Response
            

    ####################################
    #      Like related endpoints      #
    ####################################

    @app.route('/api/v1/likes/', methods=['GET'])
    @require_api_key
    def get_likes():
        if request.method == 'GET': # GET method
            likes = Like.get_all()
            results = []

            for like in likes:
                obj = {
                    'id' : like.id,
                    'user_id' : like.user_id,
                    'event_id' : like.event_id
                }
                results.append(obj)

            Response = jsonify(results)
            Response.status_code = 200
            return Response
    
    @app.route('/api/v1/likes/', methods=['POST'])
    @require_api_key
    def post_likes():
        if request.method == 'POST': # POST method
            likes = Like.get_all()
            user_id = request.args.get('user_id')
            event_id = request.args.get('event_id')

            for like in likes:
                if like.user_id == user_id and like.event_id == event_id:
                    Response = jsonify({'message': 'Like already in db'})
                    Response.status_code = 200
                    return Response

            if user_id and event_id:
                like = Like(user_id=user_id, event_id=event_id)
                like.save()

                Response = jsonify({
                    'id' : like.id,
                    'user_id' : like.user_id,
                    'event_id' : like.event_id
                })
                Response.status_code = 201
                return Response
    
    @app.route('/api/v1/likes/<int:id>/', methods=['GET'])
    @require_api_key
    def get_like_by_id(id, **kwargs):
        like = Like.query.filter_by(id=id).first()
        if not like:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # GET method
        if request.method == 'GET':
            Response = jsonify({
                'id' : like.id,
                'user_id' : like.user_id,
                'event_id' : like.event_id
            })
            Response.status_code = 200
            return Response
    
    @app.route('/api/v1/likes/user/<int:id>/', methods=['GET'])
    @require_api_key
    def get_like_by_user(id, **kwargs):
        likes = Like.query.filter_by(user_id=id)
        results = []

        if not likes:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # GET method
        if request.method == 'GET':
            for like in likes:
                obj = {
                    'id': like.id,
                    'user_id': like.user_id,
                    'event_id': like.event.id
                }
                results.append(obj)

            Response = jsonify(results)
            Response.status_code = 200
            return Response
    
    @app.route('/api/v1/likes/event/<int:id>/', methods=['GET'])
    @require_api_key
    def get_like_by_event(id, **kwargs):
        likes = Like.query.filter_by(event_id=id)
        results = []

        if not likes:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # GET method
        if request.method == 'GET':
            for like in likes:
                obj = {
                    'id': like.id,
                    'user_id': like.user_id,
                    'event_id': like.event.id
                }
                results.append(obj)

            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/likes/<int:id>/', methods=['PUT', 'DELETE'])
    @require_api_key
    def likes_manipulation(id, **kwargs):
        like = Like.query.filter_by(id=id).first()  
        if not like:
            # Raise an HTTPException with a 404 not found status code
            abort(404)
        # DELETE method
        if request.method == 'DELETE':
            like.delete()
            return {
                'id' : "{}".format(like.id)
            }
        # PUT method
        elif request.method == 'PUT':
            user_id = request.values.get('user_id')
            event_id = request.values.get('event_id')

            if user_id is not None:
                like.user_id = user_id
            if event_id is not None:
                like.event_id = event_id
            like.save()

            Response = jsonify({
                'id' : like.id,
                'user_id' : like.user_id,
                'event_id' : like.event_id
            })
            Response.status_code = 200
            return Response

    ####################################
    #      Attend related endpoints    #
    ####################################
    
    @app.route('/api/v1/attends/', methods=['GET'])
    @require_api_key
    def get_attends():
        if request.method == 'GET':
            attends = Attend.get_all()
            results = []

            for attend in attends:
                obj = {
                    'id': attend.id,
                    'user_id': attend.user_id,
                    'event_id': attend.event_id,
                    'will_go': attend.will_go
                }
                results.append(obj)

            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/attends/all/', methods=['GET'])
    @require_api_key
    def get_attends_all():
        if request.method == 'GET':

            join = db.session.query(User, Attend).filter(User.id==Attend.user_id)
                
            results = []
            
            for attend in join:
                obj = {
                    'id': attend[1].id,
                    'user_id': attend[1].user_id,
                    'event_id': attend[1].event_id,
                    'name': attend[0].name,
                    'profile_pic': attend[0].profile_pic,
                    'will_go': attend[1].will_go
                }
                results.append(obj)
            
            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/attends/<string:category>/', methods=['GET'])
    @require_api_key
    def get_attends_by_category(category, **kwargs):
        if request.method == 'GET':

            join = db.session.query(User, Attend).filter(User.id==Attend.user_id).filter(Attend.will_go==category)
                
            results = []
            
            for attend in join:
                obj = {
                    'id': attend[1].id,
                    'user_id': attend[1].user_id,
                    'event_id': attend[1].event_id,
                    'name': attend[0].name,
                    'profile_pic': attend[0].profile_pic,
                    'will_go': attend[1].will_go
                }
                results.append(obj)
            

            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/attends/event/<int:id>/<string:category>/', methods=['GET'])
    @require_api_key
    def get_attends_by_category_and_event_id(id, category, **kwargs):
        if request.method == 'GET':

            join = db.session.query(User, Attend).filter(Attend.event_id==id).filter(User.id==Attend.user_id).filter(Attend.will_go==category)
                
            results = []
            
            for attend in join:
                obj = {
                    'id': attend[1].id,
                    'user_id': attend[1].user_id,
                    'event_id': attend[1].event_id,
                    'name': attend[0].name,
                    'profile_pic': attend[0].profile_pic,
                    'will_go': attend[1].will_go
                }
                results.append(obj)
            

            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/attends/event/<int:id>/all/', methods=['GET'])
    @require_api_key
    def get_all_attends_by_event_id(id, **kwargs):
        if request.method == 'GET':

            join = db.session.query(User, Attend).filter(Attend.event_id==id).filter(User.id==Attend.user_id)
                
            results = []
            
            for attend in join:
                obj = {
                    'id': attend[1].id,
                    'user_id': attend[1].user_id,
                    'event_id': attend[1].event_id,
                    'name': attend[0].name,
                    'profile_pic': attend[0].profile_pic,
                    'will_go': attend[1].will_go
                }
                results.append(obj)
            

            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/attends/', methods=['PUT'])
    @require_api_key
    def post_attend():
        if request.method == 'PUT':
            user_id = request.args.get('user_id')
            event_id = request.args.get('event_id')
            will_go = request.args.get('will_go')

            if user_id and event_id and will_go:
                attend = Attend(user_id=user_id, event_id=event_id, will_go=will_go)
                attend.save()
            
                Response = jsonify({
                    'id': attend.id,
                    'user_id': attend.user_id,
                    'event_id': attend.event_id,
                    'will_go': str(attend.will_go)
                })
                Response.status_code = 201
                return Response

    @app.route('/api/v1/attends/<int:id>/', methods=['PUT'])
    @require_api_key
    def put_attend(id, **kwargs):
        if request.method == 'PUT':
            status = 0
            attend = Attend.query.filter_by(id=id).first()
            user_id = request.args.get('user_id')
            event_id = request.args.get('event_id')
            will_go = request.args.get('will_go')

            if not attend:
                if user_id and event_id and will_go:
                    attend = Attend(user_id=user_id, event_id=event_id, will_go=will_go)
                    attend.save()
                    status = 201
            else:
                if user_id is not None:
                    attend.user_id = user_id
                if event_id is not None:
                    attend.event_id = event_id
                if will_go is not None:
                    attend.will_go = will_go
                attend.save()
                status = 200

            Response = jsonify({
                'id': attend.id,
                'user_id': attend.user_id,
                'event_id': attend.event_id,
                'will_go': attend.will_go
            })
            Response.status_code = status
            return Response

    ####################################
    #    Favourite related endpoints   #
    ####################################

    @app.route('/api/v1/favourites/', methods=['GET'])
    @require_api_key
    def get_favourites():
        if request.method == 'GET':
            favourites = Favourite.get_all()
            results = []

            for fav in favourites:
                obj = {
                    'id': fav.id,
                    'user_id': fav.user_id,
                    'product_id': fav.product_id
                }
                results.append(obj)
            Response = jsonify(results)
            Response.status_code = 200
            return Response
    
    @app.route('/api/v1/favourites/top5/', methods=['GET'])
    @require_api_key
    def get_top5_favourites():
        if request.method == 'GET':
            favourites = Favourite.get_all()
            result = []

            for fav in favourites:
                count = db.session.query(Favourite).filter(Favourite.product_id == fav.product_id).count()
                result.append((fav.product_id, count))
            
            result = set(result)
            result = list(result)
            result = sorted(result, key=itemgetter(1), reverse=True)
            result = result[:5]

            res = []

            for item in result:
                product = db.session.query(Product).get(item[0])
                obj = {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'category_id': product.category_id,
                    'proof': str(product.proof),
                    'country': product.country,
                    'available': product.available,
                    'price': str(product.price),
                    'picture': product.picture,
                    'count': item[1]
                }
                res.append(obj)

            Response = jsonify(res)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/favourites/user/<int:id>/', methods=['GET'])
    @require_api_key
    def get_favourites_by_user(id, **kwargs):
        if request.method == 'GET':
            join = db.session.query(User, Favourite, Product).filter(User.id==id).filter(User.id==Favourite.user_id).filter(Favourite.product_id==Product.id)
            results = []

            for fav in join:
                obj = {
                    'id': fav[1].id,
                    'user_id': fav[1].user_id,
                    'user_name': fav[0].name,
                    'user_email': fav[0].email,
                    'user_pic': fav[0].profile_pic,
                    'product_id': fav[1].product_id,
                    'product_name': fav[2].name,
                    'product_pic': fav[2].picture
                }
                results.append(obj)
                
            Response = jsonify(results)
            Response.status_code = 200
            return Response

    @app.route('/api/v1/favourites/<int:id>/', methods=['PUT'])
    @require_api_key
    def put_favourites(id, **kwargs):
        if request.method == 'PUT':
            status = 0
            favourite = Favourite.query.filter_by(id=id).first()
            user_id = request.args.get('user_id')
            product_id = request.args.get('product_id')

            if not favourite:
                favourite = Favourite(user_id=user_id, product_id=product_id)
                favourite.save()
                status = 201
            else:
                if user_id is not None:
                    favourite.user_id = user_id
                if product_id is not None:
                    favourite.product_id = product_id
                favourite.save()
                status = 200

            Response = jsonify({
                'id': favourite.id,
                'user_id': favourite.user_id,
                'product_id': favourite.product_id
            })
            Response.headers['Access-Control-Allow-Origin'] = '*'
            Response.status_code = status
            return Response

    ####################################
    #         Helper functions         #
    ####################################

    def generate_api_key(input):
        salt = "INSERT SALT HASH HERE"
        data = str(input)+str(salt)
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def convertDate(date):
        return datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')

    return app
