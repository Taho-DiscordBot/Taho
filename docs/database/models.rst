.. currentmodule:: taho.database.models

Database models
===========================

All the models from the database.


Base Model
-----------

.. note::

    All these models are inherited from the Tortoise-ORM's base :tdocs:`Model <models.html>`.
    So you can use all the methods from the base model.

Model
~~~~~~
.. autoclass:: tortoise.models.Model
    :members:


Server & Cluster
-----------------

Cluster
~~~~~~~~
.. autoclass:: Cluster()
    :members:
    :exclude-members: Meta

ClusterInfo
~~~~~~~~~~~~
.. autoclass:: ClusterInfo()
    :members:
    :exclude-members: Meta

Server
~~~~~~~
.. autoclass:: Server()
    :members:
    :exclude-members: Meta

ServerInfo
~~~~~~~~~~~
.. autoclass:: ServerInfo()
    :members:
    :exclude-members: Meta


Financial sector
-----------------

Currency
~~~~~~~~~
.. autoclass:: Currency()
    :members:
    :exclude-members: Meta

Bank
~~~~~
.. autoclass:: Bank()
    :members:
    :exclude-members: Meta

BankInfo
~~~~~~~~~
.. autoclass:: BankInfo()
    :members:
    :exclude-members: Meta

BankAccount
~~~~~~~~~~~~
.. autoclass:: BankAccount()
    :members:
    :exclude-members: Meta

BankOperation
~~~~~~~~~~~~~~
.. autoclass:: BankOperation()
    :members:
    :exclude-members: Meta


Jobs
-----

Job
~~~~
.. autoclass:: Job()
    :members:
    :exclude-members: Meta

JobReward
~~~~~~~~~~
.. autoclass:: JobReward()
    :members:
    :exclude-members: Meta


Items
------

Item
~~~~~
.. autoclass:: Item()
    :members:
    :exclude-members: Meta

ItemStat
~~~~~~~~~
.. autoclass:: ItemStat()
    :members:
    :exclude-members: Meta

Inventory
~~~~~~~~~~
.. autoclass:: Inventory()
    :members:
    :exclude-members: Meta


Roles
------

Role
~~~~~
.. autoclass:: Role()
    :members:
    :exclude-members: Meta

Stats
------

Stat
~~~~~
.. autoclass:: Stat()
    :members:
    :exclude-members: Meta


Users
------

User
~~~~~
.. autoclass:: User()
    :members:
    :exclude-members: Meta

NPCs
-----

NPC
~~~~
.. autoclass:: NPC()
    :members:
    :exclude-members: Meta

NPCOwner
~~~~~~~~~
.. autoclass:: NPCOwner()
    :members:
    :exclude-members: Meta

NPCRole
~~~~~~~~
.. autoclass:: NPCRole()
    :members:
    :exclude-members: Meta
