.. image:: https://badge.fury.io/py/django-francedata.svg
    :target: https://pypi.org/project/django-francedata/

.. image:: https://github.com/entrepreneur-interet-general/django-francedata/actions/workflows/django.yml/badge.svg
    :target: https://github.com/entrepreneur-interet-general/django-francedata/actions/workflows/django.yml

.. image:: https://github.com/entrepreneur-interet-general/django-francedata/actions/workflows/codeql-analysis.yml/badge.svg
    :target: https://github.com/entrepreneur-interet-general/django-francedata/actions/workflows/codeql-analysis.yml


=================
Django-Francedata
=================

Provides a database structure, API and import scripts to manage French communes, intercommunalités, départements and régions, with their structure and data from Insee and the DGCL.

This app was created as a part of `Open Collectivités <https://github.com/entrepreneur-interet-general/opencollectivites>`_.

Unaccent extension
##################

If the PostgreSQL user specified in the Django settings is not a superuser, connect to the postgres user and create the Unaccent extension manually::

    psql
    \c <dbname>
    "CREATE EXTENSION  IF NOT EXISTS unaccent;"

Quickstart
##########

1. Add "francedata" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        "django_json_widget",
        "simple_history",
        "francedata",
    ]

2. Run ``python manage.py migrate`` to create the francedata models.

3. Run the two initialization commands to get the communes, EPCIs, départements and régions structure::

    python manage.py cog_import
    python manage.py banatic_import

4. Visit http://127.0.0.1:8000/admin/ to see the data.
  
Commands
########

cog_import:
***********

* goal: load the following data from the Code officiel géographique (COG): list of regions, departements and communes, with how they are linked and:
  * insee and siren ids for the regions/departements
  * insee for the communes
* parameters:
  * --level: partial import of only the specified level (the script expects the higher ones to already be installed) Allowed values: `regions`, `departements`, `communes`
  * --years: import the specified year (min: 2019), by default it imports the latest available one in https://www.data.gouv.fr/fr/datasets/code-officiel-geographique-cog/

banatic_import:
***************

* goal: load the following data from the Banatic:
  * siren ids and population data for the communes
  * insee for the communes
* The script expects that `cog_import` was already run and that the communes level is passed before the epci level.
* parameters:
  * --level: partial import of only the specified level. Allowed values: `communes`, `epci`
  * --years: import the specified year (min: 2019 for the communes level (data is taken from the file `Table de correspondance code SIREN / Code Insee des communes` from https://www.banatic.interieur.gouv.fr/V5/fichiers-en-telechargement/fichiers-telech.php ), by default it imports the latest available one)
* warning: The epci level only works for the current year (data is taken from https://www.data.gouv.fr/fr/datasets/base-nationale-sur-les-intercommunalites/ )
