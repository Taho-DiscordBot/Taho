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
import uuid
import tortoise
from .base import BaseModel
from tortoise import fields
from tortoise.signals import post_save
from taho.exceptions import AlreadyExists, DoesNotExist, QuantityException
from taho.enums import ShortcutType
from taho.database import db_utils
from taho.abc import OwnerShortcutable
from .info import Info
import asyncio

import sys

if TYPE_CHECKING:
    from typing import AsyncGenerator, Optional, Tuple, Union, List
    from .user import User
    from .currency import Currency
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
        
        .. collapse:: description

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` True
            
            Python: optional[:class:`str`]
        
        .. collapse:: owner_shortcut
        
            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.OwnerShortcut`
                - :attr:`null` ``True``

            Python: Optional[:class:`~taho.database.models.OwnerShortcut`]
        
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``banks``
            
            Python: :class:`~taho.database.models.Cluster`
        
        .. collapse:: default_currency

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Currency`
                - :attr:`null` ``True``
            
            Python: :class:`~taho.database.models.Currency`
    
    Attributes
    -----------
    id: :class:`int`
        The bank's ID.
    name: :class:`str`
        The bank's name.
    emoji: Optional[:class:`str`]
        The bank's emoji.
    description: Optional[:class:`str`]
        The bank's description.
    owner_shortcut: Optional[:class:`~taho.database.OwnerShortcut`]
        The bank's owner (user, ...).
        If ``None``, the bank is owned by the bot
        (cash bank).
    cluster: :class:`~taho.database.models.Cluster`
        The cluster where the bank is.
    default_currency: Optional[:class:`~taho.database.models.Currency`]
        The bank's default currency.
        The currency will be used as a reference 
    """
    class Meta:
        table = "banks"

    id = fields.IntField(pk=True)
    
    cluster = fields.ForeignKeyField("main.Cluster", related_name="banks")
    owner_shortcut = fields.ForeignKeyField("main.OwnerShortcut", null=True)
    name = fields.CharField(max_length=255)
    emoji = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    default_currency = fields.ForeignKeyField("main.Currency", null=True)

    infos: fields.ReverseRelation["BankInfo"]
    accounts: fields.ReverseRelation["BankAccount"]
    
    def __str__(self) -> str:
        return self.name
    
    async def __aiter__(self) -> AsyncGenerator[BankAccount]:
        async for account in self.accounts:
            yield account
    
    async def to_dict(self, to_edit: bool = False) -> Dict[str, Any]:
        """
        |coro|
        
        Returns the bank's dictionary.

        Parameters
        -----------
        to_edit: :class:`bool`
            Whether to return the bank's edit dictionary.
            This will remove several keys from the dictionary.
        
        Returns
        -------
        :class:`dict`
            The bank's dictionary.
        """

        bank_dict = {
            "id": self.id,
            "cluster_id": self.cluster_id,
            "name": self.name,
            "emoji": self.emoji,
            "description": self.description,
            "default_currency_id": self.default_currency_id,
            "default_currency": await self.default_currency if self.default_currency_id else None,
            "infos": [
                await info.to_abstract() async for info in self.infos.all()
            ],
        }

        if to_edit:
            bank_dict.pop("cluster_id", None)
            bank_dict.pop("default_currency_id", None)

        return bank_dict

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
        
    async def create_account(self, owner: OwnerShortcutable, currency: Currency=None) -> BankAccount:
        """|coro|

        Create a new account for the given owner.

        Parameters
        -----------
        owner: :class:`~taho.abc.OwnerShortcutable`
            The owner of the account.
        
        Returns
        --------
        :class:`.BankAccount`
            The created account.
        """
        shortcut = await db_utils.create_shortcut(ShortcutType.owner, owner)
        if not currency:
            currency = await db_utils.get_default_currency(self.cluster_id)
        balance = 0
        return await BankAccount.create(
            bank=self,
            owner_shortcut=shortcut
            )
# todo change everything about CurrencyAmount it's fucking stupid what i done

    async def _create_default_account(self) -> BankAccount:
        """|coro|

        Create the default account for the bank.
        This account is purely indicative, it is useful to make
        the balance bewteen charges and interests.

        .. warning::
            Use force_create only if you know what you are doing.
            You have to check if the account already exists.
            Having two default accounts is not allowed and provoke
            bugs in the code.

        Returns
        --------
        :class:`.BankAccount`
            The default account.
        """
        # if not default_user:
        default_user = await db_utils.get_default_user(self.cluster_id)
        default_currency = await db_utils.get_default_currency(self.cluster_id)
        
        return await BankAccount.create(
            bank=self, 
            owner=default_user,
            currency=default_currency,
            )
    
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
    
    async def edit(self, **options) -> None:
        """|coro|

        Edits the bank.

        Parameters
        -----------
        options: :class:`dict`
            The fields to edit.
            The keys are the field names.
        """
        edit_dict = {}
        queries = []
        for option, value in options.items():
            if option == "infos":
                queries.append(self.infos.all().delete())
                if value:
                    for info in value:
                        queries.append(info.to_db_access(
                            BankInfo,
                            self
                        ))

            else:
                edit_dict[option] = value
        
        self.update_from_dict(edit_dict)

        await self.save()
        await asyncio.gather(*queries)

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

class BankInfo(Info):
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

    bank = fields.ForeignKeyField("main.Bank", related_name="infos")

@overload
async def create_transaction_operation(
    from_account: BankAccount, 
    to_account: BankAccount,
    money: float,
    currency: Currency = ...,
    description: str = ...,
    return_transactions: bool = ...,
) -> Optional[Tuple[BankingTransaction]]:
    ...

@overload
async def create_transaction_operation(
    from_account: BankAccount, 
    to_account: BankAccount,
    amount: CurrencyAmount,
    description: str = ...,
    return_transactions: bool = ...,
) -> Optional[Tuple[BankingTransaction]]:
    ...

async def create_transaction_operation(
    from_account: BankAccount, 
    to_account: BankAccount, 
    money: Optional[float] = None,
    currency: Optional[Currency] = None,
    amount: Optional[CurrencyAmount] = None, 
    description: Optional[str] = None,
    return_transactions: bool = False
    ) -> Optional[Tuple[BankingTransaction]]:
    """|coro|

    Create a transaction operation between two accounts.

    ``money`` or ``amount`` must be provided, but not both.

    If ``currency`` is not provided, it is assumed to be the same as the
    ``from_account``'s currency (in case ``money`` is provided).

    Parameters
    ----------
    from_account: :class:`.BankAccount`
        The account debiting the money.
    to_account: :class:`.BankAccount`
        The account crediting the money.
    money: Optional[:class:`float`]
        The amount transfered.
    currency: Optional[:class:`.Currency`]
        The currency of the money transfered.
    amount: :class:`~taho.CurrencyAmount`
        The amount transfered.
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
    TypeError
        If none of ``money`` or ``amount`` is provided,
        or if both are provided.

    Returns
    -------
    Optional[Tuple[:class:`.BankingTransaction`]]
        The transactions created.
        If the ``return_transactions`` parameter is ``False``, 
        then ``None`` is returned.
    
    """
    if money is None and amount is None:
        raise TypeError("Either money or amount must be provided.")
    elif money is not None and amount is not None:
        raise TypeError("Only one of money or amount can be provided.")
    if (money and money < 0) or (amount and amount.amount < 0):
        raise ValueError("Amount must be positive.")
    

    if money is not None:
        if currency is None:
            currency = await from_account.currency
        amount = money
    elif amount is not None:
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
        
        .. collapse:: owner_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.OwnerShortcut`
                - :attr:`null` ``True``
            
            Python: Optional[:class:`~taho.database.models.OwnerShortcut`]
        
        .. collapse:: balance

            Tortoise: :class:`tortoise.models.fields.DecimalField`

                - :attr:`max_digits` ``32``
                - :attr:`decimal_places` ``2``
                - :attr:`default` ``0``
            
            Python: :class:`float`
        
        .. collapse:: currency

            Tortoise: :class:`tortoise.models.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Currency`

            Python: :class:`~taho.database.models.Currency`
        
        .. collapse:: is_default

            Tortoise: :class:`tortoise.models.fields.BooleanField`

                - :attr:`default` False
            
            Python: :class:`bool`
    
    Attributes
    ----------
    bank: :class:`.Bank`
        The bank the account belongs to.
    owner_shortcut: Optional[:class:`~taho.database.models.OwnerShortcut`]
        The shortcut to the owner of the account (user, ...).
        If ``None``, the account is the bank's default account.
    balance: :class:`float`
        The balance of the account.
    currency: :class:`~taho.database.models.Currency`
        The currency in which the balance is.
    is_default: :class:`bool`
        Whether the account is the default account of the user.
        This account will receive salaries, interests, etc.
    """
    class Meta:
        table = "bank_accounts"

    id = fields.IntField(pk=True)

    bank = fields.ForeignKeyField("main.Bank", related_name="accounts")
    owner_shortcut = fields.ForeignKeyField("main.OwnerShortcut", null=True)
    balance = fields.DecimalField(max_digits=32, decimal_places=2, default=0)
    currency = fields.ForeignKeyField("main.Currency")
    is_default = fields.BooleanField(default=False)

    transactions: fields.ReverseRelation["BankingTransaction"]

    @overload
    async def credit(
        self, 
        money: float, 
        currency: Currency = ...
    ) -> None:
        ...
    
    @overload
    async def credit(
        self,
        amount: CurrencyAmount, 
    ) -> None:
        ...

    async def credit(self, 
        money: Optional[float] = None,
        currency: Optional[Currency] = None,
        amount: Optional[CurrencyAmount] = None,
    ) -> None:
        """|coro|

        Credit the account with an amount of money.

        
        ``money`` or ``amount`` must be provided, but not both.

        If ``currency`` is not provided, it is assumed to be the same as the
        ``account``'s currency (in case ``money`` is provided).

        Parameters
        -----------
        money: Optional[:class:`float`]
            The amount of money to credit the account with.
        currency: Optional[:class:`~taho.database.models.Currency`]
            The currency in which the money is.
        amount: Optional[:class:`~taho.CurrencyAmount`]
            The amount of money to credit the account with.
        
        Raises
        -------
        TypeError
            If neither ``money`` or ``amount`` is provided,
            or if both are provided.
        """
        
        # Checks are done by :func:`.BankAccount._convert`
        converted_amount = await self._convert(
            money=money,
            currency=currency,
            amount=amount
        )

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
            Please use :meth:`.BankAccount.credit` instead.
        """
        self.balance += amount
        await self.save()
    
    @overload
    async def _convert(
        self,
        money: float,
        currency: Currency = ...,
    ) -> float:
        ...
    
    @overload
    async def _convert(
        self,
        amount: CurrencyAmount,
    ) -> float:
        ...
    
    async def _convert(
        self,
        money: Optional[float] = None,
        currency: Optional[Currency] = None,
        amount: Optional[CurrencyAmount] = None
    ) -> float:
        """|coro|

        Convert an amount of money to the account's currency.

        ``money`` or ``amount`` must be provided, but not both.

        If ``currency`` is not provided, it is assumed to be the same as the
        ``account``'s currency (in case ``money`` is provided).

        Parameters
        -----------
        money: Optional[:class:`float`]
            The amount of money to convert.
        currency: Optional[:class:`~taho.database.models.Currency`]
            The currency in which the money is.
        amount: Optional[:class:`~taho.CurrencyAmount`]
            The amount of money to convert.
        
        Raises
        -------
        TypeError
            If neither ``money`` or ``amount`` is provided,
            or if both are provided.

        Returns
        -------
        :class:`float`
            The converted amount.
        """
        if money is None and amount is None:
            raise TypeError("Either money or amount must be provided.")
        elif money is not None and amount is not None:
            raise TypeError("Only one of money or amount can be provided.")
        
        if money is not None:
            if currency is None:
                # The currency is the same as the account's currency
                # No need to do anything else

                converted_amount = money
            else:
                # Convert the money to the account's currency

                amount = CurrencyAmount(money, currency)
                converted_amount = await amount.convert(await self.currency)

        elif amount is not None:
            # Convert the amount to the account's currency

            converted_amount = await amount.convert(await self.currency)

        return converted_amount

    @overload
    async def transfer(
        self,
        to: BankAccount, 
        money: float, 
        currency: Currency = ...,
        description: str = ...,
    ) -> None:
        ...
    
    @overload
    async def transfer(
        self,
        to: BankAccount, 
        amount: CurrencyAmount, 
        description: str = ...,
    ) -> None:
        ...
    
    async def transfer(self,
        to: BankAccount, 
        money: Optional[float] = None,
        currency: Optional[Currency] = None,
        amount: Optional[CurrencyAmount] = None,
        description: Optional[str] = None,
    ) -> None:
        """|coro|

        Transfer money from the account to another account.

        ``money`` or ``amount`` must be provided, but not both.

        If ``currency`` is not provided, it is assumed to be the same as the
        ``account``'s currency (in case ``money`` is provided).

        Parameters
        -----------
        to: :class:`.BankAccount`
            The account to transfer money to.
        money: Optional[:class:`float`]
            The amount of money to transfer.
        currency: Optional[:class:`~taho.database.models.Currency`]
            The currency in which the money is.
        amount: Optional[:class:`~taho.CurrencyAmount`]
            The amount of money to transfer.
        description: Optional[:class:`str`]
            The description of the transaction.
        
        Raises
        -------
        TypeError
            If neither ``money`` or ``amount`` is provided,
            or if both are provided.
        ~taho.exceptions.QuantityException
            If the amount to transfer is greater than the account's balance.
        """
        
        # Convertion of the amount to the account's currency
        # to be able to compare it to the account's balance

        # Checks are done by :func:`.BankAccount._convert`

        converted_amount = await self._convert(
            money=money,
            currency=currency,
            amount=amount
        )

        if converted_amount > self.balance:
            raise QuantityException(
                "The amount to transfer is greater than the account's balance."
            )

        # Debit the account with the converted_amount
        await self._credit(-converted_amount)

        # Use the parameters of the transfer to credit the other account
        # This way, an additional conversion is not needed
        await to.credit(
            money=money,
            currency=currency,
            amount=amount,
        )

        await create_transaction_operation(
            self, 
            to, 
            money=money,
            currency=currency,
            amount=amount,
            description=description
            )

    


class BankingTransaction(BaseModel):
    """
    Represents a transaction from/to a :class:`.BankAccount`.

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

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` ``32``
                - :attr:`decimal_places` ``2``
            
            Python: :class:`float`
        
        .. collapse:: currency

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Currency`

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
        The currency in which the amount is.
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
    currency = fields.ForeignKeyField("main.Currency")
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