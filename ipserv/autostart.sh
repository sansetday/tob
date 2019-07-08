#!/bin/bash
cd /home/fly/python/ipserv/py
case "$(pgrep -f 'python3 server.py' | wc -w)" in
0) echo "$(date) restart server.py" >> ./autostart.log
   nohup python3 server.py > server.log 2>&1 &
echo 'Start'
   ;;
1) # All ok
   ;;
*) echo "$(date) kill server.py" >> ./autostart.log
   kill $(pgrep -f 'python3 server.py' | awk '{print $1}')
   ;;
esac
