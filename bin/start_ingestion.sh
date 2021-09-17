export DOCKER_GROUP_ID=`getent group docker | cut -d: -f3`

echo "Rebuilding..."

docker compose -f docker-compose_orchestration.yml build -q
docker compose -f docker-compose_ingestion.yml build -q

echo "Starting..."

docker compose -f docker-compose_ingestion.yml build -q
docker compose -f docker-compose_orchestration.yml build -q