# MCP+GraphRAG搭建检索增强智能体
我们根据GraphRAG API的调用方法，来创建一个基于GraphRAG的MCP智能体服务器，并尝试在本地client对其进行调用。



## 创建MCP客户端项目
```
uv init mcp-graphrag
```


## 初始化 GraphRAG 索引目录
```
mkdir -p ./ragtest/input
graphrag init --root ./ragtest
```
- 你自己加的本地文档都应该放在 `./ragtest/input` 目录下, 目前只支持txt和csv格式的文件。
- 你也可以直接使用我创建好的 `./ragtest/` 目录作为示例，那样就不需要运行此命令了。


## 使用 GraphRAG 构建文档索引
```
graphrag index --root ./ragtest
```



## 使用 GraphRAG进行查询
```
graphrag query --root ./ragtest --method local --queryd "请帮我介绍一下ID3算法"
```
- --root: 指定GraphRAG的根目录，用于存储索引和配置文件。
- --method: 指定查询的方法，可以是"local"或"global"。 "local"表示使用实体entity进行检索，"global"表示使用聚类获得的社区报告（community report)进行检索。
- --query: 指定要查询的文本。
