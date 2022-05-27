from tortoise.models import Model
from tortoise import fields
from .bank import Bank, BankAccount


__all__ = (
    "User",
)

class User(Model):
    class Meta:
        table = "users"
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    name = fields.CharField(max_length=255)
    cluster = fields.ForeignKeyField("main.GuildCluster", related_name="users")

    banks: fields.ReverseRelation["Bank"]
    accounts: fields.ReverseRelation["BankAccount"]

    # Defining ``__str__`` is also optional, but gives you pretty
    # represent of model in debugger and interpreter
    def __str__(self):
        return self.name