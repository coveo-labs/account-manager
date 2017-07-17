import requests
import yaml
import json
import hashlib
import uuid

class InvalidConfig(Exception):
    pass

class Manager:

	def __init__(self, push_url="pushdev.cloud.coveo.com", api_url="platformdev.cloud.coveo.com"):
		config = yaml.safe_load(open("config.yml"))

		self.is_connected = False
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

	def generate_return_message(self, message_type, message):
		returnMessage = {
			'type' : message_type,
			'message' : message
		}
		return returnMessage

	def generate_error(self, message):
		return self.generate_return_message('error', message)

	def generate_success(self, message):
		return self.generate_return_message('success', message)

	def get_push_headers(self):
		headers = {
			"Content-Type" : "application/json",
			"Authorization" : "Bearer {}".format(self.push_api_key)
		}
		return headers

	def get_api_headers(self):
		headers = {
			"Accept" : "application/json"
		}
		return headers

	def generate_hashed_password(self, password, salt):
		return hashlib.sha512(self.secret + password + salt).hexdigest()

	def get_push_url(self, doc_id):
		return "https://{}/v1/organizations/{}/sources/{}/documents?documentId={}".format(self.push_url, self.org_id, self.source_id, doc_id)

	def get_user_url(self, username):
		return """https://{}/rest/search/?numberOfResults=1&fieldsToInclude=%5B"%40username"%2C%20"%40password"%2C"%40salt"%5D&q=%40source%3Daccounts%20%40username%3D{}&access_token={}&organizationId={}&maximumAge=0""".format(self.api_url, username, self.coveo_api_key, self.org_id)


	def get_user(self, username):
		r = requests.get(self.get_user_url(username), headers=self.get_api_headers())
		profile = json.loads(r.text)['results']
		if len(profile) > 0:
			return self.generate_success(profile[0]['raw'])
		else:
			return self.generate_error("Could not find user - {}".format(r.status_code))

	def put_user(self, username, password):
		salt = uuid.uuid4().hex
		data = {
			"username" : username,
			"password" : self.generate_hashed_password(password, salt),
			"salt" : salt
		}
		r = requests.put(self.get_push_url("account://{}".format(username)), data=json.dumps(data), headers=self.get_push_headers())
		return "Added user - {}".format(r.status_code)

	def add_user(self, username, password):
		user = self.get_user(username)
		if user['type'] == 'error':
			self.put_user(username, password)
			return self.generate_success('Added user')
		else:
			return self.generate_error('User already exists')

	def validate_user(self, username, password):
		user = self.get_user(username)
		if user['type'] == 'error':
			return user
		else:
			entered_password = self.generate_hashed_password(password, user['message']['salt'])
			if(user['message']['password'] == entered_password):
				return self.generate_success('match')
			else:
				return self.generate_error('Wrong user/password')

	def modify_password(self, username, current_password, new_password):
		valid_user = self.validate_user(username, current_password)
		if valid_user['type'] == 'success':
			self.put_user(username, new_password)
			return self.generate_success('Changed password')
		else:
			return self.generate_error('Wrong password')
