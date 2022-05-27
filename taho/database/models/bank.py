from email.policy import default
from typing import Any
from tortoise.models import Model
from tortoise import fields

__all__ = (
    "Bank",
    "BankInfo",
    "BankAccount",
    "BankOperation"
)

class Bank(Model):
    class Meta:
        table = "banks"

    id = fields.IntField(pk=True)
    
    cluster = fields.ForeignKeyField("main.GuildCluster", related_name="banks")
    user = fields.ForeignKeyField("main.User", related_name="banks")
    name = fields.CharField(max_length=255)
    emote = fields.CharField(max_length=255)

    infos: fields.ReverseRelation["BankInfo"]
    operations: fields.ReverseRelation["BankOperation"]
    accounts: fields.ReverseRelation["BankAccount"]

    async def get_info(self, key: str) -> Any:
        async for info in self.infos:
            if info.key == key:
                return info.value
        return None

class BankInfo(Model):
    class Meta:
        table = "bank_infos"

    id = fields.IntField(pk=True)

    bank = fields.ForeignKeyField("main.Bank", related_name="infos")
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

class BankAccount(Model):
    class Meta:
        table = "bank_accounts"

    id = fields.IntField(pk=True)

    bank = fields.ForeignKeyField("main.Bank", related_name="accounts")
    user = fields.ForeignKeyField("main.User", related_name="accounts")
    balance = fields.DecimalField(max_digits=32, decimal_places=2, default=0)
    is_default = fields.BooleanField(default=False)

    operations: fields.ReverseRelation["BankOperation"]

class BankOperation(Model):
    class Meta:
        table = "bank_operations"

    id = fields.IntField(pk=True)

    bank = fields.ForeignKeyField("main.Bank", related_name="operations")
    account = fields.ForeignKeyField("main.BankAccount", related_name="operations")
    amount = fields.DecimalField(max_digits=32, decimal_places=2)
    type = fields.CharField(max_length=255, default="transfer")
    date = fields.DatetimeField(auto_now_add=True)
    description = fields.CharField(max_length=255, default="")