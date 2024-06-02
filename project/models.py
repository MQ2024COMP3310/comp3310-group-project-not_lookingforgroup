# Added dependencies
from flask_login import UserMixin
from . import db

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    caption = db.Column(db.String(250), nullable=False)
    file = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(600), nullable=True)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name,
           'caption'      : self.caption,
           'file'         : self.file,
           'desc'         : self.description,
       }
 
 # Added model to store user data
 # TODO implement admin roles.
 # TODO implement a default user session role
 # TODO since default roles will exist, role based access controls are needed
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    # needed a role
    role = db.Column(db.String())

# Added model for comments
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False) # Twitter x4!
    photo_id = db.Column(db.Integer,db.ForeignKey('photo.id'))
    photo = db.relationship(Photo)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    user = db.relationship(User)