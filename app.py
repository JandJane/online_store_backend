from flask import Flask, jsonify, abort, make_response, request
from flask_swagger_ui import get_swaggerui_blueprint

import db

app = Flask(__name__)

db.init_app(app)  # inits database

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


@app.route('/api/v1.0/items/', methods=['GET'])
@app.route('/api/v1.0/items', methods=['GET'])
def get_items():
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute('SELECT * from items')
    items = cur.fetchall()
    items = [dict(item) for item in items]
    return jsonify(items)


@app.route('/api/v1.0/items/<int:item_id>/', methods=['GET'])
@app.route('/api/v1.0/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute('SELECT * from items where id = %d' % item_id)
    item = cur.fetchall()
    if not len(item):
        abort(404)
    return jsonify(dict(item[0]))


@app.route('/api/v1.0/items/', methods=['POST'])
@app.route('/api/v1.0/items', methods=['POST'])
def create_item():
    if not request.json or 'id' not in request.json:
        abort(400)

    # Check if item already exists
    item_id = request.json['id']
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute('SELECT * from items where id = %d' % item_id)
    item = cur.fetchall()
    if len(item):
        abort(403)

    item = {
        'id': request.json['id'],
        'name': request.json.get('name', ''),
        'category': request.json.get('category', "")
    }
    cur.execute('INSERT INTO items VALUES (?, ?, ?)', (item['id'], item['name'], item['category']))
    conn.commit()
    return jsonify(item), 201


@app.route('/api/v1.0/items/<int:item_id>/', methods=['PUT'])
@app.route('/api/v1.0/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    if 'category' in request.json and type(request.json['category']) != str:
        abort(400)

    conn = db.get_db()
    cur = conn.cursor()
    if 'name' in request.json:
        cur.execute('UPDATE items SET name = ? where id = ?', (request.json['name'],  item_id))
    if 'category' in request.json:
        cur.execute('UPDATE items SET category = ? where id = ?', (request.json['category'], item_id))
    conn.commit()
    return get_item(item_id)


@app.route('/api/v1.0/items/<int:item_id>/', methods=['DELETE'])
@app.route('/api/v1.0/items/<int:item_id>', methods=['DELETE'])
def delete_task(item_id):
    conn = db.get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM items WHERE id = %d' % item_id)
    conn.commit()
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
