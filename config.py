###
# Make this actually random!
# >>> import os
# >>> os.urandom(24)
# '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
###

import os
import socket


ADMIN_USER = 'admin'
ADMIN_PASSWORD_HASH = '$5$rounds=535000$3ddsBs5kiD79ZJfy$ybeUpee2j5YxsB0DjS4pznu2RFP3Q4Fa.V9i.xiLwtC'
APPLICATION_WORKING_DIRECTORY = os.getcwd()
HTML_SAFE = False
LOCAL = socket.gethostname() != 'test.balloon-juice.com'
MAX_CONTENT_MB = 16
MAX_PICTURES = 7
MAX_CONTENT_LENGTH = MAX_CONTENT_MB * MAX_PICTURES * 1024 * 1024
MAX_SUBMISSIONS_PER_HOUR = 5
RECAPTCHA_PRIVATE_KEY = '6Le1LiQUAAAAAB9qyZgdau3312TjCa5QXfFsu7d0'
RECAPTCHA_PUBLIC_KEY = '6Le1LiQUAAAAAOM6zy72Onng715UbCbR_YY_JCe9'
SECRET_KEY = 'm\t\x83.\xc0\xfaJ\x00\x16\xb9*,\xa7\xb0\xc0\x89\xac\x1f\xb0\r\x9f\xed1\xb6'
SQLALCHEMY_DATABASE_URI = 'sqlite:///submissions.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True
TESTING = False
UPLOADED_IMAGES_DEST = './'
WTF_CSRF_TIME_LIMIT = 86400

CELERY_RESULT_BACKEND = 'amqp://guest@localhost//'
CELERY_BROKER_URL = 'amqp://guest@localhost//'

WORDPRESS = {
        'test': {
                'base_url': 'https://test.balloon-juice.com/index.php/wp-json',
                'client_key': '3Xh5uQ3FTY2X',
                'client_secret': 'ZUo6GuQovNUFhFmP4XNOBsnvtphs5O1cEOPolpcBx1GjmBh9',
                'resource_owner_key': u'rrg8d6gIE6Jx0Ghs6VYpBcaL',
                'resource_owner_secret': u'tU5hFTJNmUSm2v631ykw5X4g3IEHDBMBUV6XLxw7kuGHu8cM'
        },
        'production': {
                'base_url': 'https://www.balloon-juice.com/index.php/wp-json',
                'client_key': '4YfoPTVmuRUv',
                'client_secret': 'SJCMxlc0EkEDd6NhZfXu5BOjssKo1aTlgwRRczBRwnLUZufi',
                'resource_owner_key': u'Jmv0lNXcXYZTEmQ8OdkYPQMS',
                'resource_owner_secret': u'9jFXvKDVDJUWFMBUfu04gjgDpYEUvNBdwj60GicPc631kCWR'
        }
}
