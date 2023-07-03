from flask import Flask, jsonify, make_response, request
from flask_migrate import Migrate

from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

# Models

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Pizza(db.Model):
    __tablename__ = 'pizzas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class RestaurantPizza(db.Model):
    __tablename__ = 'restaurant_pizza'
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), primary_key=True)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), primary_key=True)
    price = db.Column(db.Float, nullable=False)
    restaurant = db.relationship('Restaurant', backref=db.backref('restaurant_pizzas', cascade='all, delete-orphan'))
    pizza = db.relationship('Pizza', backref=db.backref('restaurant_pizzas', cascade='all, delete-orphan'))

# Routes

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = []
    for restaurant in restaurants:
        restaurant_list.append({
            'id': restaurant.id,
            'name': restaurant.name,
        })
    return jsonify(restaurant_list)

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        pizzas = []
        for pizza in restaurant.pizzas:
            pizzas.append({
                'id': pizza.id,
                'name': pizza.name,
            })
        return jsonify({
            'id': restaurant.id,
            'name': restaurant.name,
            'pizzas': pizzas
        })
    return make_response(jsonify({'error': 'Restaurant not found'}), 404)

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    return make_response(jsonify({'error': 'Restaurant not found'}), 404)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizza_list = []
    for pizza in pizzas:
        pizza_list.append({
            'id': pizza.id,
            'name': pizza.name,
        })
    return jsonify(pizza_list)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    if not price or not pizza_id or not restaurant_id:
        return make_response(jsonify({'errors': ['Missing required fields']}), 400)

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        return make_response(jsonify({'errors': ['Pizza or restaurant not found']}), 404)

    try:
        restaurant_pizza = RestaurantPizza(price=price, restaurant=restaurant, pizza=pizza)
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify({
            'id': pizza.id,
            'name': pizza.name,
        })
    except ValueError as e:
        return make_response(jsonify({'errors': [str(e)]}), 400)


if __name__ == '__main__':
    app.run(port=5555)
