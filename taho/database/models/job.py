from tortoise.models import Model
from tortoise import fields
from enum import IntEnum

__all__ = (
    "SalaryCondition",
    "RewardType",
    "Job",
    "JobReward",
)

class SalaryCondition(IntEnum):
    """
    Represents the salary conditions of a job.
    """
    NO_SALARY = 0
    EVERY_DAYS = 1
    EVERY_DAYS_IF_WORKING = 2
    EVERY_WEEKS = 3
    EVERY_WEEKS_IF_WORKING = 4

class RewardType(IntEnum):
    """
    Represents the reward types of a job.
    """
    MONEY = 0
    ITEM = 1
    STAT = 2

class Job(Model):
    class Meta:
        table = "jobs"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.GuildCluster", related_name="jobs")
    name = fields.CharField(max_length=255)
    role = fields.ForeignKeyField("main.Role", related_name="jobs")
    salary = fields.DecimalField(max_digits=32, decimal_places=2, null=True)
    salary_condition = fields.IntEnumField(SalaryCondition, default=SalaryCondition.EVERY_DAYS)
    cooldown = fields.IntField(null=True)

class JobReward(Model):
    class Meta:
        table = "job_rewards"
    
    id = fields.IntField(pk=True)

    job = fields.ForeignKeyField("main.Job", related_name="rewards")
    is_cost = fields.BooleanField(default=False)
    reward_type = fields.IntEnumField(RewardType, default=RewardType.MONEY)
    item = fields.ForeignKeyField("main.Item", related_name="job_rewards", null=True)
    use_durability = fields.BooleanField(null=True)
    stat = fields.ForeignKeyField("main.Stat", related_name="job_rewards", null=True)
    amount = fields.IntField()
    chance = fields.DecimalField(max_digits=3, decimal_places=2)
    quantity_min = fields.IntField(null=True)
    quantity_max = fields.IntField(null=True)