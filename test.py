from manager import Manager
from time import sleep, time
import unittest

class TestStringMethods(unittest.TestCase):

    test_user = str(time())
    test_pass = str(time())
    test_new_pass = test_user + test_pass
    test_manager = Manager()

    def test_01_adduser(self):
        user = self.test_manager.add_user(self.test_user, self.test_pass)
        self.test_manager.wait_until_user_created(self.test_user)
        self.assertEqual(user['type'], self.test_manager.success)

    def test_02_getuser(self):
        user = self.test_manager.get_user(self.test_user)
        self.assertEqual(user['type'], self.test_manager.success)

    def test_03_getuser_fail(self):
        user = self.test_manager.get_user(self.test_user + "asdasd")
        self.assertEqual(user['type'], self.test_manager.error)

    def test_04_validate(self):
        user = self.test_manager.validate_user(self.test_user, self.test_pass)
        self.assertEqual(user['type'], self.test_manager.success)

    def test_05_validate_fail_password(self):
        user = self.test_manager.validate_user(self.test_user, self.test_pass + "adsads")
        self.assertEqual(user['type'], self.test_manager.error)

    def test_06_validate_fail_username(self):
        user = self.test_manager.validate_user(self.test_user + "asdasd", self.test_pass)
        self.assertEqual(user['type'], self.test_manager.error)

    def test_07_validate_fail_both(self):
        user = self.test_manager.validate_user(self.test_user + "asdasd", self.test_pass + "adsads")
        self.assertEqual(user['type'], self.test_manager.error)

    def test_08_modify_password(self):
        user = self.test_manager.modify_password(self.test_user, self.test_pass, self.test_new_pass)
        timeout = 90
        start = timer()
        while True:
            if start - timer() > timeout:
                self.assertEqual(user['type'], self.test_manager.success)
            else:
                user = self.test_manager.validate_user(self.test_user, self.test_new_pass)
                if user['type'] != self.test_manager.error:
                    self.assertEqual(user['type'], self.test_manager.success)
                    break
                else:
                    sleep(5)

if __name__ == '__main__':
    unittest.main()