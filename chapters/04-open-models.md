# 第 4 章 開源模型效能:Kimi / GLM / DeepSeek / Qwen

資料基準日:2026-10-04。等級:**A** = 獨立第三方量測;**B** = 廠商 / 夥伴公布且揭露方法;**C** = 廠商宣稱或規格、未揭露方法;**D** = 本文推算(附算式)。

## 四個模型家族的最新版本規格

截至 2026-10-04,四個家族都已換代:現役開源旗艦是 Kimi K3(2.78T 參數,權重 2026-07-27 公開)、GLM-5.3(744B,2026-08-28)、DeepSeek-V4-Pro-0813(1.6T,2026-08-13;最新架構為 2026-09-10 的 DeepSeek-V4.1-Flash)與 Qwen3.8-2.4T-A95B(2.4T,2026-08-12)。四家都改用混合式注意力,FP8 下每 token 的 KV cache 由 2025 年機型的 34–184 KiB 降到 0.9–47 KiB(D),sizing 的限制改由權重大小(旗艦量化後 0.76–2.5 TB)、每序列固定 state(0.1–0.6 GiB)與每 token 啟用參數量(8–104B)決定。

**表 4-1 現役開源模型規格**(等級 C:config.json、model card、授權條文與 vLLM recipe,2026-10-04 讀取,recipe 為 2026-10-03 的 commit。發布日依 [InferenceX model dates](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/models.ts)、[DeepSeek API updates](https://api-docs.deepseek.com/updates)、[QwenLM/Qwen3.8 README](https://github.com/QwenLM/Qwen3.8)。「最低 VRAM」是 vLLM recipe 的 `vram_minimum_gb`,即 checkpoint 大小 × 1.2。)

| 模型 | 發布日 | 參數量(總 / 啟用) | 架構與注意力機制 | context 與最大輸出 | 授權 | 最低 VRAM 與最小部署 | 來源 |
|---|---|---|---|---|---|---|---|
| Kimi K3 | API 2026-07-16;權重 2026-07-27 | 2.78T / 104.2B | 93 層 LatentMoE(896 experts,每 token 16 + 2 shared);69 層 KDA(linear attention)+ 24 層 Gated MLA | 1,048,576(config);原廠 API 最大輸出預設 131,072、上限 1,048,576 | Kimi K3 License(自訂) | 1,680 GB(MXFP4);8× B300 / GB300 / MI355X(TP8)、16× B200 / GB200、Hopper 由 32× H100 起 | [config](https://huggingface.co/moonshotai/Kimi-K3/raw/main/config.json)、[card](https://huggingface.co/moonshotai/Kimi-K3)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/moonshotai/Kimi-K3.yaml) |
| Kimi K2.7-Code / K2.6(同一 config) | 2026-06-12 / 2026-04-20 | 1T / 32B | 61 層 MoE(384 experts,每 token 8 + 1 shared);每層皆 MLA | 262,144(config);API 最大輸出未載明 | Modified MIT | 714 GB(原生 INT4)、600 GB(NVFP4);8× H200,或 4× B300(NVFP4) | [config](https://huggingface.co/moonshotai/Kimi-K2.7-Code/raw/main/config.json)、[card](https://huggingface.co/moonshotai/Kimi-K2.7-Code)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/moonshotai/Kimi-K2.6.yaml) |
| GLM-5.3(與 GLM-5.2 同一 base model) | API 2026-08-14;權重 2026-08-28 | 744B / 40B(Z.ai) | 78 層 MoE(256 experts,每 token 8 + 1 shared);MLA + sparse attention indexer(IndexShare:21 full + 57 shared);MTP 1 層 | 1,048,576(config);API 最大輸出 128K | GLM-5.3 License(自訂);GLM-5.2 為 MIT | 893 GB(FP8)、558 GB(NVFP4)、447 GB(W4A8,Hopper);8× H200 或 8× H20(FP8),完整 1M context 需 8× B200 | [config](https://huggingface.co/zai-org/GLM-5.3/raw/main/config.json)、[card](https://huggingface.co/zai-org/GLM-5.3)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/zai-org/GLM-5.3.yaml) |
| GLM-5.3-Flash | 2026-08(隨 GLM-5.3 權重釋出) | 320B / 18B | 45 層 MoE(288 experts,每 token 8 + 1 shared);34 層 KDA linear attention + 11 層 sparse MLA(NoPE);mHC;MTP 1 層 | 1,048,576(config) | MIT | 386 GB(FP8)、229 GB(NVFP4);一個 GB200 tray(TP4,FP8 + MTP) | [config](https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/config.json)、[card](https://huggingface.co/zai-org/GLM-5.3-Flash)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/zai-org/GLM-5.3-Flash.yaml) |
| DeepSeek-V4-Pro-0813 | 2026-08-13(preview 2026-04-24) | 1.6T / 49B | 61 層 MoE(384 experts,每 token 6 + 1 shared);CSA / HCA 混合、單一共用 KV head(compress ratio 4 共 30 層、128 共 31 層);MTP 1 層 + DSpark | 1,048,576(config);API 最大輸出 384K | MIT | 960 GB;8× B200 / B300 / H200(DP8 + EP;H200 的 context 上限 800K)、2 個 GB200 NVL4 tray、4× GB300 | [config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/main/config.json)、[card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4-Pro.yaml) |
| DeepSeek-V4-Flash-0731 | 2026-07-31 | 284B / 13B | 43 層 MoE(256 experts,每 token 6 + 1 shared);機制同 V4-Pro | 1,048,576(config) | MIT | 200 GB;4× B200 / B300,或 8× RTX PRO 6000 | [config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/raw/main/config.json)、[card](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4-Flash.yaml) |
| DeepSeek-V4.1-Flash | 2026-09-10 | backbone 552B + Engram 196B;prefill 每 token 8B、decode 16B | 40 層(20 層 causal encoder + 20 層 decoder);CSA2 跨層共用 KV;Engram n-gram memory;spec decode 只有 DSpark | 1,048,576(config);API 最大輸出 384K | MIT | 614 GB;一個 GB200 NVL4 tray(TP4)或一台 8× H200;Engram 表放 host DRAM 時 B200 / B300 / GB300 / MI355X 可用 TP2 | [config](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/main/config.json)、[card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4.1-Flash.yaml) |
| Qwen3.8-2.4T-A95B(代管名 Qwen3.8-Max) | 2026-08-12 | 2.4T / 95B | 92 層 MoE(512 experts,每 token 10 + 1 shared);69 層 Gated DeltaNet(linear attention)+ 23 層 GQA(4 KV heads,head_dim 256);MTP 1 層 | 原生 262,144(config),card 稱可擴至 1,010,000;代管版預設 1M、最大輸出 131K 另加 262K reasoning | Qwen3.8-Max License(自訂) | 1,737 GB(NVFP4)、2,996 GB(FP8)、5,871 GB(BF16);NVFP4:8× B300 或 2 個 GB300 tray;FP8:16 GPU;BF16:24 GPU | [config](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/config.json)、[card](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-2.4T-A95B.yaml) |
| Qwen3.8-27B | 2026-08-14 | 27B(dense) | 64 層;48 層 linear attention + 16 層 full attention(4 KV heads,head_dim 256);MTP 1 層 | 原生 262,144;以 YaRN(factor 4.0)擴至 1,000,000 | Apache-2.0 | 67 GB(BF16)、38 GB(FP8)、32 GB(NVFP4)、24 GB(INT4);各精度皆單張 GPU | [config](https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json)、[card](https://huggingface.co/Qwen/Qwen3.8-27B)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-27B.yaml) |
| Qwen3.8-Flash-Next(代管名 Qwen3.8-Flash) | 2026-08-26 | 125B / 6B,另有 51B n-gram embedding 與 4B MTP | 48 層 MoE(512 experts,每 token 10 + 1 shared);36 層 Gated DeltaNet + 12 層 Qwen Sparse Attention | 原生 262,144;可擴至 1,000,000 | Qwen Community License 1.0(自訂) | 130 GB(NVFP4)、250 GB(FP8);NVFP4:一張 B200 / B300;FP8:GB300 至少 2 張、建議 4 張 | [config](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/config.json)、[card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-Flash-Next.yaml) |

- 自訂授權的門檻(C,條文摘要,使用前需重讀原文):Kimi K3 對 12 個月營收超過 US$20M 的 model-as-a-service 業者要求另簽協議([LICENSE](https://huggingface.co/moonshotai/Kimi-K3/blob/main/LICENSE));GLM-5.3 對 12 個月營收超過 US$10B 的公司要求先通過 Z.AI 安全審查([LICENSE](https://huggingface.co/zai-org/GLM-5.3/blob/main/LICENSE));Qwen3.8-Max License 的門檻是 US$50M([LICENSE](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/blob/main/LICENSE)),Qwen Community License 1.0 則是任何規模的 MaaS 都要另簽([LICENSE](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/main/LICENSE))。
- 自架時的最大輸出是 serving 設定,不是 config 欄位;model card 的建議為 DeepSeek V4 的 high / max effort 384K、V4.1-Flash 至少 256K、Qwen3.8-2.4T 為 262,144 reasoning + 131,072 response,Kimi K3 與 GLM-5.3 的 card 查無此類建議。

**表 4-2 sizing 所需數字:每 token KV、每序列 state、權重**(KV 與 state 的推算值為等級 D,算式在表後;「引擎公布或實測值」另標等級。讀取日 2026-10-04。權重大小為 Hugging Face repo 的權重檔大小總和,2026-10-05 以 [Hugging Face API](https://huggingface.co/api/models/moonshotai/Kimi-K3/tree/main?recursive=true)(各 repo 的 file tree)重算,19 個 repo 全部相符。)

| 模型 | 持有 per-token KV 的層 × 元素 | KV bytes/token(BF16 / FP8) | 每序列固定 state | 一條序列在原生上限的 KV(BF16 / FP8) | 官方權重(精度;磁碟大小) | 引擎公布或實測值(等級) | 來源 |
|---|---|---|---|---|---|---|---|
| Kimi K3 | 24 層 MLA × 576 = 13,824 | 27,648 B(27.0 KiB)/ 13,824 B(13.5 KiB) | 69 層 KDA × 96 × 128 × 128 = 108.5M 元素;FP32 約 434 MB,TP8 下每 rank 約 54 MB | 1,048,576 tokens:27.0 GiB / 13.5 GiB | 僅 MXFP4(QAT):1,560.9 GB | SGLang:每 token 約 27 KB、每請求約 54 MB(TP=8)(B);InferenceX:8× B300、TP8、FP8 KV 為 42.23 GiB / 3,249,215 tokens(A) | [LMSYS 2026-07-27](https://www.lmsys.org/blog/2026-07-27-kimi-k3-day0-support/)、[perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml) |
| Kimi K2.6 / K2.7-Code | 61 層 MLA × 576 = 35,136 | 70,272 B(68.6 KiB)/ 35,136 B(34.3 KiB) | 無 | 262,144 tokens:17.2 GiB / 8.6 GiB | 原生 INT4:595.2 GB | 無公布值 | [config](https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/config.json) |
| GLM-5.3 / GLM-5.2 | 78 層 MLA × 576 = 44,928(另有 21 個 indexer × 128) | 89,856 B(87.8 KiB)/ 44,928 B(43.9 KiB);含 indexer key 約 93.0 / 46.5 KiB | 無 | 1,048,576 tokens:87.8 GiB / 43.9 GiB(僅 MLA) | FP8(預設 repo):755.6 GB;BF16:1,506.7 GB | llm-d:GLM-5.2 每 token 約 44 KB(FP8)(B);vLLM:8× MI325X、TP8 的 KV pool 為 1,477,168 tokens(B) | [llm-d 2026-07-22](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/zai-org/GLM-5.3.yaml) |
| GLM-5.3-Flash | 11 層 sparse MLA × 512 = 5,632 | 11,264 B(11.0 KiB)/ 5,632 B(5.5 KiB) | 34 × 64 × 128 × 128 = 35.7M 元素(每元素 2 B 時 68 MiB) | 1,048,576 tokens:11.0 GiB / 5.5 GiB | FP8:328.3 GB;BF16:642.7 GB | vLLM:4× MI355X、TP4、128K context,FP8 checkpoint 的 KV pool 為 14.92M tokens,BF16 為 8.87M(B) | [recipe](https://github.com/vllm-project/recipes/blob/main/models/zai-org/GLM-5.3-Flash.yaml) |
| DeepSeek-V4-Pro | 30 層 `c4a` + 31 層 `c128a`,K = V 共用、512 維 | 1M 序列平均約 9,856 B(BF16);FP8 attention cache + FP4 indexer cache 約減半 | 每層 128-token sliding window(已含在算式內) | 1,048,576 tokens:9.62 GiB(BF16);約 4.8 GiB(fp8 / fp4) | FP4 experts + FP8:892.7 GB | vLLM:1M 序列 9.62 GiB,為 V3.2 式堆疊 83.9 GiB 的 1 / 8.7(B);InferenceX:HBM KV working set 在 8× B300 約 43M tokens、8× B200 約 22M(A) | [vLLM 2026-04-24](https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-04-24-deepseek-v4.md)、[InferenceX 2026-08-25](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-b200-vs-b300-kv-working-set) |
| DeepSeek-V4-Flash | 21 層 `c4a` + 20 層 `c128a` | 約 6,885 B(BF16);fp8 / fp4 約 3.4 KB | sliding window 同上 | 1,048,576 tokens:約 6.7 GiB(BF16) | FP4 + FP8:166.9 GB | DeepSeek:V4.1-Flash 的 890 B 約為 V4-Flash 的 1/4(890 × 4 = 3,560 B),與推算相符(C) | [card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) |
| DeepSeek-V4.1-Flash | 4 個 KV 來源層跨層共用(FP4) | 890 B(只算 global KV;SWA KV 另計且有上限) | SWA window(128 tokens × 層數,FP8) | 1,048,576 tokens:0.87 GiB | FP4 experts + FP8:510.3 GB;其中 Engram 表 183.1 GiB 可放 host DRAM | DeepSeek:global KV 為 890 bytes per token(C) | [card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)、[recipe](https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4.1-Flash.yaml) |
| Qwen3.8-2.4T-A95B | 23 層 GQA × 2 × 4 × 256 = 47,104 | 94,208 B(92.0 KiB)/ 47,104 B(46.0 KiB) | 69 × 128 × 128 × 128 = 144.7M 元素;float32 為 552 MiB(上限),vLLM 以 BF16 存為 285 MiB | 262,144 tokens:23.0 GiB / 11.5 GiB;1,000,000 tokens:87.7 GiB(BF16) | BF16:4,892.4 GB;FP8:2,496.2 GB | vLLM:full attention 每層每 token 2 KiB × 23 層;Gated DeltaNet state 每層每請求 4,216 KiB × 69 層(B) | [vLLM 2026-09-21](https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-09-21-qwen38-pd-serving.md) |
| Qwen3.8-27B | 16 × 2 × 4 × 256 = 32,768 | 65,536 B(64.0 KiB)/ 32,768 B | 48 × 48 × 128 × 128 = 37.7M 元素 = 144 MiB(float32) | 262,144 tokens:16.0 GiB / 8.0 GiB | BF16:55.6 GB;FP8:30.9 GB | vLLM:單張 Blackwell GPU、NVFP4 build、1M context 可放 6.6M KV tokens(B) | [recipe](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-27B.yaml) |
| Qwen3.8-Flash-Next | 12 × 2 × 2 × 256 = 12,288(另有壓縮的 indexer key) | 24,576 B(24.0 KiB)/ 12,288 B | 36 × 48 × 128 × 128 = 28.3M 元素 = 108 MiB(float32) | 262,144 tokens:6.0 GiB / 3.0 GiB | BF16:360.0 GB;FP8:185.5 GB | SGLang:4× H200 把 51.2B 參數的 n-gram 表(約 95.4 GiB)移到 host 記憶體,KV 容量由 1.84M 增至 3.28M tokens(B) | [LMSYS 2026-08-26](https://www.lmsys.org/blog/2026-08-26-qwen-flash-next/) |

MLA 層每 token 的 KV 元素數:

```latex
E_{\mathrm{MLA}} = N_{\mathrm{MLA}} \times (\mathrm{kv\_lora\_rank} + \mathrm{qk\_rope\_head\_dim})
```

GQA(full attention)層每 token 的 KV 元素數:

```latex
E_{\mathrm{GQA}} = N_{\mathrm{full}} \times 2 \times \mathrm{num\_key\_value\_heads} \times \mathrm{head\_dim}
```

換算成 bytes(BF16 取 2、FP8 取 1):

```latex
B_{\mathrm{token}} = E \times b, \quad b \in \{2, 1\}
```

linear attention 層每序列固定 state 的元素數:

```latex
E_{\mathrm{state}} = N_{\mathrm{linear}} \times H_{\mathrm{value}} \times d_{\mathrm{key}} \times d_{\mathrm{value}}
```

- 以上算式不含引擎的 block padding、scale 與 draft model cache,應視為下限:GLM-5.3 FP8 在 8× MI325X 的實測 pool 換算每 token 約 75 KB 預算,高於推算的 46.5 KiB(D)。
- 2025 年機型對照(D,FP8):Kimi K2 / DeepSeek V3.x 為 35,136 B,Qwen3-235B-A22B 為 96,256 B,GLM-4.5 / 4.6 / 4.7 為 188,416 B。
- prefix caching 會讓引擎為每條序列多存幾份 state checkpoint(vLLM 對 Kimi K3 每 32K tokens 加上 prompt 邊界各存一份),每 session 的總量查無公開資料。

**表 4-3 原廠 API 的 context、最大輸出與牌價**(US$ / 1M tokens;等級 C;2026-10-04 經摘要式擷取工具讀取,發布前需對原頁複核。)

| API model id | 對應開源模型 | context | 最大輸出 | 輸入(cache miss) | 快取輸入 | 輸出 | 來源 |
|---|---|---|---|---|---|---|---|
| Moonshot `kimi-k3` | Kimi K3 | 1,048,576 | 預設 131,072,上限 1,048,576 | 3.00 | 0.30 | 15.00 | [Kimi pricing](https://platform.kimi.ai/docs/pricing/chat)、[K3 quickstart](https://platform.kimi.ai/docs/guide/kimi-k3-quickstart) |
| Moonshot `kimi-k2.7-code` | Kimi K2.7-Code | 262,144 | 未載明 | 0.95 | 0.19 | 4.00 | [Kimi pricing](https://platform.kimi.ai/docs/pricing/chat) |
| Z.ai GLM-5.3 | GLM-5.3 | 1M | 128K | 1.40 | 0.26 | 4.40 | [Z.ai pricing](https://docs.z.ai/guides/overview/pricing)、[GLM-5.3 guide](https://docs.z.ai/guides/llm/glm-5.3) |
| Z.ai GLM-5.3-Flash | GLM-5.3-Flash | 未讀到(model card 為 1M) | 未讀到 | 0.15 | 0.03 | 0.50 | [Z.ai pricing](https://docs.z.ai/guides/overview/pricing) |
| DeepSeek `deepseek-v4-pro` | DeepSeek-V4-Pro-0813 | 1M | 384K | 1.32(離峰 0.66) | 0.044(離峰 0.022) | 3.96(離峰 1.98) | [DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing) |
| DeepSeek `deepseek-flash` | DeepSeek-V4.1-Flash | 1M | 384K | 0.30(離峰 0.15) | 0.006(離峰 0.003) | 1.20(離峰 0.60) | [DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing) |
| Alibaba `qwen3.8-max` | 以 Qwen3.8-2.4T-A95B 為基礎 | 1M(最大輸入 991K;thinking 模式 983K) | 131K,另加最多 262K reasoning tokens | 2.00 | 0.25(implicit cache) | 6.00 | [Qwen Cloud](https://www.qwencloud.com/models/qwen3.8-max)、[Model Studio pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing) |
| Alibaba `qwen3.8-flash` | 以 Qwen3.8-Flash-Next 為基礎 | 1M(最大輸入 991K) | 131K,另加最多 262K reasoning tokens | 0.15 | 0.016(implicit cache) | 0.47 | [Qwen Cloud](https://www.qwencloud.com/models/qwen3.8-flash) |

- 四家的 API 文件都沒有寫生成速度;原廠端點的實測速度見下一節。限流:DeepSeek 為 500(`deepseek-v4-pro`)與 2,500(`deepseek-flash`)個並行請求,Alibaba 為 2M TPM、15K RPM,Moonshot 依儲值分 Tier0–Tier5(並行 1–100、RPM 3–300、TPM 500,000–5,000,000,[Kimi rate limits](https://platform.kimi.ai/docs/pricing/limits)),Z.ai 未載明。
- **開源與僅 API**:四家旗艦都有公開權重。僅以 API 提供的是 Alibaba 的 qwen3.7-max、qwen3.7-plus、qwen3.6-plus、qwen3.6-max-preview、qwen3.5-plus,以及加速層 `kimi-k2.7-code-highspeed` 與 GLM-5.3-FlashX;DeepSeek 查無僅 API 的名稱,API model id 直接對應公開 checkpoint。
- 代管的 Qwen3.8-Max 比開源的 Qwen3.8-2.4T-A95B 多了 vision input、non-thinking 與預設 1M context;開源版只收文字且 thinking 無法關閉([card](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B))。

對常見假設的修正(以筆記查證結果為準):

- Kimi 的序列是 K2 → K2-0905 → K2 Thinking → K2.5 → K2.6 → K2.7-Code → K3。K3 是 2.78T / 104.2B 啟用,公開 checkpoint 只有 MXFP4 一種,且 config 為 `num_nextn_predict_layers=0`(tech report 寫 1 層 MTP),spec decode 靠另行釋出的 DSpark draft([tech report](https://github.com/MoonshotAI/Kimi-K3/blob/main/k3_tech_report.pdf)、[config](https://huggingface.co/moonshotai/Kimi-K3/raw/main/config.json))。
- GLM-5.3 與 GLM-5.2 是同一個 78 層 MLA base,GLM-5.3 只做 post-training。參數量有三個寫法:Z.ai 的 744B / 40B、Hugging Face tensor count 的 753B、vLLM recipe 的 743B / 39B;GLM-5.3-Flash 則是另一個架構(320B / 18B)。
- DeepSeek V4 已有帶日期的 GA checkpoint(Flash-0731、Pro-0813);2026-09-10 起 API 的 V4 Flash id 都導向 V4.1-Flash。V4-Flash 的參數量在 card 是 284B,vLLM blog 寫 285B。
- Qwen3.7 只有代管版。Qwen3.5 / 3.6 / 3.8 的 config 原生 context 都是 262,144,自架要到 1M 是引擎設定(YaRN),不是預設。
- tensor parallel 會在每個 rank 複製一份 MLA latent KV,所以 MLA 家族的 KV 容量取決於單一裝置的記憶體而不是裝置數,除非改用 DCP 或 DEP([vLLM 2026-09-13](https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-09-13-kimi-k3-performance-optimization.md))。

## 各晶片實測 TPS 與 TTFT

四個家族的現役旗艦(Kimi K3、GLM-5.3、DeepSeek V4 Pro 0813、DeepSeek V4.1 Flash、Qwen3.8 2.4T A95B)在 2026-10-04 都沒有公開的 ASIC 端點;ASIC 上只有 Qwen3.8 27B(Cerebras 公開、Groq Preview)、DeepSeek V3.1 / V3.2(SambaNova,128K / 32K context)與 Kimi K2.7 Code(Tenstorrent,2026-10-03 起列於 OpenRouter)。旗艦在 Artificial Analysis 10K workload 的最快端點為 185–723 t/s,依廠商自述全部是 GPU 上的軟體堆疊;公開端點上量得到的硬體效應只有 Cerebras 在 gpt-oss-120b 上的 5.5×(AA)與在 Qwen3.8 27B 上的約 9×(OpenRouter);另有一筆 Kimi K2.6 私有企業端點的非同時量測(3.7–3.9×,表 4-23)。

本節的 t/s 指單一請求串流的 output tokens/s(每使用者速度),不是系統吞吐量。

### 量測來源與兩者的差異

**表 4-4 Artificial Analysis 與 OpenRouter 的量測方法**(來源:[AA methodology](https://artificialanalysis.ai/methodology/performance-benchmarking)、[OpenRouter routing](https://openrouter.ai/docs/features/provider-routing))

| 來源 | 方法 | prompt 長度 | 統計口徑 | 適合用來看 |
|---|---|---|---|---|
| Artificial Analysis(AA) | 從 Google Cloud us-central1 的 VM 送出合成的單一請求;每次都是新產生的 prompt(無快取);reasoning 模型的 TTFT 是第一個 reasoning token | 預設約 10,000 input tokens、至少 1,500 answer tokens;另有 1K、100K 與 10 個並行 1K | 過去 72 小時 P50(100K 為過去 14 天 P50);以 tiktoken `o200k_base` 計 token | 同條件的供應商排名、長 prompt 行為 |
| OpenRouter | 經 OpenRouter 路由的真實客戶流量遙測,按供應商端點分開統計 | 不受控,未公布 | 30 分鐘視窗的 p50–p99 latency 與 throughput,附請求數 | 端點廣度、max output、量化標籤、uptime、尾端延遲 |

- 兩者的數值層級不能互比,因此分表呈現。AA 榜首的 LithosAI、Inco、Supernova、Systalyze 都不是 OpenRouter 供應商,所以 OpenRouter 對 Kimi K3、GLM 5.x、DeepSeek V4.x 的最大值(121–237 t/s)遠低於 AA(271–723 t/s)。
- OpenRouter 文件沒有逐字定義「latency」與「throughput」;本章依其模型頁的標示視為 TTFT 與 output tokens/s。
- 同一批 OpenRouter 端點在 2026-10-04 的 00:52 與 05:37 UTC 兩次快照之間,p50 throughput 的變動中位數為 7%–30%(D),排名差距小於約 25% 應視為雜訊。

### ASIC 端點上實際提供的模型

**表 4-5 ASIC 雲在四個家族中列出的模型**(2026-10-04;廠商數字為 C,獨立量測為 A)

| ASIC 雲 | 模型 | 狀態 | context / max output | 價格 $/1M in / out | 廠商宣稱速度(C) | 獨立量測(A) | 來源 |
|---|---|---|---|---|---|---|---|
| Cerebras(wafer-scale) | Qwen3.8 27B | 公開;2026-09-03 上線 | OpenRouter 所列 65,536 / 32,768;Cerebras 文件的付費層為 131,072 / 40,960 | 0.99 / 1.49 | 約 1,850 t/s | OpenRouter p50 1,025 t/s、p90 1,359;latency p50 0.17 s、p90 0.28 s;30 分鐘 1,096 個請求。AA 未測 | [OR qwen3.8-27b](https://openrouter.ai/qwen/qwen3.8-27b)、[Cerebras docs](https://inference-docs.cerebras.ai/models/qwen-3.8-27b) |
| Groq(LPU) | Qwen3.8-27B | Preview | 131,072 / 16,384 | 0.80 / 4.00 | 「450」t/s;developer plan 250K TPM、1K RPM | 無:AA 與 OpenRouter 都沒有這個端點 | [Groq docs](https://console.groq.com/docs/models) |
| SambaNova(RDU) | DeepSeek-V3.1 | Production | 128K;OpenRouter 所列 max output 7,168 | 3.00 / 4.50 | 未提供 | AA 列出端點但沒有速度資料 | [SambaNova docs](https://docs.sambanova.ai/docs/en/models/sambacloud-models) |
| SambaNova(RDU) | DeepSeek-V3.2 | Preview(容量有限,可能短期下架) | 32K(OpenRouter 32,768 / 7,168;AA 列 8K) | 3.00 / 4.50 | 未提供 | OpenRouter p50 51 t/s、p90 148;latency p50 1.65 s;124 個請求;uptime 93.41% | [SambaNova docs](https://docs.sambanova.ai/docs/en/models/sambacloud-models)、[OR deepseek-v3.2](https://openrouter.ai/deepseek/deepseek-v3.2) |
| Tenstorrent(Blackhole) | Kimi K2.7 Code(fp8) | 列於 OpenRouter;端點建立於 2026-10-03 | 256,000 / 128,000 | 0.85 / 3.00 | 未提供 | OpenRouter p50 147 t/s、p90 172;latency p50 0.25 s、p90 0.46 s、p99 0.74 s;427 個請求 | [OR kimi-k2.7-code](https://openrouter.ai/moonshotai/kimi-k2.7-code) |

- Cerebras、Groq、SambaNova 都沒有 Kimi K3、GLM-5.x、DeepSeek V4.x 或 Qwen3.8 2.4T 的公開端點([AA leaderboard](https://artificialanalysis.ai/leaderboards/providers));兩個來源也都沒有揭露任何 Trainium 或 TPU 端點。
- ASIC 端點的 context 較短:Cerebras 的 Qwen3.8 27B 為 65,536(其他主機 262,144 或 1,000,000),SambaNova 的 DeepSeek V3.2 為 32,768(其他主機 131,072–163,840)。
- Kimi K2.7 Code 在 Tenstorrent 的 p50 速度(147 t/s)低於 GPU 主機 CoreWeave(209)與 Nebius(175),但 p50 latency(0.25 s)是 13 個端點中最低的。

### 旗艦模型:最快、中位與原廠 API

**表 4-6 Artificial Analysis:10K workload 的最快端點、全部端點中位與原廠 API**(72 小時 P50;2026-10-04 05:45–05:47 UTC 擷取;等級 A,中位數與倍數為 D。儲存格為「t/s;TTFT 秒」。)

| 模型(AA 變體) | 有速度資料的端點數 | 最快端點:t/s;TTFT (s);硬體 | 全部端點中位 | 原廠 API | 最快 ÷ 中位 | 最快 ÷ 原廠 | 來源 |
|---|---|---|---|---|---|---|---|
| Kimi K3(max) | 17 | LithosAI(ULTRA CHAT):320;0.74;GPU(廠商自述,C) | 138;1.18 | Kimi:40;4.06 | 2.3× | 8.0× | [AA](https://artificialanalysis.ai/models/kimi-k3/providers) |
| Kimi K2.7 Code | 6 | CoreWeave:257;1.06;GPU 雲(加速器未揭露) | 97;2.66 | Kimi:97;3.07 | 2.7× | 2.7× | [AA](https://artificialanalysis.ai/models/kimi-k2-7-code/providers) |
| GLM-5.3(max) | 25 | Supernova(FP4, FAST):555;155.14;GPU(C)。TTFT 正常的最快者是 LithosAI(FP4):474;0.77 | 196;1.00 | Zai:71;2.92 | 2.8× | 7.8× | [AA](https://artificialanalysis.ai/models/glm-5-3/providers) |
| GLM-5.3-Flash | 21 | LithosAI(FP4, ULTRA CHAT):723;0.46;GPU(C) | 111;1.35 | Zai:53;3.31 | 6.5× | 13.6× | [AA](https://artificialanalysis.ai/models/glm-5-3-flash/providers) |
| DeepSeek V4 Pro 0813(max) | 9 | Systalyze:271;1.51;GPU 最佳化平台(C,加速器廠商未具名) | 85;1.69 | DeepSeek:116;1.73 | 3.2× | 2.3× | [AA](https://artificialanalysis.ai/models/deepseek-v4-pro/providers) |
| DeepSeek V4.1 Flash(max) | 22 | LithosAI(ULTRA CHAT):674;0.89;GPU(C) | 216;0.90 | DeepSeek:210;1.09 | 3.1× | 3.2× | [AA](https://artificialanalysis.ai/models/deepseek-v4-1-flash/providers) |
| Qwen3.8 2.4T A95B | 6 | Together AI:185;0.87;GPU(NVIDIA 稱其跑在 Blackwell,C) | 114;0.95 | Alibaba Cloud:38;2.76 | 1.6× | 4.9× | [AA](https://artificialanalysis.ai/models/qwen3-8-2-4t-a95b/providers) |
| Qwen3.8 27B(xhigh) | 8 | Multiverse Computing:194;0.80;GPU 雲(加速器未揭露) | 68;1.10 | Alibaba Cloud:46;3.73 | 2.8× | 4.2× | [AA](https://artificialanalysis.ai/models/qwen3-8-27b/providers) |

**表 4-7 OpenRouter:同一批模型在即時流量下的 p50**(30 分鐘視窗;2026-10-04 05:36–05:37 UTC 擷取;等級 A,中位數為 D)

| 模型 | 有遙測的端點數 | 最快 p50 t/s(供應商) | 端點 p50 的中位 t/s | 原廠 p50 t/s;latency (s) | latency 中位:p50 / p90 (s) | 最低 p50 latency (s)(供應商) | 來源 |
|---|---|---|---|---|---|---|---|
| Kimi K3 | 22 | 121(Amazon Bedrock,us-east-2) | 58 | 30;4.32 | 1.22 / 2.98 | 0.48(Makora) | [OR](https://openrouter.ai/moonshotai/kimi-k3) |
| Kimi K2.7 Code | 13 | 209(CoreWeave,int4) | 72 | 72;1.25 | 1.25 / 3.58 | 0.25(Tenstorrent) | [OR](https://openrouter.ai/moonshotai/kimi-k2.7-code) |
| GLM 5.3 | 40 | 169(Together) | 93 | 51;2.78 | 1.03 / 3.16 | 0.29(Friendli) | [OR](https://openrouter.ai/z-ai/glm-5.3) |
| GLM 5.3 Flash | 35 | 174(Friendli) | 60 | 54;3.45 | 1.11 / 4.02 | 0.36(Modal) | [OR](https://openrouter.ai/z-ai/glm-5.3-flash) |
| DeepSeek V4 Pro 0813 | 20 | 126(CoreWeave,fp8) | 56 | 63;1.17 | 1.43 / 2.95 | 0.52(CoreWeave) | [OR](https://openrouter.ai/deepseek/deepseek-v4-pro-0813) |
| DeepSeek V4.1 Flash | 30 | 226(Together) | 107 | 104;0.89 | 0.91 / 2.27 | 0.25(Together) | [OR](https://openrouter.ai/deepseek/deepseek-v4.1-flash) |
| Qwen3.8 2.4T A95B | 7 | 142(Modal) | 35 | 33;4.11 | 1.60 / 4.39 | 0.29(DeepInfra) | [OR](https://openrouter.ai/qwen/qwen3.8-2.4t-a95b) |
| Qwen3.8 27B | 17 | 1,025(Cerebras,fp16) | 68 | 29;4.30 | 0.75 / 2.07 | 0.17(Cerebras) | [OR](https://openrouter.ai/qwen/qwen3.8-27b) |

- 旗艦最快的端點都是 GPU 軟體堆疊(C,廠商自述):LithosAI 寫「Standard GPUs」,其主打數字量自一台 8× B300([LithosAI](https://www.lithosai.com/));Inco 是 GPU fleet 加 DFlash speculative decoding 與自家 NVFP4 checkpoint([Inco](https://inco.ai/blog/inco-platform-aa/));Supernova 跑在租來的 GPU、把 KV cache 放在 NAND([Supernova](https://supernova-labs.ai/));Systalyze 是 GPU 最佳化平台([Systalyze](https://www.systalyze.com/))。因此 1.6×–3.2× 的「最快 ÷ 中位」是供應商與 serving stack 的效應,不是晶片差異。
- 原廠 API 多半落在慢的一端:Kimi K3 在 Moonshot 為 40 t/s、TTFT 4.06 s(17 個端點中最慢),Qwen3.8 2.4T 在 Alibaba Cloud 為 38 t/s(6 個中最慢)。DeepSeek 例外,V4 Pro 0813 的原廠 API 排第 2(116 t/s)。
- FAST / ULTRA 層多半高於牌價:Kimi K3 在 LithosAI ULTRA CHAT 為 $5.60 / $28、Inco FAST 為 $6 / $30,牌價是 $3 / $15。這些加速層在 AA 的頁面上沒有 Endpoint Accuracy Index 數值。
- 廠商宣稱與 AA 同日量測的落差(C 對 A):LithosAI 宣稱 Kimi K3 每使用者峰值「800 tokens/second」,AA 量到 320 t/s;Crusoe 宣稱 Kimi K2.6 / K2.7「430+」t/s([Crusoe](https://www.crusoe.ai/resources/blog/430-tokens-per-second-optimizing-kimi-k2-6-and-k2-7-for-production)),AA 無資料,OpenRouter 量到 85 t/s p50([OR](https://openrouter.ai/moonshotai/kimi-k2.6))。

### 同權重跨硬體:gpt-oss-120b 與 Qwen3.8 27B

**表 4-8 Artificial Analysis:同一份權重在不同硬體類別的 10K workload 結果**(2026-10-04 05:46 UTC;等級 A;硬體類別為筆記的標註,GPU 型號為 C。來源:[AA gpt-oss-120b](https://artificialanalysis.ai/models/gpt-oss-120b/providers)、[AA Qwen3.8 27B](https://artificialanalysis.ai/models/qwen3-8-27b/providers)。AA 沒有 Cerebras 的 Qwen3.8 27B 資料。)

| 模型 | 供應商 | 硬體類別 | context | t/s | TTFT (s) | E2E (s) | 價格 $/1M in / out |
|---|---|---|---|---|---|---|---|
| gpt-oss-120b(high) | Cerebras | wafer-scale ASIC(WSE-3) | 131K | 1,764 | 0.42 | 1.8 | 0.35 / 0.75 |
| gpt-oss-120b(high) | SambaNova | RDU ASIC | 131K | 706 | 1.14 | 4.7 | 0.22 / 0.59 |
| gpt-oss-120b(high) | Groq | LPU ASIC | 131K | 473 | 0.74 | 6.0 | 0.15 / 0.6 |
| gpt-oss-120b(high) | Microsoft Azure | 超大規模雲,硬體未揭露 | 131K | 320 | 0.74 | 8.6 | 0.15 / 0.6 |
| gpt-oss-120b(high) | Nebius(Base) | GPU 雲 | 128K | 280 | 0.97 | 9.9 | 0.15 / 0.6 |
| gpt-oss-120b(high) | DeepInfra(Turbo) | GPU 雲(NVIDIA Blackwell) | 131K | 248 | 0.81 | 10.9 | 0.15 / 0.6 |
| gpt-oss-120b(high) | Crusoe | GPU 雲(型號未揭露) | 131K | 233 | 0.41 | 11.2 | 0.05 / 0.2 |
| gpt-oss-120b(high) | Baseten | GPU 雲(NVIDIA Blackwell) | 128K | 221 | 0.18 | 11.5 | 0.1 / 0.5 |
| gpt-oss-120b(high) | Amazon Bedrock | 超大規模雲,硬體未揭露 | 131K | 83 | 1.08 | 31.2 | 0.15 / 0.6 |
| gpt-oss-120b(high) | Google Vertex | 超大規模雲,硬體未揭露 | 131K | 45 | 95.92 | 152.0 | 0.09 / 0.36 |
| Qwen3.8 27B(xhigh) | Multiverse Computing | GPU 雲 | 262K | 194 | 0.80 | 13.7 | 0.4 / 2 |
| Qwen3.8 27B(xhigh) | Crusoe | GPU 雲 | 262K | 189 | 0.86 | 14.1 | 0.25 / 2 |
| Qwen3.8 27B(xhigh) | Parasail(FP8) | GPU 雲 | 262K | 78 | 1.30 | 33.5 | 0.24 / 2.2 |
| Qwen3.8 27B(xhigh) | Alibaba Cloud(原廠) | 未揭露 | 1M | 46 | 3.73 | 58.3 | 0.5 / 3 |

**表 4-9 OpenRouter:同一份權重在不同硬體類別的即時流量結果**(2026-10-04 05:36–05:37 UTC;30 分鐘視窗;等級 A。來源:[OR gpt-oss-120b](https://openrouter.ai/openai/gpt-oss-120b)、[OR qwen3.8-27b](https://openrouter.ai/qwen/qwen3.8-27b)。)

| 模型 | 供應商(tag) | 硬體類別 | context;max output | p50 t/s(p90) | p50 latency s(p90) | 30 分鐘請求數 | 價格 $/1M in / out |
|---|---|---|---|---|---|---|---|
| gpt-oss-120b | Cerebras(`cerebras/fp16`) | wafer-scale ASIC | 131K;41K | 946(1,748) | 0.20(0.54) | 19,468 | 0.35 / 0.75 |
| gpt-oss-120b | SambaNova(`sambanova`) | RDU ASIC | 131K;131K | 374(528) | 0.82(1.78) | 659 | 0.14 / 0.95 |
| gpt-oss-120b | Groq(`groq`) | LPU ASIC | 131K;66K | 355(437) | 0.14(0.45) | 43,439 | 0.15 / 0.6 |
| gpt-oss-120b | Amazon Bedrock(`amazon-bedrock`) | 硬體未揭露 | 131K;未列 | 234(387) | 0.55(1.04) | 1,415 | 0.15 / 0.6 |
| gpt-oss-120b | Crusoe(`crusoe/bf16`) | GPU 雲 | 131K;131K | 230(265) | 0.25(0.39) | 11,420 | 0.05 / 0.25 |
| gpt-oss-120b | Baseten(`baseten/fp4`) | GPU 雲 | 128K;128K | 217(279) | 0.25(0.43) | 3,753 | 0.1 / 0.5 |
| gpt-oss-120b | Google Vertex(`google-vertex/global`) | 硬體未揭露 | 131K;131K | 100(269) | 1.57(9.95) | 4,407 | 0.09 / 0.36 |
| Qwen3.8 27B | Cerebras(`cerebras/fp16`) | wafer-scale ASIC | 66K;33K | 1,025(1,359) | 0.17(0.28) | 1,096 | 0.99 / 1.49 |
| Qwen3.8 27B | DekaLLM(`dekallm`) | 第三方主機,加速器未揭露 | 262K;未列 | 113(176) | 0.72(1.72) | 6,594 | 0.049 / 3 |
| Qwen3.8 27B | Parasail(`parasail/fp8`) | 第三方主機,加速器未揭露 | 262K;262K | 83(113) | 0.80(1.37) | 2,154 | 0.24 / 2.2 |
| Qwen3.8 27B | CoreWeave(`coreweave/fp8`) | GPU 雲 | 262K;262K | 64(71) | 0.75(1.95) | 288 | 0.4 / 3 |
| Qwen3.8 27B | Alibaba Cloud Int.(`alibaba`,原廠) | 未揭露 | 1M;131K | 29(55) | 4.30(16.71) | 24,226 | 0.425 / 2.55 |

- gpt-oss-120b 的硬體效應(D,AA 10K):Cerebras ÷ Azure(最快的非 ASIC 端點)= 1,764 ÷ 320 = 5.5×;Cerebras ÷ Nebius(最快的已揭露 GPU 雲)= 6.3×;SambaNova ÷ Azure = 2.2×;Groq ÷ Azure = 1.5×。
- Qwen3.8 27B 的硬體效應(D,OpenRouter):Cerebras ÷ 次快端點 = 1,025 ÷ 113 = 9.1×;÷ 17 個端點的中位(68 t/s)= 15×。代價是 context 只有四分之一(65,536 對 262,144),輸入單價 $0.99 對 GPU 主機的 $0.024–$0.45。
- Cerebras 在 gpt-oss-120b 的廠商數字約 3,000 t/s(C),AA 量到 1,764 t/s,OpenRouter p50 為 946 t/s;同一端點的 Qwen3.8 27B 廠商數字約 1,850 t/s,OpenRouter p50 為 1,025、p90 為 1,359 t/s。
- 速度與端點保真度是兩回事:gpt-oss-120b 的 AA Endpoint Accuracy Index 為 Cerebras 87.3 與 Groq 86.4(低於 reference)、SambaNova 98.2 與 Amazon Bedrock 100.8(在 reference 內)、Google Vertex 72.2。
- Google Vertex 的 gpt-oss-120b 端點當日狀態異常(AA 的 TTFT 中位 95.92 s;OpenRouter 一日 uptime 51.02%),不能代表 Google 的硬體。

### prompt 由 1K、10K 到 100K

**表 4-10 各模型在 1K / 10K / 100K workload 的端點中位**(AA;1K 與 10K 為 72 小時 P50,100K 為 14 天 P50;只計三種 workload 都有資料的端點;2026-10-04;跨端點中位為 D。來源同表 4-6 與表 4-8 的 AA 模型頁。)

| 模型 | 端點數 | TTFT 中位 1K (s) | TTFT 中位 10K (s) | TTFT 中位 100K (s) | 速度中位 1K (t/s) | 速度中位 10K (t/s) | 速度中位 100K (t/s) |
|---|---|---|---|---|---|---|---|
| Kimi K3 | 17 | 0.73 | 1.18 | 6.25 | 115 | 138 | 85 |
| Kimi K2.7 Code | 5 | 0.97 | 2.25 | 9.74 | 94 | 97 | 72 |
| GLM-5.3 | 24 | 0.52 | 0.96 | 6.60 | 193 | 199 | 164 |
| GLM-5.3-Flash | 20 | 0.65 | 1.24 | 6.17 | 122 | 122 | 142 |
| DeepSeek V4 Pro 0813 | 9 | 1.20 | 1.69 | 6.25 | 79 | 85 | 125 |
| DeepSeek V4.1 Flash | 22 | 0.71 | 0.90 | 4.70 | 205 | 216 | 202 |
| Qwen3.8 2.4T | 6 | 0.71 | 0.95 | 7.62 | 115 | 114 | 76 |
| Qwen3.8 27B | 7 | 0.58 | 1.19 | 10.01 | 78 | 74 | 72 |
| gpt-oss-120b | 16 | 0.52 | 0.81 | 3.73 | 207 | 208 | 150 |

**表 4-11 代表性端點的 1K → 10K → 100K 與 10 個並行 1K**(AA,2026-10-04;等級 A。儲存格為「t/s;TTFT 秒」,100K 欄再加 E2E 秒。)

| 模型 | 端點 | 硬體類別 | 1K | 10K | 100K(t/s;TTFT;E2E) | 10 並行 1K | 來源 |
|---|---|---|---|---|---|---|---|
| gpt-oss-120b | Cerebras | wafer-scale ASIC | 1,752;0.19 | 1,764;0.42 | 1,225;3.44;5.5 | 1,666;0.22 | [AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |
| gpt-oss-120b | SambaNova | RDU ASIC | 762;0.59 | 706;1.14 | 360;6.78;13.7 | 740;0.59 | [AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |
| gpt-oss-120b | Groq | LPU ASIC | 474;0.23 | 473;0.74 | 476;4.88;10.1 | 313;0.23 | [AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |
| gpt-oss-120b | Baseten | GPU(NVIDIA Blackwell,C) | 217;0.25 | 221;0.18 | 332;1.25;8.8 | 206;0.41 | [AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |
| gpt-oss-120b | Amazon Bedrock | 硬體未揭露 | 79;0.80 | 83;1.08 | 35;3.74;74.2 | 135;1.68 | [AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |
| gpt-oss-120b | Google Vertex | 硬體未揭露 | 54;6.89 | 45;95.92 | 86;3.72;32.7 | 33;2.78 | [AA](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |
| Kimi K3 | LithosAI(ULTRA CHAT) | GPU(C) | 322;0.36 | 320;0.74 | 276;6.25;15.3 | 412;13.14 | [AA](https://artificialanalysis.ai/models/kimi-k3/providers) |
| Kimi K3 | Amazon Bedrock | 硬體未揭露 | 191;0.80 | 182;1.30 | 108;9.85;33.1 | 210;0.79 | [AA](https://artificialanalysis.ai/models/kimi-k3/providers) |
| Kimi K3 | Kimi(原廠) | 未揭露 | 35;2.62 | 40;4.06 | 36;6.73;76.3 | 36;3.52 | [AA](https://artificialanalysis.ai/models/kimi-k3/providers) |
| GLM-5.3 | LithosAI(FP4) | GPU(C) | 511;0.33 | 474;0.77 | 425;4.97;10.9 | 362;0.51 | [AA](https://artificialanalysis.ai/models/glm-5-3/providers) |
| GLM-5.3 | Zai(原廠) | 未揭露 | 75;2.70 | 71;2.92 | 42;6.92;66.1 | 79;2.45 | [AA](https://artificialanalysis.ai/models/glm-5-3/providers) |
| DeepSeek V4 Pro 0813 | Systalyze | GPU(C) | 286;0.98 | 271;1.51 | 215;6.17;17.8 | 147;1.45 | [AA](https://artificialanalysis.ai/models/deepseek-v4-pro/providers) |
| DeepSeek V4 Pro 0813 | DeepSeek(原廠) | 未揭露 | 115;1.07 | 116;1.73 | 66;8.38;46.1 | 113;1.02 | [AA](https://artificialanalysis.ai/models/deepseek-v4-pro/providers) |
| DeepSeek V4.1 Flash | LithosAI(ULTRA CHAT) | GPU(C) | 749;0.70 | 674;0.89 | 693;40.47;44.1 | 761;21.42 | [AA](https://artificialanalysis.ai/models/deepseek-v4-1-flash/providers) |
| DeepSeek V4.1 Flash | Together AI | GPU(C) | 297;0.22 | 325;0.30 | 149;3.47;20.3 | 325;0.22 | [AA](https://artificialanalysis.ai/models/deepseek-v4-1-flash/providers) |
| Qwen3.8 2.4T A95B | Modal | GPU 雲 | 200;0.40 | 178;0.79 | 92;4.18;31.3 | 133;0.51 | [AA](https://artificialanalysis.ai/models/qwen3-8-2-4t-a95b/providers) |
| Qwen3.8 27B | Crusoe | GPU 雲 | 208;0.34 | 189;0.86 | 190;7.52;20.6 | 217;0.44 | [AA](https://artificialanalysis.ai/models/qwen3-8-27b/providers) |

- prompt 從 1K 拉到 100K,各模型的 TTFT 中位放大約 5×–17×(0.5–1.2 s 變成 3.7–10 s),端點中位的輸出速度只掉 0–40%。AA 最長只測到 100K,200K–1M 的區間查無公開資料。
- 由 100K 的 TTFT 反推未快取的 prefill 速率(D;TTFT 還含排隊與網路,所以算出來的是下限):Kimi K3 的端點中位約 16,000 tokens/s(100,000 ÷ 6.25 s);gpt-oss-120b 上 Baseten 80,000、Crusoe 47,000、Cerebras 29,000、Groq 20,500、SambaNova 14,700 tokens/s。

```latex
R_{\mathrm{prefill}} \ge \frac{100{,}000\ \mathrm{tokens}}{\mathrm{TTFT}_{100\mathrm{K}}}
```

- ASIC 的優勢隨 prompt 變長而縮小(D):gpt-oss-120b 的 E2E 在 10K 時 Cerebras 比最快的非 ASIC 端點快 4.6×(1.84 s 對 Azure 的 8.55 s),在 100K 時只剩 1.6×(5.48 s 對 Baseten 的 8.77 s)。Cerebras 與 SambaNova 在 100K 分別掉 31% 與 49% 的輸出速度,Groq 持平(473 → 476 t/s)。
- 加速層在長 prompt 或並行下不穩:Kimi K3 的 Inco(FAST)在 100K 的 TTFT 為 106 s,GLM-5.3 的 Supernova(FP4, FAST)在 10K 為 155 s,DeepSeek V4.1 Flash 的 LithosAI(ULTRA)在 100K 為 198 s。筆記推測是優先通道容量有限造成排隊(D),AA 的並行測試一天只跑一次。
- AA 的 TTFT 是未快取的 prefill;同一模型在不同主機的 prompt cache 命中率差距很大(Kimi K3:Fireworks FAST 100%、Moonshot 97%、Amazon Bedrock 82%、Parasail 68%),會同時改變長 context agent 的延遲與成本。

### 超大規模雲代管端點(硬體未揭露)

**表 4-12 Amazon Bedrock、Google Vertex AI、Azure AI Foundry 上四個家族模型的 AA 實測**(10K workload;AA leaderboard 2026-10-04 00:47 UTC 的副本;等級 A。來源:[AA leaderboard](https://artificialanalysis.ai/leaderboards/providers)。)

| 服務 | 模型(AA 標籤) | context | t/s | TTFT (s) | TTFAT (s) | E2E (s) |
|---|---|---|---|---|---|---|
| Amazon Bedrock | Kimi K3(max),`global.moonshotai.kimi-k3` | 1M | 172 | 1.33 | 13.0 | 15.9 |
| Amazon Bedrock | Kimi K2.5 | 256K | 98 | 1.30 | 31.7 | 36.8 |
| Amazon Bedrock | DeepSeek V3.2 | 128K | 75 | 1.55 | 28.1 | 34.7 |
| Amazon Bedrock | GLM-4.7 | 200K | 71 | 1.45 | 29.8 | 36.9 |
| Amazon Bedrock | Qwen3 Coder 480B | 262K | 112 | 1.26 | 1.3 | 5.7 |
| Google Vertex AI | GLM-5 | 200K | 85 | 1.31 | 37.8 | 43.7 |
| Google Vertex AI | Kimi K2 Thinking | 262K | 240 | 0.76 | 9.1 | 11.2 |
| Azure AI Foundry | DeepSeek V4 Pro(max;2026-04-23 版權重) | 1M | 90 | 1.66 | 50.2 | 55.7 |
| Azure AI Foundry | Kimi K2.6 | 262K | 235 | 1.49 | 20.5 | 22.6 |

- Amazon Bedrock 的 Kimi K3 在 05:45 UTC 的模型頁讀數是 182 t/s、TTFT 1.30 s(17 個端點中第 4),與原廠同價($3 / $15)而快 4.5×(D:182 ÷ 40)。OpenRouter 對其 us-east-2 端點量到 p50 121 t/s、p90 179;latency p50 1.17 s、p90 2.51 s、p99 12.8 s;一日 uptime 97.24%。
- 這三家都沒有揭露這些端點的加速器,所以上表不是 Trainium、TPU 或 Maia 的證據。Vertex 的兩列已 deprecated,2026-10-21 停用。
- Bedrock 與 AA 所列的 context 有出入:DeepSeek V3.2 的 Bedrock card 為 164K、AA 列 128K;Qwen3 Coder 480B 的 card 為 128K、AA 列 262K。

## 自架 benchmark 與硬體需求

GPU 是唯一有獨立第三方量測(InferenceX,等級 A)的自架平台:在 agentic trace replay、spec decode 採固定 acceptance 的條件下,4–16 張 Blackwell 級 GPU 上的單一使用者約 190–350 output tok/s(Kimi K3 216–259、GLM-5.2 272–350、DeepSeek-V4-Pro 187–312),高吞吐點每張 GPU 約 50–150 output tok/s(Kimi K3、GLM-5.2)、350–850(DeepSeek-V4-Pro 的 EP 或 P/D 佈局)、最高約 3,100(DeepSeek-V4.1-Flash)。TPU、Trainium、Cerebras 對現役旗艦都沒有公開結果:TPU 最新只到 Qwen3.5-397B 與 DeepSeek-V3,Trainium 只有 context 512–2,048 tokens 的社群移植,Cerebras 的公開目錄在這四個家族只剩 Qwen3.8 27B。

### GPU:InferenceX agentic trace replay

讀表前提(來源:[InferenceX MODELS.md](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/docs/MODELS.md),commit 2026-10-02):

- workload 是長 context、多輪、含 sub-agent 的真實流量 trace 重播。DeepSeek V4 各次執行的輸入長度為 p50 88K、p90 272K、p99 675K tokens,輸出 p50 413 tokens;Kimi K3 每輪中位 142K input、444 output tokens,每個 session 中位 65 輪。
- 「tok/s/user」是 interactivity(1 / TPOT),不含 TTFT。「低並行點」是最低並行的一點;「高吞吐點」是中位 TTFT 低於 5 s 的最高 total-throughput 點,沒有任何點符合時取最高吞吐點。
- spec decode 採固定 acceptance:每個模型用 SPEED-Bench `coding` 類別量出的一條 acceptance 曲線。Kimi K3 的 DSpark 在真實 trace 上只接受 1.18–1.68 個 token(固定值為 3.84),改用真實驗證後並行 4 / 8 的吞吐量退步 20–63%,所以開了 spec decode 的每使用者速度是上限([perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml))。
- InferenceX 的「total tokens」含輸入與跨輪重用的快取輸入,不能和 output 速率或 8K / 1K 的 total 相比。下列表格只列 output tok/s/GPU;高吞吐點的 total ÷ output 約 130–150(D,例:Kimi K3 在 GB300 為 19,303 ÷ 136 ≈ 142)。
- GPU 數為推算值(D):叢集 total tok/s ÷ 每 GPU total tok/s 後四捨五入,因為 API 的 GPU 數欄位在部分 EP 列不可靠。KV offload 只允許 CPU DRAM(每台伺服器最多 3 TB)。
- 設定由 NVIDIA、AMD 與引擎團隊提供並調校,由 SemiAnalysis 以公開的 GitHub Actions 執行;軟體每週在變,數字要連同執行日一起引用。
- 選列規則:Kimi K3 與 Qwen3.8-Flash-Next 列出 API 的全部列;其餘模型在每個「硬體 × 模式(aggregated 或 P/D disaggregation)」取高吞吐點 output tok/s/GPU 最高的一列,並略去 MI300X 與 MI325X。

**表 4-13 Kimi K3**(MXFP4,InferenceX 精度標籤 `fp4`;spec decode 標籤 `mtp` 指 DSpark draft。來源:[InferenceX API,model=Kimi-K3](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Kimi-K3),2026-10-04 擷取;等級 A。)

| 硬體 | 引擎;模式;spec decode 標籤 | 低並行點:conc;GPU 數;佈局 | 低並行:tok/s/user 中位 / P90;TTFT 中位 / P90 (s) | 高吞吐點:conc;GPU 數;佈局;KV offload | 高吞吐:output tok/s/GPU(叢集 output tok/s) | 高吞吐:tok/s/user 中位 / P90;TTFT 中位 / P90 (s) | 執行日 |
|---|---|---|---|---|---|---|---|
| H200 | vllm;aggregated;`mtp` | c1;32;TP16/EP32/DPA×2 | 5 / 5;3.73 / 5.41 | c5;32;TP16/EP32/DPA×2;無 | 1(17) | 5 / 3;4.58 / 103.67 | 2026-09-13 |
| B200 | dynamo-vllm;aggregated;`mtp` | c1;16;TP8 | 216 / 193;0.85 / 1.91 | c72;16;TP8;無 | 86(1,375) | 21 / 17;1.01 / 2.62 | 2026-10-02 |
| B200 | dynamo-vllm;aggregated;`none` | c96;16;TP8 | 11 / 9;1.22 / 3.07 | c96;16;TP8;無 | 70(1,123) | 11 / 9;1.22 / 3.07 | 2026-10-02 |
| B300 | vllm;aggregated;`mtp` | c1;8;TP8, DCP8 | 236 / 203;1.37 / 3.14 | c70;8;TP8, DCP8;mooncake 2,249 GB | 88(701) | 11 / 8;1.21 / 3.84 | 2026-08-16 |
| GB200 NVL72 | dynamo-vllm;aggregated;`mtp` | c1;16;TP16 | 223 / 198;2.20 / 3.72 | c32;16;TP8;mooncake 721 GB | 47(751) | 45 / 27;1.24 / 2.87 | 2026-09-19 |
| GB200 NVL72 | dynamo-vllm;aggregated;`none` | c8;16;TP16 | 60 / 40;1.09 / 2.29 | c96;16;TP8;mooncake 721 GB | 71(1,132) | 12 / 8;1.18 / 3.85 | 2026-09-19 |
| GB300 NVL72 | dynamo-vllm;aggregated;`mtp` | c1;8;TP8 | 258 / 224;0.74 / 1.49 | c48;8;TP8;mooncake 160 GB | 136(1,085) | 38 / 26;1.15 / 2.88 | 2026-09-15 |
| GB300 NVL72 | dynamo-vllm;P/D disagg;`mtp` | c1;32;P TP8 + D TP8×3 | 259 / 251;0.89 / 1.49 | c56;16;P TP8 + D TP8;mooncake 160 GB | 112(1,800) | 61 / 56;1.51 / 4.63 | 2026-09-15 |
| MI355X | atom;aggregated;`mtp` | c1;8;TP8 | 159 / 151;0.79 / 1.70 | c72;8;TP8, DCP8;lmcache 1,538 GB | 104(829) | 13 / 10;2.31 / 6.96 | 2026-09-29 |
| MI355X | vllm;aggregated;`mtp` | c1;8;TP8 | 172 / 155;1.01 / 2.46 | c70;8;TP8, DCP8;vllm-simple 1,799 GB | 92(734) | 12 / 9;1.32 / 3.87 | 2026-09-30 |

**表 4-14 GLM-5.2(TileRT 列為 GLM-5.3)**(spec decode 標籤皆為 `mtp`,即原生 MTP。來源:[InferenceX API,model=GLM-5.2](https://inferencex.semianalysis.com/api/v1/benchmarks?model=GLM-5.2),2026-10-04 擷取;等級 A。)

| 硬體 | 引擎;模式;精度 | 低並行點:conc;GPU 數;佈局 | 低並行:tok/s/user 中位 / P90;TTFT 中位 / P90 (s) | 高吞吐點:conc;GPU 數;佈局;KV offload | 高吞吐:output tok/s/GPU(叢集 output tok/s) | 高吞吐:tok/s/user 中位 / P90;TTFT 中位 / P90 (s) | 執行日 |
|---|---|---|---|---|---|---|---|
| H200 | dynamo-sglang;aggregated;fp8 | c2;8;TP8 | 218 / 159;0.43 / 2.10 | c4;8;TP8;hicache 1,234 GB | 15(123) | 218 / 151;0.41 / 2.48 | 2026-09-18 |
| B200 | sglang;aggregated;fp4 | c1;8;TP8 | 318 / 301;0.73 / 1.35 | c16;8;TP8;hicache 1,731 GB | 78(627) | 189 / 96;0.56 / 5.94 | 2026-09-02 |
| B200 | dynamo-sglang;P/D disagg;fp4 | c48;24;P TP8/EP8/DPA + D TP4×4 | 211 / 173;4.63 / 26.48 | c64;16;P TP8/EP8/DPA + D TP8/EP8/DPA;hicache 1,731 GB | 132(2,107) | 92 / 84;3.88 / 18.23 | 2026-10-02 |
| B300 | sglang;aggregated;fp4 | c1;8;TP8 | 282 / 273;0.77 / 1.26 | c24;8;TP8;hicache 2,399 GB | 118(943) | 150 / 86;0.60 / 2.25 | 2026-09-11 |
| GB200 NVL72 | dynamo-sglang;aggregated;fp4 | c2;8;TP8 | 347 / 299;0.24 / 0.76 | c8;8;TP8;hicache 721 GB | 53(421) | 282 / 205;0.25 / 0.77 | 2026-08-19 |
| GB200 NVL72 | dynamo-sglang;P/D disagg;fp4 | c45;32;P TP8/EP8/DPA + D TP4×6 | 225 / 192;2.12 / 6.77 | c128;32;P TP8/EP8/DPA×2 + D TP16/EP16/DPA;hicache 721 GB | 137(4,394) | 103 / 91;3.54 / 14.25 | 2026-08-19 |
| GB300 NVL72 | dynamo-sglang;aggregated;fp4 | c2;8;TP8 | 350 / 292;0.25 / 0.64 | c4;8;TP8;hicache 721 GB | 29(234) | 337 / 255;0.25 / 0.81 | 2026-10-02 |
| GB300 NVL72 | dynamo-sglang;P/D disagg;fp4 | c45;28;P TP4/EP4/DPA + D TP4×6 | 229 / 186;4.48 / 16.81 | c128;32;P TP8/EP8/DPA×2 + D TP16/EP16/DPA;hicache 721 GB | 149(4,774) | 101 / 90;2.33 / 5.81 | 2026-10-02 |
| MI355X | atom;aggregated;fp4 | c1;8;TP8 | 239 / 230;0.74 / 1.37 | c48;4;TP4, DCP4;lmcache 256 GB | 230(921) | 35 / 19;0.81 / 3.87 | 2026-09-22 |
| MI355X | tilert(GLM-5.3);P/D disagg;fp8 | c1;16;P TP8 + D TP8 | 485 / 469;2.37 / 4.35 | c1;16;P TP8 + D TP8;無 | 9(149) | 485 / 469;2.37 / 4.35 | 2026-09-24 |

**表 4-15 DeepSeek-V4-Pro 與 DeepSeek-V4.1-Flash**(V4-Pro 的標籤 `draft_model` 指 V4-Pro-0813 的 DSpark heads、`mtp` 指原生 MTP;V4.1-Flash 的 recipe 只有 DSpark 一種 spec decode,表中照錄 InferenceX 的標籤。VR200 用 pre-release 的 TensorRT-LLM。來源:[model=DeepSeek-V4-Pro](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4-Pro)、[model=DeepSeek-V4.1-Flash](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4.1-Flash),2026-10-04 擷取;等級 A。)

| 模型;硬體 | 引擎;模式;精度;spec decode 標籤 | 低並行點:conc;GPU 數;佈局 | 低並行:tok/s/user 中位 / P90;TTFT 中位 / P90 (s) | 高吞吐點:conc;GPU 數;佈局;KV offload | 高吞吐:output tok/s/GPU(叢集 output tok/s) | 高吞吐:tok/s/user 中位 / P90;TTFT 中位 / P90 (s) | 執行日 |
|---|---|---|---|---|---|---|---|
| V4-Pro;H200 | dynamo-sglang;aggregated;fp8;`draft_model` | c1;8;TP8 | 225 / 187;0.92 / 2.75 | c8;8;TP8;hicache 1,234 GB | 41(330) | 152 / 97;0.94 / 4.85 | 2026-09-16 |
| V4-Pro;B200 | vllm;aggregated;fp4;`draft_model` | c1;8;TP8 | 288 / 281;0.47 / 3.27 | c128;8;TP8/EP8/DPA;vllm-simple 1,947 GB | 456(3,645) | 68 / 58;4.68 / 17.32 | 2026-09-19 |
| V4-Pro;B200 | dynamo-sglang;P/D disagg;fp4;`mtp` | c64;16;P TP8/EP8/DPA + D TP8/EP8/DPA | 139 / 124;1.87 / 4.10 | c256;24;P TP8/EP8/DPA×2 + D TP8/EP8/DPA;hicache 1,731 GB | 346(8,299) | 90 / 78;3.68 / 12.41 | 2026-09-22 |
| V4-Pro;B300 | sglang;aggregated;fp4;`mtp` | c1;8;TP8 | 211 / 199;0.84 / 2.36 | c384;8;TP8/EP8/DPA;hicache 2,849 GB | 739(5,910) | 37 / 34;2.94 / 12.66 | 2026-09-29 |
| V4-Pro;GB200 NVL72 | dynamo-vllm;aggregated;fp4;`mtp` | c1;8;TP8 | 203 / 181;0.65 / 2.41 | c8;8;TP8;無 | 41(328) | 145 / 85;0.63 / 1.58 | 2026-08-18 |
| V4-Pro;GB200 NVL72 | dynamo-vllm;P/D disagg;fp4;`mtp` | c128;16;P TP8/EP8/DPA + D TP8/EP8/DPA | 67 / 65;2.15 / 4.36 | c576;28;P TP8/EP8/DPA×2 + D TP12/EP12/DPA;mooncake | 595(16,657) | 56 / 52;3.16 / 6.34 | 2026-08-18 |
| V4-Pro;GB300 NVL72 | dynamo-sglang;aggregated;fp4;`draft_model` | c1;8;TP8 | 312 / 288;0.63 / 1.74 | c8;4;TP4;無 | 93(374) | 207 / 146;0.61 / 1.06 | 2026-09-10 |
| V4-Pro;GB300 NVL72 | dynamo-sglang;P/D disagg;fp4;`draft_model` | c480;24;P TP8/EP8/DPA + D TP16/EP16/DPA | 114 / 97;17.70 / 43.63 | c1920;48;P TP8/EP8/DPA×4 + D TP16/EP16/DPA;hicache 721 GB | 846(40,613) | 43 / 32;9.38 / 30.96 | 2026-09-10 |
| V4-Pro;VR200(Vera Rubin NVL72) | trt;P/D disagg;fp4;`mtp` | c6;28;P TP4/EP4/DPA + D TP4/EP4×6 | 292 / 276;0.55 / 1.32 | c934;32;P TP8/EP8/DPA×2 + D TP16/EP16/DPA;無 | 1,092(34,932) | 145 / 138;4.22 / 8.05 | 2026-09-10 |
| V4-Pro;MI355X | sglang;aggregated;fp4;`draft_model` | c1;8;TP8 | 230 / 216;0.80 / 1.45 | c128;8;TP8/EP8/DPA;hicache 2,399 GB | 362(2,895) | 34 / 31;3.24 / 16.36 | 2026-09-29 |
| V4-Pro;MI355X | mori-sglang;P/D disagg;fp4;`draft_model` | c4;8;P TP4 + D TP4 | 204 / 170;1.07 / 2.31 | c256;16;P TP8/EP8/DPA + D TP8/DPA;umbp-linker 2,399 GB | 449(7,191) | 75 / 63;4.86 / 15.33 | 2026-10-04 |
| V4.1-Flash;H100 | vllm;aggregated;fp4;`mtp` | c1;8;TP8 | 341 / 304;0.48 / 1.11 | c20;8;TP8;無 | 90(718) | 110 / 59;0.36 / 2.31 | 2026-09-18 |
| V4.1-Flash;H200 | vllm;aggregated;fp4;`mtp` | c1;8;TP8 | 360 / 321;0.42 / 0.79 | c32;4;TP4;無 | 231(923) | 71 / 34;0.40 / 2.73 | 2026-09-21 |
| V4.1-Flash;B200 | vllm;aggregated;fp4;`mtp` | c1;4;TP4 | 606 / 581;0.18 / 0.28 | c128;4;TP4/EP4/DPA;無 | 1,362(5,449) | 132 / 81;0.16 / 0.44 | 2026-10-03 |
| V4.1-Flash;B300 | vllm;aggregated;fp4;`mtp` | c1;4;TP4 | 599 / 575;0.29 / 0.50 | c192;2;TP2/EP2/DPA;無 | 3,059(6,119) | 60 / 41;0.25 / 0.81 | 2026-10-02 |
| V4.1-Flash;GB200 NVL72 | vllm;aggregated;fp4;`mtp` | c1;4;TP4 | 461 / 426;0.32 / 0.62 | c64;4;TP4;無 | 615(2,460) | 77 / 50;0.39 / 0.85 | 2026-09-21 |
| V4.1-Flash;GB300 NVL72 | vllm;aggregated;fp4;`mtp` | c1;4;TP4 | 621 / 599;0.17 / 0.27 | c192;2;TP2/EP2/DPA;無 | 3,108(6,217) | 62 / 44;0.24 / 0.73 | 2026-10-02 |
| V4.1-Flash;MI355X | vllm;aggregated;fp4;`mtp` | c1;4;TP4 | 380 / 347;0.23 / 0.63 | c64;2;TP2;無 | 999(1,998) | 59 / 32;0.40 / 3.31 | 2026-10-02 |

**表 4-16 Qwen3.8-Flash-Next 與 Qwen3.5-397B-A17B**(InferenceX 沒有 Qwen3.8-2.4T-A95B 與 Qwen3.8-27B 的資料。Qwen3.8-Flash-Next 在 Blackwell 用 RadixArk 的 NVFP4 build、Hopper 用 FP8;Qwen3.5-397B 用截斷到 256K 的 trace。spec decode 標籤皆為 `mtp`。來源:[model=Qwen3.8-Flash-Next](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Qwen3.8-Flash-Next)、[model=Qwen-3.5-397B-A17B](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Qwen-3.5-397B-A17B),2026-10-04 擷取;等級 A。)

| 模型;硬體 | 引擎;模式;精度 | 低並行點:conc;GPU 數;佈局 | 低並行:tok/s/user 中位 / P90;TTFT 中位 / P90 (s) | 高吞吐點:conc;GPU 數;佈局;KV offload | 高吞吐:output tok/s/GPU(叢集 output tok/s) | 高吞吐:tok/s/user 中位 / P90;TTFT 中位 / P90 (s) | 執行日 |
|---|---|---|---|---|---|---|---|
| Flash-Next;H100 | sglang;aggregated;fp8 | c1;8;TP8/EP8 | 240 / 16;0.82 / 10.60 | c16;8;TP8/EP8;無 | 72(578) | 127 / 14;1.06 / 3.55 | 2026-08-27 |
| Flash-Next;H200 | sglang;aggregated;fp8 | c1;4;TP4/EP4 | 244 / 15;0.77 / 15.32 | c16;4;TP4/EP4;無 | 153(611) | 129 / 14;0.94 / 1.95 | 2026-08-27 |
| Flash-Next;B200 | sglang;aggregated;fp4 | c1;1;TP1 | 292 / 259;0.48 / 1.09 | c16;1;TP1;無 | 638(638) | 128 / 52;0.75 / 3.84 | 2026-09-15 |
| Flash-Next;B300 | sglang;aggregated;fp4 | c1;1;TP1 | 290 / 38;0.50 / 2.56 | c16;1;TP1;無 | 709(709) | 155 / 85;0.72 / 1.60 | 2026-08-27 |
| Qwen3.5-397B;H100 | sglang;aggregated;fp8 | c1;8;TP8/EP8 | 280 / 229;0.57 / 1.45 | c12;8;TP8/EP8;hicache 1,731 GB | 58(465) | 145 / 89;1.40 / 12.14 | 2026-09-16 |
| Qwen3.5-397B;H200 | sglang;aggregated;fp8 | c2;8;TP8 | 299 / 233;0.55 / 1.39 | c24;8;TP8;hicache 1,234 GB | 110(878) | 86 / 52;0.94 / 1.89 | 2026-09-21 |
| Qwen3.5-397B;B200 | sglang;aggregated;fp4 | c1;4;TP4 | 483 / 18;0.46 / 7.28 | c32;2;TP2;hicache 599 GB | 632(1,265) | 147 / 85;1.82 / 8.79 | 2026-08-03 |
| Qwen3.5-397B;B200 | dynamo-sglang;P/D disagg;fp8 | c8;8;P TP4 + D TP4 | 427 / 355;0.32 / 0.72 | c64;8;P TP4 + D TP4;hicache 865 GB | 378(3,021) | 145 / 112;2.74 / 7.10 | 2026-09-19 |
| Qwen3.5-397B;B300 | sglang;aggregated;fp4 | c1;4;TP4 | 495 / 37;0.31 / 1.67 | c52;2;TP2/EP2;hicache 599 GB | 1,006(2,012) | 86 / 53;0.80 / 2.00 | 2026-08-03 |
| Qwen3.5-397B;B300 | dynamo-sglang;P/D disagg;fp8 | c4;8;P TP4 + D TP4 | 461 / 375;0.30 / 0.66 | c56;4;P TP2/EP2 + D TP2/EP2;hicache 599 GB | 596(2,382) | 108 / 84;1.65 / 6.16 | 2026-09-21 |
| Qwen3.5-397B;GB200 NVL72 | dynamo-sglang;aggregated;fp4 | c1;4;TP4 | 575 / 518;0.13 / 0.41 | c48;2;TP2;hicache 405 GB | 878(1,755) | 87 / 43;0.42 / 1.84 | 2026-09-11 |
| Qwen3.5-397B;GB300 NVL72 | dynamo-sglang;aggregated;fp4 | c7;8;TP8 | 562 / 518;2.47 / 10.87 | c7;8;TP8;hicache 811 GB | 43(347) | 562 / 518;2.47 / 10.87 | 2026-09-09 |
| Qwen3.5-397B;GB300 NVL72 | dynamo-sglang;P/D disagg;fp4 | c565;28;P TP1×3 + D TP4/EP4/DPA×4 | 163 / 150;3.70 / 6.57 | c704;20;P TP1×3 + D TP4/EP4/DPA×2;hicache 811 GB | 1,266(25,326) | 90 / 80;4.56 / 7.67 | 2026-09-09 |
| Qwen3.5-397B;MI355X | sglang;aggregated;fp4 | c1;4;TP4 | 446 / 395;0.41 / 0.82 | c40;2;TP2;hicache 599 GB | 737(1,473) | 104 / 64;1.69 / 3.07 | 2026-09-29 |

- KV 容量是單節點的實際瓶頸。Kimi K3 在 8× B300 扣掉權重後 HBM 只放得下 3.25M tokens;並行 16 / 24 時,KV 全留在 GPU 的組別 cache 命中率 2.7%、TTFT p50 為 86 s / 191 s、輸出 49.6 / 54.9 tok/s,開 DRAM offload 的組別則為 245 / 261 output tok/s、TTFT p50 0.85 s / 6.2 s([perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml))。
- DeepSeek-V4-Pro 在 8× B300(並行 384)的 HBM KV working set 約 43M tokens,8× B200(並行 196)約 22M([InferenceX 2026-08-25](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-b200-vs-b300-kv-working-set))。兩者都相當於每個 session 約 112K tokens 常駐 HBM(D:43M ÷ 384),可用下式粗估 session 容量:

```latex
N_{\mathrm{session}} \approx \frac{T_{\mathrm{HBM\,KV}}}{1.1 \times 10^{5}}
```

- Hopper 仍可服務 0.3T–1.6T 的 sparse attention 機型(GLM-5.2 在 8× H200 並行 2–4 為 218 tok/s/user,DeepSeek-V4-Pro 在 8× H200 並行 1 為 225),但 Kimi K3 需要 32 張 H200 且只有約 5 tok/s/user。
- Vera Rubin NVL72 只有 DeepSeek-V4-Pro 一筆(pre-release TensorRT-LLM、NVFP4):在 P90 為 100 tok/s/user 時約 59.4M total tok/s/MW,同條件下 GB300 Dynamo-SGLang 為 28.5M、B200 SGLang 為 6.95M、H200(FP8)為 2.26M、MI355X SGLang 為 2.01M;這些是含快取輸入的 total tokens([InferenceX 2026-09-14](https://inferencex.semianalysis.com/blog/vera-rubin-nvl72-agentic-inference))。

### GPU:Qwen3.8-2.4T 與其他引擎團隊量測

**表 4-17 Qwen3.8-2.4T-A95B:只有引擎團隊的數字**(等級 B;「每 GPU tok/s」是 8K / 1K 的 total,即 input + output,不是 output 速率。)

| 來源(日期) | 硬體;精度;佈局 | workload | 並行;spec decode | 每使用者 output tok/s | 每 GPU total tok/s | 備註 |
|---|---|---|---|---|---|---|
| [vLLM recipe](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-2.4T-A95B.yaml)(2026-10-03) | GB300;FP8,TP16 | 8K in / 1K out | 低並行;無 MTP / MTP-3 | 130 / 307 | 未列 | NVFP4、TP8 為 133 / 304 |
| [vLLM recipe](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-2.4T-A95B.yaml)(2026-10-03) | GB300;FP8 TP4·DP4 + EP16,或 NVFP4 DEP16 | 8K in / 1K out | 未註明 | 未列 | 最高 3,200(FP8)/ 4,300(NVFP4) | 吞吐量端 |
| [vLLM recipe](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-2.4T-A95B.yaml)(2026-10-03) | GB300 2 個 tray;NVFP4;TP8,無 EP | 8K in / 1K out | c1 / c32 / c64 / c128;spec decode 未註明 | 101 / 41.9 / 26.9 / 18.3 | 108 / 1,338 / 1,715 / 2,170 | TPOT 9.9 / 23.9 / 37.2 / 54.7 ms |
| [LMSYS](https://www.lmsys.org/blog/2026-08-12-qwen3-8-day0-support/)(2026-08-12) | 8× B300;NVFP4;TP8 | 未註明 | batch 1;原生 MTP(accept 3.3)/ DSpark(accept 4) | 346 / 378 | 未列 | 單節點 decode |
| [LMSYS](https://www.lmsys.org/blog/2026-08-12-qwen3-8-day0-support/)(2026-08-12) | GB300;NVFP4;P/D(2× PP6 prefill + DP2-attn / TP4 / EP8 decode,20 張 GPU) | 8,192 / 1,024 | accept length 固定為 3.3 | 36;低延遲端 334 | 5,126;低延遲端 108 | FP8 佈局為 30 tok/s/user 時 3,532,c1 時 362 tok/s/user、220 |
| [vLLM blog](https://vllm.ai/blog/2026-09-21-qwen38-pd-serving)(2026-09-21) | GB300 NVL72;NVFP4;P/D(48 張 GPU) | 8,192 / 1,024 | c2,560 / c512 / c128 / c32 / c16;c2,560 點無 MTP | 約 12 / 42 / 58 / 83 / 101 | 約 4,950 / 3,700 / 2,130 / 1,270 / 810 | 讀圖近似值;c1 於 16 張 GPU 為 182.1 tok/s/user |

兩份 vLLM 來源對「TP8 一個引擎能放幾個請求」差約 5×,兩者並列:

- vLLM recipe(引擎回報):NVFP4、TP8、GB300,70 GiB 的 KV 在 `max-model-len` 262,144 時保留 25 個並行請求,在 9,240 tokens(8K in + 1K out)時為 506 個。
- vLLM blog(推導):TP8 每張 GPU 留 73–83 GiB 給 KV,一個 10,240-token 請求需 759 MiB(474 MiB full attention + 285 MiB Gated DeltaNet),約 98–112 個請求;TP4 DP4 約 133.8 GiB、約 180 個。
- 筆記的調和(D,未經原作者確認):若每個 TP8 rank 只存 4 個 KV head 之一與八分之一的 linear attention head,一個 9,240-token 請求在每個 rank 佔 142 MiB,即可重現 recipe 的數字。

```latex
\frac{70\ \mathrm{GiB}}{142\ \mathrm{MiB}} \approx 504
```

```latex
\frac{73\text{–}83\ \mathrm{GiB}}{759\ \mathrm{MiB}} \approx 98\text{–}112
```

**表 4-18 其他自架量測**(非 InferenceX;每列標示並行、spec decode 與吞吐量是 output 還是 total。)

| 模型;來源(日期) | 硬體;引擎;精度 | workload | 並行;spec decode | 每使用者 tok/s | 系統吞吐量 | TTFT | 等級 |
|---|---|---|---|---|---|---|---|
| Kimi K3;[OpenZeka](https://whitepapers.openzeka.com/papers/kimi-k3-dgx-b300-inference-benchmark/)(2026-07) | 8× B300(DGX B300);vLLM,TP8;MXFP4,FP8 KV | 約 128 in / 128 out | c1;無 | 100.84 | 101 output tok/s | 平均 66.5 ms | A(短 prompt) |
| Kimi K3;同上 | 同上 | 同上 | c1;DSpark(7 tokens) | 187.74 | 188 output tok/s | 平均 71.0 ms | A(短 prompt) |
| Kimi K3;同上 | 同上 | 同上 | c16;無 / DSpark | 43.95 / 43.60 | 703 / 698 output tok/s | 平均 543.8 / 344.3 ms | A(短 prompt) |
| Kimi K3;同上 | 同上 | 同上 | c64;無 / DSpark | 27.49 / 11.21 | 1,759 / 717 output tok/s | 平均 731.7 / 1,030.9 ms | A(短 prompt) |
| GLM-5.2-FP8;[llm-d](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)(2026-07-22) | 64× H200(3 prefill + 1 decode,DEP16);vLLM;CPU KV offload | SemiAnalysis agentic trace | c128;原生 MTP | 36.6(E2E) | 6,281 output tok/s(每 GPU 98);input 431K tok/s | p50 2.18 s;p90 15.82 s | B |
| GLM-5.2-FP8;同上 | 32× H200(1 prefill + 1 decode) | 同上 | c128;MTP 開 / 關 | 35.0 / 21.6(E2E) | 5,647 / 3,505 output tok/s | p50 2.4 / 1.6 s | B |
| GLM-5.2-NVFP4;[vLLM / DaoCloud](https://vllm.ai/blog/2026-07-23-glm-5.2-nvfp4-b300-pd)(2026-07-23) | 24× B300(4 prefill + 1 decode);MTP 3 tokens | 8K input | 約 700 並行 | mean TPOT 19.21 ms | total 162,207 tok/s;output 17,647 tok/s | 平均 1.92 s | B(讀自圖片) |
| GLM-5.2-NVFP4;同上 | 同上 | 256K input | 約 25 並行 | 未列 | total 57,660 tok/s;output 219 tok/s | 平均 28.74 s;P90 53.74 s | B(讀自圖片) |
| DeepSeek-V4-Pro;[SGLang / Ant Group](https://www.lmsys.org/blog/2026-08-19-deepseek-v4-pro-engine-optimization-h20/)(2026-08-19) | 每節點 8× H20-141GB;MXFP4 experts + FP8 activations;單節點 TP8 | 輸入長度不一 | batch 1;spec decode 未註明 | 271(依輸入長度 183–271) | prefill 每節點 8.45K input tok/s | 1M-token prompt 的 prefill 為 43.7 s | B |

- OpenZeka 的結論是 spec decode 在低負載把 inter-token latency 減半,到高並行反成瓶頸(vLLM 約在並行 16 打平)。容量規劃以無 spec decode 的每使用者速度(Kimi K3 在 8 張 B300 / GB300、batch 1 約 100–118 tok/s)為基準較安全;該頁經摘要式擷取工具讀取,引用前需複核。
- llm-d 的 GLM-5.2 執行中,輸入佔全部 token 的 98.6%,所以瓶頸在 prefill 容量;MTP 每個 decode step 約吐出 2.95 個 token。

### GPU 硬體需求

- GPU 數下限由權重決定(D):`vram_minimum_gb` 除以單張 GPU 記憶體,再進位到合法的 TP 度數。

```latex
N_{\mathrm{GPU}} \ge \frac{1.2 \times S_{\mathrm{checkpoint}}}{M_{\mathrm{GPU}}}
```

- 例:Kimi K3 的 1,680 GB ÷ 268–288 GB ≈ 6–7,取 8 張 B300 / GB300 / MI355X;÷ 180–192 GB ≈ 9,取 16 張 B200 / GB200。Qwen3.8-2.4T 的 NVFP4 為 1,737 GB,取 8 張 B300;FP8 為 2,996 GB,取 16 張。
- Hopper 的可行選項(C,recipe):GLM-5.2 / 5.3 的 FP8 或 W4A8 在 8× H200 / H20;DeepSeek-V4-Pro 在 8× H200(context 上限 800K);DeepSeek-V4.1-Flash、V4-Flash、GLM-5.3-Flash、Qwen3.8-Flash-Next 在 4–8 張 H100 / H200。Kimi K3 與 Qwen3.8-2.4T 在 Hopper 需要 16–64 張,且 context 或吞吐量受限。
- Moonshot 自己的建議是把 Kimi K3 部署在 64 個以上加速器的 supernode(C,[Kimi K3 tech blog](https://www.kimi.ai/blog/kimi-k3));8 張 GPU 的下限來自引擎 recipe。

### Google TPU

TPU 上有公布結果的最新機型是 Qwen3.5-397B-A17B 與 DeepSeek-V3 / R1;Kimi K3、GLM-5.1 / 5.2 / 5.3、DeepSeek V4 Pro 與 Qwen3.8-2.4T 的 TPU serving 結果查無公開資料。

**表 4-19 四個家族在 TPU 上的支援狀態**(vLLM TPU release support matrix;README dashboard 標示更新於 2026-08-27,本次以 2026-10-04 的 matrix CSV 逐列核對;等級 C)

| 家族 | 模型 | v7x(Ironwood) | v6e(Trillium) | 來源 |
|---|---|---|---|---|
| Qwen | Qwen3-4B、Qwen3-32B、Qwen3-30B-A3B | unit、correctness、performance 全部 Passing | 全部 Passing | [support matrices](https://github.com/vllm-project/tpu-inference/tree/main/support_matrices) |
| Qwen | Qwen3-Coder-480B-A35B-Instruct、Qwen3.5-397B-A17B | 全部 Passing | 「not enough HBM」 | [support matrices](https://github.com/vllm-project/tpu-inference/tree/main/support_matrices) |
| Qwen | Qwen3.8-2.4T-A95B-FP8 | 只有每日 CI benchmark case(tpu7x-32,TP=32,`max-model-len` 40,960,8,192 in / 1,024 out,並行 368);未公布結果 | 無 | [CI case](https://github.com/vllm-project/tpu-inference/blob/main/.buildkite/benchmark/cases/daily/daily_qwen3_8_2p4t_fp8_tpu7x_32.json) |
| Qwen | Qwen3.8-27B | 無 | SGL-JAX 有驗證過的 recipe(BF16,v6e-4) | [SGL-JAX](https://github.com/sgl-project/sglang-jax/tree/main/docs/cookbook/autoregressive) |
| DeepSeek | DeepSeek-R1 | unit、correctness Passing;performance Untested | 「not enough HBM」（unit、correctness;performance 為 Untested） | [support matrices](https://github.com/vllm-project/tpu-inference/tree/main/support_matrices) |
| DeepSeek | DeepSeek-V3.1、V3.2、V3.2-Speciale | Untested | Untested | [support matrices](https://github.com/vllm-project/tpu-inference/tree/main/support_matrices) |
| DeepSeek | DeepSeek-V4-Flash | 實驗性 kernel 與 nightly MMLU accuracy job;沒有 V4 Pro | 無 | [CI pipeline](https://github.com/vllm-project/tpu-inference/blob/main/.buildkite/pipeline_jax_kube.yml) |
| Kimi | Kimi-K2.6 | unit、correctness Passing;performance Untested | 「not enough HBM」（unit、correctness;performance 為 Untested） | [support matrices](https://github.com/vllm-project/tpu-inference/tree/main/support_matrices) |
| Kimi | Kimi K3 | Google 表示待 TorchTPU 基礎就緒後擴充支援(2026-09-07) | 無 | [InferenceX 2026-09-07](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam) |
| GLM | zai-org/GLM-5 | Untested | Untested | [support matrices](https://github.com/vllm-project/tpu-inference/tree/main/support_matrices) |
| GLM | GLM 5.3 | 同 Kimi K3,僅為 roadmap 說法 | 無 | [InferenceX 2026-09-07](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam) |

**表 4-20 TPU 上已公布的量測**(等級 B:Google tpu-recipes 與 SGL-JAX cookbook;random dataset、`--request-rate=inf`。來源:[tpu-recipes](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/ironwood/vLLM)、[SGL-JAX](https://github.com/sgl-project/sglang-jax/tree/main/docs/cookbook/autoregressive)。)

| 模型;精度 | 硬體;引擎 build | workload(in / out);並行 | 系統 output tok/s(每晶片) | mean TTFT | mean TPOT(每使用者) | context 上限 |
|---|---|---|---|---|---|---|
| DeepSeek-V3 671B;FP8 KV、FP4 MoE 權重重量化 | Ironwood 4 晶片,TP=8;vllm-tpu nightly-20260626 | 1K / 1K;128 | 1,999.78(499.95) | 4.94 s(P99 7.82 s) | 55.07 ms(約 18 tok/s) | `max-model-len` 9,216 |
| DeepSeek-R1 671B;同上 | 同上 | 1K / 1K;128(512 個請求中 8 個失敗) | 1,188.39(297.10) | 14.34 s(P99 93.1 s) | 80.50 ms(約 12 tok/s) | 9,216 |
| Qwen3.5-397B-A17B-FP8;FP8 KV | Ironwood 4 晶片,TP=8;nightly-20260626 | 1K / 8K;128 | 5,171.98(1,293.00) | 未公布 | 未公布 | 9,216 |
| Qwen3.5-397B-A17B-FP8 | 同上 | 8K / 1K;128 | 2,280.85(570.21) | 未公布 | 未公布 | 9,216 |
| Qwen3-Coder-480B-A35B-Instruct-FP8 | Ironwood 4 晶片,TP=8;nightly-20260624 | 1K / 1K;64 | 1,996.00(499) | 未公布 | 未公布 | 10,240 |
| Qwen3-Coder-480B-A35B-Instruct-FP8 | 同上 | 8K / 1K;64 | 1,053.10(263.27) | 未公布 | 未公布 | 10,240 |
| Qwen3-32B;FP8 | Ironwood 1 晶片,TP=2;nightly-20260914 | 1K / 1K;320 | 7,709.61(7,709.61) | 未公布 | 未公布 | 未載明 |
| Qwen3-32B;FP8 | 同上 | 8K / 1K;320 | 1,509.15(1,509.15) | 未公布 | 未公布 | 未載明 |
| GLM-4.5-Air(106B / 12B 啟用);BF16 | v7x-4,TP=8、EP=8;SGL-JAX | 1,024 / 1,024;128 | 4,013.55(約 1,003) | 3,126 ms | 28.84 ms | 32,768 |
| Kimi-Linear-48B-A3B;BF16 | v6e-16;SGL-JAX | 1,024 / 1,024;16 | 690.57 | 607.66 ms | 20.77 ms | 未載明 |
| Qwen3.8-27B;BF16 | v6e-4;SGL-JAX | 512 / 128,固定 shape | 391.77 | 169.93 ms | 未擷取 | 未載明 |

**表 4-21 TPU 唯一的獨立量測:InferenceX Official Preview**(等級 A,成本列套用 SemiAnalysis 的 TCO 模型;Qwen3.5 397B、FP8、8K in / 1K out、aggregated、無 MTP;pre-release 的 TorchTPU vLLM stack;2026-09-07。來源:[InferenceX 2026-09-07](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam)。)

| 操作點 | 指標 | Ironwood | B200 | B300 |
|---|---|---|---|---|
| 20 tok/s/user | 每晶片 total tok/s(input + output) | 9,364 | 8,903 | 8,925 |
| 並行 256 | mean TTFT | 5.41 s | 3.75 s | 2.40 s |
| 100 tok/s/user | 每百萬 total tokens 成本(external TCO 模型) | $0.181 | $0.222 | $0.276 |

- 表 4-21 的 9,364 是 8K / 1K 的 total tokens,不能和表 4-20 的 output tok/s 或 agentic 的數字相比。SemiAnalysis 的說法是「在大部分原始效能曲線上 TPU 沒有勝過 NVIDIA GPU」,優勢來自較低的模型化每小時成本;每個 replica 的晶片數未在公開版揭露。
- TTFT 是 TPU 已公布結果中最弱的指標:大型 MoE 在並行 128 的 mean TTFT 為 3–5 s。LLM recipe 的 context 多為 9,216–10,240 tokens(另有 Gemma 4 的 1,524 與 Qwen3-Embedding-8B 的 16,384),8K 以上輸入、agentic 或多輪 workload 的 TPU 結果查無公開資料。
- Vertex AI 的代管開源模型端點沒有揭露加速器,不能算作 TPU serving 的證據。

### AWS Trainium / Inferentia

AWS 沒有公布 Kimi、GLM、DeepSeek 文字模型在 Trainium 上的任何效能數字或第一方 recipe,只有 Qwen 有 AWS 與 Hugging Face 的數字;任何一代 Trainium 都沒有等級 A 的獨立量測。

**表 4-22 四個家族在 Trainium / Inferentia 上的公開結果**

| 家族;模型 | 來源類型(日期) | 硬體與設定 | workload | 結果(output tok/s;TTFT) | context 上限 | 等級 | 來源 |
|---|---|---|---|---|---|---|---|
| Qwen;Qwen3-32B | AWS NxDI tutorial(SDK 2.26.1,2025 年底) | Trn2,TP=64,單一序列 | 128 in / 512 out,並行 1,p99 值 | 102.3;加 Qwen3-0.6B draft 後 137.8。TTFT 48.3 → 47.4 ms | max length 6,400 | B | [NxDI tutorial](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/tutorials/sd-inference-tutorial.html) |
| Qwen;Qwen3-235B-A22B-Instruct-2507 | Hugging Face Optimum Neuron(2025-10-08 至 2025-10-17) | Trainium2,TP=64,batch 4 | 1,500 ± 150 in / 250 ± 20 out | 單使用者 18.7;TTFT 4,587 ms。最大吞吐 27.9;TTFT 5,824 ms | sequence length 4,096 | B | [Optimum Neuron](https://github.com/huggingface/optimum-neuron/tree/main/benchmark/vllm/single-instance) |
| Qwen;Qwen3-30B-A3B-Instruct-2507 | 同上 | Trainium2,TP=4,batch 16 | 同上 | 單使用者 15.9;TTFT 1,547 ms。最大吞吐 89.2;TTFT 7,107 ms | 4,096 | B | [Optimum Neuron](https://github.com/huggingface/optimum-neuron/tree/main/benchmark/vllm/single-instance) |
| Qwen;Qwen3.5-35B-A3B | 社群 contrib(2026-07-28 合併) | trn2.48xlarge,TP=8,BF16,無 expert parallel | 未載明 | 136(TPOT 7.4 ms);TTFT 561 ms | sequence 512 | B(社群) | [contrib](https://github.com/aws-neuron/neuronx-distributed-inference/blob/main/contrib/models/Qwen3.5-35B-A3B/README.md) |
| DeepSeek;DeepSeek-V3-0324(671B / 37B) | 社群 contrib(2026-04-07 合併;SDK 2.28) | trn2.48xlarge,TP=64(唯一可行設定);FP8 解量化為 BF16 | batch 1,256 in / 256 out | 48.7(TPOT 20.5 ms);TTFT 1,667 ms。經 vLLM 為 batch 1 的 33.3、batch 8 的 66.7 | 512 通過;1,024 載入失敗 | B(社群) | [contrib](https://github.com/aws-neuron/neuronx-distributed-inference/blob/main/contrib/models/DeepSeek-V3/README.md) |
| GLM;GLM-5.2(FP8 checkpoint) | 社群 contrib(2026-06-17 驗證) | trn2.48xlarge,TP=64,batch 1 | 2,048-token prefill | 2.96(每 token 241.5 ms);TTFT 6,377 ms | 2,048(sparse indexer 停用、MTP 移除) | B(社群) | [contrib](https://github.com/aws-neuron/neuronx-distributed-inference/blob/main/contrib/models/GLM-5.2/README.md) |
| DeepSeek;DeepSeek-R1-Distill-Qwen-7B(Inferentia2) | AWS China blog(2025-02-12) | inf2.8xlarge,TP=2 | 單一請求 | 「25–30」 | `max-model-len` 4,096 | C | [AWS China blog](https://aws.amazon.com/cn/blogs/china/deploying-the-deepseek-r1-distillation-model-using-amazon-inferentia2/) |

- 查無公開資料:Kimi 任何版本(68 個 contrib 模型中沒有 Kimi,[contrib models](https://github.com/aws-neuron/neuronx-distributed-inference/tree/main/contrib/models));DeepSeek V3.1 / V3.2 / V4 / V4.1 的模型程式碼(只有實驗性 NKI kernel);GLM-5.3;Qwen3.6 / 3.8;四個家族的任何 Trainium3 結果。
- 第一方的 vLLM Neuron(0.24.0.1.1.0,Beta,Trn2 / Trn3)只驗證 Llama 3、gpt-oss、Qwen3-VL 與 Qwen3-Embedding-8B([README](https://github.com/vllm-project/vllm-neuron/blob/release-0.24.0.1.1.0/README.md));Qwen3-235B-A22B 在已進入維護模式的 NxDI 上為 beta。社群移植也都在 NxDI 上,要用 paged KV、prefix caching 或 disaggregation 需重新移植。
- context 受限的原因(D,筆記推論):這些 MoE 要用滿 trn2.48xlarge 的 64 個 logical core 才放得下權重(DeepSeek-V3 的 BF16、GLM-5.2 只能用 FP8),HBM 幾乎沒有餘裕給 KV。同類的 MiniMax-M3 移植在 8K / 16K 失敗,訊息是「per-rank 24 GB HBM insufficient — needs KV-cache DP/CP」([contrib](https://github.com/aws-neuron/neuronx-distributed-inference/blob/main/contrib/models/MiniMax-M3/README.md))。
- Inferentia2 每個 core 16 GB,實測可用的 context 上限約 16K–32K;Qwen3 或任何 MoE 在 Inf2 上的 tokens/s 查無公開資料。
- Bedrock 的 serverless 開源模型跑在什麼加速器上,AWS 沒有說明,只點名推論引擎 Project Mantle([AWS What's New 2026-02-10](https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-bedrock-adds-support-six-open-weights-models/))。「Bedrock 大部分推論跑在 Trainium」(原文 "runs most of its inference on Trainium")是服務層級的說法(C,[Jassy shareholder letter](https://www.aboutamazon.com/news/company-news/amazon-ceo-andy-jassy-2025-letter-to-shareholders));SemiAnalysis 在 2025-12-04 報導內部 Bedrock 的 DeepSeek / Qwen 工作負載以私有 vLLM fork 跑在 Trainium([SemiAnalysis](https://newsletter.semianalysis.com/p/aws-trainium3-deep-dive-a-potential)),Kimi 與 GLM 沒有任何來源指向 Trainium。

### Cerebras

Cerebras 的公開目錄在 2026-10-04 只剩 `gpt-oss-120b` 與 `qwen-3.8-27b` 兩個模型;四個家族的其他模型只在企業專屬通路,旗艦(Kimi K3、DeepSeek V4、Qwen3.8-2.4T)不在任何清單上。

**表 4-23 Cerebras 上四個家族的供應與量測**

| 模型 | 供應層級與狀態 | context;max output | 速度與延遲(等級;日期) | 價格 | 來源 |
|---|---|---|---|---|---|
| `qwen-3.8-27b` | Shared Inference 公開 API;GA,2026-09-03 上線 | Free Trial 65,536;32,768。付費層 131,072;40,960 | 廠商約 1,850 t/s(C)。OpenRouter p50 1,025、p90 1,359 t/s,latency p50 0.17 s(A,2026-10-04)。AA 未測 | $0.99 / $1.49 每 1M tokens;快取輸入不打折 | [Cerebras docs](https://inference-docs.cerebras.ai/models/qwen-3.8-27b)、[OR](https://openrouter.ai/qwen/qwen3.8-27b) |
| Kimi K2.6 | 私有企業端點;2026-05-19 宣布 enterprise trial,從未上公開 gateway | 未公布 | AA 於 2026-05-06 量到 981 output t/s;10,000 input / 500 output 的 E2E 為 5.6 s,Moonshot 自家端點為 163.7 s(A,但端點不公開) | 未公布 | [Cerebras blog](https://www.cerebras.ai/blog/cerebras-kimi-k2-Enterprise)、[VentureBeat](https://venturebeat.com/technology/cerebras-says-its-chips-run-a-trillion-parameter-ai-model-nearly-7-times-faster-than-gpu-clouds) |
| GLM-4.7(355B) | Cerebras Code 訂閱;`zai-glm-4.7` 於 2026-08-17 宣布 deprecation | 查無公開資料 | 「1,000 tokens+ per second」(C) | Pro $50 / 月、Max $200 / 月,兩者都顯示售完 | [Cerebras Code](https://www.cerebras.ai/code)、[deprecation](https://inference-docs.cerebras.ai/support/deprecation) |

- `kimi-k2.7-code` 只開放客戶試用;Dedicated Inference 清單列有 Z.AI GLM 4.X / 5.X、Moonshot Kimi K2.X、DeepSeek V3.X 與 Qwen 3.8 / Qwen3 / Qwen3-Coder(0.6B 至 480B),各模型的 context、速度與價格都未公布([Dedicated](https://inference-docs.cerebras.ai/dedicated/overview))。
- Kimi K2.6 私有端點對目前最快公開 GPU 端點的倍數有兩個算法,且量測日不同:981 ÷ 264(AA 圖表值,Nebius)= 3.7×,或 981 ÷ 250(AA 比較表值)= 3.9×(D)。Cerebras 在 2026-05 公布時的說法是次快 GPU 雲的 6.7×。
- Cerebras 對 Kimi 不上公開 gateway 的說法是容量:「We prioritize our enterprise customers」([VentureBeat](https://venturebeat.com/technology/cerebras-says-its-chips-run-a-trillion-parameter-ai-model-nearly-7-times-faster-than-gpu-clouds))。DeepSeek V4 未列入的原因只有分析師估計(非量測):1.6T 參數在 1M context、256 個同時請求下約需 40 套系統,而公開端點的 context 上限是 128K([SemiAnalysis](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please)、[SemiAnalysis, 19 Aug 2026](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast))。
- `qwen-3.8-27b` 的 Developer 層限流為 300 RPM、未快取 150K TPM、總量 750K TPM(2026-09-22 由 450K 暫時調高,[rate limits](https://inference-docs.cerebras.ai/support/rate-limits))。

## 供應矩陣

2026-10-04 的供應狀態:Amazon Bedrock 在這四個家族只有 Kimi K3 一個現役世代模型(GA 2026-09-18,1M context),Google Vertex AI 在 2026-10-21 之後只剩 GLM 5.2(Preview),Azure AI Foundry 有 DeepSeek V4 Pro / Flash(2026-04-23 版)與 Kimi K2.5 至 K2.7 Code,但沒有 GLM 與 Qwen。GLM-5.3、DeepSeek V4 Pro 0813、DeepSeek V4.1 Flash 與 Qwen3.8 只能走第三方 GPU 雲(OpenRouter 上各有 7–40 個端點)或自架。

**表 4-24 模型 × 硬體類別 × 代管服務**(2026-10-04。「GPU 雲」欄為第三方端點數「AA 有速度資料 / OpenRouter」,不含 ASIC 雲、三家超大規模雲與原廠,為 D;其後為 OpenRouter 全部端點的 context 分布。來源:[AA leaderboard](https://artificialanalysis.ai/leaderboards/providers)、[Bedrock model cards](https://docs.aws.amazon.com/bedrock/latest/userguide/model-cards.html)、[Vertex open models](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/use-open-models)、[Vertex deprecations](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/deprecations/open-models)、[Azure models](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure)、[Groq docs](https://console.groq.com/docs/models)、[SambaNova docs](https://docs.sambanova.ai/docs/en/models/sambacloud-models)。)

| 模型 | Cerebras | Groq | SambaNova | GPU 雲 | Amazon Bedrock | Google Vertex AI | Azure AI Foundry |
|---|---|---|---|---|---|---|---|
| Kimi K3 | 無 | 無 | 無 | 15 / 22;24 個端點中 23 個 ≥ 1M | GA 2026-09-18;1M;只能 cross-Region | 無 | 無 |
| Kimi K2.7 Code | 僅企業試用 | 無 | 無 | 5 / 10;256K–262K | 無 | 無 | Preview;262,144 |
| Kimi K2.6 | 僅私有企業端點 | 無 | 無 | 6 / 17;256K–262K | 無 | 無 | Preview;262,144 |
| Kimi K2.5 | 無 | 無 | 無 | 3 / 4 | 有;256K;In-Region | 無 | Preview;262,144 |
| GLM-5.3 | 無 | 無 | 無 | 24 / 39;40 個端點中 38 個 ≥ 1M | 無 | 無 | 無 |
| GLM-5.3-Flash | 無 | 無 | 無 | 20 / 34;35 個端點中 33 個 ≥ 1M | 無 | 無 | 無 |
| GLM-5.2 | 無 | 無 | 無 | 15 / 33;34 個端點中 31 個 ≥ 1M | 無 | Preview(2026-08-24);1,000,000 context、64,000 輸出;`global` | 無 |
| GLM-5 | 無 | 無 | 無 | 2 / 6;約 200K | 有;200K;In-Region | 200,000;已 deprecated,2026-10-21 停用 | 無 |
| DeepSeek V4 Pro 0813 | 無 | 無 | 無 | 8 / 19;20 個端點全部 ≥ 1M | 無 | 無 | 無(Azure 的 `DeepSeek-V4-Pro` 是 2026-04-23 版) |
| DeepSeek V4 Pro(4 月版) | 無 | 無 | 無 | 5 / 14 | 無 | 無 | 有;1,000,000 輸入、384,000 輸出 |
| DeepSeek V4.1 Flash | 無 | 無 | 無 | 21 / 29;30 個端點全部 ≥ 1M | 無 | 無 | 無 |
| DeepSeek V4 Flash 0731 | 無 | 無 | 無 | 15 / 28 | 無 | 無 | Preview;1,000,000 輸入、384,000 輸出 |
| DeepSeek V3.2 | 無 | 無 | Preview;32K | 5 / 11;131K–164K | 有;164K;In-Region | 已 deprecated,2026-10-21 停用 | 有;128,000 |
| Qwen3.8 2.4T A95B | 無 | 無 | 無 | 5 / 6;7 個端點中 5 個 ≥ 1M、2 個為 262K | 無 | 無 | 無 |
| Qwen3.8 27B | 有;65,536(OpenRouter)或 131,072(Cerebras 文件,付費層) | Preview;131,072 | 無 | 7 / 15;17 個端點中 14 個 ≤ 262K、3 個 ≥ 1M | 無 | 無 | 無 |
| Qwen3.5 397B A17B | 無 | 無 | 無 | 5 / 9;128K–262K | 無 | 無 | 無 |
| Qwen3 235B / Coder 480B / Next 80B(2025 年機型) | 無 | 無 | 無 | 數個 | 有;128K–256K;In-Region | 已 deprecated,2026-10-21 停用 | 無 |
| gpt-oss-120b(對照) | 有;131K | 有;131K | 有;131K | 10 / 17 | 有;131K | 有;131K(不在 deprecation 表) | Preview;131,072 |

- 其他硬體:Tenstorrent 自 2026-10-03 起在 OpenRouter 提供 Kimi K2.7 Code(256,000 context);唯一揭露使用 AMD GPU 的主機是 Zyphra(MI355X,2026-05 宣布提供 DeepSeek V3.2、Kimi K2.6、GLM 5.1,查無速度數字,[Zyphra](https://www.zyphra.com/our-work/zyphra-and-amd-partner-to-power-zyphra-cloud-on-amd-instinct-mi355x-gpus))。
- 亞太可用性:Bedrock 的 Kimi K3 沒有 In-Region 選項,global profile 可從 32 個 Region 呼叫(含 ap-east-2 台北、ap-northeast-1 / 2 / 3、ap-south-1 / 2、ap-southeast-1 至 7),但請求會路由到全球任一支援的商用 Region,沒有 In-Region 或亞太地理範圍的處理保證。舊機型的 In-Region 在 Tokyo、Mumbai、Sydney、Jakarta、Melbourne,不含 Taipei、Singapore、Seoul、Hong Kong。
- Azure 的 Global Standard 可從 5 個亞太 region 部署(australiaeast、japaneast、japanwest、koreacentral、southindia,[Azure regions](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure-region-availability));Vertex 的 GLM 5.2 只有 `global`,且只承諾「至少提供到 2026-10-31」([Vertex GLM 5.2](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/maas/zaiorg/glm-52))。
- 三家超大規模雲與四家原廠 API 都沒有揭露加速器,矩陣中的這些欄位應標為「硬體未揭露」。

**表 4-25 Amazon Bedrock:四個家族模型的 context、價格、service tier 與 quota**(等級 C;價格依 [Bedrock pricing](https://aws.amazon.com/bedrock/pricing/),quota 依 [Bedrock quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html);2026-10-04。)

| 模型 | context;max output | 價格 $/1M in / out(US;Tokyo) | Standard / Priority / Flex / Reserved | Region 與推論型態 | 預設 on-demand quota | 來源 |
|---|---|---|---|---|---|---|
| Kimi K3 | 1M;card 未載明(OpenRouter 對其 Bedrock 端點列 128,000) | global profile 3.00 / 15.00,cache read 0.30,cache write(30 分鐘)3.75;US profile 3.30 / 16.50 | 有 / 有 / 有 / 無 | 無 In-Region;US geo profile(5 個 Region)與 global profile(32 個 Region) | cross-Region 與 global cross-Region 各 10,000,000 TPM(可調);14,400,000,000 tokens / 日(不可調);未見 RPM 列 | [card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-moonshot-ai-kimi-k3.html) |
| Kimi K2.5 | 256K;16K | 0.60 / 3.00;0.72 / 3.60 | 有 / 有 / 有 / 無 | In-Region,11 個 Region(含 Tokyo、Mumbai、Sydney、Jakarta、Melbourne) | 10,000 RPM;100,000,000 TPM(不可調) | [card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-moonshot-ai-kimi-k2-5.html) |
| GLM 5 | 200K;128K | 1.00 / 3.20;1.20 / 3.84 | 有 / 有 / 有 / 無 | In-Region,同上 11 個 Region | 10,000 RPM;100,000,000 TPM | [card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-zai-glm-5.html) |
| DeepSeek V3.2 | 164K;8K | 0.62 / 1.85;0.74 / 2.22 | 有 / 有 / 有 / 無 | In-Region,10 個 Region(含 Tokyo、Mumbai、Sydney、Jakarta) | 10,000 RPM;100,000,000 TPM | [card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-deepseek-deepseek-v3-2.html) |

- service tier:Priority 以 Standard 的 1.75× 計費,Flex 為 0.5×;Converse 與 Invoke API 只支援 Standard on-demand,要用 tier 需走 Responses 或 Chat Completions API。Priority 與 Flex 的延遲查無量測,AA 與 OpenRouter 測的都是 Standard。
- Kimi K3 是 Bedrock 上第一個支援 explicit prompt caching 的開源模型(每個 cache checkpoint 至少 1,024 tokens,保留至少 30 分鐘),cache 命中不計入每分鐘輸入 token 的 quota;global profile 比地理 profile 便宜約 10%([AWS What's New](https://aws.amazon.com/about-aws/whats-new/2026/09/moonshot-ai-kimi-k3-on-amazon-bedrock/))。
- Kimi K3 的 10,000,000 TPM 是舊開源機型 100,000,000 TPM 的十分之一;以 100K-token 的 agentic prompt 計,約等於每分鐘 100 個未快取請求(D:10,000,000 ÷ 100,000)。
- Bedrock 的 DeepSeek、GLM、Qwen 產品線停在 DeepSeek V3.2、GLM 5 與 Qwen3;舊 card 上的「Model launch date」看來是模型原始發布日而不是 Bedrock 上架日,不應當作上架日期引用。

## 網站呈現建議

- 表 4-24 做成可排序、可篩選的供應矩陣(列為模型,欄為硬體類別與代管服務),儲存格顯示狀態與 context;提供「只看有 ASIC 端點」「只看亞太可部署」「只看 1M context」三個篩選,並把「硬體未揭露」「查無公開資料」畫成不同的灰階而不是留白。
- 表 4-6 與表 4-7 做成每個模型一列的區間圖(最快、中位、原廠三個點,對數座標,點的顏色代表硬體類別),AA 與 OpenRouter 用切換鈕分開,不放在同一個座標軸;hover 顯示 TTFT、端點名稱與量測時間。
- 表 4-10 與表 4-11 做成 small multiples 折線圖:x 軸為 prompt 長度(1K、10K、100K),上圖 TTFT、下圖 t/s,ASIC、GPU、未揭露三類分色;加速層的 TTFT 離群值要保留並標註。
- 表 4-13 至表 4-16 做成互動散點圖(x 軸為 tok/s/user,y 軸為 output tok/s/GPU),可選模型、硬體、引擎與 spec decode;預設顯示 output 而不是 total,每個點標明並行數、佈局、TTFT、執行日,並固定顯示「spec decode 採固定 acceptance」的註記。
- 表 4-2 做成 KV sizing 計算器:輸入模型、context 長度、並行 session 數與 KV 精度,輸出 KV 與 state 的 GiB,並顯示所用算式與等級 D 標記。
- 可刪減:各供應商的逐列長表與 2025 年機型只提供下載或外連;表 4-17、4-18 與 TPU、Trainium、Cerebras 三個小節收進可展開的區塊,預設只顯示「有無公開結果」的一行結論。
