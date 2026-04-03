# Divine

<!-- Static badges -->
![python3.14](docs/badges/py314.svg)
![poetry2](docs/badges/poetry2.svg)
![since|2026/04](docs/badges/since.svg)
[![cov](docs/badges/coverage.svg)](.reports/htmlcov/index.html)


This is a sample project for Python API to illustrate a complete stack with several aspects:
- logging
- testing
  - flush-based integration tests
  - polyfactory working with SQLAlchemy
- tooling
- a DDD project structure

## Namesake

I chose Divine as it is similar to Device so it will remind to the purpose of the service

## Disclaimers

- The code project is based in code from previous talks, challenges, and example projects, as well
as code of my previous companies all of it created by me or with a high degree of participation
- AI has been used for this project but in a limited fashion, for solving occasional errors and
  get suggesting but not to build the bulk of the project. Things that I relied more on IA:
  - authentication
  - solve test event loop issues and improvements
  
## Glossary and naming

- DB models have prefix "Db" to differentiate from main objects from other layers (entities, schemas)
- Entities are not prefixed or suffixed in general
- Interface models are suffixed with Schema, or as Request, Response classes
- Other relevant names are DTO, which are simple transport structure to communicate in between
  layers, or Value Objects

see [Architecture](#architecture) for more info about naming

# TLDR Instructions

## Dependencies

To run the application you will need:
- docker (I used 28.3)

To run tests locally:
- python3.14
- poetry 2 
- make (optional)
  - simplifies calls, otherwise, use the commands listed in make directly
- if needed, tests can be enabled to run in docker, should not be long but not trivial

If you don't have poetry, one way to install it is `pipx install poetry`.

Other dependencies may apply depending on your OS, please report any problem

## Run the application

- `make dkc-build`
- `make dkc-run`
- [ApiDocs](localhost:8080/docs) 
  - once running, there is a user available `user@example.com:admin` if you want to Authorize
  - there are device templates (0 to 20) to list or create devices from it

You may need to create the folder `data` in the root of the project, if it is not created
automatically

If you need more details in how to assess the application goto [Usage](#usage)

## Run tests

```
poetry install --with test,dev
poetry run pytest
```

# Choices

## Frameworks: FastAPI and SQLAlchemy

I chose FastAPI and SQLAlchemy as frameworks as I have been working with this stack since 2020 and I feel that it is
a good combination for a CRUD-ish API. I prefer this over other frameworks out
of simplicity and versatility. I also worked with other frameworks but these are the ones I can deliver the most
in a short time while not hindering future work.

They also play nice with DDD and Clean Architecture

## Database: Postgres

I opted for Postgres because it is more versatile, and it can cover non pure SQL use cases pretty well (like 
search, document-like storage, vectors ...).
I think it is the best option for an MVP-like project with the less uncertainties possible.

The code is prepared to shift to other Database if need by implementing a repository for other
technology or re-implemented to use a dual backend which is a pretty common case in crawling and data companies.

The nature of devices data could suggest opting for other database with high read speed. This can be achieved
with a distributed solution with Postgres but a in-memory database could work well with the scraping
services which will be running against thousands or millions of entries. This could also be divided in logical
shards by proxy approach, country or other parameters.

## Entities and DTOs

I preferred to create DTOs specifically instead of using just plain dicts, it is a bit wasteful 
but, it provides structure and centralizes adaptation. With the chosen frameworks we could 
easily add custom serializers and serialize with `model_dump` to get "dict DTOs".

# Architecture

## Design

The project is a simple API with an operational SQL database

I used a MVC-ish solution taking a few things about DDD (specially tactical design)
The result is really a couple of Controllers (views.py) - Model (db_models), one per domain, as the application layer is
so thin that it doesn't make sense to add it separately as this point. So we end up with interface and persistence.

I choose to keep `views.py` instead of `controllers.py` as it is the most familiar name for most Python developers.
The main code is in files `views.py` and `postgres_repository.py`, two of each kind.

Once the application becomes bigger, adding application services, use cases and a "fat" application layer is necessary.
Nevertheless, some domain code is already separated. See [structure](#structure) for more on this

## Structure

This is the folder structure of the project, inspired in DDD terms and suggestions

<!-- tree -d src/ -I __pycache__ -->

```bash
src/
├── divine
│ ├── shared
│ ├── extensions
│ ├── devices
│ │ ├── domain
│ │ ├── interface
│ │ └── persistence
│ └── users
│     ├── domain
│     ├── interface
│     ├── persistence
│     └── services (future)
└── migrations
    └── versions
```

I opted to divide the application in domains "users" and "devices".
It is quite usual that users and authentication/authorization is reused across projects, this way
is already separated and ready for extraction into reusable artifacts (template, libraries, ...)

Also, code which is potentially reusable is located in [extensions](src/divine/extensions) package,
and code which is the shared kernel is located in [shared](src/divine/shared).

## Components

- API Backend in Python 3.14
- Postgres 18 as operational DB
- Jaeger to check traces

## Microservice Tech Stack

- Main
  - `FastAPI`: API framework
  - `Pydantic 2`: Model framework (entities and more)
  - `SQLAlchemy 2`: Async ORM
  - `Alembic`: DB Migrations
  - `uvicorn`: ASGI server
- Secondary
  - `pydantic-settings`: settings definition and auto-loading
  - Passlib and Argon2: password encryption and salting

See [Python project dependencies](pyproject.toml) for specific versions

## Highlights

I would like to highlight a few items in this solution:

- The project is ready for active development with a good scaffolding for continuing development
- It has a high test coverage and good test base with factories and integration tests
  - Integration tests run on flush only, making them faster
- It has a good tooling kit to keep code neat
- Settings are defined programmatically, and it can be easily configured with YAML, secrets or Env
  Vars for a future deploy in most clouds and systems.

# Design

We use the following nomenclature:
- schemas and views: interface models and endpoints or routes (HTTP)
- entities: domain models, but we usually omit Entity in the class name
- db_models: database models, we prefix them with `Db` like `DbUser`

The structure follows a 3-layered architecture approach with interface, application and persistence.
But in essence it doesn't have application layer yet, so the API views in the interface call
the repository layer directly.

The more relevant code is available at `src/divine` in the following modules:
- `app_factory`
- `users` or `device` domains 
  - *.interface.views
  - *.domain.entities
  - *.persistence.db_models

While applying Clean Architecture principles we don't apply a full domain (DDD) approach as it
 seems too much for a project this simple. So I choose not to introduce domain differentiation, but
I could have easily split users and auth, but it is too soon to apply.

Also, I let some coupling happen between persistence and interface, as schemas reach the db access
layer. This is easily achievable passing schemas into DTOs. I also identified some inefficiency
passing models into entities, but it can be reduced using Pydantic's `model_construct` which skips
validation.

Another compromise was avoiding controllers or use cases, as the application layer is so thin that I chose not to
define controllers and overload the views. So far I dind't have the nee for application or domain services.

# Usage

You can run the app locally doing:
```
make dkc-build
make dkc-run
xdg-open http://localhost:8080/docs
```

Once in the API docs you can follow this script:
- try to create a device without authenticating
- create an user or use the one available (`user@example.com:admin`)
- authenticate
- create a device, edit it and delete it
- list templates, take note of one template ID
- create a device from a template
- list all devices

# Tests

Test rely in `pytest` and `testcontainers`. Additionally I use `polyfactory` to create
synthetic data to run the test.

I relied more in integration tests than unit ones, as the cost of integration tests with this
choice of frameworks is rather low and it makes better tests.

To run the whole suite or a subset do:

```
make run-tests
pytest -m unit
pytest -m integration
pytest -m current
pytest
```

## Test stack

Tests are based in pytest using a collection of plugins:
- pytest-cov
- pytest-env
- pytest-mock
- pytest-asyncio
- python-dotenv

Additionally we have created a few factories (or mother objects) using `polyfactory`, a great python
library similar to `factoryboy`, and `faker`. In this case, we focus in db-enabled factories, which enable the developer to create integration
tests quite easily.

`faker` it is used to create synthetic objects in the
database and could be used to create other data fixtures or API inputs. I created a couple of custom
fake providers specific to this project.

## Testing approach

I focused exclusively in Database testing which can be considered integration or, as I like to say,
"unit plus", since the coupling of the backend with the database is so high that it makes little sense 
mocking "everything" having a ready database through Docker.

# Maintenance

If you continue this project we recommend the following:
- Convert `views.py` into a module, and group views (routes) by resource
- Convert `db_models.py` into a module
- Consider using repositories for different aspects of the DB
- As a project like this progresses, some code could be extracted into libraries, like a potential
  auxiliary code for each layer like HttpProblem

## Migrations

After adding or modifying a schema you can generate a new migration with:

`make migrate-generate "message"`

And you can apply it locally:

`make migrate-apply`

# Tooling

For this project I set up:

- `mise` to manage system dependencies like Python and Poetry. Alternatives: `asdf`
- `isort` for import formatting
- `ruff` for general linting and formatting
- `interrogate` for docstring syntax and formatting
- `pyright` for typing analysis. Alternatives: `mypy`
- `codespell` for spelling and grammar
- `radon`: code quality metrics

Run `make` for instructions on how to run then

At the moment of writing the current code quality stats were:

<!-- make run-tests -->
- 85% code coverage
<!-- make qual-complexity -->
- 1.49 (A) avg. complexity
<!-- make interrogate -->
- 18.8% docstring coverage

With enough time I would have liked to try `asdf` to make it easier to handle poetry `versions` 1 and 2,
and setup pre-commit to apply tooling on commit or demand.

# Future work and improvements

## Naming

I started cutting short `device_profiles` into `device` as in `device_id`, but as I introduced `device templates`
it could make sense to add `profiles` too, specially since profiles and templates are very generic words

## Structure

- DTOs and Entities could have their own modules
- User is part of the shared kernel, but I kept the domain separated, except for auth that goes in `shared` 

## Application

- Basic Auth is not a good thing, we could quickly shift to a token based (like JWT) auth
  system

## Persistence

- Enums are not used properly in DB, we should adapt python enums to SQLA enums so they are rendered
  in the DB
- Id fields should be returned from the DB, it needs work

## Testing

- Review the setup to run migrations only if needed or if start from scratch is requested

## Performance

- We could use caching for things like authentication
- The same for devices, if they are requested by very intensive crawling services

## Tooling

- Having pre-commit would have improved the development process, but for now make is fine
- There are more modern tools than make, but it was there ready to use
- Having `asdf` will simplify working on different system dependencies version (python, poetry)
- Pending a markdown linter

## Documentation

- We should add diagrams with `mermaid` or `python-diagrams` to name a couple

## Observability 

This project is very simple regarding observability, it barely has logs and it has commodity instrumentors.

- In the future we should migrate to a more sophisticated and async-friendly log framework
  like `structlog`
- tracing is configured and instrumented for FastAPI (HTTP) and SQLAlchemy (SQL), with that we
  already can have tracing and we can use tracing to extract metrics. However, for a full APM
  observability we should pass logs to metrics (using `logfmt` like in logs `device_id=12345`)
  and pushing custom metrics.

## Know problems and troubleshooting

You may need to create the folder `data` in the root of the project, if it is not created
automatically
