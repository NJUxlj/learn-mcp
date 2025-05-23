# PersonalKB: 智谱AI+MCP工具增强的个人知识库  

一个与智谱AI集成的个人知识库系统。本项目允许您使用智谱的大语言模型直接与您的知识库进行交互，帮助您管理和检索个人笔记和信息。  

## 功能特点  

- 创建、读取、更新和删除笔记  
- 标签系统用于组织  
- 全文搜索功能  
- 智谱AI模型集成  
- 使用SQLite数据库实现简单性和可移植性  
- 交互式命令行界面  


## 在不安装包的情况下使用
```bash
git clone https://github.com/yourusername/personal-kb-mcp.git  
cd personal-kb-mcp 

# 首先确保你本地有一个conda环境，没有的话可以创建一个
pip install uv
uv venv .venv    # 为本项目单独创建一个虚拟环境

source .venv/bin/activate 【Linux】
./.venv/Scripts/activate 【Windows】

uv pip install -r pyproject.toml  # 安装项目依赖



## 启动mcp服务器
uv run python -m personal_kb.server run 

## 启动对话客户端
uv run python -m personal_kb.chat_app chat


## 启动cli
uv run python -m personal_kb.cli
```

## 安装 personal-kb-mcp 包，并运行命令行工具，实现与上面相同的功能

```bash  
# 从源代码安装  
git clone https://github.com/yourusername/personal-kb-mcp.git  
cd personal-kb-mcp 

# 安装项目及其依赖  【安装 personal-kb-mcp 包】
pip install -e .  

# 激活虚拟环境
source .venv/bin/activate 【Linux】
./.venv/Scripts/activate 【Windows】

# 激活行会在命令行最前面显示 (personal-kb-mcp)

# 初始化数据库（创建示例笔记）  
personalkb init  

```


使用方法
设置API密钥
在使用智谱API之前，需要设置API密钥：

```bash
export ZHIPU_API_KEY="your_api_key_here"  
```
或者您可以在运行命令时通过参数传递密钥。

启动交互式聊天界面
```bash
personalkb-chat  
```
或者指定模型：

```bash
personalkb-chat --model glm-4  
```

使用命令行工具管理知识库
```bash
# 显示知识库统计信息  
personalkb-cli stats  

# 列出所有笔记  
personalkb-cli list-notes  

# 添加新笔记（会打开编辑器）  
personalkb-cli add --title "我的新笔记" --tags "测试,笔记,示例"  

# 搜索笔记  
personalkb-cli search "关键词"  

# 显示笔记详情  
personalkb-cli show 1  

# 编辑笔记内容  
personalkb-cli edit 1 --edit-content  

# 列出所有标签  
personalkb-cli tags  
```

启动MCP服务器
```bash
# 启动MCP服务器  
personalkb run  
```


在您自己的Python代码中使用
```python
from personal_kb.zhipu_client import ZhipuClient  

# 创建客户端  
client = ZhipuClient(api_key="your_api_key_here")  

# 启动对话  
response = client.chat([  
{"role": "user", "content": "创建一个关于Python的新笔记"}  
])  

print(response)  
```

对话示例
您可以在交互式聊天界面中尝试以下命令：

"创建一个关于机器学习基础的新笔记"
"搜索我的知识库中的食谱"
"列出我的知识库中的所有标签"
"显示与Python相关的笔记"
"更新我的关于园艺的笔记，加入关于番茄的信息"


## 开发说明
本项目使用Model Context Protocol (MCP)作为底层技术，允许智谱AI模型与知识库交互。项目结构：

server.py: MCP服务器实现
database.py: 数据库操作
zhipu_client.py: 智谱API客户端
chat_app.py: 交互式命令行应用


## 许可证
MIT


