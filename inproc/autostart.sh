#!/bin/bash
cd /home/uadm/inproc
case "$(pgrep -f 'python3 extractip.py' | wc -w)" in
0) echo "$(date) restart extractip.py" >> ./autostart.log
   nohup python3 extractip.py > extractip.log 2>&1 &
   ;;
1) # All ok
   ;;
*) echo "$(date) kill extractip.py" >> ./autostart.log
   kill $(pgrep -f 'python3 extractip.py' | awk '{print $1}')
   ;;
esac

case "$(pgrep -f 'python3 recognizeip.py' | wc -w)" in
0) echo "$(date) restart recognizeip.py" >> ./autostart.log
   nohup python3 recognizeip.py > recognizeip.log 2>&1 &
   ;;
1) # All ok
   ;;
*) echo "$(date) kill recognizeip.py" >> ./autostart.log
   kill $(pgrep -f 'python3 recognizeip.py' | awk '{print $1}')
   ;;
esac
