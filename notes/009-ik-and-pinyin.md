# ik and pinyin

## 准备 docker 环境

- 设置 data 和 plugins 的 volume
- 设置端口映射

## 安装 pinyin 插件

- 查看 es 版本
- 下载对应插件版本 https://github.com/medcl/elasticsearch-analysis-pinyin/releases
- 解压到 `plugins/pinyin` 目录下

## 测试 pinyin

### 测试 analyzer

```shell
$ curl -X POST 'http://localhost:9200/_analyze?pretty' -d \
'{
  "analyzer": "pinyin",
  "text": "大西瓜"
}'
{
  "tokens" : [
    {
      "token" : "da",
      "start_offset" : 0,
      "end_offset" : 1,
      "type" : "word",
      "position" : 0
    },
    {
      "token" : "dxg",
      "start_offset" : 0,
      "end_offset" : 3,
      "type" : "word",
      "position" : 0
    },
    {
      "token" : "xi",
      "start_offset" : 1,
      "end_offset" : 2,
      "type" : "word",
      "position" : 1
    },
    {
      "token" : "gua",
      "start_offset" : 2,
      "end_offset" : 3,
      "type" : "word",
      "position" : 2
    }
  ]
}
```

// 这里会发现按照现在的配置索引出来的是单个字的拼音，以及一个全部自己的全部拼音首字母

### 创建索引

```shell
$ curl -X PUT 'localhost:9200/ikpy'
{"acknowledged":true,"shards_acknowledged":true,"index":"ikpy"}

$ curl -XPOST 'localhost:9200/ikpy/_close'
{"acknowledged":true}
$ curl -X PUT 'localhost:9200/ikpy/_settings?pretty' -d \
'{
  "analysis": {
    "analyzer": {
      "default": {
        "tokenizer": "ik_max_word"
      },
      "pinyin_analyzer": {
        "tokenizer": "my_pinyin"
      }
    },
    "tokenizer": {
      "my_pinyin": {
        "keep_separate_first_letter": "false",
        "lowercase": "true",
        "type": "pinyin",
        "limit_first_letter_length": "16",
        "keep_original": "true",
        "keep_full_pinyin": "true"
      }
    }
  }
}'

$ curl -XPOST 'localhost:9200/ikpy/_open'
{"acknowledged":true}
```

### 创建 mapping

```shell
$ curl -XPOST "localhost:9200/ikpy/test_mapping/_mapping?pretty" -d \
'{
    "test_mapping": {
            "_all":{
              "enabled":false
            },
            "properties": {
                "id": {
                    "type": "integer"
                },
                "username": {
                    "type": "text",
                    "analyzer": "pinyin_analyzer"
                },
                "description": {
                    "type": "text",
                    "analyzer": "pinyin_analyzer"
                }
            }
        }
}'
{
  "acknowledged" : true
}
```


```shell
curl -XPOST "localhost:9200/ikpy/test_mapping/?pretty" -d '
{
    "id" : 1,
    "username" :  "中国高铁速度很快",
    "description" :  "如果要修改一个字段的类型"
}'

    curl -XPOST "localhost:9200/ikpy/test_mapping/?pretty" -d '
    {
        "id" : 2,
        "username" :  "动车和复兴号，都属于高铁",
        "description" :  "现在想要修改为string类型"
    }'
```

```shell
$ curl -XPOST "localhost:9200/ikpy/test_mapping/_search?pretty"  -H "Content-Type: application/json"  -d '
{
    "query": {
        "match": {
            "username": "gaotie"
        }
    }
}'
{
  "took" : 8,
  "timed_out" : false,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : 2,
    "max_score" : 0.56977004,
    "hits" : [
      {
        "_index" : "ikpy",
        "_type" : "test_mapping",
        "_id" : "AWaqOKaHS1SZcYaFLmhu",
        "_score" : 0.56977004,
        "_source" : {
          "id" : 1,
          "username" : "中国高铁速度很快",
          "description" : "如果要修改一个字段的类型"
        }
      },
      {
        "_index" : "ikpy",
        "_type" : "test_mapping",
        "_id" : "AWaqOp-qS1SZcYaFLmhw",
        "_score" : 0.5257321,
        "_source" : {
          "id" : 2,
          "username" : "动车和复兴号，都属于高铁",
          "description" : "现在想要修改为string类型"
        }
      }
    ]
  }
}
```

## 测试 ik + pinyin

主要思路是用 ik 来分词，然后再用 pinyin 做一次 filter。

参考[Elasticsearch 5 Ik+pinyin分词配置详解 - 1.01^365=37.78 (Lucene、ES、ELK开发交流群: 370734940) - CSDN博客](https://blog.csdn.net/napoay/article/details/53907921)

### 创建索引与分析器设置

```shell
curl -XPUT "localhost:9200/ikpy2/" -d'
{
    "index": {
        "analysis": {
            "analyzer": {
                "ik_pinyin_analyzer": {
                    "type": "custom",
                    "tokenizer": "ik_smart",
                    "filter": ["my_pinyin", "word_delimiter"]
                }
            },
            "filter": {
                "my_pinyin": {
                    "type": "pinyin",
                    "first_letter": "prefix",
                    "padding_char": " "
                }
            }
        }
    }
}'
```

创建一个 type 并设置 mapping：

```shell
curl -XPOST http://localhost:9200/ikpy2/folks/_mapping -d'
{
    "folks": {
        "properties": {
            "name": {
                "type": "keyword",
                "fields": {
                    "pinyin": {
                        "type": "text",
                        "store": "no",
                        "term_vector": "with_positions_offsets",
                        "analyzer": "ik_pinyin_analyzer",
                        "boost": 10
                    }
                }
            }
        }
    }
}'
```

### 索引测试文档

```shell
curl -XPOST http://localhost:9200/ikpy2/folks/andy -d'{"name":"刘德华"}'
curl -XPOST http://localhost:9200/ikpy2/folks/tina -d'{"name":"中华人民共和国国歌"}'
```

### 测试(1)拼音分词

```shell
curl -XPOST "http://localhost:9200/ikpy2/folks/_search?q=name.pinyin:liu"
curl -XPOST "http://localhost:9200/ikpy2/folks/_search?q=name.pinyin:de"
curl -XPOST "http://localhost:9200/ikpy2/folks/_search?q=name.pinyin:hua"
curl -XPOST "http://localhost:9200/ikpy2/folks/_search?q=name.pinyin:ldh"
# 上面的可以搜索到

curl -XPOST "http://localhost:9200/ikpy2/folks/_search?q=name.pinyin:liudehua"
# 会被切开再按单个的搜索

curl -XPOST "http://localhost:9200/ikpy2/folks/_search?q=刘德华"
# 无结果
```

### 测试(2) IK 分词测试

```shell
curl -XPOST "http://localhost:9200/ikpy2/_search?pretty" -d'
{
  "query": {
    "match": {
      "name.pinyin": "国歌"
    }
  },
  "highlight": {
    "fields": {
      "name.pinyin": {}
    }
  }
}'
```

```shell
{
  "took" : 77,
  "timed_out" : false,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : 1,
    "max_score" : 9.507006,
    "hits" : [
      {
        "_index" : "ikpy2",
        "_type" : "folks",
        "_id" : "tina",
        "_score" : 9.507006,
        "_source" : {
          "name" : "中华人民共和国国歌"
        },
        "highlight" : {
          "name.pinyin" : [
            "<em>中华人民共和国</em><em>国歌</em>"
          ]
        }
      }
    ]
  }
}
```

### 测试(4) pinyin+ik 分词测试

```shell
curl -XPOST "http://localhost:9200/ikpy2/_search?pretty" -d'
{
  "query": {
    "match": {
      "name.pinyin": "zhonghua"
    }
  },
  "highlight": {
    "fields": {
      "name.pinyin": {}
    }
  }
}'
```

```shell
{
  "took" : 18,
  "timed_out" : false,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : 2,
    "max_score" : 6.188843,
    "hits" : [
      {
        "_index" : "ikpy2",
        "_type" : "folks",
        "_id" : "tina",
        "_score" : 6.188843,
        "_source" : {
          "name" : "中华人民共和国国歌"
        },
        "highlight" : {
          "name.pinyin" : [
            "<em>中华人民共和国</em>国歌"
          ]
        }
      },
      {
        "_index" : "ikpy2",
        "_type" : "folks",
        "_id" : "andy",
        "_score" : 0.22534128,
        "_source" : {
          "name" : "刘德华"
        },
        "highlight" : {
          "name.pinyin" : [
            "<em>刘德华</em>"
          ]
        }
      }
    ]
  }
}
```

```shell
$ curl -X POST 'http://localhost:9200/ikpy2/_analyze?pretty' -d \
'{
  "analyzer": "ik_pinyin_analyzer",
  "text": "大西瓜"
}'
{
  "tokens" : [
    {
      "token" : "da",
      "start_offset" : 0,
      "end_offset" : 1,
      "type" : "CN_CHAR",
      "position" : 0
    },
    {
      "token" : "d",
      "start_offset" : 0,
      "end_offset" : 1,
      "type" : "CN_CHAR",
      "position" : 0
    },
    {
      "token" : "xi",
      "start_offset" : 1,
      "end_offset" : 3,
      "type" : "CN_WORD",
      "position" : 1
    },
    {
      "token" : "gua",
      "start_offset" : 1,
      "end_offset" : 3,
      "type" : "CN_WORD",
      "position" : 2
    },
    {
      "token" : "xg",
      "start_offset" : 1,
      "end_offset" : 3,
      "type" : "CN_WORD",
      "position" : 2
    }
  ]
}
```

使用 pinyin 分词以后，原始的字段搜索要加上 `.pinyin` 后缀，搜索原始字段没有返回结果

## refs

- [ES中安装中文/拼音分词器（IK+pinyin） - 简书](https://www.jianshu.com/p/653f7b33e63c) 
- [elasticsearch 拼音 中文 分词 混合使用«海底苍鹰(tank)博客](http://blog.51yip.com/server/1894.html)
- [elasticsearch - error when trying to update the settings - Stack Overflow](https://stackoverflow.com/questions/19758335/error-when-trying-to-update-the-settings)
- [Update Indices Settings | Elasticsearch Reference [6.4] | Elastic](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-update-settings.html#indices-update-settings)
- [elastic search配置ik分词及pinyin分词使搜索同时支持中文和拼音搜索 - u013905744的专栏 - CSDN博客](https://blog.csdn.net/u013905744/article/details/80935846)
- [Elasticsearch 5 Ik+pinyin分词配置详解 - 1.01^365=37.78 (Lucene、ES、ELK开发交流群: 370734940) - CSDN博客](https://blog.csdn.net/napoay/article/details/53907921)
