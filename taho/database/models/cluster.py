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
from typing import TYPE_CHECKING, overload
from .base import BaseModel
from tortoise import fields
from tortoise import exceptions as t_exceptions
from tortoise.signals import post_save
from .role import Role
from taho.exceptions import DoesNotExist, AlreadyExists
from ..utils import convert_to_type, get_type
from taho.database import utils as db_utils
from taho.enums import InfoType
from taho.babel import _


if TYPE_CHECKING:
    from taho import Bot, Emoji
    from typing import Any, List, Optional, Union, Dict, AsyncGenerator
    from taho.enums import RoleType, ItemType
    from taho.bot import Bot
    from .server import Server
    from .user import User
    from .bank import Bank
    from .item import Item
    from .currency import Currency
    import discord




__all__ = (
    "Cluster",
    "ClusterInfo",
)

class Cluster(BaseModel):
    """Represents a cluster.

    .. container:: operations

        .. describe:: x == y

            Checks if two clusters are equal.

        .. describe:: x != y

            Checks if two clusters are not equal.
        
        .. describe:: hash(x)

            Returns the cluster's hash.
        
        .. describe:: str(x)

            Returns the cluster's name.

        .. describe:: async for x

            Returns an async iterator on the cluster's servers.
    
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: name

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` ``True``

    Attributes
    -----------
    id: :class:`int`
        The cluster's ID.
    name: Optional[:class:`str`]
        The cluster's name.
    infos: List[:class:`.ClusterInfo`]
        |coro_attr|

        The cluster's infos.
    servers: List[:class:`~taho.database.models.Server`]
        |coro_attr|

        The cluster's servers.
    users: List[:class:`~taho.database.models.User`]
        |coro_attr|

        The cluster's users.
    banks: List[:class:`~taho.database.models.Bank`]
        |coro_attr|

        The cluster's banks.
    items: List[:class:`~taho.database.models.Item`]
        |coro_attr|

        The cluster's items.
    roles: List[:class:`~taho.database.models.Role`]
        |coro_attr|

        The cluster's RP roles.
    """
    class Meta:
        table = "clusters"
    
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255, null=True)

    infos: fields.ReverseRelation["ClusterInfo"]
    servers: fields.ReverseRelation["Server"]
    users: fields.ReverseRelation["User"]
    banks: fields.ReverseRelation["Bank"]
    items: fields.ReverseRelation["Item"]
    roles: fields.ReverseRelation["Role"]



    async def __aiter__(self) -> AsyncGenerator[Server]:
        async for server in self.servers:
            yield server

    def __str__(self) -> str:
        return self.name or self.__repr__()

    async def get_info(self, key: str) -> Optional[Union[str, int, float, None]]:
        """|coro|

        Gets the value of a key in the cluster's info.

        Parameters
        -----------
        key: :class:`str`
            The key to get the value of.
        
        Raises
        -------
        KeyError
            If the key doesn't exist.
        
        Returns
        --------
        Optional[Union[str, int, float, None]]
            The value of the key.
        """
        try:
            return await self.infos.get(key=key).py_value #test that
        except t_exceptions.DoesNotExist:
            raise KeyError(f"No info with key {key}")
        
    async def set_info(self, key: str, value: Optional[Union[str, int, float, None]]) -> None:
        """|coro|

        Sets the value of a key in the cluster's info.

        Parameters
        -----------
        key: :class:`str`
            The key to set the value of.
        value: Optional[Union[str, int, float, None]]
            The value to set.
            If :class:`None`, the info will be deleted.
        
        """
        await ClusterInfo.update_or_create(
            cluster=self,
            key=key,
            type=db_utils.get_type(value),
            value=str(value)
        )

    async def get_user(self, user_id: int, create_if_not_exists: bool=False) -> User:
        """|coro|

        Gets a user from the cluster.

        Parameters
        -----------
        user_id: :class:`int`
            The user's ID.
        create_if_not_exists: :class:`bool`
            Whether to create the user if it doesn't exist.
        
        Raises
        -------
        DoesNotExist
            If the user doesn't exist.
            Only raised if :attr:`create_if_not_exists` is :class:`False`.
        
        Returns
        --------
        :class:`~taho.database.models.User`
            The user.
        """
        from .user import User
        try:
            return await self.users.all().get(id=user_id)
        except t_exceptions.DoesNotExist:
            if create_if_not_exists:
                return await User.create(user_id=user_id, cluster=self)
            raise DoesNotExist(f"User with ID {user_id} doesn't exist")

    # async def get_guilds_members(self, bot: Bot) -> Dict[Server, List[discord.Member]]:
    #     """|coro|

    #     Gets the guilds and their members of the cluster.

    #     Parameters
    #     -----------
    #     bot: :class:`discord.Bot`
    #         The bot to get the guilds and members of.
        
    #     Returns
    #     --------
    #     Dict[:class:`~taho.database.models.Server`, List[:class:`discord.Member`]]
    #         The guilds and their members.
    #     """
    #     #todo create <Server>.get_members()
    #     return {server:await server.get_members(bot) async for server in self.servers}

    # async def get_guilds_member(self, bot: Bot, user_id: int) -> List[discord.Member]:
    #     """|coro|

    #     Get the :class:`discord.Member` objects for the user in every server of the cluster.

    #     Parameters
    #     -----------
    #     bot: :class:`discord.ext.commands.Bot`
    #         The bot to use.
    #     user_id: :class:`int`
    #         The user's ID.
        
    #     Returns
    #     --------
    #     List[:class:`discord.Member`]
    #         The members of the user in the cluster.
    #     """
    #     members = []
    #     async for server in self.servers:
    #         members.append(await server.get_member(bot, user_id))
    #     return [m for m in members if m]

    # async def get_guilds_roles(self, bot: Bot) -> Dict[Server, List[discord.Role]]:
    #     """|coro|

    #     Gets the guilds and their roles of the cluster.

    #     Parameters
    #     -----------
    #     bot: :class:`discord.Bot`
    #         The bot to get the guilds and roles of.
        
    #     Returns
    #     --------
    #     Dict[:class:`~taho.database.models.Server`, List[:class:`discord.Role`]]
    #         The guilds and their roles.
    #     """
    #     #todo create <Server>.get_roles()
    #     return {server:await server.get_roles(bot) async for server in self.servers}

    # #todo: apply get_discord_members modification (get_discord_members -> get_guilds_member)

    # async def get_servers_roles(self, bot: Bot) -> Dict[Server, List[discord.Role]]:
    #     """|coro|

    #     Get the :class:`discord.Role` objects for the cluster's servers.

    #     Parameters
    #     -----------
    #     bot: :class:`discord.ext.commands.Bot`
    #         The bot to use.
        
    #     Returns
    #     --------
    #     Dict[:class:`~taho.database.models.Server`, List[:class:`discord.Role`]]
    #         The roles of the cluster's servers.
    #         The key is the server where the roles are.
    #     """
    #     return {guild:guild.roles for guild in await self.get_guilds(bot)}
    #     return {role:await role.get_discord_roles(bot) async for role in self.roles}
        
    # async def get_common_guild_roles(self, bot: Bot, extended: bool=False) -> Dict[str, List[discord.Role]]:
    #     """
    #     Get all the roles that are common to all the guilds in the cluster.
    #     A role is common if it is named the same way in all the guilds.
    #     """
    #     # Fetch all guilds from the cluster
    #     servers = await self.servers.all()
    #     # Pick one guild to get the roles from
    #     # All roles will be compared to the ones on the guild
    #     server: Server = servers.first()
    #     # For each role in the guild, check if it is common to all the guilds
    #     # We use the get_common_discord_role function to check if the role is common
    #     roles = {
    #         role.name: await self.get_common_discord_role(bot, role, servers) 
    #         for role in (await server.get_guild(bot)).roles
    #     }
    #     # Remove empty lists corresponding to roles that are not common to all the guilds
    #     return {k: v for k, v in roles.items() if v is not None}

    # async def get_commun_discord_role(self, bot: Bot, role: discord.Role, servers: List[Server]=None) -> List[discord.Role]:
    #     """
    #     Returns a list of discord.Role objects that are common to all the guilds in the cluster.
    #     A role is common if it is named the same way in all the guilds.

    #     The difference between this method and get_common_discord_roles is that this method
    #     returns the roles in common with the one given as parameter, whereas get_common_discord_roles
    #     returns all the roles that are common to all the guilds in the cluster.
    #     """
    #     if servers is None:
    #         servers = await self.servers.all()
    #     if len(servers) == 1:
    #         return [role]
    #     else:
    #         roles = []
    #         guild_roles = [
    #             (await server.get_guild(bot)).roles for server in servers
    #         ]
    #         for guild_role in guild_roles:
    #             r = find(lambda r: r.name == role.name, guild_role)
    #             if not r:
    #                 return None
    #             roles.append(r)
    #         return roles

    # async def create_role(self, bot: Bot, role: discord.Role, type: RoleType) -> Role:
    #     """
    #     Configure a RP role on a cluster.
    #     Raises exception if:
    #     - RoleException: The role already exists;
    #     - RoleException: The role is not common to all guilds of the cluster.
    #     """
    #     roles = []
    #     #todo apply <Cluster>.get_servers_roles modification
    #     for r in (await self.get_servers_roles(bot)).values():
    #         roles.extend(r)
    #     if role in roles:
    #         raise RoleException("Role already exists.")
    #     common_roles = await self.get_commun_discord_role(bot, role)
    #     if not common_roles:
    #         raise RoleException("Role is not common to all guilds of the cluster.")
    #     # Create the Role instance
    #     role_obj = await Role.create(cluster=self, type=type)
    #     from taho.utils.db import get_db_guild # Avoid circular import
    #     # For each guild of the cluster, create the ServerRole instance
    #     objects = [
    #         ServerRole(role=role_obj, server=await get_db_guild(r.guild), discord_role_id=r.id)
    #         for r in common_roles
    #     ]
    #     # Save the Role and ServerRole instances
    #     await ServerRole.bulk_create(objects=objects)
    #     return role_obj

    async def get_default_user(self) -> User:
        """|coro|

        Get (or create if not stored) the default User of the cluster.
        This user will be used to store a bunch of things with a User field
        but not directly related to a user in this specific case.
        Example: A bank's default account is stored with this user.
        
        Returns
        --------
        :class:`~taho.database.models.User`
            The default user of the cluster.
        """
        from .user import User # Avoid circular import
        user = await User.get_or_create(cluster=self, user_id=0)
        return user[0]
    
    async def get_default_currency(self) -> Optional[Currency]:
        """|coro|

        Get the default Currency of the cluster.
        
        Returns
        --------
        :class:`~taho.database.models.Currency`
            The default currency of the cluster.
        """
        return await db_utils.get_default_currency(self.id)
        

    async def get_default_bank(self) -> Bank:
        """|coro|

        Get (or create if not stored) the default User of the cluster.
        This user will be used to store a bunch of things with a User field
        but not directly related to a user in this specific case.
        Example: A bank's default account is stored with this user.
        
        Returns
        --------
        :class:`~taho.database.models.User`
            The default user of the cluster.
        """
        from .bank import Bank # Avoid circular import
        bank = await Bank.get_or_create(
            cluster=self, 
            name=_("Cash"), 
        )
        return bank[0]

    
    @classmethod
    async def from_guild(cls, guild: discord.Guild) -> Cluster:
        """|coro|

        Get the :class:`.Cluster` of a :class:`discord.guild`.

        Parameters
        -----------
        guild: :class:`discord.Guild`
            The guild to get the cluster from.
        
        Raises
        -------
        ~taho.exceptions.DoesNotExist
            The guild is not stored as a :class:`~taho.database.models.Server` 
            in the database.
        
        Returns
        --------
        :class:`.Cluster`
            The cluster of the guild.
        """
        from .server import Server # avoid circular import
        try:
            server = await Server.get(id=guild.id)
        except t_exceptions.DoesNotExist:
            raise DoesNotExist("The guild is not stored as a Server in the database.")
        else:
            return await server.cluster

    
        
    async def add_guild(self, bot: Bot, guild: discord.Guild, sync_server: bool=True) -> Server:
        """|coro|
        
        Add a server to the Cluster from a Guild object.

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        guild: :class:`discord.Guild`
            The guild to add.
        sync_server: :class:`bool`
            Whether to sync the server with the database.
            Set to ``False`` only if you create a Cluster
            and add it the server at the same time.
        
        Returns
        --------
        :class:`~taho.database.models.Server`
            The server added.
        """
        from .server import Server # avoid circular import

        server = await Server.get_or_create(id=guild.id)

        await self.add_server(bot, server[0], sync_server=sync_server)
        await server[0].refresh_from_db()
        return server[0]

    async def add_server(self, bot: Bot, server: Server, sync_server: bool=True) -> None:
        """|coro|
        
        Add a server to the Cluster from a Server object.
        
        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        server: :class:`~taho.database.models.Server`
            The server to add.
        sync_server: :class:`bool`
            Whether to sync the server with the database.
            Set to ``False`` only if you create a Cluster
            and add it the server at the same time.
        
        """
        server.cluster = self
        await server.save()
        if sync_server:
            await server.sync_server(bot)

    @overload
    async def create_item(self,
        name: str,
        type: ItemType,
        *,
        emoji: Optional[Emoji] = ...,
        description: Optional[str] = ...,
        ) -> Item:
        ...
    
    @overload
    async def create_item(self,
        name: str,
        type: ItemType,
        *,
        emoji: Optional[Emoji] = ...,
        description: Optional[str] = ...,
        durability: Optional[int] = ...,
        cooldown: Optional[int] = ...,
        ) -> Item:
        ...
    
    @overload
    async def create_item(self,
        name: str,
        type: ItemType,
        *,
        emoji: Optional[Emoji] = ...,
        description: Optional[str] = ...,
        durability: Optional[int] = ...,
        cooldown: Optional[int] = ...,
        ammo: Optional[Item] = ...,
        charger_size: Optional[int] = ...,
        ) -> Item:
        ...
    
    async def create_item(self, name: str, type: ItemType, **options: Any) -> Item:
        """|coro|

        Create an item in the cluster.

        Parameters
        -----------
        name: str
            The name of the item.
        type: :class:`~taho.enums.ItemType`
            The type of the item.
        emoji: Optional[:class:`~taho.Emoji`]
            The emoji of the item.
        description: Optional[str]
            The description of the item.
        durability: Optional[int]
            The durability of the item.
            Only if ``type`` is :attr:`~taho.enums.ItemType.consumable`
        cooldown: Optional[int]
            The cooldown between two item use.
            Only if ``type`` is :attr:`~taho.enums.ItemType.consumable`

        Raises
        -------
        ~taho.exceptions.AlreadyExists
            An item with the same name already exists.
        TypeError
            If you specified ``ammo`` but ``charger_size`` is not defined
            or if you specified ``charger_size`` but ``ammo`` is not defined.
        ValueError
            If ``cooldown`` is negative (<=0).
            If ``durability`` is negative (<=-1).
            If ``charger_size`` is negative (<=-1).
        """
        from .item import Item # avoid circular import
        if options.get("ammo") and not options.get("charger_size"):
            raise TypeError("You must specify the charger size if you specify the ammo.")
        if options.get("charger_size") and not options.get("ammo"):
            raise TypeError("You must specify the ammo if you specify the charger size.")
        if options.get("ammo"):
            options["ammo"] = options["ammo"].id
        if options.get("charger_size", 1) <= -1:
            raise ValueError("The charger size must be positive.")

        charger_size = options.get("charger_size", 1)
        if charger_size <= -1 or charger_size == 0:
            raise ValueError("The charger size must be positive or equal to -1 (infinite).")
        if options.get("cooldown", 1) <= 0:
            raise ValueError("The cooldown must be positive.")
        dura = options.get("durability", 1)
        if dura <= -1 or dura == 0:
            raise ValueError("The durability must be positive or equal to -1 (infinite).")
        try:
            return await Item.create(
                cluster=self, 
                name=name, 
                type=type,
                **options
                )
        except t_exceptions.IntegrityError:
            raise AlreadyExists("An item with the same name already exists.")

    async def create_bank(self, name: str) -> Bank:
        """|coro|

        Create a bank in the cluster.

        Parameters
        -----------
        name: :class:`str`
            The name of the bank.

        Raises
        -------
        ~taho.exceptions.AlreadyExists
            A bank with the same name already exists.
        
        Returns
        --------
        :class:`~taho.database.models.Bank`
            The created bank.
        """
        from .bank import Bank

@post_save(Cluster)
async def cluster_post_save(_, instance: Cluster, created: bool, *args, **kwargs) -> None:
    """|coro|

    Automatically create the default user, bank
    and currency for the cluster when it is created.
    If the cluster already exists, do nothing.


    .. warning::

        This function is used as a signal, it's not meant to be called manually.

    Parameters
    ----------
    instance: :class:`.Cluster`
        The saved cluster.
    created: :class:`bool`
        Whether the cluster was created or not.
    """
    if created:
        # Create the default user
        await instance.get_default_user()

        # Create the default Currency
        from .currency import Currency # avoid circular import
        await Currency.create(
            cluster=instance, 
            name="Dollar",
            symbol="$",
            code="USD",
            is_default=True
            )

        # Create the default bank
        await instance.get_default_bank()


class ClusterInfo(BaseModel):
    """
    Represents a cluster's info.

    .. container:: operations

        .. describe:: x == y

            Checks if two info are equal.
            The two :attr:`.py_value` are compared.
        
        .. describe:: x != y

            Checks if two info are different.
            The two :attr:`.py_value` are compared.
        
        .. describe:: hash(x)

            Returns the info's hash.
        
        .. describe:: str(x)

            Returns the info's string representation.
    
    .. container:: fields

        .. collapse:: id

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True
            
            Python: :class:`int`
        
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`.Cluster`
                - :attr:`related_name` ``infos``
            
            Python: :class:`.Cluster`
        
        .. collapse:: key

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.InfoType`
            
            Python: :class:`~taho.enums.InfoType`
        
        .. collapse:: value

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`
        
    Attributes
    -----------
    cluster: :class:`.Cluster`
        The cluster the info belongs to.
    key: :class:`str`
        The key of the info.
    type: :class:`~taho.enums.InfoType`
        The type of the info.
    value: :class:`str`
        The value of the info.
    py_value: Union[``None``, :class:`bool`, :class:`int`, :class:`float`, :class:`str`]
        The value of the info in Python's type.
    """
    class Meta:
        table = "cluster_infos"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="infos")
    key = fields.CharField(max_length=255)
    type = fields.IntEnumField(InfoType)
    value = fields.CharField(max_length=255)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ClusterInfo):
            return self.py_value == other.py_value
        return other == self.py_value
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def py_value(self) -> Union[None, bool, int, float, str]:
        return db_utils.convert_to_type(self.value, self.type)
