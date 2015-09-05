planningpoker
=============

Planning poker web application - in Python 3.

https://en.wikipedia.org/wiki/Planning_poker

Status
------

.. image:: https://travis-ci.org/not-raspberry/planningpoker.svg?branch=master
    :target: https://travis-ci.org/not-raspberry/planningpoker


Intended features
=================

- No login required - as a moderator create a game and share the game URL with the players. Players
  don't need to login too. Anonymous sessions handle players' identity.
- Able to persist in memory (if you call it persistence), on Redis or in Postgres.
- Single-page-app frontend.

Progress
--------

The persistence backend is more or less established. It evolves along with its reference in-memory
storage implementation as the backend views are being implemented.

No frontend so far.

System requirements
===================

Currently supporting Python 3.4 and 3.4 only.

Python 3 header files are required to compile PyCrypto. Should be possible to obtain by installing
``python3-dev`` or ``python3-devel``.
