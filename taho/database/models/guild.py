from typing import Any
from tortoise.models import Model
from tortoise import fields
from .user import User
from .bank import Bank

__all__ = (
    "GuildCluster",
    "Guild",
    "ClusterInfo",
    "GuildInfo"
)

class GuildCluster(Model):
    class Meta:
        table = "guild_clusters"
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255)

    infos: fields.ReverseRelation["ClusterInfo"]
    guilds: fields.ReverseRelation["Guild"]
    users: fields.ReverseRelation["User"]
    banks: fields.ReverseRelation["Bank"]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        
    async def get_info(self, key: str) -> Any:
        async for info in self.infos:
            if info.key == key:
                return info.value
        return None
    # Defining ``__str__`` is also optional, but gives you pretty
    # represent of model in debugger and interpreter
    def __str__(self):
        return self.name

class Guild(Model):
    class Meta:
        table = "guilds"
    
    id = fields.BigIntField(pk=True)
    cluster = fields.ForeignKeyField("main.GuildCluster", related_name="clusters")

    infos: fields.ReverseRelation["GuildInfo"]

    async def get_info(self, key: str) -> Any:
        async for info in self.infos:
            if info.key == key:
                return info.value
        return await self.cluster.get_info(key)

class ClusterInfo(Model):
    class Meta:
        table = "cluster_infos"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.GuildCluster", related_name="infos")
    key = fields.CharField(max_length=255)
    type = fields.CharField(max_length=255)
    value = fields.CharField(max_length=255)

    def __str__(self):
        return f"{self.key} : {self.value} ({self.type})"
    
    @property
    def py_value(self) -> Any:
        if self.type == "int":
            return int(self.value)
        elif self.type == "float":
            return float(self.value)
        elif self.type == "bool":
            return bool(self.value)
        elif self.type == "list":
            return list(self.value)
        else:
            return self.value

class GuildInfo(Model):
    class Meta:
        table = "guild_infos"

    id = fields.IntField(pk=True)

    guild = fields.ForeignKeyField("main.Guild", related_name="infos")
    key = fields.CharField(max_length=255)
    type = fields.CharField(max_length=255)
    value = fields.CharField(max_length=255)

    def __str__(self):
        return f"{self.key} : {self.value} ({self.type})"
    
    @property
    def py_value(self) -> Any:
        if self.type == "int":
            return int(self.value)
        elif self.type == "float":
            return float(self.value)
        elif self.type == "bool":
            return bool(self.value)
        elif self.type == "list":
            return list(self.value)
        else:
            return self.value