import os
import json
import time
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = "https://openrouter.ai/api/v1"

if api_key:
    client = OpenAI(api_key=api_key, base_url=base_url)
else:
    client = None

CALL_DELAY = float(os.getenv("LLM_CALL_DELAY", "4"))

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=10, max=60),
    retry=retry_if_exception_type(RateLimitError)
)
def call_llm_with_retry(messages, response_format, temperature):
    model = os.getenv("LLM_MODEL", "google/gemma-4-31b-it:free")

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 512,
        "seed": 42,
    }

    if response_format:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content

    if response_format:
        try:
            return json.loads(content, strict=False)
        except json.JSONDecodeError:
            # Strip markdown code fences if model wraps JSON in them
            clean = content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean, strict=False)

    return content

def call_llm(messages, response_format=None, temperature=0.0):
    if not client:
        print("LLM Error: OPENROUTER_API_KEY is not set.")
        return None

    time.sleep(CALL_DELAY)  # proactive throttle before every call

    try:
        return call_llm_with_retry(messages, response_format, temperature)
    except Exception as e:
        print(f"LLM Error: {e}")
        return None
