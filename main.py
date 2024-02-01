import os
from flask import Flask, render_template, request, redirect, url_for, flash
from azure.appconfiguration.provider import load

app = Flask(__name__,template_folder='templates')

def load_config(): 
    app_config = {"title": "Azure App Configuration Demo", "message": "Howdy Everyone!"}
    if connection_string := os.environ.get("AZURE_APPCONFIG_CONNECTION_STRING",None):
        # Connect to Azure App Configuration using a connection string.
         if config := load(connection_string=connection_string):
            app_config = config

    return app_config 

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

app.run(host='0.0.0.0', port=5001, debug=True)