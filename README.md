# Sabzbin back-end

_Pipenv have been used to install the environment_

Pipenv Installation
------------
Debian :

    $ sudo apt install pipenv

Fedora:

    $ sudo dnf install pipenv
    
FreeBSD:

    # pkg install py36-pipenv

Windows:

    # Google IT :)


 Automatically install required package
-----------

    $ pipenv sync
    
then:

    $ pipenv shell
    
 
Run Django Project
-----------------

    $ python manage.py makemigration
    $ python manage.py migrate
    $ python manage.py runserver 
    
Run Factory for Fake DATA
-----------------

    $ python manage.py fake_fact

swagger:
-----------------
    127.0.0.1:8000/swagger