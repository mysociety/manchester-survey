This is the code to run a survey across mySociety sites in conjuction
with the University of Manchester

## Install instructions for Debian

Install necessary packages

    sudo apt-get update -y
    sudo apt-get upgrade -y
    sudo apt-get install -y $(cut -d " " -f 1 conf/packages | egrep -v "^#")

Install the project's requirements into a virtualenv

    virtualenv ~/virtualenv-manchester-survey
    source ~/virtualenv-manchester-survey/bin/activate
    pip install -r requirements.txt

Create a user and a database in postgres

    sudo -u postgres psql --command="CREATE USER questions WITH PASSWORD 'questions' CREATEDB;"
    sudo -u postgres psql --command='CREATE DATABASE questions OWNER questions;'

Add required configuration

    cp conf/general.yml-example conf/general.yml

- Edit MANSURV_DB_USER to be 'questions' in conf/general.yml
- Edit MANSURV_DB_NAME to be 'questions' in conf/general.yml
- Edit MANSURV_DB_PASS to be 'questions' in conf/general.yml
- Edit DJANGO_SECRET_KEY in conf/general.yml

Install gems and compile CSS

    sudo gem install --conservative --no-ri --no-rdoc compass zurb-foundation
    compass compile web
