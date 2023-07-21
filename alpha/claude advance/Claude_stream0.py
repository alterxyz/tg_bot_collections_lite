import anthropic
import os
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
with client.messages.stream(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    model="claude-3-5-sonnet-20240620",
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    
    # 获取最终消息，包括使用情况统计
    message = stream.get_final_message()
    print(message.usage)