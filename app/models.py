from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# Restaurant model
class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    pizzas = db.relationship('Pizza', secondary='restaurant_pizza', backref='restaurants')

    def __repr__(self):
        return f'<Restaurant {self.name}>'


# Pizza model
class Pizza(db.Model):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    restaurants = db.relationship('Restaurant', secondary='restaurant_pizza', backref='pizzas')

    def __repr__(self):
        return f'<Pizza {self.name}>'


# RestaurantPizza model
class RestaurantPizza(db.Model):
    __tablename__ = 'restaurant_pizza'

    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), primary_key=True)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), primary_key=True)

    restaurant = db.relationship('Restaurant', backref=db.backref('restaurant_pizzas', cascade='all, delete-orphan'))
    pizza = db.relationship('Pizza', backref=db.backref('restaurant_pizzas', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<RestaurantPizza restaurant_id={self.restaurant_id} pizza_id={self.pizza_id}>'


# Create tables
db.create_all()

# Seed data
restaurant1 = Restaurant(name='Restaurant 1')
restaurant2 = Restaurant(name='Restaurant 2')

pizza1 = Pizza(name='Pizza 1')
pizza2 = Pizza(name='Pizza 2')

restaurant1.pizzas.extend([pizza1, pizza2])
restaurant2.pizzas.append(pizza2)

db.session.add_all([restaurant1, restaurant2, pizza1, pizza2])
db.session.commit()

print('Seed data has been added successfully.')
