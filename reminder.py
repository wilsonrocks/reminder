import argparse

import peewee

import secrets

dbfile = "reminder.db"
db = peewee.SqliteDatabase(dbfile)

class ReminderModel(peewee.Model):
    class Meta:
        database = db

class Anniversary(ReminderModel):
    date = peewee.DateField()

    name = peewee.CharField()

db.create_tables([Anniversary],safe=True)
