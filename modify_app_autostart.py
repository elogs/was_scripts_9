# Jython Script to modify auto-start of apps. 
# usage: "/opt/IBM/WebSphere/AppServer9/bin/wsadmin.sh -username wasadmin -password wasadmin -lang jython -f tmp.py disable "appName_A, appName_B, appName_C""

import os
import re
import sys

#MAIN
try:
    option=sys.argv[0] # enable or disable
    apps_list=sys.argv[1].strip("[]").split(','); # app-names list separated by ','

    print 'start' 
    
    if option == "enable":
       enable_value = 'true'
    if option == "disable":
       enable_value = 'false'
    
    for app in apps_list:
        #app_id = AdminConfig.getid('/Deployment:'+app+'/ApplicationDeployment:/')
        app_id = AdminConfig.showAttribute(AdminConfig.getid('/Deployment:'+app+'/ApplicationDeployment:/'), 'targetMappings')
        AdminConfig.modify(app_id.strip("[]"), '[[enable '+enable_value+']]')
        AdminConfig.save()
        print "**** Successfully modified auto-start of "+app+"to: "+option
        
    print 'end'
except:
    print "***** Unexpected error:", sys.exc_info(), " *****"
    raise




