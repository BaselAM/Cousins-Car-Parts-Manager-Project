"""Alias module of `OpenGL.GL`_ of `pyglm`.

Instead of:

.. code-block:: python

   import glm

You do:

.. code-block:: python

   from mt import glm

It will import the `pyglm` and provide some additional, mostly svd-related, functions that MT has
written.

Please see Python package `pyglm`_ for more details.

.. _pyglm:
   https://github.com/Zuzu-Typ/PyGLM
"""


try:
    from glm import *
except ImportError:
    raise ImportError("Alias 'mt.glm' requires package 'pyglm' be installed.")


from .linear import *
