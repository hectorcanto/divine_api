# MVP Rest API to manage device profiles

- Clean code, readable and logically structured
- CRUD+L for device profiles
- Basic authentication
- Limited user support (KISS)
- Expose in port 8080
- don't worry about advanced scalability
- endpoints to create from scratch or from templates

## Device profiles

- id
- device_type: desktop/mobile
- window_size (width/height)
- user agent (str)
- country code (assuming ISO like pycountry, numeric)
  - not creating country table, using pycountry as source of truth 
- custom headers (list of key-values)

## Docs

- explain DB choice
- explain other choices
- explain possible enhancements
  - think about profile validation

## Extra requirements

- maintainability