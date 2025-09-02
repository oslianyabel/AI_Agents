# pip install --upgrade openai
from openai import OpenAI

client = OpenAI(
    api_key="sk-Df9tniDmqHTzarp1X1W18REuVQFgaf39waPpU8CJ5ibHAQMs",
    base_url="https://apigateway.avangenio.net",
)

completion = client.chat.completions.create(
    messages=[
        { "role": "system", "content": "You are a helpful assistant." },
        { "role": "user", "content": "How many days are in a year?" }
    ],
    model="agent-xs",
)

print(completion.choices[0].message.content)