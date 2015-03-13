#!env/bin/python
from btree import Tree
import json


def fancy_print(thingy, *args, **kwargs):
    print(json.dumps(thingy, indent=4), *args, **kwargs)


def main():
    for j in range(10):
        tree = Tree(max_size=3)
        for i in range(j+1):
            tree[i] = i**2

        fancy_print(tree)

        print('COMMMMIITTTTTT')
        tree.commit()
        print('IMPORRRTTTTT')
        new_tree = Tree.from_file()
        new_tree[2] = 20
        fancy_print(new_tree)
        print()
        print()


if __name__ == '__main__':
    main()
