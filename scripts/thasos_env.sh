# Source this at the start of every thasos session:   source ~/intexr/scripts/thasos_env.sh
# Sets up vLLM, your API keys, the model cache and the one judge every model in the scale study is scored by.
source ~/vllm-env/bin/activate
[ -f ~/.intexr_keys ] && source ~/.intexr_keys || echo "warning: ~/.intexr_keys not found (Groq/Gemini models will fail)"
export HF_HOME=/tmp/ss4910_hf VLLM_USE_V1=0 JUDGE_LOCAL=Qwen/Qwen3-32B-AWQ
cd ~/intexr
echo "ready: judge=$JUDGE_LOCAL, keys: ${GROQ_API_KEY:+groq }${GEMINI_API_KEY:+gemini }${HF_TOKEN:+hf}"
