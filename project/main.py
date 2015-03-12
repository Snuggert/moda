#!env/bin/python
from btree import Tree
from pprint import pprint
import json


def main():
    for j in range(20):
        tree = Tree(max_size=3)
        for i in range(j+1):
            tree[i] = i**2
        for i in range(j+1):
            del tree[i]
            print(json.dumps(tree.root, indent=4))
        print()


if __name__ == '__main__':
    main()
