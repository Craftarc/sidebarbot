# dailydealsbot

A bot for the poe subreddit to update the sidebar with new daily deals

HOW TO
===
Build your docker container
```
docker build -t dailydealsbot:latest .
```

Upload a secret with your config
```
cat instance/config.json | docker secret create dailydealsconfig.json -
```

Create the service
```
docker service create --name dailydealstest --secret dailydealsconfig.json -e CONFIG_FILE='/run/secrets/dailydealsconfig.json' dailydealsbot:latest
```


boom done
