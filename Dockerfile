FROM python:3.9.14-slim-bullseye

COPY requirements.txt ./    
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update && apt install -y --no-install-recommends \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /srv/bot
RUN mkdir /srv/bot/log

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY *.py /srv/bot/


CMD ["/usr/bin/supervisord"]
