# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os

from fastapi.responses import StreamingResponse
from langchain_community.llms import VLLM
from langsmith import traceable

from comps import GeneratedDoc, LLMParamsDoc, ServiceType, opea_microservices, opea_telemetry, register_microservice

@opea_telemetry
def post_process_text(text: str):
    new_text = text.replace("\n", " <br/>")
    return new_text

@register_microservice(
    name="opea_service@llm_vllm",
    service_type=ServiceType.LLM,
    endpoint="/v1/chat/completions",
    host="0.0.0.0",
    port=9000,
)
@opea_telemetry
def llm_generate(input: LLMParamsDoc):
    model = os.getenv("LLM_MODEL_ID", "Intel/neural-chat-7b-v3-3")
    print("use model", model)
    print(input)
    llm = VLLM(
        model=model,
        trust_remote_code=True,  # mandatory for hf models
        max_new_tokens=128,
        top_k=10,
        top_p=0.95,
        temperature=0.8,
    )

    if input.streaming:

        async def stream_generator():
            chat_response = ""
            async for text in llm.astream(input.query):
                chat_response += text
                processed_text = post_process_text(text)
                if text and processed_text:
                    chunk_repr = repr(processed_text.encode("utf-8"))
                    # print(f"[llm - chat_stream] chunk:{chunk_repr}")
                    yield f"data: {chunk_repr}\n\n"
            print(f"[llm - chat_stream] stream response: {chat_response}")
            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_generator(), media_type="text/event-stream")
    else:
        response = llm.invoke(input.query)
        return GeneratedDoc(text=response, prompt=input.query)



if __name__ == "__main__":
    HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", "abc")
    os.system(f"huggingface-cli login --token {HF_TOKEN}")
    opea_microservices["opea_service@llm_vllm"].start()