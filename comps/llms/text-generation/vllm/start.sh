export http_proxy=${your_http_proxy}
export https_proxy=${your_http_proxy}
#export HUGGINGFACEHUB_API_TOKEN=${your_hf_api_token}
export LLM_MODEL_ID=Intel/neural-chat-7b-v3-3
export vLLM_LLM_ENDPOINT="http://10.45.77.191:8008"
export LLM_MODEL=Intel/neural-chat-7b-v3-3
# export no_proxy="localhost,127.0.0.1,intel.com,.intel.com,goto.intel.com,.maas,10.0.0.0/8,172.16.0.0/16,192.168.0.0/16,134.134.0.0/16,.maas-internal,.sv"

docker compose -f docker_compose_llm.yaml up -d
