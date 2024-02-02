FROM nexus.gaig.com:5500/pcf/platform/python-slim-bullseye:3.11.4
LABEL maintainer="DL-GAI.PCF.CloudOps@GAIG.COM>"

# RUN apt-get update
# RUN apt-get -y install gcc
RUN adduser johndoe
RUN chown johndoe:johndoe /usr/local/bin

#Install the libraries
WORKDIR /home/johndoe

RUN python -m venv venv
RUN  . venv/bin/activate

COPY --chown=johndoe:johndoe config config
COPY --chown=johndoe:johndoe main.py logging.cfg requirements.txt docker_run.sh ./
RUN venv/bin/pip install  --trusted-host nexus.gaig.com -r requirements.txt
RUN chmod +x docker_run.sh

USER root
ENTRYPOINT ["./docker_run.sh"]

EXPOSE 5000 