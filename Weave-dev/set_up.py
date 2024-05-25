import weave
weave.init("cheese_recommender")

# then use mistralai library as usual
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = MistralClient(api_key=api_key)

messages = [
    ChatMessage(role="user", content="What is the best French cheese?")
]

chat_response = client.chat(
    model=model,
    messages=messages,
)