# Console queries

Find empty points

```
POST collections/k6-perf-test/points/scroll
{
  "limit": 10,
  "filter": {
    "must": [
      {
        "is_empty": {
          "key": "color"
        }
      }
    ]
  }
}
```
