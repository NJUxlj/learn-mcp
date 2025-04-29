# 安装必要的包  
# pip install mcp  

from mcp import ClientSession, StdioServerParameters  
from mcp.client.stdio import stdio_client  

# 连接到MCP服务器  
server_params = StdioServerParameters(  
    command='python',  
    args=['./server.py']  
)  

async def main():  
    
    try:
        async with asyncio.timeout(5):
            async with stdio_client(server_params) as (read_stream, write_stream):  
                # 创建ClientSession对象
                async with ClientSession(read_stream, write_stream) as client:
                    
                    try:
                        # 验证连接
                        await client.initialize()
                        # 获取可用工具列表  
                        tools = await client.list_tools()
                        print(f"\n\nAvailable tools: \n{tools}\n")
                        
                        while True:
                            print("\n输入操作 (add/subtract/multiply/divide/quit):")
                            operation = input().strip().lower()
                            
                            if operation == 'quit':
                                break
                                
                            if operation in ['add', 'subtract', 'multiply', 'divide']:
                                print("输入第一个数字:")
                                a = int(input())
                                print("输入第二个数字:")
                                b = int(input())  
                                # 调用工具
                                result = await client.call_tool(  
                                    operation,   
                                    { "a": a, "b": b }  
                                )  
                                print(f"结果: {a} + {b} = {result.content[0].text}")  

                            else:
                                print("无效操作，请重试")
                        
                    except asyncio.TimeoutError:
                        print("⏱️ 操作超时，请检查服务器是否响应")
                    except ConnectionError:
                        print("🔌 连接错误，请确保服务器正在运行")
                    except Exception as e:
                        print(f"⚠️ 无法连接到服务器: {str(e)}")
                        return
    except asyncio.TimeoutError:
        print("⏱️ 连接服务器超时，请检查服务器是否启动")
    except Exception as e:
        print(f"⚠️ 初始化错误: {str(e)}")

# 运行客户端  
import asyncio  
asyncio.run(main())  