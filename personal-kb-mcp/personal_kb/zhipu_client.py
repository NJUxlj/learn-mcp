"""  
智谱AI API客户端集成模块。  
该模块提供了与智谱API交互和调用MCP服务器的功能。  
"""  

import json  
import os  
import subprocess  
import tempfile  
from typing import List, Dict, Any, Optional, Union  
import zhipuai  
import requests  
from rich.console import Console  

console = Console()  

class ZhipuClient:  
    """智谱API客户端，用于调用GLM模型并与MCP服务器交互。"""  
    
    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4"):  
        """  
        初始化智谱API客户端。  
        
        Args:  
            api_key: 智谱API密钥  
            model: 要使用的模型名称  
        """  
        # 从环境变量或参数中获取API密钥  
        self.api_key = api_key or os.environ.get("ZHIPU_API_KEY")  
        if not self.api_key:  
            raise ValueError("必须提供ZHIPU_API_KEY环境变量或api_key参数")  
            
        # 初始化智谱客户端  
        self.client = zhipuai.ZhipuAI(api_key=self.api_key)  
        self.model = model  
        
        # MCP服务器进程  
        self.mcp_process = None  
        self.mcp_tools = None  
        
    def start_mcp_server(self) -> None:  
        """启动MCP服务器作为子进程。"""  
        if self.mcp_process is not None:  
            console.log("[yellow]MCP服务器已在运行[/yellow]")  
            return  
            
        # 使用subprocess启动MCP服务器  
        console.log("[green]启动MCP知识库服务器...[/green]")  
        self.mcp_process = subprocess.Popen(  
            ["personalkb", "run"],  
            stdin=subprocess.PIPE,  
            stdout=subprocess.PIPE,  
            stderr=subprocess.PIPE,  
            text=True,  
            bufsize=1  
        )  
        
        # 读取MCP服务器输出直到准备就绪  
        for line in iter(self.mcp_process.stdout.readline, ''):  
            if "Server is ready." in line:  
                console.log("[green]MCP服务器已就绪[/green]")  
                break  
                
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
            },  
            {  
                "name": "get_note",  
                "description": "通过ID获取笔记",  
                "parameters": {  
                    "type": "object",  
                    "properties": {  
                        "note_id": {"type": "integer", "description": "笔记ID"}  
                    },  
                    "required": ["note_id"]  
                }  
            },  
            {  
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
            },  
            {  
                "name": "delete_note",  
                "description": "通过ID删除笔记",  
                "parameters": {  
                    "type": "object",  
                    "properties": {  
                        "note_id": {"type": "integer", "description": "要删除的笔记ID"}  
                    },  
                    "required": ["note_id"]  
                }  
            },  
            {  
                "name": "list_notes",  
                "description": "列出笔记（分页）",  
                "parameters": {  
                    "type": "object",  
                    "properties": {  
                        "limit": {"type": "integer", "description": "要返回的最大笔记数"},  
                        "offset": {"type": "integer", "description": "要跳过的笔记数"}  
                    }  
                }  
            },  
            {  
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
            },  
            {  
                "name": "list_tags",  
                "description": "列出知识库中的所有标签",  
                "parameters": {  
                    "type": "object",  
                    "properties": {}  
                }  
            },  
            {  
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
            },  
            {  
                "name": "get_database_stats",  
                "description": "获取知识库统计信息",  
                "parameters": {  
                    "type": "object",  
                    "properties": {}  
                }  
            }  
        ]  
        
    def _execute_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:  
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
        
        # 创建调用请求  
        request = {  
            "jsonrpc": "2.0",  
            "method": "invoke",  
            "params": {  
                "name": tool_name,  
                "parameters": parameters  
            },  
            "id": 1  
        }  
        
        # 将请求发送到MCP服务器  
        self.mcp_process.stdin.write(json.dumps(request) + "\n")  
        self.mcp_process.stdin.flush()  
        
        # 读取响应  
        response_line = self.mcp_process.stdout.readline()  
        response = json.loads(response_line)  
        
        # 检查错误  
        if "error" in response:  
            return {"error": response["error"]}  
        
        # 返回结果  
        return response.get("result", {})  
    
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
            }  
            
            # 如果启用工具，添加工具参数  
            if tools and self.mcp_tools:  
                kwargs["tools"] = self.mcp_tools  
                kwargs["tool_choice"] = "auto"  
            
            # 调用API  
            response = self.client.chat.completions.create(**kwargs)  
            
            # 处理工具调用  
            message = response.choices[0].message  
            if tools and hasattr(message, 'tool_calls') and message.tool_calls:  
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
                if tool_results:  
                    new_messages = messages + [message.model_dump()] + tool_results  
                    # 递归调用，但不再提供工具（防止无限循环）  
                    final_response = self.chat(new_messages, tools=False)  
                    return final_response  
            
            return response.model_dump()  
        
        except Exception as e:  
            console.log(f"[red]智谱API调用错误: {str(e)}[/red]")  
            return {"error": str(e)}  