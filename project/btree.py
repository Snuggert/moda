from collections import Mapping, MutableMapping, OrderedDict
from sortedcontainers import SortedDict

"""Module that monkey-patches json module when it's imported so
JSONEncoder.default() automatically checks for a special "to_json()"
method and uses it to encode the object if found.
"""
from json import JSONEncoder


def _default(self, obj):
    return getattr(obj, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default  # save unmodified default
JSONEncoder.default = _default  # replacement


class Tree(MutableMapping):
    def __init__(self, max_size=1024, filename='db.db'):
        self.root = self._create_leaf(tree=self)
        self.max_size = max_size
        self.filename = filename

    @staticmethod
    def _create_leaf(*args, **kwargs):
        return LazyNode(node=Leaf(*args, **kwargs))

    @staticmethod
    def _create_node(*args, **kwargs):
        return LazyNode(node=Node(*args, **kwargs))

    def _create_root(self, left, right):
        root = self._create_node(tree=self)
        root.bucket[right._smallest_key()] = left
        root.rest = right

        self.root = root

    def __getitem__(self, key):
        return self.root[key]

    def __setitem__(self, key, value):
        """
        Inserts the key and value into the root node. If the node has been
        split, creates a new root node with pointers to this node and the new
        node that resulted from splitting.
        """
        self.root._insert(key, value)

    def __delitem__(self, key):
        if self.root._delete(key) and isinstance(self.root, Node) and \
                len(self.root) == 1:
            self.root = self.root.rest

    def __iter__(self):
        pass

    def __len__(self):
        pass

    def to_json(self, extra=None):
        return {'root': self.root, 'max_size': self.max_size}

    def __repr__(self):
        return 'Tree(' + repr(self.root) + ', ' + repr(self.max_size) + ')'

    def commit(self):
        with open(self.filename, 'bw+') as db:
            self.root._commit(db)
            db.write(encode(self))

    @staticmethod
    def from_file(filename='db.db'):
        with open(filename, 'br') as db:
            tree = Tree(filename=filename)
            return decode(db.read(), tree)


class BaseNode(object):
    def __init__(self, tree, bucket=None):
        self.tree = tree
        if bucket is not None:
            self.bucket = SortedDict(bucket)
        else:
            self.bucket = SortedDict()

        self.lazy = None
        self.changed = False

    def _split(self):
        """
        Creates a new node of the same type and splits the contents of the
        bucket into two parts of an equal size. The lower keys are being stored
        in the bucket of the new node. The higher keys are being stored in
        the bucket of the old node. Afterwards, the new node is being returned.
        """
        new_bucket = self.bucket.items()[:len(self.bucket)//2]
        self.bucket = SortedDict(self.bucket.items()[len(self.bucket)//2:])

        new_node = LazyNode(node=self.__class__(tree=self.tree,
                                                bucket=new_bucket))

        if hasattr(new_node, 'rest'):
            new_node.rest = new_node.bucket.popitem()[1]

        new_node.changed = True

        if self is self.tree.root.node:
            print('yeaaah a root')
            self.tree._create_root(new_node, self.lazy)

        return new_node

    def _insert(self, key, value):
        """
        Inserts the key and value into the bucket. If the bucket has become too
        large, the node will be split into two nodes.
        """
        self.changed = True
        self.bucket[key] = value
        if len(self.bucket) > self.tree.max_size:
            return self, self._split()
        return self, None

    def _take_first(self):
        key = self.bucket.keys()[0]
        return key, self.bucket.pop(key)

    def _set_first(self, key, value):
        self.bucket[key] = value

    def _merge_right(self, right, parent):
        """Merge the buckets of the two children and place them at of the right
        node in the parent"""
        self.bucket.update(right.bucket)

        left_key = right._smallest_key()
        try:
            right_index = parent.bucket.values().index(right)
            right_key = parent.bucket.keys()[right_index]
            parent.bucket[right_key] = self

        except ValueError:
            parent.rest = self
        del parent.bucket[left_key]

    def _commit(self, db):
        pos = db.tell()
        db.write(encode(self))
        return pos


class Node(BaseNode):
    def __init__(self, *args, rest=None, **kwargs):
        self.rest = rest
        super(Node, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        """
        Selects the bucket the key should belong to.
        """
        return self._next_node(key)[key]

    def _next_node(self, key):
        for k in self.bucket.keys():
            if key < k:
                return self.bucket[k]

        return self.rest

    def _insert(self, key, value):
        """
        Recursively inserts the key and value by selecting the bucket the key
        should belong to, and inserting the key and value into that back. If
        the node has been split, it inserts the key of the newly created node
        into the bucket of this node.
        """
        self.changed = True
        old_node, new_node = self._next_node(key)._insert(key, value)
        if new_node is not None:
            return super()._insert(old_node._smallest_key(), new_node)
        return self, None

    def _delete(self, key):
        next_node = self._next_node(key)
        if next_node._delete(key) and \
                len(next_node) < self.tree.max_size/2:
            vals = self.bucket.values()

            try:
                index = vals.index(next_node)
                if index != 0:
                    l_neighbour = vals[index - 1]
                else:
                    l_neighbour = None

                try:
                    r_neighbour = vals[index + 1]
                except IndexError:
                    r_neighbour = self.rest

            except ValueError:
                l_neighbour = vals[-1]
                r_neighbour = None

            if r_neighbour is not None and \
                    (len(r_neighbour) - 1) > self.tree.max_size/2:
                key, val = r_neighbour._take_first()
                next_node._set_last(key, val)
                left = next_node
                right = r_neighbour

            elif l_neighbour is not None and \
                    (len(l_neighbour) - 1) > self.tree.max_size/2:
                key, val = l_neighbour._take_last()

                if key is None:
                    key = next_node._smallest_key()

                next_node._set_first(key, val)

                left = l_neighbour
                right = next_node
            else:
                if l_neighbour:
                    l_neighbour._merge_right(next_node, self)
                elif r_neighbour:
                    next_node._merge_right(r_neighbour, self)
                else:
                    print('This is a problemo, it should never happen')

                return True

            # Change index of the left of the two nodes
            left_key = self.bucket.keys()[vals.index(left)]
            self.bucket.pop(left_key)
            self.bucket[right._smallest_key()] = next_node

            return False

    def _merge_right(self, right, parent):
        self.bucket[right._smallest_key()] = self.rest
        self.rest = right.rest

        super()._merge_right(right, parent)

    def _take_last(self):
        last = self.rest
        self.rest = self.bucket.popitem()[1]
        return None, last

    def _set_last(self, key, value):
        self.bucket[value._smallest_key()] = self.rest
        self.rest = value

    def _smallest_key(self):
        if self.bucket:
            item = self.bucket.values()[0]
        else:
            item = self.rest

        return item._smallest_key()

    def __len__(self):
        return len(self.bucket) + 1

    def to_json(self, extra=None):
        return OrderedDict((('bucket', self.bucket), ('rest', self.rest)))

    def __repr__(self):
        return 'Node(' + str(dict(self.bucket)) + ', ' + repr(self.rest) + ')'

    def _commit(self, db):
        self.rest._commit(db)
        for n in self.bucket.values():
            n._commit(db)

        super()._commit(db)


class Leaf(Mapping, BaseNode):
    def _smallest_key(self):
        return self.bucket.keys()[0]

    def _take_last(self):
        return self.bucket.popitem()

    def _set_last(self, key, value):
        self.bucket[key] = value

    def __getitem__(self, key):
        return self.bucket[key]

    def _delete(self, key):
        del self.bucket[key]
        return True

    def __iter__(self):
        return self.bucket.__iter__()

    def __len__(self):
        return len(self.bucket)

    def to_json(self, extra=None):
        return self.bucket

    def __repr__(self):
        return 'Leaf(' + str(dict(self.bucket)) + ')'


class LazyNode(object):
    _init = False

    def __init__(self, offset=None, node=None, tree=None):
        """
        Sets up a proxy wrapper for a node at a certain disk offset.
        """
        self.node = node
        self.offset = offset
        self._init = True
        if self.node is not None:
            self.node.lazy = self

    @property
    def changed(self):
        """
        Checks if the node has been changed.
        """
        if self.node is None:
            return False

        return self.node.changed

    def _commit(self, db):
        """
        Commit the changes if the node has been changed.
        """
        if not self.changed:
            return

        self.offset = self.node._commit(db)
        self.changed = False

    def _load(self):
        """
        Load the node from disk.
        """
        if self.offset is None:
            raise Exception
        with open(self.tree.filename, 'rb') as db:
            return decode(db.seek(self.offset), self.tree)

    def __getattr__(self, name):
        """
        Loads the node if it hasn't been loaded yet, and dispatches the request
        to the node.
        """
        if self.node is None:
            self.node = self._load()

        return getattr(self.node, name)

    def __setattr__(self, name, value):
        """
        Dispatches the request to the node, if the proxy wrapper has been fully
        set up.
        """
        if not self._init or \
                ((name in self.__dict__ or name in LazyNode.__dict__)
                 and name != 'changed'):
            return super().__setattr__(name, value)

        setattr(self.node, name, value)

    def __repr__(self):
        return 'LazyNode(' + repr(self.offset) + ', ' + repr(self.node) + ')'


from encode import encode, decode  # No circular imports
