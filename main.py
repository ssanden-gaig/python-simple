import logging
import logging.config
import os
from flask import Flask, render_template
from azure.appconfiguration.provider import load

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
    logger.info("Testing Redis")
    r = redis.Redis(host='mydb-redis-master.appworkloads.svc.cluster.local', port=6379, db=0)
    logger.info(r)
    logger.info("Setting key foo to bar")
    r.set('foo', 'bar')
    return_val= r.get('foo')
    logger.info(f"return_val: {return_val}")
    #render_template('index.html', return_val=return_val)

@app.route('/')
def index():
    config = load_config()
    logger.info("Rendering index.html with config")
    return render_template('index.html', config=config)

#app.run(host='0.0.0.0', port=5000, debug=True)