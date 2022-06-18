from tortoise.models import Model
from tortoise import fields
from ..enums import RPEffect, RegenerationType

__all__ = (
    "Stat",
)



class Stat(Model):
    class Meta:
        table = "stats"

    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.ServerCluster", related_name="stats")
    name = fields.CharField(max_length=255)
    emoji = fields.CharField(max_length=255, null=True)
    rp_effect = fields.IntEnumField(RPEffect, null=True)
    maximum = fields.IntField(null=True)
    regeneration = fields.IntEnumField(RegenerationType, default=RegenerationType.NO_REGENERATION)
    duration = fields.IntField(null=True)