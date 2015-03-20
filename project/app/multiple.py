from flask import Blueprint, jsonify
from btree import Tree
from app.single import add_request_to_db

import uuid

bp = Blueprint('multiple', __name__, url_prefix='/documents')


@bp.route('/', methods=['GET'])
def get():
    db = Tree.from_file()
    l = []
    for k, v in db:
        l.append({'id': k, 'data': v})
    return jsonify(items=l)


@bp.route('/', methods=['DELETE'])
def delete():
    db = Tree.from_file()
    db.root = db._create_leaf()
    db.commit()
    db.compact()
    return jsonify()


@bp.route('/', methods=['POST'])
def post():
    db = Tree.from_file()
    _id = uuid.uuid4()
    return add_request_to_db(db, _id)
