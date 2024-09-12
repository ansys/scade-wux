Library
=======

The module ``ansys.scade.wux.wux`` contains helpers for generating code.
It also provides a global instance of the class ``Wux``, called ``wux``,
used in particular to gather and share makefile data:

* Source files
* Include directories
* Object files

.. TODO: link to the API reference

The class ``Wux`` gives access to the KCG mapping file API and to all the source files, libraries and search include directories declared by the module's generation services.

.. code-block:: python

  class Wux:
      def __init__(self):
          # context
          mf: MappingFile = None
          mh: MappingHelpers = None
          ips: List[InterfacePrinter] = []

          # generated C files, for makefile
          self.sources: set[str] = []
          # build
          self.libraries: set[str] = []
          self.includes: set[str] = []
          self.definitions: set[str] = []

.. Note:

  The variables ``mf``, ``mh`` and ``ips`` are initialized by the
  generation service ``WUX_CTX``. They remain uninitialized if this service
  is not explicitly requested by a wrapper.


.. code: python

  sctoc.add_c_files(files, False, 'WUX')

Use the dependency ``WUX`` to declare a new target containing the sources from
the generation services, either generated ones or runtime files.
