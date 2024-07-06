import http from "k6/http";
import { check, fail } from "k6";
import { SharedArray } from "k6/data";
import { uuidv4 } from "https://jslib.k6.io/k6-utils/1.4.0/index.js";

export const options = {
  scenarios: {
    load: {
      executor: "constant-arrival-rate",
      rate: 10,
      timeUnit: "1s",
      duration: "30s",
      preAllocatedVUs: 1,
    },
  },
};

const baseUrl = __ENV.BASE_URL || "http://localhost:6333";
const apiKey = __ENV.API_KEY;
const ordering = __ENV.ORDERING || "strong";
const shardNumber = __ENV.SHARD_NUMBER && parseInt(__ENV.SHARD_NUMBER);
const replicationFactor =
  __ENV.REPLICATION_FACTOR && parseInt(__ENV.REPLICATION_FACTOR) || 3;
const writeConsistencyFactor =
  __ENV.WRITE_CONSISTENCY_FACTOR && parseInt(__ENV.WRITE_CONSISTENCY_FACTOR) || 3;

let params = { headers: { "content-type": "application/json" } };
if (apiKey) {
  params["headers"]["api-key"] = apiKey;
}
const collectionName = `k6-perf-test`;
const vectorSize = (__ENV.VECTOR_SIZE && parseInt(__ENV.VECTOR_SIZE)) || 1536;
const initPoints = (__ENV.INIT_POINTS && parseInt(__ENV.INIT_POINTS)) || 1000;
const deletePoints = __ENV.DELETE_POINTS && __ENV.DELETE_POINTS.toLowerCase() === 'true';

const vectors = new SharedArray("shared vectors", function () {
  // called once and the result is shared among VUs
  // see https://grafana.com/docs/k6/latest/javascript-api/k6-data/sharedarray/
  return Array(initPoints)
    .fill(null)
    .map((_, i) => getRandomVector(vectorSize));
});

export function setup() {
  // delete collection if exists

  const resExistsCollection = http.get(
    `${baseUrl}/collections/${collectionName}`,
    params
  );

  if (resExistsCollection.status === 200) {
    console.log(`deleting existing collection ${collectionName}`);
    const resDeleteCollection = http.del(
      `${baseUrl}/collections/${collectionName}?timeout=10`,
      null,
      params
    );
    console.log(
      `delete existing collection ${collectionName}: ${resDeleteCollection.body}`
    );
  }

  // create collection

  const resCreateCollection = http.put(
    `${baseUrl}/collections/${collectionName}`,
    JSON.stringify({
      vectors: { size: vectorSize, distance: "Dot" },
      shard_number: shardNumber,
      replication_factor: replicationFactor,
      write_consistency_factor: writeConsistencyFactor,
    }),
    params
  );
  check(
    resCreateCollection,
    checks("create collection", {
      "status is 200": (r) => r.status === 200,
      "is OK": (r) => r.json().status === "ok",
    })
  );

  // add initial points
  // break into batches to avoid hitting limits with ingress or qdrant
  const batchSize = 25;
  const numBatches = Math.ceil(initPoints / batchSize);
  for (let b = 0; b < numBatches; b++) {
    let numPointsInBatch =
      b == numBatches - 1 && initPoints % batchSize
        ? initPoints % batchSize
        : batchSize;
    let points = Array(numPointsInBatch)
      .fill(null)
      .map((_, i) => ({
        id: uuidv4(),
        vector: vectors[b * batchSize + i],
        payload: { color: getRandomColor() },
      }));

    let resAddPoints = http.put(
      `${baseUrl}/collections/${collectionName}/points?${stringifySearchParams({
        wait: "true",
      })}`,
      JSON.stringify({ points }),
      params
    );
    if (
      !check(
        resAddPoints,
        checks(`add points`, {
          "status is 200": (r) => r.status === 200,
          "is OK": (r) => r.status === 200 && r.json().status === "ok",
          completed: (r) =>
            r.status === 200 && r.json().result.status === "completed",
        })
      )
    ) {
      fail(`http status: ${resAddPoints.status}\n${resAddPoints.body}`);
    }
  }
}

export default function () {

  // mimic an upsert - ie add new points with same vector as existing points
  const numUpserts = 10;
  let operations = [
    {
      upsert: {
        batch: {
          ids: Array(numUpserts)
            .fill(null)
            .map((_, i) => uuidv4()),
          payloads: Array(numUpserts)
            .fill(null)
            .map(() => ({ color: getRandomColor() })),
          vectors: Array(numUpserts)
            .fill(null)
            // reuse existing vector
            .map(() => vectors[Math.floor(Math.random() * initPoints)]),
        },
      },
    },
  ];

  if (deletePoints) {
    operations.push({
      delete: {
        filter: { must: [{ key: "color", match: { any: ["blue", "green"] } }] },
      },
    });
  }

  const resBatchUpdatePoints = http.post(
    `${baseUrl}/collections/${collectionName}/points/batch?${stringifySearchParams(
      { wait: "true", ordering: ordering }
    )}`,
    JSON.stringify({ operations }),
    params
  );
  if (
    !check(
      resBatchUpdatePoints,
      checks("batch update points", {
        "status is 200": (r) => r.status === 200,
        "is OK": (r) => r.status === 200 && r.json().status === "ok",
        completed: (r) =>
          r.status === 200 &&
          r.json().result.every((x) => x.status === "completed"),
      })
    )
  ) {
    fail(
      `http status: ${resBatchUpdatePoints.status}\n${resBatchUpdatePoints.body}`
    );
  }
}

function checks(prefix, obj) {
  return Object.fromEntries(
    Object.entries(obj).map(([k, v]) => [`${prefix} - ${k}`, v])
  );
}

function stringifySearchParams(obj) {
  return Object.entries(obj)
    .map(([k, v]) => `${k}=${v}`)
    .join("&");
}

function getRandomVector(size) {
  return Array(size)
    .fill(null)
    .map(() => Math.random());
}

function getRandomColor() {
  const i = getRandomInt(0, 3);
  if (i === 0) {
    return "red";
  }
  if (i === 1) {
    return "blue";
  }
  if (i === 2) {
    return "green";
  }
  if (i === 3) {
    return "yellow";
  }
  throw new Error(`Invalid: ${i}`);
}

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}
