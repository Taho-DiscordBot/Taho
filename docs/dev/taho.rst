
Taho Global
===============

THe following section outlines the module Taho.
This doesn't include taho's submodules (database, babel...).

.. currentmodule:: taho.abc

ABC
----

Shortcutable
~~~~~~~~~~~~~

.. autoclass:: Shortcutable()
    :members:

StuffShortcutable
~~~~~~~~~~~~~~~~~~

.. autoclass:: StuffShortcutable()
    :members:

OwnerShortcutable
~~~~~~~~~~~~~~~~~~

.. autoclass:: OwnerShortcutable()
    :members:

AccessShortcutable
~~~~~~~~~~~~~~~~~~~

.. autoclass:: AccessShortcutable()
    :members:

TradeStuffShortcutable
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: TradeStuffShortcutable()
    :members:

.. currentmodule:: taho.enums

Enums
------

InfoType
~~~~~~~~~

.. class:: InfoType

    |int_enum|
    
    The python's type of an info stored in
    the database.
    Used for :class:`~taho.database.models.ClusterInfo`,
    :class:`~taho.database.models.BankInfo` and
    :class:`~taho.database.models.ServerInfo`

    .. attribute:: NULL
    
        The info is a :class:`None` value.
    
    .. attribute:: BOOl

        The info is a :class:`bool` value.
    
    .. attribute:: INT

        The info is a :class:`int` value.
    
    .. attribute:: FLOAT
    
        The info is a :class:`float` value.
    
    .. attribute:: STR
    
        The info is a :class:`str` value.

ChannelType
~~~~~~~~~~~~

.. class:: taho.enums.ChannelType

    |int_enum|

    The type of a :class:`~taho.database.models.ServerChannel`.

    .. attribute:: roleplay
    
        The channel is a roleplay channel.
    
    .. attribute:: other
        
        The channel has no special type.


ItemType
~~~~~~~~~

.. class:: taho.enums.ItemType

    |int_enum|

    The type of an :class:`~taho.database.models.Item`.

    .. attribute:: resource
    
        The item is a resource.
    
    .. attribute:: consumable

        The item is a consumable.
    
    .. attribute:: equipment

        The item is an equipment.

ItemReason
~~~~~~~~~~~

.. class:: taho.enums.ItemReason

    |int_enum|

    The reason why a :class:`~taho.database.models.Role` / 
    :class:`~taho.database.models.Stat` linked to an 
    :class:`~taho.database.models.Item` is added to the 
    :class:`~taho.database.models.User`.

    .. attribute:: item_used
    
        The item has been used.
    
    .. attribute:: item_equiped

        The item has been equiped (in the hotbar).
    
    .. attribute:: item_in_inventory

        The item has been added to the inventory
        or is already in the inventory.

ItemUse
~~~~~~~~

.. class:: taho.enums.ItemUse

    |int_enum|

    When an :class:`~taho.database.models.Item` is used, 
    precises the type of use.

    .. attribute:: use
    
        The item is just used.
    
    .. attribute:: equip
    
        The item is equiped in the hotbar.
    
    .. attribute:: unequip
    
        The item is unequiped from the hotbar.
    
    .. attribute:: give

        The item is given to the user.

SalaryCondition
~~~~~~~~~~~~~~~~

.. class:: taho.enums.SalaryCondition

    |int_enum|

    The condition to be met for the salary of a
    :class:`~taho.database.models.Job` to be paid.

    .. attribute:: no_salary
    
        No salary is paid.
    
    .. attribute:: every_day

        The salary is paid every day.
    
    .. attribute:: every_day_if_worked
    
        The salary is paid every day if the user
        worked.
    
    .. attribute:: every_week

        The salary is paid every week.

    .. attribute:: every_week_if_worked

        The salary is paid every week if the user
        worked.

RewardType
~~~~~~~~~~~

.. class:: taho.enums.RewardType

    |int_enum|

    The type of :class:`~taho.database.models.JobReward` 
    given by a :class:`~taho.database.models.Job`.
    This enum is also used for :class:`~taho.database.models.JobCost`.

    .. attribute:: money
    
        The reward is money.
    
    .. attribute:: item

        The reward is an item.
    
    .. attribute:: stat

        The reward is a stat.

RoleType
~~~~~~~~~

.. class:: taho.enums.RoleType

    |int_enum|

    The type of a :class:`~taho.database.models.Role`.

    .. attribute:: default
    
        The role is the default rp role.
    
    .. attribute:: job

        The role is linked to a job.
    
    .. attribute:: class_

        The role is linked to a class.
    
    .. attribute:: other

        The role is not linked to any system
        of the bot, but it is still a rp role.

RoleAddedBy
~~~~~~~~~~~~

.. class:: taho.enums.RoleAddedBy
    
        |int_enum|
    
        By what a :class:`~taho.database.models.UserRole`
        was added to a :class:`~taho.database.models.User`.
    
        .. attribute:: admin
        
            The role was added intentionally by a Discord
            admin or with a command.
        
        .. attribute:: item
        
            The role was added due to the presence
            of an item in the inventory.
        
        .. attribute:: shop
            
            The role was added because of a shop purchase.

        .. attribute:: other
        
            The role is added by an unknown source. 

RegenerationType
~~~~~~~~~~~~~~~~~

.. class:: taho.enums.RegenerationType

    |int_enum|

    The type of regeneration of a :class:`~taho.database.models.Stat`.

    .. attribute:: no_regeneration
    
        The stat can't be regenerated.
    
    .. attribute:: no_regen

        Same as :attr:`~taho.enums.RegenerationType.no_regeneration`.
    
    .. attribute:: regeneration

        The stat is regenerated naturally.

    .. attribute:: regen

        Same as :attr:`~taho.enums.RegenerationType.regeneration`.
    
    .. attribute:: not_natural_regeneration

        The stat is regenerated, but not naturally.
    
    .. attribute:: not_natural_regen

        Same as :attr:`~taho.enums.RegenerationType.not_natural_regeneration`.
    
RPEffect
~~~~~~~~~

.. class:: taho.enums.RPEffect

    |int_enum|

    The effect in the roleplay of a :class:`~taho.database.models.Stat`.

    .. attribute:: no_effect
    
        The stat has no effect in the roleplay.
    
    .. attribute:: hp

        The stat is the hp of the user.
    
    .. attribute:: stamina

        The stat is the stamina of the user.
    
    .. attribute:: strength

        The stat is the strength of the user.
    
    .. attribute:: protection

        The stat is the protection of the user.
    
    .. attribute:: speed

        The stat is the speed of the user.
    
    .. attribute:: agility

        The stat is the agility of the user.
    
    .. attribute:: ability

        The stat is the ability of the user.

ShortcutType
~~~~~~~~~~~~~~

.. class:: taho.enums.ShortcutType

    |int_enum|

    The type of a :class:`~taho.database.models.Shortcut`.

    .. attribute:: item
    
        This shortcut goes to an :class:`~taho.database.models.Item`.
    
    .. attribute:: stat
    
        This shortcut goes to a :class:`~taho.database.models.Stat`.
    
    .. attribute:: currency
    
        This shortcut goes to a :class:`~taho.database.models.Currency`.
    
    .. attribute:: role

        This shortcut goes to a :class:`~taho.database.models.Role`.
    
    .. attribute:: user

        This shortcut goes to a :class:`~taho.database.models.User`.
    
    .. attribute:: inventory

        This shortcut goes to a :class:`~taho.database.models.Inventory`.

CraftAccessType
~~~~~~~~~~~~~~~~

.. class:: taho.enums.CraftAccessType

    |int_enum|

    The type of entity which have (or not) access 
    to a :class:`~taho.database.models.Craft`.

    .. attribute:: user
    
        The access is for a user.
    
    .. attribute:: role
    
        The access is for a role.

ShopType
~~~~~~~~~

.. class:: taho.enums.ShopType

    |int_enum|

    The type of a :class:`~taho.database.models.Shop`.

    .. attribute:: user
    
        The shop is a personnal shop of a :class:`~taho.database.models.User`.
    
    .. attribute:: admin
    
        The shop is created by a Server admin (the shop can have unlimited amounts).
    
    .. attribute:: shared
    
        The shop is shared between all users.