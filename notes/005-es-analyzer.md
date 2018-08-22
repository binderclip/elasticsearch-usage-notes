# es analyzer

analyzer 就是分词器。

## test ik analyzer

```shell
$ curl -X POST 'http://localhost:9200/_analyze?pretty' -d \
'{
  "analyzer": "ik_smart",
  "text": "大西瓜"
}'
{
  "tokens" : [
    {
      "token" : "大",
      "start_offset" : 0,
      "end_offset" : 1,
      "type" : "CN_CHAR",
      "position" : 0
    },
    {
      "token" : "西瓜",
      "start_offset" : 1,
      "end_offset" : 3,
      "type" : "CN_WORD",
      "position" : 1
    }
  ]
}
```

```shell
$ curl -X POST 'http://localhost:9200/_analyze?pretty' -d \
'{
  "analyzer": "ik_max_word",
  "text": "大西瓜"
}'
{
  "tokens" : [
    {
      "token" : "大西",
      "start_offset" : 0,
      "end_offset" : 2,
      "type" : "CN_WORD",
      "position" : 0
    },
    {
      "token" : "西瓜",
      "start_offset" : 1,
      "end_offset" : 3,
      "type" : "CN_WORD",
      "position" : 1
    }
  ]
}
```

## install ik analyzer

- plugins 目录可能也需要挂载
- 使用 unzip 安装的方式安装 ik 插件
- 重启 es

## analyzer test api

```shell
$ curl -X POST 'http://localhost:9200/_analyze?pretty' -d \
'{
  "analyzer": "standard",
  "text": "大西瓜"
}'
{
  "tokens" : [
    {
      "token" : "大",
      "start_offset" : 0,
      "end_offset" : 1,
      "type" : "<IDEOGRAPHIC>",
      "position" : 0
    },
    {
      "token" : "西",
      "start_offset" : 1,
      "end_offset" : 2,
      "type" : "<IDEOGRAPHIC>",
      "position" : 1
    },
    {
      "token" : "瓜",
      "start_offset" : 2,
      "end_offset" : 3,
      "type" : "<IDEOGRAPHIC>",
      "position" : 2
    }
  ]
}
```

## refs

- [Testing analyzers | Elasticsearch Reference [6.3] | Elastic](https://www.elastic.co/guide/en/elasticsearch/reference/current/_testing_analyzers.html)
- [medcl/elasticsearch-analysis-ik: The IK Analysis plugin integrates Lucene IK analyzer into elasticsearch, support customized dictionary.](https://github.com/medcl/elasticsearch-analysis-ik)
- [v5.6.8 index null_pointer_exception · Issue #533 · medcl/elasticsearch-analysis-ik](https://github.com/medcl/elasticsearch-analysis-ik/issues/533)
