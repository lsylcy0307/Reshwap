from flask import Flask

from flask_mail import Mail, Message
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lvillereshwap@gmail.com'
app.config['MAIL_PASSWORD'] = 'rqmhlktqoykoahhx'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

from app import routes
