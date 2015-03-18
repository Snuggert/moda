#!env/bin/python
from btree import Tree
import json
from os.path import getsize


def fancy_print(thingy, *args, **kwargs):
    print(json.dumps(thingy, indent=4), *args, **kwargs)


def main():
    for j in range(30):
        tree = Tree(max_size=3)
        for i in range(j+1):
            tree[i] = i**2

        fancy_print(tree)

        print(tree)
        print('COMMMMIITTTTTT')
        tree.commit()
        print('IMPORRRTTTTT')
        new_tree = Tree.from_file()
        print('IMUPPORRTTAANTT', new_tree)
        fancy_print(new_tree)
        new_tree[2] = 20
        fancy_print(new_tree)
        print('IMUPPORRTTAANTT', new_tree)
        fancy_print(new_tree)
        new_tree[3] = 30
        print('IMUPPORRTTAANTT', new_tree)
        fancy_print(new_tree)
        del new_tree[0]
        fancy_print(new_tree)
        print('IMUPPORRTTAANTT', new_tree)

        fancy_print(new_tree)
        print(getsize(new_tree.filename))
        print('COOOOMMMPPPAAACCCTTT')
        new_tree.compact()
        print(getsize(new_tree.filename))
        print('IMPORT COOOOMMMPPPAAACCCTTT')
        new_tree = Tree.from_file()
        new_tree[2] = 30
        print("PRRRRRINIINNT 11111")
        fancy_print(new_tree)
        del new_tree[3]
        print("PRRRRRINIINNT 2222222")
        fancy_print(new_tree)
        print()
        print()


if __name__ == '__main__':
    main()
