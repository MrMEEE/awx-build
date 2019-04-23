# Install AWX Community Edition (RPM)

**Now updated to the newest release of AWX (python3 and PostgreSQL 10), please be adviced that this has not been firmly tested, yet..** 

**LinkedIn group for Questions, support, talk and more: https://www.linkedin.com/groups/13694893/**

**Follow updates and other info at: https://twitter.com/martinjuhl and https://www.linkedin.com/in/martin-juhl-9b71b25/**

**Caveats/TODO List**
* Firewall rules has still not been created, so you'll have to make your own or disable the firewall...
* Backup/Restore scripts
* Fix Migrations/upgrades so that they will work everytime.. see bottom for more description..

Please submit issues here: https://github.com/MrMEEE/awx-build/issues

## PreReqs
### Disk requirements

AWX is primarily resident in /opt/awx and /opt/rh/rh-python36, where it takes up around 500MB...

It's works is done in tmp and /var/lib/awx.. but shouldn't take up much space...

I would say that a server with 10GB of space should be more than enough to start with.. Of course this depends on your playbooks..

## Installation Steps

### SELinux 

```
yum -y install policycoreutils-python
semanage port -a -t http_port_t -p tcp 8050
semanage port -a -t http_port_t -p tcp 8051
semanage port -a -t http_port_t -p tcp 8052
setsebool -P httpd_can_network_connect 1
```

### Repos

* Activate EPEL
  * CentOS
  ```bash
  yum -y install epel-release
  ```
  * RHEL
  ```bash
  yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
  ```

* Activate PostgreSQL 10 and Python 3.6
  * CentOS x86_64
  ```bash
    yum -y install centos-release-scl centos-release-scl-rh # Software Collections
  ```
  * CentOS ppc64le
  ```bash
    yum -y install centos-release-scl centos-release-scl-rh # Software Collections
    wget -O /etc/yum.repos.d/mrmeee-rh-postgresql10-epel-7.repo https://copr.fedorainfracloud.org/coprs/mrmeee/rh-postgresql10/repo/epel-7/mrmeee-rh-postgresql10-epel-7.repo
  ```
  * RHEL x86_64
  ```
    rpm -ivh http://mirror.centos.org/centos/7/extras/x86_64/Packages/centos-release-scl-rh-2-2.el7.centos.noarch.rpm
    subscription-manager repos --enable=rhel-server-rhscl-7-rpms
  ```
  * RHEL ppc64le
  ```
    rpm -ivh http://mirrors.dotsrc.org/centos-altarch/7/extras/ppc64le/Packages/centos-release-scl-rh-2-3.el7.centos.noarch.rpm
    subscription-manager repos --enable=rhel-server-rhscl-7-rpms
  ```
* AWX Repo

For all builds:
```bash
yum install -y wget
wget -O /etc/yum.repos.d/ansible-awx.repo https://copr.fedorainfracloud.org/coprs/mrmeee/ansible-awx/repo/epel-7/mrmeee-ansible-awx-epel-7.repo
```

### Install Pre-Reqs for AWX

* Install RabbitMQ
  ```
  echo "[rabbitmq-erlang]
  name=rabbitmq-erlang
  baseurl=https://dl.bintray.com/rabbitmq/rpm/erlang/20/el/7
  gpgcheck=1
  gpgkey=https://dl.bintray.com/rabbitmq/Keys/rabbitmq-release-signing-key.asc
  repo_gpgcheck=0
  enabled=1" > /etc/yum.repos.d/rabbitmq-erlang.repo
  
  yum -y install https://dl.bintray.com/rabbitmq/all/rabbitmq-server/3.7.5/rabbitmq-server-3.7.5-1.el7.noarch.rpm
  ```

* Install PostgreSQL and memcached
  ```bash
  yum install -y rh-postgresql10 memcached
  ```
  
* Install Python dependecies (needs cleaning, probably too much)
  * CentOS
  ```bash
  yum -y install rh-python36
  yum -y install --disablerepo='*' --enablerepo='mrmeee-ansible-awx, base' -x *-debuginfo rh-python36*
  ```
* RHEL
  ```bash
  yum -y install rh-python36
  yum -y install --disablerepo='*' --enablerepo='mrmeee-ansible-awx, rhel-7-server-rpms' -x *-debuginfo rh-python36*
  ```


* Install AWX:
```bash
yum install -y ansible-awx
```

### Configure Pre-Req Applications

* Initialize DB
  ```bash
  scl enable rh-postgresql10 "postgresql-setup initdb"
  ```

* Start services: RabbitMQ
```bash
systemctl enable rabbitmq-server
systemctl start rabbitmq-server
```

* Start services: Postgresql Database
  ```bash
  systemctl start rh-postgresql10-postgresql.service
  systemctl enable rh-postgresql10-postgresql.service
  ```

* Start services: Memcached
```bash
systemctl enable memcached
systemctl start memcached
```

* Create Postgres user and DB:
  ```bash
  scl enable rh-postgresql10 "su postgres -c \"createuser -S awx\""
  scl enable rh-postgresql10 "su postgres -c \"createdb -O awx awx\""
  ```

### Configure AWX

* Import Database data:
```bash
sudo -u awx scl enable rh-python36 rh-postgresql10 "awx-manage migrate"
```

* Initial configuration of AWX
```bash
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'root@localhost', 'password')" | sudo -u awx scl enable rh-python36 rh-postgresql10 "awx-manage shell"

sudo -u awx scl enable rh-python36 rh-postgresql10 "awx-manage create_preload_data"
sudo -u awx scl enable rh-python36 rh-postgresql10 "awx-manage provision_instance --hostname=$(hostname)"
sudo -u awx scl enable rh-python36 rh-postgresql10 "awx-manage register_queue --queuename=tower --hostnames=$(hostname)"
```

### Install and Configure Web Server Proxy

* Install NGINX as proxy:
```bash
yum -y install nginx
wget -O /etc/nginx/nginx.conf https://raw.githubusercontent.com/MrMEEE/awx-build/master/nginx.conf
systemctl enable nginx
systemctl start nginx
```

### Start and Enable AWX

* Start Services
```bash
systemctl start awx-cbreceiver
systemctl start awx-dispatcher
systemctl start awx-channels-worker
systemctl start awx-daphne
systemctl start awx-web
```

* Enable Services
```bash
systemctl enable awx-cbreceiver
systemctl enable awx-dispatcher
systemctl enable awx-channels-worker
systemctl enable awx-daphne
systemctl enable awx-web
```

---

# Create Virtualenv for Ansible
AWX runs Ansible inside Virtualenvs, to be able to utilize several version simultanious. You should create one now, with your preferred Ansible version:

```
yum -y install gcc

awx-create-venv [-options] venvname

Create a Virtual Enviroment for use with AWX-RPM, containing Ansible

Note: GCC is needed to setup the Virtual Environments, install gcc with "yum -y install gcc", if it's not installed..

 options:
  -p, --pythonversion        pythonversion to use (2 or 3), defaults to 3
  -a, --ansibleversion       ansible version to install in venv, defaults to latest
  -n, --venvname             name of venv, defaults to "{pythonversion}-{ansibleversion}-{date}"
  -e, --venvpath             path where the venv will be created, defaults to /var/lib/awx/venv/
```

Now this version can be selected for each play or organization default. (if you can't see it there, try to create another, there is a bug upstream, that means that the dropdown will first appear, when there are 3 or more venvs)


# Upgrade AWX Community Edition (RPM)

## Working Upgrade Paths

Confirmed working upgrade paths:
* 1.0.5.0 -> 1.0.5.31 (have tried almost every minor between)
* 1.0.5.32 -> 1.0.6.0
* 1.0.6.0 -> 1.0.6.1
* 1.0.6.1 -> 1.0.6.3
* 1.0.6.3 -> 1.0.6.7
* 1.0.6.7 -> 1.0.6.8 <sup>[1](#workaround)</sup>
* 1.0.6.8 -> 1.0.6.11
* 1.0.6.11 -> 1.0.6.14
* 1.0.6.14 -> 1.0.6.16
* 1.0.6.16 -> 1.0.6.23
* 1.0.6.23 -> 1.0.6.28
* 1.0.6.28 -> 1.0.6.47
* 1.0.6.47 -> 1.0.7.3 <sup>[1](#workaround)</sup>
* 1.0.7.3 -> 1.0.7.4
* 1.0.7.4 -> 1.0.7.9 <sup>[2](#merge)</sup>
* 1.0.7.9 -> 1.0.8.14
* 1.0.8.14 -> 2.0.0
* 2.0.0 -> 2.1.0.74 <sup>[1](#workaround)</sup><sup>[2](#merge)</sup>
* 2.1.0.74 -> 2.1.0.119
* 2.1.0.119 -> 2.1.0.155
* 2.1.0.155 -> 2.1.0.194
* 2.1.0.194 -> 2.1.0.272 <sup>[2](#merge)</sup>
* 2.1.0.272 -> 2.1.1.27-2 <sup>[2](#merge)</sup>
* 2.1.1.27-2 -> 2.1.1.36
* 2.1.1.36 -> 2.1.2.1
* 2.1.2.1 -> 2.1.2.32-3
* 2.1.2.32 -> 2.1.2.36
* 2.1.2.36 -> 2.1.2.44
* 2.1.2.44 -> 3.0.0.0 <sup>[1](#workaround)</sup>
* 3.0.0.0 -> 3.0.0.59
* 3.0.0.59 -> 3.0.0.124
* 3.0.0.124 -> 3.0.1.12
* 3.0.1.12 -> 3.0.1.35
* 3.0.1.35 -> 3.0.1.219
* 3.0.1.219 -> 3.0.1.223
* 3.0.1.223 -> 3.0.1.305
* 3.0.1.305 -> 3.0.1.340-2
* 3.0.1.340-2 -> 4.0.0.4
* 4.0.0.4 -> 4.0.0.6
* 4.0.0.6 -> 4.0.0.15
* 4.0.0.15 -> 4.0.0.43
* 4.0.0.43 -> 4.0.0.144
* 4.0.0.144 -> 4.0.0.227 <sup>[1](#workaround)</sup>
* 4.0.0.227 -> 4.0.0.299
* 4.0.0.299 -> 4.0.0.347 <sup>[1](#workaround)</sup>
* 4.0.0.347 -> 4.0.0.354

<a name="workaround">1</a>: [Small workarounds needed](migrations.md)

<a name="merge">2</a>: "awx-manage makemigrations" needs to be run with "--merge"

Upgrading to newest version (not guaranteed to work)
```bash
yum update
yum install --disablerepo='*' --enablerepo='mrmeee-ansible-awx, base' -x *-debuginfo rh-python36*
sudo -u awx scl enable rh-postgresql10 rh-python36 "awx-manage makemigrations"
sudo -u awx scl enable rh-postgresql10 rh-python36 "awx-manage migrate"
```

## Broken Upgrade Paths

Confirmed Breaking Upgrade paths:
* 1.0.5.31 -> 1.0.5.32

Here you need to get creative.

Got an answer from the AWX Team:
> "Upgrades between AWX versions are not expected to work. However, we have recently added an import/export capability to tower-cli/awx-cli, which allows you to export your job templates and other objects (not including credential secrets) to a JSON file, which you can then re-import to a freshly installed 1.0.6."

They are referring to the awx-cli tool from their separate repo.. also, the awx-manage tool have a dumpdata/loaddata tool...

I'm going to see if I can do a workaround for upgrades.


### Upgrade Method Using Export/Import Utility

For the guys that really want to push their luck :)... Something like this will probably work.

You have to install awx-cli in advance, available in the repo:
```bash
yum install ansible-tower-cli
```

As far as I can see.. this is missing when using the awx-cli export/import:
* Users (export is blank), and therefore user permissions isn't set
* Log/History is not exported (not high priority in the short run)
* Inventory Groups (custom created groups fails for me, going from 1.0.5.31->1.0.6.1
* Credential passwords (there should be an option to include them)
* LDAP/Auth config (is just not included)

Create a backup of AWX data
```bash
awx-cli receive --organization all --team all --credential_type all --credential all --notification_template all --user all --inventory_script all --inventory all --project all --job_template all --workflow all > alldata
```

Stop all services, re-create the database
```bash
systemctl stop awx-celery-worker awx-cbreceiver awx-celery-beat awx-channels-worker awx-daphne awx-web
su - postgres -c "dropdb awx"
su - postgres -c "createdb -O awx awx"
```

Migrate AWX data into the new database
```bash
sudo -u awx /opt/awx/bin/awx-manage migrate
```

Re-create the admin user, provision the instance and queues
```bash
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'root@localhost', 'test')" | sudo -u awx /opt/awx/bin/awx-manage shell
sudo -u awx /opt/awx/bin/awx-manage provision_instance --hostname=$(hostname)
sudo -u awx /opt/awx/bin/awx-manage register_queue --queuename=tower --hostnames=$(hostname)
```

Restore AWX data from the file (alldata)
```bash
awx-cli send alldata
```

** High availability setup **
Has been reported to work [here](https://github.com/MrMEEE/awx-build/issues/26)

Steps:
rabbitmq clustering
disable celery-beat service
modify the celery-worker execstart command


** Interesting Links
[https://github.com/sujiar37/AWX-HA-InstanceGroup] Ansible playbook Repository for HA for the Docker version **

