Installation
============

From GitHub
###########
 - Clone the repository with ``git clone https://github.com/nwithan8/dizqueTV-python.git``
 - Enter project folder with ``cd dizqueTV-python``
 - Install requirements with ``pip install -r requirements.txt``


From PyPi
#########
 - Run ``pip install dizqueTV``

Setup
============
Import the ``API`` class from the dizqueTV module

.. code-block:: python

    from dizqueTV import API
    dtv = API(url="http://localhost:8000")

Enable verbose logging by passing ``verbose=True`` into the API object declaration