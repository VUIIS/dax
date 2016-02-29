DAX Installation
================

Table of Contents:
~~~~~~~~~~~~~~~~~~

1.  `Requirements <#requirements>`__
2.  `For Linux user <#for-linux-user>`__
3.  `For Mac user <#for-mac-user>`__
4.  `Warnings <#warnings>`__
5.  `Install dax <#install-dax>`__
6.  `For Linux user <#install-for-linux-user>`__
7.  `For Mac user <#install-for-mac-user>`__
8.  `No Sudo Access <#no-sudo-access>`__
9.  `Verify the installation <#verify-the-installation>`__
10. `Programming in python <#programming-in-python>`__

--------------

Requirements
------------

--------------

Requirements for DAX: \* Linux or MacOS operating system (has not been
tested on windows yet). \* Python installed with version 2.7.X \* git or
pip installed

To check that your python version is 2.7.X:

::

    python --version

--------------

For Linux user
~~~~~~~~~~~~~~

pip install
^^^^^^^^^^^

To install pip if you want/don't have it (optional):

::

    easy_install pip

git install
^^^^^^^^^^^

To install git if you don't have it:

::

    apt-get install git

--------------

For Mac user
~~~~~~~~~~~~

SVN install
^^^^^^^^^^^

If svn command doesn't exist on you mac, install xcode from the Apple
Store. Run it and go to Xcode -> Preferences -> Downloads -> Command
Line Tools -> Install. Now, you can use svn.

A quick way to check the installation of Xcode and command line
developer is to run:

::

    xcode-select --install

If it asks: "install requested for command line developer tools", do the
install.

pip install
^^^^^^^^^^^

To install pip, run:

::

    sudo easy_install pip

If you don't have easy\_install, follow the instructions on this link
https://pypi.python.org/pypi/setuptools .

git install
^^^^^^^^^^^

To Install git: on this link http://git-scm.com/downloads , click on the
Mac Os X button to download the package and install it.

--------------

Warnings
~~~~~~~~

Before starting with the different steps, if you see a 'Permission
denied' while trying to install the libraries, add sudo in front of the
command line. It will ask for your password. This will use the sudo
access (http://en.wikipedia.org/wiki/Sudo) when running the command line
and you will have the permission to install packages everywhere on your
computer.

If you don't have sudo access on your computer, follow the section No
Sudo access.

Previously all of the commonly used CLI tools (XnatSwitchProcessStatus,
Xnatupload, Xnatdownload, and Xnatinfo etc) were stored under
masimatlab. These versions are no longer maintained and the new versions
are part of DAX. If you get errors that your versions don't work, you
should check your PATH variable

::

    echo $PATH

If you see a reference to masimatlab/trunk/xnatspiders/Xnat\_tools, you
should remove this from your path so versions do not conflict. When you
install DAX, your environement is set for the new versions (but does not
make any changes to the old versions so you need to do this manually).

If you get any nasty traceback errors, you may be missing a required
module package. Below is an example:

::

    Traceback (most recent call last):
    File "/usr/local/bin/fsdownload", line 14, in <module>
      from dax import XnatUtils
    File "/Library/Python/2.7/site-packages/dax/__init__.py", line 3, in <module>
      from .launcher import Launcher
    File "/Library/Python/2.7/site-packages/dax/launcher.py", line 12, in <module>
      import processors
    File "/Library/Python/2.7/site-packages/dax/processors.py", line 4, in <module>
      import task
    File "/Library/Python/2.7/site-packages/dax/task.py", line 9, in <module>
      import XnatUtils, bin
    File "/Library/Python/2.7/site-packages/dax/bin.py", line 8, in <module>
      import redcap
    File "/Library/Python/2.7/site-packages/redcap/__init__.py", line 19, in <module>
      from .project import Project
    File "/Library/Python/2.7/site-packages/redcap/project.py", line 10, in <module>
      from .request import RCRequest, RedcapError, RequestException
    File "/Library/Python/2.7/site-packages/redcap/request.py", line 18, in <module>
      from requests import post, RequestException
    ImportError: No module named requests

In this case, the "requests" package is missing. To install, just run
"sudo pip install requests". If you get other import errors, they can
generally be fixed by running sudo pip install where package name is the
last word in the ImportError line.

--------------

Install DAX
-----------

--------------

Install for Linux user
~~~~~~~~~~~~~~~~~~~~~~

-  Install dax (Distributed Automation for XNAT) package:

With pip:

::

    sudo pip install dax
    #or 
    pip install https://github.com/VUIIS/dax/archive/master.zip --upgrade    
    #to get the last version of dax and not the version on pip

OR with git:

::

    git clone git://github.com/VUIIS/dax
    cd dax
    sudo python setup.py install

-  add the XNAT variables to your file ~/.xnat\_profile:

Run these commands:

::

    echo "export XNAT_USER=XXXXXXXX" >> ~/.xnat_profile
    echo "export XNAT_PASS=XXXXXXXX" >> ~/.xnat_profile
    echo "export XNAT_HOST=http://XXXXXXXXXXX" >> ~/.xnat_profile 

Replace the XXXXX by your personal information.

-  Last step, you need to check that the file .xnat\_profile is called
   in your .bash\_profile.

To do so, use the following command to see the content of your file
.bash\_profile:

::

    cat ~/.bash_profile

If you don't see the line "source ~/.xnat\_profile" or ".
~/.xnat\_profile", your configuration file is not linked to your
bash\_profile.

To do so, run:

::

    echo "source ~/.xnat_profile" >> ~/.bash_profile 

-  Apply the changes:

Run this command:

::

    . ~/.xnat_profile

You are ready to go.

--------------

Install for Mac user
~~~~~~~~~~~~~~~~~~~~

-  Install dax (Distributed Automation for XNAT) package:

With pip:

::

    sudo pip install dax
    # or 
    pip install https://github.com/VUIIS/dax/archive/master.zip --upgrade    
    #to get the last version of dax and not the version on pip

OR with git:

::

    git clone git://github.com/VUIIS/dax
    cd dax
    sudo python setup.py install

-  add the XNAT variables to your file ~/.xnat\_profile:

Run these commands:

::

    echo "export XNAT_USER=XXXXXXXX" >> ~/.xnat_profile
    echo "export XNAT_PASS=XXXXXXXX" >> ~/.xnat_profile
    echo "export XNAT_HOST=http://xnat.vanderbilt.edu:8080/xnat" >> ~/.xnat_profile 

Replace the XXXXX by your personal information.

-  Last step, you need to check that the file .xnat\_profile is called
   in your .bash\_profile.

To do so, use the following command to see the content of your file
.bash\_profile:

::

    cat ~/.bash_profile

If you don't see the line "source ~/.xnat\_profile" or ".
~/.xnat\_profile", your configuration file is not linked to your
bash\_profile.

To do so, run:

::

    echo "source ~/.xnat_profile" >> ~/.bash_profile 

-  Apply the changes:

Run this command:

::

    . ~/.xnat_profile

You are ready to go.

--------------

No Sudo access
~~~~~~~~~~~~~~

If you are not a sudoer on your computer (Linux or MacOS), you can still
install dax locally. You need to use git to clone the dax repository and
install it locally. Follow the steps below to process with the
installation:

::

    git clone git://github.com/VUIIS/dax
    cd dax
    python setup.py install --user

You will need to add the local folder of dax/Xnat\_tools executables to
your PATH:

-  For Linux: echo "export PATH=\ :sub:`/.local/bin:$PATH">>`/.bashrc

-  For MacOS: echo "export PATH=~/Library/Python/2.7/bin/:$PATH" >>
   ~/.profile

If you don't see a line like "source ~/.profile" or ". ~/.profile" (same
for .bashrc), your configuration file is not linked to your
bash\_profile. To do so, run:

::

    echo "source ~/.profile" >> ~/.bash_profile    
    # or for bashrc
    echo "source ~/.bashrc" >> ~/.bash_profile

Run your configuration file to apply the changes:

::

    . ~/.profile   
    #or for bashrc
    . ~/.bashrc

--------------

Verify the installation
-----------------------

If you want to be sure everything is installed, you can check running
those commands:

::

    XXXXXXXXX$ python
    Python 2.7.1 (r271:86832, Jul 31 2011, 19:30:53) 
    [GCC 4.2.1 (Based on Apple Inc. build 5658) (LLVM build 2335.15.00)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>>import httplib2
    >>>import lxml
    >>>import pyxnat
    >>>import redcap
    >>>import dax

If you don't have any error, the python packages are all installed
properly.

Now you can verify your logins by running:

::

    XnatCheckLogin

If you see '-->Good login', you are good to go.

You are ready to use the Xnat\_tools, dax executables or the spiders.

--------------

Programming in python
---------------------

All the Spiders/DAX package/Xnat\_tools are written in python.

'''Where can I learn how to program in python?''' If you want to learn
how to program in python, here are several links that could help you: \*
http://www.learnpython.org \* https://www.python.org \*
http://stackoverflow.com \* http://google.com

'''Where can I program in python?'''

-  You can use any text Editor that you like to program in python.
-  There is an extension for Eclipse for python development called
   pydev. Here is the link to install pydev on Eclipse and it explains
   how to create a script :
   http://www.rose-hulman.edu/class/csse/resources/Eclipse/eclipse-python-configuration.htm
-  Atom (https://atom.io) is a nice editor developed by the team who
   created github.

