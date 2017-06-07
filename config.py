###
# Make this actually random!
# >>> import os
# >>> os.urandom(24)
# '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
###

import os
import socket


APPLICATION_WORKING_DIRECTORY = os.getcwd()
HTML_SAFE = False
LOCAL = socket.gethostname() != 'test.balloon-juice.com'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
MAX_PICTURES = 5
RECAPTCHA_PRIVATE_KEY = '6Le1LiQUAAAAAB9qyZgdau3312TjCa5QXfFsu7d0'
RECAPTCHA_PUBLIC_KEY = '6Le1LiQUAAAAAOM6zy72Onng715UbCbR_YY_JCe9'
SECRET_KEY = 'm\t\x83.\xc0\xfaJ\x00\x16\xb9*,\xa7\xb0\xc0\x89\xac\x1f\xb0\r\x9f\xed1\xb6'
SQLALCHEMY_DATABASE_URI = 'sqlite:///submissions.db'
UPLOADED_IMAGES_DEST = './'

WORDPRESS = {
        'testing': {
                'base_url': 'https://test.balloon-juice.com/index.php/wp-json',
                'client_key': '3Xh5uQ3FTY2X',
                'client_secret': 'ZUo6GuQovNUFhFmP4XNOBsnvtphs5O1cEOPolpcBx1GjmBh9',
                'resource_owner_key': u'rrg8d6gIE6Jx0Ghs6VYpBcaL',
                'resource_owner_secret': u'tU5hFTJNmUSm2v631ykw5X4g3IEHDBMBUV6XLxw7kuGHu8cM'
        }
}
