# Migration issues:

* 1.0.6.7 -> 1.0.6.8

Something in rabbitmq changed.. so the queue needs to be reset:
```
rabbitmqctl delete_vhost /
systemctl stop rabbitmq-server
rm -rf /var/lib/rabbitmq/mnesia/
systemctl start rabbitmq-server
systemctl restart awx-celery-worker awx-cbreceiver awx-celery-beat awx-channels-worker awx-daphne awx-web
```
comment out these two lines in /etc/awx/settings.py: (will be fixed from version 1.0.6.9)
```
CELERY_ROUTES['awx.main.tasks.cluster_node_heartbeat'] = {'queue': CLUSTER_HOST_ID, 'routing_key': CLUSTER_HOST_ID}
CELERY_ROUTES['awx.main.tasks.purge_old_stdout_files'] = {'queue': CLUSTER_HOST_ID, 'routing_key': CLUSTER_HOST_ID}
```
