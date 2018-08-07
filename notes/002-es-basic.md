# es basic

## 基础概念

- Cluster，集群，es 是分布数据库
- Node，节点，集群中的一个节点
- Index，索引，对应数据库
  - 查看所有索引 `curl 'http://localhost:9200/_cat/indices?v'`
- Document，文档，对应一条记录，但是同一个 index 中的 document 可以有不同的 schema
- Type，虚拟逻辑分组，之后会被去掉
  - 查看所有分组 `curl 'http://localhost:9200/_mapping?pretty=true'`

## 操作

### 新建和删除 Index

```shell
$ curl -X PUT 'localhost:9200/weather'
{"acknowledged":true,"shards_acknowledged":true,"index":"weather"}
$ curl -X DELETE 'http://localhost:9200/weather'
{"acknowledged":true}
```

### 设置分词

```shell
$ curl -X PUT 'http://localhost:9200/accounts' -d \
'{
  "mappings": {
    "person": {
      "properties": {
        "user": {
          "type": "text",
          "analyzer": "standard",
          "search_analyzer": "standard"
        },
        "title": {
          "type": "text",
          "analyzer": "standard",
          "search_analyzer": "standard"
        },
        "desc": {
          "type": "text",
          "analyzer": "standard",
          "search_analyzer": "standard"
        }
      }
    }
  }
}'
{"acknowledged":true,"shards_acknowledged":true,"index":"accounts"}
```

- index: account
- type: person
- fields: user, title, desc

analyzer 是字段文本的分词器，search_analyzer 是搜索词的分词器。

### 添加记录

```shell
$ curl -X PUT 'http://localhost:9200/accounts/person/1' -d \
'{
  "user": "张三",
  "title": "工程师",
  "desc": "数据库管理"
}'
{"_index":"accounts","_type":"person","_id":"1","_version":1,"result":"created","_shards":{"total":2,"successful":1,"failed":0},"created":true}
```

or

```shell
$ curl -X POST 'http://localhost:9200/accounts/person' -d \
'{
  "user": "李四",
  "title": "工程师",
  "desc": "系统管理"
}'
{"_index":"accounts","_type":"person","_id":"AWUTf1Bd8NgGBIdLoQOG","_version":1,"result":"created","_shards":{"total":2,"successful":1,"failed":0},"created":true}
```

id 是字符串。

### 查看记录

```shell
$ curl 'http://localhost:9200/accounts/person/1?pretty=true'
{
  "_index" : "accounts",
  "_type" : "person",
  "_id" : "1",
  "_version" : 1,
  "found" : true,
  "_source" : {
    "user" : "张三",
    "title" : "工程师",
    "desc" : "数据库管理"
  }
}

$ curl 'http://localhost:9200/accounts/person/3?pretty=true'
{
  "_index" : "accounts",
  "_type" : "person",
  "_id" : "3",
  "found" : false
}
```

### 删除记录

```shell
$ curl -X DELETE 'http://localhost:9200/accounts/person/1'
{"found":true,"_index":"accounts","_type":"person","_id":"1","_version":2,"result":"deleted","_shards":{"total":2,"successful":1,"failed":0}}
```

### 更新记录

```shell
$ curl -X PUT 'http://localhost:9200/accounts/person/1' -d \
'{
    "user" : "张三",
    "title" : "工程师",
    "desc" : "软件开发，数据库管理"
}'
{"_index":"accounts","_type":"person","_id":"1","_version":2,"result":"updated","_shards":{"total":2,"successful":1,"failed":0},"created":false}
```

### 查询所有记录

```shell
$ curl 'http://localhost:9200/accounts/person/_search'
{"took":138,"timed_out":false,"_shards":{"total":5,"successful":5,"skipped":0,"failed":0},"hits":{"total":2,"max_score":1.0,"hits":[{"_index":"accounts","_type":"person","_id":"AWUTf1Bd8NgGBIdLoQOG","_score":1.0,"_source":{
  "user": "李四",
  "title": "工程师",
  "desc": "系统管理"
}},{"_index":"accounts","_type":"person","_id":"1","_score":1.0,"_source":{
    "user" : "张三",
    "title" : "工程师",
    "desc" : "软件开发，数据库管理"
}}]}}
```

### 全文搜索

```shell
$ curl 'http://localhost:9200/accounts/person/_search'  -d \
'{
  "query" : { "match" : { "desc" : "软件" }}
}'

$ curl 'http://localhost:9200/accounts/person/_search'  -d \
'{
  "query" : { "match" : { "desc" : "管理" }}
}'
{"took":10,"timed_out":false,"_shards":{"total":5,"successful":5,"skipped":0,"failed":0},"hits":{"total":2,"max_score":0.43273005,"hits":[{"_index":"accounts","_type":"person","_id":"AWUTf1Bd8NgGBIdLoQOG","_score":0.43273005,"_source":{
  "user": "李四",
  "title": "工程师",
  "desc": "系统管理"
}},{"_index":"accounts","_type":"person","_id":"1","_score":0.29516566,"_source":{
    "user" : "张三",
    "title" : "工程师",
    "desc" : "软件开发，数据库管理"
}}]}}
```

类似数据库中的 limit、offset 的操作：

```shell
$ curl 'http://localhost:9200/accounts/person/_search'  -d \
'{
  "query" : { "match" : { "desc" : "管理" }}, "from": 1, "size": 10
}'
{"took":10,"timed_out":false,"_shards":{"total":5,"successful":5,"skipped":0,"failed":0},"hits":{"total":2,"max_score":0.43273005,"hits":[{"_index":"accounts","_type":"person","_id":"1","_score":0.29516566,"_source":{
    "user" : "张三",
    "title" : "工程师",
    "desc" : "软件开发，数据库管理"
}}]}}
```

### 全文搜索中的逻辑运算

`or`，空格会自动当做 `or`，`软件 系统` -> `'软件' or '系统'`

```shell
$ curl 'http://localhost:9200/accounts/person/_search'  -d \
'{
  "query" : { "match" : { "desc" : "软件 系统" }}
}'
{"took":15,"timed_out":false,"_shards":{"total":5,"successful":5,"skipped":0,"failed":0},"hits":{"total":2,"max_score":1.6451461,"hits":[{"_index":"accounts","_type":"person","_id":"AWUTf1Bd8NgGBIdLoQOG","_score":1.6451461,"_source":{
  "user": "李四",
  "title": "工程师",
  "desc": "系统管理"
}},{"_index":"accounts","_type":"person","_id":"1","_score":1.122156,"_source":{
    "user" : "张三",
    "title" : "工程师",
    "desc" : "软件开发，数据库管理"
}}]}}
```

and

```shell
$ curl 'http://localhost:9200/accounts/person/_search'  -d \
'{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "desc": "软件"
          }
        },
        {
          "match": {
            "desc": "系统"
          }
        }
      ]
    }
  }
}'
{"took":14,"timed_out":false,"_shards":{"total":5,"successful":5,"skipped":0,"failed":0},"hits":{"total":0,"max_score":null,"hits":[]}}
```

## 分词测试

由于 standard 分词是直接一个字一个字的分开，所以换个顺序依然能搜索到。

```shell
$ curl 'http://localhost:9200/accounts/person/_search'  -d \
'{
  "query" : { "match" : { "desc" : "理管" }}
}'
```

## refs

- [全文搜索引擎 Elasticsearch 入门教程 - 阮一峰的网络日志](http://www.ruanyifeng.com/blog/2017/08/elasticsearch.html)
