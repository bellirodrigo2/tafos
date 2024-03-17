from base_tree import _Node, _BaseTree

def node_map(level: int, number: int ):
    
    map = {}
    for i in range(number):
        map[i] = _Node(tag=f'node{level}{i}', id=f'{level}{i}')
    return map

def populate_two_level_tree(tree: _BaseTree):
        root = _Node(tag='root', id='root')
        tree.create_node(parent=None, data=root)
        
        nodes = node_map(0, 3)
        nodes1 = node_map(1, 3)
        
        tree.create_node(parent=root, data=nodes[0])
        tree.create_node(parent=root, data=nodes[1])
        tree.create_node(parent=root, data=nodes[2])
        tree.create_node(parent=nodes[0], data=nodes1[0])
        tree.create_node(parent=nodes[1], data=nodes1[1])
        tree.create_node(parent=nodes[2], data=nodes1[2])

