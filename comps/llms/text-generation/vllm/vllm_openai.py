# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os

from fastapi.responses import StreamingResponse
from langchain_community.llms import VLLMOpenAI
from langsmith import traceable

from comps import GeneratedDoc, LLMParamsDoc, ServiceType, opea_microservices, opea_telemetry, register_microservice

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
@traceable(run_type="llm")
def llm_generate(input: LLMParamsDoc):
    llm_endpoint = os.getenv("vLLM_LLM_ENDPOINT", "http://localhost:8008")
    llm = VLLMOpenAI(
        openai_api_key="EMPTY",
        openai_api_base=llm_endpoint,
        max_tokens=input.max_new_tokens,
        model_name=os.getenv("LLM_MODEL_ID", "meta-llama/Meta-Llama-3-8B-Instruct"),
        top_p=input.top_p,
        temperature=0.9,
        presence_penalty=input.repetition_penalty,
        streaming=input.streaming,
        model_kwargs={"stop": ["<|eot_id|>"]},
    )
    print(input)
    if input.streaming:

        async def stream_generator():
            chat_response = ""
            async for text in llm.astream(input.query):
                # print(f"[llm - chat_stream] text:{text}")
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
    opea_microservices["opea_service@llm_vllm"].start()
