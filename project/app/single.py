from flask import Blueprint, jsonify, request
from btree import Tree

bp = Blueprint('single', __name__, url_prefix='/document')


@bp.route('/<_id>/', methods=['GET'])
def get(_id):
    db = Tree.from_file()
    val = db[_id]
    return jsonify(data=val)


@bp.route('/<_id>/', methods=['PUT'])
def put(_id):
    db = Tree.from_file()
    print(request.json)
    print(request.data)
    if request.json is not None:
        data = request.json
    elif len(request.data):
        try:
            data = request.data.decode()
        except UnicodeError:
            return jsonify(error='Only UTF8 encoded data is accepted'), 500
    else:
        return jsonify(error='no data was specified'), 500

    db[_id] = data
    db.commit()
    return jsonify(id=_id, data=data)
