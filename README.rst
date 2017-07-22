======================
Django prov_vo package
======================

This package is an implementation of the
IVOA Provenance Data Model. The data model classes
are implemented as django models, a provenance data layer access
(ProvDAL) is also included.

This package can be used in a web application that
serves provenance data.

Installation
------------

1. Add "djvoprov" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'prov_vo',
    ]

2. Include the prov_vo URLconf in your project urls.py like this::

    url(r'^prov_vo/', include('prov_vo.urls')),

3. Run `python manage.py migrate` to update the database and create 
   the provenance models.

4. Start the development server and open a browser with http://127.0.0.1:8000/prov_vo/


