from collections import ChainMap
import logging
import logging.config
import os
import uuid
from flask import Flask, render_template
from azure.appconfiguration.provider import load
import datetime
from flask_bootstrap import Bootstrap5


# setup loggers
logging.config.fileConfig('logging.cfg', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)

app = Flask(__name__,template_folder='templates')
bootstrap = Bootstrap5(app)

def load_config(): 
    app_config = {"title": "Azure App Configuration Demo", "message": "Howdy All!"}
    if connection_string := os.environ.get("AZURE_APPCONFIG_CONNECTION_STRING"):
        # Connect to Azure App Configuration using a connection string.
         logger.info(f"Loading config from Azure App Configuration {connection_string}")
         if config := load(connection_string=connection_string):
            app_config = config

    return app_config 

@app.route('/testredis')
def redistest():
    import redis

    from pyservicebinding import binding
    try:
        logger.info("Creating ServiceBinding object")
        sb = binding.ServiceBinding()
        logger.info("Testing Redis connection")
    
        bindings_list = sb.all_bindings()
        service_conn = dict(ChainMap(*bindings_list))

        connection = redis.Redis(host=service_conn["host"], 
                                port=int(service_conn["port"]), 
                                db=0,password=service_conn["password"])
        
        key = str(uuid.uuid4())
        logger.info(f"Setting date for key {key}")
        connection.set(key, datetime.datetime.now().isoformat())
        return_val= connection.get(key)
       
        message=f"The date value for key:{key} from Redis is {return_val}"
        return render_template('redis.html', message=message, connection=connection)

    except binding.ServiceBindingRootMissingError as msg:
      # log the error message and retry/exit
      logger.exception("SERVICE_BINDING_ROOT env var not set. Add a service binding to the app and try again.")
      return render_template('redis.html', message="SERVICE_BINDING_ROOT env var not set.<br>Add a service binding to the app and try again.", connection=None)

@app.route('/')
def index():
    config = load_config()
    logger.info("Rendering index.html with config")
    return render_template('index.html', config=config)

#app.run(host='0.0.0.0', port=5000, debug=True)