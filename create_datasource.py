# WSADMIN_DIR=/opt/IBM/WebSphere/AppServer/bin/
# $WSADMIN_DIR/wsadmin.sh -username user -password pass -lang jython -f <this_script_filename>

import os
import re
import sys


def createDataSource(dsName, node, jndiName, dbName, dbServer, dbUser, dbPass, dbPort):
    providerName='MySQL JDBC Provider'
    userAlias='sitcell/MySQLdbCredentials'
    parentNode='/Cell:sitcell/Node:' + node + '/' + 'JDBCProvider:' + providerName + '/'
    
    jdbc_provider = AdminConfig.getid(parentNode)
    data_source = AdminConfig.getid('/JDBCProvider:'+providerName+'/DataSource:' + dsName + '/')

    name = ['name', dsName]
    jndiName = ['jndiName', jndiName]
    description = ['description', dsName]
    helperclass = ['datasourceHelperClassname', 'com.ibm.websphere.rsadapter.ConnectJDBCDataStoreHelper']
    #cmp = ['containerManagedPersistence', 'true']
    
    authDataAlias = ['authDataAlias' , userAlias]
    mapConfigprop=["mappingConfigAlias", "none"] 
    mapConfigs=[authDataAlias , mapConfigprop] 
    mappingConfig=["mapping", mapConfigs]

    ds_properties = [name, jndiName, description, helperclass, authDataAlias, mappingConfig]
    data_source = AdminConfig.create('DataSource', jdbc_provider, ds_properties)

    #Set the DB URL dbName, dbServer, dbUser, dbPass, dbPort
    propSet = AdminConfig.create('J2EEResourcePropertySet', data_source, [])
    AdminConfig.create('J2EEResourceProperty', propSet, [["name", "databaseName"], ["value", dbName]])
    AdminConfig.create('J2EEResourceProperty', propSet, [["name", "serverName"], ["value", dbServer]])
    AdminConfig.create('J2EEResourceProperty', propSet, [["name", "user"], ["value", dbUser]])
    AdminConfig.create('J2EEResourceProperty', propSet, [["name", "password"], ["value", dbPass]])
    AdminConfig.create('J2EEResourceProperty', propSet, [["name", "portNumber"], ["value", dbPort]])

    AdminConfig.save()

    print 'Creating JDBC Datasource on server sucessfull with datasource:' + dsName + "on " + node

def updateConnectionPool(dsName, node):
    providerName='MySQL JDBC Provider'
    parentNode='/Cell:sitcell/Node:' + node + '/' + 'JDBCProvider:' + providerName + '/'

    MINEDataSource=AdminConfig.getid(parentNode + 'DataSource:' + dsName + '/')
    conpool = AdminConfig.showAttribute(MINEDataSource, 'connectionPool')
    AdminConfig.modify(conpool, '[[maxConnections 500]]')
    AdminConfig.modify(conpool, '[[connectionTimeout 600]]')
    #print AdminConfig.showall(conpool)
    AdminConfig.save()


#MAIN
try:

    print 'start' 
    targetnode = "sit-live"
    createDataSource('ds_name1', targetnode, 'jdbc/ds1', 'ds1_dbName', 'db.server.com', 'dbuser', 'dspass', '3306')

    updateConnectionPool('ds_name1', targetnode)


    print 'end'
except:
    print "***** Unexpected error while creating JDBC datasource:", sys.exc_info(), " *****"
    raise


