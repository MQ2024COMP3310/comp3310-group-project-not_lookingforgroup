from . import db

class Photo(db.Model): # Extension of base model class, models are for creating database objects.
    id = db.Column(db.Integer, primary_key=True) # Fields of the model
    name = db.Column(db.String(50), nullable=False)
    caption = db.Column(db.String(250), nullable=False)
    file = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(600), nullable=True)

    @property
    def serialize(self): # Function to retrieve data
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name,
           'caption'      : self.caption,
           'file'         : self.file,
           'desc'         : self.description,
       }
 
