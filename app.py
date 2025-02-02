from flask import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=271d1234d3f497eed5b1d80a07b3fcd1'
    r = requests.get(url).json()
    return r

@app.route('/')
def index_get():
    cities = City.query.all()
    weather_data = []

    for city in cities:
        r = get_weather_data(city.name)

        # Ensure API response is valid
        if r.get('cod') == 200:
            weather = {
                'city': city.name,
                'temperature': r['main']['temp'],
                'description': r['weather'][0]['description'],
                'icon': r['weather'][0]['icon'],
            }
            weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)

@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city').strip().title()  # Normalize input to title case
    
    if new_city:
        # Case-insensitive duplicate check
        existing_city = City.query.filter(db.func.lower(City.name) == new_city.lower()).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)

            if new_city_data.get('cod') == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
                flash('City added successfully!', 'success')
            else:
                err_msg = 'City does not exist in the world!'
        else:
            err_msg = 'City already exists in the database!'

    if err_msg:
        flash(err_msg, 'error')

    return redirect(url_for('index_get'))

@app.route('/delete/<name>', methods=['GET'])
def delete_city(name):
    city = db.session.query(City).filter_by(name=name).first()
    if city:
        db.session.delete(city)
        db.session.commit()
        flash("City deleted successfully!", "success")
    else:
        flash("City not found.", "error")
    return redirect(url_for('index_get'))

if __name__ == "__main__":
    app.run(debug=True, port=5500)
