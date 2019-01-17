service docker stop
rm -rf /var/lib/docker
service docker start
docker volume create --name=grafana-volume
