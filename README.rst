Weather bot
===========

For periodic tasks cron jobs are usually the first option.
While they are simple to use, they have several disadvantages.
This is clearly visible in the situation of debugging failed multi-stage tasks:

    - The logs of each step are not stored centrally
    - If a stage, other than the first stage, failed the cron job still shows it ran 'successfully'


To address these challenges workflow management platforms such as Airflow were developed.
Each task in Airflow is a Directed Acyclic Graph (DAG) that is executed with a certain
frequency. The DAGs and their logs are centrally stored and easily accessible via a UI.
This makes managaging periodic tasks and debugging DAGs simpler.

In this repo a simple three step DAG is made that sends the weather to your phone:

1. Retrieve the weather forecast for the location of your choice from OpenWeatherMap

2. Parse the JSON response from OpenWeatherMap to a text message (string)

3. Send the text message to a phone number via the Twilio API


============
Dependencies
============
This project has the following dependencies:

    - `Docker <https://www.docker.com/>`_
    - `Git LFS <https://git-lfs.github.com/>`_ to store the Basic World Cities Database csv from `SimpleMaps <https://simplemaps.com/data/world-cities>`_
    - `OpenWeatherMap <https://openweathermap.org/>`_ API
    - `Twilio <https://www.twilio.com/>`_ API

=====
Setup
=====

1. Download Docker `here <https://www.docker.com/products/docker-desktop>`__ and install it on your machine

2. Download Git LFS `here <https://git-lfs.github.com/>`__ or via brew:

.. code-block:: bash

   $ brew install git-lfs

2. Install Git LFS on your machine:

.. code-block:: bash

   $ sudo git lfs install --system --skip-repo

3. Clone the repo.
    If you have already cloned the repo before installing Git LFS, run the following to get all the *large files* (else only the pointers to the large files will be present on your machine):

.. code-block:: bash

   $ git lfs pull origin

4. Create the directories :code:`data` and :code:`secrets`

.. code-block:: bash

   $ mkdir data secrets

5. Create an account at `OpenWeatherMap <https://openweathermap.org/>`_.
    Generate an API key for their service and store it at the following location: :code:`secrets/OPEN_WEATHER_MAP_API_KEY.txt`

6. Follow the `Twilio SMS Python Quickstart <https://www.twilio.com/docs/sms/quickstart/python>`_ to:
    - Create a Twilio Account
        Each account has a unique 'Account SID' and 'Auth Token'. Store these values at :code:`secrets/TWILIO_ACCOUNT_SID.txt` and :code:`secrets/TWILIO_AUTH_TOKEN.txt`
    - Obtain a Twilio phone number
        Save your Twilio phone number at :code:`secrets/TWILIO_PHONE_NUMBER.txt`
        Do note that the receiver phone number should be `whitelisted <https://support.twilio.com/hc/en-us/articles/223180048-Adding-a-Verified-Phone-Number-or-Caller-ID-with-Twilio>`_ for trial accounts.

7. Configure your PostgreSQL database by creating the following files:
    - :code:`secrets/POSTGRES_DB.txt`
        Name of the PostgreSQL database. This is an arbitrary value provided by the user
    - :code:`secrets/POSTGRES_PASSWORD.txt`
        Password of the PostgreSQL database. This is an arbitrary value provided by the user. Do note that special characters in the text file should be url encoded!
        See the SQLAlchemy `documentation <https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls>`_ for more information on url encoding strings.
    - :code:`secrets/POSTGRES_USER.txt`
        Username of the PostgreSQL database. This is an arbitrary value provided by the user

8. Provide user-specific information:
    - Store the phone number that should receive the text messages at :code:`secrets/PERSONAL_PHONE_NUMBER.txt`
    - Provide the location for the weather forecast as an environment variable in the :code:`docker-compose.yaml`.
        It should be provided in the format 'city, ISO2 country code', e.g. 'The Hague, NL'. For an overview of ISO2 country codes see the `ISO 3166-1 alpha-2 <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_ wiki.
        Currently only large cities present in the Basic World Cities Database csv from SimpleMaps are supported. Providing smaller cities/villages not present in this overview will result into an error.


=========================
Get your weather forecast
=========================

Once the setup is completed we can launch the weatherbot.

.. code-block:: bash

   $ docker-compose up --build

The first time a text message will be sent immediately, but all subsequent messages will be sent on weekdays at 7 am.