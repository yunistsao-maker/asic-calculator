# 第 8 章 效能與成本指標比較

資料基準日：2026-10-04。等級：**A** = 獨立第三方量測；**B** = 廠商 / 夥伴公布且揭露方法；**C** = 廠商宣稱或規格、未揭露方法；**D** = 本文推算（附算式）。

## 效能總表

沒有任何單一 benchmark 同時涵蓋五個家族，同條件的跨硬體比較只有兩組：gpt-oss-120b 在 Artificial Analysis（AA）上，Cerebras 每串流 1,764 t/s，最快的非 ASIC 端點 320 t/s（5.5×）；InferenceX 上 Ironwood 與 B200 / B300 的每晶片 total 吞吐量為 9,364 對 8,903 / 8,925 tok/s（1.05×，20 tok/s/user）。Trainium、Inferentia2 與 LPX 的數字都出自廠商或夥伴自選的模型與負載，只能在列內閱讀。

讀表規則有三條：

- **每使用者速度**是單一串流的 output tok/s（InferenceX 稱 interactivity，即 1 / TPOT）；**系統吞吐量**是每顆晶片每秒的 output tokens，並附上該點的每使用者速度與 TTFT。兩者分表，不互相換算。
- InferenceX 的 total tok/s 含輸入；AgentX 的 total 另含跨輪重複使用的 cached input，total ÷ output 約 130–150（D：19,303 ÷ 136 ≈ 142；定義見 [InferenceX 2026-09-28](https://inferencex.semianalysis.com/blog/sparse-savings-persistent-demand-inside-glm53)）。系統吞吐量一律取 output 欄；固定長度 8K/1K 的 output = total × 1,024 ÷ 9,216。
- AgentX 的 speculative decoding 以固定的 acceptance 曲線計分（pinned）。Kimi K3 的 DSpark 在實際 trace 上量到 1.18–1.68 個 accepted tokens，設定值是 3.84，所以開啟 spec decode 的每使用者速度是上限（[MODELS.md](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/docs/MODELS.md)、[perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)）。

**表 8-1 哪些比較是同條件**

| 比較組 | 相同的條件 | 不同的條件 | 可以比什麼 | 來源 |
|---|---|---|---|---|
| gpt-oss-120b：Cerebras、SambaNova、Groq、GPU 雲、三大雲代管 | 權重、量測者（AA）、10K 輸入的單一請求、P50 / 72 h | 量化（OpenRouter 標記為 fp16、fp4、bf16 不等）、context 上限、reasoning token 量；硬體類別是筆記依廠商資料所標，AA 不揭露硬體 | 每串流 output tok/s、TTFT | [AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers)、[OpenRouter](https://openrouter.ai/openai/gpt-oss-120b) |
| Qwen3.5-397B：Ironwood 對 B200 / B300 | 模型、FP8、8K/1K、aggregated、無 MTP、同一套 harness | 引擎（private beta 的 TorchTPU vLLM 對 GPU 引擎）；每 replica 晶片數未公開 | 每晶片吞吐量、TTFT；成本另套 TCO 模型 | [InferenceX 2026-09-07](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam) |
| AgentX：NVIDIA（H100 至 Vera Rubin）對 AMD（MI300X 至 MI355X） | 模型、trace、harness、KV offload 規則 | 引擎與 image、Hopper 多用 FP8、spec decode 種類 | 每使用者速度、每 GPU output tok/s、TTFT | [MODELS.md](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/docs/MODELS.md) |
| Qwen3.8 27B：Cerebras 對 GPU 主機 | 權重、量測者（OpenRouter 遙測） | 實際流量，prompt 不受控；Cerebras context 65,536，其餘 262,144 以上 | 每串流 tok/s（p50） | [OpenRouter](https://openrouter.ai/qwen/qwen3.8-27b) |
| TPU 的 Google recipes | client 與 InferenceX 同為 `benchmark_serving.py` | Google 自跑；模型不同；多為 1K/1K、concurrency 128 | 只有 Qwen3.5-397B 8K/1K 一列可與 InferenceX 對照量級 | [tpu-recipes](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/ironwood/vLLM) |
| Trainium（AWS 教學、Bedrock、Hugging Face） | 無 | 模型（Llama 3.x、Claude 3.5 Haiku、gpt-oss-120b、Qwen3）、負載、量測者；多為 concurrency 1 | 只能列內閱讀 | [AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/optimizing-ai-responsiveness-a-practical-guide-to-amazon-bedrock-latency-optimized-inference/)、[Optimum Neuron](https://github.com/huggingface/optimum-neuron/tree/main/benchmark/vllm/single-instance) |
| Inferentia2（Hugging Face） | 無 | 只有 Llama 3.1 8B | 只能列內閱讀 | [Optimum Neuron CSV](https://github.com/huggingface/optimum-neuron/blob/main/benchmark/vllm/data-parallel/llama3.1-8b/vllm-results-dp3.csv) |
| LPX | 無 | Gemma 4 31B、100K context、私有端點；精度、concurrency、引擎未揭露 | 無 | [NVIDIA 2026-08-24](https://nvidianews.nvidia.com/news/nvidia-groq-3-lpx-now-in-full-production-with-world-class-speed-for-agentic-ai) |

- 不在本調查範圍、但出現在同一個 benchmark 的 ASIC：InferenceX 首頁與硬體登錄檔列有 OpenAI Jalapeño（登錄值為晶片 700 W、all-in 1.125 kW、TCO 每 chip-hour $1.27），首頁連到 DeepSeek R1、8K/1K、FP4 的結果頁；2026-10-05 的公開 API（`model=DeepSeek-R1-0528`，1,310 列）沒有 Jalapeño 的列，所以本章沒有它的數字。首頁另預告 TPU 8i、SambaNova SN50 與 MI455X（[InferenceX](https://inferencex.semianalysis.com/)；[InferenceX gpu-keys.ts](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/gpu-keys.ts)；[InferenceX API, DeepSeek-R1](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-R1-0528)）。

### 每使用者體驗

Blackwell 級以上的 GPU 在 0.7T–2.8T 旗艦上的單一使用者速度為 216–350 tok/s（8–16 顆 GPU，Vera Rubin 列為 28 顆；spec decode 開啟；TTFT median 0.25–0.85 s）；Hopper 上 DeepSeek-V4-Pro 為 225 tok/s，Kimi K3 需要 32 顆 H200 且只有 5 tok/s。ASIC 端高出一個量級的是 Cerebras（981–1,764 t/s）與 LPX（3,400 t/s，31B 模型、私有端點）；表 8-3 中 TPU、Trainium、Inferentia2 的中位數或單一串流值為 18–144 tok/s。

**表 8-2 每使用者體驗：GPU**（等級 A。AgentX 列取最低 concurrency 點，輸入中位數約 88K–142K tokens；8K/1K 列取每使用者速度最高的點。來源：InferenceX API，2026-10-04 擷取：[Kimi-K3](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Kimi-K3)、[GLM-5.2](https://inferencex.semianalysis.com/api/v1/benchmarks?model=GLM-5.2)、[DeepSeek-V4-Pro](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4-Pro)、[DeepSeek-V4.1-Flash](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4.1-Flash)、[Qwen-3.5-397B-A17B](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Qwen-3.5-397B-A17B)）

| 系統（GPU 數、layout） | 模型、精度 | 負載；concurrency | spec decode | output tok/s 每使用者（median / P90） | TTFT，s（median / P90） | 量測日 |
|---|---|---|---|---|---|---|
| GB300 NVL72（8 GPU，TP8） | Kimi K3，MXFP4 | AgentX；1 | DSpark | 258 / 224 | 0.74 / 1.49 | 2026-09-15 |
| B200（16 GPU，TP8） | Kimi K3，MXFP4 | AgentX；1 | DSpark | 216 / 193 | 0.85 / 1.91 | 2026-10-02 |
| H200（32 GPU，TP16 / EP32） | Kimi K3，MXFP4 | AgentX；1 | DSpark | 5 / 5 | 3.73 / 5.41 | 2026-09-13 |
| GB300 NVL72（8 GPU，TP8） | GLM-5.2，FP4 | AgentX；2 | MTP | 350 / 292 | 0.25 / 0.64 | 2026-10-02 |
| Vera Rubin NVL72（28 GPU，P/D disagg；pre-release TensorRT-LLM） | DeepSeek-V4-Pro，FP4 | AgentX；6 | MTP | 292 / 276 | 0.55 / 1.32 | 2026-09-10 |
| GB200 NVL72（8 GPU，TP8） | DeepSeek-V4-Pro，FP4 | AgentX；1 | DSpark | 312 / 286 | 0.49 / 2.15 | 2026-10-02 |
| H200（8 GPU，TP8） | DeepSeek-V4-Pro，FP8 | AgentX；1 | DSpark | 225 / 187 | 0.92 / 2.75 | 2026-09-16 |
| GB300 NVL72（4 GPU，TP4） | DeepSeek-V4.1-Flash，FP4 | AgentX；1 | MTP | 621 / 599 | 0.17 / 0.27 | 2026-10-02 |
| B200（TP8） | Qwen3.5-397B，FP8 | 8K/1K；1 | 無 | 226（median） | 0.13（median） | 2026-09-18 |
| B300（TP4） | Qwen3.5-397B，FP4 | 8K/1K；4 | MTP | 365（median） | 0.19（median） | 2026-09-10 |
| GB300 NVL72（P/D disagg） | Qwen3.5-397B，FP4 | 8K/1K；12 | MTP | 608（median） | 3.02（median） | 2026-08-27 |
| MI355X（8 GPU，TP8，vLLM） | Kimi K3，MXFP4 | AgentX；1 | DSpark | 172 / 155 | 1.01 / 2.46 | 2026-09-30 |
| MI355X（8 GPU，TP8，SGLang） | GLM-5.2，FP4 | AgentX；1 | MTP | 291 / 273 | 1.03 / 1.86 | 2026-10-03 |
| MI355X（8 GPU，TP8，SGLang） | DeepSeek-V4-Pro，FP4 | AgentX；1 | DSpark | 230 / 216 | 0.80 / 1.45 | 2026-09-29 |
| MI355X（4 GPU，TP4，vLLM） | DeepSeek-V4.1-Flash，FP4 | AgentX；1 | MTP | 380 / 347 | 0.23 / 0.63 | 2026-10-02 |
| MI355X（TP4，SGLang） | Qwen3.5-397B，FP4 | 8K/1K；4 | MTP | 250（median） | 0.22（median） | 2026-09-29 |

- 同模型、同 trace、concurrency 1–2 時，NVIDIA 最佳點 ÷ MI355X（D，取 median）：Kimi K3 258 ÷ 172 = 1.50×；GLM-5.2 350 ÷ 291 = 1.20×；DeepSeek-V4-Pro 312 ÷ 230 = 1.36×；DeepSeek-V4.1-Flash 621 ÷ 380 = 1.63×。
- 一次只服務一個請求的 TileRT 把上限再推高：GLM-5.3 FP8 在 16 顆 MI355X（P/D disagg）上為 485 / 469 tok/s/user、TTFT 2.37 / 4.35 s（A，2026-09-24，[GLM-5.2 API](https://inferencex.semianalysis.com/api/v1/benchmarks?model=GLM-5.2)）；GLM-5.1 FP8 在一台 8× B200 上、8K/1K 為 340 tok/s/user（A，[InferenceX 2026-08-10](https://inferencex.semianalysis.com/blog/ultra-high-interactivity-on-nvidia)）。

**表 8-3 每使用者體驗：TPU、Trainium、Inferentia2、Cerebras、LPX**

| 加速器（系統） | 模型、精度 | 負載；concurrency | spec decode | output tok/s 每串流 | TTFT（s） | 日期；等級 | 來源 |
|---|---|---|---|---|---|---|---|
| Ironwood（晶片數未公開） | Qwen3.5-397B，FP8 | 8K/1K；256 | 無 | 20（InferenceX 的 iso-interactivity 讀數） | mean 5.41 | 2026-09-07；A（preview） | [InferenceX](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam) |
| Ironwood ×4（TP8） | DeepSeek-V3 671B，FP8 KV、FP4 MoE 權重 | 1K/1K；128 | 未載明 | ≈18（TPOT 55.07 ms） | mean 4.94；P99 7.82 | image nightly-20260626；B | [tpu-recipes](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/ironwood/vLLM) |
| Ironwood ×4（SGL-JAX，TP8 / EP8） | GLM-4.5-Air，BF16 | 1,024 / 1,024；128 | 未載明 | ≈35（TPOT 28.84 ms） | mean 3.13 | 2026-10-04 讀取；B | [sglang-jax](https://github.com/sgl-project/sglang-jax/tree/main/docs/cookbook/autoregressive) |
| Trillium ×8（TP8） | Llama-3.3-70B，精度未載明 | 1K/1K；64 | 未載明 | ≈39（TPOT 25.35 ms） | mean 0.25；P99 2.50 | 2026-10-04 讀取；B | [tpu-recipes](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/trillium/vLLM/Llama3.x) |
| Trainium2 ×16（trn2.48xlarge，TP64） | Llama 3.1 405B，FP8 權重 | 10,000 / 1,500；1 | fused spec decode（Llama 3.2 1B draft） | 102.41（BF16、無 spec：25.46） | P50 2.26（2.44） | 教學未載日期，文件 2026-09-30；B | [NxDI 405B](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/tutorials/trn2-llama3.1-405b-speculative-tutorial.html) |
| Trainium2 ×16（TP64） | Llama 3.3 70B，BF16 | 10,000 / 1,500；1 | fused spec decode | 144（無 spec：36） | P50 0.87（0.81） | 教學未載日期；B | [NxDI 70B](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/tutorials/trn2-llama3.3-70b-tutorial.html) |
| Trainium2 ×4（TP16；以 LNC=2 推算晶片數） | gpt-oss-120b，BF16（MXFP4 於載入時還原） | 512 / 128；1 | EAGLE3 | 134.53（無 spec：112.13） | 0.22（0.25） | 2026 年中，Neuron 2.31+；B | [vLLM Neuron](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/tutorials/tutorial-eagle3-speculative-decoding-gpt-oss.html) |
| Trainium2（Bedrock latency-optimized，晶片數未揭露） | Claude 3.5 Haiku | 輸入 100–100,000、輸出 100–1,000；約 1,600 次 API 呼叫 | 未揭露 | P50 85.9、P90 152.0（standard：48.4、67.4） | P50 0.6、P90 1.4（standard：1.1、2.9） | 2025-01-28；B | [AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/optimizing-ai-responsiveness-a-practical-guide-to-amazon-bedrock-latency-optimized-inference/) |
| 同上 | Llama 3.1 70B | 同上 | 未揭露 | P50 137.0、P90 203.7（standard：30.2、32.4） | P50 0.4、P90 1.2（standard：0.9、42.8） | 2025-01-28；B | 同上 |
| Inferentia2 ×12（inf2.48xlarge，3 replicas × TP8） | Llama 3.1 8B，精度未載明 | 1,500 ± 150 / 250 ± 20；單一串流 | 未載明 | 38.8 | 0.33 | 2026-08-27；B | [Optimum Neuron CSV](https://github.com/huggingface/optimum-neuron/blob/main/benchmark/vllm/data-parallel/llama3.1-8b/vllm-results-dp3.csv) |
| Inferentia2 ×12（sequence length 16,512） | Llama 3.1 8B | 約 15,900 / 290；單一串流 | 未載明 | 28.4 | 1.59 | 2025-05-27；B | [AWS Builder Center](https://builder.aws.com/content/2zruvftx03ZtQFFxyur6kdzfwMv/benchmarking-llm-inference-with-optimum-neuron-on-inferentia2) |
| Cerebras Inference（wafer 數未揭露） | gpt-oss-120b（OpenRouter 標記 fp16） | AA 10K 輸入；單一請求 | 未揭露 | 1,764 | 0.42 | 2026-10-04；A | [AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |
| 同上 | 同上 | AA 100K 輸入；單一請求 | 未揭露 | 1,225 | 3.44 | 2026-10-04；A | 同上 |
| 同上 | Qwen3.8 27B（fp16） | OpenRouter 實際流量 | 未揭露 | p50 1,025；p90 1,359 | latency p50 0.17 | 2026-10-04；A | [OpenRouter](https://openrouter.ai/qwen/qwen3.8-27b) |
| Cerebras 私有 enterprise 端點 | Kimi K2.6（1T，32B active） | 10,000 / 500；單一請求 | 未揭露 | 981 | 未公布（E2E 5.6 s） | 2026-05-06；A（端點不公開） | [Cerebras](https://www.cerebras.ai/blog/cerebras-kimi-k2-Enterprise) |
| Groq 3 LPX（256 顆 LP30，一個機櫃當量） | Gemma 4 31B，精度未揭露 | 100,000-token context；concurrency 未揭露 | 未揭露 | 3,400 | 未公布 | 2026-08-21 量測；A / C（AA 量測，經廠商新聞稿轉述） | [NVIDIA](https://nvidianews.nvidia.com/news/nvidia-groq-3-lpx-now-in-full-production-with-world-class-speed-for-agentic-ai)、[StorageReview](https://www.storagereview.com/news/nvidia-groq-3-lpx-enters-full-production-3400-tokens-per-second-at-100k-context-256-lp30s-per-rack) |
| GroqCloud（第一代 LPU） | gpt-oss-120b | AA 10K 輸入；單一請求 | 未揭露 | 473 | 0.74 | 2026-10-04；A | [AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |

- Trainium3 的絕對數字：查無公開資料。AWS 只給相對宣稱（「3x higher throughput per chip … 4x faster response times than Trn2 UltraServers」，GPT-OSS，C，2025-12-02，[About Amazon](https://www.aboutamazon.com/news/aws/trainium-3-ultraserver-faster-ai-training-lower-cost)）。Trainium 不在 InferenceX 的支援硬體清單內（[InferenceX](https://github.com/SemiAnalysisAI/InferenceX)，2026-10-02）。
- TPU 上高於 100 tok/s 的每串流速度只見於 Google 自家端點：AA 量到 Gemini 3.7 Flash（low reasoning）292.7 t/s、time to first answer token 1.41 s，Gemini 2.5 Flash-Lite（non-reasoning）297.2 t/s、0.33 s（A，2026-10-04，[AA](https://artificialanalysis.ai/providers/google)）。Google 稱 Gemini 在 TPU 上服務，世代與服務堆疊未揭露。
- Cerebras 的 1,764 t/s 是 05:46 UTC 的讀數；同日稍早的讀數為 1,781 t/s、TTFT 0.43 s。OpenRouter 實際流量 p50 為 946 t/s（p90 1,748），Cerebras 自述約 3,000 t/s（C，[Cerebras docs](https://inference-docs.cerebras.ai/models/overview)）。

### 系統吞吐量

在 Blackwell 級以上的 GPU 與 MI355X 上，median TTFT 低於 5 s 時的每 GPU output 吞吐量是 Kimi K3 86–136 tok/s、DeepSeek-V4-Pro 449–1,092 tok/s、DeepSeek-V4.1-Flash 999–3,108 tok/s（A）。ASIC 端有對應數字的只有 TPU（Ironwood 在 397B–671B 模型上每晶片 263–1,293 tok/s，B；InferenceX 的同條件點為 1,040 tok/s）與小模型上的 Trainium2、Inferentia2；Cerebras 與 LPX 查無公開的系統吞吐量。

**表 8-4 系統吞吐量：GPU**（等級 A。AgentX 列取 median TTFT < 5 s 的最高吞吐點，沒有合格點時取最高吞吐點；8K/1K 列取每使用者 ≥ 30 tok/s 且 median TTFT ≤ 10 s 的最高吞吐點。來源同表 8-2；MLPerf 列見備註）

| 系統（GPU 數、模式） | 模型、精度 | 負載；concurrency | spec decode | output tok/s 每 GPU | 該點的每使用者 tok/s（median / P90）；TTFT，s（median / P90） | 量測日 |
|---|---|---|---|---|---|---|
| Vera Rubin NVL72（32 GPU，P/D） | DeepSeek-V4-Pro，FP4 | AgentX；934 | MTP | 1,092 | 145 / 138；4.22 / 8.05 | 2026-09-10 |
| GB300 NVL72（12 GPU，P/D，Dynamo vLLM） | DeepSeek-V4-Pro，FP4 | AgentX；256 | MTP | 603 | 61 / 58；4.30 / 9.96 | 2026-08-14 |
| B300（8 GPU） | DeepSeek-V4-Pro，FP4 | AgentX；384 | MTP | 739 | 37 / 34；2.94 / 12.66 | 2026-09-29 |
| GB200 NVL72（28 GPU，P/D） | DeepSeek-V4-Pro，FP4 | AgentX；576 | MTP | 595 | 56 / 52；3.16 / 6.34 | 2026-08-18 |
| B200（8 GPU） | DeepSeek-V4-Pro，FP4 | AgentX；128 | DSpark | 456 | 68 / 58；4.68 / 17.32 | 2026-09-19 |
| MI355X（16 GPU，P/D，MoRI SGLang） | DeepSeek-V4-Pro，FP4 | AgentX；256 | DSpark | 449 | 75 / 63；4.86 / 15.33 | 2026-10-04 |
| H200（8 GPU） | DeepSeek-V4-Pro，FP8 | AgentX；8 | DSpark | 41 | 152 / 97；0.94 / 4.85 | 2026-09-16 |
| GB300 NVL72（8 GPU） | Kimi K3，MXFP4 | AgentX；48 | DSpark | 136 | 38 / 26；1.15 / 2.88 | 2026-09-15 |
| MI355X（8 GPU，ATOM） | Kimi K3，MXFP4 | AgentX；72 | DSpark | 104 | 13 / 10；2.31 / 6.96 | 2026-09-29 |
| B300（8 GPU） | Kimi K3，MXFP4 | AgentX；70 | DSpark | 88 | 11 / 8；1.21 / 3.84 | 2026-08-16 |
| B200（16 GPU） | Kimi K3，MXFP4 | AgentX；72 | DSpark | 86 | 21 / 17；1.01 / 2.62 | 2026-10-02 |
| MI355X（4 GPU，ATOM） | GLM-5.2，FP4 | AgentX；48 | MTP | 230 | 35 / 19；0.81 / 3.87 | 2026-09-22 |
| GB300 NVL72（32 GPU，P/D） | GLM-5.2，FP4 | AgentX；128 | MTP | 149 | 101 / 90；2.33 / 5.81 | 2026-10-02 |
| B200（16 GPU，P/D） | GLM-5.2，FP4 | AgentX；64 | MTP | 132 | 92 / 84；3.88 / 18.23 | 2026-10-02 |
| GB300 NVL72（2 GPU） | DeepSeek-V4.1-Flash，FP4 | AgentX；192 | MTP | 3,108 | 62 / 44；0.24 / 0.73 | 2026-10-02 |
| B300（2 GPU） | DeepSeek-V4.1-Flash，FP4 | AgentX；192 | MTP | 3,059 | 60 / 41；0.25 / 0.81 | 2026-10-02 |
| B200（4 GPU） | DeepSeek-V4.1-Flash，FP4 | AgentX；128 | MTP | 1,362 | 132 / 81；0.16 / 0.44 | 2026-10-03 |
| MI355X（2 GPU，vLLM） | DeepSeek-V4.1-Flash，FP4 | AgentX；64 | MTP | 999 | 59 / 32；0.40 / 3.31 | 2026-10-02 |
| H200（4 GPU） | DeepSeek-V4.1-Flash，FP4 | AgentX；32 | MTP | 231 | 71 / 34；0.40 / 2.73 | 2026-09-21 |
| B200（TP4） | Qwen3.5-397B，FP8 | 8K/1K；128 | 無 | 950（total 8,581） | 31（median）；1.18（median） | 2026-09-18 |
| B300（TP4） | Qwen3.5-397B，FP8 | 8K/1K；64 | 無 | 608（total 5,481） | 39（median）；0.44（median） | 2026-05-21 |
| MI355X（TP4，SGLang） | Qwen3.5-397B，FP8 | 8K/1K；64 | 無 | 535（total 4,823） | 35（median）；0.97（median） | 2026-09-25 |
| MI355X ×512 | DeepSeek-R1 | MLPerf Inference v6.1，Server / Offline | 未載明 | 4,698 / 5,668（D：2,405,310 ÷ 512；2,901,950 ÷ 512） | MLPerf 自訂的延遲條件 | 2026-09-17 |

- GB300 上的 Dynamo SGLang（48 GPU，P/D）在 concurrency 1,920 達每 GPU 846 output tok/s，但 median TTFT 為 9.38 s，不符合 5 s 的條件，所以表中 GB300 列取 Dynamo vLLM 的合格點（明細見表 4-15）。
- MLPerf 列是 AMD 的 submission，經 [AMD ROCm blog](https://rocm.blogs.amd.com/artificial-intelligence/mlperf-inf-v6.1/README.html) 讀取，與 InferenceX 的負載不同，不可互比。NVIDIA 端只有相對值：Vera Rubin 在 Qwen3-VL 上最高為 GB300 NVL72 的 3.7 倍、DeepSeek-R1 上 2.5 倍（[Techstrong.ai](https://techstrong.ai/articles/mlperf-inference-v6-1-updated-for-rag-agents-and-api-based-serving/)，2026-09-16）。
- 按加速器整理的 MLPerf Inference v6.0 / v6.1 成績表：查無公開資料（結果頁未能讀取）。v6.1 新增的加速器清單沒有 TPU（[MLCommons](https://mlcommons.org/2026/09/mlperf-inference-v6-1-results/)），Trainium 的 submission 未查。

**表 8-5 系統吞吐量：TPU、Trainium、Inferentia2**（各列的模型與負載不同，不可跨列比較；Google 與 Hugging Face 的結果都未載明是否使用 spec decode）

| 加速器（晶片數） | 模型、精度 | 負載；concurrency | output tok/s 每晶片 | 該點的服務水準 | 日期；等級 | 來源 |
|---|---|---|---|---|---|---|
| Ironwood（晶片數未公開） | Qwen3.5-397B，FP8，無 MTP | 8K/1K；256 | 1,040（D：total 9,364 ÷ 9） | 20 tok/s/user；mean TTFT 5.41 s | 2026-09-07；A（preview） | [InferenceX](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam) |
| Ironwood ×4 | Qwen3.5-397B-A17B，FP8 | 8K/1K；128 | 570 | 未公布 | image nightly-20260626；B | [tpu-recipes](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/ironwood/vLLM) |
| Ironwood ×4 | Qwen3.5-397B-A17B，FP8 | 1K/8K；128 | 1,293 | 未公布 | 同上；B | 同上 |
| Ironwood ×4 | DeepSeek-V3 671B | 1K/1K；128 | 500 | ≈18 tok/s/user；mean TTFT 4.94 s；mean E2E 61.3 s | 同上；B | 同上 |
| Ironwood ×4 | DeepSeek-R1 671B | 1K/1K；128（512 個請求有 8 個失敗） | 297 | ≈12 tok/s/user；mean TTFT 14.34 s | 同上；B | 同上 |
| Ironwood ×4 | Qwen3-Coder-480B-A35B，FP8 | 8K/1K；64 | 263 | 未公布 | image nightly-20260624；B | 同上 |
| Ironwood ×1 | Qwen3-32B，FP8 | 1K/1K；320 | 7,710 | 未公布 | image nightly-20260914；B | 同上 |
| Ironwood ×4（SGL-JAX） | GLM-4.5-Air，BF16 | 1,024 / 1,024；128 | 1,003 | ≈35 tok/s/user；mean TTFT 3.13 s | 2026-10-04 讀取；B | [sglang-jax](https://github.com/sgl-project/sglang-jax/tree/main/docs/cookbook/autoregressive) |
| Trillium ×8 | Llama-3.3-70B | 1K/1K；128 | 443 | ≈28 tok/s/user；mean TTFT 0.51 s，P99 8.25 s | 2026-10-04 讀取；B | [tpu-recipes](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/trillium/vLLM/Llama3.x) |
| Trainium2 ×1（TP4，batch 32） | Llama 3.1 8B | 1,500 / 250；腳本預設最多 128 個使用者 | 579 | inter-token 44.5 ms（≈22 tok/s/user）；TTFT 1.25 s | 2025-10；B | [Optimum Neuron](https://github.com/huggingface/optimum-neuron/tree/main/benchmark/vllm/single-instance) |
| Trainium2 ×16（TP64，batch 8） | Llama 4 Maverick 17B-128E | 同上 | 5.9（93.6 ÷ 16） | inter-token 56.5 ms；TTFT 3.31 s | 2025-10；B | 同上 |
| Trainium2 ×16（TP64，batch 4） | Qwen3-235B-A22B | 同上 | 1.7（27.9 ÷ 16） | inter-token 69.4 ms；TTFT 5.82 s | 2025-10；B | 同上 |
| Trainium1 ×16（trn1.32xlarge，4 replicas × TP8） | Llama 3.1 8B | 同上 | 109（1,744.9 ÷ 16） | 未載明 | 2026-10-04 讀取；B | [Optimum Neuron DP4](https://github.com/huggingface/optimum-neuron/blob/main/benchmark/vllm/data-parallel/llama3.1-8b/vllm-results-dp4.csv) |
| Inferentia2 ×12（inf2.48xlarge，3 replicas × TP8，batch 32） | Llama 3.1 8B | 1,500 / 250；腳本預設最多 128 個使用者 | 102（1,226.8 ÷ 12） | inter-token 43.2 ms（≈23 tok/s/user）；TTFT 4.47 s | 2026-08-27；B | [Optimum Neuron CSV](https://github.com/huggingface/optimum-neuron/blob/main/benchmark/vllm/data-parallel/llama3.1-8b/vllm-results-dp3.csv) |
| Inferentia2 ×12（sequence 16,512，batch 8） | Llama 3.1 8B | 約 15,900 / 290 | 20.8（249.6 ÷ 12） | mean TTFT 24.6 s；request latency 43.8 s | 2025-05-27；B | [AWS Builder Center](https://builder.aws.com/content/2zruvftx03ZtQFFxyur6kdzfwMv/benchmarking-llm-inference-with-optimum-neuron-on-inferentia2) |

- Trainium 沒有任何 235B 以上模型在高 concurrency 下的吞吐量數字。AWS 的 gpt-oss production recipe（16P1D，decode batch 128 以上）只公布拓樸，沒有結果（[vLLM Neuron](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/tutorials/tutorial-gpt-oss.html)，2026-07-15）；Trainium3：查無公開資料。
- Cerebras：查無公開的系統吞吐量，每條 pipeline 的 concurrency 未揭露。LPX 的 3,400 tok/s 未揭露 concurrency，無法換算成每晶片吞吐量。

### 同條件比較

**表 8-6 gpt-oss-120b（high reasoning）跨供應商**（等級 A；AA，P50 / 72 h，2026-10-04 05:46 UTC；每次量測為單一請求，各端點的精度與是否使用 spec decode 未揭露；硬體類別為筆記所標。來源：[AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers)）

| 供應商 | 硬體類別 | 10K 輸入：t/s | 10K 輸入：TTFT（s） | 100K 輸入：t/s；TTFT（s） | 10 個並行請求（1K）：t/s | 10K 速度 ÷ Azure（D） |
|---|---|---|---|---|---|---|
| Cerebras | wafer-scale ASIC（WSE-3） | 1,764 | 0.42 | 1,225；3.44 | 1,666 | 5.5× |
| SambaNova | RDU ASIC | 706 | 1.14 | 360；6.78 | 740 | 2.2× |
| Groq | LPU ASIC（第一代） | 473 | 0.74 | 476；4.88 | 313 | 1.5× |
| Microsoft Azure | 未揭露 | 320 | 0.74 | 160；4.01 | 562 | 1.0× |
| Nebius（Base） | GPU 雲 | 280 | 0.97 | 189；3.48 | 255 | 0.88× |
| DeepInfra（Turbo） | GPU 雲（NVIDIA 稱 Blackwell） | 248 | 0.81 | 218；2.51 | 294 | 0.78× |
| Crusoe | GPU 雲 | 233 | 0.41 | 208；2.11 | 214 | 0.73× |
| Baseten | GPU 雲（NVIDIA 稱 Blackwell） | 221 | 0.18 | 332；1.25 | 206 | 0.69× |
| Amazon Bedrock | 未揭露 | 83 | 1.08 | 35；3.74 | 135 | 0.26× |
| Google Vertex | 未揭露 | 45 | 95.92 | 86；3.72 | 33 | 0.14× |

- 對十個第三方 GPU 端點的中位數 179 t/s，Cerebras 為 9.9×（D）。100K 輸入時差距縮小：Cerebras 1,225 ÷ 最快的 GPU 端點 Baseten 332 = 3.7×（D）。TTFT 最低的是 GPU 端點（Baseten 0.18 s、Crusoe 0.41 s），不是 ASIC。
- OpenRouter 的實際流量 p50 較低也較接近：Cerebras 946、SambaNova 374、Groq 355、Bedrock 234、Vertex 100 t/s（A，[OpenRouter](https://openrouter.ai/openai/gpt-oss-120b)）。Vertex 端點當日 TTFT 96 s、單日 uptime 51%，不能代表 Google 的硬體。
- 速度與端點品質是兩個軸：AA 的 Endpoint Accuracy Index 上，Cerebras 87.3、Groq 86.4 低於參考端點，SambaNova 98.2、Bedrock 100.8 在參考範圍內（A，[AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers)）。

**表 8-7 Ironwood 對 B200 / B300**（InferenceX Official Preview；Qwen3.5-397B、FP8、8K/1K、aggregated、無 MTP；2026-09-07。來源：[InferenceX](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam)）

| 指標 | 操作點 | Ironwood | B200 | B300 | Ironwood ÷ B200；÷ B300 | 等級 |
|---|---|---|---|---|---|---|
| total tok/s 每晶片 | 20 tok/s/user（concurrency 256） | 9,364 | 8,903 | 8,925 | 1.05×；1.05× | A |
| output tok/s 每晶片 | 同上 | 1,040 | 989 | 992 | 1.05×；1.05× | D（total ÷ 9） |
| mean TTFT（s） | concurrency 256 | 5.41 | 3.75 | 2.40 | 1.44×；2.25× | A |
| total tok/s 每晶片 | 100 tok/s/user | 1,857 | 2,165 | 2,275 | 0.86×；0.82× | D（由成本反推，見備註） |
| 每百萬 total tokens 成本 | 100 tok/s/user | $0.181 | $0.222 | $0.276 | 0.82×；0.66× | 吞吐量 A；成本為 TCO 模型 |
| 每百萬 total tokens 成本 | median E2E 20 s | ≈$0.098 | $0.106 | $0.132 | 0.92×；0.74× | 同上 |

- 100 tok/s/user 的吞吐量是本文由文章的成本反推：吞吐量 = TCO ÷（成本 × 3,600）× 10^6，TCO 取 InferenceX 的自有成本 $1.21、$1.73、$2.26 每 chip-hour。同一組 TCO 可重現文章的「+50.4%、+96.0% tokens per dollar」（(9,364 ÷ 1.21) ÷ (8,903 ÷ 1.73) = 1.504），所以判定文章的 external TCO 即這組數值（D）。
- SemiAnalysis 的結論是「Across most of the raw-performance curve, TPU does not outperform NVIDIA GPUs」。Ironwood 沒有原生 FP4，對 GPU 的 FP4 落後；對 GB300 NVL72 的 disaggregated serving，在延遲中段約落後 30% perf per dollar。AgentX 上的 TPU 結果尚未公布。
- 這是 2026-09-07 的快照。[InferenceX API](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Qwen-3.5-397B-A17B) 中 2026-09-18 的 B200 FP8 重跑為 31 tok/s/user 時 total 8,581、9 tok/s/user 時 12,951 tok/s/GPU，線性內插到 20 tok/s/user 約 10,800（D），高於文章當時的 8,903。

**表 8-8 gpt-oss-120b：同一份權重、不同量測**（負載不同，只能比量級。InferenceX 列取自 [InferenceX API，gpt-oss-120b](https://inferencex.semianalysis.com/api/v1/benchmarks?model=gpt-oss-120b)，2026-10-05 重抓後四列逐一相符，等級 A）

| 平台 | 設定（精度、晶片、spec decode） | 負載；concurrency | output tok/s 每串流 | TTFT（s） | 量測者；日期；等級 |
|---|---|---|---|---|---|
| Cerebras（API） | fp16 標記 | 10K 輸入；單一請求 | 1,764 | 0.42 | AA；2026-10-04；A |
| SambaNova / Groq（API） | 未揭露 | 同上 | 706 / 473 | 1.14 / 0.74 | AA；2026-10-04；A |
| GB200 NVL72（自架） | FP4；P TP1 + D TP4；Dynamo + TensorRT-LLM；無 spec decode | 1K/1K；1 | 527 | 0.04 | InferenceX；2026-01-07；A |
| B200（自架） | FP4；8 GPU，TP8；TensorRT-LLM；無 spec decode | 1K/1K；4 | 431 | 0.05 | InferenceX；2026-05-18；A |
| MI355X（自架） | FP4；4 GPU，TP4；vLLM；無 spec decode | 1K/1K；4 | 318 | 0.03 | InferenceX；2026-06-05；A |
| H200（自架） | FP4；8 GPU，TP8；vLLM；無 spec decode | 1K/1K；4 | 270 | 0.03 | InferenceX；2026-05-30；A |
| GPU 雲 API | 各家不一 | 10K 輸入；單一請求 | 中位數 179；最快 280（Nebius） | 0.97（Nebius） | AA；2026-10-04；A |
| Trainium2（自架） | BF16；TP16（4 顆晶片）；EAGLE3 | 512 / 128；1 | 134.53（無 spec：112.13） | 0.22（0.25） | AWS；2026 年中；B |
| Amazon Bedrock（硬體未揭露） | 未揭露 | 10K 輸入；OpenRouter p50 | 83；234 | 1.08；latency 0.55 | AA、OpenRouter；2026-10-04；A |

- TPU：Google 的 GPT-OSS recipe 只有方法，結果欄是佔位值，查無公開資料（[tpu-recipes](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/ironwood/vLLM)）。Inferentia2：gpt-oss 只支援 Trn2 / Trn3（[vLLM Neuron README](https://github.com/vllm-project/vllm-neuron/blob/release-0.24.0.1.1.0/README.md)）。
- 其他同權重比較（D）：Qwen3.8 27B 在 OpenRouter 上 Cerebras p50 1,025 t/s，次快端點 113 t/s（9.1×），17 個端點中位數 68 t/s（15×）。Kimi K2.6 的 Cerebras 私有端點 981 t/s（2026-05-06）對 2026-10-04 最快的公開 GPU 端點 Nebius 264 t/s 為 3.7×，同日另一次讀數為 250 t/s（3.9×），Cerebras 與 GPU 兩端非同時量測（[AA](https://artificialanalysis.ai/models/kimi-k2-6/providers)）。
- GPU 世代之間：GB300 對 GB200（DeepSeek-V4-Pro FP4、8K/1K、P/D disagg、無 spec decode，2026-05-22 執行）在相同 interactivity 下，每 GPU total tok/s 為 1.20×（16 tok/s/user）至 2.83×（27 tok/s/user）（A，[InferenceX 2026-05-27](https://inferencex.semianalysis.com/blog/gb300-nvl72-vs-gb200-nvl72-dsv4-pro-vllm-fp4)）。

## 成本與能效

在唯一同條件的操作點（Qwen3.5-397B FP8、8K/1K、20 tok/s/user）上，以牌價換算的每百萬 output tokens 成本是 Ironwood 3 年承諾 $1.44、on-demand $3.20，B200 為 $1.88（Lambda on-demand）至 $4.00（AWS on-demand）（D）。換成 SemiAnalysis 的自有 TCO 才是 $0.32 對 $0.49；Trainium2 每 chip-hour $2.235 是同頁 B200 的 18%，但沒有任何量測能把它換成每 token 成本，Cerebras 與 LPX 不以 chip-hour 販售。

### 每 chip-hour 的價格

**表 8-9 每 chip-hour 牌價與購買方式**（供應商自己的價目頁或價目 API，2026-10-04 讀取。牌價的等級依各筆記原標：GPU 為 B，Trainium 為 C，TPU 與 Inferentia2 的價目表未另標等級。分析師估計另行標明）

| 平台 | 晶片（執行個體） | 購買方式 | 每 chip-hour（USD） | Region 與備註 | 來源 |
|---|---|---|---|---|---|
| AWS | Trainium2（trn2.48xlarge 16 顆；trn2.3xlarge 1 顆） | 只有 Capacity Blocks for ML；無 on-demand | 2.235（$35.7608 ÷ 16） | trn2.48xlarge：Ohio、Hyderabad；trn2.3xlarge：Hyderabad、Melbourne、São Paulo | [AWS Capacity Blocks](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| AWS | Trainium1（trn1.32xlarge，16 顆） | on-demand；Capacity Blocks | 1.344（$21.50 ÷ 16）；0.596 | on-demand 只在 N. Virginia、Ohio、Oregon | [AWS 價目表](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28Ohio%29/Linux/index.json)、[AWS Capacity Blocks](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| AWS | Trainium3（Trn3 UltraServer） | 無公開價格、無 Capacity Blocks 列、無 Region 清單 | 查無公開資料 | 2025-12-02 宣布 GA | [AWS Trn3](https://aws.amazon.com/ec2/instance-types/trn3/) |
| AWS | Inferentia2（inf2.xlarge 1 顆；inf2.48xlarge 12 顆） | on-demand | 0.758；1.082（$12.9813 ÷ 12） | us-east-1；Tokyo 為 1.137 與 1.623（$19.4719 ÷ 12）；價目表 2026-09-25 | [AWS 價目表](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json)、[AWS price list (Tokyo)](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/Asia%20Pacific%20%28Tokyo%29/Linux/index.json) |
| Google Cloud | Ironwood（TPU7x） | on-demand / DWS Flex-start / 1 年 / 3 年承諾 | 12.00 / 6.00 / 8.40 / 5.40 | us-central1；europe-west2 on-demand 13.20；TPU 8i、8t 無價格 | [Cloud TPU pricing](https://cloud.google.com/tpu/pricing) |
| Google Cloud | Trillium（v6e） | 同上 | 2.70 / 1.35 / 1.89 / 1.22 | us-east1、us-east5；Tokyo on-demand 3.24 | 同上 |
| Google（分析師估計） | Ironwood | Google 內部 TCO；Anthropic 向 GCP 取得的成本 | 1.03；1.60 | SemiAnalysis 模型，非牌價 | [InferenceX](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam)、[SemiAnalysis](https://newsletter.semianalysis.com/p/tpuv7-google-takes-a-swing-at-the) |
| AWS | H200（p5en.48xlarge） | on-demand；Capacity Blocks | 7.91；6.865（2026-10-07 起 7.895） | Capacity Blocks 為美國 Region 價 | [Vantage](https://instances.vantage.sh/aws/ec2/p5en.48xlarge)、[AWS Capacity Blocks](https://aws.amazon.com/ec2/capacityblocks/pricing) |
| AWS | B200（p6-b200.48xlarge） | on-demand；Capacity Blocks | 14.24；12.355（2026-10-07 起 14.208） | Spot 6.44 | [Vantage](https://instances.vantage.sh/aws/ec2/p6-b200.48xlarge)、[AWS Capacity Blocks](https://aws.amazon.com/ec2/capacityblocks/pricing) |
| AWS | B300（p6-b300.48xlarge） | on-demand；Capacity Blocks | 17.80（二手來源）；14.04（2026-10-07 起 16.146） | on-demand 價出自第三方部落格 | [Thunder Compute](https://www.thundercompute.com/blog/ec2-gpu-instances)、[AWS Capacity Blocks](https://aws.amazon.com/ec2/capacityblocks/pricing) |
| AWS | GB200（P6e-GB200 UltraServer） | 只有 Capacity Blocks | 10.582 | Dallas Local Zone | [AWS Capacity Blocks](https://aws.amazon.com/ec2/capacityblocks/pricing) |
| Google Cloud | B200（a4-highgpu-8g） | 無 on-demand；1 年 / 3 年 CUD；Spot | 11.12 / 7.09；4.95 | GB200、GB300 機型不在公開價目頁 | [Google Cloud](https://cloud.google.com/products/compute/pricing/accelerator-optimized) |
| Oracle（OCI） | H200 / B200 / B300 / GB200 / GB300 | on-demand | 10.00 / 14.00 / 15.00 / 16.00 / 18.00 | 價目 API 2026-10-01 更新；無 Rubin 項目 | [Oracle](https://www.oracle.com/cloud/compute/pricing/) |
| CoreWeave | H200 / B200 / GB200 | on-demand；承諾用量「up to 60%」折扣 | 6.31 / 8.60 / 10.50 | GB300、B300 為 contact sales；Vera Rubin 自 2026-09-30 limited availability，無公開價格 | [CoreWeave](https://www.coreweave.com/pricing)、[CoreWeave 2026-09-30](https://www.coreweave.com/blog/cognition-becomes-first-customer-for-nvidia-vera-rubin-nvl72-on-coreweave-cloud) |
| Lambda；Nebius | B200；H200 / B200 / B300 | on-demand | 6.69；4.50 / 7.15 / 7.85 | Nebius 另有一份「effective October 1, 2026」價目（5.40 / 8.50 / 9.50），適用範圍不明 | [Lambda](https://lambda.ai/pricing)、[Nebius](https://nebius.com/prices) |
| Azure | GB200（Standard_ND128isr_NDR_GB200_v6） | on-demand | 每 VM-hour 108.16 | 每 VM 的 GPU 數未確認，無法換算每 GPU | [Azure 價目 API](https://prices.azure.com/api/retail/prices?$filter=contains%28armSkuName,%27GB200%27%29) |
| Oracle（OCI） | AMD MI300X / MI355X | on-demand | 6.00 / 8.60 | Helios、MI455X 沒有任何雲端 SKU 或價格 | [Oracle](https://www.oracle.com/cloud/compute/pricing/)、[Moor Insights](https://moorinsightsstrategy.com/field-notes/amd-advancing-ai-2026-helios-ships-venice-swings-and-the-software-moat-narrows/) |
| Cerebras | WSE-3（CS-3）、WSE-3T（CS-4） | 不以 chip-hour 販售；公開 API 按 token 計價 | 查無公開資料 | gpt-oss-120b 每百萬 input / output $0.35 / $0.75；Dedicated 價格未公布；CS-3 每機櫃 BoM 約 $450k（分析師估計） | [OpenRouter](https://openrouter.ai/api/v1/models/openai/gpt-oss-120b/endpoints)、[SemiAnalysis](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) |
| NVIDIA | Groq 3 LPX | 無公開 SKU | 查無公開資料 | 報導的目標價為 premium token「$45 per million tokens」（C） | [Tom's Hardware](https://www.tomshardware.com/tech-industry/semiconductors/nvidias-20-billion-groq-deal-produces-its-first-chip) |

- 價格方向是上漲：AWS 於 2026-07-01 把 GPU 的 Capacity Blocks 調漲約 20%，2026-10-07 再把 P6-B300、P6-B200、P5en、P5e、P5 各調漲約 15%（D：16.146 ÷ 14.04；14.208 ÷ 12.355；7.895 ÷ 6.865；6.866 ÷ 5.97；5.970 ÷ 5.191），同一公告另列 P4de $2.546 與 P4d $1.696；Trainium 的 Capacity Blocks 價格不變（[Yahoo Finance](https://ca.finance.yahoo.com/news/aws-raising-gpu-instance-prices-134610388.html)、[AWS Capacity Blocks](https://aws.amazon.com/ec2/capacityblocks/pricing/)）。
- 同一顆 B200 的 on-demand 價，AWS 與 OCI（$14.00–14.24）是 CoreWeave、Nebius、Lambda（$6.69–8.60）的 1.6–2.1 倍（D）。

### 推算：每百萬 output tokens

```latex
C_{\mathrm{out}} = \frac{P}{R_{\mathrm{out}} \times 3600} \times 10^{6}
```

P 是每 chip-hour 的價格（USD），R_out 是每顆晶片每秒的 output tokens；全部成本都攤給 output tokens，所以輸入越重的負載 C_out 越高。以下皆為等級 D，假設晶片在計費時間內全程維持該吞吐量。

**表 8-10 同條件組：Qwen3.5-397B FP8、8K/1K、20 tok/s/user**（aggregated、無 MTP、concurrency 256；R_out：Ironwood 1,040、B200 989、B300 992 tok/s 每晶片，取自表 8-7；每百萬 total tokens 以 total 吞吐量 9,364、8,903、8,925 計）

| 晶片 | 價格來源（購買方式） | P（$ / chip-hour） | 每百萬 output tokens | 每百萬 total tokens |
|---|---|---|---|---|
| Ironwood | Google on-demand | 12.00 | $3.20 | $0.356 |
| Ironwood | Google 1 年承諾 | 8.40 | $2.24 | $0.249 |
| Ironwood | Google DWS Flex-start | 6.00 | $1.60 | $0.178 |
| Ironwood | Google 3 年承諾 | 5.40 | $1.44 | $0.160 |
| Ironwood | SemiAnalysis 估計的 Anthropic 取得成本 | 1.60 | $0.427 | $0.047 |
| Ironwood | InferenceX 自有 TCO | 1.21 | $0.323 | $0.036 |
| Ironwood | SemiAnalysis 估計的 Google 內部 TCO | 1.03 | $0.275 | $0.031 |
| B200 | AWS on-demand | 14.24 | $4.00 | $0.444 |
| B200 | OCI on-demand | 14.00 | $3.93 | $0.437 |
| B200 | AWS Capacity Blocks（2026-10-07 起 14.208） | 12.355 | $3.47（$3.99） | $0.385（$0.443） |
| B200 | Google 1 年 CUD | 11.12 | $3.12 | $0.347 |
| B200 | CoreWeave on-demand | 8.60 | $2.41 | $0.268 |
| B200 | Nebius on-demand | 7.15 | $2.01 | $0.223 |
| B200 | Google 3 年 CUD | 7.09 | $1.99 | $0.221 |
| B200 | Lambda on-demand | 6.69 | $1.88 | $0.209 |
| B200 | InferenceX 自有 TCO | 1.73 | $0.486 | $0.054 |
| B300 | AWS on-demand（二手來源） | 17.80 | $4.99 | $0.554 |
| B300 | OCI on-demand | 15.00 | $4.20 | $0.467 |
| B300 | AWS Capacity Blocks（2026-10-07 起 16.146） | 14.04 | $3.93（$4.52） | $0.437（$0.503） |
| B300 | Nebius on-demand | 7.85 | $2.20 | $0.244 |
| B300 | InferenceX 自有 TCO | 2.26 | $0.633 | $0.070 |

- 這一組可比：模型、精度、負載、harness 與每使用者速度都相同，三者的吞吐量只差 5%，成本差距幾乎全部來自 P。同一購買方式下，Google 的 3 年承諾價 Ironwood $1.44 對 B200 $1.99（低 28%）；on-demand 則是 Ironwood $3.20 對 neocloud 的 B200 $1.88–2.41。
- 限制有三：Ironwood 該點的 mean TTFT 是 5.41 s，B200 為 3.75 s；GPU 一旦改用 FP4、MTP 與 disaggregated serving，吞吐量遠高於此組（表 8-14）；B200 在 2026-09-18 的重跑於 31 tok/s/user 時為 950 output tok/s 每 GPU，Lambda on-demand 換算 $1.96。

**表 8-11 GPU：AgentX 高吞吐點與其他量測**（R_out 取自表 8-4；NVIDIA 與 AMD 各列用同一套 harness，可互比。AgentX 每個 output token 伴隨約 130–150 個 input 與 cached tokens，所以 C_out 不可與表 8-10、表 8-12 比較）

| 加速器 | 模型；concurrency | R_out（output tok/s 每 GPU） | P（$ / GPU-hour，來源） | 每百萬 output tokens |
|---|---|---|---|---|
| GB300 NVL72 | Kimi K3；48 | 136 | 18.00（OCI） | $36.76 |
| B200 | Kimi K3；72 | 86 | 6.69（Lambda）；8.60（CoreWeave）；12.355（AWS Capacity Blocks） | $21.61；$27.78；$39.91 |
| MI355X | Kimi K3；72 | 104 | 8.60（OCI） | $22.97 |
| GB300 NVL72 | GLM-5.2；128 | 149 | 18.00（OCI） | $33.56 |
| B200 | GLM-5.2；64 | 132 | 6.69；8.60；12.355 | $14.08；$18.10；$26.00 |
| MI355X | GLM-5.2；48 | 230 | 8.60（OCI） | $10.39 |
| GB300 NVL72 | DeepSeek-V4-Pro；256 | 603 | 18.00（OCI） | $8.29 |
| GB200 NVL72 | DeepSeek-V4-Pro；576 | 595 | 10.50（CoreWeave）；10.582（AWS Capacity Blocks）；16.00（OCI） | $4.90；$4.94；$7.47 |
| B300 | DeepSeek-V4-Pro；384 | 739 | 7.85（Nebius）；14.04（AWS Capacity Blocks） | $2.95；$5.28 |
| B200 | DeepSeek-V4-Pro；128 | 456 | 6.69；8.60；12.355 | $4.08；$5.24；$7.53 |
| MI355X | DeepSeek-V4-Pro；256 | 449 | 8.60（OCI） | $5.32 |
| H200 | DeepSeek-V4-Pro（FP8）；8 | 41 | 4.50（Nebius）；6.31（CoreWeave）；6.865（AWS Capacity Blocks） | $30.49；$42.75；$46.51 |
| GB300 NVL72 | DeepSeek-V4.1-Flash；192 | 3,108 | 18.00（OCI） | $1.61 |
| B300 | DeepSeek-V4.1-Flash；192 | 3,059 | 7.85（Nebius）；14.04（AWS Capacity Blocks） | $0.71；$1.27 |
| B200 | DeepSeek-V4.1-Flash；128 | 1,362 | 6.69；8.60；12.355 | $1.36；$1.75；$2.52 |
| MI355X | DeepSeek-V4.1-Flash；64 | 999 | 8.60（OCI） | $2.39 |
| MI355X ×512 | DeepSeek-R1；MLPerf v6.1 Server | 4,698 | 8.60（OCI） | $0.51 |
| B200 | gpt-oss-120b（FP4，1K/1K，無 spec decode）；256 | 14,725 | 6.69（Lambda）；12.355（AWS Capacity Blocks） | $0.13；$0.23 |

- Vera Rubin NVL72 沒有公開價格，無法推算。gpt-oss-120b 列的吞吐量來自 [InferenceX API，gpt-oss-120b](https://inferencex.semianalysis.com/api/v1/benchmarks?model=gpt-oss-120b)（run 412112：TensorRT-LLM，59 tok/s/user、TTFT 0.07 s，2026-05-18），可對照代管 API 的 output 牌價 $0.17–0.75。
- 同一模型內，C_out 的排序由價格決定的程度不亞於硬體：DeepSeek-V4.1-Flash 在 B300 上的 R_out 與 GB300 幾乎相同（3,059 對 3,108），但 Nebius 的 B300 每 GPU-hour 比 OCI 的 GB300 便宜 56%。

**表 8-12 廠商 recipe：TPU、Trainium、Inferentia2**（R_out 取自表 8-5 與表 8-3。各列的模型、負載與 concurrency 都不同，彼此不可比，也不可與 GPU 列比；Trainium2 的單一串流列是功能示範，不是量產經濟性）

| 加速器 | 模型；負載；concurrency | R_out（output tok/s 每晶片） | P（$ / chip-hour） | 每百萬 output tokens |
|---|---|---|---|---|
| Ironwood | Qwen3.5-397B FP8；8K/1K；128 | 570.2 | 12.00 on-demand；5.40 3 年承諾 | $5.85；$2.63 |
| Ironwood | Qwen3.5-397B FP8；1K/8K；128 | 1,293.0 | 同上 | $2.58；$1.16 |
| Ironwood | DeepSeek-V3；1K/1K；128 | 499.9 | 同上 | $6.67；$3.00 |
| Ironwood | Qwen3-Coder-480B；8K/1K；64 | 263.3 | 同上 | $12.66；$5.70 |
| Ironwood | GLM-4.5-Air（SGL-JAX）；1K/1K；128 | 1,003.4 | 同上 | $3.32；$1.49 |
| Ironwood | Qwen3-32B；1K/1K；320 | 7,709.6 | 同上 | $0.43；$0.19 |
| Trillium | Llama-3.3-70B；1K/1K；128 | 443.1 | 2.70 on-demand；1.22 3 年承諾 | $1.69；$0.76 |
| Trainium2 | Llama 3.1 8B；1,500 / 250；batch 32 | 578.8 | 2.235（Capacity Blocks） | $1.07 |
| Trainium2 | gpt-oss-120b；512 / 128；1；EAGLE3 | 33.6（134.53 ÷ 4） | 同上 | $18.46 |
| Trainium2 | Llama 3.3 70B；10,000 / 1,500；1；spec decode | 9.0（144 ÷ 16） | 同上 | $68.98 |
| Trainium2 | Llama 3.1 405B FP8；10,000 / 1,500；1；spec decode | 6.4（102.41 ÷ 16） | 同上 | $97.00 |
| Trainium2 | Qwen3-235B-A22B；1,500 / 250；batch 4 | 1.74（27.9 ÷ 16） | 同上 | $356 |
| Trainium1 | Llama 3.1 8B；1,500 / 250；4 replicas | 109.1（1,744.9 ÷ 16） | 1.344 on-demand；0.596 Capacity Blocks | $3.42；$1.52 |
| Inferentia2 | Llama 3.1 8B；1,500 / 250；batch 32 × 3 | 102.2（1,226.8 ÷ 12） | 1.082 us-east-1；1.623 Tokyo | $2.94；$4.41 |
| Inferentia2 | Llama 3.1 8B；約 15,900 / 290；batch 8 × 3 | 20.8（249.6 ÷ 12） | 1.082 us-east-1 | $14.45 |

- Bedrock 曾以每百萬 output tokens $5 販售 Trainium2 上的 latency-optimized Claude 3.5 Haiku，遠低於上表 Trainium2 大模型列的 $18–356，可見 AWS 內部服務堆疊的 batch 遠高於公開教學（[Anthropic](https://claude.com/blog/trainium2-and-distillation)）。
- Cerebras 與 LPX 沒有 chip-hour 價格，也沒有公開的系統吞吐量，C_out 無法計算；InferenceX 的 TCO 表也沒有 Trainium、Inferentia、Cerebras 與 LPX。

### InferenceX 的模型化成本與每 MW token

InferenceX 的成本 = 自有 TCO ÷（每晶片 tok/s × 3,600）× 10^6，每 MW token = 每晶片 tok/s ÷ all-in kW × 1,000；兩個輸入都是 SemiAnalysis 的模型值，不是量測。本文以計算器輸出驗算，兩式逐列吻合（例：Vera Rubin 195,949 total tok/s 每 GPU → $0.0051、59.4M tok/s per MW；output 成本欄因顯示的 output 速率取整數，第二位小數會有出入）。

**表 8-13 InferenceX 的 TCO 與功耗假設**（等級 B。InferenceX-app 儲存庫的 [gpu-keys.ts](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/gpu-keys.ts)（2026-10-05 重讀，11 列數值全部相符）；同目錄的 [tco.ts](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/tco.ts) 註明出處為「SemiAnalysis Market July 2026 Pricing Surveys & AI Cloud TCO Model」）

| 加速器 | TDP（W） | all-in 功耗（kW / 晶片） | 自有 TCO（$ / chip-hour） | 3 年租用（$ / chip-hour） |
|---|---|---|---|---|
| Vera Rubin NVL72 | 1,800 | 3.30 | 3.61 | 8.50 |
| GB300 NVL72 | 1,400 | 2.12 | 2.31 | 5.00 |
| GB200 NVL72 | 1,200 | 1.87 | 1.86 | 4.00 |
| B300 | 1,200 | 1.90 | 2.26 | 4.25 |
| B200 | 1,000 | 1.71 | 1.73 | 3.70 |
| H200 | 700 | 1.37 | 1.22 | 2.90 |
| H100 | 700 | 1.37 | 1.17 | 2.00 |
| MI355X | 1,400 | 2.09 | 1.50 | 2.90 |
| MI325X | 1,000 | 1.69 | 1.10 | 1.60 |
| MI300X | 750 | 1.39 | 0.95 | 1.30 |
| TPU7x Ironwood | 980 | 1.207 | 1.21 | 2.00 |

- 自有 TCO 是以 hyperscaler 的採購與融資條件，把伺服器與網路的資本支出、colocation、電力與資金成本攤入每 GPU-hour；3 年租用是 SemiAnalysis 租金調查的 3 年承諾市價（[InferenceX 2026-09-14](https://inferencex.semianalysis.com/blog/vera-rubin-nvl72-agentic-inference)）。all-in 功耗在檔內定義為晶片加上主機與 NIC 的每 GPU 分攤。
- 各篇文章用的 TCO 不一致：2026-05-27 的文章用 GB200 $2.21、GB300 $2.65，2026-09-28 的文章與儲存庫是 $1.86、$2.31（[InferenceX 2026-05-27](https://inferencex.semianalysis.com/blog/gb300-nvl72-vs-gb200-nvl72-dsv4-pro-vllm-fp4)、[InferenceX 2026-09-28](https://inferencex.semianalysis.com/blog/sparse-savings-persistent-demand-inside-glm53)）。Ironwood 在儲存庫的 3 年租用值 $2.00 遠低於 Google 的 3 年承諾牌價 $5.40，內部 TCO 在文章中是 $1.03、儲存庫是 $1.21。

**表 8-14 InferenceX 模型化結果：AgentX、P90 interactivity 100 tok/s/user**（吞吐量 A；成本與每 MW 為模型值。每個硬體取 total 吞吐量最高的引擎；concurrency 是內插點；各列都開啟 spec decode（MTP 或 DSpark，pinned acceptance）。前六個數值欄是 InferenceX 計算器的輸出，自有 TCO，本文於 2026-10-02 與 2026-10-03 讀取，該頁沒有可連結的固定網址。最後一欄是查核：本文以公開 API（2026-10-05 重抓）重算同一操作點，做法是對每組「硬體 × 引擎 × 精度」取 Pareto frontier，再在 P90 interactivity = 100 的兩側量測點之間線性內插，等級 D；括號為相對計算器讀數的差異。22 列中 15 列在 ±2.5% 內、20 列在 ±7% 內；差異最大的兩列，兩側量測點相距很遠（B300 vLLM 為 concurrency 8 與 64）。MI355X MoRI SGLang 在 2026-10-04 重跑過。）

| 模型 | 硬體（引擎） | concurrency | total tok/s 每 GPU | output tok/s 每 GPU | 每百萬 total tokens | 每百萬 output tokens | total tok/s per MW | 查核：API 重算的 total tok/s 每 GPU |
|---|---|---|---|---|---|---|---|---|
| DeepSeek-V4-Pro，FP4 | Vera Rubin NVL72（TensorRT-LLM） | 1,803 | 195,949 | 1,447 | $0.0051 | $0.69 | 59.4M | 186,246（−5.0%） |
| DeepSeek-V4-Pro，FP4 | GB300 NVL72（Dynamo SGLang） | 451 | 60,567 | 479 | $0.0106 | $1.34 | 28.6M | 60,341（−0.4%） |
| DeepSeek-V4-Pro，FP4 | B200（Dynamo SGLang） | 146 | 40,156 | 317 | $0.0120 | $1.51 | 23.5M | 39,612（−1.4%） |
| DeepSeek-V4-Pro，FP4 | GB200 NVL72（Dynamo SGLang） | 428 | 34,754 | 243 | $0.0149 | $2.13 | 18.6M | 36,791（+5.9%） |
| DeepSeek-V4-Pro，FP4 | MI355X（MoRI SGLang） | 52 | 22,470 | 152 | $0.0185 | $2.74 | 10.8M | 21,634（−3.7%） |
| DeepSeek-V4-Pro，FP4 | B300（vLLM） | 20 | 18,463 | 140 | $0.0340 | $4.49 | 9.7M | 21,870（+18.5%） |
| DeepSeek-V4-Pro，FP8 | H200（Dynamo SGLang） | 8 | 5,139 | 40 | $0.0659 | $8.41 | 3.8M | 5,097（−0.8%） |
| Kimi K3，MXFP4 | GB300 NVL72（Dynamo vLLM） | 48 | 9,600 | 64 | $0.0668 | $10.06 | 4.5M | 9,748（+1.5%） |
| Kimi K3，MXFP4 | MI355X（ATOM） | 7 | 4,132 | 33 | $0.1008 | $12.50 | 2.0M | 4,611（+11.6%） |
| Kimi K3，MXFP4 | B300（vLLM） | 6 | 4,051 | 30 | $0.1550 | $21.04 | 2.1M | 3,879（−4.2%） |
| Kimi K3，MXFP4 | B200（Dynamo vLLM） | 8 | 2,958 | 23 | $0.1625 | $21.28 | 1.7M | 2,976（+0.6%） |
| Kimi K3，MXFP4 | GB200 NVL72（Dynamo vLLM） | 16 | 2,395 | 15 | $0.2157 | $34.34 | 1.3M | 2,420（+1.1%） |
| GLM-5.2，FP4 | MI355X（ATOM） | 10 | 14,799 | 111 | $0.0282 | $3.75 | 7.1M | 14,684（−0.8%） |
| GLM-5.2，FP4 | B200（Dynamo SGLang） | 62 | 15,292 | 120 | $0.0314 | $3.99 | 8.9M | 14,935（−2.3%） |
| GLM-5.2，FP4 | GB200 NVL72（Dynamo SGLang） | 116 | 15,900 | 130 | $0.0325 | $3.98 | 8.5M | 15,934（+0.2%） |
| GLM-5.2，FP4 | GB300 NVL72（Dynamo SGLang） | 91 | 18,162 | 140 | $0.0353 | $4.60 | 8.6M | 18,262（+0.6%） |
| DeepSeek-V4.1-Flash，FP4 | GB300 NVL72（vLLM） | 72 | 232,066 | 1,666 | $0.0028 | $0.39 | 109.5M | 234,609（+1.1%） |
| DeepSeek-V4.1-Flash，FP4 | B300（vLLM） | 64 | 214,417 | 1,527 | $0.0029 | $0.41 | 112.9M | 214,436（+0.0%） |
| DeepSeek-V4.1-Flash，FP4 | B200（vLLM） | 89 | 157,803 | 1,152 | $0.0030 | $0.42 | 92.3M | 157,953（+0.1%） |
| DeepSeek-V4.1-Flash，FP4 | MI355X（vLLM） | 32 | 77,236 | 393 | $0.0054 | $1.06 | 37.0M | 75,905（−1.7%） |
| DeepSeek-V4.1-Flash，FP4 | GB200 NVL72（vLLM） | 29 | 55,813 | 329 | $0.0093 | $1.57 | 29.9M | 56,002（+0.3%） |
| DeepSeek-V4.1-Flash，FP4 | H200（vLLM） | 11 | 16,626 | 121 | $0.0204 | $2.80 | 12.1M | 17,747（+6.7%） |

- total 含 cached input，每百萬 total tokens 的成本因此比 output 口徑低約兩個量級；跨模型或與 8K/1K 比較時只能用 output 欄。固定長度的 disaggregated 結果另有一個陷阱：計算器的 output 吞吐量是除以 decode GPU 數，不是全部 GPU（Qwen3.5-397B 8K/1K 的 GB300 Dynamo TensorRT-LLM 列顯示 10,977，整體口徑是 37,956 ÷ 9 = 4,217，D）。
- 文章快照與三週後的計算器差距很大。[InferenceX 2026-09-14](https://inferencex.semianalysis.com/blog/vera-rubin-nvl72-agentic-inference) 的文章在同一操作點列出 Rubin 59.4M、GB300 Dynamo SGLang 28.5M、B200 SGLang 6.95M、B300 vLLM 5.56M、H200（FP8）2.26M、MI355X SGLang 2.01M total tok/s per MW；10 月初 B200 與 MI355X 已換成新引擎的 23.5M 與 10.8M，Rubin 對 MI355X 由 29.5× 降為 5.5×（D）。
- 其他已公布的模型化結果：GLM-5.3 在 150 tok/s/user（P90）下 GB200 約 $0.044、MI355X ATOM $0.049 每百萬 total tokens，只計 output 為 $5.92 對 $6.68；加上 P90 TTFT ≤ 2 s 的條件後變成 MI355X ATOM $0.0607 對 B200 $0.0666（[InferenceX 2026-09-28](https://inferencex.semianalysis.com/blog/sparse-savings-persistent-demand-inside-glm53)）。DeepSeek-V4-Pro 8K/1K 上，GB300 加 MTP 在 50 tok/s/user 時為每百萬 output tokens $0.156（[InferenceX 2026-06-09](https://inferencex.semianalysis.com/blog/deepseekv4-16t-day-0-to-day-43-performance)）。

### 代管 API：為速度付出的溢價

同一個 gpt-oss-120b，Cerebras 一次 10K 輸入、500 輸出的請求成本是 Groq、Azure、Nebius 的 2.2 倍，換到 3.7–6.3 倍的每串流速度；對最便宜的 GPU 端點則是 8.5–10 倍的價格換 37–40 倍的速度（D）。

**表 8-15 gpt-oss-120b：牌價對量測速度**（價格與速度取自 AA，2026-10-04；單次成本 = 10,000 × input 價 + 500 × output 價，D。來源：[AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers)）

| 供應商 | 硬體類別 | 每百萬 input / output（USD） | AA 10K：t/s | 單次請求成本（10K + 500） | Cerebras 成本 ÷ 本列 | Cerebras 速度 ÷ 本列 |
|---|---|---|---|---|---|---|
| Cerebras | wafer-scale ASIC | 0.35 / 0.75 | 1,764 | $0.00388 | 1.0× | 1.0× |
| SambaNova | RDU ASIC | 0.22 / 0.59（OpenRouter：0.14 / 0.95） | 706 | $0.00250（$0.00188） | 1.6×（2.1×） | 2.5× |
| Groq | LPU ASIC | 0.15 / 0.60 | 473 | $0.00180 | 2.2× | 3.7× |
| Microsoft Azure | 未揭露 | 0.15 / 0.60 | 320 | $0.00180 | 2.2× | 5.5× |
| Nebius（Base） | GPU 雲 | 0.15 / 0.60 | 280 | $0.00180 | 2.2× | 6.3× |
| DeepInfra（Turbo） | GPU 雲 | 0.15 / 0.60 | 248 | $0.00180 | 2.2× | 7.1× |
| Crusoe | GPU 雲 | 0.05 / 0.20 | 233 | $0.00060 | 6.5× | 7.6× |
| Baseten | GPU 雲 | 0.10 / 0.50 | 221 | $0.00125 | 3.1× | 8.0× |
| Amazon Bedrock | 未揭露 | 0.15 / 0.60 | 83 | $0.00180 | 2.2× | 21× |
| DeepInfra（標準） | GPU 雲 | 0.037 / 0.17 | 48 | $0.00046 | 8.5× | 37× |
| CoreWeave | GPU 雲 | 0.03 / 0.17 | 44 | $0.00038 | 10× | 40× |

- Cerebras 的溢價集中在 input，而且快取命中不打折：gpt-oss-120b 的 input 價是 21 個 OpenRouter 端點中最高，Qwen3.8 27B 為 $0.99 / $1.49，input 是 17 個端點中最高、output 最低，cache read 仍收 $0.99（[OpenRouter gpt-oss-120b](https://openrouter.ai/api/v1/models/openai/gpt-oss-120b/endpoints)、[OpenRouter Qwen3.8 27B](https://openrouter.ai/api/v1/models/qwen/qwen3.8-27b/endpoints)）。Qwen3.8 27B 同樣的 10K + 500 請求，Cerebras $0.0106、Parasail $0.0035（3.0×），速度是 1,025 對 83 t/s（12×，D）。
- Trainium2 的溢價是 25%：Bedrock latency-optimized 的 Claude 3.5 Haiku 為 $1 / $5，standard 為 $0.80 / $4，P50 output 速度 85.9 對 48.4 tok/s（1.8×）（[Anthropic](https://claude.com/blog/trainium2-and-distillation)、[AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/optimizing-ai-responsiveness-a-practical-guide-to-amazon-bedrock-latency-optimized-inference/)）。
- GPU 上的快速層不一定比較貴：Kimi K3 在 LithosAI ULTRA CHAT（320 t/s）為 $5.60 / $28、Inco FAST（282 t/s）為 $6 / $30，牌價是 $3 / $15；但 LithosAI 的標準 GLM-5.3 端點（474 t/s）為 $1.05 / $3.30，低於牌價 $1.40 / $4.40（A，2026-10-04，[AA Kimi K3](https://artificialanalysis.ai/models/kimi-k3/providers)、[AA GLM-5.3](https://artificialanalysis.ai/models/glm-5-3/providers)）。

### 功耗與實測能耗

功耗的公開數字只有三類：路線圖報導的 Rubin GPU 1,800 W、Google 的 Ironwood pod「nearly 10 MW」（9,216 顆）、分析師估計的 Cerebras CS-3 每系統約 25 kW。NVL72 級機櫃、LPX、Helios、Trainium 與 Inferentia2 的功耗都查無公開資料。

**表 8-16 每晶片與每機櫃功耗**

| 系統 | 晶片功耗 | 機櫃或系統功耗 | 等級 | 來源 |
|---|---|---|---|---|
| Trainium1 / 2 / 3 | 查無公開資料（AWS 未揭露任何一代的晶片功耗） | 查無公開資料 | 無 | [SemiAnalysis](https://newsletter.semianalysis.com/p/aws-trainium3-deep-dive-a-potential) |
| Inferentia2 | 查無公開資料 | 查無公開資料 | 無 | [AWS News Blog](https://aws.amazon.com/blogs/aws/amazon-ec2-inf2-instances-for-low-cost-high-performance-generative-ai-inference-are-now-generally-available/) |
| TPU Ironwood | Google 未公布 TDP；InferenceX 假設 980 W、all-in 1.207 kW（表 8-13） | 9,216 顆的 pod「nearly 10 MW」，約 1.09 kW / 晶片（D：10 MW ÷ 9,216） | C；D；B | [Google](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/ironwood-tpu-age-of-inference/) |
| H100、H200、B200、B300 | InferenceX 假設 TDP 700、700、1,000、1,200 W（表 8-13）；NVIDIA 產品頁數值未取得 | 8-GPU 節點功耗：查無公開資料 | B | 表 8-13 |
| GB200 NVL72、GB300 NVL72 | InferenceX 假設 1,200、1,400 W | 查無公開資料（NVIDIA 產品頁未載） | B；無 | [GB200](https://www.nvidia.com/en-us/data-center/gb200-nvl72/)、[GB300](https://www.nvidia.com/en-us/data-center/gb300-nvl72/) |
| Vera Rubin NVL72 | Rubin GPU 1,800 W（2025-08 的路線圖報導，上市前） | 查無公開資料；全液冷、45 °C 進水、約 4,000 lb | C | [Tom's Hardware](https://www.tomshardware.com/tech-industry/semiconductors/nvidia-enterprise-roadmap-rubin-rubin-ultra-feynman-and-silicon-photonics)、[NVIDIA](https://developer.nvidia.com/blog/nvidia-vera-rubin-pod-seven-chips-five-rack-scale-systems-one-ai-supercomputer/) |
| Rubin Ultra（Kyber，2027 下半年） | 3,600 W / package | 600 kW（2025-03 報導） | C | [Tom's Hardware](https://www.tomshardware.com/tech-industry/semiconductors/nvidia-enterprise-roadmap-rubin-rubin-ultra-feynman-and-silicon-photonics)、[DCD](https://www.datacenterdynamics.com/en/news/nvidias-rubin-ultra-nvl576-rack-expected-to-be-600kw-coming-second-half-of-2027/) |
| Groq 3 LPX | 未揭露 | 未揭露 | 無 | [StorageReview](https://www.storagereview.com/news/nvidia-groq-3-lpx-enters-full-production-3400-tokens-per-second-at-100k-context-256-lp30s-per-rack) |
| AMD MI355X；Helios | InferenceX 假設 1,400 W、all-in 2.09 kW | Helios：查無公開資料 | B；無 | [AMD](https://www.amd.com/en/products/accelerators/instinct/mi400.html) |
| Cerebras CS-3 | 不適用（一片 WSE-3） | 約 25 kW / 系統；冷卻流量約 4 LPM/kW，NVL72 參考值約 1.5 | 分析師估計 | [SemiAnalysis](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) |
| Cerebras CS-4 | 不適用（三片 WSE-3T） | 120–140 kW / 機櫃，或「125–135 kW TDP」 | 分析師估計 | [Futurum](https://futurumgroup.com/insights/cerebras-cs-4-makes-the-rack-the-new-chip-by-doubling-power-and-tripling-wafers/)、[SemiAnalysis](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast) |

- 筆記由 NVIDIA 的「100 MW AI factory」數字推得 Vera Rubin NVL72 每機櫃約 172–180 kW（含 NVIDIA 假設的 overhead，D），72 顆 GPU 以 1,800 W 計為 130 kW；兩者都是估計，不是機櫃規格（[NVIDIA](https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/)）。
- Cerebras 的大模型功耗只有分析師估計：1.6T 模型、1M context、256 個並行請求約需 40 套系統、約 1 MW（[SemiAnalysis](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast)）。

**表 8-17 InferenceX 實測的 GPU 功耗與每 output token 能耗**（等級 A。只含 GPU 本體的平均功耗，不含主機、網路與散熱；只取通過 InferenceX power 驗證的列。J / output token = 平均功耗 ÷ 每 GPU output tok/s。來源：InferenceX API，2026-10-04 擷取，連結同表 8-2）

| 模型（負載） | 硬體（引擎） | concurrency | output tok/s 每 GPU | GPU 平均功耗（W） | J / output token | 量測日 |
|---|---|---|---|---|---|---|
| DeepSeek-V4.1-Flash，FP4，MTP（AgentX） | GB300 NVL72（vLLM） | 192 | 3,108 | 904 | 0.29 | 2026-10-02 |
| 同上 | B300（vLLM） | 192 | 3,059 | 948 | 0.31 | 2026-10-02 |
| 同上 | B200（vLLM） | 128 | 1,362 | 861 | 0.63 | 2026-10-03 |
| 同上 | MI355X（vLLM） | 64 | 999 | 910 | 0.91 | 2026-10-02 |
| 同上 | GB200 NVL72（vLLM） | 64 | 615 | 805 | 1.31 | 2026-09-21 |
| 同上 | H200（vLLM） | 32 | 231 | 600 | 2.61 | 2026-09-21 |
| 同上 | H100（vLLM） | 20 | 90 | 493 | 5.54 | 2026-09-18 |
| DeepSeek-V4-Pro，FP4（AgentX） | B300（SGLang，MTP） | 384 | 739 | 866 | 1.18 | 2026-09-29 |
| 同上 | B200（vLLM，DSpark） | 128 | 456 | 734 | 1.62 | 2026-09-19 |
| 同上 | MI355X（SGLang，DSpark） | 128 | 362 | 719 | 1.99 | 2026-09-29 |
| DeepSeek-V4-Pro，FP8（AgentX） | H200（Dynamo SGLang，DSpark） | 8 | 41 | 475 | 11.5 | 2026-09-16 |
| Kimi K3，MXFP4，DSpark（AgentX） | GB300 NVL72（Dynamo vLLM） | 48 | 136 | 983 | 7.27 | 2026-09-15 |
| 同上 | B200（Dynamo vLLM） | 72 | 86 | 767 | 8.96 | 2026-10-02 |
| 同上 | MI355X（ATOM） | 72 | 104 | 941 | 9.11 | 2026-09-29 |
| Qwen3.5-397B，FP8，無 spec decode（8K/1K） | B200（SGLang） | 128 | 950 | 948 | 1.00 | 2026-09-18 |
| 同上 | MI355X（SGLang） | 64 | 535 | 861 | 1.61 | 2026-09-25 |

- 同模型、同 trace 下，每 output token 的能耗 MI355X 是 B200 的 1.4 倍（0.91 ÷ 0.63）、Kimi K3 上與 B200 相當（9.11 對 8.96）；Hopper 是 Blackwell Ultra 的 9–19 倍（2.61 ÷ 0.29；5.54 ÷ 0.29）（D）。
- P/D disaggregated 的列與 Vera Rubin 在快取中沒有通過驗證的功耗紀錄。TPU、Trainium、Inferentia2、Cerebras 與 LPX 沒有任何對應的獨立量測：查無公開資料。

### 廠商的經濟性宣稱

以下全部是等級 C：比值而非絕對值，條件多半未揭露。唯一可對照的客戶數字是 Cognition 的 4.8×，低於 NVIDIA 的 10×。

**表 8-18 廠商的成本與能效宣稱**（等級 C）

| 廠商；產品 | 宣稱 | 基準 | 已揭露的條件 | 日期 | 來源 |
|---|---|---|---|---|---|
| AWS；Trainium2 | 「30-40% better price performance」 | P5e、P5en（H200）執行個體 | workload 與指標未載；早於 2026-07 與 2026-10 的 GPU Capacity Blocks 調漲 | 2024-12 | [AWS Trn2](https://aws.amazon.com/ec2/instance-types/trn2/) |
| AWS；Trainium | 「about 30% better price-performance than comparable GPUs」 | comparable GPUs | 無 | 2026-04-09 | [股東信](https://www.aboutamazon.com/news/company-news/amazon-ceo-andy-jassy-2025-letter-to-shareholders) |
| AWS；Trainium3 | 「up to 40% better price-performance」；股東信為 30–40% | Trainium2 | 無 | 2026-07-31；2026-04-09 | [About Amazon](https://www.aboutamazon.com/news/aws/amazon-ai-chips-business-history)、[股東信](https://www.aboutamazon.com/news/company-news/amazon-ceo-andy-jassy-2025-letter-to-shareholders) |
| AWS；Trainium3 | 「up to 3× faster」「over 5× higher output tokens per megawatt at similar latency per user」 | Trainium2 | 在 Bedrock 上；模型未載，AWS Japan 的摘要指為 GPT-OSS-120B | 2025-12-02 | [AWS What's New](https://aws.amazon.com/about-aws/whats-new/2025/12/amazon-ec2-trn3-ultraservers/) |
| AWS；Trn3 UltraServer | 「up to 4.4x higher performance … 4x better performance/watt」 | Trn2 UltraServer | UltraServer 對 UltraServer；無 workload | 2025-12-02 | [AWS Trn3](https://aws.amazon.com/ec2/instance-types/trn3/) |
| AWS；Inferentia2 | 「up to 50 percent better performance per watt」 | 其他可比的 EC2 執行個體 | 2023 年上市時的說法；無功耗數字 | 2023-04-13 | [AWS News Blog](https://aws.amazon.com/blogs/aws/amazon-ec2-inf2-instances-for-low-cost-high-performance-generative-ai-inference-are-now-generally-available/) |
| Google；Ironwood | perf/W「2x relative to Trillium」 | Trillium | 無 | 2025-04-09 | [Google](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/ironwood-tpu-age-of-inference/) |
| Google；TPU 8i | 「up to 80% performance-per-dollar improvement over Ironwood TPU, particularly at low-latency targets for large MoE models」；「up to 2x better performance-per-watt」 | Ironwood | 無絕對值；TPU 8i 尚無價格與文件頁（已宣布未出貨） | 2026-04-22 | [Google Cloud](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive) |
| NVIDIA；Vera Rubin NVL72 | 「one-tenth the cost per million tokens」；「up to 10x more tokens per megawatt」 | GB200 NVL72 | Kimi-K2-Thinking、32K / 8K ISL / OSL；精度、引擎、concurrency、成本模型未載 | 2026-01-05 | [NVIDIA](https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/) |
| NVIDIA；Vera Rubin NVL72 | tokens per MW「up to 30x」 | GB300 NVL72 | 140K context 的 agentic coding；DeepSeek-V4-Pro 上 110、130、160 tok/s/user 分別為 2×、10×、30× | 2026-08-24 | [StorageReview](https://www.storagereview.com/news/nvidia-groq-3-lpx-enters-full-production-3400-tokens-per-second-at-100k-context-256-lp30s-per-rack)、[NVIDIA](https://developer.nvidia.com/blog/nvidia-vera-rubin-and-blackwell-set-a-new-standard-for-agentic-ai-performance-per-watt/) |
| NVIDIA；Rubin + LPX | 「up to 35x higher inference throughput per megawatt」；「up to 10x more revenue opportunity」 | Blackwell | 「for trillion-parameter models」；模型、精度、context、concurrency、機櫃功耗皆未載 | 2026-03-16 | [NVIDIA](https://nvidianews.nvidia.com/news/nvidia-vera-rubin-platform) |
| CoreWeave；Cognition（客戶數字） | 「4.8x increase in total token throughput」 | GB200 NVL72 | Cognition SWE-2、matched interactivity；同文的「45x lower token cost vs Blackwell」筆記標為待查證 | 2026-09-30 | [CoreWeave](https://www.coreweave.com/blog/cognition-becomes-first-customer-for-nvidia-vera-rubin-nvl72-on-coreweave-cloud) |
| Cerebras；CS-4 | 「up to 10 times more throughput per watt than CS-3」；比 GPU 方案快「up to 30 times」 | CS-3；GPU | wafer 數、batch、context、concurrency 未載；SemiAnalysis 認為 perf/W「at best a slight improvement」 | 2026-08-18 | [Cerebras](https://www.cerebras.ai/blog/introducing-cerebras-cs-4)、[Cerebras 新聞稿](https://www.cerebras.ai/press-release/cerebras-unveils-cs-4-up-to-30-times-faster-than-gpu-based-solutions-3347356)、[SemiAnalysis](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast) |
| Cerebras + AMD Helios | 「up to five times more tokens per second per watt」 | 只用 Cerebras 的配置 | 內部模型推估（Kimi K2.6）；Cerebras 稱 AMD 方案 2026 Q4 進入量產 | 2026-07-23 宣布（eWeek 報導 2026-07-26） | [eWeek](https://www.eweek.com/news/amd-cerebras-disaggregated-inference/)；[Cerebras Q2 2026 results](https://www.sec.gov/Archives/edgar/data/2021728/000162828026056186/cbrsannouncesfinancialresu.htm) |
| AMD；Helios（MI455X） | 「up to 30% more tokens per dollar」 | Vera Rubin | 以預估售價計；無 workload | 2026-07-24 | [Moor Insights](https://moorinsightsstrategy.com/field-notes/amd-advancing-ai-2026-helios-ships-venice-swings-and-the-software-moat-narrows/) |

- Trainium2 的「30–40%」約等於當時牌價本身的差距：trn2.48xlarge 的 Capacity Blocks 價比 p5e.48xlarge 低 25%、比 p5en.48xlarge 低 35%（D），等同宣稱 16 顆 Trn2 的吞吐量與一台 8× H200 相當，不是對 Blackwell 的宣稱。
- NVIDIA 的倍數隨 context 與 interactivity 目標升高（32K / 8K 為 10×，140K 為 30×，加 LPX 為 35×）；InferenceX 在 DeepSeek-V4-Pro AgentX 量到的 Rubin 對 GB300 是 100 tok/s/user 時 2.1×、150 tok/s/user 時 7.2×（A，[InferenceX 2026-09-14](https://inferencex.semianalysis.com/blog/vera-rubin-nvl72-agentic-inference)）。

## 各晶片的適用情境評分

七項準則、六個平台共 42 格：NVIDIA GPU 有 4 格為「高」、沒有低於「中高」的格子；Cerebras 只有「每使用者速度」為「高」，另有 3 格為「低」；Inferentia2 有 4 格為「低」。評等是本文依前兩節證據所做的判斷（等級 D），不是量測；標 † 的 4 格沒有任何量測可依，只反映廠商宣稱或資料缺口。

評等的尺度：**高** = 有獨立量測支持，且為六者中最佳或並列最佳；**中高**、**中**、**中低** = 依與最佳者的差距遞減；**低** = 有證據顯示明顯受限。每格只列一項最關鍵的事實，完整數字見表 8-2 至表 8-17。

**表 8-19 適用情境評分卡**（等級 D；資料基準日 2026-10-04）

| 準則 | Trainium | Inferentia2 | TPU | NVIDIA GPU | AMD GPU | Cerebras |
|---|---|---|---|---|---|---|
| 每使用者速度 | **中**：一台 16 顆 Trainium2 加 spec decode 的單一串流為 102–144 tok/s（B）[NxDI 405B](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/tutorials/trn2-llama3.1-405b-speculative-tutorial.html) | **低**：Llama 3.1 8B 單一串流 38.8 tok/s（B）[Optimum Neuron CSV](https://github.com/huggingface/optimum-neuron/blob/main/benchmark/vllm/data-parallel/llama3.1-8b/vllm-results-dp3.csv) | **中**：Ironwood 在 100 tok/s/user 的每晶片吞吐量是 B200 的 0.86×，concurrency 256 的 TTFT 5.41 s 對 3.75 s（A；D）[InferenceX](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam) | **中高**：旗艦模型 concurrency 1–2 為 216–350 tok/s，Flash 級 621 tok/s（A）[InferenceX API](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Kimi-K3) | **中**：MI355X 同條件為 NVIDIA 最佳點的 0.61–0.83×（Kimi K3 172 對 258 tok/s）（A）[InferenceX API](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Kimi-K3) | **高**：gpt-oss-120b 1,764 t/s，是最快非 ASIC 端點的 5.5×（A）[AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |
| 每 token 成本 | **中** †：每 chip-hour $2.235 是 B200 的 18%，但沒有量測的每 token 成本；AWS 自稱比 H200 執行個體好 30–40%（C）[AWS Trn2](https://aws.amazon.com/ec2/instance-types/trn2/) | **中低**：Llama 3.1 8B 每百萬 output tokens $2.94（us-east-1 on-demand，D）[Optimum Neuron CSV](https://github.com/huggingface/optimum-neuron/blob/main/benchmark/vllm/data-parallel/llama3.1-8b/vllm-results-dp3.csv) | **中**：同條件點 3 年承諾 $1.44，Google 的 B200 3 年 CUD $1.99；on-demand $3.20 高於 neocloud 的 B200 $1.88–2.41（D）[Cloud TPU pricing](https://cloud.google.com/tpu/pricing) | **中高**：同一 AgentX 操作點的模型化成本最低（DeepSeek-V4-Pro：Rubin $0.69、GB300 $1.34 每百萬 output tokens），但 AWS 的 B200 Capacity Blocks 到 2026-10-07 將在三個月內累計上漲約 38%（表 8-14；D：1.20 × 1.15）[AWS Capacity Blocks](https://aws.amazon.com/ec2/capacityblocks/pricing) | **中**：隨模型而異；GLM-5.2 上 MI355X $3.75 低於 B200 $3.99，DeepSeek-V4-Pro 上 $2.74 高於 GB300 $1.34（表 8-14） | **中低**：gpt-oss-120b 單次請求成本是 Groq、Azure 的 2.2 倍，快取命中不打折（D）[OpenRouter](https://openrouter.ai/api/v1/models/openai/gpt-oss-120b/endpoints) |
| 長上下文 | **中低**：公開 recipe 最長 16,384 tokens；Bedrock latency-optimized 的 Llama 3.1 405B 上限 11K [vLLM Neuron](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/tutorials/tutorial-gpt-oss.html)、[Bedrock User Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html) | **低**：實測可服務的最大 context 為 32,768（6 顆晶片、11B 模型），單晶片機型為 1,024（A）[Exawizards](https://zenn.dev/exwzd/articles/20250930-inferentia-llama) | **中**：Gemini 的 1M context 在 TPU 上服務，但開源模型的公開 recipe 為 9,216–32,768 tokens，8K 輸入以上沒有獨立量測 [tpu-recipes](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/ironwood/vLLM) | **高**：AgentX 重播的輸入 p99 為 675K tokens、p50 為 88K（A）[InferenceX 2026-08-25](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-mi355x-vs-b200-august) | **中高**：MI355X 跑同一組 AgentX trace；AMD 自己的 Kimi K3 recipe 預設 `--max-model-len 16384`（C）[AMD](https://www.amd.com/en/developer/resources/technical-articles/2026/kimi-k3-on-amd-instinct-gpus.html) | **低**：公開 API 上限 131K；Qwen3.8 27B 在 OpenRouter 為 65,536，他處為 262,144 以上 [Cerebras docs](https://inference-docs.cerebras.ai/models/overview) |
| 開源旗艦模型的可用性 | **低**：AWS 沒有 Kimi、GLM、DeepSeek 的第一方 recipe；社群移植的 GLM-5.2 為 2.96 tok/s、sequence 2,048（B）[NxDI contrib](https://github.com/aws-neuron/neuronx-distributed-inference/blob/main/contrib/models/GLM-5.2/README.md) | **低**：沒有任何一個目標模型；gpt-oss 等新模型只支援 Trn2 / Trn3 [vLLM Neuron README](https://github.com/vllm-project/vllm-neuron/blob/release-0.24.0.1.1.0/README.md) | **中低**：Kimi K3、GLM-5.1 至 5.3、DeepSeek V4 Pro、Qwen3.8 都不在 support matrix；Qwen3.5-397B 與 DeepSeek V3 / R1 有 recipe [support matrices](https://github.com/vllm-project/tpu-inference/tree/main/support_matrices) | **高**：DeepSeek-V4.1-Flash day 0 即在 H100、H200、B200、B300、GB200、GB300 六種 SKU 上執行（A）[InferenceX 2026-09-18](https://inferencex.semianalysis.com/blog/engrams-embedding-entendre-codesign) | **中高**：MI355X 有 Kimi K3、GLM-5.2、DeepSeek-V4-Pro、V4.1-Flash 的結果，但 V4.1-Flash 第 7 天的 perf per dollar 仍比 B200 差 2–4 倍（A）[InferenceX 2026-09-18](https://inferencex.semianalysis.com/blog/engrams-embedding-entendre-codesign) | **低**：公開 API 只有 gpt-oss-120b 與 qwen-3.8-27b，四個家族的旗艦都不在公開目錄 [Cerebras docs](https://inference-docs.cerebras.ai/models/overview) |
| 取得容量與區域覆蓋 | **低**：Trn2 只能用 Capacity Blocks，且只在 Ohio、Hyderabad、Melbourne、São Paulo；Trn3 無公開價格與 Region；Tokyo、Singapore、Taipei 都沒有 [AWS EC2 Regions](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-regions.html) | **中高**：on-demand；至少 14 個 Region 有牌價，含 Tokyo、Singapore、Sydney、Mumbai，Taipei 沒有 [AWS 價目表](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json) | **中低**：單一雲；Ironwood 的 zone 在 Region 文件只列 us-central1，on-demand 不保證有容量 [TPU Regions](https://docs.cloud.google.com/tpu/docs/regions-zones) | **中高**：七家雲有公開牌價（表 8-9）；但 Vera Rubin 只有 CoreWeave 的 limited availability，GB300、B300 在 CoreWeave 為 contact sales [CoreWeave](https://www.coreweave.com/pricing) | **中低**：公開牌價只查到 OCI（MI300X $6.00、MI355X $8.60）；Helios 與 MI455X 沒有任何雲端 SKU [Oracle](https://www.oracle.com/cloud/compute/pricing/) | **低**：Cerebras Code 兩個方案都售罄，旗艦模型只供 enterprise，管理階層稱「Everyone is in a capacity crunch」[Cerebras Code](https://www.cerebras.ai/code)、[VentureBeat](https://venturebeat.com/technology/cerebras-says-its-chips-run-a-trillion-parameter-ai-model-nearly-7-times-faster-than-gpu-clouds) |
| 軟體成熟度與工程負擔 | **中低**：vLLM Neuron 為 Beta，支援表中每個模型的 Perf Tuning 欄都是「In progress」[vLLM Neuron README](https://github.com/vllm-project/vllm-neuron/blob/release-0.24.0.1.1.0/README.md) | **低**：Inf2 路徑凍結在 PyTorch 2.9 / vLLM 0.16.0，每個配置需 12–38 分鐘的 ahead-of-time 編譯 [Exawizards](https://zenn.dev/exwzd/articles/20250827_inferentia_compile) | **中低**：對外的 TorchTPU vLLM stack 仍是 private beta；support matrix 的量化、MLA、MoE 與 multi-host 多為 Untested [support matrices](https://github.com/vllm-project/tpu-inference/tree/main/support_matrices) | **高**：同一套 stack 涵蓋 vLLM、SGLang、TensorRT-LLM，並整合 AWS、Google Cloud、Azure、OCI（Dynamo 1.0）[NVIDIA](https://developer.nvidia.com/blog/nvidia-dynamo-1-production-ready/) | **中**：MI355X 上 DeepSeek-V4-Pro 從首次可跑到調校後，26 天內每 GPU 吞吐量提升 110.5 倍，day 0 不成熟但追趕快（A）[InferenceX 2026-05-26](https://inferencex.semianalysis.com/blog/mi355x-deepseek-v4-pro-sglang-110x-in-26-days) | **中高**：代管 API 相容 OpenAI，含 prompt caching、strict structured outputs、parallel tools，使用者不需自管引擎；但 2025-01 以來有 14 次模型下架 [Cerebras docs](https://inference-docs.cerebras.ai/support/deprecation) |
| 能效 | **中** †：只有相對宣稱（Trainium3「over 5× higher output tokens per megawatt」）；AWS 未揭露任何一代的晶片功耗（C）[AWS What's New](https://aws.amazon.com/about-aws/whats-new/2025/12/amazon-ec2-trn3-ultraservers/) | **中低** †：沒有功耗資料，只有 2023 年「up to 50 percent better performance per watt」的宣稱（C）[AWS News Blog](https://aws.amazon.com/blogs/aws/amazon-ec2-inf2-instances-for-low-cost-high-performance-generative-ai-inference-are-now-generally-available/) | **中高**：以 InferenceX 假設的 all-in 1.207 kW 計，同條件點每 MW 的 total tok/s 是 B200 的 1.49 倍（D：(9,364 ÷ 1.207) ÷ (8,903 ÷ 1.71)）；無實測功耗 [InferenceX](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam) | **高**：Vera Rubin 在 DeepSeek-V4-Pro AgentX、100 tok/s/user 為 59.4M total tok/s per MW，GB300 為 28.5M（吞吐量 A，功耗為模型值）[InferenceX 2026-09-14](https://inferencex.semianalysis.com/blog/vera-rubin-nvl72-agentic-inference) | **中**：實測每 output token 能耗 MI355X 0.91 J，B200 0.63 J、GB300 0.29 J（DeepSeek-V4.1-Flash，A）[InferenceX API](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4.1-Flash) | **中低** †：沒有獨立的 tokens per watt 量測；CS-4 機櫃 125–135 kW，SemiAnalysis 認為 perf/W 對 CS-3「at best a slight improvement」[SemiAnalysis](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast) |

會改變評等的證據：

- **Trainium**：任何獨立量測，或 AWS 公布 Trainium3 的絕對 tok/s、TTFT 與 tokens per MW，會改寫速度、成本、能效三格。InferenceX 的 OperatorX 已有 16 顆 Trn3 的 runner 但沒有結果（[CLUSTERS.md](https://github.com/SemiAnalysisAI/InferenceX/blob/main/operatorx/CLUSTERS.md)）；Trn3 出現公開價格或東亞 Region 會改變容量一格。
- **TPU**：TPU 8i GA 並以原生 FP4 進入 InferenceX 與 AgentX；TorchTPU stack 開源，Kimi K3 與 GLM-5.3 進入 support matrix。這會同時影響速度、成本、模型可用性與軟體四格。
- **NVIDIA**：LPX 出現公開 SKU、價格與機櫃功耗，每使用者速度可升為「高」；Vera Rubin 的公開牌價與 NVL72 級機櫃功耗的一手數字會檢驗成本與能效。未 pinned 的 spec decode acceptance 若進入 AgentX，每使用者速度可能下修。
- **AMD**：Helios 或 MI455X 的雲端 SKU 與 InferenceX 結果，會改變容量、成本與能效三格。
- **Cerebras**：公布每條 pipeline 的 concurrency、系統吞吐量與功耗，成本與能效才評得出來；公開目錄加入四個家族的旗艦，或 context 超過 131K，會改變模型可用性與長上下文兩格。
- **Inferentia2**：目前沒有 Inferentia3，Neuron 的新功能也只給 Trn2 / Trn3；除非 AWS 改變路線，各格不會上調。
- **共同**：MLPerf Inference v6.x 的按加速器成績表（本次未能讀取）可交叉驗證 GPU 的吞吐量；任何把 Trainium、TPU、Cerebras 放進同一 harness 的量測，都會取代表 8-12 的推算。

## 網站呈現建議

- **效能矩陣**：把表 8-2 至表 8-5 合成一張可排序、可篩選的矩陣，篩選條件為加速器、模型、負載、spec decode 與等級。「每使用者速度」與「每晶片 output 吞吐量」放在兩個分頁，不提供跨分頁排序；每列固定顯示 concurrency 與量測日。
- **同條件比較圖**：表 8-6 做成對數軸的水平長條圖，以硬體類別上色，hover 顯示 TTFT、100K 輸入與 10 個並行請求的數值；表 8-15 做成散佈圖（x = 單次請求成本，y = t/s）。表 8-7 用並列長條顯示 Ironwood、B200、B300 的吞吐量與 TTFT，並標明是 2026-09-07 的快照。
- **成本計算器**：表 8-10 至表 8-12 改成互動計算器，使用者輸入每 chip-hour 價格、選擇購買方式與操作點，頁面即時算出每百萬 output 與 total tokens 成本，公式固定顯示在旁。預設載入表 8-9 的牌價，並以開關切換 InferenceX 的自有 TCO。
- **能效圖**：表 8-14 的 tokens per MW 與表 8-17 的 J / output token 各做一張以模型分頁的長條圖，圖例明確區分「模型值（all-in）」與「實測（GPU 本體）」。沒有資料的平台以空白欄位加「查無公開資料」呈現，不補估計值。
- **評分卡**：表 8-19 做成 7 × 6 的 heatmap，點擊格子展開佐證事實與來源，† 的格子用斜線底紋；「會改變評等的證據」放在同頁的可展開清單。
- **可收合或移出的內容**：表 8-9 的完整價目移到第 1 章並在此連結，本章只保留同條件組用到的價格；表 8-18 的廠商宣稱預設收合，表 8-1 改成每張圖旁的「可比性」標籤。

