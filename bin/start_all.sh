export DOCKER_GROUP_ID=`getent group docker | cut -d: -f3`

echo "Rebuilding..."

docker compose build -q

docker compose up -d
