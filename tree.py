from base_tree import _BaseTree, _Node, _Links, TreeBaseClass, NodeTypeError
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from session import init_session, Session

class Node(_Node):
    __tablename__ = "node_v0"
    
    id: Mapped[str] = mapped_column(ForeignKey("base_node.id"), primary_key=True)
    user:Mapped[str] = mapped_column(default='default_user')

    __mapper_args__ = {
    "polymorphic_identity": "node_v0",
    }
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id: {self.id}, tag: {self.tag}, user: {self.user}, type:{self.type})"

class Tree(_BaseTree):
    
    def __init__(self, user, session:Session, nodeclass: Node):
        
        if issubclass(nodeclass, Node) is False:
            raise NodeTypeError(f'Tree Error - nodeclass {nodeclass} is not derived from {Node}')
        
        self.__user = user
        
        query = session.query(nodeclass, _Links)           \
            .join(_Links, _Links.child_id == nodeclass.id) \
            .filter(nodeclass.user == user)                \
        
        _BaseTree.__init__(self, query=query, identifier=user, session=session)
    
    def create_node(self, parent: Node | None, data: Node):

        if parent is not None:
            if self.__user != parent.user:
                raise Exception('Tree Error - Node user, Parent user and/or tree user are not all equal.')
                    
        data.user = self.__user
        return super().create_node(parent, data)

def init_tree_session(url):
    return init_session(url, TreeBaseClass)