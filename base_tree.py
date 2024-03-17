from treelib import Tree
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

def sort_query(query: Query):
    
    rows = []
    child = get_children(query, None, rows)    
    while len(child) > 0:
        child = get_children(query, child, rows)
    
    if len(query.all()) != len(rows):
        raise BadFormedTreeError('BaseTree Error - Bad formed Query Tree')
    return rows
        
class _BaseTree(Tree):
    
    def __init__(self, query: list[(_Node, _Links)], identifier:str, session:Session, commit='always'):
        
        self._session = session
        self.__commit = commit
        
        Tree.__init__(self, identifier = identifier)    
        
        sorted_query = sort_query(query)
        
        for node in sorted_query:
            super().create_node(tag = node[0].tag, identifier = node[0].id, parent=node[1].parent_id, data = node[0])
    
    def __del__(self):
        if self.__commit == 'ondelete':
            self._session.commit()
            
            
    def __commit_IF(self):
        if self.__commit == 'always':
            self.save2file()        
            
    def _clone(self, identifier=None, with_tree=False, deep=False):
        return Tree(identifier=f'cloned_{self.identifier}')
    
    def save2file(self):
        try:
            self._session.commit()
        except:
            self._session.rollback()
            raise
    
    def create_node(self, parent: _Node | None, data: _Node):
        
        if isinstance(data, _Node) is False:
            raise NodeTypeError(f'BaseTree Error - "data" type is "{type(data)}, and should be "{_Node}""')
        parent_id = parent if (parent is None) else parent.id
        
        try:
            super_return = super().create_node(tag = data.tag, identifier=data.id, parent=parent_id, data=data)
        except:
            raise

        link = _Links(parent_id=parent_id, child_id=data.id)
        self._session.add(data)        
        self._session.add(link)

        self.__commit_IF()
                
        return super_return
    
    def add_node(self, parent: _Node | None, data):
        # checar se data.data nao está null
        # checar se data.identifier eh igual data.data.id
        #CHECAR SE data.TAG EH IGUAL data.data.tag
        return super().add_node(parent, data)
    
    # def remove_node(self, node: _Node):
        # pass
    
    def remove_subtree(self, nid, identifier=None):
        
        remove_tree = super().remove_subtree(nid, identifier)

        removed_list = list(remove_tree.expand_tree())
        
        query = self._session.query(_Links)      \
            .filter(_Links.child_id == nid)
            # .filter(_Node.id.in_(removed_list))

        count = query.count()
        if count != 1:
            raise Exception(f'New subtree root node should be unique, but {count} was found')

        for node in query.all():
            node.parent_id = None
            # self._session.delete(node[0])
            # self._session.delete(node[1])

        self.__commit_IF()
                   
        return SelfDestroyTree(tree = remove_tree, session = self._session)
    
    # def update_node(self, nid, **attrs):
        # pass

class SelfDestroyTree(Tree):
    
    def __init__(self, tree, session):
        Tree.__init__(self, tree=tree)
        self.__session = session
    
    def __del__(self):
        
        removeds = []
        for node in self._nodes.values():
            removeds.append(node.data.id)
            self.__session.delete(node.data)
        
        query = self.__session.query(_Links) \
            .filter(_Links.child_id.in_(removeds))
        
        query.delete(synchronize_session=False)

        self.__session.commit()
