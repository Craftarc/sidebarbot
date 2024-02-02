# How to use this repository

1. Clone it
2. Update bot client id and secret in config.json
3. At the project root do `./run.sh`

If you make any changes just re-run `./run.sh`. This will force you to do Oauth again.
If no changes were made, and you just want to restart the container do `docker compose run`.
It will use the refresh token if Oauth was done before.

**After you paste the localhost:8080/... url into the container you are free to detach from it**
Linux detach control sequence: Ctrl-P + Ctrl-Q

## config.json
- The update works by polling poe's website for a list of items on sale, then looking through
the list and looking for items that contain the 'parse_target' in their name
- 'parse_target'='stash' so any stash tabs on sale will be picked up and trigger the update
- This value can be changed if the search target needs to be refined
