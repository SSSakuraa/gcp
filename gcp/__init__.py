from flask import Flask
from views.networks import networks
from views.instances import instances
from views.errors import errors
from views.fee import Fee
app = Flask(__name__)
app.register_blueprint(networks)
app.register_blueprint(instances)
app.register_blueprint(errors)
fee = Fee()