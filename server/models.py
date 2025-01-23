from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Define relationship to Pizza through RestaurantPizza
    pizzas = relationship(
        "Pizza",
        secondary="restaurant_pizzas",
        back_populates="restaurants"
    )

    # Relationship with RestaurantPizza
    restaurant_pizzas = relationship("RestaurantPizza", back_populates="restaurant")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "restaurant_pizzas": [rp.to_dict() for rp in self.restaurant_pizzas],
        }

    # add serialization rules
    serialize_rules = ("-pizzas.restaurants", "restaurant_pizzas")

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Define relationship to Restaurant through RestaurantPizza
    restaurants = relationship(
        "Restaurant",
        secondary="restaurant_pizzas",
        back_populates="pizzas"
    )

    # Relationship with RestaurantPizza
    restaurant_pizzas = relationship("RestaurantPizza", back_populates="pizza")

    # add serialization rules
    serialize_rules = ("-restaurant.pizzas",)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign keys for relationships
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"))
    
    # Define relationships
    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")
    
    cascade = "all, delete-orphan"

    # add serialization rules
    serialize_rules = ("-restaurant.pizzas", "-pizza.restaurant")

    # add validation
    @validates('price')
    def validate_price(self, key, value):
        if not (1 <= value <= 30):
            raise ValueError("Price must be between 1 and 30")
        return value
    

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
