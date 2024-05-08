@echo ####################
@echo This will set up a local virtual python environment at ./env
@echo press enter to continue or Ctrl + C to break.
@echo ####################
@pause

python -m venv %cd%/env

@echo Activating environment

call env\Scripts\activate

@echo now in Environment
pip install -r requirements.txt
@echo ####################
@echo Finished setup, dropping into command prompt.
@echo I reccommend setting up database using, if it hasn't been initialised yet.
@echo python initialise_db.py
@echo INFO: This prompt is running in the virtual environment.
@echo ####################
@pause

cmd -k