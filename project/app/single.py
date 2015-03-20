from flask import Blueprint, jsonify, request
from btree import Tree

bp = Blueprint('single', __name__, url_prefix='/document')


@bp.route('/<_id>/', methods=['GET'])
def get(_id):
    db = Tree.from_file()
    try:
        return jsonify(data=db[_id])
    except KeyError:
        return jsonify(error='No data was found for this id'), 404


@bp.route('/<_id>/', methods=['POST'])
def post(_id):
    db = Tree.from_file()
    if _id in db:
        return jsonify(error=('This key already exists in the database, use '
                              'PUT to update the key')), 500

    return add_request_to_db(db, _id)


@bp.route('/<_id>/', methods=['PUT'])
def put(_id):
    db = Tree.from_file()
    if _id not in db:
        return jsonify(error=('No data was found for this id, use POST if'
                              ' you want to add a new document')), 404
    return add_request_to_db(db, _id)


@bp.route('/<_id>/', methods=['DELETE'])
def delete(_id):
    db = Tree.from_file()
    try:
        del db[_id]
    except KeyError:
        return jsonify(error='No data was found for this id'), 404

    db.commit()

    return jsonify(succes='deleted')


def add_request_to_db(db, _id):
    if request.json is not None:
        data = request.json
    elif len(request.get_data()):
        try:
            data = request.get_data().decode()
        except UnicodeError:
            return jsonify(error='Only UTF8 encoded data is accepted'), 500
    else:
        return jsonify(error='No data was specified'), 500
    db[_id] = data
    db.commit()
    return jsonify(id=_id, data=data)
