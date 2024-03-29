# Aquacrop-API

## API

1. Submit: https://aquacropapiapp.azurewebsites.net/api/submit
2. Query: https://aquacropapiapp.azurewebsites.net/api/query
3. GetJob: https://aquacropapiapp.azurewebsites.net/api/getjob
4. Move-mock: https://aquacropapiapp.azurewebsites.net/api/move-mock

## Deployment

1. Edit `config.ini` to your needs - in particular, enter the storage access key.
2. Make sure you are in a Python 3 environment (e.g. `python3 -m venv &ENVDIR && source $ENVDIR/bin/activate`)
3. If the app is already deployed, use `make fetch-app-settings` to store the existing settings locally.
4. Then you can (re-)deploy with make azure-deploy.


## Example messages

### API

#### submit message (`POST`)

```json
{
  "area_name": "Malawi",
  "crop": "Maize",
  "planting_date": "2018-01-01",
  "irrigated": false,
  "fraction": 0.0,
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [
          33.652496337890625,
          -13.062088034413119
        ],
        [
          34.028778076171875,
          -13.062088034413119
        ],
        [
          34.028778076171875,
          -12.746176829427826
        ],
        [
          33.652496337890625,
          -12.746176829427826
        ],
        [
          33.652496337890625,
          -13.062088034413119
        ]
      ]
    ]
  }
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

where `status` can be can be any of `["awaiting", "processing", "completed", "failed"]`.

#### getjob message (`POST`)

```json
{
  "num_messages": 1
}
```


### Behind the scenes

#### job queue message

```json
{
  "guid": "c1edf256-c4b2-4373-8ac8-3f3be5a2a82e",
  "area_name": "Malawi",
  "crop": "Maize",
  "planting_date": "2018-01-01",
  "irrigated": false,
  "fraction": 0.0,
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [
          33.652496337890625,
          -13.062088034413119
        ],
        [
          34.028778076171875,
          -13.062088034413119
        ],
        [
          34.028778076171875,
          -12.746176829427826
        ],
        [
          33.652496337890625,
          -12.746176829427826
        ],
        [
          33.652496337890625,
          -13.062088034413119
        ]
      ]
    ]
  }
}

```

### done queue message

```json
{
  "guid": "c1edf256-c4b2-4373-8ac8-3f3be5a2a82e",
  "error": null
}
```
