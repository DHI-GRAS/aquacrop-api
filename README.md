# Aquacrop-API

API:
1. Submit: https://aquacropapiapp.azurewebsites.net/api/submit
2. Query: https://aquacropapiapp.azurewebsites.net/api/query
3. Move-mock: https://aquacropapiapp.azurewebsites.net/api/move-mock


## Example messages

### API

#### submit message (`POST`)

```json
{
  "area_name": "Volta",
  "crop": "Maize",
  "planting_date": "2018-01-01",
  "irrigated": false,
  "fraction": 0.0
}
```

#### submit response

```json
{
  "guid": "c1edf256-c4b2-4373-8ac8-3f3be5a2a82e"
}
```

#### query response

```json
{
  "status": "completed",
  "error": null
}
```

where `status` can be can be any of `["completed", "awaiting", "failed"]`.


### Behind the scenes

#### job queue message

```json
{
  "guid": "c1edf256-c4b2-4373-8ac8-3f3be5a2a82e",
  "area_name": "Volta",
  "crop": "Maize",
  "planting_date": "2018-01-01",
  "irrigated": false,
  "fraction": 0.0
}
```

### done queue message

```json
{
  "guid": "c1edf256-c4b2-4373-8ac8-3f3be5a2a82e",
  "error": null
}
```
