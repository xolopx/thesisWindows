from flask import Flask
from database import globs

customApp = Flask(__name__)
db = globs.Globs()

import webapp.streamer