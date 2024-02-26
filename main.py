import logging
import logging.config
import os
import uuid
from flask import Flask, render_template
from azure.appconfiguration.provider import load
import datetime

# setup loggers
logging.config.fileConfig('logging.cfg', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)

app = Flask(__name__,template_folder='templates')

def load_config(): 
    app_config = {"title": "Azure App Configuration Demo", "message": "Howdy All!"}
    if connection_string := os.environ.get("AZURE_APPCONFIG_CONNECTION_STRING"):
        # Connect to Azure App Configuration using a connection string.
         logger.info(f"Loading config from Azure App Configuration {connection_string}")
         if config := load(connection_string=connection_string):
            app_config = config

    return app_config 

@app.route('/redistest')
def redistest():
    # using redis
    import redis
    logger.info("Testing Redis connection")
    redis_pw = os.environ["REDIS_PASSWORD"]
    r = redis.Redis(host='appworkloads-redis-master-0.appworkloads.svc.cluster.local', port=6379, db=0,password=redis_pw)
    logger.info(f"Connected to Redis: {r}")
    key = str(uuid.uuid4())
    logger.info(f"Setting date for key {key}")
    r.set(key, datetime.datetime.now().isoformat())
    return_val= r.get(key)
    connection =f"Connected to Redis: {r}"
    message=f"The date value for key:{key} from Redis is {return_val}"

    return render_template('redis.html', message=message, connection=connection)

@app.route('/')
def index():
    config = load_config()
    logger.info("Rendering index.html with config")
    return render_template('index.html', config=config)

#app.run(host='0.0.0.0', port=5000, debug=True)