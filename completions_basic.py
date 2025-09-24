from openai import OpenAI
import httpx
import os

# Configure proxy - can be set via environment variable HTTP_PROXY or hardcoded
proxy_url = os.getenv("HTTP_PROXY", "http://osliani.figueiras:Dteam801*@proxy.desoft.cu:3128")

# Create HTTP client with proxy configuration
http_client = httpx.Client(
    proxy=proxy_url,  # Use 'proxy' instead of 'proxies' for newer httpx versions
    timeout=60.0,
    verify=True  # Enable SSL verification
)

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
