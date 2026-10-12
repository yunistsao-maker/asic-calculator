# 總覽

資料基準日：2026-10-04；逐項事實查核於 2026-10-05 完成。等級：**A** = 獨立第三方量測；**B** = 廠商 / 夥伴公布且揭露方法；**C** = 廠商宣稱或規格、未揭露方法；**D** = 本文推算（附算式）。

## 關鍵發現

14 項發現各自連到佐證所在的章節；每一項的數字都在 2026-10-05 的查核中對回章節內文與來源。

### 模型與端點

1. **模型世代已換，開源旗艦都以 1M context 提供。** Kimi K3（2.78T 參數 / 104B 啟用，權重 2026-07-27 公開）、GLM-5.3（744B / 40B）、DeepSeek-V4-Pro（1.6T / 49B）與 V4.1-Flash、Qwen3.8（2.4T / 95B 與 27B）。Kimi、GLM 與 DeepSeek 的 config 為 1,048,576；Qwen3.8 原生 262,144，model card 稱可擴至約 1M，代管版預設 1M [C]。見第 4 章。
2. **旗艦開源模型沒有公開的 ASIC 端點。** Cerebras（公開）與 Groq（Preview）在四個家族中只供應 Qwen3.8 27B，SambaNova 停在 DeepSeek V3.1 / V3.2，Tenstorrent 自 2026-10-03 起在 OpenRouter 列出 Kimi K2.7 Code；沒有任何公開端點標明由 Trainium 或 TPU 支撐。公開端點上量得到的硬體效應只有 Cerebras 在 gpt-oss-120b 的 5.5×（Artificial Analysis）與 Qwen3.8 27B 的約 9×（OpenRouter）[A]；另有一筆 Kimi K2.6 私有端點的非同時量測（3.7–3.9×）。見第 4 章。
3. **同條件下 Cerebras 的輸出速度是最快的非 ASIC 端點的 5.5 倍，長 prompt 會縮小差距。** gpt-oss-120b、10K 輸入：1,764 對 320 tokens/s（Azure，硬體未揭露）[A]。100K 輸入降到 3.7 倍（1,225 對 Baseten 332），TTFT 也不領先：三個 ASIC 端點為 3.44–6.78 s，四個 GPU 雲端點為 1.25–3.48 s。見第 8 章。
4. **旗艦模型最快的端點是 GPU 上的軟體堆疊。** Kimi K3 最快 320 tokens/s（廠商自述為 GPU）、17 個端點的中位數 138、原廠 API 40；Bedrock 的 Kimi K3 是 182 tokens/s、TTFT 1.30 s [A]。見第 4 章。

### 技術與長上下文

5. **技術支援差距很大。** 34 項技術中文件列為「支援」的：NVIDIA GPU 33、AMD GPU 24、Trainium 12、TPU 11、Inferentia2 8、Cerebras 公開 API 6 [D]。最要緊的缺口是 MLA 與 sparse attention kernel、1M context、KV offload。見第 6 章。
6. **1M context 目前只在 GPU 上可重現。** GPU 以外文件記載或實測的最大值：Trainium 文件測試到 128K（131,072）、Cerebras 公開 API 131K、TPU repository 內最大 98,304（Ironwood 的 LLM recipe 多為 9,216–10,240）、Inferentia2 實測 32,768。Gemini 與 Claude 以 1M 視窗販售，但服務這些請求的硬體與技術未揭露。見第 7 章。
7. **長上下文的瓶頸是 KV 容量與 cache 命中，不是算力。** 1M tokens 一條序列的 KV：V4.1-Flash 0.87 GiB、V4-Pro 約 4.8 GiB、Kimi K3 13.5 GiB、GLM-5.x 43.9 GiB、Qwen3.8-2.4T 46 GiB [D]。併發 1、命中率 0.964–0.984 的 9 筆量測，TTFT p50 為 0.18–1.03 s；Kimi K3 在 8× B300、併發 16 且沒有 DRAM offload 時 KV 用盡，命中率掉到 2.7%、TTFT p50 86 s，開啟 DRAM offload 後為 0.85 s [A]。見第 7 章。

### 硬體與引擎

8. **Trainium 與 TPU 的硬體到位，限制在軟體與取得管道。** Trainium2 只能用 Capacity Blocks 買，每 chip-hour $2.235，是 B200 Capacity Blocks $12.355 的 18%（2026-10-07 GPU 調漲到 $14.208 後為 16%）[D]；Trainium3 沒有公開價格，Tokyo、Singapore、Taipei 都沒有 Trainium。InferenceX 預覽中 Ironwood 每顆晶片在 20 tok/s/user 的高併發點與 B200 / B300 相當（1.05 倍）[A]，在每使用者 100 tokens/s 時落後（0.86 與 0.82 倍）[D]。見第 1 章與第 8 章。
9. **Cerebras 的代價是記憶體。** 每片晶圓 44 GB SRAM，公開 context 停在 131K，公開目錄只有 2 個模型；AWS Bedrock 整合延到 2027 Q1 [C]。見第 1 章與第 9 章。
10. **引擎沒有單一贏家。** InferenceX 的 AgentX 快照（2026-10-04）中，NVIDIA 硬體上 Kimi K3 與 DeepSeek-V4.1-Flash 由 vLLM 領先，GLM 與 Qwen3.5 由 SGLang 領先；DeepSeek-V4-Pro 每使用者最快的是 Dynamo-SGLang（312 tok/s），每 GPU 吞吐量最高的是 Vera Rubin 上的 TensorRT-LLM（148,886 total tok/s）[A]。AMD MI355X 上 GLM 的最高數字來自 TileRT（485 tok/s per user，僅 concurrency 1）與 ATOM（每 GPU 34,195）。同時涵蓋 GPU 與非 GPU 加速器的引擎只有 vLLM 與 SGLang。見第 2 章。

### 容量與成本

11. **容量由 coding 決定。** 100,000 人（OA 70% / coding 12% / R&D 18%，base 用量，單一時區）的尖峰約 4,764 RPM、24.5M 未快取輸入 TPM、3.13M 輸出 TPM、212M cache read TPM；coding 佔 94% 的 token。10,000 人是 476 RPM、2.45M、313K；員工分散全球時尖峰為 0.59 倍（2,820 RPM）[D]。見第 10 章。
12. **同一流量在各平台要申請的數字差 3.4–9.8 倍。** 上例全部 token 240M TPM，Anthropic 計 24.5M ITPM，Bedrock 對 Opus 5.5（output 10×）計 55.8M TPM，是預設 30M 的 1.86 倍 [D]。見第 10 章。
13. **自建規模。** 同一情境全部走 Kimi K3 的線性需求約 480 顆 Blackwell 級 GPU（decode 受限、使用率 0.8，未加備援）；分層路由的線性需求 134 顆，取整到各模型的部署單位後 172 顆，另加一個 Opus API 池 [D]。見第 10 章。
14. **成本。** InferenceX 的模型化成本（DeepSeek-V4-Pro、agentic、P90 每使用者 100 tokens/s）：Vera Rubin 每百萬 output tokens $0.69、GB300 $1.34、MI355X $2.74。gpt-oss-120b、一次 10K 輸入與 500 輸出的請求：Cerebras 的成本是 Groq、Azure、Nebius 的 2.2 倍，換到 3.7–6.3 倍的每串流速度 [D]。見第 8 章。

## 研究範圍

本調查涵蓋 5 類推論晶片、4 個開源模型家族與主要私有模型，共 11 章、{{N_TABLES}} 張表、{{N_SRC}} 個不重複來源，每個數字都標示來源與證據等級。

| 項目 | 範圍 |
|---|---|
| 晶片 | AWS Trainium（1 / 2 / 3，4 已宣布）、AWS Inferentia（1 / 2）、Google TPU（v5e 到 Ironwood，8t / 8i 已宣布）、GPU（NVIDIA Hopper / Blackwell / Vera Rubin，AMD Instinct 為對照）、Cerebras（WSE-3 / CS-3 / CS-4） |
| 只作對照點 | NVIDIA Groq 3 LPX、Groq LPU、SambaNova。OpenAI Jalapeño 出現在 InferenceX 的硬體登錄檔，但公開 API 沒有它的資料列，本調查沒有它的數字 |
| 開源模型 | Kimi（K3、K2.x）、GLM（5.3、5.2）、DeepSeek（V4-Pro、V4.1-Flash）、Qwen（3.8 系列、3.5-397B） |
| 私有模型 | Claude、GPT、Gemini、Nova、Grok 等，限於有公開統計者 |
| 推論引擎 | vLLM、SGLang、TensorRT-LLM、Dynamo、llama.cpp、TGI、ATOM、TileRT、TokenSpeed、vLLM Neuron plugin、NxD Inference、vLLM TPU plugin、Cerebras 自有堆疊 |
| 容量情境 | 1,000 / 10,000 / 50,000 / 100,000 人；OA、coding、R&D 三種角色；8 種角色組合 × 3 個用量級；4 種模型路由 |

## 方法與限制

- 14 份英文研究筆記（約 21 萬字）由來源頁面整理而成，各章只用筆記內的事實與連結；查不到的寫「查無公開資料」。
- 容量模型以 Python 實作，可重跑；第 10 章的表由程式產生，網站上的計算器以同一組測試向量驗證。
- 逐項事實查核於 2026-10-05 完成：{{N_SRC}} 個來源中 {{N_LOCAL}} 個以本地副本比對、{{N_WEB}} 個線上逐句核對、{{N_UNREAD}} 個無法重讀；共更正 {{N_CORR}} 處，紀錄在「查核紀錄」頁。
- 模型與價格每週在變。OpenRouter 同一批端點在 2026-10-04 兩次快照（00:52 與 05:37 UTC）之間，p50 throughput 的變動中位數依模型為 7–30% [D]，排名差距小於約 25% 應視為雜訊；引用前請對照來源。
- 尚未做的事：成本與能效的專題研究（第 8 章以既有筆記與 InferenceX 的公開資料寫成）；私有模型晶片對應的專題查證（第 5 章的 23 筆對應全部是等級 C）。
- 容量模型的角色用量有 28 列參數是判斷值，其中 R&D 最弱；套用到實際客戶前應換成該客戶的遙測。
