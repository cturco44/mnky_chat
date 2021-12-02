#!/bin/bash

# Get system environment variables
systemenv=`cat /opt/elasticbeanstalk/deployment/custom_env_var | tr '\n' ',' | sed 's/%/%%/g' | sed 's/export //g' | sed 's/$PATH/%(ENV_PATH)s/g' | sed 's/:$PYTHONPATH//g' | sed 's/$LD_LIBRARY_PATH//g'`
systemenv=${systemenv%?}
systemenv=`echo $systemenv | sed 's/,/",/g' | sed 's/=/="/g'`
systemenv="$systemenv\""

# Get Django environment variables, comment if not using python-dotenv
djangoenv=`cat /opt/elasticbeanstalk/deployment/django_env_var | tr '\n' ',' | sed 's/%/%%/g' | sed 's/export //g'`
allenv="$systemenv,$djangoenv"

# Create daemon configuration script
daemonconf="[program:daphne]
command=daphne -b :: -p 5000 <Django Root App>.asgi:application

directory=/var/app
user=ec2-user
numprocs=1
stdout_logfile=/var/log/stdout_daphne.log
stderr_logfile=/var/log/stderr_daphne.log
autostart=true
autorestart=true
startsecs=10

; Need to wait for currently executing tasks to finish at shutdown.
; Increase this if you have very long running tasks.
stopwaitsecs = 600

; When resorting to send SIGKILL to the program to terminate it
; send SIGKILL to its whole process group instead,
; taking care of its children as well.
killasgroup=true

environment=$allenv
"

# Create the Supervisor conf script
echo "$daemonconf" | sudo tee /etc/supervisor/conf.d/daemon.conf

# Reread the Supervisor config
supervisorctl reread

# Update Supervisor in cache without restarting all services
supervisorctl update

# Start/restart processes through Supervisor
supervisorctl restart daphne
