# OVIL - Objects and Verbs Issue Logger

## Getting started
These instructions will get you an instance of the _**Objects and Verbs Issue Logger**_ application up and running.

## Prerequisistes
This tutorial assumes the following:
```
> You have Python version 3.6.x

> You are issuing the following terminal commands within the application root folder (the same where the MANIFEST.in and setup.py files are)

> Your firewall allows external connections to port 5000

> SonarW and sonar gateway are installed in their default location

> You use Chrome or Firefox as your browser
```
## Creating a virtual environment `(venv)`

1. Whenever you have to install several python modules to accomplish something it's always recommended to do so in a _`virtual environment`_. So start the installation by creating one:  
```console
python3 -m venv ovil-venv
```

2. Now activate the newly created virtual environment:
```console
source ovil-venv/bin/activate
```
> _Note the `(ovil-venv)` before the username in the command line. It means that you'll now be running python and pip commands within a virtual, secure environment. If things go wrong for some reason, just remove the recently created _`ovil-venv`_ folder and repeat steps 1 and 2._

## Generating the Wheel (.whl) file

1. _**`While in the virtual environment`**_, you'll generate a _`wheel`_ file in order to install it. Do it so by first installing _`wheel`_ with:
```console
pip3 install wheel
```

2. Now create the _`.whl`_ file by running:
```console
 python3 setup.py bdist_wheel
 ```
 > _This will generate a folder called `dist`. Within it you'll find the recently created file called `ovil-1.0.0-py3-none-any.whl`_

## Installing OVIL

1. Now that you created and activated the _`virtual environment`_ and created the _`.whl`_ file, you will have to install the application by issuing the following command (it will also install the required dependencies):  
```console
pip3 install dist/ovil-1.0.0-py3-none-any.whl
```

## Setting up the _`ovil-config.cfg`_ file

1. The application will generate a default _`ovil-config.cfg`_ file located at _`~/.ovil-instance`_. For the application to work properly, you'll have to set some variables in this file.
> _**`ATTENTION!`** All file paths within the _`ovil-config.cfg`_ file **have** to be **`absolute`**_.

2. Following is a description of each variable found inside the _`ovil-config.cfg`_ file:
    * _**`DB_CONN_STRING`**_  
    This is the connection string to _`SonarW`_ and is exactly like a normal MongoDB string.   
    >_e.g. `'mongodb://admin:jS0nar$@127.0.0.1:27117/admin'`_

    * _**`SGW_PATH` and `SGW_CONFIG_PATH`**_  
    These global variables tell the application where to find the _`sonar gateway`_ and the _`.json`_ file to pass as the _`--config`_ parameter to the gateway

    * _**`GITHUB_APP_REPO_OWNER` and  `GITHUB_APP_REPO_NAME`**_  
    These are the variables that tell the application which GitHub account (_`GITHUB_APP_REPO_OWNER`_) and repository (_`GITHUB_APP_REPO_NAME`_) the issues should be logged to. They are used to replace the placeholders in the following URL: _`'https://api.github.com/:repo_owner/:repo_name/issues'`_  
    >_e.g.  
    `GITHUB_APP_REPO_OWNER='jsonar'`  
    `GITHUB_APP_REPO_NAME='sonarg'`  
    yields to:  
    `'https://api.github.com/jsonar/sonarg/issues'`_

    * _**`GITHUB_APP_PEM_PATH`**_  
    This variable tells the application where the _`.pem`_ file containing the _`private key`_ is located. This key must be generated in the configuration page of the application at the [GitHub website](https://github.com/settings/apps). 

    * _**`GITHUB_APP_ID`**_  
    This is the ID number of the application and can also be found at its configuration page at the [GitHub website](https://github.com/settings/apps).

    > _**`ATTENTION!`** Don't forget to **`install`** the `application` in the `GitHub account`. Otherwise GitHub will ignore the application attempts of logging issues._

## Setting up and running the Flask server:

1.  OVIL is now installed on your virtual environment. The next step is to setup Flask. First you need to tell Flask which application it should run by issuing the following command:
```console
export FLASK_APP=ovil
```
2. You are now ready to start your Flask application! The following command will start Flask and set it up to listen to external connections to port `5000`:
```console
flask run --host=0.0.0.0 --port=5000
```

3. _*`(OPTIONAL)`*_ If you'd like to see debug messages being printed to the terminal where your application is running you must tell Flask to run in `development` mode by issuing the following command and then repeating _**`step 2`**_:
```console
export FLASK_ENV=development
```
> _The default value to this environment variable is `production`_

4. _*`(OPTIONAL)`*_ Alternatively you can run Flask _locally_ by skipping _**`step 2`**_ and issuing the following command instead. That way you will have to access you application by typing _`localhost:5000`_ in your browser.
```console
flask run
```

* _**CONGRATULATIONS!**_ The configuration is finished. You should be able to access the application from your browser.