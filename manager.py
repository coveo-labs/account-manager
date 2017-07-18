import requests
import yaml
import json
import hashlib
import uuid
from timeit import default_timer as timer
from time import sleep


class InvalidConfig(Exception):
    pass


class Manager:
	success = 'success'
	error = 'error'

	def __init__(
			self, 
			push_url="pushdev.cloud.coveo.com", 
			api_url="platformdev.cloud.coveo.com"):

		config = yaml.safe_load(open("config.yml"))
		self.push_url = push_url
		self.api_url = api_url

		if 'coveo_api_key' in config:
			self.coveo_api_key = config['coveo_api_key']
		else:
			raise InvalidConfig("Failed to find coveo API in config file")

		if 'push_api_key' in config:
			self.push_api_key = config['push_api_key']
		else:
			raise InvalidConfig("Failed to find Push API in config file")

		if 'secret' in config:
			self.secret = config['secret']
		else:
			raise InvalidConfig("Failed to find secret in config file")

		if 'org_id' in config:
			self.org_id = config['org_id']
		else:
			raise InvalidConfig("Failed to find org_id in config file")

		if 'source_id' in config:
			self.source_id = config['source_id']
		else:
			raise InvalidConfig("Failed to find source_id in config file")

		if 'push_name' in config:
			self.push_name = config['push_name']
		else:
			raise InvalidConfig("Failed to find push_name in config file")

	def generate_return_message(self, message_type, message):
		"""Base template for a generated message"""
		returnMessage = {
			'type': message_type,
			'message': message
		}
		return returnMessage

	def generate_error(self, message):
		"""Generate an error message"""
		return self.generate_return_message(self.error, message)

	def generate_success(self, message):
		"""Generate a success message"""
		return self.generate_return_message(self.success, message)

	def get_push_headers(self):
		"""The Push API headers"""
		headers = {
			"Content-Type": "application/json",
			"Authorization": "Bearer {}".format(self.push_api_key)
		}
		return headers

	def get_api_headers(self):
		"""The search API headers"""
		headers = {
			"Accept": "application/json"
		}
		return headers

	def generate_hashed_password(self, password, salt):
		"""Generates a hashed password with a given password and salt
		This uses a secret thats in the config.yml
		"""
		return hashlib.sha512(self.secret + password + salt).hexdigest()

	def get_push_url(self, doc_id):
		"""Generate the push url"""
		return "https://{}/v1/organizations/{}/sources/{}/documents?documentId={}".format(self.push_url, self.org_id, self.source_id, doc_id)

	def get_user_url(self, username):
		"""Get the url for a user search"""
		return """https://{}/rest/search/?numberOfResults=1&fieldsToInclude=%5B"%40username"%2C%20"%40password"%2C"%40salt"%2C"%40uniqueid"%5D&q=%40source%3D{}%20%40username%3D{}&access_token={}&organizationId={}&maximumAge=0""".format(self.api_url, self.push_name, username, self.coveo_api_key, self.org_id)

	def get_user(self, username):
		"""Gets the user profile"""
		r = requests.get(self.get_user_url(username), headers=self.get_api_headers())
		profile = json.loads(r.text)['results']
		if len(profile) > 0:
			profile[0]['raw']['uniqueid'] = profile[0]['uniqueId']
			return self.generate_success(profile[0]['raw'])
		else:
			return self.generate_error("Could not find user - {}".format(r.status_code))

	def put_user(self, username, password):
		"""Update a user's info"""
		salt = uuid.uuid4().hex
		data = {
			"username": username,
			"password": self.generate_hashed_password(password, salt),
			"salt": salt
		}
		r = requests.put(
			self.get_push_url("account://{}".format(username)),
			data=json.dumps(data),
			headers=self.get_push_headers())
		return "Added user - {}".format(r.status_code)

	def add_user(self, username, password):
		"""Add a user into the system"""
		user = self.get_user(username)
		if user['type'] == self.error:
			self.put_user(username, password)
			return self.generate_success('Added user')
		else:
			return self.generate_error('User already exists')

	def validate_user(self, username, password):
		"""Validate a user to see if he logged in"""
		user = self.get_user(username)
		if user['type'] == self.error:
			return user
		else:
			entered_password = self.generate_hashed_password(password, user['message']['salt'])
			if(user['message']['password'] == entered_password):
				return user
			else:
				return self.generate_error('Wrong user/password')

	def modify_password(self, username, current_password, new_password):
		"""Modify the password of a user"""
		valid_user = self.validate_user(username, current_password)
		if valid_user['type'] == self.success:
			self.put_user(username, new_password)
			return self.generate_success('Changed password')
		else:
			return self.generate_error('Wrong password')

	def wait_until_user_created(self, username, timeout = 90):
		"""Waits until a user is created in the system then returns
		his profile
		Timeouts after 90 seconds by default, change it by changing the function argument"""
		start = timer()
		while True:
			if start - timer() > timeout:
				return self.generate_error('Timed out')
			else:
				user = self.get_user(username)
				if user['type'] != self.error:
					return user
				else:
					sleep(5)
