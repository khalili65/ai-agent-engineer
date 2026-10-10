"""Session 2.4: which models can my key call? We look for small reasoning models."""
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

names = sorted(model.id for model in client.models.list())
small = [name for name in names if name.startswith("gpt-5") and name.endswith(("-mini", "-nano", "-luna"))]
print(f"{len(names)} models in total. Small GPT-5 models:")
for name in small:
    print(" ", name)
