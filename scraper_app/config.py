from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import os

#hardcoded fallbacks
test_outage_bool = False
test_outage = "false"
data_keeping_ip = "0.0.0.0:8000"

#try to read environment variables
try:
    data_keeping_ip = os.environ["DATA_KEEPING_IP"]
except:
    pass
try:
    test_outage = os.environ["TEST_OUTAGE"]
except:
    pass

#try to read from configMap
try:
    with open("/etc/config/data-keeping-ip", "r") as f:
        data_keeping_ip = f.read()
except:
    pass

try:
    with open("/etc/config/test-outage", "r") as f:
        test_outage = f.read()
except:
    pass

#setup dynamic reconfig for test_outage

class EventHandler(LoggingEventHandler):
    def on_modified(self, event):
        print(event)
        global test_outage,data_keeping_ip,test_outage_bool
        with open("/etc/config/test-outage", "r") as f:
            test_outage = f.read()
            if test_outage == "true":
                test_outage_bool = True
            else:
                test_outage_bool = False
            print(test_outage_bool)
        with open("/etc/config/data-keeping-ip", "r") as f:
            data_keeping_ip = f.read()

try:
    path = "/etc/config"
    eventHandler = EventHandler()
    observer = Observer()
    observer.schedule(eventHandler,path,recursive=True)
    observer.start()
except:
    print("Could not setup dynamic config!")