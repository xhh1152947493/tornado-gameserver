pid=$(cat ./main.pid)
kill -SIGTERM $pid
