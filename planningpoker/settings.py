"""Setting defaults."""

HOST = '127.0.0.1'
PORT = 8080

# The key length must be a multiple of 16.
# What's happening below is not the way it should be done but at this phase of development
# it doesn't matter.
COOKIE_SECRET_KEY = ('really secret key yo' + '!' * 30)[:16]
