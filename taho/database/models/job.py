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
from tortoise.models import Model
from tortoise import fields
from taho.enums import SalaryCondition, RewardType

__all__ = (
    "Job",
    "JobReward",
    "JobCost",
)

class Job(Model):
    """Represents a job.

    .. container:: operations

        .. describe:: x == y

            Checks if two jobs are equal.

        .. describe:: x != y

            Checks if two jobs are not equal.
        
        .. describe:: hash(x)

            Returns the job's hash.
        
        .. describe:: str(x)

            Returns the job's name.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: name

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`

        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``jobs``
            
            Python: :class:`~taho.database.models.Cluster`
        
        .. collapse:: role

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Role`
                - :attr:`related_name` ``jobs``

            Python: :class:`~taho.database.models.Role`
        
        .. collapse:: salary_condition

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.SalaryCondition`
                - :attr:`default` :attr:`SalaryCondition.every_day`
            
            Python: :class:`~taho.enums.SalaryCondition`
        
        .. collapse:: salary

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` 32
                - :attr:`decimal_places` 2
                - :attr:`null` True
            
            Python: Optional[:class:`float`]
        
        .. collapse:: cooldown

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`null` True
            
            Python: Optional[:class:`int`]     
    
    Attributes
    -----------
    id: :class:`int`
        The job's ID.
    name: :class:`str`
        The job's name.
    cluster: :class:`~taho.database.models.Cluster`
        The cluster where the job is.
    role: :class:`~taho.database.models.Role`
        The role linked to the job.
        A user needs this role to be able to do the job.
    salary_condition: :class:`~taho.enums.SalaryCondition`
        The salary condition of the job.
    salary: Optional[:class:`float`]
        The salary of the job.
    cooldown: Optional[:class:`int`]
        The cooldown between two job executions.
    """
    class Meta:
        table = "jobs"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="jobs")
    name = fields.CharField(max_length=255)
    role = fields.ForeignKeyField("main.Role", related_name="jobs")
    salary = fields.DecimalField(max_digits=32, decimal_places=2, null=True)
    salary_condition = fields.IntEnumField(SalaryCondition, default=SalaryCondition.every_day)
    cooldown = fields.IntField(null=True)

    rewards: fields.ReverseRelation["JobReward"]
    costs: fields.ReverseRelation["JobCost"]

class JobReward(Model):
    """Represents a reward for a job.

    .. container:: operations

        .. describe:: x == y

            Checks if two rewards are equal.

        .. describe:: x != y

            Checks if two rewards are not equal.
        
        .. describe:: hash(x)

            Returns the reward's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
            
        .. collapse:: job

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Job`
                - :attr:`related_name` ``rewards``
            
            Python: :class:`~taho.database.models.Job`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.RewardType`
                - :attr:`default` :attr:`RewardType.money`
            
            Python: :class:`~taho.enums.RewardType`
        
        .. collapse:: item

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Item`
                - :attr:`related_name` ``job_rewards``
                - :attr:`null` True
            
            Python: Optional[:class:`~taho.database.models.Item`]
        
        .. collapse:: stat

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Stat`
                - :attr:`related_name` ``job_rewards``
                - :attr:`null` True
            
            Python: Optional[:class:`~taho.database.models.Stat`]
        
        .. collapse:: give_regeneration

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`null` True
            
            Python: Optional[:class:`bool`]
        
        .. collapse:: currency

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Currency`
                - :attr:`related_name` ``job_rewards``
                - :attr:`null` True
            
            Python: Optional[:class:`~taho.database.models.Currency`]
            
        .. collapse:: chance

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` 3
                - :attr:`decimal_places` 2

            Python: :class:`float`
        
        .. collapse:: amount_min

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`
        
        .. collapse:: amount_max

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`    

    Attributes
    -----------
    id: :class:`int`
        The reward's ID.
    job: :class:`~taho.database.models.Job`
        The job linked to the reward.
    type: :class:`~taho.enums.RewardType`
        The type of the reward.
    item: Optional[:class:`~taho.database.models.Item`]
        If the reward's type is :attr:`RewardType.item`, this is the item rewarded.
    stat: Optional[:class:`~taho.database.models.Stat`]
        If the reward's type is :attr:`RewardType.stat`, this is the stat rewarded.
    give_regeneration: Optional[:class:`bool`]
        If the reward's type is :attr:`RewardType.stat`, then a regenerable point
        will be rewarded.
    currency: Optional[:class:`~taho.database.models.Currency`]
        If the reward's type is :attr:`RewardType.money`, this is the currency in
        which the money is rewarded.
    chance: :class:`float`
        The chance of the reward.
        It is a percentage (0.0 to 1.0).
    amount_min: :class:`int`
        The minimum amount of the reward.
    amount_max: :class:`int`
        The maximum amount of the reward.
    

    .. note::

        For a fix amount of the reward, set :attr:`amount_min` and :attr:`amount_max`
        to the same value.
    """
    class Meta:
        table = "job_rewards"
    
    id = fields.IntField(pk=True)

    job = fields.ForeignKeyField("main.Job", related_name="rewards")
    type = fields.IntEnumField(RewardType, default=RewardType.money)
    item = fields.ForeignKeyField("main.Item", related_name="job_rewards", null=True)
    stat = fields.ForeignKeyField("main.Stat", related_name="job_rewards", null=True)
    give_regeneration = fields.BooleanField(null=True)
    currency = fields.ForeignKeyField("main.Currency", related_name="job_rewards", null=True)
    chance = fields.DecimalField(max_digits=3, decimal_places=2)
    amount_min = fields.IntField()
    amount_max = fields.IntField()

class JobCost(Model):
    """Represents a cost for a job.

    .. container:: operations

        .. describe:: x == y

            Checks if two costs are equal.

        .. describe:: x != y

            Checks if two costs are not equal.
        
        .. describe:: hash(x)

            Returns the cost's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
            
        .. collapse:: job

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Job`
                - :attr:`related_name` ``rewards``
            
            Python: :class:`~taho.database.models.Job`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.RewardType`
                - :attr:`default` :attr:`RewardType.money`
            
            Python: :class:`~taho.enums.RewardType`
        
        .. collapse:: item

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Item`
                - :attr:`related_name` ``job_rewards``
                - :attr:`null` True
            
            Python: Optional[:class:`~taho.database.models.Item`]
        
        .. collapse:: use_durabilty

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`null` True
            
            Python: Optional[:class:`bool`]
        
        .. collapse:: stat

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Stat`
                - :attr:`related_name` ``job_rewards``
                - :attr:`null` True
            
            Python: Optional[:class:`~taho.database.models.Stat`]
        
        .. collapse:: use_regeneration

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`null` True
            
            Python: Optional[:class:`bool`]
        
        .. collapse:: currency

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Currency`
                - :attr:`related_name` ``job_rewards``
                - :attr:`null` True
            
            Python: Optional[:class:`~taho.database.models.Currency`]
    
        .. collapse:: chance

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` 3
                - :attr:`decimal_places` 2

            Python: :class:`float`
        
        .. collapse:: amount_min

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`
        
        .. collapse:: amount_max

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`    

    Attributes
    -----------
    id: :class:`int`
        The cost's ID.
    job: :class:`~taho.database.models.Job`
        The job linked to the cost.
    type: :class:`~taho.enums.RewardType`
        The type of the cost.
    item: Optional[:class:`~taho.database.models.Item`]
        If the cost's type is :attr:`RewardType.item`, this is the item removed.
    use_durabilty: Optional[:class:`bool`]
        If the cost's type is :attr:`RewardType.item`, then durability will be
        removed to the item.
    stat: Optional[:class:`~taho.database.models.Stat`]
        If the cost's type is :attr:`RewardType.stat`, this is the stat removed.
    use_regeneration: Optional[:class:`bool`]
        If the cost's type is :attr:`RewardType.stat`, then a regenerable point
        will be removed.
    currency: Optional[:class:`~taho.database.models.Currency`]
        If the cost's type is :attr:`RewardType.money`, this is the currency in
        which the money is removed.
    chance: :class:`float`
        The chance of the cost.
        It is a percentage (0.0 to 1.0).
    amount_min: :class:`int`
        The minimum amount of the cost.
    amount_max: :class:`int`
        The maximum amount of the cost.
    

    .. note::

        For a fix amount of the cost, set :attr:`amount_min` and :attr:`amount_max`
        to the same value.
    """
    class Meta:
        table = "job_costs"
    
    id = fields.IntField(pk=True)

    job = fields.ForeignKeyField("main.Job", related_name="costs")
    type = fields.IntEnumField(RewardType, default=RewardType.money)
    item = fields.ForeignKeyField("main.Item", related_name="job_costs", null=True)
    use_durability = fields.BooleanField(null=True)
    stat = fields.ForeignKeyField("main.Stat", related_name="job_costs", null=True)
    use_regeneration = fields.BooleanField(null=True)
    currency = fields.ForeignKeyField("main.Currency", related_name="job_costs", null=True)
    chance = fields.DecimalField(max_digits=3, decimal_places=2)
    amount_min = fields.IntField()
    amount_max = fields.IntField()