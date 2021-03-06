# -*- coding: utf-8 -*-

import os
import pathlib
import shutil
import redis
from datetime import timedelta
from smart_getenv import getenv
from kombu import Queue

DEBUG = getenv('DEBUG', default=False, type=bool)
FAKE_USER = {
    'id': 12345,
    'username': 'sheldon',
    'nickname': 'Sheldon Lee Cooper',
    'email': 'sheldon@sheldon.com',
    'privileged': 1,
}

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = LOGGER_NAME = 'console'
CONFIG_ROOT_DIR = '/etc/kae-console'
CONSOLE_CONFIG_PATHS = [
    os.path.join(CONFIG_ROOT_DIR, "config.py"),
    os.path.join(REPO_DIR, "local_config.py"),
]

INGRESS_ANNOTATIONS_PREFIX = "nginx.ingress.kubernetes.io"
APP_BUILD_TIMEOUT = 1800     # timeout for build image(30 minutes)

# in order to avoid nginx to close the idle websocket connection,
# we need to send heartbeat message to refresh the read timeout
WS_HEARTBEAT_TIMEOUT = 60

EMAIL_SENDER = ""
EMAIL_SENDER_PASSWOORD = ""
# SERVER_NAME = getenv('SERVER_NAME', default='127.0.0.1')
SENTRY_DSN = getenv('SENTRY_DSN', default='')
SECRET_KEY = getenv('SECRET_KEY', default='testsecretkey')

REDIS_URL = getenv('REDIS_URL', default='redis://127.0.0.1:6379/0')

DEFAULT_NS = getenv('DEFAULT_NS', default='kae')
DEFAULT_APP_NS = getenv('DEFAULT_APP_NS', default='kae-app')
DEFAULT_JOB_NS = getenv('DEFAULT_JOB_NS', default='kae-job')

SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI', default="mysql+pymysql://root@127.0.0.1:3306/kaetest?charset=utf8mb4")
SQLALCHEMY_TRACK_MODIFICATIONS = getenv('SQLALCHEMY_TRACK_MODIFICATIONS', default=True, type=bool)
SQLALCHEMY_POOL_SIZE = getenv('SQLALCHEMY_POOL_SIZE', default=30)
SQLALCHEMY_MAX_OVERFLOW = getenv('SQLALCHEMY_MAX_OVERFLOW', default=10)
# you should set SQLALCHEMY_POOL_RECYCLE to a value smaller than wait_timeout config in mysql
SQLALCHEMY_POOL_RECYCLE = getenv('SQLALCHEMY_POOL_RECYCLE', default=580)

OAUTH_APP_NAME = 'gitlab'
# I registered a test app on gitlab that redirect to
# http://console.gtapp.xyz/user/authorized as callback url
GITLAB_CLIENT_ID = getenv('GITLAB_CLIENT_ID')
GITLAB_CLIENT_SECRET = getenv('GITLAB_CLIENT_SECRET')
GITLAB_HOST = getenv('GITLAB_HOST', default='gitlab.com')

EMAIL_DOMAIN = getenv('EMAIL_DOMAIN')
BOT_WEBHOOK_URL = getenv('BOT_WEBHOOK_URL')
BEARYCHAT_CHANNEL = 'platform'
DEFAULT_REGISTRY = "registry.cn-hangzhou.aliyuncs.com/kae"
REGISTRY_AUTHS = {
    "registry.cn-hangzhou.aliyuncs.com": "aliyun",
}

# Set base domain for cluster, when a cluster has base domain,
# every app in that cluster will a host name `appname.basedomain`
# if you use incluster config, then the cluster name should be `incluster`.
CLUSTER_BASE_DOMAIN_MAP = {
    # "cluster1": "domain name",
    # "cluster2": "domain name",
}

TLS_SECRET_MAP = {
    # "cluster1": {
    #     "domain name": "tls secret name"
    # }
}

# cluster's dfs root directory
DFS_HOST_DIR_MAP = {
    # "cluster1": "/dfs"
}

HOST_DATA_DIR = "/data/kae"
POD_LOG_DIR = "/kae/logs"

DFS_MOUNT_DIR = '/cephfs'
JOBS_ROOT_DIR = os.path.join(DFS_MOUNT_DIR, "kae/jobs")
JOBS_OUPUT_ROOT_DIR = os.path.join(DFS_MOUNT_DIR, "kae/job-outputs")
JOBS_REPO_DATA_DIR = os.path.join(DFS_MOUNT_DIR, "kae/job-repos")
JOBS_LOG_ROOT_DIR = os.path.join(DFS_MOUNT_DIR, "kae/job-logs")

DFS_TYPE = os.environ.get('DFS_TYPE', 'hostPath')
DFS_VOLUME = {}

if DFS_TYPE == 'hostPath':
    DFS_VOLUME = {
        'name': 'cephfs',
        'hostPath': {
            'path': os.environ.get('KAE_DFS_HOSTPATH', '/cephfs')
        }
    }
elif DFS_TYPE == 'nfs':
    DFS_VOLUME = {
        'name': 'cephfs',
        'nfs': {
            'server': os.environ.get('KAE_NFS_SERVER'),
            'path': os.environ.get('KAE_NFS_PATH', '/'),
            'readOnly': False,
        }
    }

for console_cfg in CONSOLE_CONFIG_PATHS:
    if os.path.isfile(console_cfg):
        exec(open(console_cfg, encoding='utf-8').read())

if SQLALCHEMY_DATABASE_URI is None:
    raise ValueError("SQLALCHEMY_DATABASE_URI can't be None")

if REDIS_URL is None:
    raise ValueError("REDIS_URL can't be None")

# validate CLUSTER_BASE_DOMAIN_MAP
for cluster, base_domain in CLUSTER_BASE_DOMAIN_MAP.items():
    if cluster not in TLS_SECRET_MAP:
        raise ValueError("cluster {} base domain {} needs tls secret".format(cluster, base_domain))
    if base_domain not in TLS_SECRET_MAP[cluster]:
        raise ValueError("cluster {} base domain {} needs tls secret".format(cluster, base_domain))

##################################################
# the config below must not use getenv
##################################################
TASK_PUBSUB_CHANNEL = 'citadel:task:{task_id}:pubsub'
# send this to mark EOF of stream message
# TODO: ugly
TASK_PUBSUB_EOF = 'CELERY_TASK_DONE:{task_id}'

# celery config
timezone = getenv('TIMEZONE', default='Asia/Shanghai')
broker_url = REDIS_URL
result_backend = REDIS_URL
broker_transport_options = {'visibility_timeout': 10}
task_default_queue = PROJECT_NAME
task_queues = (
    Queue(PROJECT_NAME, routing_key=PROJECT_NAME),
)
task_default_exchange = PROJECT_NAME
task_default_routing_key = PROJECT_NAME
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json', 'pickle']
beat_schedule = {
    # 'check_app_pods_watcher': {
    #     'task': 'console.tasks.check_app_pods_watcher',
    #     'schedule': timedelta(minutes=5),
    # },
}

# flask-session settings
SESSION_USE_SIGNER = True
SESSION_TYPE = 'redis'
SESSION_REDIS = redis.Redis.from_url(REDIS_URL)
SESSION_KEY_PREFIX = '{}:session:'.format(PROJECT_NAME)
PERMANENT_SESSION_LIFETIME = timedelta(days=5)

# flask cache settings
CACHE_REDIS_URL = REDIS_URL

HOST_VOLUMES_DIR = os.path.join(HOST_DATA_DIR, "volumes")
REPO_DATA_DIR = "/tmp/repo-data"

# create dir if not exists
pathlib.Path(REPO_DATA_DIR).mkdir(parents=True, exist_ok=True)


def setup_config_from_secrets():
    # prepare for git command
    def setup_git_ssh(setup_known_hosts=False):
        src_secret = os.path.join(CONFIG_ROOT_DIR, "id_rsa")
        src_known_hosts = os.path.join(CONFIG_ROOT_DIR, "known_hosts")

        secret = os.path.expanduser("~/.ssh/id_rsa")
        known_hosts = os.path.expanduser("~/.ssh/known_hosts")

        pathlib.Path(os.path.dirname(secret)).mkdir(parents=True, exist_ok=True)

        if not os.path.exists(secret):
            shutil.copyfile(src_secret, secret)
        os.chmod(secret, 0o600)

        if setup_known_hosts:
            if not os.path.exists(known_hosts):
                shutil.copyfile(src_known_hosts, known_hosts)
            ssh_cmd = "ssh -q -o UserKnownHostsFile={} -i {}".format(known_hosts, secret)
        else:
            ssh_cmd = "ssh -q -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i {}".format(secret)
        os.environ['GIT_SSH_COMMAND'] = ssh_cmd

    def setup_docker_config_json():
        src_docker_cfg = os.path.join(CONFIG_ROOT_DIR, 'docker_config.json')
        dst_docker_cfg = os.path.expanduser('~/.docker/config.json')

        if not os.path.exists(dst_docker_cfg):
            pathlib.Path(os.path.dirname(dst_docker_cfg)).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src_docker_cfg, dst_docker_cfg)

    def setup_kubeconfig():
        src_kubeconfig = os.path.join(CONFIG_ROOT_DIR, 'kubeconfig')
        dst_kubeconfig = os.path.expanduser('~/.kube/config')

        if not os.path.exists(dst_kubeconfig):
            pathlib.Path(os.path.dirname(dst_kubeconfig)).mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src_kubeconfig, dst_kubeconfig)

    setup_git_ssh()
    setup_docker_config_json()
    setup_kubeconfig()


if getenv("PYTEST") is None:
    setup_config_from_secrets()
