from umsgpack import packb, unpackb, unpack
from snappy import compress, decompress  # noqa
from btree import Tree, Node, Leaf, LazyNode
from checksum import add_integrity, check_integrity


def encode_btree(obj):
    if isinstance(obj, (Tree, Node, Leaf)):
        obj = {'__class__': obj.__class__.__name__,
               'data': obj.serialize()}
    elif isinstance(obj, LazyNode):
        obj = obj.offset
    return obj


def encode(data):
    # Pack the data add the integrity compress it then to make it as small as
    # possible and then pack it again, so msgpack knows where the package ends
    return packb(compress(add_integrity(packb(encode_btree(data)))))


def decode(data, tree):
    def decode_btree(obj):
        if hasattr(obj, '__iter__') and '__class__' in obj:
            cls_name = obj['__class__']
            data = obj['data']
            if cls_name == 'Leaf':
                obj = Leaf(tree, bucket=bucket_to_lazynodes(data, tree))
            elif cls_name == 'Node':
                bucket = bucket_to_lazynodes(data['bucket'], tree)
                obj = Node(tree, bucket=bucket,
                           rest=LazyNode(offset=data['rest'], tree=tree))
            else:
                tree.max_size = data['max_size']
                tree.root = LazyNode(offset=data['root'], tree=tree)
                obj = tree
        return obj

    # Decompress the first data group that can be found in the data stream
    data = decompress(unpack(data))

    data = decode_btree(unpackb(check_integrity(data)))
    return data


def bucket_to_lazynodes(bucket, tree):
    bucket = {k: LazyNode(offset=v, tree=tree) for k, v in
              bucket.items()}
    return bucket
