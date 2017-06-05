###
# Make this actually random!
# >>> import os
# >>> os.urandom(24)
# '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
###

import os


SECRET_KEY = 'm\t\x83.\xc0\xfaJ\x00\x16\xb9*,\xa7\xb0\xc0\x89\xac\x1f\xb0\r\x9f\xed1\xb6'
HTML_SAFE = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///submissions.db'
UPLOADED_IMAGES_DEST = './'
RECAPTCHA_PUBLIC_KEY = '6Le1LiQUAAAAAOM6zy72Onng715UbCbR_YY_JCe9'
RECAPTCHA_PRIVATE_KEY = '6Le1LiQUAAAAAB9qyZgdau3312TjCa5QXfFsu7d0'
APPLICATION_WORKING_DIRECTORY = os.getcwd()
