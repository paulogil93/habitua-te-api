# Habitua-te

Habitua-te is an Ionic App built only for the costumers of a local bar, Habitua-te Bar, located in Penalva do Castelo, Viseu, Portugal. Users can check what kind of product are available, their description and price. They can also see what are the upcoming events that will be hosted at the bar.

This project is divided in:

* [Habitua-te API](https://www.github.com/paulogil93/habitua-te-api)
* [Habitua-te Ionic](https://www.github.com/paulogil93/habitua-te-ionic)
* [Habitua-te Admin](https://www.github.com/paulogil93/habitua-te-admin)



# Habitua-te API

In order to respond to the different kind of requests performed within the app, it was better to make a REST API. It was built using SQLAlchemy to deal with the Database and Flask to deal with the calls.

## SQLAlchemy

<p align="center">
	<img src="https://miro.medium.com/max/590/1*gJO7yKfLFOK2zfHaFDMdgA.jpeg" width=450 height=225/>
	<img src="https://img.favpng.com/7/5/11/postgresql-logo-computer-software-database-png-favpng-VzwjvpxaDys6FnN0apYZJbGV7.jpg" width=210 height=225/>
</p>

SQLAlchemy is the Python SQL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL.
It is great for it's simplicity as we only have to write down the models and SQLAlchemy migrates all those table definitions into the Database, which in this case PostgreSQL was used.

## Flask

Flask is a lightweight [WSGI](https://wsgi.readthedocs.io/) web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications. It began as a simple wrapper around [Werkzeug](https://www.palletsprojects.com/p/werkzeug) and [Jinja](https://www.palletsprojects.com/p/jinja) and has become one of the most popular Python web application frameworks.

It also has some security on the endpoints. When a user registers, it is generated an API Key which is stored on the Database. It is verified everytime the user makes a call to the API.

```python
  def require_api_key(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            users = User.get_all()
            for user in users:
                if request.headers.get('X-Api-Key') and user.api_key == request.headers.get('X-Api-Key'):
                    return view_function(*args, **kwargs)
            abort(401)
        return decorated_function
```


## Get the App

You can download and try the full project by following the link into Google Play Store.
<br>
<br>
[<img src="https://lh3.googleusercontent.com/1hJj6Aw2k6cEyFu10xdj5riLo0wBGFKE5XnbGaymhgo1z8Tsr8EpfJr2jbQFRxDONvwk6lak-62F2Fx7-_jp-ykJKA=w1000" width=200 height=60>](https://play.google.com/store/apps/details?id=com.paulogil.habitua_te)
