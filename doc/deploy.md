## prepare namespace and certifications
create two namespace `kae-app` and `kae-job`, you should add certifications to `kae-app` namespace

## prepare ssh key and know hosts
  you need to create secret for git and docker

    kubectl create secret generic kae-console --from-file=id_rsa=config/id_rsa --from-file=docker_config.json=config/docker_config.json --from-file=config.py=config/config.py --namespace kae

  you can also privide an optional kubeconfig

    kubectl create secret generic kae-console --from-file=kubeconfig=config/kubeconfig --from-file=id_rsa=config/id_rsa --from-file=docker_config.json=config/docker_config.json --from-file=config.py=config/config.py --namespace kae

## prepare pullImageSecret
 in order to pull image from private repository, you need to create secret in every namespace.
 
    kubectl create secret docker-registry aliyun --docker-server=registry.cn-hangzhou.aliyuncs.com --docker-username=xxxx --docker-password=xxxxx --docker-email=xxx@xxx.com
