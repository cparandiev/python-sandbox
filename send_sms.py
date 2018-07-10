# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'AC5a212b36e7e30bfd3556e5387e875c36'
auth_token = 'd2bbb88bb40f3bbf908ef2819cc81de2'
client = Client(account_sid, auth_token)

message = client.messages.create(
                              body='Denitoooo mnogoooooo mrunkaaaaa :D',
                              from_='+17027665831',
                              to='+359877768626'
                          )

print(message.sid)
