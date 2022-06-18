from enum import IntEnum

__all__ = (
    "ItemType",
    "ItemReason",
    "ItemUse",
    "SalaryCondition",
    "RewardType",
    "RoleType",
    "InfoType",
    "RPEffect",
)

class ItemType(IntEnum):
    RESOURCE = 0
    CONSUMABLE = 1
    EQUIPMENT = 2

class ItemReason(IntEnum):
    ITEM_USED = 1
    ITEM_EQUIPPED = 2
    ITEM_IN_INVENTORY = 3

class ItemUse(IntEnum):
    USE = 1
    EQUIP = 2
    UNEQUIP = 3
    GIVE = 4
    DEFAULT = 4

class SalaryCondition(IntEnum):
    """
    Represents the salary conditions of a job.
    """
    NO_SALARY = 0
    EVERY_DAYS = 1
    EVERY_DAYS_IF_WORKING = 2
    EVERY_WEEKS = 3
    EVERY_WEEKS_IF_WORKING = 4

class RewardType(IntEnum):
    """
    Represents the reward types of a job.
    """
    MONEY = 0
    ITEM = 1
    STAT = 2

class RoleType(IntEnum):
    DEFAULT = 0
    JOB = 1
    CLASS = 2
    OTHER = 3

class InfoType(IntEnum):
    NULL = 0
    BOOL = 1
    INT = 2
    STRING = 3
    FLOAT = 4

class RPEffect(IntEnum):
    """
    Represents the RP effects of a stat.
    """
    HP = 0
    ENDURANCE = 1
    STRENGTH = 2
    PROTECTION = 3
    SPEED = 4
    AGILITY = 5
    COMPETENCE = 6

class RegenerationType(IntEnum):
    """
    Represents the regeneration types of a stat.
    """
    NO_REGENERATION = 0
    REGENERATION = 1
    NOT_NATURAL_REGENERATION = 2

class UseType(IntEnum):
    USE = 1
    EQUIP = 2
    UNEQUIP = 3
    GIVE = 4
    DEFAULT = 4
