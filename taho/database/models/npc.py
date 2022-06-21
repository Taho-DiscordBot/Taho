"""
The MIT License (MIT)

Copyright (c) 2022-present Taho-DiscordBot

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from tortoise.models import Model
from tortoise import fields
from tortoise.signals import post_save

if TYPE_CHECKING:
    from typing import List
    from .user import User
    from .role import Role

__all__ = (
    "NPC",
    "NPCOwner",
    "NPCRole"
)

class NPC(Model):
    class Meta:
        table = "npcs"

    id = fields.IntField(pk=True)
    cluster = fields.ForeignKeyField("main.ServerCluster", related_name="npcs")
    name = fields.CharField(max_length=255)
    avatar = fields.CharField(max_length=255, null=True)

    users: fields.ReverseRelation["NPCOwner"]
    roles: fields.ReverseRelation["NPCRole"]

    async def add_role(self, role: Role) -> None:
        """
        Add a role to the NPC.
        """
        await NPCRole.get_or_create(npc=self, role=role)

    async def remove_role(self, role: Role) -> None:
        """
        Remove a role from the NPC.
        """
        await NPCRole.filter(npc=self, role=role).delete()

    async def get_db_user(self) -> User:
        """
        Get the User that represents the NPC.
        """
        from .user import User # Avoid circular import
        return (await User.get_or_create(user_id=self.id, cluster=self.cluster))[0]

    async def get_users(self) -> List[User]:
        """
        Get all the users who own the NPC as a <User> instance.
        This is different from <.users> because <.users> returns <NPCOwner>
        """
        return [await u.user async for u in self.users]
        

@post_save(NPC)
async def on_npc_save(_, instance: NPC, created: bool, *args, **kwargs) -> None:
    if created:
        from .user import User # circular import
        await User.get_or_create(user_id=instance.id, cluster=instance.cluster)

class NPCOwner(Model):
    class Meta:
        table = "npc_owners"

    id = fields.IntField(pk=True)

    npc = fields.ForeignKeyField("main.NPC", related_name="users")
    user = fields.ForeignKeyField("main.User", related_name="npcs")
    original_owner = fields.BooleanField(default=False)
    pattern = fields.CharField(max_length=255, null=True)
    is_selected = fields.BooleanField(default=False)

class NPCRole(Model):
    class Meta:
        table = "npc_roles"

    id = fields.IntField(pk=True)

    npc = fields.ForeignKeyField("main.NPC", related_name="npc_roles")
    role = fields.ForeignKeyField("main.Role", related_name="npc_roles")