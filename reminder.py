import argparse,datetime
one_day = datetime.timedelta(days=1)
format = "%a %d %b"
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

def age(target):
    return (next_anniversary(target).year - target.year)

def next_anniversary(target):
    this_year = datetime.date.today().year
    date_this_year = datetime.date(this_year,target.month,target.day)

    if date_this_year > datetime.date.today():
        answer = date_this_year
    else:
        answer = datetime.date(this_year+1,target.month,target.day)
    return answer

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

    delta = next_anniversary(target) - datetime.date.today()

    return delta.days

def last_posting_day(target):
    delivery_day = target

    while is_posting_day(delivery_day) == False:
        delivery_day -= one_day

    posting_day = delivery_day - one_day
    return posting_day

def format_message(target):
    return "{} has a birthday on {}, this is in {} days. The last posting day is {}. They will be {}".format(
        occasion.name,
        occasion.date.strftime(format),
        days_until(occasion.date),
        last_posting_day(occasion.date).strftime(format),
        age(occasion.date)
        )

db.create_tables([Anniversary,Contact,Bank_Holiday],safe=True)

for occasion in Anniversary.select():
    print(format_message(occasion))
