# Bayesian MUlti-Risk Assessment

---

## Install on Ubuntu GNU \\ Linux 12.04   


#### 1. Install requirements
```sh
sudo apt-get install python-pip python-virtualenv virtualenvwrapper python-wxgtk2.8 build-essentials libpng-dev libmysqlclient-dev
```

#### 2. Configure virtualenvwrapper

 [Read http://virtualenvwrapper.readthedocs.org/en/latest/ for more infos] 
 
 If you want to use a non-standard directory to store your virtualenvs
 you should comment out (or delete) `/etc/bash_completion.d/virtualenvwrapper`
 and then add these instructions in `~/.bashrc` or `~/.profile` :

 ```sh
export WORKON_HOME=$HOME/dev/virtualenvs
export VIRTUALENVWRAPPER_LOG_DIR="$WORKON_HOME"
export VIRTUALENVWRAPPER_HOOK_DIR="$WORKON_HOME"
source /etc/bash_completion.d/virtualenvwrapper
```

#### 3. Create the new env (with virtualenvwrapper)
 ```sh
 $ mkvirtualenv bymur-dev
 ```

#### 4. (ugly workaround) While the new virtualenv is activated link the external wxPython module inside it
 ```sh
 (bymur_dev)$ ln -s /usr/lib/python2.7/dist-packages/wx* $VIRTUAL_ENV/lib/python2.7/site-packages/
 ```

#### 5. Check out the git repository
 ```sh
 (bymur_dev)$ git clone git@gitlab.bo.ingv.it:perfetti/bymur.git
 ```

#### 6. Install requested python modules
 ```sh
 (bymur_dev)$ pip install --upgrade distribute
 (bymur_dev)$ pip install -r requirements.txt
 ```
