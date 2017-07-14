from manager import Manager
from time import sleep

test = Manager("myorgsarecursed", "uuzynxmjnz35hbsjufgvkgcgqa-myorgsarecursed")

print test.validate_user("test2", "new password")

while True:
    user = test.get_user("test2")
    print user
    if len(user) > 0:
        break
    else:
        sleep(5)

print "Valid password:"
print test.validate_user("test2", "some password")

print "Mod password:"
print test.modify_password("test2", "some password", "new password")

while True:
    user = test.validate_user("test2", "new password")
    print user
    if len(user) > 0 and user['type'] != 'error':
        break
    else:
        sleep(5)
