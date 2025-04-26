# 使用现成的MCP服务器

from mcp import ClientSession, StdioServerParameters  
from mcp.client.stdio import stdio_client  

# 连接到Python执行MCP服务器  
server_params = StdioServerParameters(  
    command='deno',  
    args=['run', '-N', '-R=node_modules', '-W=node_modules',   
          '--node-modules-dir=auto', 'jsr:@pydantic/mcp-run-python', 'stdio']  
)  

async def main():  
    code = """  
    import numpy  
    a = numpy.array([1, 2, 3])  
    print(a)  
    a  
    """  
    
    async with stdio_client(server_params) as client:  
        # 调用run_python工具  
        result = await client.call_tool(  
            "run_python",   
            { "code": code }  
        )  
        print(result)  

import asyncio  
asyncio.run(main())  