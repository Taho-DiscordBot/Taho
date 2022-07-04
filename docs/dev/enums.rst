.. currentmodule:: taho.enums

Enums
===========================


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


ItemType
~~~~~~~~~

.. class:: ItemType

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

.. class:: ItemReason

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

.. class:: ItemUse

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

.. class:: SalaryCondition

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

.. class:: RewardType

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

.. class:: RoleType

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

RegenerationType
~~~~~~~~~~~~~~~~~

.. class:: RegenerationType

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

.. class:: RPEffect

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