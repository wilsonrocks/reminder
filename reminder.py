import argparse,datetime

import peewee

dbfile = "reminder.db"
db = peewee.SqliteDatabase(dbfile)

class ReminderModel(peewee.Model):
    class Meta:
        database = db

class Anniversary(ReminderModel):
    name = peewee.CharField()
    date = peewee.DateField()


class Contact(ReminderModel):
    name = peewee.CharField()
    email = peewee.CharField()
    phone = peewee.CharField()

class Bank_Holiday(ReminderModel):
    date = peewee.DateField()

def is_posting_day(target):
    answer = True

    if target.isoweekday() in [6,7]: #ignore weekends
        answer = False

    bank_holidays = Bank_Holiday.select()

    for hol in bank_holidays:
        if (target.month,target.day) == (hol.date.month,hol.date.day): #ignore bank holidays
            answer = False
    return(answer)

def days_until(target):
    this_year = datetime.date.today().year
    date_this_year = datetime.date(this_year,target.month,target.day)
    date_next_year = datetime.date(this_year+1,target.month,target.day)

    delta = date_this_year - datetime.date.today()

    if delta < datetime.timedelta(seconds=0):
        delta = date_next_year - datetime.date.today()

    return delta


db.create_tables([Anniversary,Contact,Bank_Holiday],safe=True)

