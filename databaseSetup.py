from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ ="user"
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))
class Category(Base):
    __tablename__="category"
    id = Column(Integer, primary_key= True)
    name = Column(String(250), nullable = False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

#stores items and show which category items are part of
class Item(Base):
    __tablename__="items"
    id = Column(Integer, primary_key= True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    category = relationship(Category)
    user = relationship(User)
    @property
    def serialize(self):
        return{
            'name':self.name,
            'description':self.description,
            'id': self.id,
            'user': self.user.name,
            'category': self.category.name,
        }

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
