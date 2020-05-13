Welcome to DAX's documentation!
===============================

DAX is Distributed Automation for `XNAT <http://xnat.org/>`_

DAX allows you to:

- store analyzed imaging data on XNAT (datatypes)
- extract information from XNAT via scripts (Xnat_tools)
- run pipelines on your data in XNAT via a cluster (processors)


Installation
------------

Install the latest release with `pip <https://pypi.org/project/pip/>`_:

.. code::

   pip install dax
   dax setup
   XnatCheckLogin --host http://129.59.135.143:8080/xnat
   # When prompted, enter user/pwd combination
   # Yes to use as default host

Contents:

.. toctree::
   :maxdepth: 3
   
   dax_xnat_dataypes_install
   dax
   dax_manager
   contributors
   how_to_contribute
   faq
   processors
   assessors_in_vuiis_xnat
   dax_command_line_tools
   dax_executables
   installing_dax_in_a_virtual_environment
   manage_a_project
