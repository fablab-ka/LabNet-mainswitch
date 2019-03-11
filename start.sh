#!/bin/sh

# Source: http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/

### BEGIN INIT INFO
# Provides: labnet-mainswitch
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Put a short description of the service here
# Description: Put a long description of the service here
### END INIT INFO

# Change the next 3 lines to suit where you install your script and what you want to call it
DIR=/home/pi/labnet-mainswitch
DAEMON=$DIR/main-mqtt.py
DAEMON_NAME=labnet-mainswitch

# Add any command line options for your daemon here
DAEMON_ARGS=""

# This next line determines what user the script runs as.
# Root generally not recommended but necessary if you are using the Raspberry Pi GPIO from Python.
DAEMON_USER=root

# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid

# The log file
LOG=/var/log/$DAEMON_NAME.log

. /lib/lsb/init-functions

do_start () {
    log_daemon_msg "Starting system $DAEMON_NAME daemon"
    create_log_file
    start-stop-daemon --start --quiet --background --pidfile $PIDFILE --make-pidfile --chuid $DAEMON_USER --chdir $DIR --startas /bin/bash -- -c "exec $DAEMON $DAEMON_ARGS >> $LOG 2>&1"
    log_end_msg $?
}
do_stop () {
    log_daemon_msg "Stopping system $DAEMON_NAME daemon"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}

create_log_file () {
    touch $LOG
    chown $DAEMON_USER $LOG
}

case "$1" in

    start|stop)
        do_${1}
        ;;

    restart|reload|force-reload)
        do_stop
        do_start
        ;;

    status)
        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
        ;;

    *)
        echo "Usage: service $DAEMON_NAME {start|stop|restart|status}"
        exit 1
        ;;

esac
exit 0
