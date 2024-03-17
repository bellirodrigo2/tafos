from __future__ import print_function
import inspect

import unittest

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from treelib.exceptions import DuplicatedNodeIdError, MultipleRootError
from sqlalchemy import create_engine, String, DateTime, ForeignKey
from sqlalchemy.orm import Session, sessionmaker, mapped_column, Mapped

from base_tree import _Links #, _Node, _BaseTree, TreeBaseClass, NodeTypeError, BadFormedTreeError
from tree import Node, Tree
from factories import node_map, populate_two_level_tree
from sqlalchemy.sql import func

file = 'test_base.db'
url = f'sqlite:///{file}'

user1 = 'user1'
user2 = 'user2'

class _TimedNode(Node):
    __tablename__ = "timed_node"
    
    id: Mapped[str] = mapped_column(ForeignKey("node_v0.id"), primary_key=True)
    time_created = mapped_column(DateTime(timezone=True), server_default=func.now())
    time_updated = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    __mapper_args__ = {
    "polymorphic_identity": "timed_node",
    }

class TreeCalculations(unittest.TestCase):

    def setUp(self):
        
        self.engine = create_engine(url)
        Node.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.tree1 = Tree(user = user1, session = self.session, nodeclass=Node)
        self.tree2 = Tree(user = user2, session = self.session, nodeclass=Node)
        self.tree3 = Tree(user = user1, session = self.session, nodeclass=_TimedNode)

    def tearDown(self):
        Node.__table__.drop(self.engine)
        _Links.__table__.drop(self.engine)

    def test_(self):
        # testar duas classes diferentes, derivadas de Node.... para ver se usar o mesmo _Links nao vai dar problema
        pass