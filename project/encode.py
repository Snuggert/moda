from msgpack import packb, unpackb
from msgpack.exceptions import ExtraData
from snappy import compress, decompress  # noqa
from btree import Tree, Node, Leaf, LazyNode


def encode_btree(obj):
    print(obj)
    if isinstance(obj, (Tree, Node, Leaf)):
        print({'__class__': obj.__class__.__name__,
               'data': obj.to_json()})

        return {'__class__': obj.__class__.__name__,
                'data': obj.to_json()}
    elif isinstance(obj, LazyNode):
        print('This is an offset', obj.offset)
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
                print('THIS IS THE BUCKET')
                obj = Leaf(tree, bucket=data)
            elif cls_name == 'Node':
                print('THIS IS THE BUCKET')
                print(data[b'bucket'].items())
                bucket = {k: LazyNode(offset=v) for k, v in
                          data[b'bucket'].items()}
                obj = Node(tree, bucket=bucket,
                           rest=LazyNode(offset=data[b'rest'], tree=tree))
            else:
                tree.max_size = data[b'max_size']
                tree.root = LazyNode(offset=data[b'root'], tree=tree)
                print('THE TREE ROOOT')
                print(tree.root)
                return tree
        return obj

    try:
        unpackb(data, object_hook=decode_btree)
    except ExtraData as e:
        return e.unpacked
