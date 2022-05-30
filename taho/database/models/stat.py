from tortoise.models import Model
from tortoise import fields
from enum import IntEnum

__all__ = (
    "RPEffect",
    "RegenerationType",
    "Stat",
)

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

class Stat(Model):
    class Meta:
        table = "stats"

    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.GuildCluster", related_name="stats")
    name = fields.CharField(max_length=255)
    emoji = fields.CharField(max_length=255, null=True)
    rp_effect = fields.IntEnumField(RPEffect, null=True)
    maximum = fields.IntField(null=True)
    regeneration = fields.IntEnumField(RegenerationType, default=RegenerationType.NO_REGENERATION)
    duration = fields.IntField(null=True)