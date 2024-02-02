#!/bin/bash
# Kill and remove old container
id=$(docker ps -a | grep 'sidebarbot' | grep -oE '^\S+')
docker kill $id > /dev/null 2>&1
docker container rm $id > /dev/null 2>&1

# Remove the previous volume storing the refresh token
docker volume rm sidebarbot_refresh_token > /dev/null 2>&1

# Build and start the process again
docker compose run --build sidebarbot