.. currentmodule:: taho.database.models

Database models
===========================

All the models from the database.


.. note::

    All these models are inherited from the Tortoise-ORM's base :tdocs:`Model <models.html>`.
    So you can use all the methods from the base model.

Model
~~~~~~
.. autoclass:: tortoise.models.Model
    :members:


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

ServerChannel
~~~~~~~~~~~~~~
.. autoclass:: ServerChannel()
    :members:
    :exclude-members: Meta

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
    :private-members:
    :exclude-members: Meta

BankingTransaction
~~~~~~~~~~~~~~~~~~~
.. autoclass:: BankingTransaction()
    :members:
    :exclude-members: Meta

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

JobCost
~~~~~~~~~~
.. autoclass:: JobCost()
    :members:
    :exclude-members: Meta


Item
~~~~~
.. autoclass:: Item()
    :members:
    :exclude-members: Meta, save


ItemStat
~~~~~~~~~
.. autoclass:: ItemStat()
    :members:
    :exclude-members: Meta

Inventory
~~~~~~~~~~
.. autoclass:: Inventory()
    :members:
    :exclude-members: Meta, save

Hotbar
~~~~~~~
.. autoclass:: Hotbar()
    :members:
    :exclude-members: Meta


Role
~~~~~
.. autoclass:: Role()
    :members:
    :exclude-members: Meta

.. autoclass:: ServerRole()
    :members:
    :exclude-members: Meta

Stat
~~~~~
.. autoclass:: Stat()
    :members:
    :exclude-members: Meta

Class
~~~~~~
.. autoclass:: Class()
    :members:
    :exclude-members: Meta

ClassStat
~~~~~~~~~~
.. autoclass:: ClassStat()
    :members:
    :exclude-members: Meta

User
~~~~~
.. autoclass:: User()
    :members:
    :exclude-members: Meta

UserStat
~~~~~~~~~
.. autoclass:: UserStat()
    :members:
    :exclude-members: Meta

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

NPCMessage
~~~~~~~~~~~
.. autoclass:: NPCMessage()
    :members:
    :exclude-members: Meta
