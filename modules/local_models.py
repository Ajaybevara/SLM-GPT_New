import asyncio
import base64
import io
import os
import json
import urllib.request
from urllib.parse import urlparse

import numpy as np
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")

# Never send local/LAN model traffic through a system proxy. This is important
# on managed Windows machines where HTTP(S)_PROXY may point at a corporate or
# sandbox proxy that cannot reach private addresses.
for _endpoint in ("VLLM_API_BASE", "EMBED_BASE_URL"):
    _vllm_host = urlparse(os.getenv(_endpoint, "")).hostname
    if not _vllm_host:
        continue
    for _key in ("NO_PROXY", "no_proxy"):
        _hosts = [item.strip() for item in os.getenv(_key, "").split(",") if item.strip()]
        for _host in (_vllm_host, "127.0.0.1", "localhost"):
            if _host not in _hosts:
                _hosts.append(_host)
        os.environ[_key] = ",".join(_hosts)

from litellm import acompletion, completion


def _vllm_settings():
    api_base = os.getenv("VLLM_API_BASE", "http://127.0.0.1:8000/v1").rstrip("/")
    api_key = os.getenv("VLLM_API_KEY", "empty")
    model = os.getenv("VLLM_MODEL", "qwen3-vl-8b")
    return api_base, api_key, model


def models_configured():
    return bool(os.getenv("VLLM_API_BASE") and os.getenv("VLLM_MODEL"))


async def llm_complete(prompt, system_prompt=None, history_messages=None, **kwargs):
    api_base, api_key, model = _vllm_settings()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    response = await acompletion(
        model=f"openai/{model}",
        messages=messages,
        api_base=api_base,
        api_key=api_key,
        timeout=float(os.getenv("VLLM_TIMEOUT_SECONDS", "300")),
        max_retries=2,
    )
    return response.choices[0].message.content


def _image_data_uri(image):
    image = image.convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def vision_complete(prompt, images, temperature=0.1):
    api_base, api_key, model = _vllm_settings()
    content = [{"type": "text", "text": prompt}]
    content.extend(
        {"type": "image_url", "image_url": {"url": _image_data_uri(image)}}
        for image in images
    )
    response = completion(
        model=f"openai/{model}",
        messages=[{"role": "user", "content": content}],
        api_base=api_base,
        api_key=api_key,
        temperature=temperature,
        timeout=float(os.getenv("VLLM_TIMEOUT_SECONDS", "300")),
        max_retries=2,
    )
    return response.choices[0].message.content


async def local_embeddings(texts, is_query=False, **kwargs):
    texts = list(texts)
    dimension = int(os.getenv("EMBED_DIM", "1024"))
    if not texts:
        return np.empty((0, dimension), dtype=np.float32)
    if is_query:
        instruction = os.getenv("EMBED_QUERY_INSTRUCT", "Given a web search query, retrieve relevant passages that answer the query")
        texts = [f"Instruct: {instruction}\nQuery: {text}" for text in texts]

    def encode():
        batches = []
        for start in range(0, len(texts), 32):
            batch = texts[start:start + 32]
            payload = {"model": os.getenv("EMBED_MODEL", "qwen3-embedding-0.6b"), "input": batch, "encoding_format": "float"}
            request = urllib.request.Request(
                os.getenv("EMBED_BASE_URL", "http://192.168.1.100:8701/v1").rstrip("/") + "/embeddings",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": "Bearer " + os.getenv("EMBED_API_KEY", "empty")},
            )
            with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=float(os.getenv("VLLM_TIMEOUT_SECONDS", "300"))) as response:
                data = json.load(response)
            vectors = np.asarray([item["embedding"] for item in sorted(data["data"], key=lambda item: item["index"])], dtype=np.float32)
            if vectors.shape != (len(batch), dimension) or not np.isfinite(vectors).all():
                raise RuntimeError(f"Invalid embedding response: expected ({len(batch)}, {dimension}), got {vectors.shape}")
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            if (norms == 0).any():
                raise RuntimeError("Embedding server returned a zero vector.")
            batches.append(vectors / norms)
        return np.concatenate(batches, axis=0)

    return await asyncio.to_thread(encode)


