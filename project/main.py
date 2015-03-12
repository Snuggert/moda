#!env/bin/python
from btree import Tree
import json


def fancy_print(thingy, *args, **kwargs):
    print(json.dumps(thingy, indent=4), *args, **kwargs)


def main():
    for j in range(7):
        tree = Tree(max_size=3)
        for i in range(j+1):
            tree[i] = i**2

        fancy_print(tree)

        tree.commit()
        new_tree = Tree.from_file()
        fancy_print(new_tree)


if __name__ == '__main__':
    main()
