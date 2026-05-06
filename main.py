import argparse
import json

from openai import OpenAI

from settings import settings


PROMPT_STYLES = {
  "concise": "Answer briefly with the most practical points first.",
  "creative": "Answer creatively with vivid examples and one surprising insight.",
  "mentor": "Answer like a supportive mentor with clear next steps.",
}


def build_messages(question: str, style: str) -> list[dict[str, str]]:
  return [
    {"role": "system", "content": PROMPT_STYLES[style]},
    {"role": "user", "content": question},
  ]


def build_request_payload(question: str, style: str) -> dict:
  return {
    "extra_headers": {
      "HTTP-Referer": "<YOUR_SITE_URL>",
      "X-Title": "<YOUR_SITE_NAME>",
    },
    "extra_body": {},
    "model": settings.openrouter_model,
    "messages": build_messages(question, style),
  }


def run(question: str | None = None, style: str = "concise", dry_run: bool = False):
  effective_question = question or settings.default_question
  payload = build_request_payload(effective_question, style)

  if dry_run:
    return payload

  client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
  )
  completion = client.chat.completions.create(**payload)
  return completion.choices[0].message.content


def main() -> None:
  parser = argparse.ArgumentParser(description="Simple AI agent with style presets.")
  parser.add_argument("--question", help="Question to ask the model")
  parser.add_argument(
    "--style",
    choices=sorted(PROMPT_STYLES.keys()),
    default="concise",
    help="Prompt style preset",
  )
  parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Print request payload without calling the model API",
  )
  args = parser.parse_args()

  result = run(question=args.question, style=args.style, dry_run=args.dry_run)
  if args.dry_run:
    print(json.dumps(result, indent=2))
  else:
    print(result)


if __name__ == "__main__":
  main()