## 配置 mcp-client 环境
```
conda create -n mcp-client python=3.12 -y

conda activate mcp-client

pip install uv

uv add mcp openai python-dotenv

# 或者
uv pip install mcp openai python-dotenv
```

## 配置模型服务相关变量
- 在项目根目录下创建 .env 文件，内容如下：
```
BASE_URL="反向代理地址"
MODEL=glm-4-flash
OPENAI_API_KEY="OpenAI-API-Key"
```


## 运行 mcp-client
```
uv run client.py
uv run client2.py

# 或
uv run --active client.py
```