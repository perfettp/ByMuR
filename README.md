# Bayesian MUlti-Risk Assessment

Bymur Software computes Risk and Multi-Risk associated to Natural Hazards.
In particular this tool aims to provide a final working application for
the city of Naples, considering three natural phenomena, i.e earthquakes,
volcanic eruptions and tsunamis.
The tool is the final product of BYMUR, an Italian project funded by the
Italian Ministry of Education (MIUR) in the frame of 2008 FIRB, Futuro in
Ricerca funding program.

---

## License

Bymur is released under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.

The XML Schema Definitions in the subdir `schemas/oq-nrmlib` are originally 
taken from the [GEM OpenQuake](https://github.com/gem/oq-engine) and are 
relased under the terms of the GNU Affero General Public License version 3.

---

## Install on Debian or Ubuntu GNU \\ Linux

#### 1. Install requirements
```sh
sudo apt-get install python-pip python-virtualenv virtualenvwrapper \
        python-wxgtk2.8 build-essentials libpng-dev libmysqlclient-dev \
        python-dev libfreetype6-dev libxml2-dev libxslt-dev \
        libatlas-base-dev gfortran

```
Tested on Debian 6.0.9, Ubuntu 12.04 and 14.04, packages name could change 
slightly

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
