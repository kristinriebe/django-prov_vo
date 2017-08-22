======================
Django prov_vo package
======================

This package is intended to be used with a Django web application, see e.g. github.com/kristinriebe/provenance-rave/. It is an implementation of the
IVOA Provenance Data Model: the data model classes
are implemented as Django models, a provenance data layer access
(ProvDAL) interface is also included.
Thus, provenance metadata can be stored and served in an VO-compatible way.


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

  An example for a web application using this package is available at https://github.com/kristinriebe/provenance-rave

* Install the prov_vo app (e.g. inside your virtual environment) using pip::

    pip install ../django-prov_vo/dist/django-prov_vo-0.1.tar.gz

  Alternatively, you can also add the following lines in your webapp's :code:`settings.py`::

    import sys
    sys.path.append('../django-prov_vo/')


* Add prov_vo to your INSTALLED_APPS setting in :code:`settings.py` like this::

    INSTALLED_APPS = [
        ...
        'prov_vo',
    ]

* Include the prov_vo URLconf in your project's urls.py like this::

    url(r'^prov_vo/', include('prov_vo.urls')),

* Run :code:`python manage.py migrate` to update the database and create the provenance models.

* Start the development server and open a browser with http://127.0.0.1:8000/prov_vo/. You should see now a page with some introductory words and links to forms, activity lists etc.

Have fun! :-)


TODO
----

* Fully implement new ProvDAL suggestions, along with optional extensions,
 + implement a version that is closer to what the users need

* Fix REST API: create new activities etc. (datetime format problem), allow data update (PUT)

* Proper error handling
* Write tests for checking all the functionality
* Use MySQL database/remote database instead of Sqlite3
* check code coverage
* write extended documentation
* publish as PyPi package

* Implement xml serialization, votable serialization, for REST api and for Prov-DAL endoint
* Implement "description" classes, i.e. ActivityDescription etc. (if needed)
* Find a better way to visualize activityFlow, collection, detail/basic etc.

