slacker-python
==============

.. image:: https://img.shields.io/pypi/v/slacker-python.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/slacker-python/
.. image:: https://img.shields.io/pypi/l/slacker-python.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/slacker-python/
.. image:: https://img.shields.io/pypi/pyversions/slacker-python.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/slacker-python/


Python client of the `slacker RPC <https://github.com/sunng87/slacker>`_.

This project is still working in progress.

Installation
------------

`pip install slacker-python`

Usage
-----

::

   from slacker.geventbackend import Client
   from slacker.proxy import Proxy

   c = Client("127.0.0.1:2104")
   p = Proxy(c, "slacker.example.api")

   ## remote function echo
   p.echo("hello")

   ## remote function rand-ints
   p.call("rand-ints", 40)


License
-------

This package is open sourced under MIT License.
