# WSADMIN_DIR = /opt/IBM/WebSphere/AppServer9/bin
# $WSADMIN_DIR/wsadmin.sh -lang jython -f <this_script>.py [applicationA, applicationB, applicationC, applicationC] \
#                                                          [type1_env, type2_env, type3_env, type4_env] \
#                                                          [1.0, 2.0, 2.1] \
#                                                          [sit, uat1, uat2] <war_location>

import os
import re
import sys
import time

NODE_SIT_EDITORIAL="WebSphere:cell=sitcell,node=sit-type1_env,server=sit-type1_env"
NODE_SIT_STAGING="WebSphere:cell=sitcell,node=sit-type2_env,server=sit-type2_env"
NODE_SIT_LIVE="WebSphere:cell=sitcell,node=sit-type3_env,server=sit-type3_env"
NODE_SIT_PUBLIC="WebSphere:cell=sitcell,cluster=cluster-sit-type3_env"

NODE_UAT1_EDITORIAL="WebSphere:cell=uatcell_dmgr,node=uat-type1_env,server=uat-type1_env"
NODE_UAT1_STAGING="WebSphere:cell=uatcell_dmgr,node=uat-type2_env,server=uat-type2_env"
NODE_UAT1_LIVE="WebSphere:cell=uatcell_dmgr,node=uat-type3_env-0,server=uat-type3_env-0"
NODE_UAT1_PUBLIC="WebSphere:cell=uatcell_dmgr,cluster=cluster-uat1-pc1"

NODE_UAT2_EDITORIAL="WebSphere:cell=uatcell_dmgr,node=uat2-type1_env,server=uat2-type1_env"
NODE_UAT2_STAGING="WebSphere:cell=uatcell_dmgr,node=uat2-type2_env,server=uat2-type2_env"
NODE_UAT2_LIVE="WebSphere:cell=uatcell_dmgr,node=uat2-type3_env-0,server=uat2-type3_env-0"
NODE_UAT2_PUBLIC="WebSphere:cell=uatcell_dmgr,node=uat2-type3_env-1,server=uat2-type3_env-1"


def installWar(warPath, fileName, appName, prettyName, dataSource, node, propFile, contextRoot):
    print 'Params warPath:{}, file:{}, appName:{}, prettyName:{}, ds:{}, node:{}, prop:{}, croot:{}'.format(warPath, fileName, appName, prettyName, dataSource, node, propFile, contextRoot)
    options = '-nopreCompileJSPs \
                -distributeApp \
                -nouseMetaDataFromBinary \
                -appname {} \
                -createMBeansForResources \
                -noreloadEnabled \
                -nodeployws \
                -validateinstall warn \
                -noprocessEmbeddedConfig \
                -filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755 \
                -noallowDispatchRemoteInclude \
                -noallowServiceRemoteInclude \
                -asyncRequestDispatchType DISABLED \
                -nouseAutoLink \
                -noenableClientModule \
                -clientMode isolated \
                -novalidateSchema \
                -contextroot {} '.format(appName, contextRoot)

    resource='-MapResRefToEJB [[ {} "" {},WEB-INF/web.xml {} javax.sql.DataSource {} "" "" "" ]] '.format(prettyName, fileName, dataSource, dataSource)
    modules='-MapModulesToServers [[ {} {},WEB-INF/web.xml {} ]] '.format(prettyName, fileName, node)
    virtualHost='-MapWebModToVH [[ {} {},WEB-INF/web.xml default_host ]] '.format(prettyName, fileName)
    metadata='-MetadataCompleteForModules [[ {} {},WEB-INF/web.xml true ]] '.format(prettyName, fileName)
    envEntry='-MapEnvEntryForWebMod [[ {} {},WEB-INF/web.xml backbase/config String "" {} ]] '.format(prettyName, fileName, propFile)

    if dataSource == 'none':
        AdminApp.install(warPath, '[' + options + modules + virtualHost + metadata + envEntry + ']')
    else: 
        AdminApp.install(warPath, '[' + options + resource + modules + virtualHost + metadata + envEntry + ']')
        AdminConfig.save()
        AdminApp.edit(appName, '[ -MapSharedLibForMod [\
        [ {} META-INF/application.xml JavaAssist-3 ]\
        [ {} {},WEB-INF/web.xml JavaAssist-3 ]]]'.format(appName, prettyName, fileName))

    AdminConfig.save()
    
    isReady = AdminApp.isAppReady(appName)
    while (isReady == "false"):
        time.sleep(5)
        isReady = AdminApp.isAppReady(appName)
    print "*******************************************************"
    print("*** " + appName + " is ready for launching - server restart is recommended") 
    print "*******************************************************"    
    

    
#MAIN
try:
    app=sys.argv[0];        # supported: applicationA, applicationB, applicationC, applicationB
    target=sys.argv[1];     # target server type e.g. type1_env / type2_env / type3_env
    version=sys.argv[2];    # ex. 1.0 
    env_set=sys.argv[3];    # supported: sit, uat1, uat2
    war_dir=sys.argv[4];    # location of war files, must be ending in '/' ex: /opt/IBM/WebSphere/wars/
    
    # [TODO] add input validations, ex war_dir must be ending in /
    
    pretty_name_app_a="\"Application A\""
    pretty_name_app_b="\"Application B\""
    pretty_name_app_c="\"Application C\""
    pretty_name_app_c="\"Application D\""

    was_nodes_sit={"type1_env":NODE_SIT_EDITORIAL, "type2_env":NODE_SIT_STAGING, "type3_env":NODE_SIT_LIVE, "type4_env":NODE_SIT_PUBLIC}
    was_nodes_uat1={"type1_env":NODE_UAT1_EDITORIAL, "type2_env":NODE_UAT1_STAGING, "type3_env":NODE_UAT1_LIVE, "type4_env":NODE_UAT1_PUBLIC}
    was_nodes_uat2={"type1_env":NODE_UAT2_EDITORIAL, "type2_env":NODE_UAT2_STAGING, "type3_env":NODE_UAT2_LIVE, "type4_env":NODE_UAT2_PUBLIC}
    
    
    # Set environment set specific parameters
    if env_set == "sit":
       was_nodes = was_nodes_sit
       app_name_prefix = version
       
    elif env_set == "uat1":
       was_nodes = was_nodes_uat1
       app_name_prefix = "uat1-" + version
       
    elif env_set == "uat2":
       was_nodes = was_nodes_uat2
       app_name_prefix = "uat2-" + version
  

    # Set ESL specific parameters  
    if target == 'type1_env':
        wasnode=was_nodes["type1_env"]
        appA_file_name='applicationA-type1_env.war'
        
    elif target =='type2_env':
        wasnode=was_nodes.get("type2_env")
        appA_file_name='applicationA.war'
        
    elif target == 'type3_env':
        wasnode=was_nodes["type3_env"]
        appA_file_name='applicationA.war'
        
    elif target == 'type4_env':
        wasnode=was_nodes["type4_env"]
        appA_file_name='applicationA.war'


    # Set war application specific parameters        
    if app == 'applicationA':    
        propertyFile='/opt/some_path/config/appA.properties'
        appA_AppName=app_name_prefix + '-applicationA-' + target        
        ds='jdbc/appA'
        fullPath=''.join([war_dir, appA_file_name])
        installWar(fullPath, appA_file_name, appA_AppName, appA_file_name, ds, wasnode, propertyFile, '/')
             
    elif app == 'applicationC': 
        fn='applicationC.war'
        name=app_name_prefix + '-applicationC-' + target  
        ds='none'
        propertyFile='/opt/some_path/config/appC.properties'
        fullPath=''.join([war_dir, fn])    
        installWar(fullPath, fn, name, pretty_name_app_c, ds, wasnode, propertyFile, '/appC/contextroot')
       
    elif app == 'applicationB':
        fn='applicationB.war'
        name=app_name_prefix + '-applicationB-' + target
        ds='none'
        propertyFile='/opt/some_path/applicationB.properties'
        fullPath=''.join([war_dir, fn])
        installWar(fullPath, fn, name, pretty_name_app_b, ds, wasnode, propertyFile, '/appB/contextroot')
        
    elif app == 'applicationD':     
        fn='applicationD.war'
        name=app_name_prefix + '-applicationD-' + target
        ds='jdbc/appD'
        propertyFile='/opt/some_path/applicationD.properties'
        fullPath=''.join([war_dir, fn])
        installWar(fullPath, fn, name, pretty_name_app_d, ds, wasnode, propertyFile, '/appD/contextroot')    
    
except:
    print "***** Unexpected error while installing", sys.exc_info(), " *****"
    raise



