=================
Supervisor celery
=================

Description
===========

Adds support for running Celery with ``celery multi`` command to Supervisor_.

It brings new commands such as ``cmstart``, ``cmstop`` and ``cmrestart`` to launch the processes with Celery multi_


Example
=======

::

  supervisor> status
  celery-a                                RUNNING    pid 15085, uptime 0:00:11
  celery-b                                RUNNING    pid 15086, uptime 0:00:12
  gunicorn-a                              RUNNING    pid 14151, uptime 0:05:18
  gunicorn-b                              RUNNING    pid 14237, uptime 0:04:45
  supervisor> mstop *-a
  celery-a: stopped
  gunicorn-a: stopped
  supervisor>

Installation
============

::

  pip install supervisor-celery

And then add into your supervisor.conf:

::

  [ctlplugin:celerymulti]
  supervisor.ctl_factory = supervisorcelery.controllerplugin:make_celerymulti_controllerplugin

Changelog
=========

 * 0.1.0

    * Add project skeleton

.. _Supervisor: http://supervisord.org/
.. _Celery multi: http://docs.celeryproject.org/en/latest/reference/celery.bin.multi.html
