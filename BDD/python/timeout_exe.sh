
TIMEOUT=8
timeout $TIMEOUT /usr/bin/python2.7 $1 $2
echo $?
