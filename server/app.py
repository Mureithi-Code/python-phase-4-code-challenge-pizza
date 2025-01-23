#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError  # Import IntegrityError to handle database errors
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    try:
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])
    except Exception as e:
        print(f"Error fetching restaurants: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return ({"error": "Restaurant not found"}), 404
    return jsonify(restaurant.to_dict()), 200


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return ({"error": "Restaurant not found"}), 404
    
    # Delete associated restaurant_pizzas before deleting the restaurant itself
    RestaurantPizza.query.filter_by(restaurant_id=id).delete()
    db.session.delete(restaurant)
    db.session.commit()
    
    return {'message': 'Restaurant deleted successfully'}, 204


# Route to get all pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    try:
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])
    except Exception as e:
        print(f"Error fetching pizzas: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    
    if not data.get('price') or not data.get('pizza_id') or not data.get('restaurant_id'):
        return jsonify({"errors": ["validation errors"]}), 400
    
    price = data['price']
    if price < 1 or price > 30:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        response_data = {
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza_id": restaurant_pizza.pizza_id,
            "restaurant_id": restaurant_pizza.restaurant_id,
            "pizza": restaurant_pizza.pizza.to_dict(),
            "restaurant": restaurant_pizza.restaurant.to_dict()
        }

        return jsonify(response_data), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
