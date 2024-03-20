from treelib import Tree, Node
from closure import TreeBaseClass, _Node, _Links
from sqlalchemy.orm.query import Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

# from sqlalchemy.inspection import inspect

class NodeTypeError(Exception):
    """Exception raise when the node´s data is not a _Node (SQL) class type."""
    pass

class BadFormedTreeError(Exception):
    """Exception raise when at least one of the queries node is not linked to the tree."""
    pass

def get_children(query, parent, list):

    filter_expr = (_Links.parent_id == None) if parent is None else _Links.parent_id.in_(parent)
    children = query.filter(filter_expr).all()    
    list.extend(children)
    
    return [row[1].child_id for row in children]

def sort_query(query: Query)->Query:
    
    rows = []
    child = get_children(query, None, rows)   
    # FAZER OQUE AQUI SE NAO HOUVER NONE PARENT ???
    # ACHAR O UNICO NA QUERY QUE O PARENT NAO ESTA NA PROPRIA QUERY ?????
     
    while len(child) > 0:
        child = get_children(query, child, rows)
    
    if len(query.all()) != len(rows):
        raise BadFormedTreeError('BaseTree Error - Bad formed Query Tree')
    return rows
    
def create_tree(query: list[(_Node, _Links)], identifier:str, session:Session, commit='always'):
        
    sorted_query = sort_query(query)

    tree = Tree(node_class=Node)
    for node in sorted_query:
        tree.create_node(tag=node[0].tag, identifier=node[0].id, parent = node[1].parent_id, data=node[0])
    return _BaseTree(session=session, commit=commit, tree=tree, node_class=tree.node_class, identifier=identifier)

class _BaseTree(Tree):
    
    def __init__(self, session:Session, commit:str, tree=None, node_class=None, identifier=None):
        self._session = session
        self._commit = commit
        
        Tree.__init__(self, tree=tree, node_class=node_class, identifier=identifier)   
    
    def __del__(self):
        if self._commit == 'ondelete':
            self.save2file()
            
    def _commit_IF(self):
        if self._commit == 'always':
            self.save2file()        
            
    def _clone(self, identifier=None, with_tree=False):
        return Tree(identifier=f'cloned_{self.identifier}')

    def __get_parent_id(self, parent):
        return parent.identifier if isinstance(parent, self.node_class) else parent.id if isinstance(parent, _Node) else parent
    
    def save2file(self):
        try:
            self._session.commit()
        except:
            self._session.rollback()
            raise
    
    def create_node(self, parent: _Node | Node | str | None, data: _Node):
        
        if isinstance(data, _Node) is False:
            raise NodeTypeError(f'BaseTree Error - "data" type is "{type(data)}, and should be "{_Node}""')

        node = self.node_class(tag=data.tag, identifier=data.id, data=data)
        self.add_node(node=node, parent=parent)
        return node

    def add_node(self, node: Node, parent: Node | _Node | str | None):
        
        if node.identifier != node.data.id:
            raise Exception(f"Tree node ID is and SQL node ID is different. {node.identifier} x {node.data.id}")
        if node.tag != node.data.tag:
            raise Exception(f"Tree node TAG is and SQL node TAG is different. {node.tag} x {node.data.tag}")

        parent_id = self.__get_parent_id(parent)

        try:
            super_return = super().add_node(node=node, parent=parent_id)
        except:
            raise
            
        link = _Links(parent_id=parent_id, child_id=node.data.id)
        self._session.add(node.data)
        self._session.add(link)

        self._commit_IF()
                
        return super_return
            
    def merge(self, nid, new_tree):
        pass
    
    def paste(self, node: _Node | Node | str | None, tree: Tree):
        pass
    
    def update_node(self, nid, **attrs):
        pass
    
    def remove_node(self, node: _Node):
        # chamar o remove_subtree e deixar a SelfDestroyTree morrer
        pass
    
    def remove_subtree(self, nid, identifier=None):
        
        remove_tree = super().remove_subtree(nid, identifier)

        query = self._session.query(_Links)      \
            .filter(_Links.child_id == nid)

        count = query.count()
        if count != 1:
            raise Exception(f'New subtree root node should be unique, but {count} was found')

        query[0].parent_id = None

        self._commit_IF()
                   
        return SelfDestroyTree(tree = remove_tree, session = self._session, commit = self._commit, \
            identifier=self.identifier, node_class=self.node_class)
        
class SelfDestroyTree(_BaseTree):

    def __init__(self, tree, session, commit, node_class, identifier):
        _BaseTree.__init__(self, tree=tree, session=session, commit=commit, \
            node_class=node_class, identifier=identifier)

    def transfer_tree(self) ->Tree:
        tree = _BaseTree(session = self._session, tree=self, node_class=self.node_class, commit=self._commit)
        self._nodes = {}
        return tree
            
    def _clean_table(self):
        removeds = []
        for node in self._nodes.values():
            removeds.append(node.data.id)
            self._session.delete(node.data)
        
        query = self._session.query(_Links) \
            .filter(_Links.child_id.in_(removeds))
        
        query.delete(synchronize_session=False)

        self._session.commit()
    
    def __del__(self):
        self._clean_table()