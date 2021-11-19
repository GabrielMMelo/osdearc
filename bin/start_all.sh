export DOCKER_GROUP_ID=`getent group docker | cut -d: -f3`

echo "Rebuilding..."

docker compose build -q

docker compose -f docker-compose-airbyte.yml build -q

docker compose -f docker-compose-superset.yml build -q

echo "Starting..."

docker compose up -d

docker compose -f docker-compose-airbyte.yml up -d

docker compose -f docker-compose-superset.yml up -d