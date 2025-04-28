# 安装必要的包  
# pip install mcp  

from mcp import ClientSession, StdioServerParameters  
from mcp.client.stdio import stdio_client  

# 连接到MCP服务器  
server_params = StdioServerParameters(  
    command='python',  
    args=['path_to_your_mcp_server.py']  
)  

async def main():  
    async with stdio_client(server_params) as client:  
        # 获取可用工具列表  
        tools = await client.list_tools()  
        print(f"Available tools: {tools}")  
        
        # 调用add工具  
        result = await client.call_tool(  
            "add",   
            { "a": 5, "b": 3 }  
        )  
        print(f"5 + 3 = {result}")  
        
        # 调用multiply工具  
        result = await client.call_tool(  
            "multiply",   
            { "a": 4, "b": 7 }  
        )  
        print(f"4 * 7 = {result}")  

# 运行客户端  
import asyncio  
asyncio.run(main())  