#!/usr/bin/python

r'''
Locking semantics:

basedir: Exclusive required to cleanup, shared required for iteration
per-artifact: Exclusive required for creation/deletion, shared for compose
Once 
'''

__version__ = '0.0.0'
