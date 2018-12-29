import logging
import sys
logging.basicConfig(filename='/home/dad/reminder/reminder.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


import datetime


logger.info("Running script on {}".format(datetime.datetime.now()))

one_day = datetime.timedelta(days=1)
days_to_send = [2,7,21]
format = "%a %d %b"

import peewee
import requests

import secrets

dbfile = "/home/dad/reminder/reminder.db"
db = peewee.SqliteDatabase(dbfile)

class ReminderModel(peewee.Model):
    class Meta:
        database = db

class Anniversary(ReminderModel):
    name = peewee.CharField()
    date = peewee.DateField()

    def date_this_year(self):
        return datetime.date(datetime.date.today().year, self.date.month, self.date.day)


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
    return "Wilsons!!\n\n{} has a birthday on {}, this is in {} days.\nThe last posting day is {}.\nThey will be {}.".format(
        target.name,
        target.date_this_year().strftime(format),
        days_until(target.date),
        last_posting_day(target.date_this_year()).strftime(format),
        age(target.date)
        )


def send_SMS(occasion):

    params = {
            "sender" : "Wilsons!",
            "message" : format_message(occasion),
            "username" : secrets.SMS_LOGIN,
            "hash" : secrets.HASH,
            "numbers" : ",".join([contact.phone for contact in Contact.select()])
            }
    logger.info("sending SMS to {}".format(params["numbers"]))
    return requests.post("https://api.txtlocal.com/send/",data=params)

for occasion in Anniversary.select():
    print(occasion.name, occasion.date)
    if days_until(occasion.date) in days_to_send:
        logger.info("Sending reminder for {}".format(occasion.name))
        logger.info("texting {}".format(occasion.name))
        response = send_SMS(occasion)
    else:
        logger.debug("Not sending reminder for {}".format(occasion.name))

