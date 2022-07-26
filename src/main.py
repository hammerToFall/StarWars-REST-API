"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, FavoriteCharacter, FavoritePlanet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# @app.route('/user', methods=['GET'])
# def handle_hello():

#     response_body = {
#         "msg": "Hello, this is your GET /user response "
#     }

#     return jsonify(response_body), 200


@app.route('/character', methods=['GET'])
def get_characters():
    "Returns the list of people"
    characters = Character.query.all()
  #  characters = Character.query.filter_by(name='Carlos')
    data = []
    for character in characters:
        data.append(character.serialize())
    # data = [character.serialize() for character in characters]  
    return jsonify(data), 200


@app.route('/character/<int:id>', methods=['GET'])
def character_detail(id):      #consultamos la lista de un personaje por id
    character = Character.query.get(id)
    return jsonify(character.serialize()), 200


@app.route('/planet', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    data = []
    data = [planet.serialize() for planet in planets]
    return jsonify(data), 200

@app.route('/planet/<int:id>', methods=['GET'])
def planet_detail(id):
    planet = Planet.query.get(id)
    return jsonify(planet.serialize()), 200


@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    data = []
    data = [user.serialize() for user in users]
    return jsonify(data), 200


@app.route('/user/favorites', methods=['GET'])
def get_favorites():
    user = request.json.get('user')

    userObj = User.query.filter_by(id=user['id']).first()

    if not userObj:
        return jsonify('User do not exist'), 404
    
    favoritesPlanetsObj = FavoritePlanet.query.filter_by(user_id=user['id']).all()
    favoriteCharactersObj = FavoriteCharacter.query.filter_by(user_id=user['id']).all()

    data = { 
        'favoritePlanets': [planet.serialize() for planet in favoritesPlanetsObj],
        'favoriteCharacters': [character.serialize() for character in favoriteCharactersObj]
    }

    return jsonify(data), 200

@app.route('/users/<int:user_id>/favorites', methods=['POST'])
def add_favorite_character(user_id):
    user = request.get_json()
    # print(user["character_id"])
    # print(user_id)

    favorite_character = FavoriteCharacter(user_id=user_id,character_id=user['character_id'])
    db.session.add(favorite_character)
    db.session.commit()

    data = { 
        "msg": "Favorite character saved"
    }

    return jsonify(data), 200

@app.route('/users/<int:user_id>/planet/favorites', methods=['POST'])
def add_favorite_planet(user_id):
    user = request.get_json()
    print(user["planet_id"])

    favorite_planet = FavoritePlanet(user_id=user_id,planet_id=user['planet_id'])
    db.session.add(favorite_planet)
    db.session.commit()

    data = { 
        "msg": "Favorite planet saved"
    }

    return jsonify(data), 200

@app.route('/favorite/people/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    # user = request.get_json()
    # print(user["character_id"])
    # print(user_id)
    character = FavoriteCharacter.query.filter_by(character_id=character_id).first()
    db.session.delete(character)
    db.session.commit()
    print(character)


    data = { 
        "msg": "Favorite character deleted"
    }

    return jsonify(data), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    
    planet = FavoritePlanet.query.filter_by(planet_id=planet_id).first()

    db.session.delete(planet)
    db.session.commit()
    print(planet)


    data = { 
        "msg": "Favorite planet deleted"
    }

    return jsonify(data), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
