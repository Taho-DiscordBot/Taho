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
import uuid
import tortoise
from .base import BaseModel
from tortoise import fields
from tortoise.signals import post_save
from taho.exceptions import AlreadyExists, DoesNotExist
from taho.enums import InfoType
from taho.database.utils import convert_to_type
import sys

if TYPE_CHECKING:
    from typing import AsyncGenerator, Optional, Tuple, Union, List
    from .user import User
    from taho import Emoji, Bot
    from taho import CurrencyAmount


__all__ = (
    "Bank",
    "BankInfo",
    "BankAccount",
    "BankingTransaction",
)

class Bank(BaseModel):
    """Represents a bank.

    .. container:: operations

        .. describe:: x == y

            Checks if two banks are equal.

        .. describe:: x != y

            Checks if two banks are not equal.
        
        .. describe:: hash(x)

            Returns the bank's hash.
        
        .. describe:: str(x)

            Returns the bank's name.

        .. describe:: async for x

            Returns an async iterator on the bank's accounts.
    
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`

        .. collapse:: name

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``

            Python: :class:`str`
        
        .. collapse:: emoji

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` True

            Python: optional[:class:`str`]
        
        .. collapse:: user
        
            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``banks``

            Python: :class:`~taho.database.models.User`
        
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``banks``
            
            Python: :class:`~taho.database.models.Cluster`
    
    Attributes
    -----------
    id: :class:`int`
        The bank's ID.
    name: :class:`str`
        The bank's name.
    emoji: Optional[:class:`str`]
        The bank's emoji.
    user: :class:`~taho.database.User`
        The bank's owner, the user who created the bank.
    cluster: :class:`~taho.database.models.Cluster`
        The cluster where the bank is.
    """
    class Meta:
        table = "banks"

    id = fields.IntField(pk=True)
    
    cluster = fields.ForeignKeyField("main.Cluster", related_name="banks")
    user = fields.ForeignKeyField("main.User", related_name="banks")
    name = fields.CharField(max_length=255)
    emoji = fields.CharField(max_length=255, null=True)

    infos: fields.ReverseRelation["BankInfo"]
    accounts: fields.ReverseRelation["BankAccount"]
    
    def __str__(self) -> str:
        return self.name
    
    async def __aiter__(self) -> AsyncGenerator[BankAccount]:
        async for account in self.accounts:
            yield account
    
    def get_emoji(self, bot: Bot) -> Emoji:
        """
        Get the bank's emoji as a :class:`~taho.Emoji` object.

        Parameters
        ----------
        bot: :class:`~taho.Bot`
            The bot instance.
            Used to get the emoji from Discord.
        
        Returns
        --------
        :class:`~taho.Emoji`
            The bank's emoji.
        """
        from taho.utils import Emoji
        return Emoji(bot, self.emoji)
        


    async def get_info(self, key: str) -> Union[str, int, float, None]:
        """|coro|

        Get an info from the Bank.

        Parameters
        ----------
        key: :class:`str`
            The key of the info.
        
        Raises
        ------
        KeyError
            If the info does not exist.
        
        Returns
        --------
        Union[:class:`str`, :class:`int`, :class:`float`, :class:`None`, :class:`bool`]
            The info.
        """
        async for info in self.infos:
            if info.key == key:
                return info.value
        return None

    async def get_account(self, account_id: Optional[int]=None) -> BankAccount:
        """|coro|

        Get an account from the Bank.

        If no account_id is provided, the default account is returned.

        Parameters
        ----------
        account_id: Optional[:class:`int`]

        Raises
        ------
        ~taho.DoesNotExist
            If the account does not exist.

        Returns
        --------
        :class:`.BankAccount`
            The account.
        """

        if account_id is None:
            return await self._get_default_account(force_get=True)
        try:
            return await BankAccount.get(bank=self, pk=account_id)
        except tortoise.exceptions.DoesNotExist:
            raise DoesNotExist("Account not found.")

    async def get_transactions(self, limit: int=100, *orderings: str) -> List[BankingTransaction]:
        """|coro|

        Get transactions from the Bank.
        
        Parameters
        ----------
        limit: :class:`int`
            The limit on the number of transactions returned.
        orderings: :class:`str`
            The orderings to use.
            To sort by descending date, use "-date".
            The orderings used must by a field of the BankingTransaction model.

        """
        return (
            await BankingTransaction.filter(account__bank__pk=self.pk)
            .order_by(*orderings)
            .limit(limit or sys.maxsize)
        )
        
    async def _create_default_account(self, default_user: User=None, force_create: bool=False) -> BankAccount:
        """|coro|

        Create the default account for the bank.
        This account is purely indicative, it is useful to make
        the balance bewteen charges and interests.

        .. warning::
            Use force_create only if you know what you are doing.
            You have to check if the account already exists.
            Having two default accounts is not allowed and provoke
            bugs in the code.

        Parameters
        ----------
        default_user: Optional[:class:`~taho.database.User`]
            The cluster's default user, the default_account is 
            created with this user.
        force_create: :class:`bool`
            If True, the default account is created even if it does already exist.
        
        Raises
        ------
        ~taho.AlreadyExists
            If the default account already exists.
            Not raised if force_create is True.

        Returns
        --------
        :class:`.BankAccount`
            The default account.
        """
        if not default_user:
            default_user = await (await self.cluster).get_default_user()
        if force_create:
            return await BankAccount.create(bank=self, user=default_user)
        try:
            await self._get_default_account(default_user=default_user)
            raise AlreadyExists("Default account already exists.")
        except DoesNotExist:
            return await BankAccount.create(bank=self, user=default_user)
    
    async def _get_default_account(self, default_user: User=None, force_get: bool=False) -> BankAccount:
        """|coro|

        Get the default account for the bank.
        This account is purely indicative, it is useful to make
        the balance bewteen charges and interests.

        Parameters
        ----------
        default_user: Optional[:class:`~taho.database.User`]
            The cluster's default user, the default_account is 
            created with this user.
        force_get: :class:`bool`
            If True, the default account is created if it does not exist
            rather than raising an error.

        Raises
        ------
        ~taho.DoesNotExist
            If the default account does not exist.
            Not raised if force_get is True.
        
        Returns
        --------
        :class:`.BankAccount`
            The default account.
        """
        try:
            if not default_user:
                default_user = await (await self.cluster).get_default_user()
            return await BankAccount.get(bank=self, default_user=default_user)
        except tortoise.exceptions.DoesNotExist:
            if force_get:
                return await self._create_default_account(default_user=default_user)
            raise DoesNotExist("Default account does not exist.")

@post_save(Bank)
async def bank_post_save(_, instance: Bank, created: bool, *args, **kwargs) -> None:
    """|coro|

    Automatically create the default account for the bank when it is created.
    If the bank already exists or already has a default account, do nothing.

    .. warning::

        This function is used as a signal, it's not meant to be called manually.

    Parameters
    ----------
    instance: :class:`.Bank`
        The saved bank.
    created: :class:`bool`
        Whether the bank was created or not.
    """
    if created:
        try:
            await instance._create_default_account()
        except AlreadyExists:
            pass

class BankInfo(BaseModel):
    """
    Represents an info about a bank.

    .. container:: operations

        .. describe:: x == y
        
            Checks if two info are equal.

        .. describe:: x != y

            Checks if two info are different.

        .. describe:: hash(x)

            Returns the info's hash.
    
    .. container:: fields

        .. collapse:: id

            Tortoise: :class:`~tortoise.models.fields.IntField`

                - :attr:`pk` True
            
            Python: :class:`int`
        
        .. collapse:: bank

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`.Bank`
                - :attr:`related_name` ``infos``
            
            Python: :class:`.Bank`
        
        .. collapse:: key

            Tortoise: :class:`tortoise.models.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.models.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.InfoType`
            
            Python: :class:`~taho.enums.InfoType`
        
        .. collapse:: value

            Tortoise: :class:`tortoise.models.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`

    Attributes
    ----------
    bank: :class:`.Bank`
        The bank the info belongs to.
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
        table = "bank_infos"

    id = fields.IntField(pk=True)

    bank = fields.ForeignKeyField("main.Bank", related_name="infos")
    key = fields.CharField(max_length=255)
    type = fields.IntEnumField(InfoType)
    value = fields.CharField(max_length=255)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BankInfo):
            return self.py_value == other.py_value
        return other == self.py_value

    @property
    def py_value(self) -> Union[None, bool, int, float, str]:
        return convert_to_type(self.value, self.type)

async def create_transaction_operation(
    from_account: BankAccount, 
    to_account: BankAccount, 
    amount: CurrencyAmount, 
    description: str=None,
    return_transactions: bool=False
    ) -> Optional[Tuple[BankingTransaction]]:
    """|coro|

    Create a transaction operation between two accounts.

    Parameters
    ----------
    from_account: :class:`.BankAccount`
        The account to debit.
    to_account: :class:`.BankAccount`
        The account to credit.
    amount: :class:`~taho.CurrencyAmount`
        The amount to transfer.
    description: Optional[:class:`str`]
        The description of the operation.
    return_transactions: :class:`bool`
        If True, the transactions are returned.

        .. note::
            Returning the transactions is less optimized because two queries are
            performed.

    Raises
    ------
    ValueError
        If the amount is negative.

    Returns
    -------
    Optional[Tuple[:class:`.BankingTransaction`]]
        The transactions created.
        If the ``return_transactions`` parameter is ``False``, ``None`` is returned.
    """
    if amount < 0:
        raise ValueError("Amount must be positive.")
    currency = amount.currency
    amount = amount.amount
    ref = uuid.uuid4()
    transactions = (
        BankingTransaction(
            account=from_account, 
            amount=-amount, 
            currency=currency, 
            description=description,
            ref=ref
        ),
        BankingTransaction(
            account=to_account, 
            amount=amount, 
            currency=currency, 
            description=description,
            ref=ref
        )
    )
    if return_transactions:
        await transactions[0].save()
        await transactions[1].save()
        return transactions
    else:
        await BankingTransaction.bulk_create(transactions)

class BankAccount(BaseModel):
    """
    Represents an account in a bank.

    .. container:: operations

        .. describe:: x == y

            Checks if two accounts are equal.

        .. describe:: x != y

            Checks if two accounts are different.
        
        .. describe:: hash(x)

            Returns the account's hash.
    
    .. container:: fields

        .. collapse:: id

            Tortoise: :class:`~tortoise.models.fields.IntField`

                - :attr:`pk` True
            
            Python: :class:`int`
        
        .. collapse:: bank

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`.Bank`
                - :attr:`related_name` ``accounts``
            
            Python: :class:`.Bank`
        
        .. collapse:: user

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``accounts``
            
            Python: :class:`~taho.database.models.User`
        
        .. collapse:: currency

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Currency`
                - :attr:`related_name` ``accounts``
            
            Python: :class:`~taho.database.models.Currency`
        
        .. collapse:: balance

            Tortoise: :class:`tortoise.models.fields.DecimalField`

                - :attr:`max_digits` 32
                - :attr:`decimal_places` 2
                - :attr:`default` 0
            
            Python: :class:`float`
        
        .. collapse:: is_default

            Tortoise: :class:`tortoise.models.fields.BooleanField`

                - :attr:`default` False
            
            Python: :class:`bool`
    
    Attributes
    ----------
    bank: :class:`.Bank`
        The bank the account belongs to.
    user: :class:`~taho.database.models.User`
        The user the account belongs to.
        If None, the account is the bank's default account.
    balance: :class:`float`
        The balance of the account.
    currency: :class:`~taho.database.models.Currency`
        The currency of the money stored on account.
    is_default: :class:`bool`
        Whether the account is the default account of the user.
        This account will receive salaries, interests, etc.
    """
    class Meta:
        table = "bank_accounts"

    id = fields.IntField(pk=True)

    bank = fields.ForeignKeyField("main.Bank", related_name="accounts")
    user = fields.ForeignKeyField("main.User", related_name="accounts", null=True)
    balance = fields.DecimalField(max_digits=32, decimal_places=2, default=0)
    currency = fields.ForeignKeyField("main.Currency", related_name="accounts")
    is_default = fields.BooleanField(default=False)

    transactions: fields.ReverseRelation["BankingTransaction"]

    def get_balance(self) -> CurrencyAmount:
        """

        Returns the balance of the account.

        Returns
        -------
        :class:`~taho.CurrencyAmount`
            The balance of the account.
        
        """
        return CurrencyAmount(self.balance, self.currency)
    
    async def credit(self, amount: CurrencyAmount) -> None:
        """|coro|

        Credit the account with an amount.

        Parameters
        ----------
        amount: :class:`~taho.CurrencyAmount`
            The amount to credit.
        """
        converted_amount = await amount.convert(self.currency)
        return await self._credit(converted_amount)

    async def _credit(self, amount: float) -> None:
        """|coro|

        Credit the account with money.

        Parameters
        ----------
        amount: :class:`float`
            The amount to receive.
        

        .. note::

            This method is not intended to be used directly
            because it doesn't perform any conversion between
            currencies.
            Please use :meth:`.credit` instead.
        """
        self.balance += amount
        await self.save()
    
    async def transfer(self, to: BankAccount, amount: CurrencyAmount, description: str=None) -> None:
        """|coro|

        Transfer money from this account to another one.

        Parameters
        -----------
        to: :class:`.BankAccount`
            The account to credit.
        amount: :class:`~taho.CurrencyAmount`
            The amount to transfer.
        description: Optional[:class:`str`]
            The description of the operation.

        Raises
        -------
        ValueError
            If the account doesn't have enought money (balance < amount).
        
        """
        self_currency = await self.currency
        new_amount = await amount.convert(self_currency)
        if self.balance < new_amount:
            raise ValueError(f"Not enough money in account {self.id}")
        await self._credit(-new_amount)
        await to.credit(amount)
        await create_transaction_operation(self, to, amount, description)


class BankingTransaction(BaseModel):
    """
    Represents a transaction from a :class:`.BankAccount`.

    .. container:: operations

        .. describe:: x == y

            Checks if two transactions are equal.

        .. describe:: x != y

            Checks if two transactions are not equal.
        
        .. describe:: hash(x)

            Returns the transaction's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: account

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`.BankAccount`
                - :attr:`related_name` ``transactions``
            
            Python: :class:`.BankAccount`
        
        .. collapse:: amount

            Tortoise: :class:`tortoise.models.fields.DecimalField`

                - :attr:`max_digits` 32
                - :attr:`decimal_places` 2
            
            Python: :class:`float`
        
        .. collapse:: currency

            Tortoise: :class:`tortoise.models.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Currency`
                - :attr:`related_name` '``transactions``
            
            Python: :class:`~taho.database.models.Currency`
        
        .. collapse:: ref

            Tortoise: :class:`tortoise.models.fields.UUIDField`

                - :attr:`null` True

            Python: Optional[:class:`uuid.UUID`]
        
        .. collapse:: date

            Tortoise: :class:`tortoise.models.fields.DatetimeField`

                - :attr:`auto_now_add` True
            
            Python: :class:`datetime.datetime`
        
        .. collapse:: description

            Tortoise: :class:`tortoise.models.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` True
            
            Python: Optional[:class:`str`]

    Attributes
    -----------
    id: :class:`int`
        The transaction's ID.
    account: :class:`.BankAccount`
        The account on which the transaction is done.
    amount: :class:`float`
        The amount of the transaction.
    currency: :class:`~taho.database.models.Currency`
        The currency of the transaction.
    ref: Optional[:class:`uuid.UUID`]
        An UUID allowing to link two transactions resulting 
        from the same action.

        Example: 

            When you use :meth:`.BankAccount.transfer`,
            two transactions are created. This attribute
            allows to link the two transactions.
    date: :class:`datetime.datetime`
        The date of the operation.
    description: Optional[:class:`str`]
        The description of the operation.
    """
    class Meta:
        table = "bank_transactions"

    id = fields.IntField(pk=True)

    account: BankAccount = fields.ForeignKeyField("main.BankAccount", related_name="transactions")
    amount = fields.DecimalField(max_digits=32, decimal_places=2)
    currency = fields.ForeignKeyField("main.Currency", related_name="transactions")
    ref = fields.UUIDField(null=True)
    date = fields.DatetimeField(auto_now_add=True)
    description = fields.CharField(max_length=255, null=True)



    async def get_similar(self) -> List[BankingTransaction]:
        """|coro|

        Returns the transactions which have the same
        :attr:`~.BankingTransaction.ref` as this one.

        Returns
        -------
        List[:class:`.BankingTransaction`]
            The similar transactions.
        """
        #todo check return type
        return await BankingTransaction.filter(ref=self.ref).all().exclude(id=self.id)