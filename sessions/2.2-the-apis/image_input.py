"""Session 2.2: image input. The model reads the picture that Sara sent."""
import base64
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
MODEL = os.getenv("MODEL", "gpt-4o-mini")  # the model must accept images

image = Path(__file__).parent / "flight_notice.png"  # an example image made for this course
data = base64.b64encode(image.read_bytes()).decode()

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": [
        {"type": "text", "text": "A customer sent this picture. Which flight is it, "
                                 "what happened, and who cancelled it? Answer in two short sentences."},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{data}"}},
    ]}],
)
print(response.choices[0].message.content)
print("Tokens:", response.usage.prompt_tokens, "in,", response.usage.completion_tokens, "out")
