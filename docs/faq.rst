FAQ
===

These FAQs assume that you have read the XNAT documentation and or are familiar with navigating through the web UI.
If you are not, you can read the XNAT documentation `here <https://wiki.xnat.org/display/XNAT16/Home/>`_.

#. What is DAX?
    DAX is an open source project that uses the pyxnat wrapper for the REST api to automate pipeline running on a DRMAA compliant grid.

#. What are Modules?
    Modules are a special class in DAX. They represent, generally, a task that should not be performed on the grid. The purpose for this was to not fill up the grid queue with jobs that take 20-30 seconds. Examples of such tasks could be converting a DICOM to a NIfTI file, changing the scan type, archiving a session from the prearchive, or performing skull-stripping. As you can see, these tasks can all be considered "light-weight" and thus probably don't have a place on the grid.

#. What are Spiders?
    Spiders are a python script. The purpose of the script is to download data from XNAT, run an image processing pipeline, and then prepare the data to be uploaded to XNAT. Spiders are run on the grid because they can take hours to days.

#. How do I know the EXACT command line call that was made?
    The PBS resource contains the script that was submitted to the grid scheduler for execution. You can view this file for the exact command line call(s) that were executed on the grid.

#. I think I found a bug, what should I do?
    The easiest way to get a bug fixed is to post as much information as you can on the `DAX github issue tracker <https://github.com/VUIIS/dax/issues>`_. If possible, please post the command line call you made (with any sensitive information removed) and the stack trace or error log in question.

#. I have an idea of something I want to add. How do I go about adding it?
    Great! We'd love to see what you have to include! Please read the guidelines on how to contribute.
