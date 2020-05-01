from time import sleep
import requests
from flask import Flask, jsonify, abort, make_response, request
from flask_swagger_ui import get_swaggerui_blueprint
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, get_raw_jwt
)
import mysql.connector

app = Flask(__name__)

# Init database
config = {
        'user': 'admin',
        'password': 'admin',
        'host': 'db',
        'database': 'my_db'
    }
sleep(10)
db = mysql.connector.connect(**config)

# Init JWT authorization
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60
app.config['JWT_HEADER_TYPE'] = ''
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = 'refresh'
jwt = JWTManager(app)
USERS = {'admin': 'admin'}
blacklist = set()

# init swagger
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Online Grocery Store"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Item not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(403)
def already_exists(error):
    return make_response(jsonify({'error': 'Item with this id already exists'}), 403)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


@app.route('/token/validate/', methods=['POST'])
@app.route('/token/validate', methods=['POST'])
@jwt_required
def validate():
    try:
        return jsonify({'valid_user_token': True}), 200
    except:
        return jsonify({'valid_user_token': False}), 201
    return jsonify({'current_user': current_user}), 200


@app.route('/token/register/', methods=['POST'])
@app.route('/token/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username in USERS:
        return jsonify({'error': 'User with this username already exists'}), 403
    USERS[username] = password
    return jsonify({'register': f'Sucessfully registered user {username}'}), 200


@app.route('/token/auth/', methods=['POST'])
@app.route('/token/auth', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username not in USERS or USERS[username] != password:
        return jsonify({'login': False}), 401
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    resp = jsonify({'login': True, 'access_token': access_token, 'refresh_token': refresh_token})
    return resp, 200


@app.route('/token/refresh/', methods=['POST'])
@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    resp = jsonify({'refresh': True, 'access_token': access_token})
    return resp, 200


@app.route('/token/remove/', methods=['DELETE'])
@app.route('/token/remove', methods=['DELETE'])
@jwt_refresh_token_required
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    resp = jsonify({'logout': True})
    return resp, 200


@app.route('/api/v1.0/items/', methods=['GET'])
@app.route('/api/v1.0/items', methods=['GET'])
def get_items():
    cur = db.cursor()
    cur.execute('SELECT * from items')
    items = cur.fetchall()
    print(items)
    items = [dict(zip(['id', 'name', 'category'], item)) for item in items]
    return jsonify(items)


@app.route('/api/v1.0/items/<int:item_id>/', methods=['GET'])
@app.route('/api/v1.0/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    cur = db.cursor()
    cur.execute('SELECT * from items where id = %d' % item_id)
    item = cur.fetchall()
    if not len(item):
        abort(404)
    return jsonify(dict(zip(['id', 'name', 'category'], item[0])))


@app.route('/api/v1.0/item/', methods=['POST'])
@app.route('/api/v1.0/item', methods=['POST'])
@jwt_required
def create_item():
    if not request.json or 'name' not in request.json or not request.json['name'] or 'category' not in request.json \
            or not request.json['category']:
        abort(400)
    cur = db.cursor()
    item = {
        'name': request.json.get('name', ''),
        'category': request.json.get('category', "")
    }
    cur.execute("INSERT INTO items (name, category) VALUES ('%s', '%s')" % (item['name'], item['category']))
    db.commit()
    cur.execute('SELECT LAST_INSERT_ID()')
    item['id'] = cur.fetchall()[0][0]
    return jsonify(item), 201


@app.route('/api/v1.0/items/<int:item_id>/', methods=['PUT'])
@app.route('/api/v1.0/items/<int:item_id>', methods=['PUT'])
@jwt_required
def update_item(item_id):
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    if 'category' in request.json and type(request.json['category']) != str:
        abort(400)

    cur = db.cursor()
    if 'name' in request.json:
        cur.execute("UPDATE items SET name = '%s' where id = %d" % (request.json['name'],  item_id))
    if 'category' in request.json:
        cur.execute("UPDATE items SET category = '%s' where id = %d" % (request.json['category'], item_id))
    db.commit()
    return get_item(item_id)


@app.route('/api/v1.0/items/<int:item_id>/', methods=['DELETE'])
@app.route('/api/v1.0/items/<int:item_id>', methods=['DELETE'])
@jwt_required
def delete_task(item_id):
    cur = db.cursor()
    cur.execute('DELETE FROM items WHERE id = %d' % item_id)
    db.commit()
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
