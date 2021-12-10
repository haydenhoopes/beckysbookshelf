Becky's Bookshelf
========================================


### SET UP
Install the virtualenv package: 

    py -m pip install --user virtualenv


Enter this command after going to the project directory: 

    py -m venv env


This will create the env folder with all of the information.


### USING VENV
Use this command to start using your virtual environment:

Git bash/Mac: 

    source ./env/Scripts/activate


Windows: 

    .\env\Scripts\activate


You can check that you are using your virtual environment with this command: 

    which python
    
When you finish using the virtual environment, you can deactivate it with this command:

    deactivate


### RUN SERVER
Use this command to start the django server: 

    python beckysbookshelf/manage.py runserver

Or this command:

    django-admin runserver


### INSTALLING PACKAGES FROM REQUIREMENTS
Use this command to install the required project dependencies from the requirements file:

    pip install -r requirements.txt


### ADDING MODULES
Make sure that you use the following command to store the packages that you install as
project dependencies before you push up changes.

    pip freeze > requirements.txt

## Using Git
### Pulling in changes other people have made
Every so often you should run this command to get the latest version of code.

    git pull
    
Sometimes you will get an error called a merge conflict, which occurs when several people have edited the same lines of code. You will be presented with both versions (yours and the repository's) and will need to decide what to keep.

### Pushing your changes to the repository
You need to pull before you push up changes to the repository.
To push up changes, first add files to the staging area. You can specify a file(s) or you can add all of the files you've worked on with a period:

    git add .

Or

    git add <<filename>>

After adding to the staging area, create a commit which will box up the changes and add a message describing what you did. The message is followed by the -m flag.

    git commit -m "Added git essentials to the README document"

Then push up changes

    git push

### Other git commands
You can see what is going on in your git repository (which files are in the staging area, see if your local code is up to date with the GitHub code) using the following command:

    git status

Bugs to hayden.hoopes@aggiemail.usu.edu
