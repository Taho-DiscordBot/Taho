from __future__ import annotations
from typing import Any, AsyncGenerator, Optional, Tuple, Union
from tortoise.models import Model
from tortoise import fields
from tortoise.signals import post_save
from .user import User
from taho.exceptions import Unknown

__all__ = (
    "Bank",
    "BankInfo",
    "BankAccount",
    "BankOperation",
)

class Bank(Model):
    """
    Represents a bank.

    The bank have a default account (the one that is used when no account_id is provided).
    The default account is purely indicative, it is useful to make 
    the balance bewteen charges and interests.
    All accounts charges are transfered to the default account;
    All accounts interests are transfered from the default account.

    .. container:: operations
        .. describe:: x == y
            Checks if two banks are equal.

        .. describe:: x != y
            Checks if two banks are not equal.
        
        ..describe:: hash(x)
            Returns the bank's hash.

        ..describe:: aiter(x)
            Returns an async iterator on the bank's accounts.
    
    Attributes
    -----------
    id: :class:`int`
        The bank's ID (DB primary key).
    name: :class:`str`
        The bank's name.
    
    """
    class Meta:
        table = "banks"

    id = fields.IntField(pk=True)
    
    cluster = fields.ForeignKeyField("main.ServerCluster", related_name="banks")
    user = fields.ForeignKeyField("main.User", related_name="banks")
    name = fields.CharField(max_length=255)
    emote = fields.CharField(max_length=255)

    infos: fields.ReverseRelation["BankInfo"]
    accounts: fields.ReverseRelation["BankAccount"]

    def __repr__(self) -> str:
        return f"<Bank {self.id}>"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Bank):
            return self.id == other.id
        return False
    
    def __hash__(self) -> int:
        return hash(self.__repr__())
    
    async def __aiter__(self) -> AsyncGenerator[BankAccount]:

        async for account in self.accounts:
            yield account

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
        Unknown
            If the account does not exist.

        Returns
        --------
        :class:`.BankAccount`
            The account.
        """

        if account_id is None:
            return await get_or_create_bank_default_account(self)
        async for account in self.accounts:
            if account.id == account_id:
                return account
        raise Unknown("Account not found.")

    async def get_operations(self, **kwargs) -> Tuple[BankOperation]:
        """
        Get all operations from the Bank.
        If no account_id is provided, all operations are returned.
        The operations are sorted by date (desc).
        """
        operations = []
        async for account in self.accounts:
            async for operation in account.operations:
                operations.append(operation)
        operations.sort(key=lambda operation: operation.date, reverse=True)
        return tuple(operations)

@post_save(Bank)
async def bank_post_save(_, instance: Bank, created: bool, *args, **kwargs) -> None:
    """
    Automatically create the default account for the bank when it is created.
    """
    if created:
        await get_or_create_bank_default_account(instance)

async def get_or_create_bank_default_account(bank: Bank, user: User=None) -> BankAccount:
    """
    Get or create the default account for the bank.
    """
    if not user:
        user = await User.get_or_create(cluster=bank.cluster, user_id=0)
        user = user[0]
    return (await BankAccount.get_or_create(bank=bank, user=user))[0]
    
class BankInfo(Model):
    """
    Represents a bank info.
    A bank info is an information that can be set by the bank owner.
    This is useful to store the bank's configuration
    (ex: the interest rate).
    """
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

async def create_transaction_operation(
    from_account: BankAccount, 
    to_account: BankAccount, 
    amount: int, description: str=None
    ) -> Tuple[BankOperation]:
    """
    Create a transaction operation between two accounts.
    """
    operations = (
        BankOperation(account=from_account, amount=-amount, description=description),
        BankOperation(account=to_account, amount=amount, description=description)
    )
    await BankOperation.bulk_create(operations)
    return operations

class BankAccount(Model):
    """
    Represents a bank account.
    A bank account is a bank account that can be used to store money.
    A bank account is owned by a user, or a bank (cf. Bank -> default account).

    You can transfer money from one account to another.
    """
    class Meta:
        table = "bank_accounts"

    id = fields.IntField(pk=True)

    bank = fields.ForeignKeyField("main.Bank", related_name="accounts")
    user = fields.ForeignKeyField("main.User", related_name="accounts")
    balance = fields.DecimalField(max_digits=32, decimal_places=2, default=0)
    is_default = fields.BooleanField(default=False)

    operations: fields.ReverseRelation["BankOperation"]

    async def receive(self, amount: float) -> None:
        """
        Receive money from another account.
        """
        self.balance += amount
        await self.save()

    async def transfer(self, to: BankAccount, amount: float, description: str=None) -> None:
        """
        Transfer money from this account to another one.

        Raises:
            ValueError: If the account doesn't have enought money (balance < amount).
        """
        if self.balance < amount:
            raise ValueError(f"Not enough money in account {self.id}")
        self.balance -= amount
        await self.save()
        await to.receive(amount)
        await create_transaction_operation(self, to, amount, description)

class BankOperation(Model):
    """
    Represents a bank operation.
    A bank operation is a bank operation that can be done on a bank account.

    When a transaction is done between two accounts, two bank operations are created:
    - One for the source account, with a negative amount;
    - One for the destination account, with a positive amount.
    """
    class Meta:
        table = "bank_operations"

    id = fields.IntField(pk=True)

    account = fields.ForeignKeyField("main.BankAccount", related_name="operations")
    amount = fields.DecimalField(max_digits=32, decimal_places=2)
    date = fields.DatetimeField(auto_now_add=True)
    description = fields.CharField(max_length=255, default="")