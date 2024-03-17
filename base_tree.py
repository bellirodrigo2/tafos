from treelib import Tree
from closure import TreeBaseClass, _Node, _Links
from sqlalchemy.orm.query import Query
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
    
    def __init__(self, query: list[(_Node, _Links)], identifier:str, session):
        
        self._session = session
        
        Tree.__init__(self, identifier = identifier)    
        
        sorted_query = sort_query(query)
        
        for node in sorted_query:
            super().create_node(tag = node[0].tag, identifier = node[0].id, parent=node[1].parent_id, data = node[0])
    
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

        try:
            self._session.commit()
        except:
            self._session.rollback()
            raise
        
        return super_return
    
    
    def add_node(self, parent: _Node | None, data):
        # checar se data.data nao está null
        # checar se data.identifier eh igual data.data.id
        #CHECAR SE data.TAG EH IGUAL data.data.tag
        return super().add_node(parent, data)
    
    # def remove_node(self, node: _Node):
        # pass
    
    # def remove_subtree(self, nid, identifier=None):
        # pass
    
    # def update_node(self, nid, **attrs):
        # pass