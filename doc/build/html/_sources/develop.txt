.. index:: development, architecture

=============================
Development and contributions
=============================

Push requests are welcome
+++++++++++++++++++++++++
Yep, this project is under active development!

Any contribution is welcome, please push against the *develop* branch.
If you are developing special features that required heavy and custom changes create a custom branch.

Found a bug? Fill the `issue`_ on github.

.. _`issue`: https://github.com/SoftwareWorkersSrl/SaltWebGui/issues

Coding style
++++++++++++
Try to be conformed where possible to PEP8. If need help while using *VIM* I'd recommend the use of `syntastic`_.

.. _`syntastic`: https://github.com/vim-syntastic/syntastic

Principles
++++++++++

SaltWebGui is based on the python framework Flask.

By now all of the data are stored in custom variables or classes. This is valid for user management as well as for the data received from saltstack.

The first demo of the code was using directly the CLI (there is still a legacy code available under *saltwebgui/sat/salt_binding.py*), but now it is preferred to user the salt-api.
This way is possible to run SaltWebGui on any server as long as there is an access to salt's api.

The current implementation uses the python `pepper`_ module in order to bind to saltstack.
For quick references under *saltwebgui/salt/views.py* are available some the following objects to interact with saltstack:

- JOBS = Jobs()
- JOB = Job()
- KEYS = Keys()
- RUN = Run()

The web interface is developed with bootstrap (and little of javascript code).

.. _`pepper`: https://github.com/saltstack/pepper
