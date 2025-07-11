Library
=======

The module :py:mod:`ansys.scade.wux.wux` contains helpers for generating code.

It also maintains global instances of WrapGen API classes that give access
to the C generated code mapping file data, or the C root operators interfaces.

A set of functions allows generation services to declare resources for the
makefile:

* Source files
* Include directories
* Object files or libraries
* Preprocessor definitions

.. Note::

  The :py:data:`mf <wux.mf>`, :py:data:`mh <wux.mh>` and
  :py:data:`ips <wux.ips>` variables are initialized by the
  :ref:`usage/services:Context` generation service. They remain uninitialized
  if this service is not explicitly requested by a wrapper.
