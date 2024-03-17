from treelib import Tree
from closure import TreeBaseClass, _Node, _Links
# from sqlalchemy.inspection import inspect

class _BaseTree(Tree):
    
    def __init__(self, query: list[(_Node, _Links)], identifier:str, session, nodeclass: _Node):
        
        self._session = session
        self._nodeclass = nodeclass
        
        Tree.__init__(self, identifier = identifier)    
            
        for node in query:
            super().create_node(identifier = node[0].id, parent=node[1].parent_id, data = node[0])
            
    def create_node(self, parent: _Node | None, data: _Node):
                
        is_root = parent is None
        has_root = self.root is not None
        
        if has_root is is_root:
            raise Exception(f'BaseTree Error - Tree has_root({has_root}) and Node is_root({is_root})')
                
        if (parent is not None) and (isinstance(parent, self._nodeclass) is False):
                raise Exception(f'BaseTree Error - Parent object is not instance of {self._nodeclass}')
    
        if isinstance(data, self._nodeclass) is False:
            raise Exception(f'BaseTree Error - Data object is not instance of {self._nodeclass}')

        parent_id = parent.id if isinstance(parent, self._nodeclass) else parent
        
        parent_counts = self._session.query(self._nodeclass)    \
            .filter(self._nodeclass.id == parent_id)            \
            .order_by(self._nodeclass.depth.asc())              \
            .count()
            
        if has_root is True and parent_counts == 0:
            raise Exception(f'BaseTree Error - Node ({parent_id}) is not part of this tree.')
        
        query_link = self._session.query(_Links)    \
            .filter(_Links.child_id == data.id)      \
            .all()
        if len(query_link) > 0:
            raise Exception(f'BaseTree Error - Node ({data.id}) already has a parent.')
        
        parent_depth = 0 if is_root else parent.depth + 1
        data.depth = parent_depth
        
        self._session.add(data)

        try:
            self._session.commit()
        except:
            self._session.rollback()
            return None
        
        self._session.refresh(data)
        
        link = _Links(parent_id=parent_id, child_id=data.id)
        
        self._session.add(link)

        try:
            self._session.commit()
        except:
            self._session.rollback()
            self._session.delete(data)
            self._session.commit()
            return None
            
        return super().create_node(identifier=data.id, parent=parent_id, data=data)
    
    def remove_node(self, node: _Node):
        # checar se node é do nodeclass correto ? fazer uma função interna pra isso e rodar em todas as funções ?
        
        if node is None:
            return None
        
        # checar se a tree ja nao faz uns checks para error bons...se for o caso,
        # usar composition.... chamar a função na tree primeiro e se der certo, fazer checks de SQL e então ir pro SQL

        st = self.subtree(node)
        # expand_tree para pegar todos os id´s
        nodes = [node for node in st.expand_tree(mode=Tree.DEPTH)]
        
        for node in nodes:
            self._session.delete(node.data)
            # remove the links from node.id
            pass
            
        return super().remove_node(node.id)
    
    def update_node(self, nid, **attrs):
        return super().update_node(nid, **attrs)