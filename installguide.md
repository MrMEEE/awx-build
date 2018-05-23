# Install AWX Community Edition (RPM)

**Caveats/TODO List**
* SELinux policies has still not been created (comming soon), so you'll have to make your own or disable SELinux...
* Firewall rules has still not been created, so you'll have to make your own or disable the firewall...
* Backup/Restore scripts
* Fix Migrations/upgrades so that they will work everytime.. see bottom for more description..

Please submit issues here: https://github.com/MrMEEE/awx-build/issues

## Installation Steps

### Repos

* Activate EPEL
```bash
yum install -y epel-release
```

* Activate PostgreSQL 9.6
  * CentOS
  ```bash
  yum install -y https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm
  ```
  * RHEL
    * Activate Software Collections

* AWX Repo
```bash
yum install -y wget
wget -O /etc/yum.repos.d/awx-rpm.repo https://copr.fedorainfracloud.org/coprs/mrmeee/awx-dev/repo/epel-7/mrmeee-awx-dev-epel-7.repo
```
  * **NOTE:**
  DON'T use the AWX Non-Dev repo, use the one above.
  AWX upstream doesn't release stable releases, so the following repo is not updated.
  For only releases (1.0.1, 1.0.2 ... ): https://copr.fedorainfracloud.org/coprs/mrmeee/awx/repo/epel-7/mrmeee-awx-epel-7.repo

### Install Pre-Reqs for AWX

* Install RabbitMQ, PostgreSQL and memcached
  * CentOS
  ```bash
  yum install -y rabbitmq-server postgresql96-server memcached
  ```

  * RHEL
  ```bash
  yum install -y rh-postgresql96 rabbitmq-server memcached
  ```

* Install AWX:
```bash
yum install -y awx
```

### Configure Pre-Req Applications

* Initialize DB
  * CentOS
  ```bash
  /usr/pgsql-9.6/bin/postgresql96-setup initdb
  ```
  * RHEL
  ```bash
  scl enable rh-postgresql96 "postgresql-setup initdb"
  ```

* Start services: RabbitMQ
```bash
systemctl enable rabbitmq-server
systemctl start rabbitmq-server
```

* Start services: Postgresql Database
  * CentOS
  ```bash
  systemctl enable postgresql-9.6
  systemctl start postgresql-9.6
  ```
  * RHEL
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
  sudo -u postgres createuser -S awx # (ignore "could not change directory to "/root"")
  sudo -u postgres createdb -O awx awx # (ignore "could not change directory to "/root"")
  ```

  * RHEL
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
systemctl start awx-celery-beat
systemctl start awx-celery-worker
systemctl start awx-channels-worker
systemctl start awx-daphne
systemctl start awx-web
```

* Enable Services
```bash
systemctl enable awx-cbreceiver
systemctl enable awx-celery-beat
systemctl enable awx-celery-worker
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

