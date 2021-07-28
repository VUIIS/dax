Welcome to DAX's documentation!
===============================

DAX is Distributed Automation for `XNAT <http://xnat.org/>`_

DAX allows you to:

- store analyzed imaging data on XNAT (datatypes)
- extract information from XNAT via scripts (Xnat_tools)
- run pipelines on your data in XNAT via a cluster (processors)


Versions and Installation
-------------------------

Our currently running versions of dax are:

- Dax 2 - 2.2.1 - As of July 8, 2021
  
  - Used for most purposes

- LDAX latest - 0.7.10 - As of October 7, 2020

  - Legacy Dax - Please use DAX 2
  
These can be verified with

::

  dax version
  # or 
  pip freeze | grep dax
  # or
  python3 -m pip freeze | grep dax

To install please reference our `Install Page <https://dax.readthedocs.io/en/latest/installing_dax_in_a_virtual_environment.html>`_

Contents:

.. toctree::
   :maxdepth: 3
   
   installing_dax_in_a_virtual_environment
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
   manage_a_project
   BIDS_walkthrough 
