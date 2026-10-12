# 第 7 章 長上下文：200K 與 1M

資料基準日：2026-10-04。等級：**A** = 獨立第三方量測；**B** = 廠商 / 夥伴公布且揭露方法；**C** = 廠商宣稱或規格、未揭露方法；**D** = 本文推算（附算式）。

本章的 200K 以 200,000 tokens、1M 以 1,048,576 tokens 計算（來源另有定義時另註）。cold 指沒有 prefix cache 命中、整段 prompt 重新 prefill；warm 指命中 prefix cache、只 prefill 新增的尾段。

## KV cache 記憶體與 prefill 時間的計算

一條 1M-token 序列的 KV cache 在現役開源模型之間相差約 50 倍：DeepSeek-V4.1-Flash 0.87 GiB、DeepSeek-V4-Pro 約 4.8 GiB、Kimi K3 13.5 GiB（FP8）、GLM-5.x 與 Qwen3.8-2.4T 約 44–46 GiB（D）。cold prefill 1M tokens 已公布的最快數字是 43.7 s（DeepSeek-V4-Pro、32 顆 H20，B），256K 為 10–29 s；prefix cache 命中率 ≥ 0.9 時各模型的中位 TTFT 為 0.50–1.07 s，命中率低於 0.3 時為 65–420 s（A；表 7-7）。

### 算式

一條序列的 KV 記憶體，n 為 context 的 token 數，b 為每 token 的 KV bytes，b_s 為每序列固定 state（linear attention 層的 recurrent state，不隨 n 成長）：

```latex
M_{\mathrm{KV}}(n) = n \cdot b + b_s
```

MLA 層的 b，N_MLA 為持有 per-token KV 的 MLA 層數，r_kv 為 `kv_lora_rank`，d_rope 為 `qk_rope_head_dim`，w 為每個元素的 bytes（BF16 = 2、FP8 = 1）：

```latex
b_{\mathrm{MLA}} = N_{\mathrm{MLA}} \cdot \left(r_{kv} + d_{\mathrm{rope}}\right) \cdot w
```

GQA 層的 b，N_attn 為 full-attention 層數，h_kv 為 `num_key_value_heads`，d_h 為 `head_dim`：

```latex
b_{\mathrm{GQA}} = 2 \cdot N_{\mathrm{attn}} \cdot h_{kv} \cdot d_h \cdot w
```

一個節點可同時常駐的序列數，T_pool 為引擎在扣掉權重後回報的 KV 容量（tokens）：

```latex
N_{\mathrm{seq}}(n) = \frac{T_{\mathrm{pool}}}{n}
```

cold TTFT，R_prefill 為該硬體與佈局下的 prefill 速率（input tokens/s）：

```latex
\mathrm{TTFT}_{\mathrm{cold}} \approx \frac{n_{\mathrm{prompt}}}{R_{\mathrm{prefill}}}
```

warm TTFT，n_cached 為命中 prefix cache 的 token 數：

```latex
\mathrm{TTFT}_{\mathrm{warm}} \approx t_{\mathrm{lookup}} + \frac{n_{\mathrm{prompt}} - n_{\mathrm{cached}}}{R_{\mathrm{prefill}}}
```

R_prefill 不是常數。dense attention 的 prefill FLOPs 有二次項（P 為參數量，s 為序列長度，L 為層數，n_q 為 query head 數），Llama-3-70B 在 128K 時二次項占 55%，context 加倍時重算時間變 3.1 倍並趨近 4 倍 [B，2026-09-25] [arXiv 2609.30854](https://arxiv.org/abs/2609.30854)：

```latex
F_{\mathrm{prefill}}(s) = 2 P s + 2 L \, n_q \, d_h \, s (s + 1)
```

### 每條序列在 200K 與 1M 的 KV

**表 7-1 現役模型每條序列的 KV**（「200K」「1M」兩欄為等級 D：n × b，n = 200,000 與 1,048,576；括號內為加上固定 state 或 indexer key 之後的值。b 的推導與交叉核對見第 4 章表 4-2。）

| 模型 | KV 精度 | KV bytes/token（等級） | 每序列固定 state | 200K 的 KV（GiB） | 1M 的 KV（GiB） | 來源 |
|---|---|---|---|---|---|---|
| Kimi K3 | FP8 | 13,824 B（D：24 層 MLA × 576 × 1 B；InferenceX 實測 42.23 GiB ÷ 3,249,215 tokens = 13,955 B，A） | KDA state 約 434 MB（FP32，= 414 MiB；TP8 下每 rank 約 54 MB，B） | 2.57（含 state 2.98） | 13.50（含 state 13.90） | [LMSYS 2026-07-27](https://www.lmsys.org/blog/2026-07-27-kimi-k3-day0-support/)、[perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml) |
| Kimi K3 | BF16 | 27,648 B（D；SGLang 寫「約 27 KB」，B） | 同上 | 5.15（含 state 5.55） | 27.00（含 state 27.40） | [vLLM 2026-07-27](https://vllm.ai/blog/2026-07-27-k3) |
| GLM-5.2 / 5.3 | FP8 | 44,928 B（78 層 MLA × 576；llm-d 寫「約 44 KB」，B）；加 21 個 indexer key 約 47,616 B（D，假設每層每 token 一個 128 維 key） | 無 | 8.37（含 indexer 8.87） | 43.88（含 indexer 46.50） | [llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d) |
| DeepSeek-V4-Pro | BF16 | 1M 序列平均 9,856 B（D：vLLM 公布的 9.62 GiB ÷ 1,048,576） | 每層 128-token sliding window（已含在 9.62 GiB 內） | 1.84 | 9.62（vLLM 公布值，B） | [vLLM 2026-04-24](https://vllm.ai/blog/2026-04-24-deepseek-v4) |
| DeepSeek-V4-Pro | FP8 attention cache + FP4 indexer cache | 約 4,928 B（vLLM：再縮「roughly 2x」，B） | 同上 | 約 0.92 | 約 4.81 | [vLLM 2026-04-24](https://vllm.ai/blog/2026-04-24-deepseek-v4) |
| DeepSeek-V4.1-Flash | FP4（global KV） | 890 B（C） | SWA KV 另計：FP8、每層 128 tokens、有上限，放 host 記憶體或 SSD | 0.17 | 0.87 | [DeepSeek V4.1 tech report](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/main/DeepSeek_V41_Tech_Report.pdf) |
| Qwen3.8-2.4T | FP8 | 47,104 B（23 層 GQA × 2 × 4 × 256；vLLM 寫每層 2 KiB，B） | Gated DeltaNet state 285 MiB（BF16，B）；float32 為 552 MiB（D，上限） | 8.77（含 state 9.05） | 46.00（含 state 46.28） | [vLLM 2026-09-21](https://vllm.ai/blog/2026-09-21-qwen38-pd-serving) |
| Qwen3.8-27B | FP8 | 32,768 B（D：16 層 GQA × 2 × 4 × 256 × 1 B） | 72 MiB（BF16）或 144 MiB（float32）（D） | 6.10（含 state 6.17） | 32.00（含 state 32.07） | [LMSYS 2026-09-16](https://www.lmsys.org/blog/2026-09-16-nvfp4-kv-cache/) |
| Qwen3.8-27B | NVFP4 | 18,432 B（D：32,768 B × 56.25%；比例為 LMSYS 公布，B） | 同上 | 3.43（含 state 3.50） | 18.00（含 state 18.07） | [LMSYS 2026-09-16](https://www.lmsys.org/blog/2026-09-16-nvfp4-kv-cache/) |
| gpt-oss-120b（Trainium 文件的例子） | BF16 | 73,728 B（D：2 × 36 層 × 8 KV heads × 64 × 2 B） | 無 | 13.73 | 72.00 | [vLLM Neuron KV quantization](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/design/vllm/kv-cache-quantization.html) |
| gpt-oss-120b | FP8 | 36,864 B（D） | 無 | 6.87 | 36.00 | 同上 |

- AWS 對 gpt-oss-120b 公布的是 131K-token 序列約 9.66 GB（BF16）與約 4.83 GB（FP8）[C，2026-06-23]；73,728 B × 131,072 = 9.66 GB，與上表的 b 一致（D）。
- Qwen3.8 的原生 context 是 262,144，1M 靠引擎設定（`--max-model-len 1010000` 加 `max_position_embeddings` override）達成；本表為了可比仍以 1,048,576 計 [B] [vLLM recipe Qwen3.8-2.4T](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-2.4T-A95B.yaml)。
- 算式是下限：GLM-5.3 在 8× MI325X（TP8、`--gpu-memory-utilization 0.80`）回報 1,477,168 tokens 的 pool，每 rank 可用約 110 GB（256 × 0.80 − 755.6 ÷ 8），折合每 token 約 75 KB 的預算，高於 46.5 KiB 的推算值（D）[vLLM recipe GLM-5.3](https://github.com/vllm-project/recipes/blob/main/models/zai-org/GLM-5.3.yaml)。
- 對照組：V3.2 式的 dense MLA 堆疊（61 層）在 1M 是 83.9 GiB（BF16），Llama-3-70B（GQA）在 128K 是 42 GB、在 10⁶ tokens 是 328 GB [B] [vLLM 2026-04-24](https://vllm.ai/blog/2026-04-24-deepseek-v4)、[arXiv 2609.30854](https://arxiv.org/abs/2609.30854)。

### 具名節點放得下幾條序列

**表 7-2 扣掉權重後的 KV 容量與可同時常駐的序列數**（序列數為等級 D：KV 容量 ÷ n；是上限，沒有扣掉碎片、每序列 state，以及為了維持命中率而保留的閒置 session；DeepSeek-V4-Pro 的 B300 與 B200 兩列以觀測到的 working set 代替容量。vLLM recipe 取自 commit cbf76c0，commit 日期在兩份研究筆記中分別記為 2026-10-02 與 2026-10-03。）

| 模型；節點；引擎與佈局 | KV 容量（tokens） | 容量的等級；日期 | 200K 序列數 | 1M 序列數 | 來源 |
|---|---|---|---|---|---|
| Kimi K3；8× B300；vLLM TP8；FP8 KV | 3,249,215（42.23 GiB） | A；2026-08-03 | 16.2 | 3.1 | [perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)、[InferenceX 2026-08-03](https://inferencex.semianalysis.com/blog/kimi-k3-the-manos-the-mythos-the) |
| Kimi K3；vLLM TP8 改 DCP8；120K-token workload（來源該段未重述硬體）；cache 預算每顆 46.48 GiB | 1,930,000 → 19,750,000 | B；2026-09-13 | 9.7 → 98.8 | 1.8 → 18.8 | [vLLM 2026-09-13](https://vllm.ai/blog/2026-09-13-kimi-k3-performance-optimization) |
| DeepSeek-V4-Pro；8× B300；vLLM DEP8；384 條 trace | 約 43,000,000（觀測到的 HBM KV working set） | A；2026-08-25 | 215 | 41 | [InferenceX 2026-08-25](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-b200-vs-b300-kv-working-set) |
| DeepSeek-V4-Pro；8× B200；併發 196 | 約 22,000,000（同上） | A；2026-08-25 | 110 | 21 | 同上 |
| DeepSeek-V4-Pro；8× MI355X；vLLM TP8 | 8,524,228（`--max-num-batched-tokens` 限為 8,192 之後；之前為 4,730,981） | B；recipe cbf76c0 | 42.6 | 8.1 | [vLLM recipe DeepSeek-V4-Pro](https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4-Pro.yaml) |
| DeepSeek-V4.1-Flash；8× H100；vLLM TP8 | 7,022,899（每顆 13.47 GiB KV） | A；2026-09 之後 | 35.1 | 6.7 | [perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml) |
| DeepSeek-V4.1-Flash；8× H200；SGLang | 約 34,000,000 | A；2026-09 | 170 | 32.4 | 同上 |
| GLM-5.2；8× H200；vLLM TP8；FP8 KV | 598,000（每 rank 各存一份 25 GiB） | B；2026-07-22 | 3.0 | 0.57 | [llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d) |
| GLM-5.2；同級節點；DEP8 | 1,770,000 | B；2026-07-22 | 8.9 | 1.7 | 同上 |
| GLM-5.3；8× MI325X；vLLM TP8；`--max-model-len 524288` | 1,477,168 | B；recipe cbf76c0 | 7.4 | 1.4（該設定的上限是 524,288） | [vLLM recipe GLM-5.3](https://github.com/vllm-project/recipes/blob/main/models/zai-org/GLM-5.3.yaml) |
| Qwen3.8-2.4T；GB300；vLLM TP8；NVFP4 權重 | 70 GiB KV：262,144 時引擎保留 25 條（= 6,553,600 tokens） | B；recipe cbf76c0 | 32.8 | 6.3 | [vLLM recipe Qwen3.8-2.4T](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-2.4T-A95B.yaml) |

引擎直接量到的常駐條數（不是推算）：

- DeepSeek-V4-Pro、H20-96GB、SGLang：單節點 TP8 在 1M「只夠 batch 1」；兩節點 PP2-TP8 在 1M / 512K / 256K 可放 batch 4 / 8 / 16。MXFP4 權重加 online C128 壓縮後，每 rank 容量由 1,089,024 增至 11,044,906 tokens（10.14 倍）[B，2026-08-19] [LMSYS / Ant Group](https://www.lmsys.org/blog/2026-08-19-deepseek-v4-pro-engine-optimization-h20/)。
- Qwen3.8-27B、1× RTX PRO 6000 Blackwell（96 GB）、FP8 權重：FP8 KV 在 32,768 / 163,840 / 1,048,576 input tokens 可常駐 44 / 10 / 1 條，NVFP4 KV 為 70 / 15 / 2 條 [B，2026-09-16] [LMSYS 2026-09-16](https://www.lmsys.org/blog/2026-09-16-nvfp4-kv-cache/)。
- Trainium：扣掉權重後的 KV 容量查無公開資料，只能給不扣權重的上限（D）。gpt-oss-120b 以 BF16 存 1M 序列需 72.0 GiB，一顆 Trainium3（144 GiB）最多 2 條（144 ÷ 72.0），一台 Trn3 Gen2 UltraServer（20,736 GiB，AWS 寫作 20.7 TB）最多 288 條（20,736 ÷ 72.0）[AWS EC2 Trn3](https://aws.amazon.com/ec2/instance-types/trn3/)。若 1M 以 1,000,000 tokens 計，則為 68.7 GiB 與約 300 條（D）。
- Qwen3.8-2.4T 的兩個 vLLM 來源相差約 5 倍：recipe 的引擎回報是 70 GiB 內 9,240 tokens 可放 506 條、262,144 可放 25 條；blog 以未依 rank 切分的 759 MiB 去除每顆 GPU 的 73–83 GiB KV，得 10,240 tokens 約 98–112 條 [B] [vLLM 2026-09-21](https://vllm.ai/blog/2026-09-21-qwen38-pd-serving)。表 7-2 採 recipe 的引擎回報值。

### tensor parallel 對 MLA 模型 KV 容量的影響

tensor parallel 把 MLA 的 latent KV 在每個 rank 各存一份，不是切開：增加 TP rank 不會增加 KV 容量，容量由單顆 GPU 扣掉權重後的記憶體決定 [B，2026-09-13] [vLLM 2026-09-13](https://vllm.ai/blog/2026-09-13-kimi-k3-performance-optimization)。GLM-5.2 在 8× H200 上 TP8 只有 598K tokens，同一節點改 DEP8 為 1.77M，DEP16 每個 node-share 約 5.2M [B，2026-07-22] [llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)；AMD 的 Kimi K3 配置（8× MI355X、TP8、FP8 KV）是每顆 GPU 為每條 1M 序列各付約 14.4 GiB [C，2026-07-27] [AMD 2026-07-27](https://www.amd.com/en/developer/resources/technical-articles/2026/kimi-k3-on-amd-instinct-gpus.html)。

- 解法是不再複製：decode context parallelism（DCP）沿序列維度把 KV 切到各 rank，Kimi K3 的容量由 1.93M 增至 19.75M tokens；或改用 DEP（每個 rank 一份權重、各自的 KV）[B] [vLLM 2026-09-13](https://vllm.ai/blog/2026-09-13-kimi-k3-performance-optimization)。
- Kimi K3 的 KDA state 與 MLA KV 行為相反：KDA state 依 head 與維度切到各 rank，但 state pool 是併發上限，DP、EP、DCP 都不會把它再切小；8× B300 上可准入 60–101 條請求 [B] [SGLang Kimi-K3 cookbook](https://docs.sglang.io/cookbook/autoregressive/Moonshotai/Kimi-K3)。
- GQA 模型不同：Qwen3.8-2.4T 在 TP8 下每個 rank 只存 4 個 KV head 之一（D，由 recipe 回報的 25 條與 506 條反推）；但 GQA 模型的 DCP 上限為 `tp // num_key_value_heads`，4 個 KV head 在 TP8 最多 DCP2 [A，評論] [InferenceX AgentX](https://inferencex.semianalysis.com/blog/agentx-inferencexv3-does-cuda-moat)。

### cold prefill 的量測值

**表 7-3 固定 prompt 長度、無 cache 命中的 TTFT**（自架、硬體已揭露；括號內為 total input tokens/s。）

| 模型（attention） | 硬體；引擎；平行化；精度 | 約 100K | 約 200K | 約 500K | 1M | 併發 | 等級；日期；來源 |
|---|---|---|---|---|---|---|---|
| DeepSeek-V4-Pro（CSA / HCA sparse + SWA） | 32× H20-96GB；SGLang PP4-CP8-TP8；MXFP4 權重、FP8 activation | 128K：5.88 s（22,280） | 256K：10.35 s（25,330） | 512K：20.27 s（25,860） | 43.74 s（23,970；最佳化前 55.53 s） | 1 | B；2026-08-19；[LMSYS / Ant Group](https://www.lmsys.org/blog/2026-08-19-deepseek-v4-pro-engine-optimization-h20/) |
| DeepSeek-V4-Pro | 16× H20-96GB；SGLang PP2-CP8-TP8；同上 | 128K：7.98 s（16,430） | 256K：15.51 s（16,900） | 512K：34.98 s（14,990） | 79.21 s（13,240） | 1 | B；2026-08-19；同上 |
| Qwen3-235B-A22B（dense GQA，2025 年機型；context 覆寫為 1M 僅供效能分析） | 32× H20；SGLang PP8 TP4；FP8 | 128K：10.54 s | 256K：32.68 s | 512K：114.33 s | 420.91 s | 1 | B；2026-01-15；[LMSYS chunked pipeline](https://www.lmsys.org/blog/2026-01-15-chunked-pipeline/) |
| DeepSeek-R1（dense MLA） | GB300 NVL72 的 8 顆 GPU（1 prefill + 1 decode worker）；SGLang + Dynamo PD；NVFP4 | 128K in / 8K out：mean 15.2 s（GB200 為 18.6 s）；加 32K dynamic chunk 與 chunked PP 後 8.6 s | 查無 | 查無 | 查無 | 未逐點揭露 | B；2026-02-19；[LMSYS / NVIDIA](https://www.lmsys.org/blog/2026-02-19-gb300-longctx/) |
| GLM-5.2（MLA + DSA） | 24× B300（16 顆 prefill + 8 顆 decode）；vLLM PD；NVFP4；隨機 prompt | 64K：mean 約 8 s、P90 約 13 s（讀圖，近似） | 256K：mean 28.74 s、P90 53.74 s（57,660） | 查無 | 查無 | 約 25（256K） | B；2026-07-23；[vLLM / DaoCloud](https://vllm.ai/blog/2026-07-23-glm-5.2-nvfp4-b300-pd) |
| Qwen3.8-27B（Gated DeltaNet + GQA；1M 靠 context override） | 1× RTX PRO 6000 Blackwell 96 GB；SGLang，radix cache 關閉；FP8 權重、FP8 KV | 查無 | 163,840：mean 250.19 s、P99 448.08 s（含排隊） | 查無 | 1,143.74 s | 10（163,840）；1（1M） | B；2026-09-16；[LMSYS 2026-09-16](https://www.lmsys.org/blog/2026-09-16-nvfp4-kv-cache/) |

- sparse attention 把 TTFT 隨長度的成長由接近二次壓到接近線性（D：TTFT(2n) ÷ TTFT(n)，同為 32 顆 H20）：DeepSeek-V4-Pro 在 128K→256K、256K→512K、512K→1M 為 1.76、1.96、2.16 倍，dense 的 Qwen3-235B 為 3.10、3.50、3.68 倍；1M 時前者快 9.6 倍（420.91 ÷ 43.74）。
- 每顆 GPU 的 cold prefill 速率在 1M（D：total input tokens/s ÷ GPU 數）：DeepSeek-V4-Pro 在 H20 上 PP4 為 749（23,970 ÷ 32）、PP2 為 828（13,240 ÷ 16）；Qwen3.8-27B 在單張 RTX PRO 6000 為 917（1,048,576 ÷ 1,143.74 s）。GLM-5.2 在 B300 每顆 prefill GPU 由 8K 的 9,035 降到 256K 的 3,590 input tokens/s（D：(162,207 − 17,647) ÷ 16 與 (57,660 − 219) ÷ 16），下降約 60%。
- Kimi K3、GLM-5.2 / 5.3、Qwen3.8-2.4T 在 500K–1M 的固定長度 cold prefill：查無公開資料；GLM-5.2 最長的固定長度點是 256K，Kimi K3 沒有任何一點。Trainium、TPU、Cerebras、LPX 在 100K 以上的固定長度量測：查無公開資料。

**表 7-4 由量測到的 prefill 速率推算的 cold TTFT**（四個時間欄全部為等級 D，不是量測；n = 100,000、200,000、500,000、1,048,576。）

| 模型；硬體；引擎 | prefill 速率（量測；等級） | 100K | 200K | 500K | 1M | 算式與限制 |
|---|---|---|---|---|---|---|
| DeepSeek-V4.1-Flash；8× H200；SGLang；FP4 | 4,200 input tokens/s（A；滿載時的中位數，4,096-token chunk，KV pool 34M tokens） | 約 24 s | 約 48 s | 約 119 s | 約 250 s | n ÷ 4,200；來源是滿載伺服器的速率 |
| DeepSeek-V4.1-Flash；8× H100；SGLang | 2,800 input tokens/s（A） | 約 36 s | 約 71 s | 約 179 s | 約 375 s | n ÷ 2,800 |
| GLM-5.2 NVFP4；8× B200 TP8；SGLang | 24,027 tokens/s（B；約 32K 的 cache-miss prefill，10 個樣本的峰值，median TTFT 1.369 s） | ≥ 4.2 s | ≥ 8.3 s | ≥ 21 s | ≥ 44 s | n ÷ 24,027；速率隨長度下降，線性外推是下限 |

速率來源：[perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)（2026-09）、[llm-d 2026-08-17](https://llm-d.ai/blog/sticky-until-saturated-token-aware-routing)。

**表 7-5 代管 API 在約 100K-token prompt 的 TTFT**（Artificial Analysis；每次測試用不同的 prompt，所以是未命中 cache 的 prefill 加排隊；各端點為等級 A、2026-10-04 擷取，跨端點中位數為 D。100K 是 AA 最長的 workload，200K 以上查無公開資料。）

| 模型 | 端點數 | TTFT 中位：1K → 10K → 100K（s） | 100K 的範圍（s） | 來源 |
|---|---|---|---|---|
| Kimi K3 | 17 | 0.73 → 1.18 → 6.25 | 5.12–106.1 | [AA Kimi K3](https://artificialanalysis.ai/models/kimi-k3/providers) |
| GLM-5.3 | 24 | 0.52 → 0.96 → 6.60 | 3.14–142.8 | [AA GLM-5.3](https://artificialanalysis.ai/models/glm-5-3/providers) |
| DeepSeek V4 Pro | 9 | 1.20 → 1.69 → 6.25 | 5.12–15.6 | [AA DeepSeek V4 Pro](https://artificialanalysis.ai/models/deepseek-v4-pro/providers) |
| DeepSeek V4.1 Flash | 22 | 0.71 → 0.90 → 4.70 | 2.19–198.2 | [AA DeepSeek V4.1 Flash](https://artificialanalysis.ai/models/deepseek-v4-1-flash/providers) |
| Qwen3.8-2.4T | 6 | 0.71 → 0.95 → 7.62 | 4.18–11.4 | [AA Qwen3.8 2.4T](https://artificialanalysis.ai/models/qwen3-8-2-4t-a95b/providers) |
| Qwen3.8-27B | 7 | 0.58 → 1.19 → 10.01 | 6.40–43.2 | [AA Qwen3.8 27B](https://artificialanalysis.ai/models/qwen3-8-27b/providers) |
| gpt-oss-120b | 16 | 0.52 → 0.81 → 3.73 | 1.25–19.8 | [AA gpt-oss-120b](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |

- 同一份權重（gpt-oss-120b）在 100K 的硬體類別差異 [A]：Cerebras TTFT 3.44 s、1,225 output tokens/s（10K 時 1,764）；Groq 4.88 s、476；SambaNova 6.78 s、360（10K 時 706）；GPU 代管的 Baseten 1.25 s、332，Crusoe 2.11 s。ASIC 在 100K 保住 decode 速度，TTFT 則落後最快的 GPU 端點 [AA gpt-oss-120b](https://artificialanalysis.ai/models/gpt-oss-120b/providers)。
- 私有模型在 100K 的 TTFT [A]：Claude Haiku 4.5 在 Anthropic 2.48 s、Amazon Bedrock 3.48 s；Claude Sonnet 5.5（low effort）2.97 s、Bedrock 5.17 s；Claude Opus 5.5（low effort）16.92 s、Bedrock 13.42 s；GPT-5.6 Terra（non-reasoning）在 OpenAI 1.17 s；Gemini 3.8 Flash（AI Studio）16.37 s [AA Claude 4.5 Haiku](https://artificialanalysis.ai/models/claude-4-5-haiku/providers)、[AA Claude Sonnet 5.5](https://artificialanalysis.ai/models/claude-sonnet-5-5-low/providers)、[AA Claude Opus 5.5](https://artificialanalysis.ai/models/claude-opus-5-5-low/providers)、[AA GPT-5.6 Terra](https://artificialanalysis.ai/models/gpt-5-6-terra-non-reasoning/providers)、[AA Gemini 3.8 Flash](https://artificialanalysis.ai/models/gemini-3-8-flash/providers)。

### warm（cache 命中）的量測值

**表 7-6 prefix cache 命中時的 TTFT**（InferenceX AgentX 重播 coding agent trace，併發 1，所以 TTFT ≈ cache 查找加尾段 prefill；等級 A。ISL 為 input sequence length。TTFT、ISL、命中率與日期於 2026-10-05 以 InferenceX API 的 `median_ttft`、`median_input_tokens`、`server_gpu_cache_hit_rate` 與 `date` 欄逐列核對；前九列的命中率為 0.964–0.984。）

| 模型 | 硬體；引擎；精度 | 日期 | TTFT p50 / p90 / p95（s） | ISL p50 / p90 / p95 | GPU cache 命中率 | 來源 |
|---|---|---|---|---|---|---|
| DeepSeek-V4.1-Flash | 4× B200；vLLM；FP4 | 2026-10-03 | 0.18 / 0.28 / 0.38 | 354K / 600K / 643K | 0.982 | [444098](https://inferencex.semianalysis.com/inference/agentic/444098) |
| DeepSeek-V4.1-Flash | 4× MI355X；vLLM | 2026-10-02 | 0.23 / 0.63 / 1.12 | 333K / 530K / 558K | 0.973 | [443863](https://inferencex.semianalysis.com/inference/agentic/443863) |
| DeepSeek-V4.1-Flash | 8× H100；vLLM | 2026-09-18 | 0.48 / 1.11 / 2.05 | 315K / 500K / 530K | 0.972 | [442503](https://inferencex.semianalysis.com/inference/agentic/442503) |
| DeepSeek-V4-Pro | 8× GB200；Dynamo + SGLang | 2026-10-02 | 0.49 / 2.15 / 2.57 | 304K / 478K / 512K | 0.984 | [443959](https://inferencex.semianalysis.com/inference/agentic/443959) |
| DeepSeek-V4-Pro | 8× H200；Dynamo + SGLang；FP8 | 2026-09-16 | 0.92 / 2.75 / 4.68 | 231K / 413K / 441K | 0.976 | [442203](https://inferencex.semianalysis.com/inference/agentic/442203) |
| GLM-5.2 | 8× B200；Dynamo + SGLang；FP4；HiCache | 2026-10-02 | 0.37 / 1.03 / 1.67 | 309K / 490K / 521K | 0.980 | [443969](https://inferencex.semianalysis.com/inference/agentic/443969) |
| GLM-5.2 | 8× MI355X；SGLang；FP4 | 2026-10-03 | 1.03 / 1.86 / 2.84 | 333K / 530K / 558K | 0.978 | [444064](https://inferencex.semianalysis.com/inference/agentic/444064) |
| Kimi K3 | 8× GB300；Dynamo + vLLM | 2026-09-15 | 0.74 / 1.49 / 2.28 | 290K / 440K / 475K | 0.972 | [442102](https://inferencex.semianalysis.com/inference/agentic/442102) |
| Kimi K3 | 16× B200；Dynamo + vLLM | 2026-10-02 | 0.85 / 1.91 / 2.66 | 228K / 410K / 441K | 0.964 | [443880](https://inferencex.semianalysis.com/inference/agentic/443880) |
| Kimi K3 | 32× H200；vLLM | 2026-09-13 | 3.73 / 5.41 / 5.86 | 330K / 342K / 343K | 0.899 | [441866](https://inferencex.semianalysis.com/inference/agentic/441866) |

**表 7-7 TTFT 與實際達到的命中率**（InferenceX AgentX 全部併發；儲存格為各列 p50 / p90 / p95 TTFT 的中位數，單位 s；各列為等級 A，分桶與取中位為 D。總命中率 = GPU 命中 + max(external, CPU) 命中；命中率回報為 0 的列視為未回報而排除。）

| 模型 | 命中率 ≥ 0.9 | 0.7–0.9 | 0.3–0.7 | < 0.3 |
|---|---|---|---|---|
| Kimi K3 | n = 50：1.00 / 2.43 / 3.84 | n = 10：3.16 / 6.63 / 9.26 | n = 31：9.63 / 125.06 / 206.13 | 查無 |
| GLM-5.2 / 5.3 | n = 74：0.56 / 1.65 / 2.23 | n = 8：3.71 / 17.52 / 29.76 | n = 1：7.03 / 204.44 / 215.43 | n = 2：153.68 / 526.17 / 599.51 |
| DeepSeek-V4-Pro | n = 141：1.07 / 3.97 / 7.84 | n = 2：2.68 / 42.51 / 70.76 | n = 6：5.30 / 12.86 / 16.36 | n = 1：172.84 / 233.41 / 244.76 |
| DeepSeek-V4.1-Flash | n = 181：0.50 / 1.45 / 2.02 | n = 12：2.38 / 37.38 / 59.30 | n = 9：10.87 / 153.62 / 339.06 | n = 17：420.49 / 1,670.77 / 1,687.08 |
| Qwen3.5-397B（≤ 256K） | n = 125：0.58 / 1.33 / 1.74 | n = 100：1.06 / 3.98 / 5.61 | n = 7：11.53 / 42.44 / 48.38 | n = 9：64.57 / 91.44 / 100.05 |
| 全部模型 | n = 588：0.63 / 1.71 / 2.46 | n = 134：1.40 / 4.82 / 6.90 | n = 54：9.50 / 96.01 / 146.52 | n = 29：127.97 / 592.25 / 615.05 |

來源：[InferenceX API，Kimi-K3](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Kimi-K3)、[GLM-5.2](https://inferencex.semianalysis.com/api/v1/benchmarks?model=GLM-5.2)、[DeepSeek-V4-Pro](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4-Pro)、[DeepSeek-V4.1-Flash](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4.1-Flash)、[Qwen-3.5-397B-A17B](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Qwen-3.5-397B-A17B)、[Qwen3.8-Flash-Next](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Qwen3.8-Flash-Next)（只計入「全部模型」列），2026-10-05 重抓並重算。

- warm turn 為何低於 1 s（D）：Kimi 的論文寫 1M context 的 coding turn 典型是 400K 的 prefix 加 4K 的增量 [arXiv 2607.24653](https://arxiv.org/abs/2607.24653)；以每個 8-GPU endpoint 約 24,027 tokens/s 計，4,000 ÷ 24,027 ≈ 0.17 s，對上併發 1 時量到的 0.17–0.5 s。
- 同一套硬體在命中率 ≥ 0.9 與 < 0.3 之間的中位 TTFT 相差約 200 倍（D：127.97 ÷ 0.63）。InferenceX 自己的尺度是 agentic 服務的 p90 TTFT 應在 0.2–5 s，超過 5–10 s 就不算線上推論 [A] [InferenceX AgentX](https://inferencex.semianalysis.com/blog/agentx-inferencexv3-does-cuda-moat)。
- 一條 cold 的 1M 請求在所有已公布的配置都超出互動延遲（最快 43.7 s，且是 32 顆 GPU 只服務一條請求）；長 context 的互動服務靠的是 cache 重用，不是 prefill 速度。
- decode 速度到 512K 幾乎不受 context 長度影響：DeepSeek-V4-Pro 在 H20 上不開 speculative decoding 的 TPOT 為 8K 的 26.39 ms 與 1M 的 26.42 ms（PP2-TP8）；單節點 TP8、batch 1 的輸出速度在 8K / 128K / 256K / 512K 為 260 / 267 / 271 / 254 tokens/s，1M 降到 183 [B，2026-08-19] [LMSYS / Ant Group](https://www.lmsys.org/blog/2026-08-19-deepseek-v4-pro-engine-optimization-h20/)。代管端點由 10K 到 100K 會掉 0–40% 的輸出速度 [A] [AA Kimi K3](https://artificialanalysis.ai/models/kimi-k3/providers)。

### 機隊層級：hot 與 warm KV

第 10 章的容量模型把 KV 分成 hot（99.9% 在途請求的 context，必須在 HBM）與 warm（為了下一輪命中 cache 而保留的 session，取在途數的 16 倍、每個 session 常駐 1.2 倍平均 context）。下表引用模型輸出（D），情境為 100,000 名員工、組合 B（製造業）、base、MX3（全部走開源模型）；模型本身未更動。

**表 7-8 容量模型的 hot / warm KV**（來源：`calc/out/model_mix.md`；最右欄為 D：hot KV ÷ 在途數。）

| 模型池 | 99.9% 在途請求數 | hot KV | warm KV | 每個在途請求的 hot KV |
|---|---|---|---|---|
| GLM-5.3 | 192 | 794 GB | 12.2 TB | 4.14 GB |
| Kimi K3 | 402 | 685 GB | 10.8 TB | 1.70 GB |
| DeepSeek V4-Pro | 747 | 23.2 GB | 0.4 TB | 0.031 GB |
| DeepSeek V4.1-Flash | 107 | 0.37 GB | 0.01 TB | 0.003 GB |

- GLM-5.3 與 Kimi K3 兩個池承接 coding 流量，模型內的平均 context 約 92K tokens（D：4.14 GB ÷ 44.9 KB；(1.70 GB − 0.434 GB) ÷ 13.8 KB）。hot KV 隨平均 context 放大（第 10 章的式子：在途數 × (n × b + b_s)）：平均拉到 200K 與 1M 時，GLM-5.3 池為 2.2 倍與 11.4 倍（D：200,000 ÷ 92,000；1,048,576 ÷ 92,000），Kimi K3 池因為有固定 state 為 1.9 倍與 8.7 倍（D：(n × 13.8 KB + 0.434 GB) ÷ 1.70 GB）。
- 同一情境下 GLM-5.3 池的 warm KV 是 hot 的 15 倍（12.2 TB ÷ 794 GB），這一層放在 DRAM 或共享 KV 層；沒有這一層的後果見下一節的 thrash 數據。

## 各晶片在 200K / 1M 的可行性與限制

公開且可重現的 1M-token 開源模型服務只出現在 NVIDIA 與 AMD 的 GPU 上，最少 8 顆 H100 或單張 96 GB 的 Blackwell 卡（視模型而定）。ASIC 路徑的公開上限低得多：Cerebras 公開雲與 Trainium 文件記載的配置約 131K、LPX 唯一的量測在 100K、Google 公開的 TPU repository 內最大值為 40,960–98,304 tokens（LLM recipe 多為 9,216）；Gemini（TPU）與 Claude（部分在 Trainium）雖以 1M 視窗販售，服務這些請求的硬體與技術未揭露。

**表 7-9 各加速器的長 context 判定**（判定詞：可行 = 有公開可重現的 recipe 或量測在該長度運作；有條件 = 只在特定模型、引擎或佈局下成立；不可行 = 公開端點或文件明訂的上限低於該長度，或公開測試在更短的長度就失敗；查無 = 查無公開資料，不代表做不到。判定為本文依「依據」欄所下。）

| 加速器 | 已示範或文件記載的最大 context | 綁住上限的資源 | 200K 判定 | 1M 判定 | 依據 |
|---|---|---|---|---|---|
| AWS Trainium2 / Trainium3（公開 Neuron 工具鏈：vLLM-Neuron，Beta） | disaggregated serving「typically」把 `max_model_len` 設為 131,072；segmented prefill「tested up to 128K」；NKI attention kernel 的最大序列由 36,864 提高到 131,072；AWS 的 gpt-oss recipe 用 16,384（NxDI 的 Llama 教學 12,800）；Bedrock latency-optimized 的 Llama 3.1 405B 上限 11K total tokens；社群移植在 1,024（DeepSeek-V3）與 8K（MiniMax-M3）即失敗 | 編譯期靜態 shape：KV 大小寫進 NEFF，太大會被 compiler 拒絕；scheduler 以 `total_kv_tokens // self.max_model_len` 准入；不支援 preemption；KV 預設上限為記憶體預算的 30%；HBM 以 bank 為單位（Trainium2 每顆 96 GiB 分四個 24 GB bank；Trainium3 每顆 144 GiB）；無 KV offload；不支援 MLA | 查無（文件記載的設定與 kernel 上限停在 131,072） | 查無 | [C] 編譯 context 超過 131,072 的紀錄、12,800 input tokens 以上的 TTFT 或吞吐量：查無公開資料。[Neuron What's New](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/whats-new.html)、[scheduler design](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/design/vllm/neuron-scheduler.html)、[context-length bucketing](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/design/vllm/decode-context-length-bucketing.html)、[features guide](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/guides/features-guide.html)、[NxDI contrib MiniMax-M3](https://github.com/aws-neuron/neuronx-distributed-inference/blob/main/contrib/models/MiniMax-M3/README.md)、[vLLM Neuron README](https://github.com/vllm-project/vllm-neuron/blob/release-0.24.0.1.1.0/README.md) |
| AWS Trainium（Bedrock 上的 Claude 與 Kimi K3） | Claude 的 1M context 自 2026-03-13 在 Bedrock GA；Kimi K3 在 Bedrock 為 1M（2026-09-18 GA）；AWS 把 Trn3 定位在「long contexts over 1M tokens」 | 未揭露；AWS 自己寫 Trn3 UltraServer 的 20.7 TB「overflows when you hit high concurrency with long contexts」 | 查無 | 查無 | [C] 沒有任何來源說 200K 或 1M 的請求由 Trainium 服務。[Claude 1M GA](https://claude.com/blog/1m-context-ga)、[AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/introducing-kimi-k3-on-amazon-bedrock/)、[AWS EC2 Trn3](https://aws.amazon.com/ec2/instance-types/trn3/)、[AWS Storage Blog](https://aws.amazon.com/blogs/storage/accelerate-inference-with-kv-cache-tiering-on-aws/) |
| AWS Inferentia2 | inf2.24xlarge（6 晶片、TP8、11B 模型）編譯並服務 32,768 tokens，65,536 編譯成功但無法啟動 [A，2025-09-30]；inf2.48xlarge 以 8B 模型跑 16,512 [B，2025-05-27] | 每晶片 32 GB（每 core 16 GB）；權重加 KV 必須小於 TP 數 × 16 GB；TP 只允許 1、2、4、8、24 | 不可行 | 不可行 | [Exawizards](https://zenn.dev/exwzd/articles/20250930-inferentia-llama)、[AWS Builder Center](https://builder.aws.com/content/2zruvftx03ZtQFFxyur6kdzfwMv/benchmarking-llm-inference-with-optimum-neuron-on-inferentia2)、[NxDI feature guide](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/developer_guides/feature-guide.html) |
| Google TPU（公開 recipe：vLLM-TPU、SGLang-JAX） | Ironwood 的 LLM recipe 的 `--max-model-len` 多為 9,216（Qwen3-Coder-480B 為 10,240；另有 Gemma 4 的 1,524 與 Qwen3-Embedding-8B 的 16,384）；repo 內最大值為 CI 的 40,960（Qwen3.8-2.4T）、KV offload 範例的 51,200、多模態 benchmark script 的 98,304；SGLang-JAX 為 32,768，並寫明 Qwen3.8-27B 的原生 262,144「has not been exercised end to end」；InferenceX 的 TPU 結果只有 8K in / 1K out | 沒有文件記載的硬上限，上限是已建置並測過的範圍；每晶片 HBM（v6e 32 GB、TPU7x 192 GiB）；靜態 shape 與 bucket 預編譯；KV offload 只到 host DRAM | 查無 | 查無 | [B / C] [vLLM TPU repo](https://github.com/vllm-project/tpu-inference)、[tpu-recipes](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/ironwood/vLLM)、[SGLang-JAX cookbook](https://github.com/sgl-project/sglang-jax/tree/main/docs/cookbook/autoregressive)、[InferenceX TPU](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam)、[TPU7x doc](https://docs.cloud.google.com/tpu/docs/tpu7x) |
| Google TPU（Gemini，first-party） | Gemini 3.8 Flash、3.1 Pro、3.5 Flash-Lite 的輸入上限 1,048,576、輸出 65,536；Gemini 4 Argon 的輸出上限為 1M（2026-09-30 宣布，先向 Fairwind Program 推出；輸入上限未載明） | 未揭露；TPU 8i（已宣布，「generally available later this year」）為 288 GB HBM 加 384 MB 晶片內 SRAM，後者「sized for the KV cache footprint」 | 可行（僅 first-party） | 可行（僅 first-party） | [C] 技術與 TPU 世代未揭露；Google 內部「for ages」使用 PD disaggregation。[Gemini long-context guide](https://ai.google.dev/gemini-api/docs/long-context)、[Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)、[The Decoder](https://the-decoder.com/google-gemini-4-argon-closes-the-gap-with-openai-and-anthropic-but-doesnt-take-a-clear-lead/)、[TPU 8 deep dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive)、[Google TPU 8](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/eighth-generation-tpu-agentic-era/)、[InferenceX TPU](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam) |
| NVIDIA Hopper（H100 80 GB、H200 141 GB、H20 96 GB；8 顆 640 / 1,128 GB） | 1M：DeepSeek-V4.1-Flash 在 8× H100（KV pool 7,022,899 tokens，等於 6.70 條 1M 請求）[A]；DeepSeek-V4-Pro 在 H20 跑 1M，單節點 TP8 只夠 batch 1 [B]；GLM-5.3 在 8× H200 要靠 HiSparse 才到 1M [B]；vLLM recipe 的 V4-Pro Hopper 設定內部不一致：說明文字寫上限 800K，YAML 參數是 `--max-model-len 200000` [B] | TP 下每顆 GPU 的 HBM；1M 時 indexer buffer 把 80 GB 卡的 prefill chunk 壓到 4,096；Kimi K3 要 32 顆 H200 且每使用者約 5 tokens/s | 可行 | 有條件（依模型） | [perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)、[LMSYS / Ant Group](https://www.lmsys.org/blog/2026-08-19-deepseek-v4-pro-engine-optimization-h20/)、[vLLM HiSparse](https://vllm.ai/blog/2026-09-08-glm53-part1-hybrid-sparse-offloading)、[vLLM recipe DeepSeek-V4-Pro](https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4-Pro.yaml)、[InferenceX Kimi K3 2026-08-25](https://inferencex.semianalysis.com/blog/kimi-k3-agentx-mi355x-atom-vs-gb300-nvl72) |
| NVIDIA Blackwell（B200 180 GB、B300 270 GB、GB200 內 186 GB、GB300 內約 278 GB；NVL72 機櫃 13.4 TB / 約 20 TB） | 1M：GLM-5.3 在 8× B200 達到完整 1M（FP8 KV、`--max-num-seqs 32`）[B]；Kimi K3 在 8× B300 TP8 可放 3.1 條滿長度請求 [A]；DeepSeek-V4-Pro 在 8× B300 的 working set 約 43M tokens [A]；Qwen3.8-27B 在單張 96 GB RTX PRO 6000 跑 1M，常駐 1–2 條 [B]；單顆 GB300 加 CPU weight offload 的 GLM-5.3 上限 262K、8 條序列 [B] | TP 下每顆 GPU 的 HBM；KV pool 在啟動時定大小，單條 1M 請求超過 pool 就拒絕啟動（MiniMax-M3 在 2× B200：pool 31.72 GiB、需要 37.62 GiB，上限 883,840 tokens）[A] | 可行 | 可行（併發由 KV pool 決定） | [vLLM recipe GLM-5.3](https://github.com/vllm-project/recipes/blob/main/models/zai-org/GLM-5.3.yaml)、[perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)、[InferenceX 2026-08-25](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-b200-vs-b300-kv-working-set)、[LMSYS 2026-09-16](https://www.lmsys.org/blog/2026-09-16-nvfp4-kv-cache/)、[CoreWeave pricing](https://www.coreweave.com/pricing)、[GB200 NVL72](https://www.nvidia.com/en-us/data-center/gb200-nvl72/)、[GB300 NVL72](https://www.nvidia.com/en-us/data-center/gb300-nvl72/) |
| NVIDIA Vera Rubin NVL72（Rubin 288 GB HBM4；機櫃 20.7 TB；CoreWeave 自 2026-09-30 limited availability） | AgentX trace（DeepSeek-V4-Pro，請求長度 p50 88K / p95 404K / p99 675K）有 pre-release TensorRT-LLM、NVFP4 的結果 [A，2026-09-14]；固定 1M 長度的量測查無。NVIDIA 把 Vera Rubin 加 LPX 定位為「trillion-parameter models and million-token context」[C] | 每顆 GPU 的 HBM | 可行（pre-release 軟體） | 查無 | [InferenceX 2026-09-14](https://inferencex.semianalysis.com/blog/vera-rubin-nvl72-agentic-inference)、[Vera Rubin NVL72](https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/)、[CoreWeave](https://www.coreweave.com/blog/cognition-becomes-first-customer-for-nvidia-vera-rubin-nvl72-on-coreweave-cloud)、[NVIDIA press](https://nvidianews.nvidia.com/news/nvidia-vera-rubin-platform) |
| NVIDIA Rubin CPX（prefill 專用 GPU；已宣布未出貨） | 無。2025 年宣布時為 128 GB GDDR7、30 PFLOPS NVFP4，鎖定長 context 的 prefill；GTC 2026（2026-03）起不在 2026 平台內，位置由 Groq 3 LPX 取代，NVIDIA 未正式宣布取消；Hot Chips（2026-08-26）的說法是撤下 CPX 以便當年出貨 LPU | 不適用。回歸時程兩說，均未經 NVIDIA 證實：約 2028 年隨 Feynman（Wccftech 轉述 Ian Buck）；2027 Q1 量產、改用 168 GB HBM4、2,300 W、64–256 顆的獨立機櫃（RCR Tech 轉述分析師 Ming-Chi Kuo，2026-09-02） | 查無 | 查無 | [C / 分析師] [Glenn Lockwood](https://www.glennklockwood.com/garden/processors/rubin-cpx)、[Tom's Hardware 2026-03-19](https://www.tomshardware.com/tech-industry/semiconductors/nvidias-20-billion-groq-deal-produces-its-first-chip)、[Tom's Hardware 2026-08-26](https://www.tomshardware.com/tech-industry/semiconductors/nvidia-presents-groq-3-lpx-architecture-and-unveils-its-first-third-party-inference-benchmark)、[Wccftech](https://wccftech.com/nvidia-rubin-cpx-is-off-the-roadmap-but-may-return-with-feynman-in-2028/)、[RCR Tech](https://rcrtech.com/semiconductor-news/nvidia-reportedly-revives-rubin-cpx/) |
| NVIDIA CMX（BlueField-4 的 context 儲存層，不是加速器；已宣布未出貨） | 沒有任何長 context 的量測。定位為 G3.5：以 Ethernet 連接的 flash 層，「petabytes of shared capacity per GPU pod」，decode 前把 KV block 預先載入 host 或 GPU 記憶體 | 夥伴產品「second half of 2026」；延遲與頻寬數字未公布 | 查無 | 查無 | [C] 宣稱 tokens/s 與能效各「up to 5x」於傳統儲存，無方法。[NVIDIA developer blog](https://developer.nvidia.com/blog/introducing-nvidia-bluefield-4-powered-inference-context-memory-storage-platform-for-the-next-frontier-of-ai/)、[NVIDIA press](https://nvidianews.nvidia.com/news/nvidia-bluefield-4-powers-new-class-of-ai-native-storage-infrastructure-for-the-next-frontier-of-ai)、[CMX](https://www.nvidia.com/en-us/data-center/ai-storage/cmx/) |
| AMD Instinct（MI300X 192 GB、MI325X 256 GB、MI355X 288 GB、MI455X 432 GB；Helios 機櫃 31 TB） | Kimi K3 在 MI355X 以 `--max-model-len 1048576` 上線（FP8 KV、DCP8、高併發時加 host offload）；GLM-5.3 以 TileRT 在 2 × 8 顆 MI350 系列上跑 1,048,576（perf-changelog 的設定鍵寫 MI355X，量測註記寫「2x8 MI350X」；僅併發 1）[A]；GLM-5.3 在 8× MI325X 設為 524,288 [B]；DeepSeek-V4-Pro 在 8× MI355X TP8 的 KV pool 8,524,228 tokens [B] | 每顆 GPU 的 HBM；DeepSeek-V4.1-Flash 在 2× MI300X 不可行（可用 KV 記憶體 −13.51 GiB）[A]；kernel library（AITER）在 2026 年才補上 64-bit offset 與 131K 以上 prompt 的修正；host offload 要 ROCm 7.14 才有效率；HiSparse 只支援 NVIDIA | 可行 | 有條件（MI355X 已示範；MI455X 與 Helios 查無量測） | [vLLM recipe Kimi-K3](https://github.com/vllm-project/recipes/blob/main/models/moonshotai/Kimi-K3.yaml)、[vLLM recipe GLM-5.3](https://github.com/vllm-project/recipes/blob/main/models/zai-org/GLM-5.3.yaml)、[InferenceX AgentX](https://inferencex.semianalysis.com/blog/agentx-inferencexv3-does-cuda-moat)、[perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)、[AMD MI400](https://www.amd.com/en/products/accelerators/instinct/mi400.html) |
| Cerebras（WSE-3 / CS-3；CS-4 於 2026-08-18 宣布） | 公開雲：gpt-oss-120b 65K（free）/ 131K（paid）；Qwen 3.8 27B 64K / 128K（131,072）；GPT-5.3-Codex-Spark 128K；2025-07 才由 32K 提高到 131K | 每片 wafer 44 GB SRAM（CS-4 每機櫃 132 GB），權重與 KV 共用；KV cache 不量化；每套系統另有 6 TB DDR5 的 KVSS 節點，經 150–300 GB/s 的連線（分析師） | 不可行（公開端點；Dedicated 的上限查無） | 不可行（公開端點） | [C / 分析師] 分析師估算 1.6T 模型在 1M context 約需 20 套系統、256 併發約 40 套、超過 $20M、約 1 MW，並預期客戶跑 256K。[Cerebras models](https://inference-docs.cerebras.ai/models/overview)、[131K press release](https://www.cerebras.ai/press-release/cerebras-launches-qwen3-235b-world-s-fastest-frontier-ai-model-with-full-131k-context-support)、[SemiAnalysis CS-3](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please)、[SemiAnalysis CS-4](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast) |
| NVIDIA Groq 3 LPX（參考） | 100K input tokens：Artificial Analysis 量到 Gemma 4 31B 為 3,431 output tokens/s [A，2026-08-24]，沒有 TTFT；「multi-hundred thousands of tokens」是 NVIDIA 的預期 [C] | 每機櫃 128 GB SRAM（256 顆 LP30）加 12 TB DDR5；SRAM 放不下兆級權重與長 KV，需要 GPU prefill 並「once per turn」交接 KV，或在 attention–FFN 模式讓 KV 留在 NVL72 | 查無 | 查無 | [NVIDIA developer blog](https://developer.nvidia.com/blog/how-nvidia-groq-3-lpx-unlocks-ultrafast-interactivity-at-long-context-on-nvidia-vera-rubin/)、[NVIDIA LPX](https://www.nvidia.com/en-us/data-center/lpx/) |

- **判定依據的性質不同。** GPU 各列的「可行」來自獨立量測（InferenceX）與可重現的 vLLM / SGLang recipe；TPU first-party 的「可行」只有產品規格，客戶無法用公開工具鏈重現；所有「查無」都是沒有公開資料，其中 Trainium 與 TPU 的廠商各自宣稱或實際販售 1M 視窗。
- **綁住上限的資源各不相同。** Neuron 是編譯期的靜態 shape 與 24 GB bank，Cerebras 是每片 wafer 44 GB 的 SRAM，LPX 是每機櫃 128 GB 的 SRAM，GPU 是每顆的 HBM。Trainium 把編譯 context 由 131,072 提高到 1,048,576 時，同一份 KV 預算可准入的併發降為 1 / 8（D：`total_kv_tokens // max_model_len`，1,048,576 ÷ 131,072 = 8），除非啟用 decode context-length buckets；一條 1M 的 gpt-oss-120b BF16 序列（72.0 GiB）是單一 24 GB bank 的 3 倍（D），必須靠 DCP 把 KV 沿序列維度切到多個 rank。
- **ASIC decode 的長 context 實際上落在配對的記憶體層。** Cerebras 與 LPX 的上限是 SRAM 容量造成的，兩家的路線都是改由 GPU 或 Trainium 做 prefill、把 KV 放在外部記憶體。AWS 與 Cerebras 的 disaggregated 服務（Trainium prefill、Cerebras decode）於 2026-03-13 宣布，尚未上線，Cerebras 的說法是 2027 Q1 [C] [About Amazon](https://www.aboutamazon.com/news/aws/aws-cerebras-ai-inference)、[Cerebras Q2 2026](https://www.sec.gov/Archives/edgar/data/2021728/000162828026056186/cbrsannouncesfinancialresu.htm)。TPU 的公開上限低則反映開放工具鏈尚未驗證，不是硬體限制（D，推論）。

## 各推論技術在長上下文下有效或失效

讓長 context 可服務的是 prefix caching 加 cache-affine routing（命中率 ≥ 0.9 時全部模型的中位 TTFT 為 0.63 s，各模型 0.50–1.07 s），而讓它在 session 總量超過 HBM 之後仍成立的是 host DRAM 或共享 KV 層（Kimi K3 在 8× B300：TTFT p50 0.85 s 對 86 s）。在 1M 會失效的是不加 DCP / DEP 的 tensor parallel（MLA 模型）與沒有 admission control 的高併發 continuous batching；3 bit 以下的 KV 量化在 128K–256K 就相對退化約 30%；speculative decoding 對 TTFT 沒有幫助。

**表 7-10 各技術在 200K 與 1M 的效果**（判定詞：有效 = 有可量測的增益；有條件 = 只在註明條件下有增益；中性 = 對所述指標沒有影響；失效 = 不再運作或變成有害。判定為本文依證據欄所下（D），證據欄的數字各自標等級。）

| 技術 | 在 200K | 在 1M | 證據 |
|---|---|---|---|
| automatic prefix caching（命中率、eviction、thrash） | 有效：命中時 p50 TTFT ≤ 1 s，cold 為 10–29 s | 有效，且是必要條件：0.2–1 s 對 cold 的 44–1,144 s；resident KV 用完時驟然失效 | 可重用比例：agentic coding 的 turn 有 96% 重用 ≥ 90% 的輸入（中位 99.6%）[B] [llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)；InferenceX trace 的理論命中上限 0.96–0.976 [A]。thrash：GLM-5.2 在 B300（SGLang）併發超過 8（TP8）或 64（DP8）後命中率由約 0.97 掉到 0.04–0.06；Kimi K3 在 8× B300 併發 16 / 24、無 DRAM offload 時命中率 2.7%、TTFT p50 86 s / 191 s [A] [perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)。eviction：vLLM selective retention 在 14 條併發、context 最高 1M 下維持 > 95% 命中；AMD ATOM 的 sparse checkpoint retention 把命中率由 5.6% 拉到 96.45%（併發 48）[A，評論] [InferenceX AgentX](https://inferencex.semianalysis.com/blog/agentx-inferencexv3-does-cuda-moat)；SGLang session-aware eviction 比 LRU 降低 TTFT 2.9–16.6% [B] [LMSYS 2026-08-11](https://www.lmsys.org/blog/2026-08-11-unified-radix-cache/)。被 preempt 的長請求「pays its full TTFT again on every eviction」[B] [vLLM HiSparse](https://vllm.ai/blog/2026-09-08-glm53-part1-hybrid-sparse-offloading) |
| KV offload 到 host DRAM | 有效（session 總量超過 HBM 時）；全部放得進 HBM 時中性 | 有條件：對閒置或被逐出的 session 有效；dense attention 的執行中請求必須整條留在 GPU；DRAM 需為 HBM KV 容量的 1.5–3 倍 | Kimi K3 在 8× B300 併發 16：TTFT p50 0.85 s 對 GPU-only 的 86 s，輸出 245.0 對 49.6 tokens/s [A] [perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)。GLM-5.2：每次 miss 的 restore 59 ms（22.7 GB/s）；暫停中的 conversation restore 中位 8.4 s 對重算 14.8 s；400 個 conversation 時中位 TTFT 22.2 s 對 124.5 s [B] [llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)。DeepSeek-V4-Pro 在 8× B200 併發 196：HBM 命中 73% 加 DRAM 近 20% [A] [InferenceX 2026-08-25](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-b200-vs-b300-kv-working-set)。offload ÷ 重算的時間比在 H20 為 0.60，在 H800 為 1.08–1.87（比重算慢）[A] [arXiv 2609.33762](https://arxiv.org/abs/2609.33762) |
| KV offload 到 NVMe / flash 層（本機 NVMe、檔案系統、物件儲存；CMX；儲存廠商產品） | 有條件：prompt 超過約 8K–32K 且讀取頻寬 ≥ 約 3.5–10 GB/s 時有效；短 prompt 的 TTFT 會變差 | 有條件：GLM 級一個 session 約 47 GB，需要每秒數 GB 到數十 GB 的路徑，比重算慢的層應繞過。CMX 與 VAST、DDN、Pure、NetApp、Dell、HPE 的產品：查無量測 | NVMe 持續讀取 13.5 GB/s；8K prompt 要 77.8% 的 prefix 重用才打平、80K 只要 7.8%；所需儲存頻寬由 1K 的 23.2 GB/s 降到 80K 的 3.5 GB/s；低於約 8K tokens 沒有儲存裝置贏過重算 [A] [arXiv 2609.11744](https://arxiv.org/abs/2609.11744)。GKE（Llama-3.3-70B、8× H100、LMCache）：100K prompt 的 TTFT −79%、吞吐量 +264%，但 10K prompt 在大 cache 下 TTFT +121% [B，2025-11-07] [Google Cloud](https://cloud.google.com/blog/topics/developers-practitioners/boosting-llm-performance-with-tiered-kv-cache-on-google-kubernetes-engine)。SGLang HiCache L3 在 DeepSeek-V4-Flash：命中率近 98%，有效輸入 145.5K tokens/s 對 GPU-only 的 9.4K [B] [LMSYS 2026-08-11](https://www.lmsys.org/blog/2026-08-11-unified-radix-cache/)。CMX：「up to 5x」tokens/s 與能效，無方法 [C] [NVIDIA developer blog](https://developer.nvidia.com/blog/introducing-nvidia-bluefield-4-powered-inference-context-memory-storage-platform-for-the-next-frontier-of-ai/) |
| 共享 / 遠端 KV store（Mooncake、PegaFlow、WEKA、P2P、HiCache L3） | 有效：跨 replica 與 PD pool 找回 cache affinity | 有效，是多節點與 PD 部署的必要條件；網路要 100–200 GB/s 等級 | Nebius + WEKA（DeepSeek-V4-Pro NVFP4、64× B300、512 個 session、最長 1M、8 小時）：命中率 93% 對 40%，中位 TTFT 1.05 s 對 5.68 s，p95 3.82 s 對 23.12 s，每 GPU-hour 輸出 169,000 對 46,000 tokens [B，2026-09-24] [Nebius](https://nebius.com/blog/posts/nebius-weka-shared-kv-cache-benchmark-hgx-b300)。Mooncake Store 加 PD（12× GB200、Codex trace）：命中率 1.7% → 92.2%、吞吐量 3.8 倍 [B，2026-05-06] [vLLM Mooncake Store](https://vllm.ai/blog/2026-05-06-mooncake-store)。PegaFlow：8 × 400 Gbps NIC 的遠端讀取平均 194 GB/s，24 GiB 的 KV 段約 100 ms [B] [vLLM PegaFlow](https://vllm.ai/blog/2026-05-18-pegaflow)。SGLang HiCache 的 prefetch 逾時為 2 s 加每 1,024 tokens 0.1 s、上限 30 s，約 287K tokens 就到上限（D：(30 − 2) ÷ 0.1 × 1,024）[HiCache design](https://docs.sglang.io/docs/advanced_features/hicache_design.md) |
| prefix-aware / cache-affine routing | 有效 | 有效（與 prefix caching 一起才成立） | precise prefix-cache scorer 的 P90 TTFT 0.542 s，approximate 為 31.083 s、random 為 92.551 s（16× H100、Qwen 32B 級）[B，2025-09-24] [llm-d KV cache](https://llm-d.ai/blog/kvcache-wins-you-can-see)。「sticky until saturated」維持 round-robin 2–3 倍的吞吐量 [B] [llm-d 2026-08-17](https://llm-d.ai/blog/sticky-until-saturated-token-aware-routing)。DP attention 會把 cache 困在錯的 rank：MiniMax M3 命中 28.8%，理論上限 96.0% [A] [InferenceX AgentX](https://inferencex.semianalysis.com/blog/agentx-inferencexv3-does-cuda-moat)。同一模型在不同代管商的命中率差異：Kimi K3 為 68%–100% [A] [AA Kimi K3](https://artificialanalysis.ai/models/kimi-k3/providers) |
| chunked prefill | 有效：搭配 pipeline overlap 降 TTFT，也是公平性的手段 | 有條件：必要，但 chunk 被記憶體壓到 4,096–8,192，小 chunk 的額外負擔浮現 | GB300 上 128K 的 TTFT：chunked prefill 加 pipeline overlap −30–45%，dynamic chunking 再 −8–17% [B] [LMSYS / NVIDIA](https://www.lmsys.org/blog/2026-02-19-gb300-longctx/)。DeepSeek-V4.1-Flash 的 indexer logits buffer 為 `[max-num-batched-tokens, max-model-len]`：8,192 × 1M × 2 B = 16 GiB，80 GB 的 H100 在 1M 要把 chunk 限在 4,096 [B] [vLLM recipe DeepSeek-V4.1-Flash](https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4.1-Flash.yaml)。`--long-prefill-token-threshold 512` 在 B300 最高換到 +93% 的 total tokens per GPU-second，代價是長請求的 TTFT 變高 [B] [vLLM AgentX](https://vllm.ai/blog/2026-09-08-vllm-agentx)。1M 下 chunk 大小對 TTFT 的掃描：查無公開資料 |
| pipeline / context-parallel prefill（PP、PCP） | 有效：cold TTFT −26–45% | 有效，是 cold TTFT 唯一的槓桿（GPU 加倍，79.2 s → 43.7 s）；對 warm turn 中性 | H20 上 PP4 對 PP2 在 128K / 256K / 512K / 1M 降低 TTFT 26.2% / 33.3% / 42.1% / 44.8% [B] [LMSYS / Ant Group](https://www.lmsys.org/blog/2026-08-19-deepseek-v4-pro-engine-optimization-h20/)。PCP8 在 32K prompt 比 TP8 快 2.65 倍；「PP … does not fit warm agentic turns」[B] [vLLM AgentX](https://vllm.ai/blog/2026-09-08-vllm-agentx) |
| tensor parallel（MLA 模型，不加 DCP / DEP） | 有條件：可運作，但 latent KV 每個 rank 各存一份 | 失效：TP8 節點放不下一條 1M 的 GLM-5.2 session | GLM-5.2 在 8× H200 TP8 的 KV 容量 598K tokens，低於 1,048,576（表 7-2）[B] [llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d) |
| decode context parallelism（DCP） | 有效：KV 容量約 3–10 倍，inter-token latency 約 1.8 倍 | 有條件：GQA 模型上限為 `tp // num_key_value_heads`；vLLM 的 K3 配置不與 DSpark 併用；SGLang 的 HiCache L3 會丟掉 DCP 旗標 | Kimi K2.6 NVFP4 在 8× B200：TP 在併發 64 時 KV 用量 100%、每 GPU 約 1,863 tokens/s 停滯，DCP 在併發 512 達 6,091、KV 用量 82% [B，2026-08-07] [vLLM DCP](https://vllm.ai/blog/2026-08-07-decode-context-parallelism)。Kimi K3 容量 1.93M → 19.75M tokens、TPOT p50 13.8 → 10.5 ms [B] [vLLM 2026-09-13](https://vllm.ai/blog/2026-09-13-kimi-k3-performance-optimization)。SGLang「Peak Capacity」preset（加 DCP8）把併發上限提高 72% [B] [SGLang Kimi-K3 cookbook](https://docs.sglang.io/cookbook/autoregressive/Moonshotai/Kimi-K3)。對 DeepSeek V4，DCP「only matched DEP」[B] [vLLM AgentX](https://vllm.ai/blog/2026-09-08-vllm-agentx) |
| prefill/decode disaggregation | 有效：吞吐量與 interactivity；KV 傳輸要 ≥ 數十 GB/s，並需要共享的 prefix store | 有條件：1M 的 KV 可在 1 s 內交接，但 GLM-5.3 級每 rank 要多保留約 99 GiB 的接收 buffer；尾端延遲取決於傳輸路徑 | TileRT 的 GLM-5.3 在 1,048,576 context（硬體在兩份研究筆記中分別記為 MI355X 與 2×8 MI350X，來源同為 perf-changelog）：81 GB 以 751 ms 傳完（device-to-device 108 GB/s；host-to-host 為 20.9 GiB/s）；每 rank 在 90.72 GiB 權重與 93.25 GiB engine cache window 之外再保留 99.06 GiB；併發 1 的 TTFT p50 5.7 s → 2.2 s [A] [perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)。chunked NIXL bounce path 把 KV 傳輸 p99 由 26.74 s 降到 125 ms（併發 5）[A，評論] [InferenceX AgentX](https://inferencex.semianalysis.com/blog/agentx-inferencexv3-does-cuda-moat)。沒有共享 store 的 PD 在 turn 之間會丟掉 prefix cache（1P1D 命中率 1.7%）[B] [vLLM Mooncake Store](https://vllm.ai/blog/2026-05-06-mooncake-store)。Dynamo：沒有 RDMA 時 TTFT 由 355 ms 變成 10 s 以上 [C] [Dynamo docs](https://docs.nvidia.com/dynamo/user-guides/disaggregated-serving) |
| continuous batching（少數請求占掉大部分 KV 時） | 有條件：需要 admission control；以 `max-model-len` 為每條請求保留 KV 的引擎會損失併發 | 失效（沒有 admission control 時）：每節點 batch 1–4，preemption 讓長請求重付整段 TTFT | DeepSeek-V4-Pro 在單節點 8× H20 TP8 於 1M context「has enough KV-cache capacity only for batch size 1」[B] [LMSYS / Ant Group](https://www.lmsys.org/blog/2026-08-19-deepseek-v4-pro-engine-optimization-h20/)。Qwen3.8-2.4T：262,144 時引擎為 25 條請求保留 KV，9,240 時同樣 70 GiB 可服務 506 條 [B] [vLLM recipe Qwen3.8-2.4T](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-2.4T-A95B.yaml)。DeepSeek-V4.1-Flash 在 H100 併發 20–28 是 1M trajectory 開始被 preempt 的範圍 [A] [perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)。廠商的對策：Kimi 用 budget-based admission（請求由 < 2K 到 1M）[C] [arXiv 2607.24653](https://arxiv.org/abs/2607.24653)；DeepSeek API 在請求 10 分鐘內未開始推論時關閉連線 [C] [DeepSeek rate limit](https://api-docs.deepseek.com/quick_start/rate_limit) |
| speculative decoding（MTP、DSpark、EAGLE） | 中性（對 TTFT）；decode 增益不確定 | 中性（對 TTFT）；占用 KV、state 與准入額度，可能降低吞吐量 | 「Time to first token does not improve; MTP speeds decode, not prefill」[B] [llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)。Kimi K3 的 DSpark 在 B300 的 118–230K-token trace 上每步只接受 1.18–1.68 tokens（benchmark 固定值 3.84），併發 4 / 8 的吞吐量下降 20–63% [A] [perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)。反例：同一個 speculator 在 378K-token 的 LongBench-v2 prompt 上最高 5.31 tokens per iteration [B，2026-09-15] [vLLM DSpark](https://vllm.ai/blog/2026-09-15-kimi-k3-dspark)；DeepSeek-V4-Pro 的 DSpark 在 1M 仍為 6.65 ms 對 26.42 ms [B] [LMSYS / Ant Group](https://www.lmsys.org/blog/2026-08-19-deepseek-v4-pro-engine-optimization-h20/)。DSpark 把 K3 在 8× B300 的准入上限由 101 降到 68 條 [B] [SGLang Kimi-K3 cookbook](https://docs.sglang.io/cookbook/autoregressive/Moonshotai/Kimi-K3)。acceptance 隨 context 長度的變化：查無公開資料 |
| KV-cache 量化：FP8、NVFP4 / FP4 | 有效：FP8 容量 2 倍，NVFP4 再 1.78 倍；Hopper 在 100K 以上需要 2026-04 之後的 kernel 修正。3 bit 以下：失效（品質） | 有效：MRCR 回復 94–100%；96 GB 卡上 1M 常駐由 1 條變 2 條。3 bit 以下：1M 未測 | Hopper 的 FP8 kernel 在 contraction 維度 ≥ 100K 時累加精度不足，128K needle 準確率由 91%（BF16）掉到 13%（FP8）；修正後到 1M 的 MRCR 回復 Llama-3.3-70B AUC@128k 的 97–98% [B，2026-04-22] [vLLM FP8 KV](https://vllm.ai/blog/2026-04-22-fp8-kvcache)。NVFP4 KV 為 FP8 儲存量的 56.25%；SWE-bench Verified 76.2% 對 FP8 的 77.8%；AgentX（Qwen3.5-397B、併發 16）命中率 92.35% 對 32.57% [B，2026-09-16] [LMSYS 2026-09-16](https://www.lmsys.org/blog/2026-09-16-nvfp4-kv-cache/)。3-bit TurboQuant 相對退化約 30%，集中在 128K–256K [B] [vLLM TurboQuant](https://vllm.ai/blog/2026-05-11-turboquant) |
| sparse attention 與 hybrid recurrent state（2026 旗艦的架構） | 有效：1M 序列的 KV 由約 84 GiB（V3.2 式 MLA）降到 0.9–14 GiB（DeepSeek V4 / V4.1、Kimi K3），TTFT 隨長度接近線性 | 有條件：瓶頸移位而非消失。indexer 的 key 與 score buffer 隨整個 context 成長且必須留在 GPU；每請求的 recurrent state 限制併發；prefix cache 只能在 checkpoint 邊界重用；GLM-5.x 與 Qwen3.8-2.4T 每條 1M 仍約 44–46 GiB | 1M 時 V4-Pro 的單 token FLOPs 為 V3.2 的 27%、KV 為 10% [C] [arXiv 2606.19348](https://arxiv.org/abs/2606.19348)；IndexShare 在 1M 把 per-token FLOPs 降 2.9 倍 [C] [GLM-5.2](https://huggingface.co/zai-org/GLM-5.2)；QSA 在 1M 的 kernel 層級 prefill 快 7.6 倍、decode 快 4.9 倍 [B] [arXiv 2608.30320](https://arxiv.org/abs/2608.30320)。top-k「typically requires the full context to be in HBM」[A，評論] [InferenceX GLM-5.3](https://inferencex.semianalysis.com/blog/sparse-savings-persistent-demand-inside-glm53)。4:1 壓縮下 1M context 仍有 256K 個候選 [B] [LMSYS DeepSeek V4](https://www.lmsys.org/blog/2026-04-25-deepseek-v4/)；GLM-5.2 的 TopK-V2 把 1M 的選取由 372.1 µs 降到 36.6 µs [B] [LMSYS GLM-5.2](https://www.lmsys.org/blog/2026-07-13-glm52-optimization/)。Kimi 的 prefix 只能在 512-token 邊界重用，vLLM 每 32K tokens 存一次 KDA checkpoint [B] [vLLM 2026-07-27](https://vllm.ai/blog/2026-07-27-k3) |
| sparse-aware offload（HiSparse） | 有效（容量）；低併發時有些微額外負擔 | 有條件：讓 GLM-5.3 在 8× H200 跑到 1M，但還不是吞吐量的增益；只支援 NVIDIA | 只把 top-k 的列留在 GPU（hot buffer = 2 × top-K），「enables running GLM 5.3 at full 1 million context length—previously impossible on this hardware」（8× H200、TP8、FP8 KV、384 GiB HiSparse pool 加 128 GiB offload；預計進 vLLM v0.30）[B，2026-09-08] [vLLM HiSparse](https://vllm.ai/blog/2026-09-08-glm53-part1-hybrid-sparse-offloading)。SGLang：V4-Flash 的 200K in / 20K out 在 2× B200「up to 3x」[B] [LMSYS DeepSeek V4](https://www.lmsys.org/blog/2026-04-25-deepseek-v4/)。InferenceX 的評語是容量與正確性的手段，不是高併發的吞吐量增益 [A，評論] [InferenceX AgentX](https://inferencex.semianalysis.com/blog/agentx-inferencexv3-does-cuda-moat) |
| context compaction / summarisation | 有條件：少用且保留 prefix 時有助成本與品質；改寫歷史時會打掉命中率 | 有條件：當作安全閥（300K–500K 觸發）；每次 compaction 是新 context 的一次 cold prefill | Kimi K3 的 BrowseComp：300K 觸發 compaction 為 91.2%，全 1M 不做管理為 90.4% [C / B] [arXiv 2607.24653](https://arxiv.org/abs/2607.24653)。真實 trace 中 compaction（> 500K → < 30K）占 0.03% 的 turn、prefix reset 占 2.8% [B] [llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)。prefix 命中率：不壓縮 96.50%，recent-event truncation 60.85%、observation masking 50.80%、LLM summarisation 92.15%，三種都拉長每個 instance 的推論時間（Qwen3-Coder-30B、8× RTX 3090）[A] [arXiv 2609.33762](https://arxiv.org/abs/2609.33762) |
| retrieval（RAG）取代長 context | 有條件：避開 KV 與 prefill 的問題，品質取決於檢索 | 有條件：同左 | 只有廠商指引（見「長上下文的品質」一節）；2026 機型上 RAG 對長 context 的成本、延遲或品質比較：查無公開資料 |

### 一條 1M 序列的 KV 有多大、搬一次要多久

**表 7-11 1M 序列的 KV 搬移時間**（等級 D：KV bytes ÷ 頻寬；KV 大小取表 7-1、換算為 GB 並加上固定 state；頻寬為量測值，來源列於表後。）

| 模型（1,048,576 tokens 的 KV） | NVMe 13.5 GB/s | DRAM restore 22.7 GB/s | GPU↔CPU 55 GB/s | device-to-device 108 GB/s | RDMA 194 GB/s | cold 重算 |
|---|---|---|---|---|---|---|
| GLM-5.x FP8（47.1 GB） | 3.5 s | 2.1 s | 0.86 s | 0.44 s | 0.24 s | ≥ 44 s（D，表 7-4） |
| Qwen3.8-2.4T FP8（49.4 GB + 0.3 GB state） | 3.7 s | 2.2 s | 0.90 s | 0.46 s | 0.26 s | 查無 |
| Kimi K3 FP8（14.5 GB + 0.43 GB state） | 1.1 s | 0.66 s | 0.27 s | 0.14 s | 0.08 s | 查無 |
| DeepSeek-V4-Pro（量化後約 5.2 GB） | 0.38 s | 0.23 s | 0.09 s | 0.05 s | 0.03 s | 43.7–79.2 s（B，表 7-3） |
| DeepSeek-V4.1-Flash global KV（0.93 GB） | 0.07 s | 0.04 s | 0.02 s | < 0.01 s | < 0.01 s | 約 250 s（8× H200；D，表 7-4） |

- 頻寬來源：NVMe 持續讀取 13.5 GB/s 與 GPU↔CPU 複製 54–56 GB/s [A] [arXiv 2609.11744](https://arxiv.org/abs/2609.11744)；DRAM restore 22.7 GB/s [B] [llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)；device-to-device 108 GB/s [A] [perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)；8 × 400 Gbps RDMA 194 GB/s [B] [vLLM PegaFlow](https://vllm.ai/blog/2026-05-18-pegaflow)。
- 唯一直接量到的 1M 交接是 TileRT 的 81 GB / 751 ms（A）。實際傳輸遠低於線速：200 Gb/s 連線上 4 GB 約 360 ms，約 11 GB/s、線速的 44% [B] [llm-d v0.5](https://llm-d.ai/blog/llm-d-v0.5-sustaining-performance-at-scale)；500K–1M 下 restore 對重算的端到端量測：查無公開資料。
- 每個模型的 restore 都比重算快 1–3 個數量級，所以 KV 層在長 context 下即使只有 NVMe 級的路徑也划算；200K 的 GLM-5.x（8.99 GB）由 DRAM restore 約 0.40 s（D：8.99 ÷ 22.7）。

### NVIDIA GPU

本節所有技術都可用，也是唯一每一項都有量測的平台。PD 由 Dynamo、llm-d、vLLM、SGLang 支援，KV 交接可留在 NVLink 網域內：GB200 NVL72 每顆 GPU 900 GB/s，8-GPU 節點之間的 RoCE 為 50 GB/s [A] [InferenceX 2026-05-23](https://inferencex.semianalysis.com/blog/gb200-nvl72-vs-b200-disagg-deepseek-r1-fp4-dynamo-trt)。GPUDirect Storage 到 FSx for Lustre 與 GPUDirect RDMA 到 WEKA 是 GPU 專屬路徑 [AWS Storage Blog](https://aws.amazon.com/blogs/storage/accelerate-inference-with-kv-cache-tiering-on-aws/)。

- 只在 NVIDIA 上有的：HiSparse、NVFP4 KV（Blackwell 上量測）。Hopper 的 FP8 KV 在 100K 以上要用 2026-04 之後的 kernel。
- 狀態：Dynamo 自己的 KV Block Manager 在 v1.5.0（2026-09-18）列為 deprecated，改用引擎原生的 offload [Dynamo deprecations](https://docs.nvidia.com/dynamo/dev/reference/releases/deprecations)；CMX 為已宣布未出貨（夥伴產品 2026 下半年），無量測。

### AMD GPU

除了 HiSparse，多數技術已有 AMD 上的紀錄：FP8 KV 加 DCP8 加 host offload（Kimi K3 的 MI355X 配置）、TileRT 的 device-to-device KV 交接（108 GB/s）、ATOM 引擎的 sparse checkpoint retention、vLLM 的 `MoRIIOConnector`（ROCm 專用）做 PD，Qwen3-235B 在 8× MI300X 的 100 條請求中達標 73 條對 colocated 的 30 條 [B，2026-09-29] [vLLM PD guide](https://vllm.ai/blog/2026-09-29-disaggregated-serving-guide)。

- 限制：host offload 要 ROCm 7.14 的 `hipMemcpyBatchAsync` 才有效率；AITER 在 2026 年才補上 64-bit offset（超過 4 GB 的 prefill batch、超過 2 GB 的 MLA KV）與 131,000 tokens 以上的 row indexing 修正 [A，評論] [InferenceX AgentX](https://inferencex.semianalysis.com/blog/agentx-inferencexv3-does-cuda-moat)。
- NVFP4 / FP4 KV 在 AMD 上的支援、CMX 對應的儲存層：查無公開資料。

### AWS Trainium（vLLM-Neuron 0.24.0.1.1.0，Beta；Neuron 2.32）

可用的有 automatic prefix caching（預設開啟，需要 segmented prefill，prefix 必須逐 byte 相同）、segmented prefill（512–8,192-token 分段，「tested up to 128K」）、context parallelism（Neuron 2.32，2026-08-17；decode 模式 DCP ≤ TP / num_kv_heads、不能與 attention DP 併用；另有需搭配 DI 的 prefill 模式）、PD disaggregation（1P1D 與 xPyD，KV 經 NIXL / LIBFABRIC / EFA）、decode context-length buckets，以及 EAGLE3 speculative decoding [C] [vLLM Neuron README](https://github.com/vllm-project/vllm-neuron/blob/release-0.24.0.1.1.0/README.md)、[Neuron What's New](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/whats-new.html)、[configuration reference](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/guides/reference-configuration.html)、[DCP design](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/design/parallelism/dcp.html)、[DI design](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/design/vllm/disaggregated-inference.html)。

- 不可用：KV offload / tiering（README 標「KV cache offloading ❌」）、prefill 與 decode 混批的 chunked prefill、pipeline parallelism、MTP 與 draft-model speculation、MLA 模型、preemption；每批只能有一個 prefill。
- 部分可用：FP8 KV 只支援 Llama 3，gpt-oss 會忽略該旗標 [KV quantization design](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/vllm-neuron/docs/design/vllm/kv-cache-quantization.html)；sparse attention 只有 gpt-oss 的 sliding window 與實驗性的 indexer kernel。
- 兩份 AWS 資料並列：Storage Blog 寫 Trainium 由共享層升回 HBM 的路徑走 EFA、沒有 GDS；vLLM-Neuron 的 README 則標示不支援 KV offload [AWS Storage Blog](https://aws.amazon.com/blogs/storage/accelerate-inference-with-kv-cache-tiering-on-aws/)。prefix-aware routing、4-bit KV、HiSparse 在 Trainium 上：查無公開資料。
- prefix caching 的廠商數字（NxDI、Llama 3.3 70B、Trn2）：90% 命中時 TTFT 好 3.2 倍，25% 命中 1.6 倍，0% 無增益 [C] [NxDI release notes](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/release-notes/components/nxd-inference.html)。

### AWS Inferentia2（NxDI / Optimum Neuron，維護模式）

公開紀錄的最大 context 是 32,768，本節的技術在 200K 以上都用不到。NxDI 的 KV cache 是連續配置（非 paged），每條序列一塊、大小為 `max_model_len`；prefix caching 自 Neuron 2.24（2025-06-24）起經 vLLM 支援，但與 disaggregated inference 不相容；不支援 chunked prefill；`kv_cache_quant=True`（FP8）可用；PD 只存在於已停止支援的舊 fork；KV offload 未見文件 [C] [NxDI feature guide](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/developer_guides/feature-guide.html)、[vLLM guide for NxDI](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/developer_guides/vllm-user-guide-v1.html)。Optimum Neuron 的 vLLM 平台有自己的 chunked prefill，但不支援 prefix caching [Optimum Neuron](https://github.com/huggingface/optimum-neuron/blob/main/optimum/neuron/vllm/ARCHITECTURE_VLLM_SERVING.md)。

### Google TPU（vLLM-TPU 於 v6e / TPU7x；SGLang-JAX）

release matrix 標示 Passing 的有 prefix caching、chunked prefill、KV offload 到 host DRAM（`TPUOffloadConnector`；TPU-Sync 把 host DRAM 當第二層，約 200 GB/s 雙向 PCIe）、DCN-based PD disaggregation，以及 Eagle3 / Ngram speculative decoding（DFlash 只在 Flax 與 default 路徑 Passing，Torchax 路徑為 Untested）；Ironwood recipe 一律使用 `--kv-cache-dtype=fp8`（kernel 列為 Untested）[B / C] [support matrices](https://github.com/vllm-project/tpu-inference/tree/main/support_matrices)、[tpu-recipes](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/ironwood/vLLM)、[TPU-Sync](https://github.com/google/tpu-sync)。

- 與長 context 直接相關的缺口：Google 的 benchmark recipe 以 `--no-enable-prefix-caching` 執行；沒有磁碟層，Mooncake Store 整合仍是提案；context / sequence parallel 為 Untested、無結果；MTP 對大型 MoE 尚未最佳化；sparse attention 只有實驗性 kernel（`deepseek_v4`）；「the external TPU serving stack does not have a fully optimized disagg path yet」[A，評論] [InferenceX TPU](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam)。
- 8 bit 以下的 KV 量化、NVMe / SSD KV 層、TPU 上的 PD 量測：查無公開資料。
- routing：GKE Inference Gateway 的 prefix-cache-aware routing 為 GA，endpoint picker 會看 KV-cache 命中與 TPU 使用率 [GKE docs](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/about-gke-inference-gateway)。Gemini 端只揭露產品層級的 context caching。

### Cerebras

代管服務，使用者碰不到引擎層。prompt caching 預設開啟（128-token block；TTL 保證 5 分鐘、最長 1 小時；不打折；cached tokens 不計入 uncached TPM）[C] [Cerebras prompt caching](https://inference-docs.cerebras.ai/capabilities/prompt-caching)；KV cache 不量化；speculative decoding 由 Cerebras 內部使用，只有 Dedicated 客戶可調 draft model [Cerebras Dedicated](https://inference-docs.cerebras.ai/dedicated/overview)。

- KV offload：每套系統配一台 6 TB DDR5 的 KVSS 節點（分析師），沒有使用者可見的控制項 [SemiAnalysis CS-3](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please)。
- PD：與夥伴硬體的 disaggregated prefill / decode 為已宣布未上線（AMD Helios prefill 目標 2026 Q4；AWS Trainium prefill 於 Bedrock 為 2027 Q1）[C] [Cerebras Q2 2026](https://www.sec.gov/Archives/edgar/data/2021728/000162828026056186/cbrsannouncesfinancialresu.htm)。
- chunked prefill、DCP、KV tiering 或 routing 的使用者控制：查無公開資料。

### NVIDIA Groq 3 LPX（參考）

LPX 只做 decode 端的分工，三種模式都由 Dynamo 編排：PD（Rubin GPU prefill，KV「once per turn」交給 LPX）、attention–FFN disaggregation（KV 留在 NVL72 的 HBM，LPX 跑 FFN 層）、external-draft speculative decoding（LPU 起草、GPU 驗證）[C，2026-08-24] [NVIDIA developer blog](https://developer.nvidia.com/blog/how-nvidia-groq-3-lpx-unlocks-ultrafast-interactivity-at-long-context-on-nvidia-vera-rubin/)、[NVIDIA press 2026-03-16](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Vera-Rubin-Opens-Agentic-AI-Frontier/default.aspx)。狀態為 2026-08-24 宣布 full production，未見公有雲 SKU；prefix caching、KV offload、KV 量化在 LPX 上的做法：查無公開資料。

## 模型與服務端的 context 上限對照

截至 2026-10-04，旗艦 API 的標準視窗是 1M（Claude、GPT-6.1、Gemini、Kimi K3、GLM-5.3、DeepSeek V4 / V4.1、Qwen3.8-Max），但實際買得到的 context 取決於硬體類別：Cerebras 與 Groq 停在 131K，代管商對同一批開源旗艦多數給到 1M（Kimi K3 在 Artificial Analysis 的 17 個端點中有 15 個）。計價分兩派：OpenAI 在輸入超過 272K、Gemini Pro 在超過 200K 時對整個請求加價（輸入 2 倍、輸出 1.5 倍），其餘採單一費率加 cache 計價。

### 模型的原生 context、最大輸出與長 prompt 計價

**表 7-12 原廠 API 的 context、最大輸出與長 prompt 價格**（等級 C：廠商價目與規格，2026-10-04 讀取；價格為每 1M tokens 美元，順序為輸入 / cached 輸入 / 輸出。）

| 模型（API） | context 視窗 | 最大輸出 | 長 prompt 的價格規則 | cache 條款 | 來源 |
|---|---|---|---|---|---|
| Kimi K3（Moonshot `kimi-k3`；開源權重原生 1,048,576） | 1,048,576 | 預設 131,072，最高 1,048,576 | 單一費率：$3.00 / $0.30 / $15.00 | cache write 另計：$3.00（5 分鐘 TTL，預設）或 $6.00（1 小時 TTL）；命中會續期 | [Kimi pricing](https://platform.kimi.ai/docs/pricing/chat)、[Kimi K3 quickstart](https://platform.kimi.ai/docs/guide/kimi-k3-quickstart)、[Kimi context caching](https://platform.kimi.ai/docs/guide/context-caching) |
| GLM-5.3（Z.ai；開源權重原生 1,048,576） | 1M | 128K | 單一費率：$1.40 / $0.26 / $4.40 | cached input 儲存「Limited-time Free」 | [Z.ai pricing](https://docs.z.ai/guides/overview/pricing)、[Z.ai GLM-5.3](https://docs.z.ai/guides/llm/glm-5.3) |
| DeepSeek `deepseek-v4-pro`（V4-Pro-0813） | 1M | 384K | 單一費率，分尖峰 / 離峰：尖峰 $1.32 / $0.044 / $3.96，離峰減半 | 自動；正式環境的 global KV cache 壽命 ≥ 72 小時（V4.1 tech report） | [DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing)、[DeepSeek V4.1 tech report](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/main/DeepSeek_V41_Tech_Report.pdf) |
| DeepSeek `deepseek-flash`（V4.1-Flash） | 1M | 384K | 尖峰 $0.30 / $0.006 / $1.20，離峰減半 | 同上 | [DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing) |
| Qwen3.8-Max（Alibaba `qwen3.8-max`，基於 Qwen3.8-2.4T-A95B；開源權重原生 262,144，可延伸到 1,010,000） | 1M（最大輸入 991K，thinking 模式 983K） | 131K，另加最多 262K reasoning tokens | 0–1M 單一級距：$2 / $6。舊機型分級：qwen3.6-max-preview 在 ≤ 128K 為 $1.3 / $7.8、128K–256K 為 $2 / $12 | implicit cache $0.25；explicit cache 建立 $2.50、讀取 $0.17（Qwen Cloud 頁面）；Model Studio 文件寫 qwen3.8 系列的 explicit cache 價格見 console | [Qwen Cloud](https://www.qwencloud.com/models/qwen3.8-max)、[Model Studio pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing) |
| Claude（Opus 5.5 / 5 / 4.8–4.6、Sonnet 5.5 / 5 / 4.6、Fable、Mythos） | 1M（其餘機型如 Sonnet 4.5 為 200K） | 最高 128K | 不加價：「A 900k-token request is billed at the same per-token rate as a 9k-token request」 | 5 分鐘 TTL（write 為輸入價的 1.25 倍）或 1 小時 TTL（2 倍） | [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)、[context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)、[prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) |
| GPT（gpt-6.1-sol 與同系列） | 1,050,000 | 128,000 | 輸入超過 272K tokens 時，整個請求的輸入與 cache 費率 2 倍、輸出 1.5 倍：gpt-6.1-sol $2 / $0.10 / $10 變 $4 / $0.20 / $15；gpt-6-astra $10 / $1 / $50 變 $20 / $2 / $75 | cached input 最多折 95%；GPT-5.6 之後預設 TTL 30 分鐘 | [OpenAI pricing](https://developers.openai.com/api/docs/pricing)、[gpt-6.1-sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)、[OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) |
| Gemini（3.8 Flash、3.1 Pro、3.5 Flash-Lite；Gemini 4 Argon） | 輸入 1,048,576 | 65,536；Gemini 4 Argon 為 1M（2026-09-30 宣布，先向 Fairwind Program 推出） | Pro 機型在 prompt 超過 200K 時輸入 2 倍、輸出 1.5 倍：3.1 Pro 輸入 $2 變 $4、輸出 $12 變 $18；Flash 機型沒有長度級距（3.8 Flash $0.75 / $3.75） | 3.1 Pro cached 輸入 $0.20 變 $0.40，另收每 1M tokens 每小時 $4.50 的儲存費；implicit caching 預設開啟 | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)、[Gemini caching](https://ai.google.dev/gemini-api/docs/caching)、[The Decoder](https://the-decoder.com/google-gemini-4-argon-closes-the-gap-with-openai-and-anthropic-but-doesnt-take-a-clear-lead/) |

- 沒有原廠 API 列的兩個模型：Qwen3.8-27B 的開源權重原生 262,144（card：可延伸到 1,000,000）；gpt-oss-120b 在各代管商一律約 131K（表 7-13）。
- 加價門檻的影響（D）：一條 300K-token 的 gpt-6.1-sol 請求、95% 命中 cache、輸出 2K，長 context 費率為 0.285M × $0.20 + 0.015M × $4 + 0.002M × $15 = $0.147，短 context 費率為 $0.079，整條請求是 1.87 倍；用戶端有直接的誘因把 context 壓在 272K 以下。
- Kimi Code（訂閱）不是加價而是加倍扣額度：1M 的 `k3` 約消耗 `k3-256k` 兩倍的額度，且 1M 只開放給較高方案 [C] [Kimi Code models](https://www.kimi.com/code/docs/en/kimi-code/models.html)。Kimi K3 在 Bedrock 為 1M、標準費率，Priority 為 1.75 倍、Flex 為 0.5 倍 [C] [Bedrock Kimi K3 model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-moonshot-ai-kimi-k3.html)。

### 各供應商與硬體類別實際提供的 context

**表 7-13 同一模型在不同硬體類別買得到的 context**（Artificial Analysis 各端點的 context 欄，等級 A，2026-10-04 擷取；端點計數為 D。「AA 列出的全部端點」含 ASIC、GPU、超大規模雲與原廠端點。）

| 模型 | ASIC 雲 | AA 列出的全部端點 | Amazon Bedrock | 原廠 API | 來源 |
|---|---|---|---|---|---|
| gpt-oss-120b | Cerebras 131K（paid）/ 65K（free）；Groq 131K；SambaNova 131K | 18 個：131K × 14、128K × 3、116K × 1 | 131K | 不適用 | [AA gpt-oss-120b](https://artificialanalysis.ai/models/gpt-oss-120b/providers)、[Cerebras gpt-oss](https://inference-docs.cerebras.ai/models/openai-oss) |
| Qwen3.8-27B | Cerebras 131,072（paid）/ 65,536（free）；Groq 131,072（Preview，最大輸出 16,384） | 8 個：262K × 7、1M × 1（Alibaba Cloud） | 未上架 | Alibaba Cloud 端點為 1M | [AA Qwen3.8 27B](https://artificialanalysis.ai/models/qwen3-8-27b/providers)、[Cerebras Qwen 3.8 27B](https://inference-docs.cerebras.ai/models/qwen-3.8-27b)、[Groq models](https://console.groq.com/docs/models) |
| Kimi K3 | 無端點 | 17 個：1.05M × 14、1M × 1（Bedrock）、262K × 1（Bitdeer AI）、205K × 1（Databricks） | 1M（2026-09-18 GA） | 1,048,576 | [AA Kimi K3](https://artificialanalysis.ai/models/kimi-k3/providers) |
| GLM-5.3 | 無端點 | 25 個：1M × 14、1.05M × 9、786K × 1（Crusoe）、164K × 1（Inco） | 未上架（GLM 產品線停在 GLM 5） | 1M | [AA GLM-5.3](https://artificialanalysis.ai/models/glm-5-3/providers) |
| DeepSeek V4 Pro 0813 | 無端點 | 10 個：1.05M × 7、1M × 3 | 未上架（停在 V3.2） | 1M | [AA DeepSeek V4 Pro](https://artificialanalysis.ai/models/deepseek-v4-pro/providers) |
| DeepSeek V4.1 Flash | 無端點 | 22 個：1.05M × 10、1M × 11、524K × 1（Novita） | 未上架 | 1M | [AA DeepSeek V4.1 Flash](https://artificialanalysis.ai/models/deepseek-v4-1-flash/providers) |
| Qwen3.8-2.4T | 無端點 | 6 個：262K × 5（含 Alibaba Cloud）、1M × 1（Modal） | 未上架（停在 Qwen3） | qwen3.8-max 為 1M | [AA Qwen3.8 2.4T](https://artificialanalysis.ai/models/qwen3-8-2-4t-a95b/providers) |

- ASIC 雲只公開服務小型或較舊的機型，context 上限 32K–131K（SambaNova 的 DeepSeek-V3.1 為 128K、V3.2 為 32K），GPU 代管商對同級模型給 262K–1M。這與 SRAM 容量的限制一致，但因果是推論，不是廠商說法（D）。Bedrock 的上架清單見 [Bedrock model cards](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html)。
- 同一個 Cerebras 端點兩個來源不同：Cerebras 文件寫 Qwen 3.8 27B 的 paid tier 為 131,072，OpenRouter 的端點列表寫 65,536 context / 32,768 輸出 [OpenRouter](https://openrouter.ai/qwen/qwen3.8-27b)。
- 超大規模雲的其他 1M 供應：Vertex AI 以代管 API 提供 GLM 5.2（Preview，1M context，硬體未揭露）[Vertex open models](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)；Azure AI Foundry 的 DeepSeek V4 Pro 為 1M [Azure Foundry models](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure)。

### rate limit、配額與長 context 的流量占比

**表 7-14 長 context 與 cached input 在配額上的計法**（等級 C：廠商文件；標 D 者為本文換算。）

| 供應商 | 規則 | 數字 | 來源 |
|---|---|---|---|
| Anthropic | 「Full rate limits at every context length」；多數機型的 ITPM 只計未快取輸入與 cache write | 2,000,000 ITPM 在 80% 命中時等於每分鐘 10M 總輸入 tokens（D：2,000,000 ÷ (1 − 0.8)） | [Claude 1M GA](https://claude.com/blog/1m-context-ga)；[Claude rate limits](https://platform.claude.com/docs/en/api/rate-limits) |
| Amazon Bedrock（Claude） | 配額消耗的輸入不含 cache read（`InputTokenCount + CacheWriteInputTokenCount`）；輸出依機型以 5 倍（≤ 4.7）、15 倍（4.8）或 10 倍（Opus 5.5、Sonnet 5、Opus 5、Fable 5.1）計 | 舊的獨立配額「Claude Sonnet 4.5 V1 1M Context Length」：1,000,000 TPM、1,000 RPM（cross-region，可調），每日 720M tokens（global 1.44B） | [Bedrock quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html)、[token burndown](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html) |
| Amazon Bedrock（Kimi K3） | cache 命中不計入每分鐘輸入 token 配額 | 10,000,000 TPM（可調）、每日 14.4B tokens；等於每分鐘 50 條未快取的 200K 請求或 9.5 條 1M 請求（D：10,000,000 ÷ n） | [Bedrock Kimi K3 model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-moonshot-ai-kimi-k3.html)、[AWS What's New](https://aws.amazon.com/about-aws/whats-new/2026/09/moonshot-ai-kimi-k3-on-amazon-bedrock/) |
| OpenAI | 長 context 請求有獨立的 rate limit；cached tokens 仍計入 TPM；Scale tier 的換算對長 context 輸入加權 2.0、輸出 7.5 | 獨立配額的大小：查無公開資料 | [OpenAI rate limits](https://developers.openai.com/api/docs/guides/rate-limits)、[OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) |
| Google Gemini | 3.1 Pro 的 Provisioned Throughput 消耗在輸入超過 200K 時輸入加倍 | 未列其他數字 | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| Moonshot（Kimi API） | 依累積儲值分級（併發、RPM、TPM、TPD）；沒有公布長 context 規則 | Tier0：併發 1 / 3 RPM / 500,000 TPM；Tier5：100 / 300 / 5,000,000 TPM | [Kimi rate limits](https://platform.kimi.ai/docs/pricing/limits) |
| DeepSeek | 以併發計，不是 TPM；請求 10 分鐘內未開始推論就關閉連線 | `deepseek-v4-pro` 500 併發；`deepseek-flash` 2,500 併發 | [DeepSeek rate limit](https://api-docs.deepseek.com/quick_start/rate_limit)、[DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing) |
| Alibaba（qwen3.8-max） | 計價級距由單一請求的輸入 tokens 決定；International region 為動態限流 | 兩個來源不同：30,000 RPM / 5,000,000 TPM（Global）、600 RPM / 1,000,000 TPM（Hong Kong）；Qwen Cloud 頁面為 2M tokens/min、15K requests/min | [Alibaba rate limits](https://www.alibabacloud.com/help/en/model-studio/rate-limit)、[Qwen Cloud](https://www.qwencloud.com/models/qwen3.8-max) |
| Z.ai | 查無公開資料（定價與 GLM-5.3 頁面未列 rate limit） | 查無 | [Z.ai pricing](https://docs.z.ai/guides/overview/pricing) |
| Cerebras | 雙 bucket：Uncached TPM 是主要限制，Total TPM 為其 3 倍；請求先以估計輸入加 `max_completion_tokens` 預檢 | Developer tier：gpt-oss-120b 1,000 RPM / 1M uncached / 3M total；qwen-3.8-27b 300 RPM / 150K uncached / 750K total，約每分鐘一條 131K 的未快取 prompt（D：150,000 ÷ 131,072 = 1.14） | [Cerebras rate limits](https://inference-docs.cerebras.ai/support/rate-limits) |
| Groq（Qwen3.8-27B，Preview） | 未見長 context 規則 | developer plan：250K TPM、1K RPM | [Groq models](https://console.groq.com/docs/models) |

- 長 context 的流量占比：「Nearly 1 in 5 Anthropic tokens processed in April 2026 were long-context」（門檻未定義）；同一來源指出 Claude Sonnet 4.6 的實付價為每 1M tokens $0.62 對牌價 $3.00，差距來自 caching [B，2026-06-08] [Ramp](https://ramp.com/blog/ai-token-cost-for-businesses)。各供應商超過 200K 或 1M 的請求占比：查無公開資料。
- prompt 長度的分布：多供應商 gateway 的平均 prompt 由約 1.5K 增至 6K tokens 以上，programming 請求經常超過 20K [B，2025-12] [OpenRouter State of AI](https://openrouter.ai/state-of-ai)；agentic coding trace 則是中位 142K、p90 272K、p99 675K（InferenceX）與 p50 195K、p90 521K、p99 849K（llm-d 的 main agent）[A / B] [InferenceX AgentX](https://inferencex.semianalysis.com/blog/agentx-inferencexv3-does-cuda-moat)、[llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)。
- cache-aware 的配額（Anthropic、Cerebras、Bedrock）讓有效吞吐量變成命中率的函數：Anthropic 在 80% 命中時為 5 倍，Cerebras 最多 3 倍（D）。OpenAI 把 cached tokens 計入 TPM 並另設長 context 配額，所以長 context 容量是要單獨申請的額度。
- cache TTL 決定服務端要撐住多久的閒置 session：5 分鐘（Anthropic 預設、Kimi 預設）、30 分鐘（OpenAI GPT-5.6 之後、Bedrock 的 Kimi K3）、1 小時（付費選項）、≥ 72 小時（DeepSeek）。llm-d trace 的 turn 間隔為 p50 2 s、p90 24 s、p99 11.4 分鐘，5 分鐘的 TTL 會讓少數 turn 落回 cold prefill（D，推論）。

## 長上下文的品質

名義上支援的視窗不等於可用的視窗：前置 250K–500K tokens 的相關 context 會讓 agent 通過率相對下降 10–30%（A），一個開源模型的 8-needle MRCR 由 256K 的 93–94% 掉到 512K–1M 的 21–41%（B），廠商自己公布的 1M MRCR 分數為 76–93%。Anthropic 與 OpenAI 的文件都把開發者導向 compaction 與精選 context，Google 仍建議把相關資料整份放進 context 並搭配 caching。

**表 7-15 200K–1M 的品質量測**

| 來源（等級；日期） | 測試 | 結果 |
|---|---|---|
| [Boolean](https://boolean.ai/blog/context-rot-quantified)（A；2026-09-15） | 20 個 terminal-bench v4 任務，前置 0 / 250K / 500K tokens 的 context | 無關的 context：Claude Opus 5 通過率 0.50 / 0.52 / 0.48，GPT-5.6 Sol 0.31 / 0.24 / 0.22。相關的 context：Opus 5 0.50 / 0.425 / 0.398，GPT-5.6 Sol 0.347 / 0.26 / 0.26。結論是能開新 session 或 compact 就做 |
| [Chroma](https://trychroma.com/research/context-rot)（A；2025-07） | 18 個模型，輸入長度遞增 | 連簡單任務也隨輸入變長而退化；LongMemEval 上約 300 tokens 的聚焦 prompt 在每個模型家族都勝過約 113K 的完整 prompt |
| [arXiv 2606.19348](https://arxiv.org/abs/2606.19348)、[DeepSeek-V4-Pro card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro)（B / C；2026-04） | MRCR 1M（MMR） | Claude Opus 4.6 Max 92.9、DeepSeek-V4-Pro Max 83.5、V4-Flash Max 78.7、Gemini 3.1 Pro High 76.3。reasoning effort 影響很大：V4-Pro 不開 thinking 為 44.7，high 為 83.3。「a performance degradation becomes visible beyond the 128K mark」；agent 評測的最大 context 為 512K |
| [arXiv 2608.30320](https://arxiv.org/abs/2608.30320)（B；2026-08-31） | Qwen3.8-Flash-Next 的 RULER 與 8-needle MRCR，依長度（full attention / QSA sparse） | RULER：≤ 128K 為 99.84 / 99.89，256–512K 為 97.65 / 98.95，512K–1M 為 90.08 / 93.00。8-needle MRCR：128K 為 97.14 / 95.98，256K 為 94.20 / 93.00，512K 為 30.66 / 40.53，1M 為 20.71 / 26.44 |
| [Claude 1M GA](https://claude.com/blog/1m-context-ga)（C；2026-03-13） | MRCR v2，1M | Opus 4.6 為 78.3% |
| [arXiv 2607.24653](https://arxiv.org/abs/2607.24653)、[Kimi K3 card](https://huggingface.co/moonshotai/Kimi-K3)（C / B；2026-08） | BrowseComp；AA-LCR | 300K 觸發 compaction 為 91.2%，全 1M 視窗不做管理為 90.4%；AA-LCR 74.7 |
| [GLM-5.2](https://huggingface.co/zai-org/GLM-5.2)、[Z.ai GLM-5.2](https://docs.z.ai/guides/llm/glm-5.2)（C） | 自家評測的視窗設定 | 宣稱「Solid 1M lossless context」；SWE-Bench Pro、NL2Repo、DeepSWE、ProgramBench 用 400K，Terminal-Bench 2.1 用 256K，只有第三方執行的 FrontierSWE、PostTrainBench、SWE-Marathon 用 1M |
| [vLLM FP8 KV](https://vllm.ai/blog/2026-04-22-fp8-kvcache)、[vLLM TurboQuant](https://vllm.ai/blog/2026-05-11-turboquant)（B） | KV 精度與長度的交互作用 | FP8 kernel 有缺陷時 128K needle 準確率 91% 變 13%；3-bit KV 量化相對退化約 30%，集中在 128K–256K |

**表 7-16 廠商對長 context、retrieval 與 compaction 的指引**（等級 C，廠商文件。）

| 廠商 | 指引 | 來源 |
|---|---|---|
| Anthropic | 「more context isn't automatically better. As token count grows, accuracy and recall degrade, a phenomenon known as context rot」；「server-side compaction is the primary strategy for context management」。1M GA 文中的客戶引述：1M 視窗讓 compaction 事件減少 15% | [context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)、[Claude 1M GA](https://claude.com/blog/1m-context-ga) |
| OpenAI | 歷史保持 append-only，因為「Summarization, compaction, or context truncation can change the prefix and reset cache reuse」；Responses API 提供 `context_management`（compaction）選項；Codex 預設把 context 限在 400K | [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching)、[Boolean](https://boolean.ai/blog/context-rot-quantified) |
| Google | Gemini 的視窗「invites a more direct approach: providing all relevant information upfront」，context caching 是「the primary optimization」；但多個 needle 時「the model does not perform with the same accuracy」，且「if you don't need tokens to be passed to the model, it is best to avoid passing them」（2026-06-22 更新） | [Gemini long-context guide](https://ai.google.dev/gemini-api/docs/long-context) |
| Moonshot（Kimi Code） | 1M 的 `k3` 約消耗 `k3-256k` 兩倍的額度，1M 保留給較高方案，切到 256K 機型前建議先 compact；切換模型或 effort 會讓 context cache 失效 | [Kimi Code models](https://www.kimi.com/code/docs/en/kimi-code/models.html) |
| Cerebras（分析師預期） | 1.6T 模型的客戶預期跑「256k context window, rather than the full 1M」 | [SemiAnalysis CS-4](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast) |
| vLLM recipe | static YaRN「holds the scaling factor constant regardless of input length, so leave this off unless you actually serve long prompts」；約 524K 時把 factor 減半為 2.0 | [vLLM recipe Qwen3.8-27B](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-27B.yaml) |

- 同一個模型有兩個 1M 分數：DeepSeek 論文列 Claude Opus 4.6 Max 的 MRCR 1M（MMR）為 92.9，Anthropic 公布 Opus 4.6 的 MRCR v2 為 78.3%；兩者標示的 benchmark 版本與指標不同，能否對照未經查證。
- 多事實任務的可用視窗比標示的短（D）：已公布的 1M 多 needle 分數為 76–93%，8-needle MRCR 在 256K 之後低於 41%，而單一 needle 或 RULER 式檢索到 1M 仍高於 90%。只測單一 needle 的 benchmark 會高估 1M 的可用性。
- 工程與品質的證據指向同一個設計點（D）：200K–300K 是品質仍接近持平、cold TTFT 為 10–30 s、Kimi K3 與 GLM-5.x 每 session 的 KV 約 3–13 GiB 的區間（13,824 B × 200,000 到 44,928 B × 300,000）。廠商的 compaction 觸發點（BrowseComp 的 300K、Codex 預設的 400K、llm-d trace 的 500K 以上）落在同一帶，trace 的分布是 p95 約 400–480K、p99 約 675–850K；例行服務到約 256K–400K、把 1M 當尾端處理，與這些數字相符。
- compaction 用一次短 context 的 cold prefill 換品質與 KV 用量：少用（0.03% 的 turn）時便宜，每幾輪就改寫歷史時昂貴（命中率掉到 51–61%）。
- 靠 position encoding 外插而不是訓練達到 1M 的模型有品質上的保留。DeepSeek-V4.1-Flash 如何達到 1M 有兩種說法：vLLM recipe 寫 YaRN factor 16、訓練視窗 65,536；tech report 寫 sparse attention 在 64K 從頭訓練後延伸到 1M [vLLM recipe DeepSeek-V4.1-Flash](https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4.1-Flash.yaml)、[DeepSeek V4.1 tech report](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/blob/main/DeepSeek_V41_Tech_Report.pdf)。
- 查無公開資料：Kimi K3、GLM-5.3、Qwen3.8-2.4T 在 500K–1M 的獨立長 context benchmark；現役私有模型（Opus 5.5、GPT-6.x、Gemini 3.8 / 4）的 MRCR v2、GraphWalks 或 LongBench-v2；2026 機型在 1M 下 full-context 對 retrieval 的答題品質比較。

## 網站呈現建議

- 表 7-9 做成「加速器 × context 長度」的判定矩陣：列為加速器、欄為 200K 與 1M，四種判定用顏色加圖示區分（「查無」用灰階斜線，不留白），點開顯示綁住上限的資源與依據連結。矩陣上方放一條對數刻度的橫軸，標出各平台公開示範的最大 context（32,768、98,304、100K、131,072、1,048,576）。
- 表 7-1 與表 7-2 合併成 KV 計算器：選模型、KV 精度、節點，context 用滑桿（8K–1M），輸出每序列 KV（GiB）與可常駐序列數，固定顯示算式與「D」標記；引擎量到的常駐條數（H20、RTX PRO 6000）用不同的點型疊在同一張圖上。
- 表 7-3、表 7-4 與表 7-6 畫成一張 TTFT 對 prompt 長度的 log-log 圖：量測點實心、推算點空心加虛線，warm 的 p50–p95 畫成水平帶，讓「cold 1M 為 44 s 以上、warm 為 0.2–1 s」一眼可見。表 7-7 另畫成命中率四個分桶的點圖（對數 y 軸），標示 5 s 與 10 s 兩條線。
- 表 7-10 做成可篩選的技術矩陣，儲存格只顯示判定詞，展開才顯示證據；提供第二個視圖把「各加速器是否可用」（本節的七個小節）轉成同一組列的欄位。表 7-11 做成互動：選模型與頻寬，顯示搬移時間與 cold 重算時間的比值。
- 表 7-12 至表 7-14 併成「context、計價與配額」頁籤，附一個單次請求成本計算器（輸入 prompt 長度、cache 命中率、輸出長度），在 OpenAI 的 272K 與 Gemini Pro 的 200K 畫出跳階。
- 可刪減：表 7-5 的私有模型逐項數字、表 7-6 的逐點列表、各加速器小節的不可用清單改為摺疊；KV bytes/token 的推導只連到第 4 章表 4-2，不重複。
