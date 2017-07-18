# coveo-account-manager
An attempt to use the Coveo search engine as an account database for a website.
Simple features include:
 1. Account creation
 2. Account login
 3. Password changes

 This should never be used in a real product, this is purely for showing the flexibility of the Coveo search.

 ## Description
 This project is meant as a test case to demonstrate the capabilities and flexibility of the Coveo Search.
 It is meant to replace the traditional database system in a full-stack for a website.
 So intead of using something like, MySQL or SQLITE to store your usernames and password, this uses Coveo.
 Of course, that has it's downsides. Account creation and password modification can take up for 60 seconds sometimes.
 Plus sometimes the dev platform goes down, so that means your login also goes down.

 ## Install
 #### Python:
1. Download/clone this repo
2. Install the dependencies
3. See the example for sample code on how to use
 #### Coveo platform:
1. Create a new Push source
    1. Shared
    2. Create an API key and put it in the `config.yml` file under `push_api_key`
    3. Add the name of the source under `push_name` in the `config.yml`
    4. Add the ID of the source under `source_id` in the `config.yml`
2. Add these mappings:
    1. `Map password with %[password]`
    2. `Map username with %[username]`
    3. `Map salt with %[salt]`
3. Create an API key
    1. Add the permission `Search	> Execute queries > Enable`
    2. Put it in the `config.yml` file under `coveo_api_key`
4. Add your organization name under `org_id` in the `config.yml`
5. As for the `secret` in `config.yml`, just act like a protection paladin and smash your keyboard with random letters

 ## Dependencies
1. `pip install pyyaml`
2. `pip install requests`

 ## Examples
 Import the manager
 
```python
from manager import Manager
```

Then create an instance of the class

```python
manager = Manager()
```

Once you created your instance, you can do the following things:

```python
# Add a user
manager.add_user(username, password)

# Get a user
manager.get_user(username)

# Validate a user
manager.validate_user(username, password)

# Modify a password
manager.modify_password(username, password, new_password)

# Wait until a user is created
manager.wait_until_user_created(username, timeout=90)

# All function will return a standard message format
# which looks like this
{
    'type' : manager.success || manager.error # I use the "||" here as an or for the possible return types
    'message' : 'Some message' || {'some' : 'json'}
}
```

 ## Additional notes
 This was tested on Python 2.7.13 using platformdev
 
 Although it SHOULD work on other python version and cloud platforms, I have not tested.
