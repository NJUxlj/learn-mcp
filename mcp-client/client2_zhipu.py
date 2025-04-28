import asyncio
import os
from zhipuai import ZhipuAI
from dotenv import load_dotenv
from contextlib import AsyncExitStack


# 加载 .env 文件，确保 API Key 受到保护
flag = load_dotenv(".env")
if flag:
    print("✅ .env 文件加载成功")
else:
    print("⚠️ 未找到 .env 文件")


class MCPClient:
    def __init__(self):
        """初始化 MCP 客户端"""
        self.exit_stack = AsyncExitStack()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")  # 读取 OpenAI API Key
        self.base_url = os.getenv("BASE_URL")  # 读取 BASE URL
        self.model = os.getenv("MODEL")  # 读取 model
        
        print("self.openai_api_key:", self.openai_api_key)
        print("self.base_url:", self.base_url)
        print("self.model:", self.model)
        
        if not self.openai_api_key:
            raise ValueError("❌ 未找到 OpenAI API Key，请在 .env 文件中设置 OPENAI_API_KEY")
        
        self.client = ZhipuAI(api_key=self.openai_api_key)

    async def process_query(self, query: str) -> str:
        """调用 OpenAI API 处理用户查询
        
        - 使用 async/await 语法实现非阻塞IO操作
        - 通过 asyncio.get_event_loop().run_in_executor 将同步的OpenAI API调用转为异步操作
        - 避免阻塞事件循环，保持聊天交互的流畅性
        """
        messages = [
            {"role": "system", "content": "你是一个智能助手，帮助用户回答问题。"},
            {"role": "user", "content": query}
        ]
        
        try:
            # 调用 OpenAI API
                # run_in_executor 的None参数表示使用默认线程池
                # lambda包装确保API调用在子线程执行
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ 调用 OpenAI API 时出错: {str(e)}"

    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\n🤖 MCP 客户端已启动！输入 'quit' 退出")
        while True:
            try:
                query = input("\n你: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)  # 发送用户输入到 OpenAI API
                print(f"\n🤖 OpenAI: {response}")
            except Exception as e:
                print(f"\n⚠️ 发生错误: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())