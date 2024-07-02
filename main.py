from collections import ChainMap
import logging
import logging.config
import os
import uuid
from flask import Flask, render_template
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
import datetime
from flask_bootstrap import Bootstrap5
from pyservicebinding import binding

# setup loggers
logging.config.fileConfig('logging.cfg', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)

app = Flask(__name__,template_folder='templates')
bootstrap = Bootstrap5(app)

def load_config(): 

    ## set the default config
    app_config = {"title": "PySimple App Demo", "message": "Howdy All .. Looks like Azure App Configuration isn't available!"}
    
    try:
        sb = binding.ServiceBinding()
        bindings_list = sb.bindings("cloud-config")
        if bindings_list:
            service_conn = dict(ChainMap(*bindings_list))
            if connection_string := service_conn.get("host"):
            
             # Connect to Azure App Configuration using a connection string.
             logger.info(f"Loading config from Azure App Configuration {connection_string}")
             app_config_client = AzureAppConfigurationClient.from_connection_string(connection_string)
             allitems = app_config_client.list_configuration_settings(key_filter="*")
             for item in allitems:
                    app_config[item.key] = item.value
            
    except binding.ServiceBindingRootMissingError as msg:
      # log the error message and retry/exit
      logger.exception("SERVICE_BINDING_ROOT env var not set. Add a service binding to the app and try again.")
     
    return app_config 

@app.route('/testredis')
def redistest():
    import redis
    try:
        logger.info("Creating ServiceBinding object")
        sb = binding.ServiceBinding()
        logger.info("Testing Redis connection")
        
        if bindings_list := sb.bindings("redis"):

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
     
    return render_template('redis.html', message="SERVICE_BINDING_ROOT env var not set.<br>Add a service binding to the app and try again.", connection=None)

@app.route('/')
def index():
    config = load_config()
    if 'title' not in config:
       config['title'] = "SimplePy App Demo"

    config["podName"]= os.getenv("POD_NAME","PODNAME")
    config['nodeName'] = os.getenv("NODE_NAME","NODENAME")
    config['podIp']  = os.getenv("POD_IP","PODIP")
    config['podNamespace']  = os.getenv("POD_NAMESPACE","PODNAMESPACE")

    logger.info("Rendering index.html with config")
    return render_template('index.html', config=config)