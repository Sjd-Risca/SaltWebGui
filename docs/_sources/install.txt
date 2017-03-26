.. index:: Installation

.. |br| raw:: html

   <br />

============
Installation
============

For running SaltWebGui it is recommended to use **virtualenv** in order to satisfy the dependencies (see `Virtualenv`_).
|br|
It is also required an access to the **salt-api** (see `Saltstack requirements`_ for further explanation).

The components involved are:

- a web server (where to run SaltWebGui)
- a salt-master with accessible salt-api

It is possible to deploy the SaltWebGui's web server on the salt-master itself (in this case the salt-api can be kept private on localhost)
or to have them on different server. In the latter be careful the salt-api is made accessible to the web-server: if it is widely accessible use a proper ssl encryption.

Here follows the installation requirements, then an example for `Quick installing for testing`_ and a `Reference for production installation`_.

------------
Requirements
------------

Analysis of minimum requirements for running SaltWebGui.

- `Saltstack requirements`_: minimum configuration for salt and its salt-api
- `Virtualenv`_: python dependency installation

Saltstack requirements
++++++++++++++++++++++

In order to use SaltWebGui it is required to enable **salt-api** on the salt master.

For example on a debian distro just install salt-api with

.. code:: bash

  aptitude install salt-api

Then enable the salt-api module through the *salt-master*'s configuration file. Here a quick example suitable for local test (not safe for production)::

  rest_cherrypy:
      disable_ssl: True
      host: 127.0.0.1
      port: 8000

And set-up proper user permission (here enable system user *mylinuxuser*)::

  external_auth:
      pam:
          mylinuxuser:
              - ".*"
              - "@runner"
              - "@wheel"

.. role:: bash(code)
   :language: bash

The *mylinuxuser* has to be a system user (it is possible to create a custom one with :bash:`adduser mylinuxyser`).

.. note::
  In order to use SaltWebGui an authentication method is required. At the time of writing saltstack supports both pam and LDAP, see the `eauth manual`_.

.. _`eauth manual`: https://docs.saltstack.com/en/latest/topics/eauth/index.html


Virtualenv
++++++++++

On a Debian system at least the following packages are required::

  aptitude install libmysqlclient-dev python-dev libffi-dev gcc

For using a virtualenv locally run

.. code:: bash

  cd SaltWebGui
  virtualenv ./venv
  source venv/bin/activate
  pip install -r requirements.txt

Now it's possible to launch SaltWebGui from cli, like::

  FLASK_APP=./wsgi.py flask run

----------------------------
Quick installing for testing
----------------------------

This is a quick reference for having a debuggable installation for tests.
I'd recommend to install it on salt-master (and access from an ssh tunnel) or to install it locally on you system and access the salt-api through a tunnel.
Here I'll try the latter.

On salt-master:

1. install salt-api

   .. code:: bash

     aptitude install salt-api
#. enable salt-api adding the following configuration in :code:`/etc/salt/master` adding the following options::

      rest_cherrypy:
          disable_ssl: True
          host: 127.0.0.1
          port: 8000
      external_auth:
          pam:
              mylinuxuser:
                  - ".*"
                  - "@runner"
                  - "@wheel"

#. add *mylinuxuser*:

   .. code:: bash

     adduser mylinuxuser
#. restart the salt-master:

   .. code:: bash
   
     service salt-master restart

On your system:

1. clone the repository

   .. code:: bash

     git clone https://github.com/SoftwareWorkersSrl/SaltWebGui.git
#. install minimum required packages for pip dependency:
   
   .. code:: bash
   
     aptitude install libmysqlclient-dev python-dev libffi-dev gcc
#. set-up the virtualenv
   
   .. code:: bash
   
     cd saltwebgui
     virtualenv ./venv
     source venv/bin/activate
     pip install -r requirements.txt
   
#. if the salt-api is not publicly accessible start an SSH tunnel
   
   .. code:: bash
   
     ssh -L 8000:127.0.0.1:8000 -o ServerAliveInterval=30 sshuser@saltmasterurl

#. start flask (by default it will be accessible on localhost at port *5000*):

   .. code:: bash
   
     cd saltwebgui
     source venv/bin/activate
     FLASK_APP=./wsgi.py flask run

.. warning::
  
  When deploying SaltWebGui, if deploying for production, be careful to properly secure enough the system!

  Set SSL protection on both the salt-api and the SaltWebGui, and don't forget to use an enough secure password for the salt user.

-------------------------------------
Reference for production installation
-------------------------------------

Sorry but this section is still to be implemented.

While waiting for more documentation, I'd suggest to user a WSGI server for running SaltWebGui (use the one that you prefer). Please also do not use the debug mode in production because of its security concerns.
