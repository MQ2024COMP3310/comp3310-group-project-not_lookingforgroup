from flask import (
  Blueprint, render_template, request, 
  flash, redirect, url_for, send_from_directory, 
  current_app, make_response
)
from flask_login import login_required, current_user
from .models import Photo, User, Comment
from sqlalchemy import asc, text
from . import db
import os

#########################
##### Added
#########################
from werkzeug.exceptions import InternalServerError
from werkzeug.utils import escape
# from flask_wtf.csrf import CSRFProtect
#########################

main = Blueprint('main', __name__)

#Prevents CSRF attacks on the @main
# TODO csrf = CSRFProtect(main)

# This is called when the home page is rendered. It fetches all images sorted by filename.
@main.route('/')
def homepage():
  photos = db.session.query(Photo).order_by(asc(Photo.file))
  return render_template('index.html', photos = photos)

@main.route('/uploads/<name>')
def display_file(name):
  return send_from_directory(current_app.config["UPLOAD_DIR"], name)

# TODO authorisation
# Upload a new photo
@login_required
@main.route('/upload/', methods=['GET','POST'])
def newPhoto():
  if request.method == 'POST':
    file = None
    if "fileToUpload" in request.files:
      file = request.files.get("fileToUpload")
    else:
      flash("Invalid request!", "error")

    if not file or not file.filename:
      flash("No file selected!", "error")
      return redirect(request.url)

    filepath = os.path.join(current_app.config["UPLOAD_DIR"], file.filename)
    file.save(filepath)

    newPhoto = Photo(name = current_user.name, 
                    caption = request.form['caption'],
                    description = request.form['description'],
                    file = file.filename)
    db.session.add(newPhoto)
    flash('New Photo %s Successfully Created' % newPhoto.name)
    db.session.commit()
    return redirect(url_for('main.homepage'))
  else:
    return render_template('upload.html')

# TODO authorisation
# This is called when clicking on Edit. Goes to the edit page.
@login_required
@main.route('/photo/<int:photo_id>/edit/', methods = ['GET', 'POST'])
def editPhoto(photo_id):
  editedPhoto = db.session.query(Photo).filter_by(id = photo_id).one()
  if not (editedPhoto.name == current_user.name):
    return redirect(url_for('main.profile'))
  if request.method == 'POST':
    if request.form['user'] == current_user.name:
      editedPhoto.name = request.form['user']
      editedPhoto.caption = request.form['caption']
      editedPhoto.description = request.form['description']
      db.session.add(editedPhoto)
      db.session.commit()
      flash('Photo Successfully Edited %s' % editedPhoto.name)
      return redirect(url_for('main.homepage'))
    return redirect(url_for('main.profile'))
  else:
    # TODO handle invalid user/ role
    if (current_user.role == 'admin' or current_user.name == editedPhoto.name):
      return render_template('edit.html', photo = editedPhoto)
    else:
      #TODO failure logic... stub, log the security issue
      current_app.logger.warning("User: \""+ current_user.name +
                                 "\" tried to edit another users photo.")
      return redirect(url_for('main.profile'))
      

# TODO authorisation
# This is called when clicking on Delete.
@login_required
@main.route('/photo/<int:photo_id>/delete/', methods = ['GET','POST'])
def deletePhoto(photo_id):
  fileResults = db.session.execute(text('select file from photo where id = ' + str(photo_id)))
  if not(db.session.query(Photo).filter_by(id = photo_id).one().name == current_user.name or
         current_user.role == 'admin'):
    return redirect(url_for('main.homepage'))
  filename = fileResults.first()[0]
  filepath = os.path.join(current_app.config["UPLOAD_DIR"], filename)
  os.unlink(filepath)
  db.session.execute(text('delete from photo where id = ' + str(photo_id)))
  db.session.commit()
  
  flash('Photo id %s Successfully Deleted' % photo_id)
  return redirect(url_for('main.homepage'))

#########################
##### Added
#########################

# Stub for user only content.
# Could display all photos uploaded by the user.
@main.route('/profile')
@login_required
def profile():
  # return render_template('profile.html', name=current_user.name)
  photos = db.session.query(Photo).filter_by(name = current_user.name).order_by(asc(Photo.file))
  return render_template('index.html', photos = photos)


# Catches all server errors, prevents stack trace generation.
#@main.errorhandler(Exception)
#def http_error_handler(e):
#  print(e)  # TODO Replace with logger
#  return redirect(url_for('main.homepage'))

#########################
####### Comments Feature
#########################
#@main.route('/photo/<int:photo_id>/comment/')
#def photo_detail(item_id):
#  photo = Photo.query.get_or_404(item_id)
#  comments = Comment.query.filter_by(item_id=item_id).all()
#  return render_template('photo_detail.html', photo=photo, comments=comments)

##### Comment stuff

  # TODO Should this become a function?
  # return db.session.query(Photo).filter_by(id = photo_id).one()

# TODO role based access control?
@main.route('/photo/<int:photo_id>/comment/', methods=['GET','POST'])
@login_required
def commentNew(photo_id):
  photo = db.session.query(Photo).filter_by(id = photo_id).one()
  if request.method == 'POST':
    new_comment = Comment(text = request.form['text'], 
                          photo_id = photo_id, 
                          user_id = current_user.id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('main.commentShow', photo_id = photo_id))
  else:
    # TODO implement the html template
    # return render_template('commentNew.html', photo = photo)
    # Redirect stub for the moment
    return redirect(url_for('main.commentShow', photo_id = photo_id))

# TODO role limitations?
@main.route('/photo/<int:photo_id>/comment/<int:comment_id>/edit', methods=['GET','POST'])
@login_required
def commentEdit(photo_id, comment_id):
  # photo = db.session.query(Photo).filter_by(id = photo_id).one()
  comment = Comment.query.filter_by(id = comment_id).first()
  if not (current_user.id == comment.user_id):
    return redirect(url_for('main.commentShow', photo_id = photo_id))
  if (request.method == 'POST' and request.form['text']):
    comment.text = request.form['text']
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('main.commentShow', photo_id = photo_id))
  else:
    # TODO render edit comment interface
    x= 5

# TODO role limitations
@main.route('/photo/<int:photo_id>/comment/<int:comment_id>/delete', methods=['GET','POST'])
@login_required
def commentDelete(photo_id, comment_id):
  comment = Comment.query.filter_by(id = comment_id).first()

  if not (current_user.id == comment.user_id):
    return redirect(url_for('main.commentShow', photo_id = photo_id))
  if (request.method == 'POST'):
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('main.commentShow', photo_id = photo_id))
  else:
    # TODO render delete comment interface
    x= 5


@main.route('/photo/<int:photo_id>/comment/all')
def commentShow(photo_id):
  photo = db.session.query(Photo).filter_by(id = photo_id).one()
  comment_thread = Comment.query.filter_by(photo_id = photo_id).all()
  # TODO render comment html (photo_id, comment_thread)
  return render_template('commentShow.html',photo = photo,comments=comment_thread)

#########################
