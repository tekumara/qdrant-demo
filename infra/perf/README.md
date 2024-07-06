# Qdrant perf test

## Usage

```
make perf
```

## Env vars

| Name                     | Default                 |
| ------------------------ | ----------------------- |
| BASE_URL                 | "http://localhost:6333" |
| API_KEY                  |                         |
| ORDERING                 | "weak"                  |
| SHARD_NUMBER             |                         |
| REPLICATION_FACTOR       | 3                       |
| WRITE_CONSISTENCY_FACTOR | 3                       |
| VECTOR_SIZE              | 1536                    |
| INIT_POINTS              | 1000                    |

Can be set as environment variables or passed using `-e`.
