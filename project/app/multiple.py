from flask import Blueprint, jsonify
from btree import Tree

bp = Blueprint('multiple', __name__, url_prefix='/documents')


@bp.route('/', methods=['GET'])
def get():
    tree = Tree.from_file()
    l = []
    for k, v in tree:
        l.append({'id': k, 'data': v})
    return jsonify(items=l)


@bp.route('/', methods=['DELETE'])
def delete():
    tree = Tree.from_file()
    tree.root = tree._create_leaf()
    tree.commit()
    tree.compact()
    return jsonify()
