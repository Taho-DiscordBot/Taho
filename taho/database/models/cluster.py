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
from .info import Info
from taho.exceptions import DoesNotExist, AlreadyExists
from taho.database import db_utils
from taho.enums import ItemType
from taho.babel import _
import asyncio

if TYPE_CHECKING:
    from taho import Bot, Emoji
    from typing import Any, List, Optional, Union, Dict, AsyncGenerator
    from taho.enums import RoleType
    from taho.abstract import AbstractAccessRule, AbstractRewardPack, AbstractInfo
    from .server import Server
    from .user import User
    from .bank import Bank
    from .item import Item
    from .stat import Stat
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
    stats: List[:class:`~taho.database.models.Stat`]
        |coro_attr|

        The cluster's stats.
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
    stats: fields.ReverseRelation["Stat"]
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

    async def create_role(self, type: RoleType, *roles: discord.Role) -> Role:
        """|coro|

        Creates a role in the cluster.

        Parameters
        -----------
        type: :class:`taho.enums.RoleType`
            The role's type.
        roles: :class:`discord.Role`
            The roles to create.
        
        Returns
        --------
        :class:`~taho.database.models.Role`
            The role.
        """
        from .role import Role
        role = await Role.create(cluster=self, type=type)
        await role.add_roles(*roles)

        return role
        #try:
        #    return await self.roles.all().get(type=type)
        #except t_exceptions.DoesNotExist:
        #    return await Role.create(type=type, cluster=self, *roles)
    
    async def get_guilds(self, bot: Bot) -> List[discord.Guild]:
        """|coro|

        Gets the cluster's guilds corresponding to the cluster's
        servers.

        Parameters
        -----------
        bot: :class:`taho.bot.Bot`
            The bot.
        
        Returns
        --------
        List[discord.Guild]
            The guilds.
        """
        guilds_ids = await self.servers.all().values_list("id", flat=True)

        return [bot.get_guild(guild_id) for guild_id in guilds_ids]

    async def get_roles_by_name(self, bot: Bot) -> Dict[str, Role]:
        """|coro|
        
        Gets all the roles in the cluster and organizes 
        them by name (of the servers roles).

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.

        Returns
        --------
        Dict[:class:`str`, :class:`~taho.database.models.Role`]
            The roles organized by name.
        

        Example
        --------
        How are roles organized by name?

        .. code-block:: python3

            {
                "role_name": Role,
                "role_name2": Role2,
                ...
            }

        
        .. note:: 

            Role names are taken from Discord roles associated with Server roles.
            So a Role can appear several times, under a different name.
        """
        # Get all the cluster's roles

        roles = await self.roles.all().prefetch_related("server_roles")
        roles_by_name = {}

        # For every Role in cluster
        for c_role in roles:
            # Get every Discord roles of the Role
            async for s_role in c_role.get_discord_roles(bot):
                roles_by_name[s_role.name] = c_role

        return roles_by_name

    async def get_discord_roles(self, bot: Bot) -> Dict[Role, List[discord.Role]]:
        """|coro|
        
        Gets all the roles and discord roles in the cluster and organizes 
        them.

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.

        Returns
        --------
        Dict[:class:`~taho.database.models.Role`, List[:class:`discord.Role`]]
            The roles organized.
        

        Example
        --------
        How are roles organized?

        .. code-block:: python3

            {
                Role1: [discordRole1, discordRole2...],
                Role2: [discordRole3, discordRole4...],
                ...
            }
        """
        # Get all the cluster's roles

        roles = await self.roles.all().prefetch_related("server_roles")
        roles_organized = {}

        # For every Role in cluster
        for c_role in roles:
            # Get every Discord roles of the Role
            roles_organized[c_role] = await c_role.get_discord_roles(bot)

        return roles_organized

    async def get_users_by_name(self, bot: Bot) -> Dict[str, User]:
        """|coro|
        
        Gets all the users in the cluster and organizes 
        them by name (of the servers users).

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.

        Returns
        --------
        Dict[:class:`str`, :class:`~taho.database.models.User`]
            The users organized by name.
        

        Example
        --------
        How are users organized by name?

        .. code-block:: python3

            {
                "user_name": User,
                "user_name2": User2,
                ...
            }

        
        .. note:: 

            User names are taken from Discord users associated with Server members.
            So a User can appear several times, under a different name.
        """
        # Get all the cluster's users

        users = await self.users.all()
        guilds = await self.get_guilds(bot)
        users_by_name = {}

        # For every User in cluster
        for c_user in users:
            for guild in guilds:
                user = guild.get_member(c_user.user_id)
                if user:
                    users_by_name[user.display_name] = c_user
                else:
                    try:
                        npc = await c_user.get_npc()
                    except DoesNotExist:
                        pass
                    else:
                        users_by_name[npc.name] = c_user

        return users_by_name

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
        try:
            return await Cluster.get(servers__id=guild.id)
        except t_exceptions.DoesNotExist:
            raise DoesNotExist("The guild is not stored as a Server in the database.")

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
        *,
        type: ItemType = ItemType.resource,
        emoji: Optional[Emoji] = ...,
        description: Optional[str] = ...,
        access_rules: Optional[List[AbstractAccessRule]] = ...,
        rewards: Optional[List[AbstractRewardPack]] = ...
        ) -> Item:
        ...
    
    @overload
    async def create_item(self,
        name: str,
        *,
        type: ItemType = ItemType.currency,
        currency: Optional[Union[Currency, int]] = ...,
        emoji: Optional[Emoji] = ...,
        description: Optional[str] = ...,
        access_rules: Optional[List[AbstractAccessRule]] = ...,
        rewards: Optional[List[AbstractRewardPack]] = ...
        ) -> Item:
        ...
    
    @overload
    async def create_item(self,
        name: str,
        *,
        type: ItemType = ItemType.resource,
        emoji: Optional[Emoji] = ...,
        description: Optional[str] = ...,
        durability: Optional[int] = ...,
        cooldown: Optional[int] = ...,
        access_rules: Optional[List[AbstractAccessRule]] = ...,
        rewards: Optional[List[AbstractRewardPack]] = ...
        ) -> Item:
        ...
    
    async def create_item(self, name: str, type: ItemType, **options: Any) -> Item:
        """|coro|

        Create an item in the cluster.

        Parameters
        -----------
        name: :class:`str`
            The name of the item.
        type: :class:`~taho.enums.ItemType`
            The type of the item.
        emoji: Optional[:class:`~taho.Emoji`]
            The emoji of the item.
        description: Optional[:class:`str`]
            The description of the item.
        durability: Optional[:class:`int`]
            The durability of the item.
            Only if ``type`` is :attr:`~taho.enums.ItemType.consumable`
        cooldown: Optional[:class:`int`]
            The cooldown between two item use.
            Only if ``type`` is :attr:`~taho.enums.ItemType.consumable`
        access_rules: Optional[List[:class:`~taho.utils.AbstractAccessRule`]]
            The access rules of the item.
        rewards: Optional[List[:class:`~taho.utils.AbstractRewardPack`]]
            The rewards of the item.

        Raises
        -------
        ~taho.exceptions.AlreadyExists
            An item with the same name already exists.
        ValueError
            If ``cooldown`` is negative (<=0).
            If ``durability`` is negative (<=-1) or equal to 0.
            If ``type`` is :attr:`~taho.enums.ItemType.currency` and
            ``currency`` is not defined.
        """
        from .item import Item, ItemAccessRule, ItemReward, ItemRewardPack # avoid circular import

        # Check validity of the options cooldown and durability
        if options.get("cooldown", 1) <= 0:
            raise ValueError("The cooldown must be positive.")
        dura = options.get("durability", 1)
        if dura <= -1 or dura == 0:
            raise ValueError("The durability must be positive or equal to -1 (infinite).")
        
        if type == ItemType.currency and options.get("currency", None) is None:
            raise ValueError("The currency must be defined.")
        
        currency = options.pop("currency", None)

        from .currency import Currency # avoid circular import

        if isinstance(currency, Currency):
            options["currency_id"] = currency.id
        elif isinstance(currency, int):
            options["currency_id"] = currency
        
        try:
            # Create the item
            item = await Item.create(
                cluster=self, 
                name=name, 
                type=type,
                **options
                )
        except t_exceptions.IntegrityError:
            raise AlreadyExists("An item with the same name already exists.")
        else:
            # Get the access rules and rewards
            access_rules = options.get("access_rules", [])
            reward_packs = options.get("reward_packs", [])

            queries = []

            # Register coroutines to create the access rules and rewards
            if access_rules:
                for rule in access_rules:
                    queries.append(rule.to_db_access(
                        ItemAccessRule,
                        item
                        ))
            if reward_packs:
                for pack in reward_packs:
                    queries.append(pack.to_db_pack(
                        ItemRewardPack,
                        ItemReward,
                        item
                        ))
            
            # Execute the coroutines
            await asyncio.gather(*queries)

            return item

    async def create_bank(
        self, 
        name: str,
        default_currency: Currency,
        emoji: Optional[Emoji] = None,
        description: Optional[str] = None,
        owner: Optional[User] = None,
        infos: List[AbstractInfo] = []
    ) -> Bank:
        """|coro|

        Create a bank in the cluster.

        Parameters
        -----------
        name: :class:`str`
            The name of the bank.
        default_currency: :class:`~taho.database.models.Currency`
            The bank's default currency.
        emoji: Optional[:class:`~taho.Emoji`]
            The emoji of the bank.
        description: Optional[:class:`str`]
            The description of the bank.
        owner: Optional[:class:`~taho.database.models.User`]
            The owner of the bank.
        infos: List[:class:`~taho.utils.AbstractInfo`]

        Raises
        -------
        ~taho.exceptions.AlreadyExists
            A bank with the same name already exists.
        """
        from .bank import Bank, BankInfo # avoid circular import

        try:
            # Create the item
            bank = await Bank.create(
                cluster=self, 
                name=name, 
                default_currency=default_currency,
                emoji=emoji,
                description=description,
                owner=owner
                )
        except t_exceptions.IntegrityError:
            raise AlreadyExists("A bank with the same name already exists.")
        else:

            # Register coroutines to create the infos
            if infos:
                queries = []
                for info in infos:
                    queries.append(info.to_db_info(
                        BankInfo,
                        bank
                        ))

                # Execute the coroutines
                await asyncio.gather(*queries)

            return bank


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
        currency = await Currency.create(
            cluster=instance, 
            name="Dollar",
            symbol="$",
            code="USD",
            emoji="💵",
            is_default=True
            )
        
        await instance.create_item(
            name="Dollar",
            type=ItemType.currency,
            emoji="💵",
            description=f"A cash item for the Currency {currency.name}",
            currency=currency
            )

class ClusterInfo(Info):
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
    
    cluster = fields.ForeignKeyField("main.Cluster", related_name="infos")