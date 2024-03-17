from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class TreeBaseClass(DeclarativeBase):
    pass

class _Node(TreeBaseClass):
    __tablename__ = "base_node"

    id: Mapped[str] = mapped_column(primary_key=True)    
    tag:Mapped[str]
    # depth: Mapped[int] = mapped_column(default=-1)

    type: Mapped[str]
    
    __mapper_args__ = {
        "polymorphic_identity": "base_node",
        "polymorphic_on": "type",
    }
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id: {self.id}, tag: {self.tag}, type:{self.type})"

class _Links(TreeBaseClass):
    __tablename__ = "link_table"

    parent_id: Mapped[str] = mapped_column(ForeignKey(_Node.id), primary_key=True, nullable=True)
    parent = relationship("_Node", foreign_keys=[parent_id])
    
    child_id: Mapped[str] = mapped_column(ForeignKey(_Node.id), primary_key=True)
    child = relationship("_Node", foreign_keys=[child_id])
        
    def __repr__(self):
        return f"{self.__class__.__name__}(parent_id: {self.parent_id}, child_id: {self.child_id})"
