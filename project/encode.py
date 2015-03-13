from msgpack import packb, Unpacker
from snappy import compress, decompress  # noqa
from btree import Tree, Node, Leaf, LazyNode


def encode_btree(obj):
    if isinstance(obj, (Tree, Node, Leaf)):
        return {'__class__': obj.__class__.__name__,
                'data': obj.to_json()}
    elif isinstance(obj, LazyNode):
        return obj.offset
    return obj


def encode(data):
    return packb(data, default=encode_btree)


def decode(data, tree):
    def decode_btree(obj):
        if b'__class__' in obj:
            cls_name = obj[b'__class__'].decode()
            data = obj[b'data']
            if cls_name == 'Leaf':
                obj = Leaf(tree, bucket=data)
            elif cls_name == 'Node':
                bucket = {k: LazyNode(offset=v, tree=tree) for k, v in
                          data[b'bucket'].items()}
                obj = Node(tree, bucket=bucket,
                           rest=LazyNode(offset=data[b'rest'], tree=tree))
            else:
                tree.max_size = data[b'max_size']
                tree.root = LazyNode(offset=data[b'root'], tree=tree)
                return tree
        return obj

    unpacker = Unpacker(data, object_hook=decode_btree)
    return(next(unpacker))
