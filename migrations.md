# Migration issues:

* 1.0.6.7 -> 1.0.6.8

Something in rabbitmq changed.. so we need to upgrade to newer RabbitMQ:
```

systemctl stop rabbitmq-server
yum -y remove erlang-erts-R16B-03.18.el7.x86_64
echo "[rabbitmq-erlang]
name=rabbitmq-erlang
baseurl=https://dl.bintray.com/rabbitmq/rpm/erlang/20/el/7
gpgcheck=1
gpgkey=https://dl.bintray.com/rabbitmq/Keys/rabbitmq-release-signing-key.asc
repo_gpgcheck=0
enabled=1" > /etc/yum.repo.d/rabbitmq-erlang.repo
  
yum -y install https://dl.bintray.com/rabbitmq/all/rabbitmq-server/3.7.5/rabbitmq-server-3.7.5-1.el7.noarch.rpm

rm -rf /var/lib/rabbitmq/mnesia/

systemctl start rabbitmq-server

systemctl restart awx-celery-worker awx-cbreceiver awx-celery-beat awx-channels-worker awx-daphne awx-web
```
comment out these two lines in /etc/awx/settings.py: (will be fixed from version 1.0.6.9)
```
CELERY_ROUTES['awx.main.tasks.cluster_node_heartbeat'] = {'queue': CLUSTER_HOST_ID, 'routing_key': CLUSTER_HOST_ID}
CELERY_ROUTES['awx.main.tasks.purge_old_stdout_files'] = {'queue': CLUSTER_HOST_ID, 'routing_key': CLUSTER_HOST_ID}
```
