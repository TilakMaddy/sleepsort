db := "docker compose -f docker/docker-compose.db.yml"
app := "docker compose -f docker/docker-compose.app.yaml"
image := "tfeoatmilk/sleepsort"

default:
    @just --list

# Start shared Postgres
db-up:
    {{ db }} up -d --wait

# Stop shared Postgres (keeps data)
db-down:
    {{ db }} down

# Build the app image
build:
    {{ app }} build

# Run sleep sort. Example: just sort 5,2,3,6
sort NUMBERS:
    {{ app }} run --rm app -- {{ NUMBERS }}

# Show all rows
rows:
    docker exec pg-shared psql -U postgres -d sleepsort -c "TABLE sorts;"

# Open a psql shell
psql:
    docker exec -it pg-shared psql -U postgres -d sleepsort

# Publish multi-arch image (amd64 + arm64) to Docker Hub. Example: just publish 0.1.0
publish VERSION="latest":
    docker buildx create --name sleepsort-builder --use --bootstrap 2>/dev/null || docker buildx use sleepsort-builder
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -f app/Dockerfile \
        -t {{ image }}:{{ VERSION }} \
        -t {{ image }}:latest \
        --push app
