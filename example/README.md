# WAW example application

WAW applications reside typically in their own repositories and refer to the WAW to buld and deploy the conversation applications. 
example-app is in WAW repository just to give the the new user an example of the overall setup. Please mind, your own applications showd reside out of the repository clone of WAW. 

#Configuration
You can run the scripts by subsequent calling of the WAW scripts. The parameters can be provided from command line or from configuration files typically shared by all the scripts.

Application developer can use one or more configurations files which are passed to script using -c command line parameter. We recommend to split configuration to at least two parts. 

The first one (private.cfg) contains private information (passwords) and information specific to each of the users.
The file is typicaly derived form private.cfg.template and it is not kept in the repository.

The second one (e.g. cz_app.cfg) is typically shared in repository by all the users of the application. It is specific to the application and typicaly contains configuration for names of files and directories used during building of the application.

If the application has several variants e.g. language versions, they have typically their own variant of the configuration file (e.g cz_app.cfg en_app.cfg)