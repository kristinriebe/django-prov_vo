======================
Django prov_vo package
======================

**A prototype implementation of the IVOA Provenance Data Model**

.. image:: https://travis-ci.org/kristinriebe/django-prov_vo.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/kristinriebe/django-prov_vo

.. image:: https://coveralls.io/repos/github/kristinriebe/django-prov_vo/badge.svg?branch=master
   :alt: Coverage Status
   :target: https://coveralls.io/github/kristinriebe/django-prov_vo?branch=master

This package provides a resuable django application which is intended to be used within a Django project, see e.g. https://github.com/kristinriebe/provenance-rave/. It provides an implementation of the
IVOA Provenance Data Model (see http://www.ivoa.net/documents/ProvenanceDM/ for the latest version), with a REST API and a ProvDAL interface to retrieve the stored provenance metadata.


Installation
------------

* Download the package::

       git clone https://github.com/github/kristinriebe/django-prov_vo/

* Package the prov_vo app::

       cd django-prov_vo
       python setup.py sdist

* Switch to your main web application (or create it now with :code:`django-admin startproject <my_web_app>`)::

    cd ..
    cd <my_web_app>

  An example for a django project using this package is available at https://github.com/kristinriebe/provenance-rave

* Install the prov_vo app (e.g. inside your virtual environment) using pip::

    pip install ../django-prov_vo/dist/django-prov_vo-0.1.tar.gz

  Alternatively, you can also add the following lines in your projects's :code:`settings.py`::

    import sys
    sys.path.append('../django-prov_vo/')


* Add prov_vo to your INSTALLED_APPS setting in :code:`settings.py` like this::

    INSTALLED_APPS = [
        ...
        'prov_vo',
    ]

* Include the prov_vo URLconf in your project's urls.py like this::

    url(r'^prov_vo/', include('prov_vo.urls')),

* Install the requirements of this application, e.g. in a virtual environment::

    virtualenv -p /usr/bin/python2.7 env
    source env/bin/activate

    cd django-prov_vo
    pip install -r requirements.txt

* Run :code:`python manage.py migrate` to update the database and create the provenance models.

* Start the development server and open a browser with http://127.0.0.1:8000/prov_vo/. You should see now a page with some introductory words and links to forms, activity lists etc.

Have fun! :-)


Testing
-----------

* This django application can be tested standalone, outside the project. First create a virtual environment and install the required python (2.7) packages::

    virtualenv -p /usr/bin/python2.7 env
    source env/bin/activate

    pip install -r requirements.txt

* Now switch to prov_vo and run::

    cd prov_vo
    python runtests.py

* This runs all the tests stored in :code:`tests`.


TODO
----

* Fix REST API: create new activities etc. (datetime format problem), allow data update (PUT)

* Proper error handling
* Move print-statements to error/debug log
* Write tests for checking all the functionality
* Use MySQL database/remote database instead of Sqlite3
* check code coverage
* write extended documentation
* publish as PyPi package

* Implement xml serialization, votable serialization, for REST api and for Prov-DAL endoint
* Implement "description" classes, i.e. ActivityDescription etc. (if needed)
* Find a better way to visualize activityFlow, collection, detail/basic etc.
* Add VOSI interface, for ProvDAL
