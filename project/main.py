from flask import (
  Blueprint, render_template, request, 
  flash, redirect, url_for, send_from_directory, 
  current_app, make_response
)
from .models import Photo
from sqlalchemy import asc, text
from . import db
import os

main = Blueprint('main', __name__) # Blueprint created with the name of the script.

# This is called when the home page is rendered. It fetches all images sorted by filename.
@main.route('/') # Homepage
def homepage():
  photos = db.session.query(Photo).order_by(asc(Photo.file)) # using default session query the database and sort by filename
  return render_template('index.html', photos = photos) # using the html index, passes the photots to the template

@main.route('/uploads/<name>') # uploads folder and file, used to access uploaded files
def display_file(name): # Binds the name from the url to paramater
  return send_from_directory(current_app.config["UPLOAD_DIR"], name) # STD flask function to access file in a directory, TODO `~werkzeug.security.safe_join`

# Upload a new photo
@main.route('/upload/', methods=['GET','POST']) # Base of the uploads directory, GET the interface or POST an upload
def newPhoto():
  if request.method == 'POST': # Logic for POSTing an image
    file = None
    if "fileToUpload" in request.files: # Grab a named field
      file = request.files.get("fileToUpload") # caste the field to a file
    else:
      flash("Invalid request!", "error") # If there is no field popup an error

    if not file or not file.filename:
      flash("No file selected!", "error") # If the file isn't a file popup error
      return redirect(request.url) # Redirect TODO this redirects on user input

    filepath = os.path.join(current_app.config["UPLOAD_DIR"], file.filename) # Creates filepath by combing configured path and the filename
    file.save(filepath) # Saves the file TODO secure_filename?

    newPhoto = Photo(name = request.form['user'], # Constructing an SQL element
                    caption = request.form['caption'],
                    description = request.form['description'],
                    file = file.filename) # TODO investigate for vulnerability, can a filename be used for SQL injection
    db.session.add(newPhoto) # Add the element to the database
    flash('New Photo %s Successfully Created' % newPhoto.name) # TODO invstigate for CSS
    db.session.commit()
    return redirect(url_for('main.homepage')) # Return to homepage
  else: # Logic for GETing the page
    return render_template('upload.html') # Load the "template" html with void params

# This is called when clicking on Edit. Goes to the edit page.
@main.route('/photo/<int:photo_id>/edit/', methods = ['GET', 'POST']) # Base of the photo directory, GET the interface or POST an edit
def editPhoto(photo_id):
  editedPhoto = db.session.query(Photo).filter_by(id = photo_id).one() # retrieve the photo from db
  if request.method == 'POST': # If data is being sent to the webserver
    if request.form['user']: # If the user field is not empty process post
      editedPhoto.name = request.form['user']
      editedPhoto.caption = request.form['caption']
      editedPhoto.description = request.form['description']
      db.session.add(editedPhoto)
      db.session.commit() # same id so likely overwrites
      flash('Photo Successfully Edited %s' % editedPhoto.name)
      return redirect(url_for('main.homepage'))
  else:
    return render_template('edit.html', photo = editedPhoto) # if Get use edit template with photo


# This is called when clicking on Delete. 
@main.route('/photo/<int:photo_id>/delete/', methods = ['GET','POST']) # No gaurds for GET or POST, accessing the page triggers the logic.
def deletePhoto(photo_id):
  fileResults = db.session.execute(text('select file from photo where id = ' + str(photo_id))) # Potential vulnerability TODO investigate
  filename = fileResults.first()[0] # Potential out of bounds exception
  filepath = os.path.join(current_app.config["UPLOAD_DIR"], filename) # COmpletes the filepath for the file serverside
  os.unlink(filepath) # Soft delete the file
  db.session.execute(text('delete from photo where id = ' + str(photo_id))) # Same potential vulnerability TODO
  db.session.commit()
  
  flash('Photo id %s Successfully Deleted' % photo_id) # Potential vulnerability TODO investigate cross site scripting
  return redirect(url_for('main.homepage'))

