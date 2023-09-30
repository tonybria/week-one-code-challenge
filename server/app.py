from flask import Flask, jsonify, request, make_response, abort
from models import db, Restaurant, RestaurantPizza, Pizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Define your routes here

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = [
        {
            'id': r.id,
            'name': r.name,
            'address': r.address  # Add address if needed
        }
        for r in restaurants
    ]
    return jsonify(restaurant_list)

@app.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return make_response(jsonify({'error': 'Restaurant not found'}), 404)

    pizzas = RestaurantPizza.query.filter_by(restaurant_id=restaurant_id).all()
    pizza_data = [
        {
            'id': pizza.id,
            'name': pizza.name,
            'ingredients': pizza.ingredients
        }
        for pizza in pizzas
    ]

    restaurant_data = {
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address,  # Add address if needed
        'pizzas': pizza_data
    }

    return jsonify(restaurant_data)

@app.route('/restaurants/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return make_response(jsonify({'error': 'Restaurant not found'}), 404)

    # Delete associated RestaurantPizza records
    RestaurantPizza.query.filter_by(restaurant_id=restaurant_id).delete()
    # Delete the restaurant
    db.session.delete(restaurant)
    db.session.commit()

    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizza_list = [
        {
            'id': p.id,
            'name': p.name,
            'ingredients': p.ingredients
        }
        for p in pizzas
    ]
    return jsonify(pizza_list)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    # Validate pizza_id and restaurant_id
    if not (Pizza.query.get(pizza_id) and Restaurant.query.get(restaurant_id)):
        return make_response(jsonify({'errors': ['Invalid pizza_id or restaurant_id']}), 400)

    # Validate price
    if not (1 <= price <= 30):
        return make_response(jsonify({'errors': ['Price must be between 1 and 30']}), 400)

    new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)

    try:
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        # Retrieve associated pizza data
        pizza = Pizza.query.get(pizza_id)
        pizza_data = {
            'id': pizza.id,
            'name': pizza.name,
            'ingredients': pizza.ingredients
        }

        return jsonify(pizza_data), 201
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'errors': ['Validation errors']}), 400)

if __name__ == '__main__':
    app.run(debug=True)
