# ./wsadmin.sh -lang jython -f create_sharedlib.py

import os
import re
import sys


def createSharedLib(server_name):
    target = AdminConfig.getid('/Cell:Cell_dmgr/Node:Node_' + server_name + '/')
    print target
    print AdminConfig.create('Library', target, [['name', 'JavaAssist'], ['classPath', '/opt/IBM/WebSphere/shared_libraries/javassist-3.24.0-GA.jar;'], ['isolatedClassLoader', 'true']])
    print AdminConfig.create('Library', target, [['name', 'HTTPClient'], ['classPath', '/opt/IBM/WebSphere/shared_libraries/httpcore-4.4.12.jar;/opt/IBM/WebSphere/shared_libraries/httpclient-4.5.10.jar;/opt/IBM/WebSphere/shared_libraries/httpmime-4.5.10.jar;'], ['isolatedClassLoader', 'true']])
    AdminConfig.save()
    
try:
    print 'start' 
    createSharedLib("server1")
    print 'end'
except:
    print "***** Unexpected error while creating shared library:", sys.exc_info(), " *****"
    raise

