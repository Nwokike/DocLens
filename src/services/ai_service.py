import base64
import json
import logging

import httpx

from core.constants import API_CHAT_ENDPOINT, GATEWAY_SECRET, USER_AGENT

logger = logging.getLogger(__name__)

_HEADERS = {
    "Authorization": f"Bearer {GATEWAY_SECRET}",
    "User-Agent": USER_AGENT,
    "Content-Type": "application/json",
}


async def analyze_document(image_bytes: bytes, mime_type: str, on_stage=None) -> str:
    def _stage(msg):
        if on_stage:
            on_stage(msg)

    _stage("Optimizing image...")

    b64 = base64.b64encode(image_bytes).decode("utf-8")

    _stage("Uploading to DocLens AI...")

    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are DocLens AI. Extract ALL text from this document image "
                            "verbatim. Include every word, number, and symbol. "
                            "If it's handwritten, transcribe it as accurately as possible. "
                            "Return ONLY the extracted text, no commentary."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                    },
                ],
            }
        ],
        "task_type": "multimodal",
        "temperature": 0.1,
        "max_tokens": 4096,
    }

    _stage("Reading text...")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(API_CHAT_ENDPOINT, headers=_HEADERS, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = _extract_content(data)
            if content:
                logger.info("Extracted %d chars from document", len(content))
                return content
            return "[No text could be extracted from this document.]"
    except Exception as e:
        logger.error("Document analysis failed: %s", e)
        return f"[Analysis failed: {e}]"


async def summarize(text: str, stream_callback=None, on_stage=None) -> str:
    def _stage(msg):
        if on_stage:
            on_stage(msg)

    _stage("Generating summary...")

    payload = {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Summarize the following document text in 3-5 clear bullet points. "
                    "Capture the key facts, numbers, and conclusions. "
                    "Use plain language. Return ONLY the bullet points.\n\n"
                    f"{text}"
                ),
            }
        ],
        "task_type": "text",
        "stream": stream_callback is not None,
        "temperature": 0.3,
        "max_tokens": 2048,
    }

    try:
        if stream_callback:
            return await _stream_chat(payload, stream_callback)

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(API_CHAT_ENDPOINT, headers=_HEADERS, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return _extract_content(data) or "[Summary unavailable]"
    except Exception as e:
        logger.error("Summarization failed: %s", e)
        return f"[Summary failed: {e}]"


async def translate(text: str, target_lang: str, stream_callback=None, on_stage=None) -> str:
    def _stage(msg):
        if on_stage:
            on_stage(msg)

    _stage(f"Translating to {target_lang}...")

    payload = {
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Translate the following text to {target_lang}. "
                    "Preserve the original formatting and structure. "
                    "Return ONLY the translation.\n\n"
                    f"{text}"
                ),
            }
        ],
        "task_type": "text",
        "stream": stream_callback is not None,
        "temperature": 0.3,
        "max_tokens": 4096,
    }

    try:
        if stream_callback:
            return await _stream_chat(payload, stream_callback)

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(API_CHAT_ENDPOINT, headers=_HEADERS, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return _extract_content(data) or "[Translation unavailable]"
    except Exception as e:
        logger.error("Translation failed: %s", e)
        return f"[Translation failed: {e}]"


async def _stream_chat(payload: dict, stream_callback) -> str:
    full = ""
    try:
        async with (
            httpx.AsyncClient(timeout=60.0) as client,
            client.stream("POST", API_CHAT_ENDPOINT, headers=_HEADERS, json=payload) as resp,
        ):
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if content:
                            full += content
                            stream_callback(full)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.error("Stream failed: %s", e)

    if not full:
        full = "[AI response unavailable]"

    return full


def _extract_content(data: dict) -> str:
    try:
        choices = data.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content", "") or ""
            return content.strip()
    except (IndexError, KeyError, TypeError):
        pass
    return ""
