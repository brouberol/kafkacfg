# `kafkacfg`: Kafka configuration inspector

Kafka has _a lot_ of parameters, tunables and knobs, and the [configuration page](https://kafka.apache.org/34/documentation.html#configuration) isn't the easiest to parse. `kafkacfg` allows you to parse your kafka configuration file help you understand what it does.

### `kafkacfg explain`

This command is used to display extra information about each configuration tunable used in your configuration file.

```console
$ cat test.properties
num.io.threads = 10
broker.id = 1001
auto.create.topics.enable = false
background.threads = 10
```

```console
$ kafkacfg explain -k 3.4 test.properties | jq .
[
  {
    "name": "num.io.threads",
    "override": "10",
    "description": "The number of threads that the server uses for processing requests, which may include disk I/O",
    "type": "int",
    "default": "8",
    "valid_values": "[1,...]",
    "importance": "high",
    "update_mode": "cluster-wide"
  },
  {
    "name": "broker.id",
    "override": "1001",
    "description": "The broker id for this server. If unset, a unique broker id will be generated.To avoid conflicts between zookeeper generated broker id's and user configured broker id's, generated broker ids start from reserved.broker.max.id + 1.",
    "type": "int",
    "default": "-1",
    "valid_values": null,
    "importance": "high",
    "update_mode": "read-only"
  },
  {
    "name": "auto.create.topics.enable",
    "override": "false",
    "description": "Enable auto creation of topic on the server",
    "type": "boolean",
    "default": "true",
    "valid_values": null,
    "importance": "high",
    "update_mode": "read-only"
  },
  {
    "name": "background.threads",
    "override": "10",
    "description": "The number of threads to use for various background processing tasks",
    "type": "int",
    "default": "10",
    "valid_values": "[1,...]",
    "importance": "high",
    "update_mode": "cluster-wide"
  }
]
```

This format makes it easy to pipe it through table formatting tools such as `jtbl`:

```console
$ kafkacfg explain -k 3.4 test.properties | jtbl
╒═══════════════════════════╤════════════╤═══════════════════════════════════╤═════════╤═══════════╤════════════════╤══════════════╤═══════════════╕
│ name                      │ override   │ description                       │ type    │ default   │ valid_values   │ importance   │ update_mode   │
╞═══════════════════════════╪════════════╪═══════════════════════════════════╪═════════╪═══════════╪════════════════╪══════════════╪═══════════════╡
│ num.io.threads            │ 10         │ The number of threads that the se │ int     │ 8         │ [1,...]        │ high         │ cluster-wide  │
│                           │            │ rver uses for processing requests │         │           │                │              │               │
│                           │            │ , which may include disk I/O      │         │           │                │              │               │
├───────────────────────────┼────────────┼───────────────────────────────────┼─────────┼───────────┼────────────────┼──────────────┼───────────────┤
│ broker.id                 │ 1001       │ The broker id for this server. If │ int     │ -1        │                │ high         │ read-only     │
│                           │            │  unset, a unique broker id will b │         │           │                │              │               │
│                           │            │ e generated.To avoid conflicts be │         │           │                │              │               │
│                           │            │ tween zookeeper generated broker  │         │           │                │              │               │
│                           │            │ id's and user configured broker i │         │           │                │              │               │
│                           │            │ d's, generated broker ids start f │         │           │                │              │               │
│                           │            │ rom reserved.broker.max.id + 1.   │         │           │                │              │               │
├───────────────────────────┼────────────┼───────────────────────────────────┼─────────┼───────────┼────────────────┼──────────────┼───────────────┤
│ auto.create.topics.enable │ false      │ Enable auto creation of topic on  │ boolean │ true      │                │ high         │ read-only     │
│                           │            │ the server                        │         │           │                │              │               │
├───────────────────────────┼────────────┼───────────────────────────────────┼─────────┼───────────┼────────────────┼──────────────┼───────────────┤
│ background.threads        │ 10         │ The number of threads to use for  │ int     │ 10        │ [1,...]        │ high         │ cluster-wide  │
│                           │            │ various background processing tas │         │           │                │              │               │
│                           │            │ ks                                │         │           │                │              │               │
╘═══════════════════════════╧════════════╧═══════════════════════════════════╧═════════╧═══════════╧════════════════╧══════════════╧═══════════════╛
```

### `kafkacfg overrides`

The `overrides` command will only display and enrich the configuration tunables with non-default values, to help you understand in what way your kafka configuration was tuned:

```console
$ kafkacfg overrides -k 3.4 test.properties | jtbl
name                       override    description                                                                                     type     default    valid_values    importance    update_mode
-------------------------  ----------  ----------------------------------------------------------------------------------------------  -------  ---------  --------------  ------------  -------------
num.io.threads             10          The number of threads that the server uses for processing requests, which may include disk I/O  int      8          [1,...]         high          cluster-wide
auto.create.topics.enable  false       Enable auto creation of topic on the server                                                     boolean  true                       high          read-only
```

### `kafkacfg filter`

The `filter` command allows you to filter the kafka configuration tunables with a custom query, while enriching the filter results with the usual metadata and potential override value.

```console
$ kafkacfg filter --query name=replica.fetch.min.bytes -k 1.1 server.properties | jtbl
name                     override    description                                                                                           type      default  valid_values    importance    update_mode
-----------------------  ----------  ----------------------------------------------------------------------------------------------------  ------  ---------  --------------  ------------  -------------
replica.fetch.min.bytes              Minimum bytes expected for each fetch response. If not enough bytes, wait up to replicaMaxWaitTimeMs  int             1                  high          read-only
```

You can also compose filter predicates and even use `*` for a glob match:

```console
$ kafkacfg filter --query "name=replica.*.bytes;importance=high" -k 3.4 server.properties | jtbl
name                                 override    description                                                                                           type      default  valid_values    importance    update_mode
-----------------------------------  ----------  ----------------------------------------------------------------------------------------------------  ------  ---------  --------------  ------------  -------------
replica.fetch.min.bytes                     512  Minimum bytes expected for each fetch response. If not enough bytes, wait up to replicaMaxWaitTimeMs  int             1                  high          read-only
replica.socket.receive.buffer.bytes              The socket receive buffer for network requests                                                        int         65536                  high          read-only
```


### `kafkacfg recommends`

The `recommends` command emits sourced configuration recommendation based on broker attributes (number of CPUs, number of disks, etc).

> *Note*: These are suggestions more than absolute thruths. We encourage you to read the sources, test the configuration values and make your own mind.

```console
$ kafkacfg recommends -k 3.4 --broker-num-cpus 24 --broker-num-disks 12 server.properties
Recommendation 1: set num.io.threads == 12
* https://strimzi.io/blog/2021/06/08/broker-tuning/

Recommendation 2: set replica.fetch.min.bytes == 512
* https://azure.microsoft.com/en-us/blog/processing-trillions-of-events-per-day-with-apache-kafka-on-azure/

Recommendation 3: set socket.receive.buffer.bytes == 512
* https://azure.microsoft.com/en-us/blog/processing-trillions-of-events-per-day-with-apache-kafka-on-azure/
* https://strimzi.io/blog/2021/06/08/broker-tuning/

Recommendation 4: set socket.send.buffer.bytes == 1048576
* https://azure.microsoft.com/en-us/blog/processing-trillions-of-events-per-day-with-apache-kafka-on-azure/
* https://strimzi.io/blog/2021/06/08/broker-tuning/

Recommendation 5: set replica.socket.receive.buffer.bytes == 1048576
* https://azure.microsoft.com/en-us/blog/processing-trillions-of-events-per-day-with-apache-kafka-on-azure/
```
