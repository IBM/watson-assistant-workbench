# Logging
This file shows how to set up and use logging in WAW scripts.

## Logging levels
Default logging level can be seen in the following table. The numeric value corresponds to 'importance' of the messages. By default, all messages with logging level equal to or greater than the logging level are printed (to console, or a file). Filters can be set to handle only certain logging levels. Custom logging levels can also be defined.

| Level    | Numeric value |
|----------|-------|
| CRITICAL | 50    |
| ERROR    | 40    |
| WARNING  | 30    |
| INFO     | 20    |
| DEBUG    | 10    |
| NOTSET   | 0     |

## Logger configuration
In WAW scripts, the log level option and verbosity flag can be set as CLI arguments. For example, when calling a WAW script, you can use `--log=ERROR` to show only ERROR and CRITICAL messages. You can also add a `-v` or `--verbose` for additional INFO messages.

Most logger options can be set in a config file. A basic configuration can be seen in [`logging_config.ini`](/scripts/logging_config.ini) file.

An important thing to note here is that there is a _root_ logger, which listens to ALL messages regardles of what the calling script is, but also a _common_ logger, which is needed to be able to set up different loggers for concrete scripts in an unified way. Its sole purpose is to connect all the loggers under one parent logger and then upon getting the logger check, whether or not there is a logger called `common.[script name]`. If there is no such logger, only the _root_ logger is used. This is not possible to do with the _root_ logger only.

### Setting log level
The _root_ logger has two handlers - _defaultFileHandler_ and _defaultConsoleHandler_. You can set the log level in the _root_ logger settings, which **limits**  the log level for ALL messages. That means, that if _root_ logger's level is set to WARNING, messages of log level DEBUG and INFO will not get passed to any of the logger's handlers. 

You can also set the _root_ level to UNSET and set the handlers individually. For example, you might want to output messages of all levels to a log file and show only errors and criticals in the console. For that you need to set the _root_ logger level to UNSET or DEBUG, _defaultFileHandler_ to DEBUG and _defaultConsoleHandler_ to ERROR.

### Creating custom logger for a concrete script

To create custom logger for a single script:
1) Create a logger with any name you want, but preferably according to the script name (e.g. 'cfgCommons'), create custom handlers
2) Set-up the logger:
    ```ini
    [logger_<SCRIPT_NAME>]
    qualname=common.<SCRIPT_NAME>
    handlers=<CUSTOM_HANDLERS>
    ```
    _qualname_ - must be set according to the script name without '.py' suffix, note the 'common' prefix which is needed to be able to use the root logger even without creating a logger for each script.

    _handlers_ - add any handlers you want to use for the logger

3) Add the loggers name to the [loggers] keys and the custom handlers to the [handlers] keys


#### Example
A logger that logs separately all the errors from `cfgCommons.py` to a file called `customLog.log`

```ini
 [loggers]
 keys=root,common,cfgCommons,...

 [handlers]
 keys=customHandler,...

 [formatters]
 keys=form

 [logger_cfgCommons]
 qualname=common.cfgCommons
 handlers=customFileHandler

 [handler_customFileHandler]
 class=FileHandler
 formatter=form
 level=ERROR
 args=('customLog.log',)
```

## Logging a message
To log a message in a WAW script, first import logging and call:

```python
import logging
```

and then get the logger instance:

```python
logger = getScriptLogger(__file__)
```

The `__file__` argument is needed to be able to set special logger for this concrete script. Instructions to do so will be shown below.

If the script is the first one to get called (it's not used as a module), you also need to load the configuration for the logger:

```python
if __name__ == '__main__':
    setLoggerConfig(level, verbose)
```

This loads the `logging_config.ini` file and sets the loggers. The `level` and `verbose` arguments are optional. If `level` is specified, it sets the root logger and all its handlers to this log level. If `verbose` is set to true, the logger prints additional INFO messages. In WAW scripts, both `level` and `verbose` options are set as CLI arguments. If `level` is specified as an argument, the settings from the `logging_config.ini` are overriden. There is no option of setting these values in the WAW config files.

Now you can log a message with desired log level:
```
logger.debug('This is a debug message.')
logger.info('This is an informational message.')
logger.verbose('Some additional info.')
logger.warning('This is a warning.')
logger.error('This is an errror message.')
logger.critical('Something really bad happened.')
```


## More information
For more information, refer to the [official documentation](https://docs.python.org/3/library/logging.html).