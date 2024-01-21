# `kafkacfg`: Kafka configuration analyzer CLI

Kafka has _a lot_ of parameters, tunables and knobs, and the [configuration page](https://kafka.apache.org/documentation/#brokerconfigs) isn't the easiest to parse. `kafkacfg` allows you to analyze your kafka configuration file, to help you understand what it does.

> [!NOTE]
> all `kafkacfg` commands (except `kafkacfg recommends`) can be passed a `--source librdkafka` argument, to work on the `librdkafka` [configuration parameters](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md) instead of the [Kafka parameters](https://kafka.apache.org/documentation/#brokerconfigs)


### `kafkacfg explain`

This command is used to display extra information about each configuration tunable used in your configuration file.

```console
$ cat samples/server.properties
num.io.threads = 10
broker.id = 1001
auto.create.topics.enable = false
background.threads = 10
```

```console
$ kafkacfg explain -k 3.4 samples/server.properties | jq .
[
  {
    "name": "num.io.threads",
    "override": "10",
    "description": "The number of threads that the server uses for processing requests, which may include disk I/O",
    "scope": "broker",
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
    "scope": "broker",
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
    "scope": "broker",
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
    "scope": "broker",
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
$ kafkacfg explain -k 3.4 samples/server.properties | jtbl
╒═══════════════════════════╤════════════╤═══════════════════════════════════════════════════════════════════════╤═════════╤═════════╤═══════════╤════════════════╤══════════════╤═══════════════╕
│ name                      │ override   │ description                                                           │ scope   │ type    │ default   │ valid_values   │ importance   │ update_mode   │
╞═══════════════════════════╪════════════╪═══════════════════════════════════════════════════════════════════════╪═════════╪═════════╪═══════════╪════════════════╪══════════════╪═══════════════╡
│ num.io.threads            │ 10         │ The number of threads that the server uses for processing requests, w │ broker  │ int     │ 8         │ [1,...]        │ high         │ cluster-wide  │
│                           │            │ hich may include disk I/O                                             │         │         │           │                │              │               │
├───────────────────────────┼────────────┼───────────────────────────────────────────────────────────────────────┼─────────┼─────────┼───────────┼────────────────┼──────────────┼───────────────┤
│ broker.id                 │ 1001       │ The broker id for this server. If unset, a unique broker id will be g │ broker  │ int     │ -1        │                │ high         │ read-only     │
│                           │            │ enerated.To avoid conflicts between zookeeper generated broker id's a │         │         │           │                │              │               │
│                           │            │ nd user configured broker id's, generated broker ids start from reser │         │         │           │                │              │               │
│                           │            │ ved.broker.max.id + 1.                                                │         │         │           │                │              │               │
├───────────────────────────┼────────────┼───────────────────────────────────────────────────────────────────────┼─────────┼─────────┼───────────┼────────────────┼──────────────┼───────────────┤
│ auto.create.topics.enable │ false      │ Enable auto creation of topic on the server                           │ broker  │ boolean │ true      │                │ high         │ read-only     │
├───────────────────────────┼────────────┼───────────────────────────────────────────────────────────────────────┼─────────┼─────────┼───────────┼────────────────┼──────────────┼───────────────┤
│ background.threads        │ 10         │ The number of threads to use for various background processing tasks  │ broker  │ int     │ 10        │ [1,...]        │ high         │ cluster-wide  │
╘═══════════════════════════╧════════════╧═══════════════════════════════════════════════════════════════════════╧═════════╧═════════╧═══════════╧════════════════╧══════════════╧═══════════════╛
```

You can also explain producer and consumer level configurations, by using the `-c / --config-type` flag:

```console
$ cat -p samples/producer.properties
compression.type=lz4
retries=2
$ kafkacfg explain -k 1.1 --config-type producer samples/producer.properties  | jtbl
╒══════════════════╤════════════╤═══════════════════════════════════════════════════════════════════════════════════════════════╤══════════╤════════╤═══════════╤════════════════════╤══════════════╕
│ name             │ override   │ description                                                                                   │ scope    │ type   │ default   │ valid_values       │ importance   │
╞══════════════════╪════════════╪═══════════════════════════════════════════════════════════════════════════════════════════════╪══════════╪════════╪═══════════╪════════════════════╪══════════════╡
│ compression.type │ lz4        │ The compression type for all data generated by the producer. The default is none (i.e. no com │ producer │ string │ none      │                    │ high         │
│                  │            │ pression). Valid  values are none, gzip, snappy, or lz4. Compression is of full batches of da │          │        │           │                    │              │
│                  │            │ ta, so the efficacy of batching will also impact the compression ratio (more batching means b │          │        │           │                    │              │
│                  │            │ etter compression).                                                                           │          │        │           │                    │              │
├──────────────────┼────────────┼───────────────────────────────────────────────────────────────────────────────────────────────┼──────────┼────────┼───────────┼────────────────────┼──────────────┤
│ retries          │ 2          │ Setting a value greater than zero will cause the client to resend any record whose send fails │ producer │ int    │ 0         │ [0,...,2147483647] │ high         │
│                  │            │  with a potentially transient error. Note that this retry is no different than if the client  │          │        │           │                    │              │
│                  │            │ resent the record upon receiving the error. Allowing retries without setting max.in.flight.re │          │        │           │                    │              │
│                  │            │ quests.per.connection to 1 will potentially change the ordering of records because if two bat │          │        │           │                    │              │
│                  │            │ ches are sent to a single partition, and the first fails and is retried but the second succee │          │        │           │                    │              │
│                  │            │ ds, then the records in the second batch may appear first.                                    │          │        │           │                    │              │
╘══════════════════╧════════════╧═══════════════════════════════════════════════════════════════════════════════════════════════╧══════════╧════════╧═══════════╧════════════════════╧══════════════╛
```

### `kafkacfg overrides`

The `overrides` command will only display and enrich the configuration tunables with non-default values, to help you understand in what way your kafka configuration was tuned:

```console
$ kafkacfg overrides -k 3.4 samples/server.properties | jtbl
name                       override    description                                                                                     scope    type     default    valid_values    importance    update_mode
-------------------------  ----------  ----------------------------------------------------------------------------------------------  -------  -------  ---------  --------------  ------------  -------------
num.io.threads             10          The number of threads that the server uses for processing requests, which may include disk I/O  broker   int      8          [1,...]         high          cluster-wide
auto.create.topics.enable  false       Enable auto creation of topic on the server                                                     broker   boolean  true                       high          read-only
```

You can also explain producer and consumer level configurations override, by using the `-c / --config-type` flag.

### `kafkacfg query`

The `query` command allows you to filter the kafka configuration tunables with a custom query, while enriching the filter results with the usual metadata and potential override value.

```console
$ kafkacfg query -v 1.1 'name=replica.fetch.min.bytes' | jtbl
name                     override    description                                                                                           scope    type      default  valid_values    importance    update_mode
-----------------------  ----------  ----------------------------------------------------------------------------------------------------  -------  ------  ---------  --------------  ------------  -------------
replica.fetch.min.bytes              Minimum bytes expected for each fetch response. If not enough bytes, wait up to replicaMaxWaitTimeMs  broker   int             1                  high          read-only
```

You can also compose filter predicates and even use `*` for a glob match:

```console
$ kafkacfg query -v 3.4 "name=replica.*.bytes;importance=high" | jtbl
╒═════════════════════════════════════╤════════════╤═══════════════════════════════════════════════════╤═════════╤════════╤══════════════════════╤════════════════╤══════════════╤═══════════════╕
│ name                                │ override   │ description                                       │ scope   │ type   │ default              │ valid_values   │ importance   │ update_mode   │
╞═════════════════════════════════════╪════════════╪═══════════════════════════════════════════════════╪═════════╪════════╪══════════════════════╪════════════════╪══════════════╪═══════════════╡
│ replica.fetch.min.bytes             │            │ Minimum bytes expected for each fetch response. I │ broker  │ int    │ 1                    │                │ high         │ read-only     │
│                                     │            │ f not enough bytes, wait up to replica.fetch.wait │         │        │                      │                │              │               │
│                                     │            │ .max.ms (broker config).                          │         │        │                      │                │              │               │
├─────────────────────────────────────┼────────────┼───────────────────────────────────────────────────┼─────────┼────────┼──────────────────────┼────────────────┼──────────────┼───────────────┤
│ replica.socket.receive.buffer.bytes │            │ The socket receive buffer for network requests    │ broker  │ int    │ 65536 (64 kibibytes) │                │ high         │ read-only     │
╘═════════════════════════════════════╧════════════╧═══════════════════════════════════════════════════╧═════════╧════════╧══════════════════════╧════════════════╧══════════════╧═══════════════╛
```

### `kafkacfg recommends`

The `recommends` command emits sourced configuration recommendation based on broker attributes (number of CPUs, number of disks, etc).

> _Note_: These are suggestions more than absolute thruths. We encourage you to read the sources, test the configuration values and make your own mind.

```console
$ kafkacfg recommends -k 3.4 --broker-num-cpus 24 --broker-num-disks 12 samples/server.properties
Recommendation 1: set num.io.threads == 12 (num_disks)
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


### `kafkacfg diff`

The `diff` command displays what configuration tunables have changed between 2 kafka versions, whether they have been deprecated, newly introduced, or their default value has changed.


```console

$ kafkacfg diff --from-version 3.5 --to-version 3.6 | jtbl
╒═══════════════════════════════════════════════╤══════════╤════════════════════════════════════════════════════════════╤═════════╤═════════╤════════════════════════════════════════════════════════════╤══════════════╤═══════════════╤═════════════════╤════════════════════════════════════════════════════════════╤═════════════════════════════════════╕
│ name                                          │ status   │ description                                                │ scope   │ type    │ valid_values                                               │ importance   │ update_mode   │ default (3.5)   │ default (3.6)                                              │ server_default_property             │
╞═══════════════════════════════════════════════╪══════════╪════════════════════════════════════════════════════════════╪═════════╪═════════╪════════════════════════════════════════════════════════════╪══════════════╪═══════════════╪═════════════════╪════════════════════════════════════════════════════════════╪═════════════════════════════════════╡
│ log.local.retention.bytes                     │ new      │ The maximum size of local log segments that can grow for a │ broker  │ long    │ [-2,...]                                                   │ medium       │ cluster-wide  │ [ABSENT]        │ -2                                                         │                                     │
│                                               │          │  partition before it gets eligible for deletion. Default v │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │ alue is -2, it represents `log.retention.bytes` value to b │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │ e used. The effective value should always be less than or  │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │ equal to `log.retention.bytes` value.                      │         │         │                                                            │              │               │                 │                                                            │                                     │
├───────────────────────────────────────────────┼──────────┼────────────────────────────────────────────────────────────┼─────────┼─────────┼────────────────────────────────────────────────────────────┼──────────────┼───────────────┼─────────────────┼────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
│ log.local.retention.ms                        │ new      │ The number of milliseconds to keep the local log segments  │ broker  │ long    │ [-2,...]                                                   │ medium       │ cluster-wide  │ [ABSENT]        │ -2                                                         │                                     │
│                                               │          │ before it gets eligible for deletion. Default value is -2, │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │  it represents `log.retention.ms` value is to be used. The │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │  effective value should always be less than or equal to `l │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │ og.retention.ms` value.                                    │         │         │                                                            │              │               │                 │                                                            │                                     │
├───────────────────────────────────────────────┼──────────┼────────────────────────────────────────────────────────────┼─────────┼─────────┼────────────────────────────────────────────────────────────┼──────────────┼───────────────┼─────────────────┼────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
│ log.message.timestamp.after.max.ms            │ new      │ This configuration sets the allowable timestamp difference │ broker  │ long    │ [0,...]                                                    │ medium       │ cluster-wide  │ [ABSENT]        │ 9223372036854775807                                        │                                     │
│                                               │          │  between the message timestamp and the broker's timestamp. │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │  The message timestamp can be later than or equal to the b │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │ roker's timestamp, with the maximum allowable difference d │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │ etermined by the value set in this configuration. If log.m │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │ essage.timestamp.type=CreateTime, the message will be reje │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │ cted if the difference in timestamps exceeds this specifie │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │ d threshold. This configuration is ignored if log.message. │         │         │                                                            │              │               │                 │                                                            │                                     │
│                                               │          │ timestamp.type=LogAppendTime.                              │         │         │                                                            │              │               │                 │                                                            │                                     │
├───────────────────────────────────────────────┼──────────┼────────────────────────────────────────────────────────────┼─────────┼─────────┼────────────────────────────────────────────────────────────┼──────────────┼───────────────┼─────────────────┼────────────────────────────────────────────────────────────┼─────────────────────────────────────┤
...
```

You can also highlight changes in producer and consumer level configurations, by using the `-c / --config-type` flag.
