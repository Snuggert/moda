from msgpack import packb, unpackb, Unpacker
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
    return packb(compress(add_integrity(packb(data, default=encode_btree))))


def decode(data, tree):
    def decode_btree(obj):
        if b'__class__' in obj:
            cls_name = obj[b'__class__'].decode()
            data = obj[b'data']
            if cls_name == 'Leaf':
                obj = Leaf(tree, bucket=bucket_to_lazynodes(data, tree))
            elif cls_name == 'Node':
                bucket = bucket_to_lazynodes(data[b'bucket'], tree)
                obj = Node(tree, bucket=bucket,
                           rest=LazyNode(offset=data[b'rest'], tree=tree))
            else:
                tree.max_size = data[b'max_size']
                tree.root = LazyNode(offset=data[b'root'], tree=tree)
                return tree
        return obj

    # Decompress the first data group that can be found in the data stream
    data = decompress(next(Unpacker(data)))

    data = unpackb(check_integrity(data), object_hook=decode_btree)
    return data


def bucket_to_lazynodes(bucket, tree):
    bucket =  {k.decode(): LazyNode(offset=v, tree=tree) for k, v in
            bucket.items()}
    return bucket
