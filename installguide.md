# Install AWX Community Edition (RPM)

**Caveats/TODO List**
* Firewall rules has still not been created, so you'll have to make your own or disable the firewall...
* Backup/Restore scripts
* Fix Migrations/upgrades so that they will work everytime.. see bottom for more description..

Please submit issues here: https://github.com/MrMEEE/awx-build/issues

## Installation Steps

### SELinux (Beta)

These instructions have not been tested firmly yet, so if you have any issues, please report back

```
semanage port -a -t http_port_t -p tcp 8051
semanage port -a -t http_port_t -p tcp 8052
setsebool -P httpd_can_network_connect 1
```

### Repos

* Activate EPEL
```bash
yum install -y epel-release
```

* Activate PostgreSQL 9.6
  * CentOS
  ```bash
  yum install centos-release-scl # Software Collections
  ```
  * RHEL
    * Activate Software Collections

* AWX Repo

For all builds (might be unstable, but I will probably test these better):
```bash
yum install -y wget
wget -O /etc/yum.repos.d/awx-rpm.repo https://copr.fedorainfracloud.org/coprs/mrmeee/awx-dev/repo/epel-7/mrmeee-awx-dev-epel-7.repo
```
For only "stable" builds (the base releases, 2.0.1, 2.1.0.. no minors):
```bash
yum install -y wget
wget -O /etc/yum.repos.d/awx-rpm.repo https://copr.fedorainfracloud.org/coprs/mrmeee/awx/repo/epel-7/mrmeee-awx-epel-7.repo
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
  yum install -y rh-postgresql96 memcached
  ```

* Install AWX:
```bash
yum install -y awx
```

### Configure Pre-Req Applications

* Initialize DB
  ```bash
  scl enable rh-postgresql96 "postgresql-setup initdb"
  ```

* Start services: RabbitMQ
```bash
systemctl enable rabbitmq-server
systemctl start rabbitmq-server
```

* Start services: Postgresql Database
  ```bash
  systemctl start rh-postgresql96-postgresql.service
  systemctl enable rh-postgresql96-postgresql.service
  ```

* Start services: Memcached
```bash
systemctl enable memcached
systemctl start memcached
```

* Create Postgres user and DB:
  * CentOS
  ```bash
  scl enable rh-postgresql96 "su postgres -c \"createuser -S awx\""
  scl enable rh-postgresql96 "su postgres -c \"createdb -O awx awx\""
  ```

### Configure AWX

* Import Database data:
```bash
sudo -u awx /opt/awx/bin/awx-manage migrate
```

* Initial configuration of AWX
```bash
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'root@localhost', 'password')" | sudo -u awx /opt/awx/bin/awx-manage shell
sudo -u awx /opt/awx/bin/awx-manage create_preload_data
sudo -u awx /opt/awx/bin/awx-manage provision_instance --hostname=$(hostname)
sudo -u awx /opt/awx/bin/awx-manage register_queue --queuename=tower --hostnames=$(hostname)
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
* 2.1.0.272 -> 2.1.1.23 <sup>[2](#merge)</sup>

<a name="workaround">1</a>: [Small workarounds needed](migrations.md)

<a name="merge">2</a>: "awx-manage makemigrations" needs to be run with "--merge"

Upgrading to newest version (not guaranteed to work)
```bash
yum update
sudo -u awx /opt/awx/bin/awx-manage makemigrations
sudo -u awx /opt/awx/bin/awx-manage migrate
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

### High availability setup
Has been reported to work [here](https://github.com/MrMEEE/awx-build/issues/26)

Steps:
rabbitmq clustering
disable celery-beat service
modify the celery-worker execstart command



