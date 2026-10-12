# 第 11 章 估算依據與佐證

資料日：2026-10-04。本章逐項對照第 10 章模型（`calc/capacity_model.py`）的每個參數與公開證據。等級：**A** = 獨立量測或公開資料集（「A，筆記實算」= 研究筆記由公開 trace 自行算出的統計量，資料是 A 級，統計量的選法是筆記的）；**B** = 廠商文件或揭露方法的廠商統計；**C** = 廠商或媒體宣稱、未揭露方法；**D** = 本文或筆記的推算（附算式）。

## 佐證總表

佐證總表共 94 列：33 列直接採用量測或文件值，16 列在量測範圍內取值，14 列由廠商宣稱或金額換算，28 列是判斷值、內插、借用值、校準值或情境設定，另 3 列由其他列算出。判斷值在 R&D 占 14 列中的 9 列、OA 占 17 列中的 6 列、coding 占 17 列中的 2 列；佐證最弱的是 R&D 的全部用量、OA 的 cache read 占比與 high 用量級、三個角色的 TTFT、使用率上限，以及 warm KV 的兩個係數。

最後一欄開頭的標記是模型值的性質：**量測值 / 文件值** = 直接採用量測或文件上的數字；**範圍內取值** = 在量測範圍內選一點；**換算值 / 宣稱值** = 由廠商宣稱或金額換算；**判斷值 / 內插 / 借用值 / 校準值 / 情境設定** = 沒有直接量測，取自類比、另一個對象的量測或本文的設定。low、base、high 是三種「全體平均」的情境，不是使用者的百分位。

### OA 角色

| 參數 | 模型採用值 | 公開證據的數值或範圍 | 來源 | 等級 | 採用理由或落差 |
|---|---|---|---|---|---|
| a，low | 12% | 美國全體受雇者每日使用 AI 8%（2025-06）；早期 M365 Copilot 每週使用略低於 40%，5% 每週都用、20% 從未使用（2023-09 至 2024-10） | [Gallup](https://www.gallup.com/workplace/691643/work-nearly-doubled-two-years.aspx)、[Dillon et al.](https://arxiv.org/abs/2504.11436) | A | **範圍內取值。** 8% 的母體是全體員工而非授權席次，40% 是每週而非每日；12% 本身沒有被量到。 |
| a，base | 35% | 英國政府 20,000 席試驗（2024-09-30 至 12-31）：問卷 39% 一日多次使用、34% 每日在 Teams 使用，30 日活躍約 80%；ChatGPT 的 DAU ÷ WAU 為 37%（2025-03） | [GOV.UK findings report](https://www.gov.uk/government/publications/microsoft-365-copilot-experiment-cross-government-findings-report/microsoft-365-copilot-experiment-cross-government-findings-report-html)、[Epoch AI usage-reports CSV](https://epoch.ai/data/ai_companies_usage_reports.csv) | A；C | **範圍內取值。** 34–39% 是問卷回覆者（n = 7,115）的自述；筆記折成授權席次約 31%（39% × 80%）[D]。 |
| a，high | 50% | JPMorgan LLM Suite：250,000 人可用，「about half use it daily」（2025-10-07） | [CeFPro Connect](https://connect.cefpro.com/article/view/inside-jpmorgan-llm-suite-as-ai-agents-spread-across-the-bank) | C | **宣稱值。** 主管口述的整數，沒有遙測。 |
| r，low | 4 | ChatGPT 每位 WAU 每日 3.7 則訊息（18B 則 / 週 ÷ 700M 人，2025-07）；Gemini 每位 DAU 4.0 則（2025-03）；Panasonic Connect 每位月活躍者每工作日 2.05 次（FY2025） | [OpenAI/NBER "How People Use ChatGPT"](https://cdn.openai.com/pdf/a253471f-8260-40c6-a2cc-aa93fe9f142e/economic-research-chatgpt-usage-paper.pdf)、[Epoch AI usage-reports CSV](https://epoch.ai/data/ai_companies_usage_reports.csv)、[Panasonic Newsroom Japan](https://news.panasonic.com/jp/press/jn260729-1) | B；C；B（皆經換算） | **範圍內取值。** ChatGPT 的數字只含消費者方案；一則訊息當作一次模型呼叫。 |
| r，base | 10 | ChatGPT 每位 DAU 7.5 則（1.2B ÷ 160M，2025-03 的估計）；ChatGPT Enterprise 平均每位員工訊息量年增 30%（2025-12） | [Epoch AI usage-reports CSV](https://epoch.ai/data/ai_companies_usage_reports.csv)、[OpenAI, The state of enterprise AI 2025](https://cdn.openai.com/pdf/7ef17d82-96bf-4dd1-9df2-228f7f377a29/the-state-of-enterprise-ai_2025-report.pdf) | C；B | **換算值。** 7.5 × 1.3 = 9.75；7.5 是對消費者的第三方估計，企業版的絕對訊息數查無公開資料。 |
| r，high | 30 | 筆記範圍表的 High 為 60（P95 員工訊息量是中位數的 6 倍）；Moderna 每位使用者每週 120 個對話，即每工作日 24 個 | [OpenAI, The state of enterprise AI 2025](https://cdn.openai.com/pdf/7ef17d82-96bf-4dd1-9df2-228f7f377a29/the-state-of-enterprise-ai_2025-report.pdf)、[OpenAI customer story: Moderna](https://openai.com/index/moderna/) | B；C | **判斷值。** 60 描述 P95 使用者，不能當全體平均；30 是 base 的 3 倍，與 Moderna 的對話數同量級。 |
| 輸入合計 u + c，low | 1,000 | Azure conversation trace（2024-05，27.3M 次請求）：輸入中位 928、平均 1,632 tokens | [AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md) | A | **量測值。** trace 來自 2024 年，受 8K context 的模型限制。 |
| 輸入合計 u + c，base | 3,500 | OpenRouter（至 2025-11）：每請求 prompt 平均由約 1.5K 升到 6K 以上，程式類請求常超過 20K、占 token 量 50% 以上 | [OpenRouter/a16z State of AI](https://openrouter.ai/state-of-ai) | B | **換算值。** 非程式類 ≈ (6K − 0.15 × 20K) ÷ 0.85 ≈ 3.5K [D]；來源是 API 聚合平台，不是企業 chat。 |
| 輸入合計 u + c，high | 12,000 | 筆記範圍表的 High 為 30,000（10–20 頁 PDF，每頁 1,500–3,000 tokens）；agent 的 token 約為 chat 的 4 倍、multi-agent 約 15 倍（2025-06-13） | [Claude PDF support docs](https://platform.claude.com/docs/en/build-with-claude/pdf-support)、[Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | B；C | **判斷值。** 30 次 × 每次 12.8K = 每活躍日 384K，是 base 的 9.8 倍，落在 4–15 倍之間；每次呼叫的大小沒有量測。 |
| cache read 占輸入，low | 10%（c = 100） | 輸入不重複的工作流程 cache 命中低於 20%（2026-04） | [Ramp: AI token cost for businesses](https://ramp.com/blog/ai-token-cost-for-businesses) | B | **範圍內取值。** 取 0–20% 的中點。 |
| cache read 占輸入，base | 50%（u = c = 1,750） | 重複使用 context 的工作流程 80% 以上、不重複者低於 20%（2026-04）；Copilot agent 在 turn 邊界 55% cached（2026-06） | [Ramp: AI token cost for businesses](https://ramp.com/blog/ai-token-cost-for-businesses)、[Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101) | B；A | **判斷值。** 企業 chat 的 cache read 占比查無公開量測。純 OA 時改取 0% 或 80%，未快取輸入 TPM 是 2.0 倍或 0.4 倍；組合 B 只差 ±5% [D]。 |
| cache read 占輸入，high | 75%（u = 3,000、c = 9,000） | 同上：重複使用 context 的工作流程 80% 以上 | [Ramp: AI token cost for businesses](https://ramp.com/blog/ai-token-cost-for-businesses) | B | **判斷值。** office agent 的 cache 占比查無公開量測。 |
| o，low | 125 | Azure conversation 輸出平均 105.5（2024-05）與 211（2023-11）tokens | [AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md)、[AzureLLMInferenceDataset2023](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2023.md) | A | **範圍內取值。** |
| o，base | 400 | OpenRouter completion 平均約 400（含 reasoning，至 2025-11）；WildChat 每 turn 441（2023–2024） | [OpenRouter/a16z State of AI](https://openrouter.ai/state-of-ai)、[WildChat](https://arxiv.org/abs/2405.01470) | B；A | **量測值。** reasoning 占 chat 輸出的絕對比例查無公開資料。 |
| o，high | 800 | 筆記範圍表的 High 為 1,750（以 TraceLab Claude 每步輸出的 P90 1,671 代理）；Claude 的工作對話 31–34% 開啟 extended thinking（2026-06） | [TraceLab](https://arxiv.org/abs/2606.30560)、[Anthropic Economic Index: Cadences](https://www.anthropic.com/research/economic-index-june-2026-report) | A；B | **判斷值。** 取 base 的 2 倍；P90 不能當全體平均。 |
| 週末係數 w | 0.45 | 週末日 ÷ 平日：BurstGPT 三個檔 0.52、0.36、0.52（2023–2024）；Azure conversation 0.57（2024-05） | [BurstGPT](https://github.com/HPMLL/BurstGPT)、[AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md) | A，筆記實算 | **範圍內取值。** 來源是區域性服務與全球混合的 trace；帶時間戳的企業 chat trace 查無公開資料。 |
| TTFT | 1.0 s | 無直接量測。旁證：OpenRouter 實際流量的 latency p50 為 Sonnet 5.5 1.09–2.14 s、Opus 5.5 3.72–4.64 s（2026-10-04）；呼叫時間 W = 1.0 + 400 ÷ 80 = 6.0 s，BurstGPT 的請求時間平均 7.0 s、中位 3 s | [OpenRouter Claude Sonnet 5.5](https://openrouter.ai/anthropic/claude-sonnet-5.5)、[OpenRouter Claude Opus 5.5](https://openrouter.ai/anthropic/claude-opus-5.5)、[BurstGPT](https://github.com/HPMLL/BurstGPT) | A（旁證） | **判斷值。** 走 frontier API 時偏低（Sonnet 5.5 的 p50 已是 1.1–2.1 s）；BurstGPT 是 GPT-3.5 與 GPT-4 年代的服務。 |

### Coding 角色

| 參數 | 模型採用值 | 公開證據的數值或範圍 | 來源 | 等級 | 採用理由或落差 |
|---|---|---|---|---|---|
| a，low | 30% | 查無公開資料 | 用量筆記的範圍表 | D | **判斷值。** 筆記標明這是對 late-majority 團隊的假設，沒有來源。 |
| a，base | 45% | 2026-04 的 pulse survey（約 1,100 人）：每日使用 agent 的開發者 40%、軟體業 44%、fintech 55%；2025 年調查近半數每日使用 AI 工具 | [Stack Overflow pulse survey](https://stackoverflow.blog/2026/05/27/agents-on-a-leash-agentic-ai-remains-mostly-monitored-at-work/)、[Stack Overflow blog](https://stackoverflow.blog/2026/09/30/getting-ready-for-2026-results-a-look-back-on-developer-survey-findings) | A | **範圍內取值。** 母體是自願作答的開發者，不是授權席次。 |
| a，high | 75% | Claude Code 文件：每活躍日約 $13、每月 $150–250，隱含每月 11.5–19 個活躍日，即 22 個工作日的 52–87%；Pegatron 單一開發者 28 天中 22 天活躍 | [Claude Code docs: Manage costs effectively](https://code.claude.com/docs/en/costs)、[Inference Economics of Enterprise Coding Agents](https://arxiv.org/abs/2607.13080) | C；A（n = 1） | **換算值。** 筆記範圍 70–85%，取中段。 |
| r，low | 20 | Copilot agent 的中位使用者每週 11 個 turn × 每 turn 4.5–6.6 次呼叫 = 50–73 次（2026-06 第一週） | [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101) | A | **換算值。** 假設一週約 3 個活躍日（50–73 ÷ 3 = 17–24）[D]。 |
| r，base | 170 | 每活躍日 13–23M tokens ÷ 每次呼叫 88–154K = 85–260 次；Claude Code 建議表 500 人以上列的 0.25–0.35 RPM × 8 小時 = 120–168 次 | [Claude Code docs: Manage costs effectively](https://code.claude.com/docs/en/costs) | C | **換算值。** $13 換成 token 所用的實付單價是 $0.573–1.00/M（1.7 倍的範圍）；Anthropic 未揭露 $13 的方法、樣本與模型組合。 |
| r，high | 400 | 同一文件「90% 的使用者低於每活躍日 $30」→ 30–52M tokens，÷ 每次呼叫 129.2K = 232–402 次；筆記範圍表的 High 為 1,450（Pegatron 的無人值守 agent） | [Claude Code docs: Manage costs effectively](https://code.claude.com/docs/en/costs)、[Inference Economics of Enterprise Coding Agents](https://arxiv.org/abs/2607.13080) | C；A（n = 1） | **換算值。** 取上緣，每活躍日 51.7M；1,450 是單一極端使用者，不當全體平均。 |
| u，low | 5,000 | Copilot 每次呼叫：prompt 中位 68K，其中 cached 中位 63K（2026-06） | [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101) | A | **量測值。** 兩個中位數相減。筆記範圍表的 Low 是 0.9K（TraceLab append 中位 875），模型沒有採用。 |
| u，base | 6,500 | 每次呼叫的未快取輸入：Pegatron 3.4K；Copilot 每 turn 平均 ÷ 6.6 = 5.6K；TraceLab append 平均 6.6K；Copilot 公開樣本平均 9.7K | [Inference Economics of Enterprise Coding Agents](https://arxiv.org/abs/2607.13080)、[Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101)、[TraceLab](https://arxiv.org/abs/2606.30560)、[Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) | A | **範圍內取值。** 低於 Copilot 公開樣本的 9.7K；改用 9.7K 時，組合 B 的未快取輸入 TPM 是 1.36 倍（24.5M → 33.2M）[D]。 |
| u，high | 8,500 | 同上的 3.4–9.7K；turn 的第一次呼叫或閒置超過 10 分鐘後 cache miss 時可到 20K 以上 | 同上 | A | **範圍內取值。** |
| c，low | 63,000 | Copilot 每次呼叫 cached prompt 中位 63K（2026-06） | [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101) | A | **量測值。** 筆記範圍表的 Low 是 20K（OpenRouter 的程式類請求），模型沒有採用。 |
| c，base | 85,000 | Copilot 每 turn cached 平均 545.3K ÷ 6.6 次呼叫 = 82.6K；TraceLab prefix 中位 119K；Ant 平台每請求輸入中位 70K（論文 2026-09-28） | [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101)、[TraceLab](https://arxiv.org/abs/2606.30560)、[Understanding Agent Serving at Production Scale](https://arxiv.org/abs/2609.34432) | A | **範圍內取值。** |
| c，high | 120,000 | TraceLab：prefix 中位 119K，Claude 的 P50 126K、P90 467K（2025-09 至 2026-06） | [TraceLab](https://arxiv.org/abs/2606.30560) | A | **量測值。** 筆記範圍表的 High 是 477K（Pegatron 的平均），屬單一使用者。 |
| o，low | 250 | 每次呼叫輸出的中位數：Copilot 247（不含 reasoning）；TraceLab 214，其中 Claude 252（含 reasoning） | [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101)、[TraceLab](https://arxiv.org/abs/2606.30560) | A | **量測值。** |
| o，base | 600 | 每次呼叫輸出的平均：Copilot 528–606（不含 reasoning）；TraceLab 523；Pegatron 632（含 reasoning） | [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md)、[TraceLab](https://arxiv.org/abs/2606.30560)、[Inference Economics of Enterprise Coding Agents](https://arxiv.org/abs/2607.13080) | A | **量測值。** |
| o，high | 700 | TraceLab Claude 每步輸出平均 690（P90 1,671、P99 6,571） | [TraceLab](https://arxiv.org/abs/2606.30560) | A | **量測值。** 筆記範圍表的 High（1,700–6,600）是 P90–P99。 |
| 週末係數 w | 0.25 | 週末日 ÷ 平日：Copilot agent 0.21（呼叫）、0.22（token）、0.27（輸出）；Azure code completion 0.32（請求）、0.28（token） | [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md)、[AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md) | A，筆記實算 | **範圍內取值。** |
| TTFT | 2.0 s | 無直接量測。旁證：OpenRouter 的 latency p50 為 Opus 5.5 3.72–4.64 s、Sonnet 5.5 1.09–2.14 s（2026-10-04）；自建操作點的 TTFT 中位 1.15 s（Kimi K3）、2.33 s（GLM-5.2）、2.94 s（V4-Pro）；W = 2.0 + 600 ÷ 80 = 9.5 s，Copilot 每次呼叫時間平均 11.9 s、中位 5.3 s、P90 18.6 s | [OpenRouter Claude Opus 5.5](https://openrouter.ai/anthropic/claude-opus-5.5)、[InferenceX API, model=Kimi-K3, pulled 4 Oct 2026](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Kimi-K3)、[Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) | A（旁證） | **判斷值。** MX1 有 54% 的 coding 呼叫送 Opus 5.5，2.0 s 偏低（OpenRouter 的 latency 由筆記視為 TTFT，定義未逐字確認）；W 比 Copilot 的平均短 20%，W 改為 11.9 s 時組合 B 的在途數是 1.12 倍 [D]。 |

- 筆記範圍表的 Low 欄不能逐項相乘：20 次 × (20K + 0.9K + 0.23K) = 每活躍日 0.42M，低於筆記自己由 Copilot 中位使用者得出的 1.1M（每週 3.2M ÷ 3 日）。模型的 low 改用 Copilot 的中位呼叫，得 1.36M [D]。

### R&D 角色

沒有任何公開的每位研究人員遙測；r、u、c、o 由「文件請求」與「deep research run」兩種元件合成，下表列的是元件（low / base / high）。

| 參數 | 模型採用值 | 公開證據的數值或範圍 | 來源 | 等級 | 採用理由或落差 |
|---|---|---|---|---|---|
| a，low | 28% | 學術研究者每日使用 agent 28%（2026-04 的 pulse survey） | [Stack Overflow pulse survey](https://stackoverflow.blog/2026/05/27/agents-on-a-leash-agentic-ai-remains-mostly-monitored-at-work/) | A | **量測值。** 問卷母體是學術研究者，不是企業研發人員。 |
| a，base、high | 40% / 55% | 同一調查：開發者 40%、fintech 55% | [Stack Overflow pulse survey](https://stackoverflow.blog/2026/05/27/agents-on-a-leash-agentic-ai-remains-mostly-monitored-at-work/) | D | **判斷值。** 類比開發者與 fintech；研發組織的席次遙測查無公開資料。 |
| 文件請求數 / 活躍日 | 10 / 20 / 60 | OA 的 base（10）到 OA 的 P95（60）；frontier 資料分析師使用資料分析工具的量是中位數的 16 倍（2025-12） | [OpenAI, The state of enterprise AI 2025](https://cdn.openai.com/pdf/7ef17d82-96bf-4dd1-9df2-228f7f377a29/the-state-of-enterprise-ai_2025-report.pdf) | B（類比） | **判斷值。** |
| deep research run 數 / 活躍日 | 0.2 / 1 / 3（Max） | 方案額度：ChatGPT Deep Research 每月 25 次（Plus、Team、Enterprise、Edu）、Pro 250 次（2025-04） | [Wikipedia: ChatGPT Deep Research](https://en.wikipedia.org/wiki/ChatGPT_Deep_Research) | B（三手來源） | **判斷值。** 額度不是用量；base 的每日 1 次約等於把每月 25 次用滿 [D]。每位使用者實際的 run 數查無公開資料，2026 年的額度未對照原廠頁面。 |
| 每 run 的模型呼叫數 | 80（標準）/ 160（Max） | 標準 run 約 80 次搜尋，Max 最多約 160 次（文件更新 2026-09-23） | [Gemini Deep Research agent docs](https://ai.google.dev/gemini-api/docs/deep-research) | C | **判斷值。** 假設每次搜尋對應一次模型呼叫（coding agent 量到的 LLM 呼叫與 tool 呼叫約 1 : 1）。 |
| 每 run 的輸入 | 250K、60% cached（標準）；900K、65% cached（Max） | 標準約 250K 輸入、Max 約 900K，皆約 50–70% cached | [Gemini Deep Research agent docs](https://ai.google.dev/gemini-api/docs/deep-research) | C | **宣稱值。** 只有 Google 公布估計；OpenAI 與 Anthropic 產品的每 run token 查無公開資料。 |
| 每 run 的輸出 | 60K（標準）/ 80K（Max） | 約 60K 與約 80K；研究時間最長 60 分鐘，多數 20 分鐘內完成 | [Gemini Deep Research agent docs](https://ai.google.dev/gemini-api/docs/deep-research) | C | **宣稱值。** 模型把輸出平均攤到每次呼叫（標準 run 每次 750 tokens），一次 run 的在途時間 = 80 × (2.5 + 750 ÷ 80) s ≈ 15.8 分鐘 [D]，與「20 分鐘內」相容。 |
| 文件請求的輸入 | 6K / 15K / 40K | PDF 每頁 1,500–3,000 tokens，相當於 2–4、5–10、13–27 頁 | [Claude PDF support docs](https://platform.claude.com/docs/en/build-with-claude/pdf-support) | B | **判斷值。** 每次請求帶幾頁沒有量測。 |
| 文件請求的 cache read 占輸入 | 20% / 50% / 80% | 輸入不重複的工作流程低於 20%、重複使用 context 者 80% 以上（2026-04） | [Ramp: AI token cost for businesses](https://ramp.com/blog/ai-token-cost-for-businesses) | B | **判斷值。** |
| 文件請求的輸出 | 400 / 600 / 1,500 | chat 的輸出約 400（OpenRouter）；TraceLab Claude 每步輸出 P90 1,671 | [OpenRouter/a16z State of AI](https://openrouter.ai/state-of-ai)、[TraceLab](https://arxiv.org/abs/2606.30560) | B；A | **判斷值。** |
| 合成後的 r | 26 / 100 / 540 | 筆記範圍表：約 30 / 約 100 / 約 540 次，每活躍日 0.12M / 0.62M / 5.4M tokens | 用量筆記 | D | **推算。** 10 + 0.2 × 80；20 + 1 × 80；60 + 3 × 160。筆記把 26 寫成約 30。 |
| 合成後的 u；c；o | u 2,615 / 2,500 / 2,640；c 1,615 / 3,000 / 6,805；o 615 / 720 / 611 | 同上 | 用量筆記 | D | **推算。** 算式見下；例：base 的 u = (20 × 7,500 + 1 × 100,000) ÷ 100 = 2,500。 |
| 週末係數 w | 0.35 | chat trace 0.36–0.57、coding trace 0.21–0.32；Copilot 的 deep-loop 使用者（9.2%）週末較活躍 | [BurstGPT](https://github.com/HPMLL/BurstGPT)、[Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101) | A（類比） | **判斷值。** 取兩類 trace 之間。 |
| TTFT | 2.5 s | 查無可對照的量測 | 無 | D | **判斷值。** W = 2.5 + 720 ÷ 80 = 11.5 s。 |

每次呼叫的 u（c、o 同理；q 是每 run 的呼叫數）：

```latex
u = \frac{n_{\mathrm{doc}} \cdot u_{\mathrm{doc}} + n_{\mathrm{run}} \cdot u_{\mathrm{run}}}{n_{\mathrm{doc}} + n_{\mathrm{run}} \cdot q}
```

### 尖峰形狀

| 參數 | 模型採用值 | 公開證據的數值或範圍 | 來源 | 等級 | 採用理由或落差 |
|---|---|---|---|---|---|
| busy-hour 占比 s，單一時區 | 0.11 | 平日最忙一小時占全日請求：BurstGPT（一個超過 3,000 位使用者的區域服務，2023–2024）三個檔平均 10.6%、12.4%、11.6%（p10–p90 9.0–14.1%）；Azure code completion 8.9–9.7%（平均 9.3%，2024-05） | [BurstGPT](https://github.com/HPMLL/BurstGPT)、[AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md) | A，筆記實算 | **範圍內取值。** 筆記建議 10–12.5%；兩個 trace 都早於 agent。 |
| busy-hour 占比 s，全球分散 | 0.065 | Azure conversation 5.2–5.8%（平均 5.6%，2024-05）；Copilot agent 6.8–7.0%（2026-06） | [AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md)、[Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) | A，筆記實算 | **範圍內取值。** 筆記建議 5.5–7.5%。自洽檢查：24 × 0.065 × 1.15 × 1.04 = 1.87，Copilot 公開樣本（每日約 60,360 個 session）全部 token 的尖峰分鐘 ÷ 當日平均分鐘量到 1.8–1.9 [D]。 |
| P95 平日係數 d | 1.2 | P95 平日 ÷ 平均平日：BurstGPT 三個檔 1.20、1.28、1.80（60–110 天） | [BurstGPT](https://github.com/HPMLL/BurstGPT) | A，筆記實算 | **範圍內取值（下緣）。** 取三個值中最低者；改取 1.28 或 1.80，RPM 與 TPM 是 1.07 倍或 1.50 倍 [D]。只有一個站點有多週資料，月底、release、假期等季節性沒有任何 trace 涵蓋。 |
| 尖峰分鐘係數 k 的公式 | 1 + 3 ÷ √m（m = 41 時 1.47；m = 183 時 1.22） | 兩個校準點：m ≈ 4.1 時量到中位 2.4–2.5（p90 3.0–3.1、最大 3.2–4.3），公式 2.5；m ≈ 1,300 時量到 1.09–1.12，公式 1.08 | [BurstGPT](https://github.com/HPMLL/BurstGPT)、[Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) | A，筆記實算；公式 D | **內插。** m 在 5 到 1,000 之間沒有量測；公式是 Poisson 計數的平均加 3 個標準差，實際到達的變異係數大於 1。 |
| k 的下限 | 1.15（m ≥ 400 時生效） | 尖峰分鐘 ÷ busy hour 平均分鐘：Azure code 中位 1.15、最大 1.30；Azure conversation 1.12、1.19；Copilot agent 1.09、1.12 | [AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md)、[Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) | A，筆記實算 | **範圍內取值。** 等於 Azure code 的中位數；筆記建議每分鐘 1,000 個請求以上取 1.1–1.3，取 1.30 時尖峰是 1.13 倍 [D]。 |
| f_u（未快取輸入） | 1.18 | Copilot busy hour 內的尖峰分鐘 ÷ 平均分鐘：未快取輸入 1.29（最大 1.32）、呼叫數 1.09 | [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) | A，筆記實算 | **量測值（單一 trace）。** 1.29 ÷ 1.09；疊在 k = 1.15 上是 1.36，高於量到的 1.29–1.32。套用到 OA 與 R&D 沒有佐證。 |
| f_c（cache read） | 1.04 | 同一 trace：全部 token 1.13 ÷ 呼叫數 1.09 | [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) | A，筆記實算 | **量測值（單一 trace）。** 以全部 token 代表 cache read。chat 類 trace 的 token ÷ 請求是 1.02–1.03（Azure code 1.18 ÷ 1.15、conversation 1.14 ÷ 1.12）。 |
| f_o（輸出） | 1.06 | 同一 trace：輸出 1.15 ÷ 呼叫數 1.09 | [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) | A，筆記實算 | **量測值（單一 trace）。** |
| 每月週數 | 52.14 ÷ 12 = 4.345 | 曆法換算；筆記用 4.33 | 無 | D | **推算。** 相差 0.3%。 |

### 併發

| 參數 | 模型採用值 | 公開證據的數值或範圍 | 來源 | 等級 | 採用理由或落差 |
|---|---|---|---|---|---|
| 呼叫時間 W | TTFT + o ÷ v | 「TTLT = TTFT + (TBT × Tokens Generated)」；prompt token 增加的時間遠小於生成 token | [Azure OpenAI performance and latency](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/latency) | B | **文件值。** agent 的工具執行時間不計入，因為工具在兩次呼叫之間執行。 |
| 同時在途數 L | λ × W（Little's law） | Copilot agent 整週：量到 179.5，λW = 15.38/s × 11.88 s = 182.7（差 1.8%）；最忙的八個小時為 λW 的 1.00–1.12 倍；BurstGPT 110 天：0.1721 對 0.1721 | [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md)、[BurstGPT](https://github.com/HPMLL/BurstGPT)、[Little's law](https://en.wikipedia.org/wiki/Little%27s_law) | A，筆記實算 | **量測值。** 單一小時不是穩態，長呼叫會跨小時，誤差到 12%。 |
| 每條串流的速度 v | 80 tokens/s | OpenRouter 的實際流量（2026-10-04；30 分鐘視窗）：Opus 5.5 的 throughput p50 71 tokens/s（Anthropic 與 Bedrock 端點）、Sonnet 5.5 p50 92（Anthropic）與 120（Bedrock）；Artificial Analysis（10K prompt；72 小時中位）：Opus 5.5 72–92、Sonnet 5.5 92–132；Azure PTU 的延遲目標為各模型 25–100 TPS（頁面更新 2026-09-24） | [OpenRouter Claude Opus 5.5](https://openrouter.ai/anthropic/claude-opus-5.5)、[OpenRouter Claude Sonnet 5.5](https://openrouter.ai/anthropic/claude-sonnet-5.5)、[AA providers leaderboard](https://artificialanalysis.ai/leaderboards/providers)、[PTU sizing](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing) | A；A；B | **範圍內取值。** 介於 Opus 5.5 的 71 與 Sonnet 5.5 的 92–120 之間。用於矩陣的全部流量與模型組合中的 API 池；自建池改用操作點的每使用者速度（37–101 tokens/s）。 |
| 99.9% 的分位係數 z | 3.1（L + 3.1√L） | Copilot 平日最忙小時（平均在途 328–398）：p99.9 ÷ 平均 1.12–1.20，Poisson 1.16–1.18；週末（72、85）：1.40、1.36 對 1.38、1.35 | [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) | A，筆記實算 | **量測值（大流量）。** 公式是常態近似，L 小時略低於精確 Poisson（L = 1 時 4.1 對 5.0 倍；L = 10 時 1.98 對 2.1 倍）[D]。平均在途低於 1 時不成立：BurstGPT 的 p99.9 為 10–13，Poisson 為 4。 |
| 使用率上限 | 0.80 | fleet 模擬採用的上限 ρ ≤ 0.85（2026-03）；超過 10,000 顆 GPU 的 agent 平台白天 GPU 使用率 74.8%（2026-09）；LiteLLM 的飽和門檻預設 0.80；AWS 建議把告警設在配額的 80% | [inference-fleet-sim](https://arxiv.org/abs/2603.16054)、[Understanding Agent Serving at Production Scale](https://arxiv.org/abs/2609.34432)、[LiteLLM dynamic rate limiter v3 README](https://github.com/BerriAI/litellm/blob/main/litellm/proxy/hooks/README.dynamic_rate_limiter_v3.md)、[AWS ML blog](https://aws.amazon.com/blogs/machine-learning/optimize-your-applications-for-scale-and-reliability-on-amazon-bedrock/) | A；A；B；B | **判斷值。** 四個數字量的是不同的東西（排隊模型的上限、GPU 使用率、gateway 與配額的告警門檻），都不是「操作點吞吐量的可用比例」；廠商公布的目標使用率查無公開資料。 |
| warm session ÷ 平均在途呼叫 | 16 | Copilot agent：最忙小時的平均在途呼叫是該小時活躍 session 的 5.3–7.4%（五個平日），倒數為 13.5–18.9 | [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) | A，筆記實算 | **量測值（只有 coding agent）。** 套用到 OA 與 R&D 沒有佐證；BurstGPT 的對話 turn 間隔中位 131 s、p90 2,340 s。 |
| 常駐 context 係數 | 1.2 × 每次呼叫的平均 context | 每個 session 常駐 HBM 的 KV：DeepSeek V4-Pro 43M ÷ 384 ≈ 112K tokens（8 顆 B300）、22M ÷ 196 ≈ 112K（8 顆 B200）；GLM-5.2 14.1M ÷ 128 ≈ 110K（llm-d） | [InferenceX blog, 25 Aug 2026](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-b200-vs-b300-kv-working-set)、[llm-d blog, 22 Jul 2026](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d) | A；B（皆經換算） | **校準值。** 以 coding base 的 92.1K × 1.2 ≈ 110K 回推，只有一個校準點，不是獨立量測；AgentX 重播的 trace 輸入 p50 為 88K、p90 為 272K。 |

### 平台計量

U、C、O 是尖峰分鐘的未快取輸入、cache read、輸出 tokens；換算式本身是 D，係數是 B 級的文件值。

| 參數 | 模型採用值 | 公開證據的數值或範圍 | 來源 | 等級 | 採用理由或落差 |
|---|---|---|---|---|---|
| Anthropic ITPM | U | 「only uncached input tokens count toward your ITPM rate limits」：`input_tokens` 與 `cache_creation_input_tokens` 計入，`cache_read_input_tokens` 不計（Haiku 3.5 例外） | [Anthropic rate limits](https://platform.claude.com/docs/en/api/rate-limits) | B | **文件值。** 模型的 u 已含 cache write。 |
| Anthropic OTPM | O | OTPM 是獨立的 bucket；`max_tokens` 不計入 | [Anthropic rate limits](https://platform.claude.com/docs/en/api/rate-limits) | B | **文件值。** |
| Anthropic 對照用的配額 | Scale tier：10,000 RPM、10M ITPM、2M OTPM | Start 1,000 / 2M / 0.4M；Build 5,000 / 5M / 1M；Scale 10,000 / 10M / 2M；每個模型類別分開計 | [Anthropic rate limits](https://platform.claude.com/docs/en/api/rate-limits) | B | **文件值。** |
| Bedrock runtime TPM（Claude） | U + b × O；b = 5、10、15 | 輸入 + cache write + 輸出 × burndown，cache read 不計；Claude 4.8 為 15×，Opus 5.5、Sonnet 5、Opus 5、Fable 5.1 為 10×，4.7 以下為 5× | [How tokens are counted in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html) | B | **文件值。** 入場時先扣「輸入 + `max_tokens`」的預扣量，模型沒有計。 |
| Sonnet 5.5 的 burndown | 5× | AWS 的文字沒有點名 Sonnet 5.5（Sonnet 5 為 10×） | [How tokens are counted in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html) | B（缺值） | **判斷值。** 取兩個可能值中較低者；若為 10×，第 10 章 Sonnet 池對預設配額的倍數由 3.35 升到 4.69。 |
| Bedrock runtime TPM（open-weight） | U + O | 「For all other models, the burndown rate is 1:1」；Kimi K3 是 Bedrock 上第一個支援 explicit prompt caching 的 open-weight 模型，cache 命中不計入 input TPM 配額（GA 2026-09-18） | [How tokens are counted in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html)、[AWS What's New: Kimi K3 on Amazon Bedrock](https://aws.amazon.com/about-aws/whats-new/2026/09/moonshot-ai-kimi-k3-on-amazon-bedrock/)、[AWS ML blog: Introducing Kimi K3 on Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/introducing-kimi-k3-on-amazon-bedrock/) | B | **文件值，只對 Kimi K3 成立。** 依 AWS 的說法，其他 open-weight 模型尚無 explicit prompt caching；沒有快取時模型的 c 要當一般輸入計入，計量變成 U + C + O（第 10 章的例子是 U + O 的 8.7 倍）[D]，GLM-5.3、V4-Pro、V4.1-Flash 池的 Bedrock 計量 TPM 因此被低估。 |
| Bedrock 預設配額 | Opus 5.5 30M；Sonnet 5.5 6M；Kimi K3 10M；GLM-5.3、V4-Pro、V4.1-Flash 100M | cross-Region 與 global TPM：Opus 5.5 30M、Sonnet 5.5 6M、Kimi K3 10M；DeepSeek V3.2、GLM 5 等 open-weight 模型 100M TPM 與 10,000 RPM（皆不可調） | [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html) | B | **文件值；後三個模型為借用值。** 配額表沒有 GLM-5.3、DeepSeek V4-Pro、V4.1-Flash 的列，借用同類別的 100M。 |
| Azure PTU（gpt-6.1-sol） | (U + 0.1 × C + 5 × O) ÷ 3,000 | 每 PTU 3,000 input TPM；normalised 權重：輸出 5.0、cached 輸入 0.1、cache write 1.25（long context：輸入 2.0、輸出 7.5）；頁面更新 2026-09-24 | [PTU sizing](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing) | B | **文件值，兩項權重未套用。** 模型的 U 不區分 cache write，1.25 沒有進公式；long context 的權重與門檻也沒有套用（門檻筆記未記載）。 |
| Google GSU（Claude Opus 5.5） | (U + 0.05 × C + 5 × O) ÷ 60 ÷ 261 | 每 GSU 261 tokens/s；輸出 burndown 5；cached 輸入 0.05；cache write 1.25 或 2；頁面更新 2026-10-01 | [Provisioned Throughput supported models, updated 1 Oct 2026](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/supported-models) | B | **文件值。** cache write 的權重同樣沒有套用。 |
| Google GSU（Gemini 3.8 Flash） | (U + 0.1 × C + 5 × O) ÷ 60 ÷ 675 | 每 GSU 675 tokens/s；輸出 5；cached 輸入 0.1 | [Provisioned Throughput supported models, updated 1 Oct 2026](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/supported-models) | B | **文件值。** |
| Cerebras | 未快取 bucket = U + O；total bucket = U + C + O | 兩個 bucket：uncached TPM 與 total TPM（未快取的 3 倍）；cache read 只計入 total | [Cerebras rate limits](https://inference-docs.cerebras.ai/support/rate-limits) | B | **文件值。** 入場估計值是輸入 + `max_completion_tokens`，模型沒有計預扣。 |

### 硬體換算

四個操作點都取自 InferenceX AgentX（agentic coding trace 重播）2026-10-04 的快照；完整欄位在第 10 章，這裡列每個值的出處與代用關係。

| 參數 | 模型採用值 | 公開證據的數值或範圍 | 來源 | 等級 | 採用理由或落差 |
|---|---|---|---|---|---|
| Kimi K3 操作點 | 136 output tokens/s per GPU；每使用者 38 tokens/s | GB300 NVL72、dynamo-vllm、MXFP4、TP8、併發 48、8 顆、DRAM offload 160 GB（2026-09-15）：output 136、total 19,303 tokens/s per GPU；每使用者中位 38、P90 26；TTFT 中位 1.15 s、P90 2.88 s | [InferenceX API, model=Kimi-K3, pulled 4 Oct 2026](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Kimi-K3) | A | **量測值（上限）。** speculative decoding 以固定的 acceptance 計（golden 3.84；真實 trace 量到 1.18–1.68）；不開時 GB200 NVL72、併發 96 為 71。 |
| GLM-5.3 操作點 | 149；每使用者 101 tokens/s | GLM-5.2 的量測：GB300 NVL72、dynamo-sglang、FP4、P/D disagg、併發 128、32 顆（2026-10-02）：output 149；每使用者 101 / 90；TTFT 2.33 / 5.81 s | [InferenceX API, model=GLM-5.2, pulled 4 Oct 2026](https://inferencex.semianalysis.com/api/v1/benchmarks?model=GLM-5.2) | A | **借用值。** 以 GLM-5.2 的量測代表 GLM-5.3（兩者同為 78 層 MLA、KV 元素數相同）；GLM-5.3 於 2026-09-22 才進入 InferenceX。 |
| DeepSeek V4-Pro 操作點 | 739；每使用者 37 tokens/s | B300、sglang、FP4、TP8/EP8/DPA、併發 384、8 顆、DRAM 2,849 GB（2026-09-29）：output 739；每使用者 37 / 34；TTFT 2.94 / 12.66 s | [InferenceX API, model=DeepSeek-V4-Pro, pulled 4 Oct 2026](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4-Pro) | A | **量測值。** P90 TTFT 為 12.66 s，尾端延遲長。 |
| DeepSeek V4.1-Flash 操作點 | 3,059；每使用者 60 tokens/s | B300、vllm、FP4、TP2/EP2/DPA、併發 192、2 顆、無 KV offload（2026-10-02）：output 3,059；每使用者 60 / 41；TTFT 0.25 / 0.81 s | [InferenceX API, model=DeepSeek-V4.1-Flash, pulled 4 Oct 2026](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4.1-Flash) | A | **量測值。** 同表 GB300 NVL72 為 3,108。 |
| Kimi K3 KV bytes / token | 13.8 KB | 24 層 MLA × 576 個元素 × 1 byte（FP8）= 13,824 B [D]；InferenceX 紀錄 42.23 GiB ÷ 3,249,215 tokens = 13,955 B；SGLang 的「about 27 KB」是 BF16 | [InferenceX perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)、[LMSYS blog, 27 Jul 2026](https://www.lmsys.org/blog/2026-07-27-kimi-k3-day0-support/) | A；B | **量測值（FP8 KV）。** KV 以 BF16 存放時加倍。 |
| Kimi K3 每序列的 recurrent state | 434 MB | 69 × 96 × 128 × 128 個 FP32 元素 = 434 MB [D]；SGLang：TP8 下每 rank 約 54 MB（434 ÷ 8 = 54.3） | [LMSYS blog, 27 Jul 2026](https://www.lmsys.org/blog/2026-07-27-kimi-k3-day0-support/) | B | **換算值（下限）。** vLLM 為 prefix caching 每 32K tokens 與 prompt 邊界各存一份 state，每個 session 的份數查無公開資料。 |
| Kimi K3 的 HBM KV 容量 | 3.25M tokens / 8 顆 | 8 顆 B300、TP8：「GPU HBM can only hold 3.25M tok」（2026-08-03）；vLLM 部落格同硬體為 1.93M（DCP8 為 19.75M，2026-09-13） | [InferenceX blog, 3 Aug 2026](https://inferencex.semianalysis.com/blog/kimi-k3-the-manos-the-mythos-the)、[vLLM blog, 13 Sep 2026](https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-09-13-kimi-k3-performance-optimization.md) | A；B | **借用值。** 操作點在 GB300 NVL72，容量取自 B300。兩個來源相差 1.7 倍，筆記歸因於 KV 的精度（FP8 對 BF16）[D]。TP 下 MLA KV 每個 rank 各存一份，3.25M 是整組 8 顆的容量。 |
| GLM KV bytes / token | 44.9 KB | 78 層 × 576 個 FP8 元素 = 44,928 B [D]；llm-d「about 44 KB」；含 indexer keys 約 46.5 KiB [D]；8 顆 MI325X 上引擎回報的 KV pool 折合每 token 約 75 KB（每 rank 約 110 GB ÷ 1,477,168 tokens）[D] | [llm-d blog, 22 Jul 2026](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)、[vLLM GLM-5.3 recipe](https://github.com/vllm-project/recipes/blob/main/models/zai-org/GLM-5.3.yaml) | B | **換算值（下限）。** 引擎實際的預算高 1.7 倍。模型沒有設 GLM 的 HBM KV 容量，所以 GLM 池不算 KV 受限的 GPU 數。 |
| V4-Pro KV bytes / token | 5.0 KB | 1M tokens 的序列約 9.62 GiB（BF16），即 9,856 B / token；attention cache 用 FP8、indexer cache 用 FP4 後「roughly 2x」更小 | [vLLM blog, 24 Apr 2026](https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-04-24-deepseek-v4.md) | B | **換算值。** FP8 / FP4 格式的確切 bytes 查無公開資料。 |
| V4-Pro 的 HBM KV 容量 | 43M tokens / 8 顆 | 8 顆 B300、vLLM、DEP8、3 TB DRAM、併發 384：HBM cache 命中 91%，HBM KV working set 約 43M tokens（8 顆 B200、併發 196 時為 22M） | [InferenceX blog, 25 Aug 2026](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-b200-vs-b300-kv-working-set) | A | **借用值。** 量測用 vLLM（2026-08-25），操作點是 SGLang（2026-09-29）；working set 是該併發下的常駐量，不是容量上限。 |
| V4.1-Flash KV bytes / token | 0.89 KB | global KV「890 bytes per token」；每層另有 128 tokens 的 sliding window | [V4.1-Flash card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)、[vLLM DeepSeek-V4.1-Flash recipe](https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4.1-Flash.yaml) | C | **宣稱值。** 廠商規格，不含 sliding window。 |
| list price（每 M tokens：輸入 / cached / 輸出） | Kimi K3 3.00 / 0.30 / 15.00；GLM-5.3 1.40 / 0.26 / 4.40；V4-Pro 1.32 / 0.044 / 3.96；V4.1-Flash 0.30 / 0.006 / 1.20 | 與左欄相同；DeepSeek 為尖峰價（01:00–04:00 與 06:00–10:00 UTC，週一至週五），離峰半價；Kimi K3 的 cache write 為 3.00（5 分鐘 TTL）或 6.00（1 小時） | [Kimi pricing](https://platform.kimi.ai/docs/pricing/chat)、[Z.ai pricing](https://docs.z.ai/guides/overview/pricing)、[DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing) | C | **宣稱值。** 2026-10-04 經摘要工具讀取，引用前需重查；DeepSeek 全部以尖峰價計；Opus 5.5 與 Sonnet 5.5 的價格模型未設（見第 5 章）。 |
| 混合實付均價 | $0.72 / M tokens | 2026-04 付款資料的平均實付價；Claude Sonnet 4.6 $0.62/M（牌價 $3.00）、Opus 4.6 $1.00/M、GPT-5.5 $1.42/M | [Ramp: AI token cost for businesses](https://ramp.com/blog/ai-token-cost-for-businesses) | B | **量測值，套用範圍過寬。** 這是 Ramp 客戶的整體混合；以 Kimi K3 的牌價計，coding base 的 token 組成是 $0.59/M、OA base 是 $3.02/M [D]，OA 與 R&D 的成本被低估，但兩者在組合 B 只占 token 的 6%。 |

- 操作點的 TTFT 只供顯示：自建池的 W 用角色的 TTFT 假設（1.0、2.0、2.5 s）加上 o ÷ 操作點的每使用者速度。四個操作點都來自 agentic coding trace，拿來估 OA 與 R&D 池沒有量測依據（第 10 章）。

### 角色與模型組合

八種角色組合與 MX2–MX4 的路由比例是示範用的情境設定，沒有公開資料支持任何一組比例；只有 MX1 的 Opus 占比有出處，而且出處的單位與模型不同。

| 參數 | 模型採用值 | 公開證據的數值或範圍 | 來源 | 等級 | 採用理由或落差 |
|---|---|---|---|---|---|
| 角色組合 A–E（OA / coding / R&D） | A 90 / 7 / 3；B 70 / 12 / 18；C 80 / 15 / 5；D 40 / 50 / 10；E 35 / 25 / 40（%） | 沒有各產業的角色占比資料；單一例子：一家旅遊科技公司 1,500 人中有 800 名工程師（2026-06-30） | [SemiAnalysis: TokenBudgeting](https://newsletter.semianalysis.com/p/tokenbudgeting-our-conversations) | C（單例） | **情境設定。** 使用時應代入自己的人事資料。 |
| 員工數 | 1,000、10,000、50,000、100,000 | 情境輸入 | 無 | D | **情境設定。** |
| MX1：OA 的呼叫送 Opus | 10%（其餘 90% 送 Sonnet） | Claude chat 與 Cowork 的對話 10% 由 Opus 處理（2026-06-26） | [Anthropic Economic Index: Cadences](https://www.anthropic.com/research/economic-index-june-2026-report) | B | **量測值，單位不同。** 來源是「對話」的占比，模型套在「呼叫」上；其餘全歸 Sonnet 是假設。 |
| MX1：coding 的呼叫送 Opus | 54%（其餘 46% 送 Sonnet） | Claude Code 的 session 54% 由 Opus 處理（同上） | [Anthropic Economic Index: Cadences](https://www.anthropic.com/research/economic-index-june-2026-report) | B | **量測值，單位不同。** session 的占比不等於 token 的占比。旁證：premium 模型占企業 token 的 45.8%、成本的 55.9%（2026-04）[B] [Ramp: AI token cost for businesses](https://ramp.com/blog/ai-token-cost-for-businesses)；MX1 在組合 B、base 下 Opus 占 token 的 53% [D]。 |
| MX1：R&D 的呼叫送 Opus | 50% | 查無公開資料 | 無 | D | **情境設定。** |
| MX2、MX3、MX4 的路由比例 | 見第 10 章 | 查無公開資料 | 無 | D | **情境設定。** |

- 模型值與用量筆記範圍表不同之處集中在 high：筆記的 High 欄在 OA 是 P95 使用者（每活躍日 1.9M tokens），在 coding 是單一無人值守的使用者（每活躍日 0.7B）；模型的 high 是全體平均，分別取 384K 與 51.7M。

## 公開的企業用量與 rate limit 參考資料

同時揭露 token 總量與人數的組織只有兩個：Meta（每員工每日曆日 23.6M tokens，2026-04）與 Copilot coding agent 的使用者（每人每週 prompt tokens 平均 14.0M、中位 3.2M，2026-06）；企業 chat 的每席次絕對訊息數沒有任何廠商公布。平台配額以 2026-10-04 讀到的文件為準，各平台對 cache read、output 與 `max_tokens` 的計法不同。

### (a) 企業 chat 的訊息量與活躍占比

| 對象（期間） | 揭露的數值 | 換算 [D] | 等級 | 來源 |
|---|---|---|---|---|
| ChatGPT 消費者方案（至 2025-07；不含 Business、Enterprise、Edu） | 每週 18B 則訊息、700M 位使用者；每日訊息由 451M（2024-06）到 2,627M（2025-06），其中工作相關 716M（27%） | 每位 WAU 每日 3.7 則（D：18B ÷ 700M ÷ 7） | B | [OpenAI/NBER "How People Use ChatGPT"](https://cdn.openai.com/pdf/a253471f-8260-40c6-a2cc-aa93fe9f142e/economic-research-chatgpt-usage-paper.pdf) |
| ChatGPT（公司揭露，Epoch AI 彙整） | 300M WAU、每日 1B 則（2024-12-04）；700M WAU、每日 3B 則（2025-08-04）；1.2B WAU（2026-09-29） | 每位 WAU 每日 3.3 → 4.3 則，八個月 +29% | C | [Epoch AI usage-reports CSV](https://epoch.ai/data/ai_companies_usage_reports.csv) |
| 第三方估計（2025-03-28，Epoch AI 彙整） | ChatGPT 160M DAU、每日 1.2B 則；Gemini 35M DAU、每日 140M 則 | 每位 DAU：ChatGPT 7.5 則、Gemini 4.0 則 | C | [Epoch AI usage-reports CSV](https://epoch.ai/data/ai_companies_usage_reports.csv) |
| ChatGPT Enterprise（2025-12 報告） | 超過 7M 個工作席次；每週訊息自 2024-11 起約 8 倍，平均每位員工 +30%；P95 員工的訊息量是中位數的 6 倍（coding 17 倍）；P95 公司每席次訊息是中位公司的 2 倍 | 中位數每日 10 則時 P95 約 60 則 | B | [OpenAI, The state of enterprise AI 2025](https://cdn.openai.com/pdf/7ef17d82-96bf-4dd1-9df2-228f7f377a29/the-state-of-enterprise-ai_2025-report.pdf) |
| Moderna（個案；部署於 2024） | 每位使用者每週 120 個 ChatGPT Enterprise 對話 | 每工作日 24 個對話 | C | [OpenAI customer story: Moderna](https://openai.com/index/moderna/) |
| Panasonic Connect（FY2025；約 11,800 名員工） | 使用次數 3.61M（年增 1.6 倍）；每月不重複使用者 61%（前一年 49%） | 每位員工每工作日 1.25 次；每位月活躍者 2.05 次 | B | [Panasonic Newsroom Japan](https://news.panasonic.com/jp/press/jn260729-1) |
| Microsoft 365 Copilot（財報電話會議的轉述） | 付費席次 15M（2026-01）→ 超過 30M（2026-07）；DAU 年增 10 倍；每使用者對話數約 2 倍 | 無絕對值 | C | [The Register](https://www.theregister.com/software/2026/02/02/microsoft-reveals-just-33-of-copilot-chat-users-pay-for-it/4288251)、[Yahoo Finance / Benzinga](https://finance.yahoo.com/technology/ai/articles/microsofts-copilot-just-crossed-30-183023723.html) |

| 部署（期間） | 規模 | 活躍占比 | 等級 | 來源 |
|---|---|---|---|---|
| 66 家公司的隨機實驗，早期 M365 Copilot（2023-09 至 2024-10） | 7,137 名知識工作者 | 6 個月內用過者超過 90%；每週使用穩定在略低於 40%（前幾週高峰 55%）；5% 每週都用、20% 從未使用；各公司每週 6.3–70%；電信與科技業 45%、營建與製造業 25% | A | [Dillon et al.](https://arxiv.org/abs/2504.11436) |
| 英國跨部會 M365 Copilot 試驗（2024-09-30 至 12-31） | 20,000 名公務員（遙測 14,500 人；問卷 n = 7,115） | 30 日活躍 83%，維持約 80%；問卷：39% 一日多次、另 43% 一週多次；每日使用 Teams 34%、Outlook 33%、Word 25% | A | [GOV.UK findings report](https://www.gov.uk/government/publications/microsoft-365-copilot-experiment-cross-government-findings-report/microsoft-365-copilot-experiment-cross-government-findings-report-html) |
| JPMorgan LLM Suite（2025-10-07） | 250,000 人可用 | 約半數每日使用 | C | [CeFPro Connect](https://connect.cefpro.com/article/view/inside-jpmorgan-llm-suite-as-ai-agents-spread-across-the-bank) |
| 美國受雇者的機率樣本（2025-06-15） | 全體員工，不限授權 | 一週數次以上 19%；每日 8%（前一年 4%）；科技業 50%、金融業 32% | A | [Gallup](https://www.gallup.com/workplace/691643/work-nearly-doubled-two-years.aspx) |

- 活躍占比的來源互不一致，因為量的對象不同：早期 app 內助理的遙測（每週約 40%）、自選的問卷回覆者（英國，39% 一日多次）、主管的整數（JPMorgan）、不分授權的全體員工（Gallup，每日 8%）。筆記的判斷是：有變革管理的成熟通用助理，以英國與 Panasonic（每月 60–80%、每日約 30–35%）為文件最完整的中段 [D]。

### (b) 每次請求的 token 數

| 工作負載 | 資料（期間） | 輸入 tokens / 請求 | 輸出 tokens / 請求 | 等級 | 來源 |
|---|---|---|---|---|---|
| chat | Azure conversation（2024-05；27.3M 次請求） | 平均 1,632、中位 928、P90 3,830、P99 6,683 | 平均 105.5、中位 41、P90 342、P99 694 | A，筆記實算 | [AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md) |
| chat | Azure conversation（2023-11；19,366 次） | 平均 1,155、中位 1,020 | 平均 211、中位 129 | A | [AzureLLMInferenceDataset2023](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2023.md) |
| chat | BurstGPT（2023–2024） | 平均 878、中位 524 | 平均 269、中位 203 | A，筆記實算 | [BurstGPT](https://github.com/HPMLL/BurstGPT) |
| chat | LMSYS-Chat-1M（2023-04 至 08；每對話 2.0 turn） | 每個 prompt 69.5 | 每個回應 214.5 | A | [LMSYS-Chat-1M](https://arxiv.org/abs/2309.11998) |
| chat | WildChat（2023–2024；每對話 2.54 turn） | 每 turn 295.58 | 每 turn 441.34 | A | [WildChat](https://arxiv.org/abs/2405.01470) |
| API 混合 | OpenRouter（約兩年，至 2025-11；超過 100T tokens） | 平均由約 1.5K 升到 6K 以上；程式類常超過 20K | 平均由約 150 升到 400（含 reasoning） | B | [OpenRouter/a16z State of AI](https://openrouter.ai/state-of-ai) |
| code completion | Azure code（2024-05；16.8M 次） | 平均 2,511、中位 1,930、P90 6,251、P99 7,685 | 平均 22.7、中位 8、P90 43、P99 271 | A，筆記實算 | [AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md) |
| code completion | Azure code（2023-11；8,819 次） | 平均 2,048、中位 1,469 | 平均 27.9、中位 13 | A | [AzureLLMInferenceDataset2023](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2023.md) |
| coding agent | Copilot agent 論文（2026-06 第一週；760.5M 次呼叫） | prompt 中位 68K，其中 cached 中位 63K | 中位 247；88% 的呼叫低於 1,000（不含 reasoning） | A | [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101) |
| coding agent | Copilot 公開樣本（同週；9.31M 次呼叫） | 平均 69,728、中位 56,826；85.7% 是 cache read（資料卡的總量換算為平均約 67.9K：631.4B ÷ 9.3M，cached 540.95B ÷ 631.4B = 85.7%） | 平均 543、中位 175（資料卡換算約 528：4.91B ÷ 9.3M） | A，筆記實算（本次查核未能重算，只以資料卡的總量核對） | [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) |
| coding agent | TraceLab（43 位開發者；2025-09 至 2026-06） | prefix 中位 119K、append 中位 875；Claude 的 prefix 平均 194,361、P90 467,082；Codex 平均 116,623 | 中位 214；Claude 平均 690、P90 1,671、P99 6,571；Codex 平均 415（含 reasoning） | A | [TraceLab](https://arxiv.org/abs/2606.30560) |
| coding agent | Pegatron（1 位開發者 28 天；Claude Code + Opus 4.7 / 4.8） | 每請求約 480K；cache 命中 99.3% | 平均 632 [D：20.16M ÷ 31,901] | A（n = 1） | [Inference Economics of Enterprise Coding Agents](https://arxiv.org/abs/2607.13080) |
| coding agent | Ant Group 的 agent 平台（兩週；11.7M 次請求） | 中位 70,026、P90 229K；每請求 cache 占比中位 98.1% | 中位 188、P90 1.23K | A | [Understanding Agent Serving at Production Scale](https://arxiv.org/abs/2609.34432) |
| deep research | Gemini Deep Research（文件更新 2026-09-23） | 每 run 約 250K（50–70% cached）；Max 約 900K | 每 run 約 60K；Max 約 80K；約 80 與 160 次搜尋 | C | [Gemini Deep Research agent docs](https://ai.google.dev/gemini-api/docs/deep-research) |
| 文件 | Claude 的 PDF 輸入 | 每頁 1,500–3,000 tokens；每請求最多 600 頁 | 不適用 | B | [Claude PDF support docs](https://platform.claude.com/docs/en/build-with-claude/pdf-support) |

- agent 相對 chat 的倍數：agent 約 4 倍、multi-agent 約 15 倍（2025-06-13）[C] [Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)；agent teams 約為標準 session 的 7 倍 [C] [Claude Code docs: Manage costs effectively](https://code.claude.com/docs/en/costs)；SWE-bench Verified 上的 agentic coding 任務，token 是單輪推理任務的 3,500 倍、多輪聊天的 1,200 倍（2026-04-29）[A] [How Do AI Agents Spend Your Money?](https://arxiv.org/abs/2604.22750)。
- 輸入對輸出（總量）：chat 15.5 : 1（Azure）與 3.3 : 1（BurstGPT）；code completion 110.7 : 1；coding agent 128 : 1，其中未快取輸入對輸出約 18 : 1 [A，筆記實算]。
- 兩份筆記對 Copilot 公開樣本的每次呼叫平均不一致：用量筆記以總量相除得 prompt 67.9K、completion 528；容量筆記由逐筆資料得 69,728 與 543。中位數也有兩組：論文（全樣本）68K 與 247，公開樣本 56,826 與 175。
- Copilot 論文的總量自相矛盾：摘要寫 95T tokens，Table 3 是 44.9T prompt + 39.3B completion，Table 4 的每 turn 平均 × 95.1M 個 turn 約為 55T 與 380B。筆記因此採用每次呼叫與每 turn 的分布，不用總量。

### (c) coding agent 的成本、token 揭露、預算與上限

| 對象（期間） | 揭露的數值 | 等級 | 來源 |
|---|---|---|---|
| Claude Code 文件（2026-10-04 取得） | 企業部署平均每位開發者每活躍日約 $13、每月 $150–250；90% 的使用者低於每活躍日 $30；範例 session：1.2K 輸入、5.3K 輸出、940.0K cache read、50.0K cache write（$0.55） | C | [Claude Code docs: Manage costs effectively](https://code.claude.com/docs/en/costs) |
| Copilot agent，每位使用者每週（2026-06 第一週；3.2M 位使用者） | session 中位 2、P90 8；turn 中位 11、P90 74；prompt tokens 中位 3.2M、P90 38M；completion 中位 33K、P90 282K | A | [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101) |
| Copilot agent，每個 session 與每個 turn | 每 session 的 LLM 呼叫中位 15、平均 40.6、P90 100.5；每 turn 中位 4.5、平均 6.6；每 turn 的 prompt 中位 227.6K、平均 582.5K；turn 內約 90% cached、turn 邊界 55%、換模型後 8%；87% 的呼叫由 agent 發起 | A | [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101) |
| TraceLab（43 位開發者；4,265 個 session；357,161 步） | 輸入 54.90B（其中 prefix 52.56B）、輸出 186.9M；以牌價計約 $40.4K；prefix cache 命中 95.7%；每 session 成本平均 $9.70、中位 $0.61、P90 $13.4、P99 $178 | A | [TraceLab](https://arxiv.org/abs/2606.30560) |
| Pegatron（台灣；1 位開發者；28 天；論文 2026-07-13） | 31,901 次請求、合計 15.33B tokens（cache read 15.20B）、22 個活躍日；$8,785.21，即實付 $0.573/M；改用 Opencode + GLM-5.1 / 5.2（地端 vLLM）的 28 天：12,281 次請求、cache 命中 86.4% | A（n = 1） | [Inference Economics of Enterprise Coding Agents](https://arxiv.org/abs/2607.13080) |
| 個人重度使用者（30 天；2026-05-27） | Claude Code $1,199.79、Codex $980.37（以 API 價自行量測） | C | [Simon Willison, 27 May 2026](https://simonwillison.net/2026/May/27/product-market-fit/) |

| 組織或來源（日期） | 預算、上限或總量 | 等級 | 來源 |
|---|---|---|---|
| Meta（2026-04；轉述 The Information） | 超過 85,000 名員工 30 天用了 60.2T tokens（以 API 牌價計 $900M）；用量最高的個人約 280B；2026-02 約每月 70T | C | [The Pragmatic Engineer](https://blog.pragmaticengineer.com/the-pulse-tokenmaxxing-as-a-weird-new-trend/)、[SemiAnalysis: TokenBudgeting](https://newsletter.semianalysis.com/p/tokenbudgeting-our-conversations) |
| Salesforce、Shopify（2026-04-23） | Salesforce：Claude Code 每月最低期望 $100、上限 $250，Cursor 為 $70 與 $170；Shopify 的頂端使用者每月 $1,000 的 Cursor credits | C | [The Pragmatic Engineer](https://blog.pragmaticengineer.com/the-pulse-tokenmaxxing-as-a-weird-new-trend/) |
| 超過 50 場企業訪談（2026-06-30） | 每人每月上限：美國前三大航太國防公司之一 $250（重度使用者四天用完）、大型藥廠 $500、Workday 與 Stripe 約 $2,000、上市資安公司 junior $800 與 senior $1,600–4,000；一家旅遊科技公司預設 $200 | C | [SemiAnalysis: TokenBudgeting](https://newsletter.semianalysis.com/p/tokenbudgeting-our-conversations) |
| Uber（2026-06-03；轉述 Bloomberg） | 四個月用完 2026 年的 AI 預算後，每人每個 coding 工具每月上限 $1,500 | C | [Simon Willison: Uber caps usage](https://simonwillison.net/2026/Jun/3/uber-caps-usage/) |
| Ramp 的客戶（2026-04 的付款資料） | 每員工每月 token 支出中位 $46（中間 50% 為 $3–$352）；token 用量自 2025-01 起成長 1,001%，支出 +497% | B | [Ramp: AI token cost for businesses](https://ramp.com/blog/ai-token-cost-for-businesses) |
| Ramp AI Index（2026-06-10） | 每員工每月：前 1% 的公司 $7,500、前 10% 約 $611、中位 $11.38 | C | [TechCrunch](https://techcrunch.com/2026/06/10/ai-pilled-firms-spend-7500-per-employee-each-month-on-ai/) |
| AWS 的 Claude Code on Bedrock 指引（repo commit 2026-08-20） | 每使用者每月上限的預設值 225M tokens；每日約 8.25M（225M ÷ 30 × 1.10） | C | [QUOTA_MONITORING.md](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/QUOTA_MONITORING.md) |
| Google 內部開發工具（2026-06-03） | 每日超過 3T tokens，每幾週翻倍；人數未揭露 | C | [Alphabet investor presentation](https://blog.google/alphabet/investor-presentation-june-2026/) |
| 方案額度 | GitHub Copilot 自 2026-06-01 起用量計費：Business $19 含每月 1,900 AI credits（1 credit = $0.01）、Enterprise $39 含 3,900；Cursor Pro $20 約為 225 次 Sonnet 4 請求（2025-07） | B | [GitHub Docs: plans](https://docs.github.com/en/copilot/get-started/plans)、[Cursor: Clarifying our pricing](https://cursor.com/blog/june-2025-pricing) |

- 金額換成 token [D]：以實付 $0.573/M（Pegatron）、$0.62/M（Sonnet 4.6）、$1.00/M（Opus 4.6）計，$13 = 13–23M tokens，$30 = 30–52M，每月 $150–250 = 150–436M。Pegatron 每活躍日 1,450 次請求、697M tokens；TraceLab 約每位開發者每月 $104。Meta 的 $900M ÷ 60.2T = $14.95/M，是未快取牌價的假設。
- 用量筆記自己不一致的一處：引述的論文數字是 turn 邊界 55% cached，同一份筆記的範圍表卻寫成約 45% cached（55% 未快取）。
- 每位開發者支出的來源不一致：Anthropic 的企業平均（每月 $150–250）、學術團隊（約 $104）、個人重度使用者（每個工具約 $1,000–1,200）、上限（$200–4,000）；差異來自母體、模型組合與 agent 是否無人值守。
- 每員工支出的來源不一致：Ramp 部落格的中位數（$46 / 月）只含使用其 token 支出產品的公司，Ramp AI Index 的中位數（$11.38 / 月）含所有透過 Ramp 付款給 AI 廠商的企業；SemiAnalysis 認為 Fortune 500 的中位數遠低於每員工每年 $100 [C] [SemiAnalysis: TokenBudgeting](https://newsletter.semianalysis.com/p/tokenbudgeting-our-conversations)。
- 開發者調查：59% 在工作中使用 agent（2025 年為 31%），每日使用者占開發者 40%、學術研究者 28%（2026-04）[A] [Stack Overflow pulse survey](https://stackoverflow.blog/2026/05/27/agents-on-a-leash-agentic-ai-remains-mostly-monitored-at-work/)。

### (d) 總量層級的數字

| 提供者或組織（日期） | 數值 | 等級 | 來源 |
|---|---|---|---|
| Google 全部產品（2026-05 至 06） | 每月 token：9.7T（2024）→ 480T（2025）→ 3.2 quadrillion（2026）；模型 API 每分鐘約 19B tokens | C | [Shacknews on the I/O keynote](http://www.shacknews.com/article/149205/google-3-2-quadrillion-monthly-ai-tokens)、[Alphabet investor presentation](https://blog.google/alphabet/investor-presentation-june-2026/) |
| OpenAI API | 每分鐘 6B tokens（2025-10-06）→ 超過 15B（2026-04-06；二手來源） | C | [Epoch AI usage-reports CSV](https://epoch.ai/data/ai_companies_usage_reports.csv)、[Business Analytics Review](https://businessanalytics.substack.com/p/openais-api-hits-15-billion-tokens) |
| OpenAI 的企業客戶（2025-12） | 超過 9,000 個組織處理過 10B tokens 以上，近 200 個超過 1T | B | [OpenAI, The state of enterprise AI 2025](https://cdn.openai.com/pdf/7ef17d82-96bf-4dd1-9df2-228f7f377a29/the-state-of-enterprise-ai_2025-report.pdf) |
| Doubao（2026-06-23） | 每日 180T tokens（2026-04 為 120T） | C | [IT之家](https://www.ithome.com/0/967/330.htm)、[新浪科技](https://finance.sina.com.cn/tech/roll/2026-04-02/doc-inhtazrz4446028.shtml) |
| Microsoft Foundry（2026-02-13） | 超過 80,000 家客戶；250 家以上今年各將處理超過 1T tokens | C | [Perspectives Plus](https://www.perspectives.plus/p/microsoft-ai-numbers-good-bad-ugly) |
| Meta（2026-04） | 60.2T ÷ 85,000 人 ÷ 30 天 = 每員工每日曆日 23.6M tokens [D] | C | [The Pragmatic Engineer](https://blog.pragmaticengineer.com/the-pulse-tokenmaxxing-as-a-weird-new-trend/) |
| Copilot coding agent（2026-06 第一週） | 3.2M 位使用者一週 44.9T prompt tokens，每人平均 14.0M [D] | A | [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101) |

- Doubao 的每日 180T（每月 5.4 quadrillion）高於 Google 的每月 3.2 quadrillion；兩家的計數規則沒有公開，不能跨供應商比較 [D]。
- 成長 [D]：Ramp 的企業 token 用量 15 個月 11 倍；OpenAI API 六個月 2.5 倍；chat 的每席次用量每年 +30% 至 +100%；由 chat 換成 agent 是每個任務 4–15 倍、每個開發者日 100–1,000 倍（39K 對 13–23M tokens）。

### (e) trace 上的尖峰對平均

資料集 [A]：Azure LLM inference trace 2024（2024-05-10 至 19；code 16,803,695 次與 conversation 27,303,999 次請求）[AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md)；BurstGPT（區域性 Azure OpenAI GPT 服務 213 天、10.31M 筆，其中一個服務超過 3,000 位使用者，時間戳為當地時間）[BurstGPT paper](https://arxiv.org/abs/2401.17644)；GitHub Copilot coding agent 公開樣本（非企業使用者，2026-06-01 至 07；301,026 個 session、9,310,255 次 LLM 呼叫，約為全體 session 的 2%）[Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md)；ServeGen（Alibaba Cloud Model Studio，四個月 3.54B 次請求）[ServeGen](https://arxiv.org/abs/2505.09999)；Ant Group 的 agent 平台（兩週 11.7M 次請求，超過 10,000 顆 GPU）[Understanding Agent Serving at Production Scale](https://arxiv.org/abs/2609.34432)。

下表全部是「A，筆記實算」：請求與 token 以每分鐘、每小時分箱（UTC；BurstGPT 用當地時間），只計平日；BurstGPT 的星期是推定的。

| 指標 | Azure code（2024-05） | Azure conversation（2024-05） | BurstGPT conversation（2023–2024；三個檔） | Copilot coding agent（2026-06） |
|---|---|---|---|---|
| busy hour 占平日請求 | 8.9–9.7%（平均 9.3%） | 5.2–5.8%（平均 5.6%） | 平均 10.6%、12.4%、11.6%（p10–p90 9.0–14.1%） | 6.8–7.0%（平均 6.8%） |
| busy hour 占平日 token | 9.2–9.9%（平均 9.5%） | 5.3–5.5% | 10.7%、12.5%、11.9% | 全部 6.7–7.0%；未快取輸入 6.6–7.6%；輸出 6.1–6.9% |
| 最忙 8 小時占平日 token | 64.5% | 38.9% | 59.7–65.3% | 50–52% |
| 尖峰小時 ÷ 平均小時（整週） | 3.01（請求）、3.18（token） | 1.66、1.61 | 4.2–6.8（請求） | 2.29（呼叫）、2.21（token）、2.41（未快取輸入） |
| 尖峰分鐘 ÷ 平均分鐘（整週） | 3.53、3.73 | 1.89、1.86 | 每分鐘只有 4–5 個請求，無意義 | 2.55（呼叫）、2.52（token）、3.17（未快取輸入）、2.79（輸出） |
| 尖峰分鐘 ÷ busy hour 的平均分鐘 | 中位 1.15、最大 1.30（請求）；1.18、1.38（token） | 1.12、1.19；1.14、1.16 | 中位 2.4–2.5、p90 3.0–3.1、最大 3.2–4.3 | 中位 1.09、最大 1.12（呼叫）；1.13（token）；1.29、最大 1.32（未快取輸入）；1.15（輸出） |
| 週末日 ÷ 平日 | 0.32（請求）、0.28（token） | 0.57 | 0.52、0.36、0.52 | 0.21（呼叫）、0.22（token）、0.27（輸出） |
| P95 平日 ÷ 平均平日 | 只有一週 | 只有一週 | 1.20、1.28、1.80 | 只有一週 |

同時在途數的直接量測（A，筆記實算）[BurstGPT](https://github.com/HPMLL/BurstGPT)、[Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md)：

| 資料 | 平均在途 | 高分位或最大值 | 同均值的 Poisson |
|---|---|---|---|
| BurstGPT conversation：每個工作日到達最多的小時（80 個工作日；每小時到達中位 248） | 中位 0.45、平均 0.51 | p99 3、p99.9 10、最大 14 | p99 3、p99.9 4 |
| BurstGPT conversation：每日併發最高的小時 | 中位 0.52 | p99 8、p99.9 13；每日最大瞬時併發中位 4、p90 9、最大 18 | p99.9 4 |
| BurstGPT 的 API（程式化）log：38 個工作日 | 中位 2.5、p90 32.6 | p99 66–71；每日最大值中位 14、最大 116 | p99 13–15 |
| Copilot agent：五個平日的最忙小時（取樣單位） | 328–398 | p99.9 ÷ 平均 1.12–1.20；最大 ÷ 平均 1.15–1.27 | 1.16–1.18 |
| Copilot agent：兩個週末日的最忙小時 | 72 與 85 | p99.9 ÷ 平均 1.40 與 1.36 | 1.38 與 1.35 |

每人尖峰隨母體變大而下降（多工曲線；A，筆記實算）[Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md)。作法：2026-06-02 與 06-03 兩天（各約 60,360 個 session、1.82M 次呼叫）隨機抽 S 個 session，加總每分鐘的量，取最大的一分鐘除以 S，重複 30–400 次取中位數。

| 每日 session 數 S | 尖峰分鐘全部 token / session | 尖峰分鐘「未快取輸入 + 輸出」/ session | 尖峰分鐘呼叫數 / session | 尖峰分鐘 ÷ 當日平均分鐘（全部 token） |
|---|---|---|---|---|
| 5 | 130K–143K（p90 230K–270K） | 29K–32K | 2.0 | 約 97 |
| 20 | 57K（p90 83K–90K） | 13.4K | 0.70–0.75 | 41 |
| 50 | 30K（p90 42K–45K） | 9.4K | 0.38–0.40 | 22 |
| 100 | 19.3K（p90 25.5K） | 6.6K–7.0K | 0.24–0.25 | 14 |
| 300 | 10.1K（p90 12.3K–12.9K） | 3.5K–3.6K | 0.13 | 7.5 |
| 1,000 | 5.7K–5.9K（p90 6.7K） | 1.7K | 0.08 | 4.2–4.4 |
| 3,000 | 4.1K | 1.0K | 0.057 | 2.9 |
| 10,000 | 3.1K | 0.64K | 0.045 | 2.2–2.3 |
| 30,000 | 2.7K | 0.50K | 0.040 | 1.9–2.0 |
| 約 60,360（全部） | 2.5K–2.6K | 0.43K–0.49K | 0.037–0.039 | 1.8–1.9 |

- 已發表的對照：Azure 同一週的 conversation 尖峰是平均的 1.7 倍、谷值的 3.3 倍，coding 是 2.8 倍與 34.6 倍 [A] [DynamoLLM](https://arxiv.org/abs/2408.00741)；Ant 平台平日夜間的請求降到白天的 17.6%，GPU 使用率由 74.8% 降到 61.4% [A] [Understanding Agent Serving at Production Scale](https://arxiv.org/abs/2609.34432)。
- 突發性：5 分鐘視窗內到達間隔的變異係數，Azure code 中位 1.15、conversation 1.64、Copilot 取樣 1.02（只取 2% 的 session 會把 CV 推向 1）[A，筆記實算]；ServeGen 的 2,412 個 client 中前 29 個占 90% 的請求，以 Poisson 型工作負載佈建只得 12 個 instance，實際需要 25 個 [A] [ServeGen](https://arxiv.org/abs/2505.09999)。
- 併發也跟著呼叫時間走：Copilot 一週內併發最高的小時（平均在途 398）比到達最多的小時少 18% 的呼叫，但平均呼叫時間是 13.3 s 對 10.1 s [A，筆記實算]。
- 多工曲線的限制：session 不是使用者，母體是全球分散的非企業使用者；筆記估計單一時區的組織會在約 1.5–1.8 倍的位置持平 [D]。Anthropic 的建議表由 1–5 人到 500 人以上降 20 倍，trace 由 5 到 1,000 個 session 降 24 倍 [D]。
- 母體的歸類有疑問：Copilot 論文說 trace「all across the US」，公開樣本的小時分布卻在 08:00–14:00 UTC 最高；筆記把公開樣本當作跨多個時區處理，模型的 s = 0.065 依賴這個判斷。Azure 的 trace 是取樣比例不明的樣本，絕對速率沒有意義。

### (f) 平台的配額單位（2026-10-04）

除另有註記者外都是 B 級（廠商文件）。

**Anthropic API** [Anthropic rate limits](https://platform.claude.com/docs/en/api/rate-limits)：

| Tier（每月花費上限） | Opus、Sonnet、Haiku 4.5 各模型類別：RPM / ITPM / OTPM | Fable 5.x：RPM / ITPM / OTPM |
|---|---|---|
| Start（$500） | 1,000 / 2M / 0.4M | 1,000 / 0.5M / 0.1M |
| Build（$1,000） | 5,000 / 5M / 1M | 2,000 / 1.5M / 0.3M |
| Scale（$200,000） | 10,000 / 10M / 2M | 4,000 / 4M / 0.8M |

- 上限按模型類別分開計；Custom tier 與 account team 議定。文件的例子：2M ITPM、cache 命中 80% 時，每分鐘實際可處理 10M 輸入 tokens。

**Amazon Bedrock，bedrock-runtime endpoint** [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html)、[How tokens are counted in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html)：

| 模型 | 預設 TPM（cross-Region 與 global） | 其他預設值 | output burndown |
|---|---|---|---|
| Claude Opus 5.5 | 30M | RPM 未列 | 10× |
| Claude Opus 5 | 30M | 單一 Region 15M（不可調） | 10× |
| Claude Opus 4.8 | 30M | 無 RPM 配額 | 15× |
| Claude Opus 4.7 | 10M | 無 RPM 配額 | 5× |
| Claude Opus 4.6 | 3M | 單一 Region 1.5M；RPM 10,000（cross-Region）、5,000（on-demand） | 5× |
| Claude Opus 4.5 | 2M | global 每日 2.88B tokens；RPM 10,000 | 5× |
| Claude Sonnet 5.5 | 6M | RPM 未列 | burndown 文字未點名 |
| Claude Sonnet 5 | 6M | 單一 Region 3M（不可調） | 10× |
| Claude Sonnet 4.6 | 6M | 單一 Region 3M；RPM 10,000、5,000 | 5× |
| Claude Sonnet 4.5 | 5M | 1M context 版本為 1M TPM、1,000 RPM；RPM 10,000 | 5× |
| Claude Haiku 4.5 | 5M | RPM 10,000 | 5× |
| Claude Fable 5.1 / Fable 5 | 10M / 4M | RPM 未列 | 10×（5.1）；Fable 5 未點名 |
| Moonshot Kimi K3 | 10M | 每日 14.4B tokens | 1× |
| DeepSeek V3.2、V3、Qwen3 系列、Kimi K2.5、K2 Thinking、GLM 5、GLM-4.7、gpt-oss、MiniMax M2 系列、Mistral Large 3 | 100M（單一 Region on-demand；不可調） | RPM 10,000（不可調） | 1× |
| DeepSeek R1 | 200,000 | RPM 200 | 1× |

- bedrock-mantle endpoint 的配額另計（input / output TPM，無 RPM）：Opus 5.5、5、4.8、4.7 為 20M / 2M，Sonnet 5 為 3M / 0.3M [Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html)；兩個 endpoint 的流量分開計 [Quotas for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html)。AWS 兩份文件對 Opus 4.7 的 output TPM 不一致：General Reference 寫 2M，user guide 寫 4M [Bedrock mantle quotas](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html)。
- 帳號層級的「Cross-Model Max Tokens Per Day」每個 Region 700M、不可調，只相當於平均每分鐘 486K tokens [D]；它與 TPM 配額（30M × 1,440 = 每日 43.2B）如何互動，所讀頁面沒有說明。
- Reserved tier 的 input 與 output TPM 分開購買，最低 100K 與 10K TPM，期限 1 或 3 個月 [Bedrock service tiers](https://docs.aws.amazon.com/bedrock/latest/userguide/service-tiers-inference.html)；Provisioned Throughput 的 model unit 吞吐量沒有公開 [Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)。

**Azure PTU**（頁面更新 2026-09-24）[PTU sizing](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing)：

| 模型 | 每 PTU 的 input TPM | 輸出權重 | 延遲目標 |
|---|---|---|---|
| gpt-6.1-sol、gpt-6-sol | 3,000 | 5.0（cached 輸入 0.1、cache write 1.25；long context 的輸入 2.0、輸出 7.5） | 99% > 80 TPS |
| gpt-6-astra | 600 | 同上 | 99% > 40 TPS |
| gpt-5.6-luna / terra / sol | 30,000 / 3,000 / 1,200 | 6 | 99% > 100 / 70 / 80 TPS |
| gpt-5.5 | 1,200 | 6 | 99% > 50 TPS |
| gpt-5.4 / gpt-5.4-mini | 2,400 / 7,900 | 6 | 99% > 50 / 100 TPS |
| gpt-5.2、gpt-5.3-codex | 3,400 | 8 | 99% > 50 TPS |
| gpt-5、gpt-5.1 / gpt-5-mini | 4,750 / 23,750 | 8 | 99% > 50 / 80 TPS |
| gpt-4.1 / mini / nano | 3,000 / 14,900 / 59,400 | 4 | 99% > 80 / 90 / 100 TPS |
| gpt-4o / gpt-4o-mini | 2,500 / 37,000 | 4 | 99% > 25 / 33 TPS |
| Llama-3.3-70B-Instruct | 8,450 | 4 | 99% > 50 TPS |
| DeepSeek V4 Pro / V4 Flash 0731 / v3.2（Fireworks on Foundry） | 100 / 1,400 / 833 | 未載明 | 99% > 50 TPS |
| GLM 5.3 / 5.2 / 5.1 / 5 / 4.7 | 1,050 / 325 / 500 / 167 / 1,667 | 未載明 | 99% > 50 TPS |
| Kimi K2.7 Code / K2.6 / K2.5 / K2 Thinking | 1,000 / 2,000 / 294 / 389 | 未載明 | 99% > 50 TPS |
| Qwen 3.5 397B / Qwen 3.8 27B / Qwen 3 32B | 2,125 / 6,300 / 8,000 | 未載明 | 99% > 50 TPS |
| gpt-oss-120b / gpt-oss-20b / MiniMax M3 | 10,800 / 40,000 / 2,650 | 未載明 | 99% > 50 TPS |

- 最小部署 15 PTU（DeepSeek V4 Pro 與 GLM 5.2 為 800 PTU）；有 PTU 配額不保證有容量 [PTU concepts](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/provisioned-throughput)。Microsoft 的文件沒有給目標使用率，做法是把 100% 當成限流點並開啟 spillover [Spillover](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/spillover-traffic-management)。

**Google Provisioned Throughput**（頁面更新 2026-10-01）[Provisioned Throughput supported models, updated 1 Oct 2026](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/supported-models)：

| 模型 | 每 GSU 的 tokens/s | output burndown | cached 輸入 burndown |
|---|---|---|---|
| Gemini 3.8 / 3.7 / 3.6 Flash | 675 | 5 | 0.1 |
| Gemini 3.5 Flash | 675 | 6 | 0.1 |
| Gemini 3.5 Flash-Lite | 3,360 | 9 | 0.1 |
| Gemini 3.1 Pro（Preview） | 500 | 6（輸入超過 200K 時為 9，輸入 × 2） | 0.1（0.2） |
| Gemini 2.5 Pro / 2.5 Flash | 650 / 2,690 | 8（超過 200K 時 12）/ 9 | 未列 |
| Claude Opus 5.5 / Opus 5 / Opus 4.8 | 261 / 210 / 210 | 5 | 0.05 / 0.1 / 0.1（cache write 1.25 或 2） |
| Claude Sonnet 5.5 / Sonnet 5 / Sonnet 4.6 | 525 / 350 / 350 | 5 | 0.1 |
| Claude Fable 5.1 / Haiku 4.5 | 105 / 1,050 | 5 | 0.025 / 0.1 |
| DeepSeek-V3.2、Kimi K2 Thinking | 1,680 | 4 | 未列 |
| GLM 5 / GLM 4.7 | 1,010 / 1,685 | 3 / 4 | 未列 |
| Qwen3 Coder 480B / Qwen3 235B / Qwen3-Next-80B | 1,010 / 4,035 / 6,725 | 4 / 4 / 8 | 未列 |
| gpt-oss-120b / gpt-oss-20b / MiniMax M2 | 11,205 / 14,405 / 3,360 | 4 | 未列 |

**其他平台的預設值：**

| 平台 | 預設或可購買的單位 | 來源 |
|---|---|---|
| OpenAI API | Tier 1–5 的 RPM / TPM：500 / 0.5M、5,000 / 1M、5,000 / 2M、10,000 / 4M、15,000 / 40M（gpt-6.1-sol、gpt-6-sol、gpt-5.6-sol、gpt-5.5、gpt-5 相同）；input 超過 1M TPM 後每 15 分鐘最多再增 50% | [GPT-6.1 Sol model page](https://developers.openai.com/api/docs/models/gpt-6.1-sol)、[OpenAI rate limits](https://developers.openai.com/api/docs/guides/rate-limits) |
| OpenAI Scale Tier（2026-10-05 重讀） | 以「token units」預購每分鐘 token，至少 30 天；GPT-5.5 每單位 50,000 TPM（input 與 output 合併，output 依牌價比加權）、每日 $750；較舊機型分列 input 與 output 單位（例：GPT-5.2 input 25,000 TPM $105、output 2,500 TPM $84）；TPM 以整點對齊的 15 分鐘區間平均計；99.9% uptime SLA | [OpenAI Scale Tier](https://openai.com/api-scale-tier/) |
| Azure standard（Global Standard；頁面更新 2026-08-20） | gpt-6.1-sol、gpt-6-sol、gpt-6-astra、gpt-5.6-sol、gpt-5.5：Tier 1–6 的 RPM / TPM 為 1,000 / 1M、2,000 / 2M、4,000 / 4M、7,000 / 7M、10,000 / 10M、15,000 / 15M；gpt-5 由 10,000 / 1M 到 450,000 / 45M；Data Zone Standard 為三分之一 | [Azure OpenAI quotas and limits](https://learn.microsoft.com/en-us/azure/foundry/openai/quotas-limits) |
| Google Standard PayGo（頁面更新 2026-10-02） | 依 30 日花費分 Tier 1–4：Gemini Pro 0.5M、1M、2M、10M TPM；Flash 與 Flash-Lite 2M、4M、10M、50M；沒有 RPM 上限。Priority PayGo 的基準是 10M 與 50M | [Standard PayGo](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo)、[Priority PayGo](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/priority-paygo) |
| Databricks pay-per-token（Enterprise workspace；頁面更新 2026-10-02） | ITPM / OTPM / 每小時 queries：Claude Opus 5.5、Sonnet 5.5、GPT-6 系列等 1M / 100K / 360,000；GLM 5.3、DeepSeek V4.1 Flash、Kimi K3 為 2M / 40K；DeepSeek V4 Pro 為 200K / 4K / 7,200 | [Databricks limits](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/limits) |
| Cerebras | Developer tier：gpt-oss-120b 1M uncached TPM、3M total TPM、1,000 RPM；qwen-3.8-27b 150K、750K、300；Enterprise 依組織佈建 | [Cerebras rate limits](https://inference-docs.cerebras.ai/support/rate-limits) |
| Groq | 單位為 RPM、RPD、TPM、TPD，可另設 ITPM / OTPM；頁面所列 gpt-oss-120b 與 qwen3.8-27b 為 30 RPM、8K TPM。頁面文字稱這是 Developer plan 的 base limits，數值卻像免費方案 | [Groq rate limits](https://console.groq.com/docs/rate-limits) |

**各平台怎麼計 cache read、output 與 `max_tokens`：**

| 平台 / 配額 | cache read | output 權重 | `max_tokens` 在入場時 | 超過時 |
|---|---|---|---|---|
| Anthropic API | 不計（Haiku 3.5 例外） | 1×，獨立的 OTPM | 不計；ITPM 在請求開始時估計、之後修正 | 429 與 `retry-after`；流量急升另有未量化的 acceleration limits |
| Bedrock runtime | 不計 | Claude 5×、10× 或 15×；GPT-5.6 10×；其餘 1× | 先扣「輸入 + `max_tokens`」，結束時回補；未設時取模型上限（Claude Sonnet 為 64,000） | 429 ThrottlingException（503 是容量問題，不是配額） |
| Bedrock mantle | 不計 | 1×，獨立的 output TPM | 以「輸入 + `max_tokens`」對 input TPM 檢查 | 入場時 429；生成中途碰到 output 配額即停止 |
| Azure standard | 所讀頁面未載明 | 1× | 計入：以 prompt + `max_tokens` 估計 | 429 與 `retry-after-ms`；RPM 以 1 或 10 秒切片評估 |
| Azure PTU | 不計（GPT-6 系列權重 0.1） | 4–8×（GPT-6 系列 5–7.5） | 以 prompt（扣除 cached）+ `max_tokens` 估計，完成時修正 | 使用率 100% 時 429，或 spillover 到 standard |
| OpenAI API | 查無公開資料 | 1× | 計入：取 `max_tokens` 與依字元數估計值的較大者 | 429；失敗的請求也計入每分鐘上限；流量爬升過快回 `slow_down` |
| Google PT | 權重 0.025–0.2 | Gemini 與 open models 3–9×；Claude 5× | 入場時估計輸出大小，事後對帳 | 溢到 PayGo；header 設為 `dedicated` 時 429 |
| Databricks pay-per-token | 未載明 | 1×，獨立的 OTPM | 先以 `max_tokens` 對 OTPM 預扣，差額回補 | 429 |
| Cerebras | 只計入 total bucket | 1× | 估計值 = 輸入 + `max_completion_tokens` | 429 並指明是哪個 bucket |
| Groq | 不計 | 1× | 未載明 | 429 與 `retry-after` |

- 來源：[Anthropic rate limits](https://platform.claude.com/docs/en/api/rate-limits)、[How tokens are counted in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html)、[AWS ML blog](https://aws.amazon.com/blogs/machine-learning/optimize-your-applications-for-scale-and-reliability-on-amazon-bedrock/)、[Bedrock mantle quotas](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html)、[Azure quota how-to (classic), updated May 2026](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/quota)、[Operate provisioned deployments](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-get-started)、[OpenAI rate limits](https://developers.openai.com/api/docs/guides/rate-limits)、[Use Provisioned Throughput](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput)、[Databricks limits](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/limits)、[Cerebras rate limits](https://inference-docs.cerebras.ai/support/rate-limits)、[Groq rate limits](https://console.groq.com/docs/rate-limits)。OpenAI Scale Tier、Google Standard PayGo 與 Gemini API 的頁面沒有載明這三項。
- AWS 的例子：TPM 配額 2M、輸入 500 tokens，`max_tokens` 設 1,000 時每分鐘可入場約 1,333 個請求，不設（預設 64,000）時約 31 個 [AWS ML blog](https://aws.amazon.com/blogs/machine-learning/optimize-your-applications-for-scale-and-reliability-on-amazon-bedrock/)。
- 筆記的換算例 [D]：每分鐘 100 次 coding agent 呼叫（每次 10,000 未快取輸入、59,700 cache read、543 輸出）是全部 token 7.02M TPM；Anthropic 計 1.0M ITPM + 54K OTPM，Bedrock 計 1.27M（5×）、1.54M（10×）、1.81M（15×），Azure gpt-6.1-sol 為 623 PTU，Google 的 Claude Opus 5.5 為 101 GSU。全部 token ÷ 平台計量是 3.8–7.0。

### (g) 企業如何切分共用配額

共同的做法是「組織 → team 或 workspace → 使用者 → key」的階層，各層獨立設限、取最嚴者 [B]。供應商原生的機制：

- Anthropic：workspace 可設花費與 rate limit；預設 workspace 不能設；組織上限永遠適用，workspace 沒用完的份額其他 workspace 可用 [Anthropic rate limits](https://platform.claude.com/docs/en/api/rate-limits)。
- OpenAI：限制在 organization 與 project 層級；每位使用者的上限交給應用程式自己做 [OpenAI rate limits](https://developers.openai.com/api/docs/guides/rate-limits)。
- Azure：TPM 配額分配到 deployment（240K TPM 可做成 1 個 240K 或 2 個 120K 的 deployment）[Azure quota how-to (classic), updated May 2026](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/quota)。
- Bedrock：配額在帳號與 Region 層級共用。AWS 列的選項：分 AWS 帳號（多數組織的建議做法）、application inference profile、集中式 rate limiting 服務、reserved capacity [AWS ML blog](https://aws.amazon.com/blogs/machine-learning/optimize-your-applications-for-scale-and-reliability-on-amazon-bedrock/)；inference profile 只做成本與用量追蹤，不做限流 [Bedrock inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)。
- Google：PayGo 的 tier 在 organization 層級；PT 綁定 project、Region、模型與版本 [Standard PayGo](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo)、[Calculate Provisioned Throughput requirements](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/measure-provisioned-throughput)。

| Gateway | 限制的對象與單位 | 計數時點 | 值得注意的行為 | 來源 |
|---|---|---|---|---|
| LiteLLM proxy | key、使用者、team、team 成員、end-customer；TPM、RPM、平行請求數、USD 預算；TPM 預設計 total tokens | 入場預扣，事後對帳；沒有 `max_tokens` 時用靜態估計（建議取約 p95） | 用量低於飽和門檻時任何 key 可借用閒置容量，超過後各 priority 回到保留份額；門檻在實作的 README 是 0.80，文件範例是 0.50 | [LiteLLM budgets and rate limits](https://docs.litellm.ai/docs/proxy/users)、[LiteLLM dynamic TPM/RPM allocation, updated 3 Oct 2026](https://docs.litellm.ai/docs/proxy/dynamic_rate_limit)、[LiteLLM dynamic rate limiter v3 README](https://github.com/BerriAI/litellm/blob/main/litellm/proxy/hooks/README.dynamic_rate_limiter_v3.md) |
| Envoy AI Gateway | 每個 tenant header 與模型；InputToken、CachedInputToken、OutputToken、TotalToken，或以 CEL 加權（例：cached 0.1、輸出 1.5） | 回應完成後才計 | 1,000 tokens 的上限下，已入場的請求仍可串流 1,200 tokens；`Shared` 模式要所有 bucket 用盡才拒絕；預設 fail open | [Envoy AI Gateway usage-based rate limiting, repo commit 2 Oct 2026](https://github.com/envoyproxy/ai-gateway/blob/main/site/docs/capabilities/traffic/usage-based-ratelimiting.md)、[Envoy AI Gateway quota policy](https://github.com/envoyproxy/ai-gateway/blob/main/site/docs/capabilities/traffic/quota-policy.md) |
| Kong AI Gateway（enterprise plugin） | consumer、group、IP、header、模型、provider；total、prompt、completion tokens 或 cost | 事後計，成本在下一個請求才反映 | 文件的分層設計：每使用者上限分三級（每 60 s 0.05、0.10、0.20 cost units）、組織共用池 0.35、個人硬上限 0.02，全部同時適用 | [Kong AI Rate Limiting Advanced](https://github.com/Kong/developer.konghq.com/blob/main/app/_kong_plugins/ai-rate-limiting-advanced/index.md)、[Kong tiered AI budgets how-to](https://github.com/Kong/developer.konghq.com/blob/main/app/_how-tos/ai-gateway/enforce-tiered-ai-budgets-with-kong-identity.md) |
| Portkey | provider、workspace、API key、metadata（如 user）；請求數或 token，另有成本或 token 預算 | 筆記未記載 | 範例：每使用者 100 RPM、每使用者每月 $50、每個 workspace 每模型 100,000 TPM | [Portkey workspace budgets and rate limits](https://github.com/Portkey-AI/docs-core/blob/main/aigw/product/administration/enforce-workspace-budget-and-rate-limits.mdx)、[Portkey usage and rate limit policies](https://github.com/Portkey-AI/docs-core/blob/main/aigw/product/enterprise-offering/budget-policies.mdx) |
| Apigee LLMTokenQuota | API product、developer、app 與模型；分鐘到月 | 由回應計 token | 另有 PromptTokenLimit policy 處理秒級尖峰 | [Apigee LLMTokenQuota policy, updated 1 Oct 2026](https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/llm-token-quota-policy) |
| Azure API Management `llm-token-limit` | 任意 key（subscription、IP、user）；TPM（超過回 429）與 token 配額（超過回 403） | 可選擇預估 prompt tokens | 併發的請求可短暫超過上限；計數器以 gateway Region 為單位，不是全域 | [Azure API Management llm-token-limit](https://learn.microsoft.com/en-us/azure/api-management/llm-token-limit-policy) |
| Claude apps gateway（Anthropic；自建） | 使用者、IdP group、組織；每日、每週、每月的花費上限 | 筆記未記載 | group 與組織的上限是「每個席次的預設值」，不是共用池；優先序為使用者覆寫、最嚴的 group、組織預設；超過回 429 | [Claude apps gateway spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits) |
| AWS 的 Claude Code on Bedrock 指引 | 使用者、group（JWT claims）、預設；每月與每日的 token 或金額 | 在 credential 層、呼叫 Bedrock 之前檢查；用量每 15 分鐘更新 | 80%、90%、100% 告警；repo 已是維護模式，建議新部署改用 Claude apps gateway | [QUOTA_MONITORING.md](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/QUOTA_MONITORING.md) |

公布的每使用者或每 team 數值（都是預設值或文件範例，不是量測）：

| 來源 | 數值 | 性質 | 等級 |
|---|---|---|---|
| AWS 的 Claude Code 指引 [QUOTA_MONITORING.md](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/QUOTA_MONITORING.md) | 每使用者每月 225M tokens、每日 8.25M；範例：每使用者 $50 / 月、每 team $10 / 日 | 每人上限的預設值 | C |
| Claude apps gateway [Claude apps gateway spend limits](https://code.claude.com/docs/en/claude-apps-gateway-spend-limits) | 組織預設每位開發者 $500 / 月；外包人員的 group $100 / 日 | 範例 | C |
| LiteLLM [LiteLLM budgets and rate limits](https://docs.litellm.ai/docs/proxy/users) | 每個 key「$10/day AND $100/month」；每位工程師「$200 monthly Opus budget」 | 範例 | C |
| Portkey [Portkey usage and rate limit policies](https://github.com/Portkey-AI/docs-core/blob/main/aigw/product/enterprise-offering/budget-policies.mdx) | 每使用者 100 RPM；$50 / 月 | 範例 | C |
| Kong [Kong AI Rate Limiting Advanced](https://github.com/Kong/developer.konghq.com/blob/main/app/_kong_plugins/ai-rate-limiting-advanced/index.md) | consumer group 每 60 s 100、每 3,600 s 1,000 | 範例 | C |
| Azure API Management [Azure API Management llm-token-limit](https://learn.microsoft.com/en-us/azure/api-management/llm-token-limit-policy) | 每個來源 IP 5,000 TPM；每個 subscription 每月 100,000 tokens | 範例 | C |

Anthropic 的 Claude Code 建議表全文（2026-10-04 取得）[Claude Code docs: Manage costs effectively](https://code.claude.com/docs/en/costs)：

| 團隊人數 | 每使用者 TPM | 每使用者 RPM | 相對 1–5 人列的比例 [D] |
|---|---|---|---|
| 1–5 | 200K–300K | 5–7 | 100% |
| 5–20 | 100K–150K | 2.5–3.5 | 50% |
| 20–50 | 50K–75K | 1.25–1.75 | 25% |
| 50–100 | 25K–35K | 0.62–0.87 | 12% |
| 100–500 | 15K–20K | 0.37–0.47 | 7–8% |
| 500+ | 10K–15K | 0.25–0.35 | 5% |

- 這張表沒有定義 TPM（是否含 cache read 未說明），也沒有量測依據；每一列的 TPM ÷ RPM 都是 40.0K–42.9K tokens / 請求 [D]。文件的範例是 200 位使用者 × 20K = 4M TPM，並說明人數越多、同時使用的比例越低。兩份筆記對這張表的等級不同：用量筆記標 C，容量筆記標 B 並註明數值本身接近 C。
- 硬切配額的代價 [D，由 (e) 的多工曲線]：100 個 session 的 team 在自己的尖峰分鐘每個 session 需要約 19K tokens，60,000 個 session 的組織約 2.5K；每個 team 各給一份尖峰配額，需要合併配額的約 7.6 倍，1,000 個 session 的事業單位約 2.3 倍。
- 每人上限要容得下重尾：Copilot 每位使用者每週 prompt tokens 的 P90 ÷ 中位約 12 倍；單一 agent session 最忙的一分鐘，全部 token 中位約 130–140K、P90 640–770K，以「未快取輸入 + 輸出」計為 31–40K 與 163–169K [A，筆記實算]。
- 計數要跟供應商一致：gateway 預設計 total tokens，Anthropic 與 Bedrock 不計 cache read；cache 占 86–98% 的 agent 流量在 total-token 的 gateway 上會比供應商早約 4–7 倍被限流 [D]。事後計數的限流器在併發下會超量，最多到「在途數 × 每請求 tokens」[D]。
- 筆記建議的切法 [D]：組織層級一份以合併尖峰計的配額；事業單位的上限總和可以超過組織配額（2–8 倍），保證份額只在超過飽和門檻時生效；每人用遠高於平均的 rate limit 防失控，另設每日或每月預算；程式化與 batch 流量用獨立的 key 或 tier。大型企業實際設定的每人或每單位上限查無公開資料。

### (h) 公開的 sizing 方法

由人數直接算到容量的公開來源只有兩個：Anthropic 的建議表與開源的 llm-d Planner；其餘廠商都由「尖峰請求率 × 每請求 token」出發。

| 來源 | 輸入 | 公式或規則 | 尖峰與餘裕的處理 | 等級 |
|---|---|---|---|---|
| Azure PTU [PTU sizing](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing) | 模型、peak RPM、平均 prompt、平均 response、cache rate | normalized TPM = input TPM × (1 − cache rate) + 輸出權重 × output TPM；PTU = normalized TPM ÷ 每 PTU 的 input TPM | 例：1,000 RPM、200 輸入、20 輸出、gpt-5.2 → 110 PTU（cache rate 50% 時 80）；建議 benchmark 至少 10 分鐘 | B |
| Google PT [Calculate Provisioned Throughput requirements](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/measure-provisioned-throughput) | QPS、每 query 的輸入與輸出 | tokens/s = (輸入 + 輸出 × burndown) × QPS；÷ 每 GSU 的 tokens/s | 例：10 QPS、1,500 輸入、300 輸出、gemini-3.6-flash → 45 GSU；吞吐量不累積 | B |
| NVIDIA，GTC S62797（2024-02）[NVIDIA S62797 slides](https://developer-blogs.nvidia.com/wp-content/uploads/2024/08/S62797-LLM-Inference-Sizing_-Benchmarking-End-to-End-Inference-Systems.pdf) | 模型、平均輸入、平均輸出、尖峰每秒請求數、延遲上限 | 由平均求尖峰用 Poisson 分位：`poisson.ppf(0.95, 64)` = 77（+20%）；`poisson.ppf(0.95, 7)` = 12（+71%） | 地端以最大同時負載計；例：每人每日 3 次、8 小時工作日，1.5M 次請求 / 日對應 500K DAU | B |
| AWS Bedrock [AWS ML blog](https://aws.amazon.com/blogs/machine-learning/optimize-your-applications-for-scale-and-reliability-on-amazon-bedrock/) | 各應用的尖峰 RPM | 各應用的尖峰相加再加安全邊際：3,000 + 2,000 + 2,000 → 至少 7,000，實際申請約 8,000 RPM | 告警設在 RPM / TPM 配額的 80% | B |
| llm-d Planner（commit 2026-08-29）[traffic_profile.py](https://github.com/llm-d-incubation/llm-d-planner/blob/main/src/planner/specification/traffic_profile.py)、[usecase_slo_workload.json](https://github.com/llm-d-incubation/llm-d-planner/blob/main/src/planner/data/configuration/usecase_slo_workload.json) | 使用者數、active fraction、每位活躍使用者每分鐘請求數、peak multiplier | peak RPS = 使用者 × active fraction × 每分鐘請求數 ÷ 60 × peak multiplier | 預設值：chatbot 0.20、0.4、2.0；code completion 0.25、2.0、2.5；RAG 0.20、1.0、2.5；沒有附資料來源 | C |
| 電信話務的範本 [Erlang (unit)](https://en.wikipedia.org/wiki/Erlang_(unit)) | N 位使用者、每人每日 U 次、busy hour 集中係數 C、持有時間 h 分鐘 | E = N · U · C · h ÷ 60 erlangs | Erlang B / C；壅塞而反覆重試時公式失準 | A |

- llm-d 的 chatbot 預設相當於每位使用者每分鐘 0.08 次請求；BurstGPT 的服務在 busy hour 約 248 次請求、超過 3,000 位使用者，約每人每分鐘 0.0014 次，低 60 倍 [D]。這類參數必須來自用量資料，不能直接用 planner 的預設。
- 排隊模型對 agent 流量偏樂觀：解析模型在 chatbot 工作負載比模擬保守 8–14%，在 agent 工作負載失準（24 顆 H100、每秒 20 個請求、使用率約 30%，Erlang-C 判定足夠，模擬的 P99 TTFT 為 1,052 ms）[A，模擬研究] [inference-fleet-sim](https://arxiv.org/abs/2603.16054)。

## 已知缺口

筆記列出的缺口中，直接觸及模型參數的有 16 項；三個角色的佐證強度依序是 coding、OA、R&D，R&D 的 14 列參數中只有 1 列是量測值。

| 缺口（筆記查無公開資料，或來源未揭露） | 影響的參數 | 對信心的影響 |
|---|---|---|
| ChatGPT Enterprise、Claude Enterprise / Team、M365 Copilot、Gemini in Workspace 的每席次每日絕對訊息數或 token 數 | OA 的 r、u、c、o | OA base 的 r 是「消費者 DAU 的估計 × 企業成長率」；量級可信，數值不可信。 |
| 企業 chat 輸入中 cache read 的占比 | OA 的 c | base 的 50% 是假設；純 OA 的未快取輸入 TPM 因此有 0.4–2.0 倍的不確定，組合 B 只有 ±5%。 |
| 2025–2026 年企業 chat 助理的每請求 token 分布（Azure 的 trace 是 2023–2024、受 8K context 限制） | OA 的 u + c、o | base 的 3,500 由 API 聚合平台推得；reasoning 占輸出的比例沒有絕對值。 |
| 帶時間戳的 2025–2026 年企業 chat trace | OA 流量的 s、k、w | OA 的尖峰形狀用區域性服務與全球混合的 trace 代替。 |
| 同時有使用者識別與組織邊界的 trace | s、k、warm session 係數 | 「尖峰同時使用者 ÷ 員工數」無法直接量；多工曲線用的是 session，不是使用者。 |
| 月底、release、假期等季節性的 trace | d | 只有 BurstGPT 一個站點的 1.20–1.80，模型取下緣。 |
| Anthropic「每活躍日 $13」的方法、樣本與模型組合 | coding 的 r（base、high） | 換成 token 有 1.7 倍的範圍。 |
| 企業版 Copilot 的每席次用量（公開樣本是非企業使用者） | coding 全部 | 每次呼叫的形狀可信；企業母體的平均值未知。 |
| OpenAI 與 Anthropic 的 deep research 每 run token；每位使用者實際的 run 數；Kosmos 類科學 agent 的 token；研發組織的席次遙測 | R&D 全部 | R&D 的數字是情境，不是估計。 |
| 廠商公布的目標使用率（只有 80% 的告警範例） | 使用率上限 0.80 | 類比值。 |
| Bedrock：Sonnet 5.5 的 burndown；DeepSeek V4、GLM 5.1–5.3 的配額列；Kimi K3 以外的 open-weight 模型有無 prompt caching | Bedrock 的換算與配額倍數 | Sonnet 池的倍數可能是 3.35 或 4.69；三個 open-weight 池的 100M 是借用值，且計量可能是 U + C + O。 |
| Bedrock「Cross-Model Max Tokens Per Day」700M 與 TPM 配額如何互動 | Bedrock 的配額對照 | 模型只檢查 TPM。10,000 人、組合 B、base 的平日「未快取輸入 + 輸出」已有 0.94B tokens [D]，超過 700M；這個上限的計法與適用範圍需向 AWS 確認。 |
| GLM-5.x 與 DeepSeek V4 的 FP8 / FP4 KV 格式確切 bytes；Kimi K3 每個 session 保留幾份 recurrent state | KV bytes、每序列 state | hot 與 warm KV 是下限（GLM 的引擎預算比公式高 1.7 倍）。 |
| GLM-5.3 或 Kimi K3 在 agentic trace 上、不固定 acceptance 的獨立多節點量測 | output tokens/s per GPU | GPU 數是下限。 |
| 企業 chat 與 R&D 呼叫的時間量測；含 reasoning 的首 token 時間 | 三個角色的 TTFT 與 W | 只有 coding agent（Copilot 平均 11.9 s）與 2023–2024 的 chat（BurstGPT 7.0 s）可對照；frontier API 的 latency p50 是 1.1–4.6 s，模型的 1.0–2.5 s 在下緣，在途數可能偏低。 |
| 大型企業實際設定的每人或每單位上限；由員工數出發的 hyperscaler 範例 | gateway 切分；整條計算鏈 | 沒有官方範本可對照，模型的連乘鏈是本文的組合。 |

三個角色的佐證強度：

| 排名 | 角色 | 有量測支持的部分 | 靠判斷的部分 | 讀法 |
|---|---|---|---|---|
| 1 | coding | 每次呼叫的形狀有四個獨立來源（Copilot 3.2M 位使用者、TraceLab 43 人、Pegatron 1 人、Ant 平台）；每活躍日 token 有 Anthropic 的金額、AWS 的預設上限與 Meta 的總量可交叉 | a 的 low；r 由金額換算；企業母體的平均；TTFT | base 落在 13–23M tokens / 活躍日的換算範圍內；17 列中 2 列是判斷值。 |
| 2 | OA | 活躍占比有兩個 A 級來源；每請求 token 有 2023–2024 的 trace；訊息數有消費者資料 | 企業的絕對訊息數；cache read 占比；high（office agent）的全部參數；TTFT | low 與 base 的量級可信；high 是情境。OA 只占組合 B 全部 token 的 1.1%，誤差對總量影響小，對純辦公型組織影響大。 |
| 3 | R&D | 每 run 的大小（只有 Google 一家的估計）、PDF 每頁 token、學術研究者每日使用 28% | run 數、文件請求數、cache read 占比、每 run 的呼叫數、週末係數、TTFT | 當作情境使用。R&D 升到 high 是 RPM 最大的推力（3.46 倍，見第 10 章），這一項的不確定性直接進入 RPM 與輸出 TPM。 |

- 在地適用性：韓國與台灣企業的全公司導入用量查無公開資料；台灣唯一的證據是 Pegatron 的單一開發者研究。
- 每席次 token 的年成長沒有任何廠商公布，只能由訊息成長 × 每請求 token 成長組合；多年期規劃不能用固定的每席次假設。
- 讀取方式的限制：OpenAI Scale Tier、Kimi、Z.ai、DeepSeek 的價格頁經摘要工具讀取，引用前需重查；trace 統計的腳本與輸出存在 session 的暫存區，不會保留。

## 網站呈現建議

- **佐證總表做成可篩選的矩陣。** 94 列依群組、等級（A / B / C / D）與性質標記（量測值、範圍內取值、換算值、判斷值等）篩選，每列可展開看來源與落差；第 10 章計算器的每個輸入連到對應的列，判斷值另外標色。
- **模型值對證據範圍畫成區間圖。** 每個參數一條橫線（線段是證據的範圍，點是模型值），可看出取在下緣（如 d）、中點（如 s）或沒有範圍可依（如 TTFT）。
- **trace 的圖。** 多工曲線用雙對數折線（x 為每日 session 數，y 為每個 session 的尖峰分鐘 token），疊上 Anthropic 建議表的六個點；busy-hour 占比用點圖分「單一站點」與「全球」兩群，標出模型取的 0.11 與 0.065。
- **平台配額做成可排序的表。** 平台 × 模型 × 預設 TPM / RPM / burndown，另一張比較矩陣列出 cache read、output 權重與 `max_tokens` 預扣；每列標示讀取日期 2026-10-04，經摘要工具讀取的項目加「需重查」。
- **已知缺口做成獨立頁面。** 依角色分組，連回佐證總表的判斷值列；角色的佐證強度放頁首。
- **可以刪的。** 總量層級的表只留 Meta 與 Copilot 兩列；方案額度移到註腳；PTU 與 GSU 的完整表收進可展開的區塊。
