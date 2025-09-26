from openai import OpenAI
import httpx
import os

proxy_url = os.getenv("HTTP_PROXY")

http_client = httpx.Client(proxy=proxy_url, timeout=60.0, verify=True)

client = OpenAI(
    api_key="sk-Df9tniDmqHTzarp1X1W18REuVQFgaf39waPpU8CJ5ibHAQMs",
    base_url="https://apigateway.avangenio.net",
    http_client=http_client,
)

completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "How many days are in a year?"},
    ],
    model="agent-sm",
)

print(completion.choices[0].message.content)
