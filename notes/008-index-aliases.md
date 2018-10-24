# index alias

## 为了支持 alias 代码中需要作出的操作

## 如果已经直接设置了 index 但又想用上 alias

- foo -> foo_temp
- app use foo_temp
- create foo_20180901
- foo_20180901 -> foo_temp, foo x> foo_temp
- delete foo
- foo_20180901 -> foo
- app use foo
- foo_20180901 x> foo_temp

## 思路

- _aliases 可以一下子添加和移除一个 alias
- 可以新建 index、重建索引、一键切换

## refs

- [索引别名和零停机 | Elasticsearch: 权威指南 | Elastic](https://www.elastic.co/guide/cn/elasticsearch/guide/current/index-aliases.html)
