======================
Django prov-vo package
======================

This package is intended to be used with a Django web application, see e.g. github.com/kristinriebe/provenance-rave/. It is an implementation of the
IVOA Provenance Data Model: the data model classes
are implemented as Django models, a provenance data layer access
(ProvDAL) is also included.
Thus, provenance metadata can be stored and served in an VO-compatible way.


Installation
------------

* Download the package:
    git clone ...github.com/kristinriebe/django-prov-vo/

* Package the prov-vo app:

	.. code::
	cd django-prov-vo
	python setup.py sdist

* Switch to your main web application and install the prov-vo app (e.g. inside your virtual environment) using pip:

	.. code::
	cd ..
	cd <my_web_app>
	pip install ../django-prov-vo/dist/django-prov-vo-0.1.tar.gz 

    Alternatively, you can also add the following lines in your webapp's :code:`settings.py`:

    .. code:: python
    import sys
    sys.path.append('../django-prov-vo/')


* Add prov-vo to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'prov-vo',
    ]

* Include the prov-vo URLconf in your project urls.py like this::

    url(r'^prov-vo/', include('prov-vo.urls')),

* Run `python manage.py migrate` to update the database and create
   the provenance models.

* Start the development server and open a browser with http://127.0.0.1:8000/prov-vo/
You should see now an overview of further links to forms, activity lists etc.

Have fun! :-)

