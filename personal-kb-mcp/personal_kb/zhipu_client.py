"""  
智谱AI API客户端集成模块。  
该模块提供了与智谱API交互和调用MCP服务器的功能。  
"""  

import json  
import os  
from uuid import uuid4
import subprocess  
import tempfile  
from typing import List, Dict, Any, Literal, Optional, Union  
import zhipuai  
from openai import OpenAI
import requests  
import time
# 原导包语句写法正确，此处保持不变
from rich.console import Console


from dotenv import load_dotenv

# 调用 load_dotenv() 函数加载环境变量
load_dotenv()


console = Console()  

class ZhipuClient:  
    """智谱API客户端，用于调用GLM模型并与MCP服务器交互。"""  
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):  
        """  
        初始化智谱API客户端。  
        
        Args:  
            api_key: 智谱API密钥  
            model: 要使用的模型名称  
        """  
        # 从环境变量或参数中获取API密钥  
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")  
        self.base_url = os.getenv("BASE_URL")
        if not self.api_key:  
            raise ValueError("必须提供 ***_API_KEY 环境变量或 api_key 参数")  
            
        # 初始化智谱客户端  
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)  
        self.model = "deepseek-chat"  
        
        print("api-key = ", self.api_key)
        print("base_url = ", self.base_url)
        print("model = ", self.model)
        
        # MCP服务器进程  
        self.mcp_process = None  
        self.mcp_tools = None  
        
        
    def is_mcp_server_running(self) -> bool:
        """检查MCP服务器是否已经在运行"""
        try:
            # 尝试连接到默认端口或使用其他检查方法
            # 这里只是一个示例，您需要根据实际MCP服务器的实现进行调整
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(('localhost', 8000))  # 假设MCP服务器运行在8000端口
            s.close()
            return result == 0
        except:
            return False
        
    def start_mcp_server(self, connect_only: bool = False) -> None:  
        """启动MCP服务器作为子进程。
        
        Args:
            connect_only: 如果为True，只尝试连接现有服务器而不启动新服务器
        """  
        if self.mcp_process is not None:  
            console.log("[yellow]MCP服务器已在运行[/yellow]")  
            return  
            
        if connect_only or self.is_mcp_server_running():
            try:
                console.log("[green]连接到已运行的MCP知识库服务器...[/green]")
                # 这里实现连接到现有服务器的逻辑
                # 需要根据实际MCP服务器的连接方式实现
                # 示例代码：
                self.mcp_process = subprocess.Popen(
                    ["uv", "run", "python", "-m", "personal_kb.server", "connect"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    encoding='utf-8',
                )
                self._discover_tools()  
                return 
            except Exception as e:
                console.log(f"[red]连接到已运行的MCP服务器出错: {str(e)}[/red]")
                raise
        
        # 使用subprocess启动MCP服务器  
        try:
            console.log("[green]启动MCP知识库服务器...[/green]")  
            self.mcp_process = subprocess.Popen(  
                ["uv", "run", "python", "-m", "personal_kb.server", "run"],                         #["personalkb", "run"],  
                stdin=subprocess.PIPE,  
                stdout=subprocess.PIPE,  
                stderr=subprocess.PIPE,  
                text=True,  
                bufsize=1,
                encoding='utf-8',  # 设置编码为UTF-8 
            )  
            
            # 读取MCP服务器输出直到准备就绪  
            # for line in iter(self.mcp_process.stdout.readline, ''):  
            #     if "Server is ready." in line:  
            #         console.log("[green]MCP服务器已就绪[/green]")  
            #         break  
            
            
            console.log("[green]连接到MCP知识库服务器...[/green]")
        except Exception as e:
            console.log(f"[red]启动MCP服务器出错: {str(e)}[/red]")
            raise
        
        
        # 这里应该实现连接到已存在的MCP服务器的逻辑
        # 而不是启动新的服务器进程
                
        # 获取工具列表  
        self._discover_tools()  
    
    def stop_mcp_server(self) -> None:  
        """停止MCP服务器。"""  
        if self.mcp_process is not None:  
            console.log("[yellow]关闭MCP服务器...[/yellow]")  
            self.mcp_process.terminate()  
            self.mcp_process = None  
            console.log("[green]MCP服务器已关闭[/green]")  
    
    def _discover_tools(self) -> None:  
        """发现并缓存MCP服务器提供的工具。"""  
        # 这里我们创建一个列表工具定义，与智谱API的tool_calls兼容  
        self.mcp_tools = [  
            {  
                "type": "function",  # 新增type字段
                "function": {
                    "name": "create_note",  
                    "description": "创建一个新笔记",  
                    "parameters": {  
                        "type": "object",  
                        "properties": {  
                            "title": {"type": "string", "description": "笔记标题"},  
                            "content": {"type": "string", "description": "笔记内容"},  
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "可选的标签列表"}  
                        },  
                        "required": ["title", "content"]  
                    }  
                }
            },  
            {  
                "type": "function",
                "function": {
                    "name": "get_note",  
                    "description": "通过ID获取笔记",  
                    "parameters": {  
                        "type": "object",  
                        "properties": {  
                            "note_id": {"type": "integer", "description": "笔记ID"}  
                        },  
                        "required": ["note_id"]  
                    }  
                }
            },  
            {  
                "type": "function",
                "function": {
                    "name": "update_note",  
                    "description": "更新现有笔记",  
                    "parameters": {  
                        "type": "object",  
                        "properties": {  
                            "note_id": {"type": "integer", "description": "要更新的笔记ID"},  
                            "title": {"type": "string", "description": "可选的新标题"},  
                            "content": {"type": "string", "description": "可选的新内容"},  
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "可选的新标签列表"}  
                        },  
                        "required": ["note_id"]  
                    }  
                }
            },  
            {  
                "type": "function",
                "function": {
                    "name": "delete_note",  
                    "description": "通过ID删除笔记",  
                    "parameters": {  
                        "type": "object",  
                        "properties": {  
                            "note_id": {"type": "integer", "description": "要删除的笔记ID"}  
                        },  
                        "required": ["note_id"]  
                    }  
                }
            },  
            {  
                "type": "function",
                "function": {
                    "name": "list_notes",  
                    "description": "列出笔记（分页）",  
                    "parameters": {  
                        "type": "object",  
                        "properties": {  
                            "limit": {"type": "integer", "description": "要返回的最大笔记数"},  
                            "offset": {"type": "integer", "description": "要跳过的笔记数"}  
                        }  
                    }  
                }
            },  
            {  
                "type": "function",
                "function": {
                    "name": "search_notes",  
                    "description": "通过标题或内容搜索笔记",  
                    "parameters": {  
                        "type": "object",  
                        "properties": {  
                            "query": {"type": "string", "description": "搜索词"},  
                            "limit": {"type": "integer", "description": "要返回的最大结果数"}  
                        },  
                        "required": ["query"]  
                    }  
                }
            },  
            {  
                "type": "function",
                "function": {
                    "name": "list_tags",  
                    "description": "列出知识库中的所有标签",  
                    "parameters": {  
                        "type": "object",  
                        "properties": {}  
                    }  
                }
            },  
            {  
                "type": "function",
                "function": {
                    "name": "get_notes_by_tag",  
                    "description": "获取带有特定标签的笔记",  
                    "parameters": {  
                        "type": "object",  
                        "properties": {  
                            "tag_name": {"type": "string", "description": "筛选的标签"},  
                            "limit": {"type": "integer", "description": "要返回的最大笔记数"},  
                            "offset": {"type": "integer", "description": "要跳过的笔记数"}  
                        },  
                        "required": ["tag_name"]  
                    }  
                }
            },  
            {  
                "type": "function",
                "function": {
                    "name": "get_database_stats",  
                    "description": "获取知识库统计信息",  
                    "parameters": {  
                        "type": "object",  
                        "properties": {}  
                    }  
                }
            }  
        ]  
        
    def _execute_tool_call(self, tool_name: str, parameters: Dict[str, Any], mode:Literal["sse", "stdio"]="sse") -> Dict[str, Any]:  
        """  
        执行工具调用，与MCP服务器通信。  
        
        Args:  
            tool_name: 要调用的工具名称  
            parameters: 工具参数  
            
        Returns:  
            工具调用结果  
        """  
        # 与MCP服务器通信的简化版实现  
        # 在真实实现中，这将使用MCP客户端库  
        
        console.log(f"\n[bold green] 开始执行工具调用: tool_name:{tool_name}, parameters:{parameters}[/bold green]")
        
        if mode == "sse":
            try:
                # 改为HTTP请求方式与SSE服务器通信
                response = requests.post(
                    "http://localhost:8000/",
                    json={
                        "jsonrpc": "2.0",
                        "method": "invoke",
                        "params": {
                            "name": tool_name,
                            "parameters": parameters
                        },
                        "id": str(uuid4())
                    },
                    timeout=5
                )
                response.raise_for_status()
                return response.json().get("result", {})
                
            except Exception as e:
                console.log(f"[red]执行MCP工具调用出错: {str(e)}[/red]")
                return {"error": str(e)}
        
        
        try:
            # 检查MCP进程是否存活
            if self.mcp_process.poll() is not None:
                raise RuntimeError("MCP服务器进程已终止")
            
            console.log(f"self.mcp_process.poll() = {self.mcp_process.poll()}")
            
            # 创建调用请求  
            request = {  
                "jsonrpc": "2.0",  
                "method": "invoke",  
                "params": {  
                    "name": tool_name,  
                    "parameters": parameters  
                },  
                "id": str(uuid4())  
            }  
            
            # 将请求发送到MCP服务器  
            
            self.mcp_process.stdin.write(json.dumps(request) + "\n")  
            self.mcp_process.stdin.flush()  
            
            console.log("已将请求发送到MCP服务器")
            # 设置5秒超时
            start_time = time.time()
            response_buffer = ""
            
            while time.time() - start_time < 5:
                # 读取响应  
                if self.mcp_process.stdout.readable():
                    print("开始读取响应")
                    response_line = self.mcp_process.stdout.readline()  
                    print("读取到的响应：", response_line)
                    if response_line:
                        # - 数据累积 ：由于MCP服务器的响应可能分多次到达（特别是响应较大时）， response_buffer 用于逐步累积这些分块的响应数据。
                        # - JSON解析尝试 ：每次收到新的数据块后，代码会尝试将累积的 response_buffer 解析为JSON对象。如果解析失败（说明响应还不完整），会继续等待更多数据。
                        response_buffer += response_line
                        try:
                            response = json.loads(response_buffer)  
                            # 检查错误  
                            if "error" in response:  
                                return {"error": response["error"]}  
                            return response.get("result", {})
                        except json.JSONDecodeError:
                            # 如果不是有效的JSON，继续等待
                            continue
                        
                time.sleep(0.1)  # 避免CPU占用过高
            raise TimeoutError("MCP服务器响应超时")
        
        except Exception as e:
            console.log(f"[red]执行MCP工具调用出错: {str(e)}[/red]")
            return {"error": str(e)}
        
        
    def chat(self, messages: List[Dict[str, str]], tools: bool = True) -> Dict[str, Any]:  
        """  
        调用智谱API进行聊天。  
        
        Args:  
            messages: 聊天消息列表  
            tools: 是否启用工具(默认为True)  
            
        Returns:  
            智谱API响应  
        """  
        # 确保MCP服务器在运行  
        if tools and self.mcp_process is None:  
            self.start_mcp_server()  
        
        # 调用智谱API  
        try:  
            # 准备请求参数  
            kwargs = {  
                "model": self.model,  
                "messages": messages,  
                # "max_tokens":1024,
                # "temperature":0.7,
                # "stream":False
            }  
            
            # print("self.mcp_tools = ", self.mcp_tools)
            
            # 如果启用工具，添加工具参数  
            if tools and self.mcp_tools:  
                kwargs["tools"] = self.mcp_tools  
                kwargs["tool_choice"] = "required"    # "auto"
            
            # 调用API 
            try: 
                response = self.client.chat.completions.create(**kwargs)  
            except Exception as e:
                console.log(f"\n[red]智谱API调用出错: {str(e)}[/red]")
                return {"error": str(e)}
            
            # 处理工具调用  
            message = response.choices[0].message  
            print("message = ", message)
            
            try:
                if tools and hasattr(message, 'tool_calls') and message.tool_calls:  
                    console.log(f"\n[bold green]触发工具调用:[/bold green]")
                    # 处理工具调用并获取结果  
                    tool_results = []  
                    for tool_call in message.tool_calls:  
                        tool_name = tool_call.function.name  
                        tool_args = json.loads(tool_call.function.arguments)  
                        
                        # 执行工具调用  
                        result = self._execute_tool_call(tool_name, tool_args)  
                        
                        # 添加工具响应  
                        tool_results.append({  
                            "tool_call_id": tool_call.id,  
                            "role": "tool",  
                            "name": tool_name,  
                            "content": json.dumps(result)  
                        })  
                    
                    # 如果有工具调用结果，添加到消息中并再次调用API  
                        # .model_dump(): 1. 核心作用 ：
                            # - 将Pydantic模型实例转换为Python字典
                            # - 支持灵活的字段过滤和格式控制
                            # - 保持与Pydantic v2的兼容性
                    if tool_results:  
                        new_messages = messages + [message.model_dump()] + tool_results  
                        # 递归调用，但不再提供工具（防止无限循环）  
                        final_response = self.chat(new_messages, tools=False)  
                        return final_response  
                else:
                    console.log(f"\n[bold yellow]没有触发工具调用[/bold yellow]")
                    
            except Exception as e:
                console.log(f"\n[red]处理工具调用出错: {str(e)}[/red]")
                return {"error": str(e)}
            
            return response.model_dump()  
        
        except Exception as e:  
            console.log(f"[red]智谱API调用流程出错: {str(e)}[/red]")  
            return {"error": str(e)}  