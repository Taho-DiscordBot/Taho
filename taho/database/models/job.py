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
from ..enums import SalaryCondition, RewardType

__all__ = (
    "Job",
    "JobReward",
)


class Job(Model):
    class Meta:
        table = "jobs"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.ServerCluster", related_name="jobs")
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