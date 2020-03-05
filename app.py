from flask import Flask, jsonify, abort, make_response, request

app = Flask(__name__)

items = [
    {
        'name': 'Milk',
        'category': 'Dairy',
        'id': 12345
    },
    {
        'name': 'Sausages',
        'category': 'Meet',
        'id': 324
    },
]


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
    return jsonify({'items': items})


@app.route('/api/v1.0/items/<int:item_id>/', methods=['GET'])
@app.route('/api/v1.0/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = [item for item in items if item['id'] == item_id]
    if len(item) == 0:
        abort(404)
    return jsonify({'item': item[0]})


@app.route('/api/v1.0/items/', methods=['POST'])
@app.route('/api/v1.0/items', methods=['POST'])
def create_item():
    if not request.json or 'id' not in request.json:
        abort(400)

    item_id = request.json['id']
    item = [item for item in items if item['id'] == item_id]
    if len(item) != 0:
        abort(403)

    item = {
        'id': request.json['id'],
        'name': request.json.get('name', ''),
        'category': request.json.get('category', "")
    }
    items.append(item)
    return jsonify({'item': item}), 201


@app.route('/api/v1.0/items/<int:item_id>/', methods=['PUT'])
@app.route('/api/v1.0/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = [item for item in items if item['id'] == item_id]
    if len(item) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != str:
        abort(400)
    if 'category' in request.json and type(request.json['category']) != str:
        abort(400)
    item[0]['name'] = request.json.get('name', item[0]['name'])
    item[0]['category'] = request.json.get('category', item[0]['category'])
    return jsonify({'item': item[0]})


@app.route('/api/v1.0/items/<int:item_id>/', methods=['DELETE'])
@app.route('/api/v1.0/items/<int:item_id>', methods=['DELETE'])
def delete_task(item_id):
    item = [item for item in items if item['id'] == item_id]
    if len(item) == 0:
        abort(404)
    items.remove(item[0])
    return jsonify({'result': True})


if __name__ == '__main__':
    app.run(debug=True)
