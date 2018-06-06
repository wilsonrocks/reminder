import logging
import sys
logging.basicConfig(filename='/home/dad/reminder/reminder.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


import datetime
import smtplib
import email.message


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

class Address(ReminderModel):
    line1 = peewee.CharField(null = True)
    line2 = peewee.CharField(null = True)
    line3 = peewee.CharField(null = True)
    line4 = peewee.CharField(null = True)

    def postal(self):
        non_blank = [k for k in [line1,line2,line3,line4] if k]
        return "\n".join(non_blank)

class Anniversary(ReminderModel):
    name = peewee.CharField()
    date = peewee.DateField()
#    address = peewee.ForeignKeyField(Address, related_name = 'residents', null = True)

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


def send_message(occasion):
    contacts = [contact.email for contact in Contact.select()]

    message = email.message.EmailMessage()
    message['To'] = contacts
    message['From'] = secrets.FROM_ADDR
    message['Subject'] = "{}'s Birthday in {} days!".format(occasion.name,days_until(occasion.date))
    message.set_content(format_message(occasion))
    return(message)

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




db.create_tables([Anniversary, Contact, Bank_Holiday, Address], safe=True)


server = smtplib.SMTP_SSL('smtp.gmail.com',465)
server.login(secrets.FROM_ADDR,secrets.PASSWORD)

for occasion in Anniversary.select():
    if days_until(occasion.date) in days_to_send:
        logger.info("Sending reminder for {}".format(occasion.name))
        message = send_message(occasion)
        contacts = [contact.email for contact in Contact.select()]

        server.sendmail(secrets.FROM_ADDR, ",".join(contacts), message.as_string())
        
        logger.info("Sending email:\n{}".format(message.as_string()))

        response = send_SMS(occasion)
    else:
        logger.debug("Not sending reminder for {}".format(occasion.name))

