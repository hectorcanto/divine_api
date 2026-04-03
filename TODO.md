# Done

- add tracing and jaeger
- review todos
- badges
- Use postgres with a repository interface
- Add instrumentation for sqlalchemy and fastapi (at least)
  - comment in readme

# Pending or possible

- implement HTTP Problem RFC 
- add custom metrics (noop maybe)
- add prometheus
- add basic settings
- add user_id to the access log
- use a UserEntity in get_current_user
  - if it comes from cache or via JWT, no need to access DB 
- work on soft-delete and filter out deleted_at objects

## Extras not implemented

Deeper ID capture (IMEI, MAC, IP ...)

## Tooling

- add python do-it or typer to add user to use (first_name, last_name)
  - decided to go with a bulk addition in a migration 
- toptal gitignore
- consider mise or asd

# Testing

- Enable tests fully from docker compose, needs extra tweaking with env vars and settings

## Observability

- Logging instrumentation
- Some Log viewer, check OpenObserve


## DB

- index in deleted_at is not None