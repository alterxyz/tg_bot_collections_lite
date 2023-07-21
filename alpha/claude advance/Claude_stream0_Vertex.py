from anthropic import AnthropicVertex

project_id = "gen-lang-client-xxxxxxxx"
# Where the model is running. e.g. us-central1 or europe-west4 for haiku
region = "us-east5"

client = AnthropicVertex(project_id=project_id, region=region)

model_3_5 = "claude-3-5-sonnet@20240620"
model_3="claude-3-opus@20240229"

message = client.messages.create(
    model=model_3_5,
    max_tokens=4000,
    messages=[
        {
            "role": "user",
            "content": "你好 Claude!  你是谁? 你是什么型号和设定的? 你能做什么?",
        }
    ],
)
print(f"{message.content}\n-------------------{message}\n-------------------\n")

with client.messages.stream(
    max_tokens=4000,
    messages=[{"role": "user", "content": "你好哦 Claude! 你是谁? 你是什么型号和设定的? 你能做什么?"}],
    model=model_3,
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    
    # 获取最终消息，包括使用情况统计
    message = stream.get_final_message()
    print(f"\n-------------------{message}")