# `kafkacfg`: Kafka configuration inspector

Kafka has _a lot_ of parameters, tunables and knobs, and the [configuration page](https://kafka.apache.org/34/documentation.html#configuration) isn't the easiest to parse. `kafkacfg` allows you to parse your kafka configuration file and highlights all parameters with non-default values, along with their documentation.

```console
$ cat -p test.properties
num.io.threads = 10
broker.id = 1001
auto.create.topics.enable = false
background.threads = 10
$ kafkacfg overrides --kafka-version 3.4 test.properties | jq .
{
  "num.io.threads": {
    "description": "The number of threads that the server uses for processing requests, which may include disk I/O",
    "type": "int",
    "default": "8",
    "valid_values": "[1,...]",
    "importance": "high",
    "update_mode": "cluster-wide",
    "override": "10"
  },
  "auto.create.topics.enable": {
    "description": "Enable auto creation of topic on the server",
    "type": "boolean",
    "default": "true",
    "valid_values": null,
    "importance": "high",
    "update_mode": "read-only",
    "override": "false"
  }
}
```