from __future__ import print_function
import inspect

import unittest

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from treelib.exceptions import DuplicatedNodeIdError, MultipleRootError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from base_tree import _Node, _Links, _BaseTree, TreeBaseClass, NodeTypeError, BadFormedTreeError
from factories import node_map, populate_two_level_tree

file = 'test_base.db'
url = f'sqlite:///{file}'

tree_name = 'tree1'

class TreeCalculations(unittest.TestCase):

    def setUp(self):
        
        self.engine = create_engine(url)
        TreeBaseClass.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.query = self.session.query(_Node, _Links)       \
            .join(_Links, _Links.child_id == _Node.id)

        self.tree = _BaseTree(identifier = tree_name, query = self.query, session = self.session)

    def tearDown(self):
        _Node.__table__.drop(self.engine)
        _Links.__table__.drop(self.engine)

    def test_create_root(self):
        print(f"Testing '{inspect.currentframe().f_code.co_name}'")
        
        root = _Node(tag='root', id='root')
        self.tree.create_node(parent=None, data=root)

        self.assertNotEqual(self.tree.root, None, 'The root node is not None.')            
        self.assertEqual(self.tree.get_node('root').tag, 'root', 'get_node("root").tag error.')
    
    def test_raises(self):
        print(f"Testing '{inspect.currentframe().f_code.co_name}'")
        
        populate_two_level_tree(self.tree)
        root = self.tree.get_node(self.tree.root).data
        # suc = self.tree.get_node(self.tree.root).successors(tree_name)
        
        with self.assertRaises(DuplicatedNodeIdError):
            self.tree.create_node(parent=None, data=root)
            
        with self.assertRaises(NodeTypeError):
            self.tree.create_node(parent=root, data='hello world')
            
        with self.assertRaises(MultipleRootError): 
            root2 = _Node(tag='root2', id='root2')
            self.tree.create_node(parent=None, data=root2)
    
        extra = _Node(tag='extra', id='extra')
        extraL = _Links(parent_id='parent', child_id='extra')
        self.session.add(extra)
        self.session.add(extraL)
        self.session.commit()
        
        query2 = self.session.query(_Node, _Links)      \
            .join(_Links, _Links.child_id == _Node.id)
        
        with self.assertRaises(BadFormedTreeError):         
            tree2 = _BaseTree(identifier = tree_name, query = query2, session = self.session)

    def test_create_two_levels(self):
        print(f"Testing '{inspect.currentframe().f_code.co_name}'")
        
        populate_two_level_tree(self.tree)
            
        node00  = self.tree.get_node('00')
        node11  = self.tree.get_node('11')
        pred, exp_pred = node11.predecessor(tree_name), '01'
        suc, exp_suc = node00.successors(tree_name), ['10']
        sib, exp_sib = self.tree.siblings('00'), 2
        anc, exp_anc = self.tree.ancestor('11'), '01'
        children, exp_child = self.tree.children('00'), 1
        # print(self.tree)
        
        def gt_10(node):
            try:
                return node.tag.startswith('n')
            except ValueError:
                return False
        
        search, exp_search = self.tree.rsearch('12', gt_10), ['12','02']
        for i, n in enumerate(search):
            self.assertEqual(n, exp_search[i], 'Error during rsearch.')

        self.assertEqual(len(sib), exp_sib, 'Wrong number of siblings.') 
        self.assertEqual(len(self.query.all()), 7, 'Query´s length should be 7')
        self.assertEqual(len(self.tree.all_nodes()), 7, 'all_nodes should return a list with 7 items')
        self.assertEqual(len(self.tree.all_nodes_itr()), 7, 'all_nodes_itr should return a list with 7 items')        
        self.assertEqual(pred, exp_pred, 'node11 predecessor error.')
        self.assertEqual(suc, exp_suc, 'node00 sucessor error.')
        self.assertEqual(anc, exp_anc, 'node11 ancestor error.')
        self.assertEqual(len(children), exp_child, 'children len error.')
        self.assertEqual(self.tree['00'].tag, 'node00', '__getitem__ error.')
        self.assertEqual(node11.tag, 'node11', 'get_node("11").tag error.')
        self.assertEqual(self.tree.depth(), 2, 'Tree depth mismatch.')
        self.assertNotEqual(self.tree.root, None, 'The root node is not None.')

    def test_persistance(self):
        print(f"Testing '{inspect.currentframe().f_code.co_name}'")
        
        populate_two_level_tree(self.tree)
        
        self.tree = None
        tree2 = _BaseTree(identifier = tree_name, query = self.query, session = self.session)

        node00  = tree2.get_node('00')
        node11  = tree2.get_node('11')
        pred = node11.predecessor(tree_name)
            
        self.assertEqual(pred, '01', 'node11 predecessor error.')
        self.assertEqual(node11.tag, 'node11', 'get_node("11").tag error.')
        self.assertEqual(tree2.depth(), 2, 'Tree depth mismatch.')
        self.assertNotEqual(tree2.root, None, 'The root node is not None.')
        
        nodes2 = node_map(2, 4)

# if __name__ == '__main__':
#     unittest.main()
    