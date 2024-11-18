@echo off

REM Activate the hatch environment and run the Django server
hatch run default:py testproject/manage.py runserver
