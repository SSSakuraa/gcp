import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask


from views.networks import networks
from views.instances import instances
from views.errors import errors
from views.fee import get_fee



app = Flask(__name__)
app.register_blueprint(networks)
app.register_blueprint(instances)
app.register_blueprint(errors)


fee = get_fee()


scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=get_fee,
    trigger=IntervalTrigger(seconds=5),
    id='get_fee',
    name='get fee from website every five seconds',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

