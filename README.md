doodleAlloc
===========

This project implements a simple web service to allocate persons to tasks based on a doodle (or alike).

As of now, each person gets a single task, but a task may not be allocated.
This can be used to allocated exam slots, seminar topics etc.

The web service uses flask and can be served via wsgi.

The data source must be some kind of doodle service for which a loader is implemented.
As of now, loaders are implemented for `doodle.com` and `terminplaner2.dfn.de`.

The allocation is calculated using pulp, a python lp solver.
