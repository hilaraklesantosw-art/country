#!/bin/bash
# AI Tools Screenshot Script
# Run this locally to take screenshots of popular AI tools

OUTPUT_DIR="$(dirname "$0")"
mkdir -p "$OUTPUT_DIR"

tools=(
  "chatgpt:https://chat.openai.com"
  "claude:https://claude.ai"
  "perplexity:https://www.perplexity.ai"
  "copilot:https://copilot.microsoft.com"
  "gemini:https://gemini.google.com"
  "notion:https://www.notion.so"
  "huggingface:https://huggingface.co"
  "stabilityai:https://stability.ai"
  "elevenlabs:https://elevenlabs.io"
  "runway:https://runwayml.com"
  "copyai:https://www.copy.ai"
  "jasper:https://www.jasper.ai"
  "cohere:https://cohere.com"
  "anthropic:https://www.anthropic.com"
  "inflection:https://inflection.ai"
  "ai21:https://ai21.com"
  "midjourney:https://www.midjourney.com"
  "dalle:https://openai.com/dall-e-3"
  "google-ai:https://ai.google"
  "langchain:https://www.langchain.com"
)

for tool in "${tools[@]}"; do
  name="${tool%%:*}"
  url="${tool##*:}"
  echo "Capturing: $name"
  # Use your preferred screenshot method
  # Example with puppeteer or playwright
  echo "$name,$url" >> ai-tools-list.csv
done

echo "Done! Screenshot captured tools saved to $OUTPUT_DIR"
