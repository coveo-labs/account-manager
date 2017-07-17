from manager import Manager
from time import sleep

test = Manager()

username = 'admin'
oldpassword = 'admin1213'
newpassword = 'admin'

print test.validate_user(username, oldpassword)

while True:
    user = test.get_user(username)
    print user
    if len(user) > 0 and user['type'] != 'error':
        break
    else:
        sleep(5)

print "Valid password:"
print test.validate_user(username, oldpassword)

print "Mod password:"
print test.modify_password(username, oldpassword, newpassword)

while True:
    user = test.validate_user(username, newpassword)
    print user
    if len(user) > 0 and user['type'] != 'error':
        break
    else:
        sleep(5)
