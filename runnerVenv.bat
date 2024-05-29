@echo ####################
@echo Running app in virtual environment
@echo No safety checks are implemented, ensure ./env exists
@echo ####################

call env\Scripts\activate

@echo Should be in (env) now
@echo on
echo off

python run.py

cmd -k