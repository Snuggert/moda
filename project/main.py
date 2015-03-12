#!env/bin/python
from btree import Tree
from pprint import pprint
import json
from encode import encode, decode
def fancy_print(thingy, *args, **kwargs):
    print(json.dumps(thingy, indent=4), *args, **kwargs)


def main():
    for j in range(20):
        tree = Tree(max_size=3)
        for i in range(j+1):
            tree[i] = i**2

        tree.commit()
        new_tree = Tree.from_file()
        fancy_print(new_tree)


if __name__ == '__main__':
    main()
