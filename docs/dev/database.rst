.. currentmodule:: taho.database

.. |shortcutable| replace:: This model can be pointed by a :class:`.Shortcut`. See :ref:`Shortcuts <shortcut>` for more information.

Database
=========

All the documentation about Taho's Database.
Taho uses Tortoise-ORM.


.. currentmodule:: taho.database.models

Models
-------

All the models from the database.


.. note::

    All these models are inherited from the Tortoise-ORM's base :tdocs:`Model <models.html>`.
    So you can use all the methods from the base model.


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

CurrencyAmount
~~~~~~~~~~~~~~~
.. autoclass:: CurrencyAmount()
    :members:
    :inherited-members:
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

JobHistory
~~~~~~~~~~~
.. autoclass:: JobHistory()
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

UserPermission
~~~~~~~~~~~~~~~
.. autoclass:: UserPermission()
    :members:
    :exclude-members: Meta

UserInfo
~~~~~~~~~
.. autoclass:: UserInfo()
    :members:
    :exclude-members: Meta

UserRole
~~~~~~~~~
.. autoclass:: UserRole()
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

Craft
~~~~~~
.. autoclass:: Craft()
    :members:
    :exclude-members: Meta

CraftCost
~~~~~~~~~~
.. autoclass:: CraftCost()
    :members:
    :exclude-members: Meta

CraftReward
~~~~~~~~~~~~
.. autoclass:: CraftReward()
    :members:
    :exclude-members: Meta

CraftAccess
~~~~~~~~~~~~
.. autoclass:: CraftAccess()
    :members:
    :exclude-members: Meta

CraftHistory
~~~~~~~~~~~~~
.. autoclass:: CraftHistory()
    :members:
    :exclude-members: Meta

Shop 
~~~~~
.. autoclass:: Shop()
    :members:
    :exclude-members: Meta

Sale
~~~~~
.. autoclass:: Sale()
    :members:
    :exclude-members: Meta


.. currentmodule:: taho.database.utils

Utils
------

convert_to_type
~~~~~~~~~~~~~~~~
.. autofunction:: convert_to_type

get_type
~~~~~~~~~
.. autofunction:: get_type

create_shortcut
~~~~~~~~~~~~~~~~
.. autofunction:: create_shortcut

