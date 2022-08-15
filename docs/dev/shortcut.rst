:orphan:

.. currentmodule:: taho
.. _shortcut:

Understand Shortcuts
=====================

**Shortcuts** are a way to implement Polymorphic Relations
with Tortoise-ORM.
Shortcuts can be used as a ForeignKey in a model and can be 
created (or retrieved) with the :func:`~taho.database.utils.create_shortcut` function.

There are different types of shortcuts:

StuffShortcut
--------------

    A shortcut to :class:`~taho.abc.StuffShortcutable`
    models.
    Used for rewards/costs of crafts, jobs...
    It points to everythings that can be earned and stored.

OwnerShortcut
--------------

    A shortcut to :class:`~taho.abc.OwnerShortcutable`
    models.
    Used to define banks/shops owners and for inventories.
    It points to everythings that can be able to 
    own something.

AccessRuleShortcut
--------------- 

    A shortcut to :class:`~taho.abc.AccessRuleShortcutable`
    models.
    Used to define access to something.
    It points to everythings that can have access 
    to a system, things that receive permissions.

TradeStuffShortcut
-------------------

    A shortcut to :class:`~taho.abc.TradeStuffShortcutable`
    models.
    Used to define traded stuff (in a 
    :class:`~taho.database.models.Trade`).
