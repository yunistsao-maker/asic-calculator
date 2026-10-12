# 第 5 章 私有模型效能：Claude / GPT / Gemini / Nova / Grok / Muse Spark

資料基準日：2026-10-04。等級：**A** = 獨立第三方量測；**B** = 廠商／夥伴公布且揭露方法；**C** = 廠商宣稱或規格、未揭露方法；**D** = 本文推算（附算式）。除另行標明者（表 5-9 的每晶片 total tokens/s、表 5-1 與表 5-10 的 Google 全產品 token 流量）外，本章的 tokens/s 皆指單一請求串流的輸出速度（每使用者速度），不是系統吞吐量。

## 私有模型與晶片對應

本節整理 23 筆「私有模型 ↔ 晶片」的公開對應：16 筆依據廠商聲明，7 筆依據媒體或分析師報導，沒有任何一筆來自獨立量測（等級皆為 C）。在本次讀到的來源中，沒有任何廠商公布私有模型的每晶片或每系統吞吐量；公開的只有每使用者的輸出速度（例如 GPT-5.6 Sol Ultrafast 的「最高 750 tokens/s」）與相對倍數，外加 Google 全產品的總流量（未區分晶片），因此無法由這些資料推算每顆晶片的 tokens/s。

**表 5-1 私有模型與晶片的公開對應**（2026-10-04 讀取；GW 與金額是合約或承諾規模，不是已交付容量；「廠商聲明」含合作夥伴的新聞稿與部落格，「媒體報導」含分析師與轉述報導）

| 廠商與模型 | 晶片 | 規模（晶片數、GW、金額，若有） | 日期 | 依據 | 等級 | 來源 |
|---|---|---|---|---|---|---|
| Anthropic Claude（訓練與推論；文件未逐模型說明） | AWS Trainium2（Project Rainier） | Rainier 近 50 萬顆 Trainium2，「超過 Anthropic 先前訓練算力的 5 倍」；預期 2025 年底 Claude 用到 100 萬顆以上；2026-07-31 的說法為「超過 100 萬顆」；Claude 工程主管另稱「近 100 萬顆」（日期未載） | 2025-06-24（2025-10-29 更新）；2026-07-31 | 廠商聲明 | C | [About Amazon Project Rainier](https://www.aboutamazon.com/news/aws/aws-project-rainier-ai-trainium-chips-compute-cluster)、[About Amazon 晶片事業](https://www.aboutamazon.com/news/aws/amazon-ai-chips-business-history)、[AWS Trainium customers](https://aws.amazon.com/ai/machine-learning/trainium/customers/) |
| Anthropic Claude 3.5 Haiku（Bedrock 延遲最佳化版） | AWS Trainium2 | 晶片數未載明；僅此一個「特定 Claude 模型 ↔ 特定晶片世代」的服務端對應 | 2024-12-03 | 廠商聲明 | C | [AWS News Blog](https://aws.amazon.com/blogs/aws/amazon-ec2-trn2-instances-and-trn2-ultraservers-for-aiml-training-and-inference-is-now-available/) |
| Anthropic Claude | AWS Trainium2 / 3 / 4（含未來世代） | 10 年內在 AWS 花費超過 $100B；最高 5 GW；「相當可觀的 Trainium3 容量」預計 2026 年上線；擴大亞洲與歐洲的國際推論；Amazon 另投資 $5B（最多再 $20B） | 2026-04-20 | 廠商聲明 | C | [About Amazon Anthropic 追加投資](https://www.aboutamazon.com/news/company-news/amazon-invests-additional-5-billion-anthropic-ai) |
| Anthropic Claude | Google TPU | 最多 100 萬顆 TPU、「數百億美元」、2026 年「遠超 1 GW」；Google 另稱 Claude 在 TPU 上「訓練並服務」（train and serve） | 2025-10-23（Anthropic）；2025-11-06（Google） | 廠商聲明 | C | [Anthropic 2025-10-23](https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services)、[Google Cloud blog](https://cloud.google.com/blog/products/compute/ironwood-tpus-and-new-axion-based-vms-for-your-ai-workloads) |
| Anthropic Claude | Google TPU（下一代，經 Broadcom） | 「多個 GW」的下一代 TPU 容量，預計 2027 年起上線 | 2026-04-06 | 廠商聲明 | C | [Anthropic 2026-04-06](https://www.anthropic.com/news/google-broadcom-partnership-compute) |
| Anthropic Claude | Google TPU（Ironwood 等） | 約 3.5 GW（2027 起，另有 2026 年已供應的 1 GW）；Broadcom 揭露 $10B（2025-09）與 $11B（2025-12）的 TPU 機櫃訂單；SemiAnalysis：直購約 40 萬顆以上、向 GCP 租用 60 萬顆以上，「主要用於訓練、也用於推論」；前 40 萬顆 Ironwood（約 $10B 成品機櫃）由 Broadcom 直接賣給 Anthropic | 2025-11-28；2026-04-07；2026-09-07 | 媒體報導 | C | [TNW](https://thenextweb.com/news/anthropic-google-broadcom-compute-deal)、[SemiAnalysis InferenceX](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam)、[SemiAnalysis TPUv7](https://newsletter.semianalysis.com/p/tpuv7-google-takes-a-swing-at-the) |
| Anthropic Claude | NVIDIA GPU | 規模未載明；原文："We train and run Claude on a range of AI hardware—AWS Trainium, Google TPUs, and NVIDIA GPUs" | 2026-04-06 | 廠商聲明 | C | [Anthropic 2026-04-06](https://www.anthropic.com/news/google-broadcom-partnership-compute) |
| Anthropic Claude | AMD Instinct MI450 | 最高 2 GW，2027 上半年起；AMD 最多投資 $5B | 2026-07-23 至 2026-07-24（AMD Advancing AI 2026 的報導） | 媒體報導 | C | [Moor Insights 2026-07-24](https://moorinsightsstrategy.com/field-notes/amd-advancing-ai-2026-helios-ships-venice-swings-and-the-software-moat-narrows/)、[Reuters via Yahoo Finance 2026-07-23](https://finance.yahoo.com/technology/ai/articles/amd-expected-launch-next-generation-100622118.html) |
| OpenAI GPT-5.3-Codex-Spark（research preview） | Cerebras WSE-3 | 超過 1,000 tokens/s、128K context、僅文字；Techzine 稱其為「第一個不在 NVIDIA 上服務的 OpenAI GPT 模型」；系統數未載明 | 2026-02-12 | 廠商聲明 | C | [Cerebras blog 2026-02-12](https://www.cerebras.ai/blog/openai-codexspark)、[Techzine 2026-02-13](https://www.techzine.eu/news/analytics/138754/openai-swaps-nvidia-for-cerebras-with-gpt-5-3-codex-spark/) |
| OpenAI GPT-5.6 Sol Ultrafast（limited preview） | Cerebras CS-3（多套系統） | 最高 750 tokens/s、最高為標準的 14×；Cerebras：「相同模型架構、權重、精度、context 設定」；系統數與晶圓數未揭露 | 2026-08-13（Cerebras 技術文 2026-08-27） | 廠商聲明 | C | [OpenAI Ultrafast 預覽](https://openai.com/index/previewing-ultrafast/)、[Cerebras blog 2026-08-27](https://www.cerebras.ai/blog/how-cerebras-serves-gpt-5-6-sol-at-up-to-750-tokens-per-second) |
| OpenAI（容量合約，未指明模型） | Cerebras | 750 MW、超過 $20B、多年期；3 年內部署，另有擴充到合計 2 GW 的選擇權（至 2030；分析師說法） | 2025-12 簽約；2026-01-14 公布 | 廠商聲明 | C | [Cerebras Q1 2026 results](https://investors.cerebras.ai/news-releases/news-release-details/cerebras-systems-announces-strong-first-quarter-2026-results)、[Cerebras S-1](https://www.sec.gov/Archives/edgar/data/2021728/000162828026025762/cerebras-sx1april2026.htm)、[SemiAnalysis](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please)、[Vik's Newsletter](https://www.viksnewsletter.com/p/cerebras-ipo-and-the-scaling-bottlenecks) |
| OpenAI GPT-6 Astra Ultrafast | NVIDIA GPU（型號、精度、batch size 未揭露） | NVIDIA：最高比 Astra Standard 快 8×；媒體：「最高 300 tokens/s」、API 最高 6×、Codex 最高 8× | 2026-09-29（VentureBeat）；2026-10-01（NVIDIA） | 廠商聲明 | C | [NVIDIA blog 2026-10-01](https://blogs.nvidia.com/blog/gpus-openai-gpt-6-astra-ultrafast/)、[VentureBeat 2026-09-29](https://venturebeat.com/technology/openais-gpt-6-1-sol-offers-astra-like-performance-at-1-5th-price-a-new-ultrafast-tier-clocks-at-300-tokens-per-second) |
| OpenAI GPT-6.1 Sol Ultrafast | NVIDIA GPU，低 batch size（SemiAnalysis） | 約 300 tokens/s，對照由 Cerebras 服務的前代約 750 tokens/s；截至報導時 OpenAI 與 Cerebras 均未評論 | 2026-09-30 | 媒體報導 | C | [OfficeChai 2026-09-30](https://officechai.com/ai/openais-gpt-6-1-sol-ultrafast-is-not-running-on-cerebras-but-on-nvidia-gpus-says-semi-analysis/)、[BigGo Finance 2026-09-30](https://finance.biggo.com/news/ff824066-1b87-4f34-97d6-90fde6ef0de8) |
| OpenAI GPT（AWS 上的工作負載） | NVIDIA GB300 | 規模未載明；SemiAnalysis 寫 OpenAI 在 AWS「Uses GB300s」 | 2025-12-04 | 媒體報導 | C | [SemiAnalysis Trainium3 深度分析](https://newsletter.semianalysis.com/p/aws-trainium3-deep-dive-a-potential) |
| OpenAI（未指明模型） | AMD GPU | 6 GW；機型與起始日未載明 | 2026-07-24（AMD Advancing AI 2026 的報導） | 媒體報導 | C | [Moor Insights 2026-07-24](https://moorinsightsstrategy.com/field-notes/amd-advancing-ai-2026-helios-ships-venice-swings-and-the-software-moat-narrows/) |
| OpenAI（Stateful Runtime Environment、Frontier 等進階工作負載） | AWS Trainium3 與 Trainium4 | 約 2 GW，2027 年起；既有 $38B 多年協議再擴大 $100B / 8 年；Amazon 投資 $50B。是否用於 GPT 推論，原文未說明 | 2026-02-27（2026-07-31 重申） | 廠商聲明 | C | [About Amazon OpenAI 合作](https://www.aboutamazon.com/news/aws/amazon-open-ai-strategic-partnership-investment)、[About Amazon 晶片事業](https://www.aboutamazon.com/news/aws/amazon-ai-chips-business-history) |
| Google Gemini | Google TPU | TPU 世代未揭露；Google 全產品每月處理逾 3.2 quadrillion tokens，約 12 億 tokens/s（D：3.2e15 ÷ (30 × 86,400)） | 2025-11-06；2026-05-19 | 廠商聲明 | C | [Google Cloud blog](https://cloud.google.com/blog/products/compute/ironwood-tpus-and-new-axion-based-vms-for-your-ai-workloads)、[Shacknews Pichai I/O](https://www.shacknews.com/article/149205/google-3-2-quadrillion-monthly-ai-tokens) |
| Amazon Nova（含 Bedrock 上的 Nova 2） | Cerebras CS-3（預告） | AWS 預告「年內」在 Bedrock 提供使用 Cerebras 硬體的 Nova；Bedrock 上的 Cerebras 部署依 Cerebras 公告延到 2027 年 Q1，已宣布未出貨 | 2026-03-13；2026-08-12 | 廠商聲明 | C | [About Amazon AWS + Cerebras](https://www.aboutamazon.com/news/aws/aws-cerebras-ai-inference)、[Cerebras Q2 2026 results](https://www.sec.gov/Archives/edgar/data/2021728/000162828026056186/cbrsannouncesfinancialresu.htm) |
| Amazon Bedrock（整體服務，未逐模型說明） | AWS Trainium | 股東信："runs most of its inference on Trainium"；財報電話會（CFO Olsavsky）："A consistent majority of Bedrock's workloads run on Trainium"；2025-12 已在 Trainium3 上服務正式環境工作負載；比例未揭露 | 2025-12-02；2026-04-09；2026-04-29 | 廠商聲明 | C | [About Amazon Trainium3](https://www.aboutamazon.com/news/aws/trainium-3-ultraserver-faster-ai-training-lower-cost)、[Amazon 股東信](https://www.aboutamazon.com/news/company-news/amazon-ceo-andy-jassy-2025-letter-to-shareholders)、[Q1 2026 財報電話會](https://www.fool.com/earnings/call-transcripts/2026/04/29/amazon-amzn-q1-2026-earnings-call-transcript/) |
| Meta（未指明模型） | AMD GPU | 最高 6 GW；機型與起始日未載明 | 2026-07-24（AMD Advancing AI 2026 的報導） | 媒體報導 | C | [Moor Insights 2026-07-24](https://moorinsightsstrategy.com/field-notes/amd-advancing-ai-2026-helios-ships-venice-swings-and-the-software-moat-narrows/) |
| Meta（未指明） | Google TPU | 多年期、數十億美元合約，租用 TPU「用於開發新 AI 模型」（以訓練為主）；並評估自購 TPU | 2026-02-27 | 媒體報導 | C | [The Decoder 2026-02-27](https://the-decoder.com/meta-signs-multi-billion-dollar-deal-to-rent-googles-tpus-in-a-direct-challenge-to-nvidias-ai-chip-dominance/) |
| Mistral（Le Chat） | Cerebras | 規模未載明；Cerebras 專屬推論型錄列有 Mistral Small、Large 3、Devstral 2、Mixtral（企業洽詢）；2026 年狀況查無公開資料 | 2025 年度回顧（日期未載） | 廠商聲明 | C | [Cerebras blog 2025 回顧](https://www.cerebras.ai/blog/2026Insights)、[Cerebras docs Dedicated Inference](https://inference-docs.cerebras.ai/dedicated/overview) |
| SpaceXAI（xAI，Grok） | NVIDIA Vera Rubin | 規模、用途（訓練或推論）與模型均未載明；NVIDIA 的 Vera Rubin 量產新聞稿把 SpaceXAI 列在採用 NVIDIA Confidential Computing 的雲端業者名單中 | 2026-05-31 | 廠商聲明 | C | [NVIDIA IR 2026-05-31](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Vera-Rubin-Ramps-Into-Full-Production-to-Power-Agentic-AI-Factories-Worldwide/default.aspx) |

- 規模欄的基準各異（「最高」「選購權」「報導」），GW、晶片數與金額不能相加，也不能換算成 tokens/s。
- 沒有任何來源把 Amazon Bedrock、Google Vertex AI、Microsoft Azure 或第一方 API 上的某個 Claude / GPT 端點對應到特定晶片。Anthropic 自述同時使用 Trainium、TPU 與 NVIDIA GPU，所讀的 Trainium 與 TPU 來源也都沒有指出 200K 或 1M-token 的長 context 請求跑在哪種硬體。OpenAI 的 GPT-6 系列已在 Bedrock 與 Azure 上架，這些端點的晶片同樣未揭露（[OpenAI on Amazon Bedrock](https://developers.openai.com/api/docs/guides/amazon-bedrock)）。
- Anthropic 的 Trainium2 用量（D）：Rainier 約 50 萬顆 Trainium2（2025-10-29）、Trainium 已部署「超過 100 萬顆」（2025-12-02，[DataCenterDynamics](https://www.datacenterdynamics.com/en/news/aws-makes-trainium3-ultraservers-generally-available/)）、Jassy 稱已 "landed over 1.4 million Trainium two chips"（2026-02-05，[Motley Fool 逐字稿](https://www.fool.com/earnings/call-transcripts/2026/02/05/amazon-amzn-q4-2025-earnings-call-transcript/)）、Claude 跑在「超過 100 萬顆 Trainium2」上（2026-07-31，[About Amazon 晶片事業](https://www.aboutamazon.com/news/aws/amazon-ai-chips-business-history)），四項數字互相相容。以 1.0 ÷ 1.4 ≈ 71% 估算，Claude 占 Trainium2 機隊的多數，其餘留給 Bedrock 的其他模型與外部客戶；後兩個數字相隔近 6 個月，這是本文推算，不是廠商所說。
- Amazon Nova 已陳述：Nova 2 系列支援最高 1M tokens 的 context 與 65,536 輸出 tokens（[Nova 2 developer guide](https://docs.aws.amazon.com/nova/latest/nova2-userguide/what-is-nova-2.html)）；Bedrock 延遲最佳化推論支援 Nova Pro，但文件沒有說明用哪種晶片（[Bedrock 延遲最佳化推論](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html)）；About Amazon（2026-07-31）寫 Peter DeSantis「領導涵蓋 AI 模型、自研晶片與量子運算的新組織」，這是組織安排，不是對應關係（[About Amazon 晶片事業](https://www.aboutamazon.com/news/aws/amazon-ai-chips-business-history)）。未陳述：Nova 是否在 Trainium 上訓練或服務，所讀頁面皆未載明，查無公開資料（未做專門搜尋）。
- NVIDIA 的 Groq 3 LPX 公開點名的使用者只有 Nebius（Token Factory）與 Groq（[NVIDIA 新聞稿，2026-08-24](https://nvidianews.nvidia.com/news/nvidia-groq-3-lpx-now-in-full-production-with-world-class-speed-for-agentic-ai)）；沒有任何私有模型被說明跑在 LPX 上，OpenAI Ultrafast 的來源只寫 NVIDIA GPU，未提到 LPX。
- 「約 300 tokens/s」的歸屬不一致：VentureBeat（2026-09-29）把「300 tokens per second」放在 GPT-6.1 Sol 發表報導的標題，稱為新的 Ultrafast tier；SemiAnalysis（2026-09-30）把約 300 tokens/s 歸給 GPT-6.1 Sol Ultrafast；本章第 2 節反推 GPT-6 Astra 標準速度時，假設 300 也適用於 GPT-6 Astra Ultrafast。三者是否指同一個端點，來源沒有釐清。
- 查無公開資料（本次未研究）：OpenAI 自研晶片、Microsoft 自家加速器與 MAI 模型的服務晶片、Meta 自家晶片、xAI 自有叢集與 Grok 的服務晶片（僅有表 5-1 的 NVIDIA 名單一項）、Mistral 自家部署晶片、Gemini 在 GPU 上的服務。Inferentia：所讀來源沒有任何私有前沿模型被說明跑在 Inferentia 上，本次未研究 Inferentia 的服務案例。

## 公開可得的 TPS / TTFT 統計與 fast mode

2026-10-04 的獨立量測顯示，旗艦推理模型在第一方 API 標準層級的輸出速度約 45–92 tokens/s（各 effort 的範圍：GPT-6 Astra 44.9–51.6、Claude Fable 5.1 48.6–68.2、Claude Opus 5.5 72.2–92.4），Gemini 3.8 Flash（high）為 236.5 tokens/s；TTFT 在 reasoning 關閉時為 0.56–1.05 s，Anthropic 與 OpenAI 第一方 API 在 max effort 時為 126–705 s。fast 與 priority 層級在 OR 即時流量中有獨立量測（Anthropic fast mode 在 Claude Opus 5.5 上為 118 對 71 tokens/s，1.66×，價格 2×；OpenAI Fast 為 0.96–1.31×），OpenAI Ultrafast（6× 價格）、Cerebras 上的 Codex-Spark 與 GPT-5.6 Sol Ultrafast 沒有獨立量測，而且沒有任何一筆獨立量測附有晶片資訊。

### (a) 第三方量測：Artificial Analysis 與 OpenRouter

- **Artificial Analysis（AA，等級 A）**：從單一位置（Google Cloud us-central1-a 的 VM）發出的合成單一串流測試。預設工作負載為約 10K input tokens、至少 1,500 answer tokens，1K 與 10K 每天測 8 次、100K 每週測 1 次；數值為過去 72 小時的中位數（100K 為過去 14 天）；token 一律用 tiktoken o200k_base 計算。AA 要求供應商不得把 AA 流量導向專屬或非公開資源（[AA 方法論](https://artificialanalysis.ai/methodology/performance-benchmarking)）。
- AA 的 TTFT 在有 reasoning 的 Claude 與 GPT 變體上等於「第一個 answer token」的時間，含隱藏的 thinking（D：AA 原始表中這些列的 TTFT 與 time to first answer token 兩欄數值相同），所以只適合比較同一模型的不同 effort。AA model page 的「TTFT」是 time to first chunk，定義不同：Claude Opus 5.5 low 在 Anthropic API 上，leaderboard 為 12.39 s、model page 為 4.07 s。
- **OpenRouter（OR，等級 A）**：真實客戶流量的遙測，每個端點取 30 分鐘窗口的 p50–p99「latency」與「throughput」及請求數；本文把 latency 當 TTFT、throughput 當 tokens/s（OR 的欄位定義未逐字確認）。prompt 長度、輸出長度與 effort 由客戶決定，端點之間的客戶組成不同，不嚴格可比；請求數 < 100 的端點樣本過薄，不列入表 5-5。
- 兩個來源都不是服務水準保證，同一端點的水準也不同：GPT-6 Luna 在 OpenAI API 上，AA 為 120.5–140.7 tokens/s（各 effort）、OR 為 82–83。AA 同一端點的兩次讀數（leaderboard 為 00:36 UTC、model page 為 06:53 UTC）在 19 個可比列上，10K 速度中位數相差 1.7%、最大 15.9%（GPT-6 Astra max，OpenAI API：51.6 → 59.8），16 列在 5% 以內（D），所以小於約 5% 的端點差異視為雜訊。

**表 5-2 AA 各端點的輸出速度與 TTFT**（10K-token prompt；72 小時中位數；2026-10-04 00:36 UTC 快照；等級 A；來源：[AA providers leaderboard](https://artificialanalysis.ai/leaderboards/providers)。AA 寫「Claude 4.5 Haiku」者即 Claude Haiku 4.5；無後綴的列 TTFT 為 17–21 s，應為 reasoning 變體（推論）。‡ 的列取自 AA Google 供應商頁，快照時間不同，且不在 leaderboard 的「現行」清單內，來源為 [AA Google 供應商頁](https://artificialanalysis.ai/providers/google)）

| 模型（AA 變體標籤） | 端點 | 輸出 tokens/s 中位（p5–p95） | TTFT 中位（s） |
|---|---|---|---|
| Claude Fable 5.1 (low with fallback) | Anthropic API | 48.6 (43–67) | 4.49 |
| Claude Fable 5.1 (medium with fallback) | Anthropic API | 51.5 (44–67) | 8.79 |
| Claude Fable 5.1 (high with fallback) | Anthropic API | 53.1 (42–81) | 25.00 |
| Claude Fable 5.1 (xhigh with fallback) | Anthropic API | 59.2 (47–84) | 106.70 |
| Claude Fable 5.1 (max with fallback) | Anthropic API | 68.2 (57–74) | 238.66 |
| Claude Opus 5.5 (low with fallback) | Anthropic API | 72.2 (60–88) | 12.39 |
| Claude Opus 5.5 (low with fallback) | Amazon Bedrock | 57.6 (46–75) | 13.48 |
| Claude Opus 5.5 (low with fallback) | Google Vertex AI | 71.7 (64–90) | 14.38 |
| Claude Opus 5.5 (medium with fallback) | Anthropic API | 72.8 (60–90) | 25.75 |
| Claude Opus 5.5 (high with fallback) | Anthropic API | 73.4 (61–89) | 38.91 |
| Claude Opus 5.5 (xhigh with fallback) | Anthropic API | 79.6 (66–92) | 141.03 |
| Claude Opus 5.5 (max with fallback) | Anthropic API | 92.4 (82–101) | 704.69 |
| Claude Sonnet 5.5 (low with fallback) | Anthropic API | 92.6 (78–157) | 1.19 |
| Claude Sonnet 5.5 (low with fallback) | Amazon Bedrock | 94.6 (79–154) | 1.25 |
| Claude Sonnet 5.5 (low with fallback) | Google Vertex AI | 96.0 (81–151) | 1.36 |
| Claude Sonnet 5.5 (medium with fallback) | Anthropic API | 92.0 (82–129) | 1.34 |
| Claude Sonnet 5.5 (high with fallback) | Anthropic API | 101.0 (87–124) | 12.20 |
| Claude Sonnet 5.5 (xhigh with fallback) | Anthropic API | 101.2 (86–161) | 34.69 |
| Claude Sonnet 5.5 (max with fallback) | Anthropic API | 132.2 (122–148) | 428.36 |
| Claude Sonnet 5.5 (max with fallback) | Amazon Bedrock | 129.5 (112–149) | 341.05 |
| Claude Sonnet 5.5 (max with fallback) | Google Vertex AI | 133.8 (113–147) | 435.41 |
| Claude Haiku 4.5 (non-reasoning) | Anthropic API | 88.5 (76–124) | 0.56 |
| Claude Haiku 4.5 (non-reasoning) | Amazon Bedrock | 99.8 (85–197) | 0.80 |
| Claude Haiku 4.5 (non-reasoning) | Google Vertex AI | 86.9 (72–145) | 0.68 |
| Claude Haiku 4.5 (non-reasoning) | Microsoft Azure | 90.8 (77–151) | 0.99 |
| Claude Haiku 4.5（AA 無後綴） | Anthropic API | 97.4 (76–160) | 19.33 |
| Claude Haiku 4.5（AA 無後綴） | Amazon Bedrock | 132.2 (93–221) | 20.67 |
| Claude Haiku 4.5（AA 無後綴） | Google Vertex AI | 94.9 (81–187) | 17.19 |
| Claude Haiku 4.5（AA 無後綴） | Microsoft Azure | 97.9 (76–171) | 20.16 |
| GPT-6 Astra (low) | OpenAI API | 50.7 (38–73) | 2.65 |
| GPT-6 Astra (low) | Microsoft Azure | 54.9 (45–91) | 3.16 |
| GPT-6 Astra (medium) | OpenAI API | 44.9 (38–59) | 6.21 |
| GPT-6 Astra (high) | OpenAI API | 45.4 (36–57) | 65.56 |
| GPT-6 Astra (xhigh) | OpenAI API | 49.3 (36–62) | 181.00 |
| GPT-6 Astra (max) | OpenAI API | 51.6 (44–67) | 320.14 |
| GPT-6 Astra (max) | Amazon Bedrock | 79.5 (51–95) | 346.83 |
| GPT-6 Astra (max) | Microsoft Azure | 69.4 (53–89) | 343.27 |
| GPT-6.1 Sol (low) | OpenAI API | 54.7 (37–74) | 3.25 |
| GPT-6.1 Sol (medium) | OpenAI API | 45.4 (34–68) | 5.59 |
| GPT-6.1 Sol (high) | OpenAI API | 58.2 (39–68) | 57.61 |
| GPT-6.1 Sol (xhigh) | OpenAI API | 53.4 (45–67) | 110.28 |
| GPT-6.1 Sol (max) | OpenAI API | 52.1 (46–67) | 269.34 |
| GPT-6 Luna (non-reasoning) | OpenAI API | 131.0 (93–170) | 0.68 |
| GPT-6 Luna (low) | OpenAI API | 120.5 (98–163) | 2.06 |
| GPT-6 Luna (high) | OpenAI API | 133.3 (82–169) | 13.92 |
| GPT-6 Luna (xhigh) | OpenAI API | 136.4 (94–157) | 22.85 |
| GPT-6 Luna (max) | OpenAI API | 132.5 (103–187) | 125.75 |
| GPT-6 Luna (max) | Microsoft Azure | 211.8 (164–360) | 59.57 |
| GPT-5.6 Terra (non-reasoning) | OpenAI API | 87.4 (72–122) | 0.72 |
| GPT-5.6 Terra (non-reasoning) | Amazon Bedrock | 108.2 (92–172) | 0.72 |
| GPT-5.6 Terra (low) | OpenAI API | 84.8 (71–144) | 1.66 |
| GPT-5.6 Terra (medium) | OpenAI API | 76.2 (62–114) | 2.39 |
| GPT-5.6 Terra (high) | OpenAI API | 85.0 (66–145) | 3.08 |
| GPT-5.6 Terra (high) | Microsoft Azure | 117.4 (102–168) | 2.86 |
| GPT-5.6 Terra (xhigh) | OpenAI API | 91.5 (74–143) | 24.24 |
| GPT-5.6 Terra (xhigh) | Microsoft Azure | 124.7 (105–164) | 21.86 |
| GPT-5.6 Terra (max) | OpenAI API | 102.5 (79–176) | 156.49 |
| GPT-5.6 Terra (max) | Amazon Bedrock | 133.7 (101–208) | 150.22 |
| GPT-5.5 Instant (June 2026) | OpenAI API | 117.6 (100–188) | 0.92 |
| GPT-5.3 Codex (xhigh) | OpenAI API | 94.6 (70–126) | 71.47 |
| Gemini 3.1 Pro Preview | Google AI Studio | 116.8 (100–145) | 24.14 |
| Gemini 3.1 Pro Preview | Google Vertex AI | 99.9 (96–107) | 26.44 |
| Gemini 3.8 Flash (high) | Google AI Studio | 236.5 (186–349) | 14.73 |
| Gemini 3.7 Flash (low reasoning)‡ | Google AI Studio | 292.7 (–) | 1.41 |
| Gemini 3.5 Flash (minimal reasoning)‡ | Google AI Studio | 196.8 (–) | 0.97 |
| Gemini 3.5 Flash-Lite | Google AI Studio | 360.0 (263–470) | 8.82 |
| Nova 2.0 Pro Preview (non-reasoning) | Amazon Bedrock | 106.9 (93–136) | 1.01 |
| Nova 2.0 Pro Preview (low) | Amazon Bedrock | 125.3 (109–150) | 13.25 |
| Nova 2.0 Pro Preview (medium) | Amazon Bedrock | 119.4 (108–162) | 12.87 |
| Nova 2.0 Lite (non-reasoning) | Amazon Bedrock | 169.9 (117–225) | 1.05 |
| Nova 2.0 Lite (low) | Amazon Bedrock | 147.5 (100–263) | 10.76 |
| Nova 2.0 Lite (medium) | Amazon Bedrock | 197.4 (144–258) | 14.74 |
| Nova 2.0 Lite (high) | Amazon Bedrock | 185.9 (135–269) | 17.44 |
| Nova Micro | Amazon Bedrock | 279.6 (200–352) | 0.87 |
| Grok 4.7 (low) | SpaceXAI (xAI) API | 76.3 (57–96) | 8.92 |
| Grok 4.7 (high) | SpaceXAI (xAI) API | 77.8 (63–114) | 30.21 |
| Grok 4.7 (xhigh) | SpaceXAI (xAI) API | 79.0 (58–107) | 49.32 |
| Muse Spark 1.3 (xhigh) | Meta Model API | 142.4 (69–306) | 39.81 |
| Muse Spark 1.3 (max) | Meta Model API | 129.0 (73–189) | 53.10 |

- 速度隨 effort 上升只出現在 Anthropic 模型（low 到 max：Fable 5.1 為 48.6 → 68.2、Opus 5.5 為 72.2 → 92.4、Sonnet 5.5 為 92.6 → 132.2 tokens/s），OpenAI 的 Astra 與 Sol 不單調；來源沒有解釋原因。
- AA 模型層級的列沒有端點資料：Mistral Medium 3.5 為 165.4 tokens/s、TTFT 2.30 s（第一個 answer token 為 14.4 s），Mistral Large 3 為 79.0 tokens/s、TTFT 1.13 s（[AA models leaderboard](https://artificialanalysis.ai/leaderboards/models)）。Gemini 4 Argon 與 Gemini 3.8 Flash 的 low、medium 變體尚無速度資料；Gemini 3.6 Flash 與 3.1 Flash-Lite 的 AA 數字本次未取得。
- AA 的模型索引（933 個 slug）在 2026-10-04 沒有 GPT-5.3-Codex-Spark、任何 Ultrafast 變體、任何 OpenAI Fast 變體或任何 Claude fast 變體（[AA 模型索引](https://artificialanalysis.ai/models)）。
- AA 只從美國的單一區域發出請求，沒有亞洲（例如台灣）發出的量測，客戶的區域延遲本章無法回答。

**表 5-3 AA model page：prompt 長度與 10 個並行請求的影響**（1K、10K、100K tokens；1K 與 10K 為 72 小時中位數，100K 為 14 天中位數；2026-10-04 06:53 UTC 讀取；等級 A；TTFT 為 time to first chunk；§ 為 00:35–00:37 UTC 的頁面副本；來源為各模型的 AA providers 頁，例如 [Claude Haiku 4.5](https://artificialanalysis.ai/models/claude-4-5-haiku/providers)、[Claude Opus 5.5 low](https://artificialanalysis.ai/models/claude-opus-5-5-low/providers)、[GPT-6 Astra](https://artificialanalysis.ai/models/gpt-6-astra/providers)、[GPT-5.6 Sol](https://artificialanalysis.ai/models/gpt-5-6-sol/providers)、[Gemini 3.1 Pro Preview](https://artificialanalysis.ai/models/gemini-3-1-pro-preview/providers)）

| 模型（變體） | 端點 | 1K：tokens/s；TTFT s | 10K：tokens/s；TTFT s（p5–p95） | 100K：tokens/s；TTFT s | 10 並行 1K：tokens/s；TTFT s | 100K ÷ 10K 速度（D） | 快取命中率 |
|---|---|---|---|---|---|---|---|
| Claude Haiku 4.5 (non-reasoning) | Bedrock | 130.3；0.59 | 100.5；0.80（0.70–1.05） | 121.8；3.48 | 128.7；0.71 | 1.21× | 67% |
| Claude Haiku 4.5 (non-reasoning) | Azure | 103.1；0.80 | 89.3；0.97（0.78–1.49） | 85.6；3.27 | 116.5；0.93 | 0.96× | 91% |
| Claude Haiku 4.5 (non-reasoning) | Vertex | 108.6；0.60 | 85.5；0.68（0.47–0.87） | 122.9；4.54 | 117.2；0.62 | 1.44× | 88% |
| Claude Haiku 4.5 (non-reasoning) | Anthropic | 105.5；0.48 | 84.1；0.55（0.51–1.54） | 100.4；2.48 | 111.5；0.50 | 1.19× | 80% |
| Claude Sonnet 5.5 (low effort) | Vertex | 101.6；1.33 | 98.5；1.43（0.81–2.67） | 114.8；12.12 | 112.7；1.00 | 1.17× | – |
| Claude Sonnet 5.5 (low effort) | Bedrock | 96.3；0.92 | 94.6；1.26（1.15–3.26） | 117.5；5.17 | 114.9；0.89 | 1.24× | – |
| Claude Sonnet 5.5 (low effort) | Anthropic | 105.2；0.83 | 92.6；1.16（0.66–3.76） | 115.7；2.97 | 110.9；0.82 | 1.25× | 99% |
| Claude Opus 5.5 (low effort) | Vertex | 79.1；8.44 | 72.8；6.46（1.90–20.19） | 70.9；12.18 | 81.3；2.78 | 0.97× | 90% |
| Claude Opus 5.5 (low effort) | Anthropic | 74.8；4.74 | 71.0；4.07（1.32–29.45） | 75.5；16.92 | 78.4；5.89 | 1.06× | 100% |
| Claude Opus 5.5 (low effort) | Bedrock | 62.4；8.17 | 56.5；6.63（2.11–30.73） | 69.5；13.42 | 63.1；5.00 | 1.23× | 100% |
| Claude Opus 5.5 (medium effort)§ | Anthropic | 79.5；12.04 | 71.9；22.18（6.84–60.02） | 82.6；21.18 | 79.3；10.78 | 1.15× | 100% |
| GPT-6 Astra (max effort) | Bedrock | 89.0；136.87 | 81.4；268.12（98.42–529.33） | 64.2；236.47 | 90.6；77.58 | 0.79× | 99% |
| GPT-6 Astra (max effort) | Azure | 71.3；204.04 | 65.5；312.75（158.15–526.99） | 69.6；257.24 | 76.6；128.79 | 1.06× | 98% |
| GPT-6 Astra (max effort) | OpenAI | 62.6；201.15 | 59.8；276.50（118.57–480.66） | 59.9；275.98 | 65.4；108.46 | 1.00× | 99% |
| GPT-6 Luna (max effort) | Azure | 220.6；55.79 | 208.9；54.88（26.55–135.79） | 231.9；29.25 | 231.4；28.40 | 1.11× | – |
| GPT-6 Luna (max effort) | OpenAI | 136.4；84.00 | 140.7；107.01（27.66–203.65） | 126.8；43.62 | 160.6；43.73 | 0.90× | 99% |
| GPT-5.6 Sol (max effort) | Bedrock | – | 95.0；96.63（22.34–325.92） | 108.3；34.69 | – | 1.14× | 94% |
| GPT-5.6 Sol (max effort) | Azure | – | 90.9；123.98（18.18–280.62） | 116.8；50.51 | – | 1.28× | 99% |
| GPT-5.6 Sol (max effort) | OpenAI | – | 79.6；106.10（18.63–337.93） | 92.0；97.70 | – | 1.16× | 99% |
| GPT-5.6 Terra (non-reasoning) | Bedrock | 114.4；0.49 | 108.2；0.72（0.50–2.06） | 126.0；2.38 | 143.4；0.46 | 1.16× | 99% |
| GPT-5.6 Terra (non-reasoning) | OpenAI | 99.4；0.69 | 91.7；0.72（0.60–2.22） | 106.9；1.17 | 110.6；0.76 | 1.17× | 99% |
| Gemini 3.8 Flash (high)§ | AI Studio | 270.4；11.49 | 242.3；16.13（8.86–70.99） | 226.0；16.37 | 283.3；12.08 | 0.93× | 89% |
| Gemini 3.1 Pro Preview§ | AI Studio | 129.8；24.67 | 113.6；24.14（15.40–73.18） | 108.1；35.39 | 135.8；21.74 | 0.95× | 93% |
| Gemini 3.1 Pro Preview§ | Vertex | 98.9；18.12 | 100.0；26.44（13.06–67.57） | 165.0；41.21 | 97.7；24.61 | 1.65× | 78% |

- 100K 對 10K 的速度比（D）：24 列的中位數為 1.15×，18 列 ≥ 1.0、6 列 < 1.0（最低為 GPT-6 Astra max 在 Bedrock 的 0.79×），來源沒有說明差異來自什麼。兩欄的平均窗口不同（14 天對 72 小時）。
- 10 個並行 1K 請求下的每串流速度是單一 1K 請求的 0.99–1.25×（21 列，中位數 1.05×，D）：在 AA 的並行度內，每串流速度沒有下降。
- 長 prompt 主要拉長 TTFT：Claude Haiku 4.5 non-reasoning 從 10K 的 0.55–0.97 s 到 100K 的 2.48–4.54 s；GPT-5.6 Terra non-reasoning 從 0.72 s 到 1.17 s（OpenAI）與 2.38 s（Bedrock）。AA 同時列出快取命中率（67–100%）；其定義未能從所讀頁面確認，若代表 prompt cache 命中，表中長 prompt 的 TTFT 是熱快取數字，冷啟動的 prefill 時間無法由此看出（推論，未驗證）。

**表 5-4 同一模型在不同雲端的 AA 速度**（儲存格為「輸出 tokens/s；TTFT s」；10K-token prompt；2026-10-04；等級 A；無標記的列取自 00:36 UTC 的 leaderboard，‡ 的列取自 06:53 UTC 的 model page，其 TTFT 為 time to first chunk，定義與 leaderboard 不同；最右欄為 D：最快端點 ÷ 最慢端點的 tokens/s）

| 模型（AA 變體） | 第一方 API | Amazon Bedrock | Google Vertex AI | Microsoft Azure | 最快 ÷ 最慢（D） |
|---|---|---|---|---|---|
| Claude Opus 5.5（low with fallback） | 72.2；12.39（Anthropic） | 57.6；13.48 | 71.7；14.38 | – | 1.25×（Anthropic ÷ Bedrock） |
| Claude Sonnet 5.5（low with fallback） | 92.6；1.19（Anthropic） | 94.6；1.25 | 96；1.36 | – | 1.04×（Vertex ÷ Anthropic） |
| Claude Sonnet 5.5（max with fallback） | 132.2；428.36（Anthropic） | 129.5；341.05 | 133.8；435.41 | – | 1.03×（Vertex ÷ Bedrock） |
| Claude Haiku 4.5（non-reasoning） | 88.5；0.56（Anthropic） | 99.8；0.8 | 86.9；0.68 | 90.8；0.99 | 1.15×（Bedrock ÷ Vertex） |
| Claude Haiku 4.5（AA 無後綴） | 97.4；19.33（Anthropic） | 132.2；20.67 | 94.9；17.19 | 97.9；20.16 | 1.39×（Bedrock ÷ Vertex） |
| GPT-6 Astra（low） | 50.7；2.65（OpenAI） | – | – | 54.9；3.16 | 1.08×（Azure ÷ OpenAI） |
| GPT-6 Astra（max） | 51.6；320.14（OpenAI） | 79.5；346.83 | – | 69.4；343.27 | 1.54×（Bedrock ÷ OpenAI） |
| GPT-6 Luna（max） | 132.5；125.75（OpenAI） | – | – | 211.8；59.57 | 1.60×（Azure ÷ OpenAI） |
| GPT-5.6 Terra（non-reasoning） | 87.4；0.72（OpenAI） | 108.2；0.72 | – | – | 1.24×（Bedrock ÷ OpenAI） |
| GPT-5.6 Terra（high） | 85；3.08（OpenAI） | – | – | 117.4；2.86 | 1.38×（Azure ÷ OpenAI） |
| GPT-5.6 Terra（xhigh） | 91.5；24.24（OpenAI） | – | – | 124.7；21.86 | 1.36×（Azure ÷ OpenAI） |
| GPT-5.6 Terra（max） | 102.5；156.49（OpenAI） | 133.7；150.22 | – | – | 1.30×（Bedrock ÷ OpenAI） |
| Gemini 3.1 Pro Preview | 116.8；24.14（AI Studio） | – | 99.9；26.44 | – | 1.17×（AI Studio ÷ Vertex） |
| Claude Opus 4.8（max effort，舊版）‡ | 58.9；62.22（Anthropic） | 59.9；35.79 | 61.8；31.9 | – | 1.05×（Vertex ÷ Anthropic） |
| GPT-5.6 Sol（max effort）‡ | 79.6；106.1（OpenAI） | 95；96.63 | – | 90.9；123.98 | 1.19×（Bedrock ÷ OpenAI） |
| Grok 4.3（non-reasoning，已被 4.7 取代）‡ | 105.7；0.78（xAI） | 230.2；0.64 | – | – | 2.18×（Bedrock ÷ xAI） |

- 現行模型的雲端差異為 1.03–1.60×，沒有一個來源把端點對應到晶片，所以這些差異不能歸因於晶片。Sonnet 5.5 low 與 max（1.04×、1.03×）在雜訊範圍內，Astra low 的 1.08× 接近雜訊上限。
- Claude 的 6 組比較沒有固定的贏家（最快者在 Anthropic、Vertex、Bedrock 各有出現，差異 1.03–1.39×）；Opus 5.5 low 在 Bedrock 慢 20%（57.6 對 72.2 tokens/s）。
- OpenAI 模型的 8 組比較中，OpenAI API 全是最慢的端點，Bedrock 或 Azure 快 1.08–1.60×。OR 的即時流量顯示相反的方向（見表 5-5 後的說明）。
- Gemini 3.1 Pro Preview 在 Google 自家的兩個端點之間仍差 1.17×（AI Studio 116.8、Vertex 99.9 tokens/s）。舊版模型的最大差異為 Grok 4.3 non-reasoning 在 Bedrock 230.2、在 xAI API 105.7（2.18×）。

**表 5-5 OpenRouter 即時流量的標準層級速度**（2026-10-04 06:54–06:56 UTC；30 分鐘窗口；等級 A；只列請求數 ≥ 100 的端點；來源：OR 各模型頁，[Claude Opus 5.5](https://openrouter.ai/anthropic/claude-opus-5.5)、[Claude Sonnet 5.5](https://openrouter.ai/anthropic/claude-sonnet-5.5)、[Claude Haiku 4.5](https://openrouter.ai/anthropic/claude-haiku-4.5)、[Claude Fable 5.1](https://openrouter.ai/anthropic/claude-fable-5.1)、[GPT-6 Astra](https://openrouter.ai/openai/gpt-6-astra)、[GPT-6.1 Sol](https://openrouter.ai/openai/gpt-6.1-sol)、[GPT-6 Luna](https://openrouter.ai/openai/gpt-6-luna)、[GPT-5.6 Sol](https://openrouter.ai/openai/gpt-5.6-sol)、[Gemini 3.8 Flash](https://openrouter.ai/google/gemini-3.8-flash)、[Grok 4.7](https://openrouter.ai/x-ai/grok-4.7)；括號內為 p90；帶地區的端點為資料落地端點，價格加 10%）

| 模型 | 端點（OpenRouter 標籤） | tokens/s p50（p90） | latency s p50（p90） | 30 分鐘請求數 |
|---|---|---|---|---|
| Claude Opus 5.5 | Anthropic `anthropic` | 71.0 (102) | 3.72 (5.44) | 9,367 |
| Claude Opus 5.5 | Claude Platform on AWS `claude-on-aws` | 71.0 (102) | 4.43 (6.23) | 33,162 |
| Claude Opus 5.5 | Amazon Bedrock `amazon-bedrock` | 71.0 (89) | 4.64 (10.85) | 10,346 |
| Claude Opus 5.5 | Google Vertex `google-vertex/global` | 82.0 (105) | 3.05 (5.19) | 2,923 |
| Claude Opus 5.5 | Azure `azure/global` | 81.0 (111) | 3.72 (4.92) | 728 |
| Claude Opus 5.5 | Google Vertex `google-vertex/europe` | 98.0 (120) | 2.38 (3.71) | 131 |
| Claude Sonnet 5.5 | Anthropic `anthropic` | 92.0 (137) | 2.14 (4.12) | 9,197 |
| Claude Sonnet 5.5 | Claude Platform on AWS `claude-on-aws` | 101.0 (148) | 1.91 (7.15) | 23,255 |
| Claude Sonnet 5.5 | Google Vertex `google-vertex/global` | 94.0 (144) | 2.29 (5.31) | 10,854 |
| Claude Sonnet 5.5 | Azure `azure/global` | 54.0 (146) | 1.00 (2.82) | 5,494 |
| Claude Sonnet 5.5 | Google Vertex `google-vertex/europe` | 92.5 (132) | 1.98 (3.33) | 1,197 |
| Claude Sonnet 5.5 | Amazon Bedrock `amazon-bedrock` | 120.0 (165) | 1.09 (3.74) | 1,175 |
| Claude Haiku 4.5 | Anthropic `anthropic` | 78.0 (114) | 0.59 (1.11) | 6,319 |
| Claude Haiku 4.5 | Amazon Bedrock `amazon-bedrock/global` | 66.0 (125) | 0.75 (1.56) | 41,880 |
| Claude Haiku 4.5 | Google Vertex `google-vertex/global` | 84.0 (123) | 0.98 (3.74) | 916 |
| Claude Haiku 4.5 | Azure `azure/global` | 84.0 (113) | 0.42 (0.91) | 530 |
| Claude Haiku 4.5 | Amazon Bedrock `amazon-bedrock/us` | 76.0 (112) | 0.75 (1.01) | 266 |
| Claude Haiku 4.5 | Google Vertex `google-vertex/europe` | 79.0 (88) | 0.65 (0.80) | 155 |
| Claude Fable 5.1 | Anthropic `anthropic` | 52.0 (77) | 4.30 (6.49) | 5,268 |
| Claude Fable 5.1 | Google Vertex `google-vertex/global` | 62.0 (83) | 2.17 (7.26) | 182 |
| GPT-6 Astra | OpenAI `openai` | 40.0 (58) | 3.54 (14.64) | 12,041 |
| GPT-6 Astra | Azure `azure` | 29.0 (44) | 4.72 (11.75) | 23,612 |
| GPT-6 Astra | Azure `azure/us` | 33.0 (40) | 7.99 (92.89) | 181 |
| GPT-6.1 Sol | OpenAI `openai` | 47.0 (66) | 6.03 (33.13) | 52,932 |
| GPT-6.1 Sol | Azure `azure` | 46.0 (63) | 5.22 (13.17) | 8,696 |
| GPT-6.1 Sol | Azure `azure/us` | 38.0 (61) | 5.18 (11.75) | 1,001 |
| GPT-6.1 Sol | Amazon Bedrock `amazon-bedrock/us-east-1` | 21.0 (62) | 16.63 (34.00) | 139 |
| GPT-6 Luna | OpenAI `openai` | 83.0 (128) | 2.24 (7.19) | 333,872 |
| GPT-6 Luna | Azure `azure` | 77.0 (166) | 3.04 (9.41) | 71,722 |
| GPT-6 Luna | Amazon Bedrock `amazon-bedrock/us-east-1` | 26.0 (72) | 9.74 (22.05) | 2,715 |
| GPT-6 Luna | Azure `azure/eu` | 155.0 (182) | 3.64 (10.43) | 1,011 |
| GPT-6 Luna | Azure `azure/us` | 50.0 (102) | 1.89 (4.28) | 270 |
| GPT-5.6 Sol | OpenAI `openai` | 76.0 (135) | 2.61 (8.68) | 22,578 |
| GPT-5.6 Sol | Azure `azure` | 56.0 (79) | 4.29 (9.61) | 13,426 |
| Gemini 3.8 Flash | Google AI Studio `google-ai-studio` | 153.0 (277) | 1.47 (2.96) | 27,899 |
| Gemini 3.8 Flash | Google Vertex `google-vertex/global` | 95.0 (157) | 2.12 (4.62) | 111,590 |
| Grok 4.7 | SpaceXAI `xai/zdr` | 80.0 (130) | 1.91 (9.23) | 7,149 |
| Grok 4.7 | SpaceXAI `xai` | 76.0 (116) | 2.15 (7.77) | 3,911 |

- 方向與 AA 不一致（D）：OpenAI 模型在 OR 上，Bedrock 比第一方慢（GPT-6 Luna 26 對 83 tokens/s，0.31×，2,715 筆請求；GPT-6.1 Sol 21 對 47，0.45×，139 筆），Azure 的 GPT-6 Astra 也慢（29 對 40，0.73×，23,612 筆），而 AA 的合成測試中 Bedrock 與 Azure 都比第一方快（表 5-4）。請求數 < 100 的 GPT-5.6 Sol 在 Bedrock 為 40 tokens/s（66 筆），第一方為 76，同樣是相反方向。可能原因是 AA 以 max effort 與固定 10K prompt 測試，OR 是各客戶自選的 effort 與 prompt；本文沒有資料可以驗證。
- Gemini 3.8 Flash 的方向與 AA 一致：AI Studio 153 對 Vertex 95 tokens/s（1.61×，Vertex 有 111,590 筆請求）。
- 尾端延遲（D）：表中 38 列的 p90 latency 為 p50 的 1.2–11.6 倍，中位數 2.3 倍；最高的是 GPT-6.1 Sol 第一方（6.03 → 33.13 s，5.5×，52,932 筆）與 Azure eastus2 的 GPT-6 Astra（7.99 → 92.89 s，11.6×，181 筆）。容量規劃不能只看 p50。
- OR 另有 Claude Platform on AWS 作為獨立的 Claude 端點，Opus 5.5 在窗口內的請求數（33,162）多於 Anthropic API（9,367）與 Bedrock（10,346）。區域端點的速度各異（Opus 5.5 在 Vertex eu 為 98 tokens/s、131 筆；global 為 82），OR 的資料沒有亞洲區域。

### (b) Fast、priority 與 ultrafast 層級

各家的速度層級價格為標準價的 1.8–6×（Google Priority 1.8×、Anthropic 與 OpenAI Fast 2×、Bedrock Priority 1.75×、OpenAI Ultrafast 6×），獨立量測到的 tokens/s 增幅只有 0.96–1.66×（Opus 5.5 fast 1.66×、OpenAI Fast 0.96–1.31×、Gemini Priority 1.10–1.18×）；OpenAI Fast 的實際效果在 TTFT（latency 縮短約 1.65–3.9×，取兩次快照）。

**表 5-6 各雲端與模型廠商的 fast、priority、ultrafast 變體**（2026-10-04 讀取；速度宣稱為廠商說法，等級 C；價格與限制取自廠商文件，等級 B；獨立量測見表 5-7 與表 5-8）

| 模式（狀態） | 廠商的速度宣稱（C） | 價格倍數 | 範圍與限制 | 背後硬體 | 獨立量測 | 來源 |
|---|---|---|---|---|---|---|
| Anthropic fast mode（research preview；`speed: "fast"`） | "up to 2.5x higher output tokens per second"；效益在 OTPS 而非 TTFT；同一組權重 | 2×：Opus 5.5 $8 / $40；Opus 5、Opus 4.8 $10 / $50；> 200K 輸入同樣加價 | Opus 5.5、Opus 5、Opus 4.8；僅 Claude API，不在 Bedrock、Claude Platform on AWS、Google Cloud、Microsoft Foundry；需向客戶經理申請或候補；切換速度使 prompt cache 失效 | 未揭露 | 有：Opus 5.5 為 118 對 71 tokens/s（表 5-7） | [Claude fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode)、[Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| Anthropic Priority Tier | 無速度宣稱；只減少「server overloaded」錯誤 | 承諾制 | 不再開放購買新的 capacity commitments，僅既有合約 | 未揭露 | 無 | [Claude service tiers](https://platform.claude.com/docs/en/api/service-tiers) |
| OpenAI Fast mode（`service_tier: "fast"` 或 `"priority"`；2026-07-30 由 Priority 改名） | "up to 2.5× faster speeds and more consistent latency" | 2×：GPT-6 Astra $20 / $100；GPT-6.1 Sol $4 / $20；GPT-6 Luna $0.20 / $1.00；GPT-5.6 Sol $8 / $40；GPT-5.5 為 2.5× | GPT-6 與 GPT-5.6 全系列；GPT-6 不支援 EU data residency；Astra 的 Fast 無 latency SLA；流量每 15 分鐘增幅超過 50% 會降為標準 | 未揭露 | 有：tokens/s 0.96–1.31×，latency 縮短 1.65–2.31×（表 5-7） | [OpenAI Fast mode](https://developers.openai.com/api/docs/guides/fast-mode)、[OpenAI pricing](https://developers.openai.com/api/docs/pricing) |
| OpenAI Ultrafast（GPT-6 Astra；`service_tier: "ultrafast"`） | 媒體：「up to 300 generated tokens per second」、API 最高 6×、Codex 最高 8×；NVIDIA：最高 8× | 6× 標準、3× Fast：Astra $60 / $300；> 272K 輸入 $120 / $450；GPT-6.1 Sol Ultrafast 報導為 $12 / $60 | Astra 為 "broadly available"，GPT-5.6 Sol 為預覽，GPT-6.1 Sol「數日內」（2026-09-29 的說法）；僅支援美國 data residency 與 global processing | NVIDIA GPU（NVIDIA，2026-10-01）；GPT-6.1 Sol Ultrafast 報導為 NVIDIA 低 batch size、非 Cerebras（SemiAnalysis，2026-09-30，未證實） | 無：OR 有端點但窗口內無流量，AA 無列 | [OpenAI Ultrafast mode](https://developers.openai.com/api/docs/guides/ultrafast-mode)、[VentureBeat](https://venturebeat.com/technology/openais-gpt-6-1-sol-offers-astra-like-performance-at-1-5th-price-a-new-ultrafast-tier-clocks-at-300-tokens-per-second)、[NVIDIA 部落格](https://blogs.nvidia.com/blog/gpus-openai-gpt-6-astra-ultrafast/) |
| OpenAI GPT-5.6 Sol Ultrafast（limited preview，2026-08-13） | "up to 750 output tokens per second"；媒體："up to 14x"；GDPval 任務快 5.6×、Humanity's Last Exam 端到端快 6.9×（Cerebras 自測） | 未揭露 | 僅 API，限 "a select group of customers"；Cerebras：與標準相同的架構、權重、精度、context 與 reasoning 設定 | Cerebras CS-3（多套系統） | 無 | [Cerebras 2026-08-13](https://www.cerebras.ai/blog/accelerating-gpt-5-6-sol-ultrafast-with-openai)、[Cerebras 2026-08-27](https://www.cerebras.ai/blog/how-cerebras-serves-gpt-5-6-sol-at-up-to-750-tokens-per-second)、[The Decoder](https://the-decoder.com/gpt-5-6-sol-goes-14x-faster-as-openai-launches-ultrafast-mode-powered-by-cerebras/) |
| OpenAI GPT-5.3-Codex-Spark（research preview，2026-02-12） | "over 1,000 tokens/s"；SemiAnalysis：「最高 2,000 tok/sec/user」（分析師） | 無 API 定價 | ChatGPT Pro 的 Codex；API 僅限 design partners；是較小的另一個模型，不是 GPT-5.3-Codex 的層級 | Cerebras WSE-3 | 無 | [Cerebras blog 2026-02-12](https://www.cerebras.ai/blog/openai-codexspark)、[SemiAnalysis](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) |
| Google Priority inference（Preview；`service_tier: "priority"`） | "lower latency and the highest reliability"；延遲「Seconds」對標準的「Seconds to minutes」 | 文件寫「貴 75–100%」，實際 1.8×：Gemini 3.8 Flash $1.35 / $6.75；Gemini 3.1 Pro Preview $3.60 / $21.60（≤ 200K） | Gemini 3.8、3.7、3.6、3.5 Flash，3.5 與 3.1 Flash-Lite，3.1 Pro Preview，2.5 系列；預設速率上限為標準的 0.3×，溢出降為標準並以標準價計 | 未揭露（Google 稱 Gemini 在 TPU 上服務） | 有：tokens/s 1.10–1.18×，latency 未縮短（表 5-7） | [Gemini priority inference](https://ai.google.dev/gemini-api/docs/priority-inference)、[Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| Amazon Bedrock latency-optimized inference（Preview，2024-12 起） | "significantly reduced latency without compromising accuracy"；Claude 3.5 Haiku "up to 60% faster inference speed" | Claude 3.5 Haiku $1 / $5 對標準 $0.80 / $4（+25%） | 僅 Nova Pro、Claude 3.5 Haiku、Llama 3.1 405B 與 70B；US East（Ohio）、US West（Oregon），Nova Pro 另含 N. Virginia；沒有現行 Claude、Nova 2 或 GPT；超出配額退回標準 | AWS Trainium2 加軟體最佳化（AWS，2024-12-02 與 12-03） | AWS 自測（等級 B，2025-01-28，表 5-8）；AA 無（Claude 3.5 Haiku 已無供應商） | [Bedrock 延遲最佳化推論](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html)、[Anthropic 2024-12](https://claude.com/blog/trainium2-and-distillation) |
| Amazon Bedrock Priority tier（`service_tier: "priority"`） | "delivers the fastest response times for a price premium" | +75%（Flex 為 −50%） | 支援模型列在各模型卡片，Claude 與 GPT 是否支援未擷取；與 Standard、Flex 共用 on-demand 配額 | 未揭露 | 無 | [Bedrock service tiers](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html)、[Bedrock pricing](https://aws.amazon.com/bedrock/pricing/) |
| Azure（Microsoft Foundry）priority processing | 已發布的延遲目標：gpt-6-sol、gpt-5.6-sol "99% > 80 TPS"；gpt-5.6-terra "99% > 70 TPS"；gpt-5.5 "99% > 50 TPS" | 文件只寫定價見 Azure OpenAI pricing page，倍數未擷取 | Global Standard 與 US Data Zone Standard；表中沒有 gpt-6-astra、gpt-6.1-sol、gpt-6-luna；目標以每 5 分鐘的 p50 請求延遲計 | 未揭露 | 無 | [Azure priority processing](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/priority-processing) |
| AWS 與 Cerebras 的分離式推論（已宣布未出貨；2026-03-13 宣布，Cerebras 於 2026-08-12 預期 2027 Q1） | AWS："an order of magnitude faster and higher performance than what's available today"；Cerebras："up to 3,000 tokens per second" | 未揭露 | 只透過 Bedrock；開源 LLM 與 Nova 預計「later this year」（2026-03 的說法）；沒有區域、模型 ID 與價格 | Trainium3 做 prefill、Cerebras CS-3 做 decode，以 EFA 連接 | 無 | [About Amazon](https://www.aboutamazon.com/news/aws/aws-cerebras-ai-inference)、[Cerebras Q2 2026 財報](https://www.sec.gov/Archives/edgar/data/2021728/000162828026056186/cbrsannouncesfinancialresu.htm) |

- 其他層級：xAI Priority 的速度宣稱查無公開資料，OR 列出 Grok 4.7 Priority 為 $4 / $12（2×），窗口內無流量；Google 的 Gemini 3.5 Flash-Lite 是較便宜的另一個模型而非層級（$0.30 / $2.50；AA 360.0 tokens/s、p5–p95 為 263–470，TTFT 8.82 s）；OpenAI Flex 為標準價的 0.5×，實測見表 5-7。

**表 5-7 OpenRouter 即時流量中各速度層級對標準層級的實測**（2026-10-04 06:54–06:56 UTC；30 分鐘窗口；等級 A；倍數為 D：該層 ÷ 標準的 tokens/s，標準 ÷ 該層的 latency；價格倍數取自 OR 列出的輸入價；† 為請求數 < 100，Astra Fast 僅 7 筆，134.82 s 不具代表性）

| 模型與層級（OpenRouter 標籤） | 價格倍數（$/1M 輸入 / 輸出） | tokens/s p50：標準 → 該層 | 速度倍數（D） | latency s p50：標準 → 該層 | latency 縮短倍數（D） | 30 分鐘請求數 |
|---|---|---|---|---|---|---|
| Claude Opus 5.5 Fast / Priority `anthropic/fast` | 2×（8 / 40） | 71.0 → 118.0 | 1.66× | 3.72 → 2.92 | 1.27× | 185 |
| GPT-6 Astra Flex `openai/flex` | 0.5×（5 / 25） | 40.0 → 50.0 | 1.25× | 3.54 → 2.61 | 1.36× | 747 |
| GPT-6 Astra Fast / Priority `openai/fast` | 2×（20 / 100） | 40.0 → 45.0 | 1.12× | 3.54 → 134.82 | 0.03× | 7† |
| GPT-6 Astra Ultrafast `openai/ultrafast` | 6×（60 / 300） | 無流量 | – | 無流量 | – | 0 |
| GPT-6.1 Sol Flex `openai/flex` | 0.5×（1 / 5） | 47.0 → 43.5 | 0.93× | 6.03 → 5.64 | 1.07× | 2,213 |
| GPT-6.1 Sol Fast / Priority `openai/fast` | 2×（4 / 20） | 47.0 → 61.5 | 1.31× | 6.03 → 2.73 | 2.21× | 106 |
| GPT-6 Luna Flex `openai/flex` | 0.5×（0.05 / 0.25） | 83.0 → 32.0 | 0.39× | 2.24 → 3.49 | 0.64× | 49,553 |
| GPT-6 Luna Fast / Priority `openai/fast` | 2×（0.2 / 1） | 83.0 → 97.0 | 1.17× | 2.24 → 0.97 | 2.31× | 7,131 |
| GPT-5.6 Sol Flex `openai/flex` | 0.5×（1 / 5） | 76.0 → 92.0 | 1.21× | 2.61 → 2.32 | 1.12× | 496 |
| GPT-5.6 Sol Fast / Priority `openai/fast` | 2×（4 / 20） | 76.0 → 73.0 | 0.96× | 2.61 → 1.58 | 1.65× | 65† |
| Gemini 3.8 Flash Flex `google-ai-studio/flex` | 0.5×（0.375 / 1.875） | 153.0 → 156.0 | 1.02× | 1.47 → 1.66 | 0.89× | 16,023 |
| Gemini 3.8 Flash Fast / Priority `google-ai-studio/priority` | 1.8×（1.35 / 6.75） | 153.0 → 169.0 | 1.10× | 1.47 → 1.49 | 0.99× | 2,269 |
| Gemini 3.8 Flash Fast / Priority `google-vertex/global/priority` | 1.8×（1.35 / 6.75） | 95.0 → 112.0 | 1.18× | 2.12 → 2.77 | 0.77× | 281 |
| Gemini 3.8 Flash Flex `google-vertex/global/flex` | 0.5×（0.375 / 1.875） | 95.0 → 64.0 | 0.67× | 2.12 → 13.33 | 0.16× | 274 |
| Grok 4.7 Fast / Priority `xai/priority` | 2×（4 / 12） | 無流量 | – | 無流量 | – | 0 |

- Anthropic fast mode（D）：p50 為 118 ÷ 71 = 1.66×，p90 為 242 ÷ 102 = 2.37×，價格 2×；廠商的「最高 2.5×」只與 p90 相符，樣本為單一窗口的 185 筆請求。Anthropic 說效益集中在 OTPS，而 latency p50 也從 3.72 s 降到 2.92 s（1.27×）。
- OpenAI Fast 的 tokens/s 增幅小（Luna 1.17×、GPT-6.1 Sol 1.31×、GPT-5.6 Sol 0.96×），「最高 2.5×」在這些窗口沒有出現，效果主要在 TTFT（Luna 2.24 → 0.97 s、GPT-6.1 Sol 6.03 → 2.73 s、GPT-5.6 Sol 2.61 → 1.58 s）。同一端點數分鐘後的第二次快照（07:02 UTC）顯示 Fast 層的數字會波動：速度 Luna 97 與 106、GPT-6.1 Sol 61.5 與 52.5 tokens/s，相差 9–17%；latency 縮短倍數 Luna 2.31× 與 1.96×（2.24 → 0.97 與 1.14 s）、GPT-6.1 Sol 2.21× 與 3.92×（6.03 → 2.73 與 5.88 → 1.50 s，D），所以 10–15% 內的倍數差異不具意義。
- Google Priority 的行為像可靠度與排隊層級：tokens/s 多 10–18%，latency 沒有下降（AI Studio 1.47 → 1.49 s；Vertex 2.12 → 2.77 s）。OpenAI Flex 在 Luna 上只有標準速度的 0.39×（32 對 83 tokens/s），在 GPT-6 Astra 上卻是 1.25×，不同模型不一致。
- 價格 ÷ 速度（D）：Fast 與 Priority 的價格倍數（1.8–2×）高於實測速度倍數，每單位每使用者速度的價格上升 1.2–2.1×（Opus 5.5 為 2 ÷ 1.66 = 1.20；GPT-5.6 Sol 為 2 ÷ 0.96 = 2.08）；Ultrafast 為 6× 價格換最高 6–8× 速度（廠商說法），每單位速度的價格約持平或更高。
- Ultrafast 沒有獨立量測，只能檢查廠商數字是否自洽（D）：若「300 tokens/s」與「最高 8×」都指 GPT-6 Astra Ultrafast，隱含的標準速度為 300 ÷ 8 ≈ 38 tokens/s，接近 OR 的 40、低於 AA 的 44.9–51.6；GPT-5.6 Sol 的「最高 14×」隱含標準速度 750 ÷ 14 ≈ 54 tokens/s，低於 AA（79.6–95.0，max effort）與 OR（76），對實測標準速度只有 750 ÷ 79.6 = 9.4×、750 ÷ 76 = 9.9×。Cerebras 的「比 Fable 5 快 11×」與 AA 現在的 Claude Fable 5.1 max 相符（750 ÷ 68.2 = 11.0；Cerebras 寫的是 Fable 5，版本可能不同），其「比 Opus 4.8 fast 快 5×」隱含 Opus 4.8 fast 約 150 tokens/s，為 AA 現值 58.9 的 2.5×（兩個數字相隔七週）。
- Codex-Spark 的提速不全來自晶片：OpenAI 同時以 WebSocket 路徑把 client-server overhead 降 80%、per-token overhead 降 30%、TTFT 降 50%（Techzine 轉述，C，[Techzine](https://www.techzine.eu/news/analytics/138754/openai-swaps-nvidia-for-cerebras-with-gpt-5-3-codex-spark/)）；SemiAnalysis 估計它是約 120B 的蒸餾模型、約跑在 3 片 wafer 上（分析師推測）。

**表 5-8 Bedrock latency-optimized inference 對標準模式**（AWS 自測，2025-01-28；約 1,600 次 API 呼叫、橫跨數日；input 100–100,000 tokens、output 100–1,000 tokens；client 在 us-west-2、模型在 us-east-2；等級 B；來源：[AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/optimizing-ai-responsiveness-a-practical-guide-to-amazon-bedrock-latency-optimized-inference/)；標準 → 最佳化）

| 模型 | TTFT P50（s） | TTFT P90（s） | 輸出 tokens/s P50 | 輸出 tokens/s P90 | P50 速度倍數（D） | P90 速度倍數（D） |
|---|---|---|---|---|---|---|
| Claude 3.5 Haiku | 1.1 → 0.6 | 2.9 → 1.4 | 48.4 → 85.9 | 67.4 → 152.0 | 1.77× | 2.26× |
| Llama 3.1 70B | 0.9 → 0.4 | 42.8 → 1.2 | 30.2 → 137.0 | 32.4 → 203.7 | 4.54× | 6.29× |

- 這是 Trainium2 上唯一有方法說明的私有模型服務端數字，而且是一個已停用的模型（AA 對 Claude 3.5 Haiku 寫「No API providers are currently available」，[AA Claude 3.5 Haiku](https://artificialanalysis.ai/models/claude-3-5-haiku/providers)）。AWS 的測試文章本身沒有提到 Trainium；晶片歸屬來自 AWS 的另外兩篇公告："purpose-built AI chips like AWS Trainium2 and advanced software optimizations"（[AWS What's New，2024-12-02](https://aws.amazon.com/about-aws/whats-new/2024/12/latency-optimized-inference-foundation-models-amazon-bedrock/)）與 "Trainium2 chips are already powering the latency-optimized versions of Llama 3.1 405B and Claude 3.5 Haiku"（[AWS News Blog，2024-12-03](https://aws.amazon.com/blogs/aws/amazon-ec2-trn2-instances-and-trn2-ultraservers-for-aiml-training-and-inference-is-now-available/)）。
- 兩個數字不一致：Anthropic 說 Claude 3.5 Haiku "up to 60% faster"（2024-12-03，C），AWS 自測的 P50 為 +77%（85.9 ÷ 48.4 = 1.77）；兩者量的指標與條件不同，來源沒有調和。Llama 3.1 70B 的標準模式 TTFT P90 為 42.8 s，顯示基準線排隊嚴重，P90 的約 36 倍改善（42.8 ÷ 1.2）高估了硬體效應（D）。
- 狀態：到 2026-10-04 文件仍寫「in preview release」；支援模型沒有任何現行 Claude、Nova 2 或 GPT，所以 Trainium2 對現行 Claude 的每使用者速度沒有公開數字。

### (c) 同一個模型上的硬體效應

同一個私有模型在不同晶片上的獨立量測不存在：最接近的是廠商對同一組權重在不同硬體上的倍數宣稱（GPT-5.6 Sol 在 Cerebras 最高 750 tokens/s，對實測標準速度 76–95 約 8–10×），以及開源權重模型在多家供應商上的 AA 數字（gpt-oss-120b 在 Cerebras 為 1,781、在 Bedrock 為 86 tokens/s，相差 20.7×）。後者是硬體與服務堆疊的合併效應，AA 不揭露端點的硬體。

**表 5-9 同一個模型在不同硬體或端點上的公開比較**（私有模型列在前，開源權重模型作為量級參考；日期見各列；倍數為 D）

| 比較與日期 | 模型 | 硬體與出處 | 公開數字 | 倍數（D） | 等級 | 來源 |
|---|---|---|---|---|---|---|
| 標準 vs Ultrafast（2026-08-13 起） | GPT-5.6 Sol（私有） | 標準：未揭露；Ultrafast：Cerebras CS-3（Cerebras 與 OpenAI 的說法） | 標準 76 tokens/s（OR p50）、79.6–95.0（AA，max effort，10K）；Ultrafast「最高 750」 | 750 ÷ 79.6 = 9.4×；750 ÷ 76 = 9.9×；OpenAI 稱最高 14× | Ultrafast 為 C，標準為 A | [OpenAI 預覽](https://openai.com/index/previewing-ultrafast/)、[Cerebras](https://www.cerebras.ai/blog/how-cerebras-serves-gpt-5-6-sol-at-up-to-750-tokens-per-second) |
| 標準 vs Ultrafast（2026-10-01） | GPT-6 Astra（私有） | 標準：未揭露；Ultrafast：NVIDIA GPU（NVIDIA 部落格） | 標準 44.9–51.6（AA，OpenAI API）、40（OR）；Ultrafast「最高 300」、「最高 8×」 | 300 ÷ 40–51.6 = 5.8–7.5×；8× 隱含標準約 38 tokens/s | Ultrafast 為 C，標準為 A | [NVIDIA 部落格](https://blogs.nvidia.com/blog/gpus-openai-gpt-6-astra-ultrafast/)、[VentureBeat](https://venturebeat.com/technology/openais-gpt-6-1-sol-offers-astra-like-performance-at-1-5th-price-a-new-ultrafast-tier-clocks-at-300-tokens-per-second) |
| 標準 vs latency-optimized（2025-01-28） | Claude 3.5 Haiku（私有，已停用） | Trainium2 加軟體最佳化（AWS） | 48.4 → 85.9 tokens/s（P50） | 1.77× | B | [AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/optimizing-ai-responsiveness-a-practical-guide-to-amazon-bedrock-latency-optimized-inference/) |
| 同廠商兩個端點（2026-10-04） | Gemini 3.1 Pro Preview（私有） | AI Studio 與 Vertex 皆為 Google 端點，晶片未揭露（Google 稱 Gemini 在 TPU 上服務） | AI Studio 116.8、Vertex 99.9 tokens/s（AA，10K） | 1.17× | A | [AA providers leaderboard](https://artificialanalysis.ai/leaderboards/providers) |
| 多家供應商（2026-10-04） | gpt-oss-120b high（開源權重，參考） | AA 不揭露硬體；Cerebras 為 wafer-scale ASIC，SambaNova、Groq 為 ASIC，其餘為 GPU 雲或一般雲（類型為本文標示，D） | tokens/s：Cerebras 1,781；SambaNova 709；Groq 471；Azure 314；DeepInfra（Turbo）277；Nebius 240；Crusoe 205；Novita 184；Amazon Bedrock 86；DeepInfra（標準）51；CoreWeave 44；Google Vertex 40。TTFT：Cerebras 0.43 s、Crusoe 0.39 s、Vertex 38.59 s | Cerebras ÷ Azure = 5.7×；÷ Bedrock = 20.7× | 速度為 A，類型為 D | [AA gpt-oss-120b](https://artificialanalysis.ai/models/gpt-oss-120b/providers) |
| 跨晶片，每晶片吞吐量（2026-09-07） | Qwen3.5-397B FP8（開源權重，參考） | Ironwood 對 B200、B300；8K 輸入 / 1K 輸出、aggregated serving；SemiAnalysis InferenceX 預覽 | 20 tokens/s/user 時每晶片 9,364 / 8,903 / 8,925 total tokens/s；concurrency 256 的平均 TTFT 5.41 / 3.75 / 2.40 s | Ironwood ÷ B200 約 1.05×；TTFT 5.41 ÷ 3.75 = 1.44× | A（吞吐量） | [SemiAnalysis InferenceX](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam) |
| Trainium2 → Trainium3（2025-12-02） | gpt-oss（開源權重，AWS 測試） | Trn3 UltraServer 對 Trn2 UltraServer（AWS） | 每晶片 throughput "3x"、回應 "4x faster"；無絕對值、無方法 | 3×；4×（廠商倍數） | C | [About Amazon](https://www.aboutamazon.com/news/aws/trainium-3-ultraserver-faster-ai-training-lower-cost) |

- 表 5-4 的雲端差異（1.03–1.60×）不能當成晶片差異：沒有來源把端點對應到晶片，Gemini 3.1 Pro 在 Google 自家兩個端點之間就差 1.17×，顯示端點差異可來自服務設定。
- gpt-oss-120b 的 Cerebras 實測 1,781 tokens/s 只有其宣稱「約 3,000」的 59%（1,781 ÷ 3,000），TTFT 也不是最低（Crusoe 0.39 s 較低）。

### (d) 各加速器上的私有模型數字

**表 5-10 各加速器：私有模型的公開速度數字與缺口**（承接表 5-1；等級見各列）

| 加速器 | 表 5-1 中對應的私有模型 | 公開的每使用者速度（私有模型） | 等級 | 獨立量測 | 缺口 |
|---|---|---|---|---|---|
| AWS Trainium | Claude（Rainier；Trainium2 / 3 / 4 承諾）；Claude 3.5 Haiku（Bedrock latency-optimized） | 只有已停用的 Claude 3.5 Haiku：85.9 tokens/s（P50），標準為 48.4（Trainium2，2025-01-28）；Trainium3 只有相對倍數 | B；C | 無 | 現行 Claude 在哪種晶片上服務、tokens/s、TTFT |
| AWS Inferentia | 無 | 查無公開資料：所讀來源沒有任何私有前沿模型說明跑在 Inferentia 上 | – | – | 本次未研究 |
| Google TPU | Gemini（Google：在 TPU 上訓練並服務）；Claude（Anthropic：在 TPU 上訓練並執行） | Gemini 3.1 Pro Preview 99.9–116.8、Gemini 3.8 Flash 236.5–248.6、Gemini 3.5 Flash-Lite 360.0 tokens/s（AA，10K；端點的晶片世代未揭露）；規模：Google 全產品 3.2 quadrillion tokens/月（2026-05-19）≈ 1.2 billion tokens/s（D：3.2e15 ÷ (30 × 86,400)，未區分 input 與 output） | A（速度）；C（對應與規模） | AA 量的是端點，不是晶片 | TPU 世代、每晶片 tokens/s、input 與 output 比例 |
| NVIDIA GPU（含 AMD） | GPT-6 Astra Ultrafast；GPT-6.1 Sol Ultrafast（媒體報導）；Claude、OpenAI、SpaceXAI 的採購承諾 | Astra Ultrafast "up to 300 tokens per second"、"up to 8X"；其他私有模型沒有晶片對應；AMD 只有承諾規模，沒有任何私有模型的服務數字 | C | 無 | 標準層級的晶片對應、每 GPU 的 tokens/s |
| Cerebras | GPT-5.3-Codex-Spark；GPT-5.6 Sol Ultrafast；Mistral Le Chat | Codex-Spark "over 1,000"（SemiAnalysis：最高 2,000）、Sol Ultrafast "up to 750" tokens/s | C | 無（AA 無列） | 實測速度、每系統吞吐量、系統數量 |

## 價格與 context window

2026-10-04 現行旗艦的 context window 多為 1M tokens（GPT-6 系列為 1,050,000，Gemini 為 1,048,576），Grok 4.7 為 500K，Claude Haiku 4.5 為 200K；表中輸入價（每 1M tokens）從 Amazon Nova Micro 的 $0.035 到 Claude Fable 5.1 與 GPT-6 Astra 的 $10。長 prompt 加價在所讀來源中只見於 OpenAI（輸入超過 272K，整筆請求輸入 2×、輸出 1.5×）與 Gemini Pro（超過 200K，輸入 2×、輸出 1.5×），Anthropic 文件寫明 1M 全程標準價。

**表 5-11 現行私有模型的 context、最大輸出、價格與長 prompt 規則**（2026-10-04 讀取；list price、標準層級、USD 每 1M tokens，價格欄依序為輸入 / 快取讀取 / 輸出；等級欄指價格與 context 的來源（B 為廠商文件，C 為 AA、OpenRouter 目錄、二手報導或廠商公告）；發布日取自維基百科與 OpenRouter 上架日，廠商公告頁未讀，等級 C；「現行」指廠商文件列為 current 的 API 模型，文件未標 GA 或 Preview；來源：Anthropic 為 [Claude models overview](https://platform.claude.com/docs/en/models/overview)、[Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)、[Wikipedia: Claude](https://en.wikipedia.org/wiki/Claude_(AI))；OpenAI 為 [OpenAI pricing](https://developers.openai.com/api/docs/pricing)、[GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)、[GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)、[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)、[Wikipedia: GPT-6](https://en.wikipedia.org/wiki/GPT-6)；Google 為 [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)、[Gemini 3.8 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash)、[Gemini 3.1 Pro Preview](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview)、[Gemini API changelog](https://ai.google.dev/gemini-api/docs/changelog)、[Google 部落格，2026-09-30](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/)；Nova 為 [Nova 2 developer guide](https://docs.aws.amazon.com/nova/latest/nova2-userguide/what-is-nova-2.html) 與 [AA providers leaderboard](https://artificialanalysis.ai/leaderboards/providers)；Grok 為 [xAI models documentation](https://docs.x.ai/docs/models)；Muse Spark 與 Mistral 為 [OpenRouter 模型目錄](https://openrouter.ai/api/v1/models) 與 [AA models leaderboard](https://artificialanalysis.ai/leaderboards/models)；MAI 為 [Microsoft AI，2026-06-02](https://microsoft.ai/news/building-a-hillclimbing-machine-launching-seven-new-mai-models/)）

| 模型（狀態） | 發布日（C） | context | 最大輸出 | 輸入 / 快取讀取 / 輸出 | 等級（價格與 context） | 長 prompt 規則 |
|---|---|---|---|---|---|---|
| Anthropic Claude Fable 5.1（現行） | 2026-09-01 | 1M | 128K | $10 / $0.25 / $50 | B | 無加價，1M 全程標準價 |
| Anthropic Claude Mythos 5.1（limited availability，Project Glasswing） | 2026-09-01 | 1M | 128K | $10 / $0.25 / $50 | B | 無加價 |
| Anthropic Claude Opus 5.5（現行） | 2026-09-22 | 1M | 128K | $4 / $0.20 / $20 | B | 無加價 |
| Anthropic Claude Sonnet 5.5（現行） | 2026-09-28 | 1M | 128K | $2 / $0.20 / $10 | B | 無加價 |
| Anthropic Claude Haiku 4.5（現行；文件寫最早 2026-10-15 可退役） | 2025-10-15 | 200K | 64K | $1 / $0.10 / $5 | B | 不適用（200K） |
| OpenAI GPT-6 Astra（現行） | 2026-09-03 limited preview；2026-09-04 公開 | 1,050,000 | 128,000 | $10 / $1.00 / $50 | B | 超過 272K 輸入：整筆請求 $20 / $2.00 / $75 |
| OpenAI GPT-6.1 Sol（現行） | 2026-09-29 | 1,050,000 | 128,000 | $2 / $0.10 / $10 | B | 超過 272K：$4 / $0.20 / $15 |
| OpenAI GPT-6 Sol（現行） | 2026-09-22 | 1,050,000 | 128,000 | $2 / $0.20 / $10 | B | 超過 272K：$4 / $0.40 / $15 |
| OpenAI GPT-6 Luna（現行） | 2026-09-22 | 1,050,000 | 128,000 | $0.10 / $0.01 / $0.50 | B | 超過 272K：$0.20 / $0.02 / $0.75 |
| OpenAI GPT-5.6 Sol / Terra / Luna（現行） | 2026-07-09 | 1,050,000 | 128,000 | Sol $4 / $0.40 / $20；Terra $2 / $0.20 / $12；Luna $0.20 / $0.02 / $1.20 | B（Sol 價格有衝突） | 超過 272K：輸入與快取 2×、輸出 1.5× |
| OpenAI GPT-5.3-Codex（現行） | 2026-02-05 | 400K（AA） | 查無公開資料 | $1.75 / $0.175 / $14 | B（價格）；C（context） | 價格頁未列 |
| OpenAI GPT-5.3-Codex-Spark（research preview） | 2026-02-12 | 128K，僅文字（Cerebras） | 查無公開資料 | 無 API 定價 | C | – |
| Google Gemini 3.8 Flash（GA 2026-09-02） | 2026-09-02 | 1,048,576 輸入 | 65,536 | 至 2026-12-31 為 $0.75 / $0.075 / $3.75；2027-01-01 起 $1.50 / $0.15 / $7.50 | B | 無長度分級 |
| Google Gemini 3.5 Flash-Lite（現行） | 2026-07-21 | 1,048,576 | 65,536 | $0.30 / $0.03 / $2.50 | B | 無長度分級 |
| Google Gemini 3.1 Pro Preview（Preview） | 2026-02-19 | 1,048,576 輸入 | 65,536 | $2.00 / $0.20 / $12.00（≤ 200K） | B | 超過 200K：$4.00 / $0.40 / $18.00 |
| Google Gemini 4 Argon（已宣布未出貨：僅向受邀的資安防禦者推出，不在公開 API 清單） | 2026-09-30（宣布） | 輸入上限未載明 | 1M（宣布；原為 64K） | 導入價 $2 / 快取輸入便宜 95% / $10；之後 $4 / – / $20 | C | 查無公開資料 |
| Amazon Nova 2 Lite（現行） | 2025-12-02（OR 上架日；AA 為 2025-10-29） | 1M | 65,536 | $0.30 / 查無公開資料 / $2.50 | B（context、輸出）；C（價格） | 查無公開資料 |
| Amazon Nova 2 Pro（preview） | 2025-12-02（模型 ID 日期） | 256K（AA） | 查無公開資料 | $1.25 / $0.312（AA 單筆）/ $10 | C | 查無公開資料 |
| Amazon Nova Micro | 查無公開資料 | 128K–130K | 查無公開資料 | $0.035 / $0.00875 / $0.14 | C | 查無公開資料 |
| SpaceXAI Grok 4.7（現行） | 2026-09-21 | 500K | 450,000（OR） | $2.00 / $0.50 / $6.00 | B（輸入、輸出價）；C（其餘） | 所讀頁面未列 |
| Meta Muse Spark 1.3 | 2026-09-02 | 1,048,576 | 943,718（OR） | standard $1.25 / $0.15 / $4.25；contributor 層（資料留存）$0.10 / $0.002 / $0.20 | C | 查無公開資料 |
| Mistral Medium 3.5（AA 標示為 open weights） | 2026-04-29 至 04-30 | 256K | 209,715（OR） | $1.50 / $0.15 / $7.50 | C | 查無公開資料 |
| Microsoft MAI-Thinking-1（Foundry public preview） | 2026-06-02 宣布；2026-08-12 至 08-13 preview | 256K（二手來源） | 64K（二手來源） | 查無公開資料 | C | 查無公開資料 |

- 價格預告：Gemini 3.8 Flash 的價格在 2027-01-01 變為兩倍（輸入 $0.75 → $1.50，輸出 $3.75 → $7.50）（[Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)）。
- Gemini 4 Argon（2026-09-30 宣布）：導入價 $2 / $10，導入期後 $4 / $20；輸出上限由 64K 提高到 1M tokens；先向 Fairwind Program 的資安防禦者推出，之後擴及付費 API 客戶與 Google AI Ultra 訂戶（[Google 部落格，2026-09-30](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/)）。Long Decode Continuation（跨多次呼叫暫停再續寫長輸出的 API 功能）出自媒體報導（[Latent Space AINews，2026-10-01](https://www.latent.space/p/ainews-gemini-4-argon-gdms-answer)、[The Decoder，2026-10-01](https://the-decoder.com/google-gemini-4-argon-closes-the-gap-with-openai-and-anthropic-but-doesnt-take-a-clear-lead/)）；公開 API 日期、模型 ID、輸入上限與長 prompt 分級查無公開資料。
- Claude 預告：The Decoder（2026-09-22）稱 Sonnet 5.5 與 Haiku 5.5「數週內」推出；截至 2026-10-04，模型文件已列 Sonnet 5.5，沒有 Haiku 5.5（[The Decoder](https://the-decoder.com/claude-opus-5-5-matches-fable-5-1-at-40-percent-lower-cost-as-anthropic-promises-to-fix-claudish-writing/)、[Claude models overview](https://platform.claude.com/docs/en/models/overview)）。
- 價格衝突：GPT-5.6 Sol 在 OpenAI 價格頁為 $4 / $0.40 / $20，頁面另註記 GPT-5.6 Sol 的 "promotional pricing is available at least through November 21, 2026"（[OpenAI pricing](https://developers.openai.com/api/docs/pricing)；Fast mode 文件有同一句）；OpenRouter 的 OpenAI 端點列 $2 / $0.20 / $10，Azure 端點列 $4 / $0.40 / $20（[OpenRouter GPT-5.6 Sol](https://openrouter.ai/openai/gpt-5.6-sol)）。哪一個是現行價無法由來源判定，表 5-7 的 GPT-5.6 Sol 價格倍數以 OR 的列價計算，倍數不受影響，但 OpenAI Fast 文件寫的是 $8 / $40。
- 其他現行 Gemini 的列價：3.7 與 3.6 Flash $0.75 / $3.75；3.5 Flash $1.50 / $9.00；3.1 Flash-Lite $0.25 / $1.50（[Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)）。Muse Spark 與 Mistral 的價格取自第三方目錄，未讀廠商價格頁；Nova 的快取價格只有 Nova 2 Pro 的 AA 單筆資料。
- Tokenizer：Claude 4.7 以後的 tokenizer 對同一段文字約多產生 30% tokens（Anthropic 文件自述），所以跨廠商比較價格表時，同樣的文件在 Claude 上的 token 數較多（[Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)）。

**表 5-12 同一模型在不同雲端的 context window**（AA 記錄各端點測試時接受的上限，目錄欄位，等級 C；2026-10-04；「–」為 AA 沒有該端點；來源：[AA providers leaderboard](https://artificialanalysis.ai/leaderboards/providers)）

| 模型 | 第一方 API | Amazon Bedrock | Google Vertex AI | Microsoft Azure / Foundry |
|---|---|---|---|---|
| Claude Opus 5.5、Sonnet 5.5 | 1M | 1M | 1M | 未列 |
| Claude Haiku 4.5 | 200K | 200K | 200K | 200K |
| GPT-6 Astra | 1M | 524,288 | – | 524,288 |
| GPT-6 Luna | 1M | – | – | 524,288 |
| GPT-5.6 Sol、Terra | 1M | 1M | – | 524,288 |
| GPT-5.5 | 1,050,000 | 272,000 | – | 524,288 |
| Grok 4.3 | 1M | 524,288 | – | 200,000 |

- 衝突：OpenRouter 把 Bedrock 與 Azure 上 GPT-6 Astra、GPT-6.1 Sol、GPT-6 Luna 的每個端點都列為 1,050,000（[OpenRouter GPT-6 Astra](https://openrouter.ai/openai/gpt-6-astra)），與 AA 的 524,288 不符；若 AA 正確，第三方雲端的可用 context 約為第一方的一半。Anthropic 文件確認 Fable 5.1、Opus 5.5、Sonnet 5.5 在 Microsoft Foundry 與 Google Cloud 上都是 1M（[Claude in Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry)、[Claude on Vertex AI](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai)），AA 對 Azure 的 Opus 5.5 與 Sonnet 5.5 沒有列。
- OpenAI 模型在 Bedrock 上的區域：GPT-6 Sol 與 GPT-6 Luna 在 us-east-1（N. Virginia），GPT-6 Astra 在 us-west-2（Oregon），皆可由 Bedrock Runtime 與 Mantle 呼叫（[OpenAI on Amazon Bedrock](https://developers.openai.com/api/docs/guides/amazon-bedrock)）。
- 各雲端的價格：Claude 在 Bedrock 與 Google Cloud 的區域與多區域端點比全球端點貴 10%（[Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)）；OpenAI 對 2026-03-05 以後發布的模型，資料落地端點加價 10%（[OpenAI pricing](https://developers.openai.com/api/docs/pricing)）；OR 上的 GPT-6 Astra 在 Bedrock us-west-2 與 Azure eastus2 為 $11 / $55，與此一致。AA 目錄中 GPT-5.6 Terra 在 Bedrock 為 $2.75 / $16.5（快取 $0.28），比第一方的 $2 / $12 高 37.5%（D：2.75 ÷ 2）。Bedrock 另有 Priority tier +75%、Flex −50%（表 5-6）。

**長 prompt 的成本公式與算例**（D；價格取自表 5-11；只比較價格表，不比較同一份文件的成本）

OpenAI 的規則是整筆請求依輸入 token 數換檔：

```latex
C = \frac{m_{in}\left(N_{u} P_{in} + N_{c} P_{cache}\right) + m_{out} N_{out} P_{out}}{10^{6}}, \qquad \left(m_{in}, m_{out}\right) = \begin{cases} (1,\ 1) & N_{u} + N_{c} \le 272{,}000 \\ (2,\ 1.5) & N_{u} + N_{c} > 272{,}000 \end{cases}
```

其中 `N_u` 為未快取輸入 tokens，`N_c` 為快取讀取 tokens，`N_out` 為輸出 tokens，`P` 為表 5-11 的每 1M tokens 價格。Anthropic 的 `m_in` 與 `m_out` 恆為 1；Gemini Pro 的門檻為 200K，倍數相同（輸入 2×、輸出 1.5×）。

- 500K tokens 的 prompt、不快取、只算輸入：Claude Opus 5.5 為 0.5 × $4 = $2.00；GPT-6 Astra 為 0.5 × $20 = $10.00（整筆改用長 context 價）；GPT-6.1 Sol 為 0.5 × $4 = $2.00；Gemini 3.1 Pro Preview 為 0.5 × $4 = $2.00。
- 272K 的門檻：GPT-6 Astra 的 272,000 tokens 輸入為 272,000 × $10 ÷ 10^6 = $2.72，272,001 tokens 為 272,001 × $20 ÷ 10^6 = $5.44（約 2.0×）；Anthropic 沒有這個階梯。
- 300K tokens、95% 快取讀取（`N_c` = 285,000、`N_u` = 15,000）、輸出 2K tokens 的單一請求：

| 模型 | 算式（美元） | 單一請求成本 |
|---|---|---|
| Claude Opus 5.5 | 285,000 × 0.20 + 15,000 × 4 + 2,000 × 20，再 ÷ 10^6 | $0.157 |
| GPT-6.1 Sol（長 context 價） | 2 × (285,000 × 0.10 + 15,000 × 2) + 1.5 × 2,000 × 10，再 ÷ 10^6 | $0.147 |
| GPT-6.1 Sol（假設仍為短 context 價） | 285,000 × 0.10 + 15,000 × 2 + 2,000 × 10，再 ÷ 10^6 | $0.079（超過 272K 使整筆請求成本為 1.87×） |
| GPT-6 Astra（長 context 價） | 2 × (285,000 × 1 + 15,000 × 10) + 1.5 × 2,000 × 50，再 ÷ 10^6 | $1.02 |
| Gemini 3.1 Pro Preview（> 200K 價，不含快取儲存費） | 285,000 × 0.40 + 15,000 × 4 + 2,000 × 18，再 ÷ 10^6 | $0.210 |

## 網站呈現建議

本章適合做成 5 個互動元件加 1 組收合區，每個元件都只呈現每使用者速度與價格，因為表 5-1 的 23 筆晶片對應中沒有任何一筆附每晶片吞吐量；每個元件上方固定一行警語說明這一點。

- **晶片對應矩陣（表 5-1）**：列為私有模型、欄為晶片家族（Trainium、Inferentia、TPU、NVIDIA GPU、AMD GPU、Cerebras），儲存格放日期與「廠商聲明 / 媒體報導」徽章，沒有資料的格子標示「查無公開資料」，Inferentia 整欄為空。規模欄（GW、金額、晶片數）只顯示，不排序、不加總。
- **速度瀏覽器（表 5-2、表 5-4、表 5-5）**：可排序表格加水平 dot plot，x 軸為輸出 tokens/s，p5–p95 畫成線段，顏色代表雲端，可在 AA 與 OR 之間切換。TTFT 另用對數軸，因為同一張表同時有 0.56 s 與 705 s，預設隱藏 max effort 的列；AA 與 OR 方向相反的 OpenAI 端點，以及 OR 請求數 < 100 的列加標記。
- **層級散佈圖（表 5-6、表 5-7）**：x 軸為價格倍數、y 軸為實測 tokens/s 倍數，13 列有流量的 OR 層級畫成實心點，請求數 < 100 的 2 列加 † 並淡化。GPT-6 Astra Ultrafast（價格 6×、廠商稱最高 8×）沒有獨立量測，只用空心點與 C 徽章標示，不放進同一條趨勢線；y 軸可切換為 latency 縮短倍數，因為 OpenAI Fast 的效果在 TTFT 而不在速度。
- **同模型硬體比較（表 5-9）**：gpt-oss-120b 的 12 個端點用橫條圖畫 tokens/s（對數軸，Cerebras 1,781 到 Vertex 40），圖題直接寫「開源權重，僅作量級參考，AA 不揭露端點硬體」。私有模型的 4 列用「標準 → 變體」箭頭圖，不排名次，因為沒有任何一組是同一個私有模型在兩種晶片上的獨立量測。
- **價格與長 prompt 成本計算器（表 5-11、表 5-12 與公式）**：價格表預設依輸入價排序，狀態與讀取日期（2026-10-04）放在列首；計算器輸入 prompt tokens、快取比例與輸出 tokens，依公式換算，並在 272K（OpenAI）與 200K（Gemini Pro）畫出階梯。預設值取 300K、95% 快取、2K 輸出（Claude Opus 5.5 $0.157、GPT-6.1 Sol $0.147），Gemini 3.8 Flash（2027-01-01 起加倍）與 GPT-5.6 Sol（價格來源衝突）旁加警示。
- **收合或刪除**：表 5-3（prompt 長度與並行請求，24 列）與表 5-8 的 P90 欄放進「更多資料」抽屜；第 1 節表後的 7 條說明改為表 5-1 的註腳；MAI-Thinking-1 與 GPT-5.3-Codex-Spark 這類沒有 API 定價的列，只留在價格表的收合區。所有數字旁顯示 A / B / C / D 等級徽章與基準日 2026-10-04。
