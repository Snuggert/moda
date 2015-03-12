from msgpack import packb, unpackb
from snappy import compress, decompress
from btree import Tree, Node, Leaf
import btree

temp_tree = None

def decode_btree(obj):
    if b'__class__' in obj:
        cls_name = obj[b'__class__'].decode()
        data = obj[b'data']
        if cls_name == 'Leaf':
            obj = Leaf(temp_tree, bucket=data)
        elif cls_name == 'Node':
            obj = Node(temp_tree, bucket=data[b'bucket'], rest=data[b'rest'])
        else:
            temp_tree.max_size = data[b'max_size']
            temp_tree.root = data[b'root']
            return temp_tree
    return obj

def encode_btree(obj):
    if isinstance(obj, (Tree, Node, Leaf)):
        return {'__class__': obj.__class__.__name__,
                'data': obj.to_json()}
    return obj

def encode(data):
    return compress(packb(data, default=encode_btree))


def decode(data):
    global temp_tree
    temp_tree = Tree()
    return unpackb(decompress(data), object_hook=decode_btree)
