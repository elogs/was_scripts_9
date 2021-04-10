# ./wsadmin.sh -lang jython -f create_jdbcprov.py

import os
import re
import sys


def createJDBCProvider(server_name):
    node_name = server_name
    target = AdminConfig.getid('/Cell:Cell_dmgr/Node:' + node_name + '/')
    print target
    jname = ['name', 'DB2 Using IBM JCC Driver']
    jimpclassname = ['implementationClassName', 'com.ibm.db2.jcc.DB2ConnectionPoolDataSource']
    jclasspath = ['classpath', '${DB2_JCC_DRIVER_PATH}/db2jcc4.jar;${UNIVERSAL_JDBC_DRIVER_PATH}/db2jcc_license_cu.jar;${DB2_JCC_DRIVER_PATH}/db2jcc_license_cisuz.jar;${PUREQUERY_PATH}/pdq.jar;${PUREQUERY_PATH}/pdqmgmt.jar']
    jdbcAttr = [jname, jimpclassname, jclasspath]
    AdminConfig.create('JDBCProvider', target, jdbcAttr)
    AdminConfig.save()

try:
    print 'start' 
    
    createJDBCProvider("server1")

    print 'end'
except:
    print "***** Unexpected error while creating JDBC datasource:", sys.exc_info(), " *****"
    raise

AdminConfig.save()

