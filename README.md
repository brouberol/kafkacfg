# `kafkacfg`: Kafka configuration inspector

Kafka has _a lot_ of parameters, tunables and knobs, and the [configuration page](https://kafka.apache.org/34/documentation.html#configuration) isn't the easiest to parse. `kafkacfg` allows you to parse your kafka configuration file help you understand what it does.

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

The `overrides` command will only display and enrich the configuration tunables with non-default values, to help you understand in what way your kafka configuration was tuned:

```console
$ kafkacfg overrides -k 3.4 test.properties | jtbl
name                       override    description                                                                                     type     default    valid_values    importance    update_mode
-------------------------  ----------  ----------------------------------------------------------------------------------------------  -------  ---------  --------------  ------------  -------------
num.io.threads             10          The number of threads that the server uses for processing requests, which may include disk I/O  int      8          [1,...]         high          cluster-wide
auto.create.topics.enable  false       Enable auto creation of topic on the server                                                     boolean  true                       high          read-only
```
