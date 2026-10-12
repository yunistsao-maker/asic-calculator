# 第 10 章 用量模型與 TPM / RPM 容量規劃

資料日:2026-10-04。本章的模型數字全部是 `calc/capacity_model.py` 的輸出(等級 D,算式列在第一節);公開證據的逐項出處與等級在第 11 章。

## 估算方法與公式

從員工數到尖峰 RPM / TPM 是一條連乘鏈;以 100,000 人、角色組合 B、base 用量、單一時區為例,結果是尖峰 4,764 RPM、未快取輸入 24.5M TPM、cache read 212M TPM、輸出 3.13M TPM,同時在途請求 779(99.9% 為 865)[D]。同一份流量換成各平台自己的「TPM」定義後相差 3.4–9.8 倍,要申請的數字必須照平台的計法算。

### 計算鏈

角色 i 的平日呼叫數,由員工數、角色占比、活躍占比與每活躍日呼叫數相乘:

```latex
C_i = N \cdot p_i \cdot a_i \cdot r_i
```

busy hour(一日中最忙的一小時)的平均每分鐘請求數,以 P95 平日計:

```latex
m_i = \frac{C_i \cdot s}{60} \cdot d
```

共用同一個端點或同一份配額的流量先加總,再套尖峰分鐘係數:

```latex
m = \sum_i m_i
```

```latex
k = \max\left(1.15,\ 1 + \frac{3}{\sqrt{m}}\right)
```

```latex
\mathrm{RPM}_{\mathrm{peak}} = m \cdot k
```

三類 token 的尖峰 TPM(x 分別代入 u、c、o):

```latex
\mathrm{TPM}_x = k \cdot f_x \cdot \sum_i m_i \cdot x_i
```

一次呼叫的總時間與同時在途請求數:

```latex
W_i = \mathrm{TTFT}_i + \frac{o_i}{v}
```

```latex
L = \sum_i \frac{m_i \cdot k}{60} \cdot W_i
```

```latex
L_{99.9} = L + 3.1 \sqrt{L}
```

每授權席次的平日、每週、每月 token(w 為週末係數):

```latex
T_{\mathrm{weekday}} = a \cdot r \cdot (u + c + o)
```

```latex
T_{\mathrm{week}} = T_{\mathrm{weekday}} \cdot (5 + 2w)
```

```latex
T_{\mathrm{month}} = T_{\mathrm{week}} \cdot \frac{52.14}{12}
```

| 符號 | 意義 | 預設值 | 依據 |
|---|---|---|---|
| N、p_i | 員工數(每位員工一個授權席次);角色 i 的人數占比 | 情境輸入 | 八種角色組合是情境設定,不是量測 |
| a | 平日有使用的授權席次占比 | 12%–75%,依角色與用量級 | 見「每人用量基準」;逐項佐證在第 11 章 |
| r | 每位活躍使用者每個活躍日的模型呼叫數(全體平均) | 4–540 | 同上 |
| u、c、o | 每次呼叫的未快取輸入(含 cache write)、cache read 輸入、輸出(含 reasoning)tokens | 依角色與用量級 | 同上 |
| s | busy-hour 占比:平日最忙一小時占全日請求的比例 | 0.11(單一時區);0.065(全球分散) | 單一站點 10.6–12.4%、9.3%;全球混合 5.2–5.8%、6.8–7.0% [A,筆記實算] [BurstGPT](https://github.com/HPMLL/BurstGPT)、[Azure 2024 trace](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md)、[Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) |
| d | P95 平日 ÷ 平均平日 | 1.2 | BurstGPT 三個檔為 1.20、1.28、1.80(60–110 天)[A,筆記實算] [BurstGPT](https://github.com/HPMLL/BurstGPT) |
| k | 尖峰分鐘 ÷ busy hour 的平均分鐘 | max(1.15, 1 + 3 ÷ √m) | 大流量 trace 為 1.09–1.30;每分鐘 4–5 個請求時中位 2.4–2.5 [A,筆記實算;公式為 D] |
| f_u、f_c、f_o | token 尖峰相對請求尖峰的修正 | 1.18、1.04、1.06 | Copilot busy hour 內:未快取輸入 1.29、全部 token 1.13、輸出 1.15,呼叫數 1.09 [A,筆記實算] |
| TTFT_i | 估算呼叫時間用的 TTFT | OA 1.0 s;coding 2.0 s;R&D 2.5 s | 判斷值,無直接量測 |
| v | 每條串流的輸出速度 | 80 tokens/s | 判斷值;Azure PTU 的延遲目標為 99% 高於 40–100 tokens/s [B] [PTU sizing](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing) |
| 3.1 | 99.9% 的 Poisson 分位係數 z | 3.1 | Copilot busy hour 量到 p99.9 ÷ 平均 1.12–1.20,Poisson 為 1.16–1.18 [A,筆記實算] |
| w | 週末日相對平日的量 | OA 0.45;coding 0.25;R&D 0.35 | chat trace 0.36–0.57;coding trace 0.21–0.32;R&D 為判斷值 |

### 為什麼這樣建模

**用全體平均,不用中位數使用者。** 用量分布重尾:Copilot coding agent 每位使用者每週的 prompt tokens 中位數 3.2M、平均 14.0M(44.9T ÷ 3.2M 人)、P90 38M(2026-06 第一週)[A] [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101);OpenAI 的企業資料中 P95 員工的訊息量是中位數的 6 倍(2025-12)[B] [OpenAI, The state of enterprise AI 2025](https://cdn.openai.com/pdf/7ef17d82-96bf-4dd1-9df2-228f7f377a29/the-state-of-enterprise-ai_2025-report.pdf)。容量等於人數乘平均值,拿中位數乘人數會低估約 4.4 倍(14.0M ÷ 3.2M)。所以 r、u、c、o 一律定義為「活躍使用者日的全體平均」,low、base、high 是三種全體平均的情境,不是使用者的百分位。

**busy-hour 占比 s。** s 把一日的量壓到最忙的一小時:完全平坦的一日是 4.2%(1 ÷ 24),單一時區取 0.11 等於 busy hour 的速率是 24 小時平均的 2.64 倍,全球分散取 0.065 則為 1.56 倍 [D:24 × s]。量測值:單一站點的聊天服務 10.6–12.4%(BurstGPT,超過 3,000 位使用者,2023–2024)、以美國為主的 code completion 9.3%(Azure,2024-05);全球混合的 Azure conversation 5.2–5.8%、Copilot agent 6.8–7.0%(2026-06)[A,筆記實算]。

**P95 平日係數 d。** 一週的 trace 看不到日與日之間的波動;BurstGPT 60–110 天的資料中,P95 平日是平均平日的 1.20–1.80 倍。模型取 1.2,所以所有尖峰值都是「P95 平日」的尖峰。月底、release 週等季節性沒有任何公開 trace 涵蓋,另以 d = 1.5 做敏感度。

**尖峰分鐘係數 k 隨合併流量縮小。** 一分鐘內的到達數近似 Poisson,標準差是 √m,相對波動隨 1 ÷ √m 縮小,所以合併的流量越大、每人分到的尖峰越低。量測與公式對照:m ≈ 4.1 時尖峰分鐘是 busy hour 平均分鐘的 2.4–2.5 倍(BurstGPT 中位數),公式給 2.5;m ≈ 1,300 時量到 1.09–1.12(Copilot 取樣),公式給 1.08 [A,筆記實算]。下限 1.15 取自大流量 trace 的 1.09–1.30(到達的變異係數大於 1,實測值在 Poisson 下限之上);k 以「共用同一份配額的合併流量」計算,把流量拆到多個模型池時每池的 k 會升高。

**token 的尖峰比請求數更尖。** Copilot agent 在 busy hour 內的尖峰分鐘 ÷ 平均分鐘:呼叫數 1.09、全部 token 1.13、輸出 1.15、未快取輸入 1.29(cache miss 成批出現)[A,筆記實算] [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md)。模型取比值:f_u = 1.29 ÷ 1.09 = 1.18,f_c = 1.13 ÷ 1.09 = 1.04(以全部 token 代表 cache read),f_o = 1.15 ÷ 1.09 = 1.06。

**RPM 由到達決定,同時在途數由呼叫總時間決定。** RPM 只取決於人數、活躍占比、呼叫數與 s、d、k,與延遲無關;同時在途請求數依 Little's law 是到達率乘上一次呼叫的總時間 W,而 W = TTFT + 輸出 tokens ÷ 每條串流的速度。TTFT 不能單獨當服務時間:本例若以 TTFT 取代 W,在途數會由 779 算成 164,低估 4.8 倍;反過來用「同時連線數 ÷ TTFT」回推 RPM,則高估 4.8 倍 [D]。agent 的工具執行時間不計入 W,因為工具在兩次呼叫之間執行。

**Little's law 在 trace 上成立。** Copilot agent 整週量到的平均在途呼叫數 179.5,λW = 15.38/s × 11.88 s = 182.7(差 1.8%);最忙的八個小時量測值是 λW 的 1.00–1.12 倍 [A,筆記實算] [Copilot agent trace](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md)、[Little's law](https://en.wikipedia.org/wiki/Little%27s_law)。模型的 L 以尖峰分鐘的到達率(m × k)計算,是「P95 平日尖峰分鐘內」的在途數;busy hour 的平均在途數是 L ÷ k。

**Poisson 餘裕。** 99.9% 的在途數取 L + 3.1√L:Copilot 平日 busy hour(平均在途 328–398)量到的 p99.9 ÷ 平均是 1.12–1.20,同均值的 Poisson 是 1.16–1.18 [A,筆記實算]。小規模不能用倍數:BurstGPT 的站點在最高併發的小時平均在途約 0.5,實測 p99.9 為 13、最多到達的小時為 10,Poisson 只有 4,這種規模應直接用絕對併發數(該站每日最大併發中位 4、P90 9、最大 18)[A,筆記實算] [BurstGPT](https://github.com/HPMLL/BurstGPT)。程式化的 API / batch 流量不服從 Poisson(p99 為 66–71,Poisson 為 13–15),應給獨立的 key 或 tier。

**模型沒有算進去的三件事。** 被限流的請求會重試(Azure 與 OpenAI 的 SDK 預設重試 2 次),配額剛好等於量測尖峰時,送達的負載會高於量測值 [B] [OpenAI rate limits](https://developers.openai.com/api/docs/guides/rate-limits)。用量逐年成長:聊天的每席次用量每年增加 30–100% [D],企業的 token 用量在 2025-01 至 2026-04 之間成長 1,001% [B] [Ramp](https://ramp.com/blog/ai-token-cost-for-businesses)。`max_tokens` 的入場預扣見下一小節。

### 「TPM」不是單一數量

平台在四件事上不同:cache read 是否計入、output 的權重、`max_tokens` 是否在入場時預扣、執行的時間視窗。同一份流量(上例)的全部 token 是 240M TPM,Anthropic 計 24.5M ITPM 加 3.13M OTPM,Bedrock 對 Opus 5.5 計 55.8M TPM [D]。

| 平台 / 配額 | 計入的 token | cache read | output 權重 | `max_tokens` 入場預扣 | 視窗與演算法 | 等級 | 來源 |
|---|---|---|---|---|---|---|---|
| Anthropic API | ITPM = 未快取輸入 + cache write;OTPM 另計;RPM | 不計(Haiku 3.5 例外) | 1×,獨立 bucket | 不預扣;ITPM 在請求開始時估計、之後修正 | token bucket,連續補充;60 RPM 可能以每秒 1 個請求執行 | B | [Anthropic rate limits](https://platform.claude.com/docs/en/api/rate-limits) |
| Bedrock runtime | 單一 TPM:輸入 + cache write + 輸出 × burndown;部分模型另有 RPM;另有每日 token 上限 | 不計 | Claude 5×、10× 或 15×;GPT-5.6 10×;其餘 1× | 入場先扣「輸入 + `max_tokens`」,過程中調整,結束時回補 | 每分鐘配額(AWS 部落格描述為 60 秒視窗) | B | [How tokens are counted in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html) |
| Bedrock mantle | input TPM 與 output TPM 分開;無 RPM | 不計 | 1×,獨立 bucket | 入場以「輸入 + `max_tokens`」(未設則取模型上限)對 input TPM 檢查 | 每分鐘 | B | [Bedrock mantle quotas](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-mantle.html) |
| Azure standard 部署 | 以估計 token 計的 TPM;RPM 與 TPM 成固定比例 | 所讀頁面未載明 | 1× | 計入:收到請求時以 prompt + `max_tokens` 估計 | token 計數每分鐘重置;RPM 以 1 或 10 秒切片評估 | B | [Azure quota how-to (classic), updated May 2026](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/quota) |
| Azure PTU | 已部署 PTU 的使用率 | 不計(GPT-6 系列權重 0.1) | 4–8×(GPT-6 系列 5–7.5) | 以 prompt(扣除 cached)+ `max_tokens` 估計,完成時修正 | leaky bucket 的變形,連續排空 | B | [Operate provisioned deployments](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-get-started) |
| OpenAI API | RPM、TPM(另有 RPD、TPD),依 organization 與 project | 查無公開資料 | 1× | 計入:取 `max_tokens` 與依字元數估計值的較大者 | 每分鐘;約 1M input TPM 以上另有爬升速率限制 | B | [OpenAI rate limits](https://developers.openai.com/api/docs/guides/rate-limits) |
| OpenAI Scale Tier | 預購的「token units」:新機型(GPT-5.4、GPT-5.5)是 input 與 output 合併的 TPM;較舊機型分列 input 與 output 單位 | 查無公開資料 | 合併單位中 output 依牌價比加權(GPT-5.4 為 6×);分列單位為獨立 bucket | 頁面未記載 | 以整點對齊的 15 分鐘區間平均 | B(2026-10-05 重讀) | [OpenAI Scale Tier](https://openai.com/api-scale-tier/) |
| Google Standard PayGo | 每模型、organization 層級的基準 TPM;無 RPM | 未載明 | 未載明 | 筆記未記載 | 每分鐘;超過基準的部分為 best-effort | B | [Standard PayGo](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/standard-paygo) |
| Google PT | burndown 後的 tokens/s(每 GSU) | 權重 0.025–0.2 | Gemini 與 open models 3–9×;Claude 5× | 入場估計輸出大小,事後對帳 | 動態視窗:3 GSU 以下 40–120 秒;50 GSU 以下 5–30 秒;50 GSU 以上 1–5 秒 | B | [Use Provisioned Throughput](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput) |
| Gemini API | RPM、input TPM、RPD(每 project);每 10 分鐘的花費上限 | 未載明 | 輸出不計入 TPM | 筆記未記載 | 每分鐘;花費以滾動 10 分鐘視窗 | B | [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) |
| Databricks pay-per-token | ITPM、OTPM、每小時 queries | 未載明 | 1×,獨立 bucket | `max_tokens` 先對 OTPM 預扣,差額回補 | sliding window 加 token bucket | B | [Databricks limits](https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/limits) |
| Cerebras | 未快取 TPM 與 total TPM(未快取的 3 倍)、RPM | 只計入 total bucket | 1× | 估計值 = 輸入 + `max_completion_tokens` | token bucket,連續補充 | B | [Cerebras rate limits](https://inference-docs.cerebras.ai/support/rate-limits) |
| Groq | RPM、RPD、TPM、TPD;可另設 ITPM / OTPM | 不計 | 1× | 未載明 | 每分鐘 / 每日 | B | [Groq rate limits](https://console.groq.com/docs/rate-limits) |

把上例的三類尖峰 TPM(U = 24.5M、C = 212M、O = 3.13M)代入各平台的定義 [D;係數出處見第 11 章「平台單位」]:

| 平台單位 | 算式 | 結果 | 全部 token ÷ 平台計量 | 對照預設配額或備註 |
|---|---|---|---|---|
| 全部 token(不分類別) | U + C + O | 240M TPM | 1.0 | 只有 Cerebras 的 total bucket 這樣計 |
| Anthropic API | ITPM = U;OTPM = O | 24.5M ITPM + 3.13M OTPM | 9.8(對 ITPM) | Scale tier 10M ITPM 的 2.45 倍、2M OTPM 的 1.57 倍 |
| Bedrock runtime,burndown 5× | U + 5 × O | 40.1M TPM | 6.0 | Sonnet 4.6 預設 6M 的 6.7 倍 |
| Bedrock runtime,burndown 10× | U + 10 × O | 55.8M TPM | 4.3 | Opus 5.5 預設 30M 的 1.86 倍 |
| Bedrock runtime,burndown 15× | U + 15 × O | 71.4M TPM | 3.4 | Opus 4.8 預設 30M 的 2.38 倍 |
| Bedrock runtime,open-weight(1×) | U + O | 27.6M TPM | 8.7 | Kimi K3 預設 10M 的 2.76 倍;100M 類別的 0.28 倍 |
| Azure PTU(gpt-6.1-sol) | (U + 0.1 × C + 5 × O) ÷ 3,000 | 20,444 PTU | 3.9 | normalised TPM = 61.3M |
| Google GSU(Claude Opus 5.5) | (U + 0.05 × C + 5 × O) ÷ 60 ÷ 261 | 3,239 GSU | 4.7 | burndown 後 845K tokens/s |
| Google GSU(Gemini 3.8 Flash) | (U + 0.1 × C + 5 × O) ÷ 60 ÷ 675 | 1,514 GSU | 3.9 | burndown 後 1.02M tokens/s |
| Cerebras | 未快取 bucket = U + O;total bucket = U + C + O | 27.6M + 240M TPM | 8.7(對未快取 bucket) | total 是未快取的 8.7 倍,超過 3 倍的上限,total bucket 先滿 |

- **入場預扣。** 會預扣的平台,在途請求佔住的配額是併發 ×(輸入 + `max_tokens`),不是實際 token。AWS 的例子:3,000 輸入、1,000 cache write、1,000 輸出、`max_tokens` 32,000 的請求入場時扣 36,000,結算後為 9,000(5× burndown)[B] [How tokens are counted in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas-token-burndown.html)。以上例 99.9% 在途 865、同樣的 `max_tokens` 與實際輸出計,瞬間被佔住而未消耗的配額約 865 × 31,000 ≈ 26.8M tokens [D];Azure 的建議是把 `max_tokens` 設得盡量接近實際生成長度 [B] [Operate provisioned deployments](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-get-started)。
- **執行視窗。** 模型輸出的是尖峰分鐘值,對應 Anthropic(連續補充的 token bucket)與 Bedrock(每分鐘配額)的定義。Azure standard 以 1 或 10 秒切片檢查 RPM(600 RPM 的部署每秒超過 10 個請求即限流),要用尖峰秒估;OpenAI Scale Tier 以 15 分鐘平均計,應以尖峰 15 分鐘的平均估;Google PT 在 50 GSU 以上以 1–5 秒視窗執行 [B] [Azure quota how-to (classic), updated May 2026](https://learn.microsoft.com/en-us/azure/foundry-classic/openai/how-to/quota)、[OpenAI Scale Tier](https://openai.com/api-scale-tier/)、[Use Provisioned Throughput](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/provisioned-throughput/use-provisioned-throughput)。

## 每人用量基準

base 用量下,每個授權席次每月的 token 是 OA 350K、coding 168M、R&D 6.16M,一個 coding 席次等於 481 個 OA 席次 [D]。coding 的輸入 token 約 93% 是 cache read,換到不計 cache read 的平台後只剩約十三分之一。

每次呼叫的假設與活躍度(模型參數):

| 角色 | 用量級 | 平日活躍席次占比 a | 每活躍日呼叫數 r | 未快取輸入 u(tokens/呼叫) | cache read c(tokens/呼叫) | 輸出 o(tokens/呼叫) | cache read 占輸入 |
|---|---|---|---|---|---|---|---|
| OA | low | 12% | 4 | 900 | 100 | 125 | 10.0% |
| OA | base | 35% | 10 | 1,750 | 1,750 | 400 | 50.0% |
| OA | high | 50% | 30 | 3,000 | 9,000 | 800 | 75.0% |
| Coding | low | 30% | 20 | 5,000 | 63,000 | 250 | 92.6% |
| Coding | base | 45% | 170 | 6,500 | 85,000 | 600 | 92.9% |
| Coding | high | 75% | 400 | 8,500 | 120,000 | 700 | 93.4% |
| R&D | low | 28% | 26 | 2,615 | 1,615 | 615 | 38.2% |
| R&D | base | 40% | 100 | 2,500 | 3,000 | 720 | 54.5% |
| R&D | high | 55% | 540 | 2,640 | 6,805 | 611 | 72.0% |

每活躍使用者日,以及每授權席次的平日與每週(每席次 = 每活躍使用者日 × a;每週 = 平日 ×(5 + 2w)):

| 角色 / 用量級 | 呼叫數 / 活躍使用者日 | tokens / 活躍使用者日 | 呼叫數 / 席次 / 平日 | tokens / 席次 / 平日 | 呼叫數 / 席次 / 週 | tokens / 席次 / 週 |
|---|---|---|---|---|---|---|
| OA low | 4 | 4.5K | 0.48 | 540 | 2.83 | 3.19K |
| OA base | 10 | 39K | 3.5 | 13.6K | 20.7 | 80.5K |
| OA high | 30 | 384K | 15 | 192K | 88.5 | 1.13M |
| Coding low | 20 | 1.36M | 6 | 410K | 33 | 2.25M |
| Coding base | 170 | 15.7M | 76.5 | 7.05M | 421 | 38.8M |
| Coding high | 400 | 51.7M | 300 | 38.8M | 1.65K | 213M |
| R&D low | 26 | 126K | 7.28 | 35.3K | 41.5 | 201K |
| R&D base | 100 | 622K | 40 | 249K | 228 | 1.42M |
| R&D high | 540 | 5.43M | 297 | 2.99M | 1.69K | 17M |

每授權席次每月(= 每週 × 4.345)與 token 類別拆分;成本以 2026-04 觀測的混合實付均價 $0.72/M 計 [B] [Ramp: AI token cost for businesses](https://ramp.com/blog/ai-token-cost-for-businesses):

| 角色 / 用量級 | 呼叫數 / 席次 / 月 | tokens / 席次 / 月 | 其中未快取輸入 | 其中 cache read | 其中輸出 | cache read 占全部 token | 每席次每月成本($0.72/M) |
|---|---|---|---|---|---|---|---|
| OA low | 12.3 | 13.8K | 11.1K | 1.23K | 1.54K | 8.9% | $0.01 |
| OA base | 89.7 | 350K | 157K | 157K | 35.9K | 44.9% | $0.25 |
| OA high | 385 | 4.92M | 1.15M | 3.46M | 308K | 70.3% | $3.54 |
| Coding low | 143 | 9.79M | 717K | 9.03M | 35.8K | 92.3% | $7.05 |
| Coding base | 1.83K | 168M | 11.9M | 155M | 1.1M | 92.3% | $121 |
| Coding high | 7.17K | 926M | 60.9M | 860M | 5.02M | 92.9% | $667 |
| R&D low | 180 | 874K | 471K | 291K | 111K | 33.3% | $0.63 |
| R&D base | 991 | 6.16M | 2.48M | 2.97M | 713K | 48.2% | $4.44 |
| R&D high | 7.36K | 74M | 19.4M | 50.1M | 4.49M | 67.7% | $53.3 |

**OA(辦公助理)。** low 是早期 Copilot 式的聊天:12% 席次每日活躍、每活躍日 4 次呼叫、每次約 1,000 輸入與 125 輸出 tokens,對應 ChatGPT 每位 WAU 每日 3.7 則訊息(2025-07,18B 則/週 ÷ 700M 人)[B] [OpenAI/NBER "How People Use ChatGPT"](https://cdn.openai.com/pdf/a253471f-8260-40c6-a2cc-aa93fe9f142e/economic-research-chatgpt-usage-paper.pdf) 與 Azure 2024 conversation trace 的輸入中位 928、輸出平均 105.5 tokens [A] [AzureLLMInferenceDataset2024](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md)。base 是導入成熟的通用助理:35% 每日活躍(英國政府 20,000 席試驗中 34% 每日在 Teams 使用,2024-12)[A] [GOV.UK findings report](https://www.gov.uk/government/publications/microsoft-365-copilot-experiment-cross-government-findings-report/microsoft-365-copilot-experiment-cross-government-findings-report-html)、10 次呼叫(ChatGPT 每位 DAU 7.5 則 × 企業版員工年增 30%)、每次 3,500 輸入與 400 輸出,其中 50% cache read 是假設,沒有公開量測。high 是 office agent 成為主流:50% 每日活躍(JPMorgan「about half use it daily」,2025-10)[C] [CeFPro Connect](https://connect.cefpro.com/article/view/inside-jpmorgan-llm-suite-as-ai-agents-spread-across-the-bank)、30 次呼叫、每次 12K 輸入(75% cache read)與 800 輸出,每活躍日 384K tokens,是 base 的 9.8 倍,落在 Anthropic 所說 agent 約為 chat 的 4 倍、multi-agent 約 15 倍之間(2025-06-13)[C] [Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)。

**Coding(軟體工程)。** low 是偶爾使用 agent 或 IDE 助理的團隊:30% 每日活躍(假設,無直接來源)、20 次呼叫,每次呼叫的形狀取 Copilot agent 非企業使用者的中位數,即 prompt 68K(其中 63K 來自快取)與輸出 247 tokens(2026-06)[A] [Agentic Coding in the Wild](https://arxiv.org/abs/2608.00101)。base 是已把 coding agent 標準化的企業:45% 每日活躍(2026-04 調查:40% 的開發者每日使用 agent,軟體業 44%)[A] [Stack Overflow blog](https://stackoverflow.blog/2026/05/27/agents-on-a-leash-agentic-ai-remains-mostly-monitored-at-work/)、170 次呼叫、每次 6.5K 未快取 + 85K cache read + 600 輸出,每活躍日 15.7M tokens,落在 Anthropic「每位開發者每活躍日約 $13」以實付均價 $0.573–1.00/M 換算的 13–23M 之內 [C,換算為 D] [Claude Code docs: Manage costs effectively](https://code.claude.com/docs/en/costs)。high 是平行或長時間執行的 agent:75% 每日活躍、400 次呼叫、每次 129.2K tokens,每活躍日 51.7M,貼著同一文件「90% 的使用者低於每活躍日 $30」換算的 30–52M 上緣。

**coding 的輸入約 93% 是 cache read。** 三個用量級的 cache read 占輸入 92.6%、92.9%、93.4%(占全部 token 92.3–92.9%);公開量測為 85.7%(Copilot 公開樣本)、95.7%(TraceLab)、99.3%(Pegatron 的 Claude Code + Opus)、86.4%(地端 vLLM prefix caching)[A,比例為筆記換算] [GitHub Copilot Coding Agent Traces 2026](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md)、[TraceLab](https://arxiv.org/abs/2606.30560)、[Inference Economics of Enterprise Coding Agents](https://arxiv.org/abs/2607.13080)。對容量有三個後果:

- 配額:不計 cache read 的平台(Anthropic ITPM、Bedrock)只看到每次呼叫約 7.1K tokens(6.5K 未快取 + 0.6K 輸出),不是 92.1K,相差 13 倍。
- 自建:cache read 不是免費的,它要求該 session 的 prefix KV 仍留在 HBM 或 DRAM 層;prefix cache 失效時這 93% 變回 prefill,敏感度分析中未快取輸入 TPM 變成 10.84 倍。
- 分開估:輸出只占 coding 全部 token 的 0.65%(base),decode 容量與 prefill / KV 容量必須各自估算。

**R&D(研發 / 研究)。** 沒有任何公開的每位研究人員用量遙測,三個用量級是由「文件請求」加「deep research run」組合出來的:low 為每活躍日 10 次文件請求(6K 輸入、400 輸出)加 0.2 次 run,base 為 20 次(15K、600)加 1 次,high 為 60 次(40K、1.5K)加 3 次 Max run。每次 run 的大小取 Google 文件的估計,標準約 250K 輸入(50–70% cached)、60K 輸出、80 次搜尋,Max 約 900K、80K、160 次(文件更新 2026-09-23)[C] [Gemini Deep Research agent docs](https://ai.google.dev/gemini-api/docs/deep-research);文件請求的輸入以 PDF 每頁 1,500–3,000 tokens 換算 [B] [Claude PDF support docs](https://platform.claude.com/docs/en/build-with-claude/pdf-support)。活躍占比 low 的 28% 是學術研究者每日使用 agent 的比例(2026-04)[A] [Stack Overflow pulse survey](https://stackoverflow.blog/2026/05/27/agents-on-a-leash-agentic-ai-remains-mostly-monitored-at-work/),base 40% 與 high 55% 是類比開發者與 fintech 的判斷值。

- R&D 的呼叫多而小(base 每活躍日 100 次、每次 6.2K tokens),對 RPM 與輸出 TPM 的貢獻遠大於對 token 總量的貢獻。
- 以 coding agent 做模擬、資料分析或 EDA scripting 的研發人員,應算進 coding 角色(base 每活躍日 15.7M tokens),不是 R&D 角色(622K)。
- OA 的 high 不等於用量筆記範圍表的 High 欄(60 次、30K 輸入、每活躍日 1.9M tokens):那一欄描述 P95 使用者,不能當全體平均。

## 情境計算

同樣 10,000 人、base 用量,五種混合角色組合的尖峰落在 257–1,100 RPM、未快取輸入 1.36M–7.79M TPM、全部 token 14.3M–94.4M TPM;純 OA 與純 coding 的未快取輸入 TPM 相差 69 倍(213K 對 14.8M)[D]。超過約 10,000 人後 k 已在下限 1.15,RPM 與 TPM 隨人數線性放大,100,000 人的值是 10,000 人的 9.5–10.0 倍。

設定:單一時區(s = 0.11)、d = 1.2、所有角色共用一個端點(一份配額);八種角色組合如下。

| 代號 | 角色組合 | OA | coding | R&D |
|---|---|---|---|---|
| A | 辦公為主(服務業、零售總部) | 90% | 7% | 3% |
| B | 製造 / 硬體(ODM、EMS、半導體) | 70% | 12% | 18% |
| C | 金融服務 | 80% | 15% | 5% |
| D | 軟體 / 網路公司 | 40% | 50% | 10% |
| E | 研發為主(IC 設計、研究機構) | 35% | 25% | 40% |
| 純 OA | 100% OA | 100% | 0% | 0% |
| 純 coding | 100% coding | 0% | 100% | 0% |
| 純 R&D | 100% R&D | 0% | 0% | 100% |

### 10,000 人

尖峰分鐘的請求與 token(Bedrock 式 TPM 以 Opus 5.5 的 10× burndown 計;Bedrock 預設配額為 30M TPM):

| 組合 / 用量級 | 尖峰 RPM | 未快取輸入 TPM(= Anthropic ITPM) | cache read TPM | 輸出 TPM(= OTPM) | 全部 token TPM | Bedrock 式 TPM(U + 10 × O) | k |
|---|---|---|---|---|---|---|---|
| A low | 38.1 | 129K | 994K | 11.1K | 1.13M | 239K | 1.62 |
| A base | 257 | 1.36M | 12.8M | 150K | 14.3M | 2.86M | 1.21 |
| A high | 1.1K | 7.24M | 71.1M | 830K | 79.2M | 15.5M | 1.15 |
| B low | 73.7 | 269K | 1.54M | 33.9K | 1.84M | 609K | 1.42 |
| B base | 476 | 2.45M | 21.2M | 313K | 24M | 5.58M | 1.15 |
| B high | 2.53K | 14.3M | 126M | 1.78M | 142M | 32.1M | 1.15 |
| C low | 54.3 | 225K | 1.97M | 17.4K | 2.21M | 399K | 1.50 |
| C base | 415 | 2.54M | 26.1M | 255K | 28.9M | 5.09M | 1.16 |
| C high | 1.82K | 13.7M | 148M | 1.35M | 163M | 27.1M | 1.15 |
| D low | 114 | 587K | 5.76M | 37.7K | 6.38M | 963K | 1.32 |
| D base | 1.1K | 7.79M | 85.9M | 708K | 94.4M | 14.9M | 1.15 |
| D high | 4.7K | 40.9M | 480M | 3.43M | 525M | 75.3M | 1.15 |
| E low | 131 | 515K | 2.95M | 66.2K | 3.53M | 1.18M | 1.30 |
| E base | 920 | 4.97M | 44.1M | 630K | 49.7M | 11.3M | 1.15 |
| E high | 5.04K | 28.9M | 259M | 3.47M | 292M | 63.5M | 1.15 |
| 純 OA low | 20.3 | 21.6K | 2.11K | 2.69K | 26.4K | 48.5K | 1.92 |
| 純 OA base | 103 | 213K | 188K | 43.8K | 445K | 651K | 1.34 |
| 純 OA high | 384 | 1.36M | 3.6M | 326K | 5.29M | 4.62M | 1.17 |
| 純 coding low | 166 | 982K | 10.9M | 44.1K | 11.9M | 1.42M | 1.26 |
| 純 coding base | 1.94K | 14.8M | 171M | 1.23M | 187M | 27.2M | 1.15 |
| 純 coding high | 7.59K | 76.1M | 947M | 5.63M | 1.03B | 132M | 1.15 |
| 純 R&D low | 198 | 611K | 333K | 129K | 1.07M | 1.9M | 1.24 |
| 純 R&D base | 1.01K | 2.99M | 3.16M | 772K | 6.92M | 10.7M | 1.15 |
| 純 R&D high | 7.51K | 23.4M | 53.2M | 4.87M | 81.5M | 72.1M | 1.15 |

併發、用量與成本(同時在途以 v = 80 tokens/s 計;月成本以混合實付均價 $0.72/M 計):

| 組合 / 用量級 | 同時在途(平均) | 同時在途(99.9%) | tokens / 平日 | tokens / 月 | tokens / 員工 / 月 | coding 占 token | 月成本($0.72/M) |
|---|---|---|---|---|---|---|---|
| A low | 3.25 | 8.85 | 302M | 7.24B | 724K | 95% | $5.21K |
| A base | 36.9 | 55.8 | 5.13B | 123B | 12.3M | 96% | $88.5K |
| A high | 196 | 239 | 29.8B | 715B | 71.5M | 91% | $515K |
| B low | 9.29 | 18.7 | 559M | 13.4B | 1.34M | 88% | $9.66K |
| B base | 77.9 | 105 | 9B | 216B | 21.6M | 94% | $155K |
| B high | 440 | 505 | 53.2B | 1.28T | 128M | 87% | $921K |
| C low | 5.11 | 12.1 | 636M | 15.2B | 1.52M | 97% | $11K |
| C base | 63.2 | 87.9 | 10.8B | 258B | 25.8M | 98% | $186K |
| C high | 323 | 379 | 61.2B | 1.47T | 147M | 95% | $1.06M |
| D low | 11.3 | 21.7 | 2.08B | 49.9B | 4.99M | 98% | $35.9K |
| D base | 176 | 217 | 35.5B | 849B | 84.9M | 99% | $612K |
| D high | 835 | 924 | 198B | 4.72T | 472M | 98% | $3.4M |
| E low | 18 | 31.1 | 1.17B | 28B | 2.8M | 88% | $20.2K |
| E base | 157 | 196 | 18.7B | 447B | 44.7M | 94% | $322K |
| E high | 872 | 964 | 110B | 2.63T | 263M | 88% | $1.89M |
| 純 OA low | 0.87 | 3.75 | 5.4M | 138M | 13.8K | 0% | $99.7 |
| 純 OA base | 10.3 | 20.3 | 136M | 3.5B | 350K | 0% | $2.52K |
| 純 OA high | 70.5 | 96.5 | 1.92B | 49.2B | 4.92M | 0% | $35.4K |
| 純 coding low | 14.2 | 25.9 | 4.1B | 97.9B | 9.79M | 100% | $70.5K |
| 純 coding base | 306 | 361 | 70.5B | 1.68T | 168M | 100% | $1.21M |
| 純 coding high | 1.36K | 1.47K | 388B | 9.26T | 926M | 100% | $6.67M |
| 純 R&D low | 33.6 | 51.6 | 353M | 8.74B | 874K | 0% | $6.29K |
| 純 R&D base | 194 | 237 | 2.49B | 61.6B | 6.16M | 0% | $44.4K |
| 純 R&D high | 1.27K | 1.38K | 29.9B | 740B | 74M | 0% | $533K |

### 100,000 人

| 組合 / 用量級 | 尖峰 RPM | 未快取輸入 TPM(= Anthropic ITPM) | cache read TPM | 輸出 TPM(= OTPM) | 全部 token TPM | Bedrock 式 TPM(U + 10 × O) | k |
|---|---|---|---|---|---|---|---|
| A low | 282 | 950K | 7.35M | 81.8K | 8.38M | 1.77M | 1.20 |
| A base | 2.46K | 12.9M | 122M | 1.43M | 137M | 27.2M | 1.15 |
| A high | 11K | 72.4M | 711M | 8.3M | 792M | 155M | 1.15 |
| B low | 599 | 2.19M | 12.5M | 276K | 15M | 4.94M | 1.15 |
| B base | 4.76K | 24.5M | 212M | 3.13M | 240M | 55.8M | 1.15 |
| B high | 25.3K | 143M | 1.26B | 17.8M | 1.42B | 321M | 1.15 |
| C low | 420 | 1.74M | 15.2M | 134K | 17.1M | 3.08M | 1.16 |
| C base | 4.12K | 25.2M | 260M | 2.53M | 287M | 50.6M | 1.15 |
| C high | 18.2K | 137M | 1.48B | 13.5M | 1.63B | 271M | 1.15 |
| D low | 992 | 5.1M | 50M | 328K | 55.5M | 8.37M | 1.15 |
| D base | 11K | 77.9M | 859M | 7.08M | 944M | 149M | 1.15 |
| D high | 47K | 409M | 4.8B | 34.3M | 5.25B | 753M | 1.15 |
| E low | 1.16K | 4.56M | 26.1M | 586K | 31.3M | 10.4M | 1.15 |
| E base | 9.2K | 49.7M | 441M | 6.3M | 497M | 113M | 1.15 |
| E high | 50.4K | 289M | 2.59B | 34.7M | 2.92B | 635M | 1.15 |
| 純 OA low | 136 | 145K | 14.2K | 18.1K | 177K | 326K | 1.29 |
| 純 OA base | 885 | 1.83M | 1.61M | 375K | 3.82M | 5.58M | 1.15 |
| 純 OA high | 3.79K | 13.4M | 35.5M | 3.22M | 52.2M | 45.6M | 1.15 |
| 純 coding low | 1.52K | 8.96M | 99.5M | 402K | 109M | 13M | 1.15 |
| 純 coding base | 19.4K | 148M | 1.71B | 12.3M | 1.87B | 272M | 1.15 |
| 純 coding high | 75.9K | 761M | 9.47B | 56.3M | 10.3B | 1.32B | 1.15 |
| 純 R&D low | 1.84K | 5.68M | 3.09M | 1.2M | 9.98M | 17.7M | 1.15 |
| 純 R&D base | 10.1K | 29.9M | 31.6M | 7.72M | 69.2M | 107M | 1.15 |
| 純 R&D high | 75.1K | 234M | 532M | 48.7M | 815M | 721M | 1.15 |

| 組合 / 用量級 | 同時在途(平均) | 同時在途(99.9%) | tokens / 平日 | tokens / 月 | tokens / 員工 / 月 | coding 占 token | 月成本($0.72/M) |
|---|---|---|---|---|---|---|---|
| A low | 24 | 39.2 | 3.02B | 72.4B | 724K | 95% | $52.1K |
| A base | 352 | 411 | 51.3B | 1.23T | 12.3M | 96% | $885K |
| A high | 1.96K | 2.1K | 298B | 7.15T | 71.5M | 91% | $5.15M |
| B low | 75.5 | 102 | 5.59B | 134B | 1.34M | 88% | $96.6K |
| B base | 779 | 865 | 90B | 2.16T | 21.6M | 94% | $1.55M |
| B high | 4.4K | 4.61K | 532B | 12.8T | 128M | 87% | $9.21M |
| C low | 39.5 | 59 | 6.36B | 152B | 1.52M | 97% | $110K |
| C base | 627 | 705 | 108B | 2.58T | 25.8M | 98% | $1.86M |
| C high | 3.23K | 3.41K | 612B | 14.7T | 147M | 95% | $10.6M |
| D low | 98.2 | 129 | 20.8B | 499B | 4.99M | 98% | $359K |
| D base | 1.76K | 1.89K | 355B | 8.49T | 84.9M | 99% | $6.12M |
| D high | 8.35K | 8.63K | 1.98T | 47.2T | 472M | 98% | $34M |
| E low | 159 | 198 | 11.7B | 280B | 2.8M | 88% | $202K |
| E base | 1.57K | 1.7K | 187B | 4.47T | 44.7M | 94% | $3.22M |
| E high | 8.72K | 9.01K | 1.1T | 26.3T | 263M | 88% | $18.9M |
| 純 OA low | 5.83 | 13.3 | 54M | 1.38B | 13.8K | 0% | $997 |
| 純 OA base | 88.5 | 118 | 1.36B | 35B | 350K | 0% | $25.2K |
| 純 OA high | 696 | 778 | 19.2B | 492B | 4.92M | 0% | $354K |
| 純 coding low | 130 | 165 | 41B | 979B | 9.79M | 100% | $705K |
| 純 coding base | 3.06K | 3.24K | 705B | 16.8T | 168M | 100% | $12.1M |
| 純 coding high | 13.6K | 14K | 3.88T | 92.6T | 926M | 100% | $66.7M |
| 純 R&D low | 313 | 368 | 3.53B | 87.4B | 874K | 0% | $62.9K |
| 純 R&D base | 1.94K | 2.08K | 24.9B | 616B | 6.16M | 0% | $444K |
| 純 R&D high | 12.7K | 13K | 299B | 7.4T | 74M | 0% | $5.33M |

### 規模效應

1,000 與 50,000 人的 48 列在 `calc/out/matrix.csv`(全部 96 列,另含 Bedrock 5× / 15×、Azure PTU、Google GSU、Cerebras 欄位)。下表是組合 B、base 用量在不同人數下的每人尖峰;300 與 3,000 人兩列是以同一模組補算的 [D]:

| 員工數 | busy hour 平均 RPM(m) | k | 尖峰 RPM | 每員工尖峰 RPM | 每員工未快取輸入 TPM | 同時在途(99.9%) | 99.9% ÷ 平均 |
|---|---|---|---|---|---|---|---|
| 300(補算) | 12.4 | 1.85 | 23 | 0.0767 | 394 | 9.77 | 2.60 |
| 1,000 | 41.4 | 1.47 | 60.7 | 0.0607 | 312 | 19.7 | 1.98 |
| 3,000(補算) | 124 | 1.27 | 158 | 0.0526 | 270 | 41.5 | 1.61 |
| 10,000 | 414 | 1.15 | 476 | 0.0476 | 245 | 105 | 1.35 |
| 50,000 | 2.07K | 1.15 | 2.38K | 0.0476 | 245 | 451 | 1.16 |
| 100,000 | 4.14K | 1.15 | 4.76K | 0.0476 | 245 | 865 | 1.11 |

每員工每月 token(21.6M)與每員工 busy hour 平均 RPM 與人數無關,是線性的。每員工的尖峰 RPM 與 TPM 在 m 低於 400(組合 B、base 約 9,700 人)時隨人數下降,之後持平;同時在途的 99.9% 餘裕則持續縮小,由 1,000 人的 1.98 倍降到 100,000 人的 1.11 倍。

### 規劃時要讀出的六件事

1. **哪個角色主導,取決於看哪一類 token。** 組合 B、base:coding 只占人數 12%,卻占全部 token 的 94.0%、未快取輸入的 72.8%,但只占呼叫數的 48.8% 與輸出的 47.2%;R&D(人數 18%)占 token 5.0%,卻占呼叫數 38.2% 與輸出 44.4%;OA(人數 70%)占 token 1.1%、呼叫數 13.0%。KV 與輸入配額跟著 coding 人數走,RPM 與 decode 容量要同時看 R&D。
2. **同一批人,在不同平台要申請的數字不同。** 100,000 人、組合 B、base:全部 token 240M TPM,Anthropic 計 24.5M ITPM,Bedrock(10×)計 55.8M,open-weight(1×)計 27.6M。五種混合組合的「全部 token ÷ 平台計量」為 6.8–12.8(Anthropic ITPM)與 3.0–7.0(Bedrock 10×);以全部 token 計量的 gateway 會比供應商早 3–13 倍限流。
3. **預設配額何時不夠(全部流量在同一個模型類別時)。** Bedrock 的 Opus 5.5 預設 30M TPM:組合 B、base 在約 53,800 人用滿,約 43,000 人到達 AWS 建議設告警的 80% [B] [AWS ML blog](https://aws.amazon.com/blogs/machine-learning/optimize-your-applications-for-scale-and-reliability-on-amazon-bedrock/)。Anthropic Scale tier 先被 ITPM(10M)卡住,約 40,900 人;OTPM(2M)約 63,900 人;RPM(10,000)要到約 210,000 人 [D]。10,000 人、base 的五種混合組合都在 Bedrock 預設內(2.86M–14.9M,即 0.10–0.50 倍);同樣 10,000 人升到 high,B、D、E 即超過(32.1M、75.3M、63.5M)。
4. **RPM 很少是瓶頸。** 尖峰時每個請求平均帶 5.1K 未快取輸入 tokens(24.5M ÷ 4,764),而 Anthropic Scale tier 的 ITPM 與 RPM 之比是每請求 1,000 tokens(10M ÷ 10,000),所以 ITPM 比 RPM 早 5 倍用滿。Bedrock 的 open-weight 類別相反:100M TPM 配 10,000 RPM(不可調),每請求超過 10,000 tokens 才會先碰到 TPM。
5. **併發餘裕隨規模縮小,合併成一個池比較省。** 每 1,000 名員工的 99.9% 在途數由 1,000 人時的 19.7 降到 100,000 人時的 8.65(組合 B、base),相差 2.3 倍。把同樣的人拆成多個各自保留尖峰的小池,併發槽與 hot KV 都要多備。
6. **月用量與成本的量級。** 10,000 人、base 的五種混合組合每月 123B–849B tokens,以 $0.72/M 計為 $88.5K–$612K,即每員工每月 $8.85–$61.2;Ramp 同期的每員工每月 AI token 支出中位數是 $46(中間 50% 為 $3–$352)[B] [Ramp: AI token cost for businesses](https://ramp.com/blog/ai-token-cost-for-businesses)。週末只有平日的 25–45%,以平日尖峰買的容量在週末有 55–75% 閒置。

## 模型組合情境

100,000 人、組合 B、base 用量下,四種路由的自建 GPU 線性需求(decode 受限、Blackwell 級、使用率 0.8)是 MX2 134 顆(另有一個 Opus API 池)、MX3 257 顆、MX4 480 顆;MX1 全走 API,Sonnet 5.5 池的 Bedrock 計量 TPM 是預設配額的 3.35 倍 [D]。10,000 人時線性需求只有 16–48 顆,但每個模型至少要一個操作點大小的部署,MX2 與 MX3 取整後都是 58 顆,反而高於單一模型的 MX4(48 顆)。

### 路由情境與操作點

每個角色的呼叫依下表的比例分到各模型池;每個池各自計算 k、TPM 與在途數。MX1 的 Opus 占比取自 Anthropic 的揭露(chat / Cowork 對話 10% 由 Opus 處理,Claude Code session 為 54%,2026-06-26)[B] [Anthropic Economic Index: Cadences](https://www.anthropic.com/research/economic-index-june-2026-report);R&D 的 50% 與 MX2–MX4 的比例是情境設定。

| 情境 | OA 的呼叫 | coding 的呼叫 | R&D 的呼叫 |
|---|---|---|---|
| MX1 只用 frontier API | Opus 5.5 10%;Sonnet 5.5 90% | Opus 5.5 54%;Sonnet 5.5 46% | Opus 5.5 50%;Sonnet 5.5 50% |
| MX2 分層路由 | V4.1-Flash 80%;GLM-5.3 20% | Kimi K3 40%;V4-Pro 30%;Opus 5.5 30% | V4-Pro 50%;Opus 5.5 30%;V4.1-Flash 20% |
| MX3 只用 open-weight | V4.1-Flash 100% | GLM-5.3 50%;Kimi K3 50% | V4-Pro 100% |
| MX4 單一 open flagship | Kimi K3 100% | Kimi K3 100% | Kimi K3 100% |

open-weight 模型池的自建操作點,全部取自 InferenceX 的 AgentX(agentic coding trace 重播)在 2026-10-04 的快照 [A];KV bytes 與價格的出處列在表後:

| 模型池 | 操作點:硬體;引擎;精度;layout;併發;GPU 數(量測日) | output tokens/s per GPU | 每使用者 tokens/s(中位 / P90) | TTFT(中位 / P90,s) | KV bytes / token | Bedrock 預設 TPM(burndown) | list price($/M:輸入 / cached / 輸出) |
|---|---|---|---|---|---|---|---|
| Kimi K3 | GB300 NVL72;dynamo-vllm;MXFP4;TP8;c48;8 顆;KV offload 到 DRAM 160 GB(2026-09-15) | 136 | 38 / 26 | 1.15 / 2.88 | 13.8 KB,另加每序列 434 MB 的 recurrent state | 10M(1×) | 3.00 / 0.30 / 15.00 |
| GLM-5.3(以 GLM-5.2 的量測代表) | GB300 NVL72;dynamo-sglang;FP4;P/D disagg(P TP8/EP8/DPA × 2 + D TP16/EP16/DPA);c128;32 顆;DRAM 721 GB(2026-10-02) | 149 | 101 / 90 | 2.33 / 5.81 | 44.9 KB | 100M(1×;借用同類別的值) | 1.40 / 0.26 / 4.40 |
| DeepSeek V4-Pro | B300;sglang;FP4;TP8/EP8/DPA;c384;8 顆;DRAM 2,849 GB(2026-09-29) | 739 | 37 / 34 | 2.94 / 12.66 | 5.0 KB | 100M(1×;借用同類別的值) | 1.32 / 0.044 / 3.96(尖峰時段) |
| DeepSeek V4.1-Flash | B300;vllm;FP4;TP2/EP2/DPA;c192;2 顆;無 KV offload(2026-10-02) | 3,059 | 60 / 41 | 0.25 / 0.81 | 0.89 KB(global KV) | 100M(1×;借用同類別的值) | 0.30 / 0.006 / 1.20(尖峰時段) |

- 操作點:[InferenceX API, model=Kimi-K3, pulled 4 Oct 2026](https://inferencex.semianalysis.com/api/v1/benchmarks?model=Kimi-K3)、[InferenceX API, model=GLM-5.2, pulled 4 Oct 2026](https://inferencex.semianalysis.com/api/v1/benchmarks?model=GLM-5.2)、[InferenceX API, model=DeepSeek-V4-Pro, pulled 4 Oct 2026](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4-Pro)、[InferenceX API, model=DeepSeek-V4.1-Flash, pulled 4 Oct 2026](https://inferencex.semianalysis.com/api/v1/benchmarks?model=DeepSeek-V4.1-Flash)。四個點都開了 speculative decoding(K3 用 DSpark draft,其餘用 MTP)。
- KV bytes:Kimi K3 為 24 層 MLA × 576 個 FP8 元素 = 13,824 bytes [D],InferenceX 的紀錄 42.23 GiB / 3,249,215 tokens = 13,955 bytes [A] [InferenceX perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml);recurrent state 為 TP8 下每 rank 約 54 MB × 8 [B] [LMSYS blog, 27 Jul 2026](https://www.lmsys.org/blog/2026-07-27-kimi-k3-day0-support/)。GLM-5.2「about 44 KB of KV state per token」[B] [llm-d blog, 22 Jul 2026](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)。V4-Pro 為 1M tokens 約 9.62 GiB(BF16)再以 FP8 / FP4 快取約減半 [B,換算為 D] [vLLM blog, 24 Apr 2026](https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-04-24-deepseek-v4.md)。V4.1-Flash 為廠商規格 890 bytes [C] [V4.1-Flash card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)。
- Bedrock 配額:[Amazon Bedrock endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/bedrock.html) [B]。筆記沒有找到 GLM-5.3、DeepSeek V4-Pro、V4.1-Flash 的 Bedrock 配額列,模型借用 DeepSeek V3.2、GLM 5 等 open-weight 模型的 100M TPM(另有不可調的 10,000 RPM)。
- 價格:[Kimi pricing](https://platform.kimi.ai/docs/pricing/chat)、[Z.ai pricing](https://docs.z.ai/guides/overview/pricing)、[DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing) [C;2026-10-04 經摘要工具讀取,引用前需重查]。DeepSeek 離峰時段為半價。

只走 API 的模型池:

| 模型池 | Bedrock 預設 TPM | output burndown | 呼叫時間用的 v | 價格 |
|---|---|---|---|---|
| Claude Opus 5.5 | 30M(cross-Region 與 global) | 10× | 80 tokens/s(假設) | 價格見第 5 章 |
| Claude Sonnet 5.5 | 6M | 5×(AWS 文字未點名 Sonnet 5.5;Sonnet 5 為 10×、4.7 以下為 5×,模型沿用 5×) | 80 tokens/s(假設) | 價格見第 5 章 |

### GPU 與 KV 的推算方式

GPU 數只看 decode:該池的尖峰輸出 tokens/s,除以操作點的 output tokens/s per GPU(g),再除以使用率上限 0.8:

```latex
G_{\mathrm{decode}} = \frac{\mathrm{TPM}_o / 60}{g \cdot 0.8}
```

hot KV 是 99.9% 在途請求的 context,必須放在 HBM;n 是該池每次呼叫的平均 context(u + c + o),b 是 KV bytes per token,b_s 是每序列的固定 state(只有 Kimi K3 不為零):

```latex
\mathrm{KV}_{\mathrm{hot}} = L_{99.9} \cdot \left(\bar{n} \cdot b + b_s\right)
```

warm KV 是「為了讓下一次呼叫命中 prefix cache 而保留」的 session,數量取在途數的 16 倍,每個 session 常駐 1.2 倍的平均 context:

```latex
\mathrm{KV}_{\mathrm{warm}} = 16 L \cdot \left(1.2\,\bar{n} \cdot b + b_s\right)
```

- **操作點給使用者的體驗。** 上表的每使用者速度與 TTFT 就是該 GPU 數所對應的服務水準:Kimi K3 池每位使用者中位 38 tokens/s、TTFT 1.15 s;V4-Pro 池 37 tokens/s、TTFT 2.94 s(P90 12.66 s)。要更快就得換到同一來源較低併發的點,例如 Kimi K3 在 GB300 的 P/D disagg、c56 是 112 output tokens/s per GPU 與每使用者 61 tokens/s(2026-09-15)[A],GPU 數變成 1.21 倍。自建池的在途數改用操作點的每使用者速度計算 W,API 池用 80 tokens/s。
- **對 chat 流量保守。** AgentX 重播的是 agentic coding trace(Kimi K3 的 trace 每 turn 中位 142K 輸入、444 輸出;DeepSeek V4 各次重播的輸入 p50 88K、p90 272K)[A] [InferenceX blog, 3 Aug 2026](https://inferencex.semianalysis.com/blog/kimi-k3-the-manos-the-mythos-the)、[InferenceX blog, 25 Aug 2026](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-mi355x-vs-b200-august)。OA 一次呼叫只有 3.5K 輸入配 400 輸出,每個輸出 token 分攤的 prefill 與 KV 遠少於 trace,拿 agentic 操作點估 OA 與 R&D 池會高估 GPU 數 [D,推論]。
- **對 speculative decoding 樂觀。** AgentX 把 acceptance length 固定在 SPEED-Bench coding 類別量到的 golden 曲線,不是 trace 上實際達到的值;Kimi K3 的 DSpark 在真實 trace 上量到 1.18–1.68 個 token(golden 為 3.84),併發 4 / 8 時吞吐量退回 20–63% [A] [InferenceX MODELS.md](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/docs/MODELS.md)、[InferenceX perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)。同一表中 Kimi K3 不開 speculative decoding 的點(GB200 NVL72、c96)是 71 output tokens/s per GPU、每使用者 12 tokens/s,所以 K3 的 GPU 數應視為下限。
- **只算 decode,沒有單獨算 prefill。** 操作點是在 trace 的 cache 命中條件下量到的,prefill 的負擔已隱含在內;prefix cache 失效時(未快取輸入變 10.84 倍)這個 GPU 數不成立。GPU 數是線性需求,沒有取整到最小部署單位,也沒有加備援。
- **hot 與 warm 的差別。** hot KV 是正在 decode 的序列,每一步都要讀,只能在 HBM;warm KV 是使用者閒置中的 session,放在 DRAM 或 flash 層即可,但不在任何一層時下一次呼叫的 cache read 會變回 prefill。16 倍取自 Copilot trace:最忙小時的平均在途呼叫是該小時活躍 session 的 5.3–7.4% [A,筆記實算];1.2 倍是以 coding base 校準,92.1K × 1.2 ≈ 110K tokens,對上 InferenceX 與 llm-d 量到的每 session 常駐約 110–112K tokens(43M ÷ 384;14.1M ÷ 128)[A / B,換算為 D] [InferenceX blog, 25 Aug 2026](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-b200-vs-b300-kv-working-set)、[llm-d blog, 22 Jul 2026](https://llm-d.ai/blog/serving-glm-5-2-agentic-workloads-on-llm-d)。

### 10,000 人、組合 B、base

| 情境 | 自建 GPU(線性需求) | 取整到操作點單位 | hot KV 合計 | warm KV 合計 | API 池:Bedrock 計量 TPM ÷ 預設配額 | open-weight 月成本(list price) | 各池 RPM 合計 ÷ 單一池 |
|---|---|---|---|---|---|---|---|
| MX1 | 0 | 0 | 0 | 0 | Opus 5.5 0.10×;Sonnet 5.5 0.35× | 價格見第 5 章 | 1.051 |
| MX2 | 15.6 | 58 | 104 GB | 1.26 TB | Opus 5.5 0.06× | $64.3K + Opus(價格見第 5 章) | 1.141 |
| MX3 | 28.9 | 58 | 228 GB | 2.64 TB | 無 API 池 | $108K | 1.122 |
| MX4 | 48.0 | 48 | 200 GB | 2.86 TB | 無 API 池 | $160K | 1.000 |

**MX1 只用 frontier API**

| 模型池 | 尖峰 RPM | 未快取輸入 TPM | 輸出 TPM | Bedrock 計量 TPM | ÷ 預設配額 | 同時在途(99.9%) | 月成本(list price) |
|---|---|---|---|---|---|---|---|
| Claude Opus 5.5(API) | 235 | 1.31M | 161K | 2.92M | 0.10× | 59.7 | 價格見第 5 章 |
| Claude Sonnet 5.5(API) | 265 | 1.26M | 168K | 2.1M | 0.35× | 61.8 | 價格見第 5 章 |

**MX2 分層路由**:配額與成本,以及 open-weight 池的自建換算

| 模型池 | 尖峰 RPM | 未快取輸入 TPM | 輸出 TPM | Bedrock 計量 TPM | ÷ 預設配額 | 同時在途(99.9%) | 月成本(list price) |
|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash | 101 | 246K | 57.2K | 303K | 0.00× | 30.8 | $1.09K |
| GLM-5.3 | 20.6 | 42.6K | 8.75K | 51.3K | 0.00× | 5.75 | $586 |
| Kimi K3 | 108 | 826K | 68.5K | 895K | 0.09× | 49.5 | $47.4K |
| DeepSeek V4-Pro | 175 | 876K | 124K | 1M | 0.01× | 83.3 | $15.3K |
| Claude Opus 5.5(API) | 139 | 779K | 96.4K | 1.74M | 0.06× | 39.3 | 價格見第 5 章 |

| 模型池 | 尖峰輸出 tokens/s | GPU 數(decode 受限) | hot KV tokens | hot KV | warm KV tokens | warm KV |
|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash | 953 | 0.39 | 150K | 0.13 GB | 1.66M | 1.48 GB |
| GLM-5.3 | 146 | 1.22 | 22.4K | 1.01 GB | 128K | 5.73 GB |
| Kimi K3 | 1.14K | 10.5 | 4.56M | 84.3 GB | 56.5M | 1 TB |
| DeepSeek V4-Pro | 2.07K | 3.50 | 3.62M | 18.1 GB | 49.5M | 248 GB |

**MX3 只用 open-weight**

| 模型池 | 尖峰 RPM | 未快取輸入 TPM | 輸出 TPM | Bedrock 計量 TPM | ÷ 預設配額 | 同時在途(99.9%) | 月成本(list price) |
|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash | 75.9 | 157K | 32.2K | 189K | 0.00× | 19.4 | $638 |
| GLM-5.3 | 131 | 1.01M | 83.4K | 1.09M | 0.01× | 30.3 | $37.1K |
| Kimi K3 | 131 | 1.01M | 83.4K | 1.09M | 0.11× | 58.2 | $59.2K |
| DeepSeek V4-Pro | 196 | 579K | 150K | 728K | 0.01× | 98.1 | $11.2K |

| 模型池 | 尖峰輸出 tokens/s | GPU 數(decode 受限) | hot KV tokens | hot KV | warm KV tokens | warm KV |
|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash | 537 | 0.22 | 75.5K | 0.07 GB | 726K | 0.65 GB |
| GLM-5.3 | 1.39K | 11.7 | 2.79M | 125 GB | 30.7M | 1.38 TB |
| Kimi K3 | 1.39K | 12.8 | 5.36M | 99.2 GB | 68.7M | 1.22 TB |
| DeepSeek V4-Pro | 2.5K | 4.22 | 610K | 3.05 GB | 8.57M | 42.9 GB |

**MX4 單一 open flagship(Kimi K3)**

| 模型池 | 尖峰 RPM | 未快取輸入 TPM | 輸出 TPM | Bedrock 計量 TPM | ÷ 預設配額 | 同時在途(99.9%) | 月成本(list price) |
|---|---|---|---|---|---|---|---|
| Kimi K3 | 476 | 2.45M | 313K | 2.76M | 0.28× | 183 | $160K |

| 模型池 | 尖峰輸出 tokens/s | GPU 數(decode 受限) | hot KV tokens | hot KV | warm KV tokens | warm KV |
|---|---|---|---|---|---|---|
| Kimi K3 | 5.22K | 48.0 | 8.76M | 200 GB | 134M | 2.86 TB |

### 100,000 人、組合 B、base

| 情境 | 自建 GPU(線性需求) | 取整到操作點單位 | hot KV 合計 | warm KV 合計 | API 池:Bedrock 計量 TPM ÷ 預設配額 | open-weight 月成本(list price) | 各池 RPM 合計 ÷ 單一池 |
|---|---|---|---|---|---|---|---|
| MX1 | 0 | 0 | 0 | 0 | Opus 5.5 0.92×;Sonnet 5.5 3.35× | 價格見第 5 章 | 1.000 |
| MX2 | 134 | 172 | 696 GB | 11 TB | Opus 5.5 0.52× | $643K + Opus(價格見第 5 章) | 1.003 |
| MX3 | 257 | 290 | 1.5 TB | 23.4 TB | 無 API 池 | $1.08M | 1.000 |
| MX4 | 480 | 480 | 1.72 TB | 28.6 TB | 無 API 池 | $1.6M | 1.000 |

**MX1 只用 frontier API**

| 模型池 | 尖峰 RPM | 未快取輸入 TPM | 輸出 TPM | Bedrock 計量 TPM | ÷ 預設配額 | 同時在途(99.9%) | 月成本(list price) |
|---|---|---|---|---|---|---|---|
| Claude Opus 5.5(API) | 2.23K | 12.4M | 1.52M | 27.6M | 0.92× | 440 | 價格見第 5 章 |
| Claude Sonnet 5.5(API) | 2.54K | 12M | 1.61M | 20.1M | 3.35× | 461 | 價格見第 5 章 |

**MX2 分層路由**

| 模型池 | 尖峰 RPM | 未快取輸入 TPM | 輸出 TPM | Bedrock 計量 TPM | ÷ 預設配額 | 同時在途(99.9%) | 月成本(list price) |
|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash | 860 | 2.1M | 488K | 2.59M | 0.03× | 190 | $10.9K |
| GLM-5.3 | 139 | 287K | 58.9K | 346K | 0.00× | 22 | $5.86K |
| Kimi K3 | 929 | 7.13M | 591K | 7.72M | 0.77× | 327 | $474K |
| DeepSeek V4-Pro | 1.61K | 8.03M | 1.14M | 9.17M | 0.09× | 617 | $153K |
| Claude Opus 5.5(API) | 1.24K | 6.96M | 860K | 15.6M | 0.52× | 261 | 價格見第 5 章 |

| 模型池 | 尖峰輸出 tokens/s | GPU 數(decode 受限) | hot KV tokens | hot KV | warm KV tokens | warm KV |
|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash | 8.14K | 3.33 | 926K | 0.82 GB | 14.2M | 12.6 GB |
| GLM-5.3 | 982 | 8.24 | 85.8K | 3.85 GB | 860K | 38.6 GB |
| Kimi K3 | 9.85K | 90.5 | 30.1M | 557 GB | 487M | 8.63 TB |
| DeepSeek V4-Pro | 19K | 32.1 | 26.8M | 134 GB | 454M | 2.27 TB |

**MX3 只用 open-weight**

| 模型池 | 尖峰 RPM | 未快取輸入 TPM | 輸出 TPM | Bedrock 計量 TPM | ÷ 預設配額 | 同時在途(99.9%) | 月成本(list price) |
|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash | 620 | 1.28M | 263K | 1.54M | 0.02× | 107 | $6.38K |
| GLM-5.3 | 1.16K | 8.91M | 739K | 9.65M | 0.10× | 192 | $371K |
| Kimi K3 | 1.16K | 8.91M | 739K | 9.65M | 0.96× | 402 | $592K |
| DeepSeek V4-Pro | 1.82K | 5.37M | 1.39M | 6.76M | 0.07× | 747 | $112K |

| 模型池 | 尖峰輸出 tokens/s | GPU 數(decode 受限) | hot KV tokens | hot KV | warm KV tokens | warm KV |
|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash | 4.38K | 1.79 | 416K | 0.37 GB | 5.93M | 5.28 GB |
| GLM-5.3 | 12.3K | 103 | 17.7M | 794 GB | 272M | 12.2 TB |
| Kimi K3 | 12.3K | 113 | 37M | 685 GB | 609M | 10.8 TB |
| DeepSeek V4-Pro | 23.2K | 39.2 | 4.64M | 23.2 GB | 79.6M | 398 GB |

**MX4 單一 open flagship(Kimi K3)**

| 模型池 | 尖峰 RPM | 未快取輸入 TPM | 輸出 TPM | Bedrock 計量 TPM | ÷ 預設配額 | 同時在途(99.9%) | 月成本(list price) |
|---|---|---|---|---|---|---|---|
| Kimi K3 | 4.76K | 24.5M | 3.13M | 27.6M | 2.76× | 1.58K | $1.6M |

| 模型池 | 尖峰輸出 tokens/s | GPU 數(decode 受限) | hot KV tokens | hot KV | warm KV tokens | warm KV |
|---|---|---|---|---|---|---|
| Kimi K3 | 52.2K | 480 | 75.4M | 1.72 TB | 1.34B | 28.6 TB |

有每 GPU KV 容量數據的只有兩個模型:Kimi K3 取 8 顆 B300 在 TP8 下扣掉權重後可放 3.25M tokens(每顆 406K)[A] [InferenceX blog, 3 Aug 2026](https://inferencex.semianalysis.com/blog/kimi-k3-the-manos-the-mythos-the),DeepSeek V4-Pro 取 8 顆 B300 在 c384 量到的 HBM KV working set 43M tokens(每顆 5.4M)[A] [InferenceX blog, 25 Aug 2026](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-b200-vs-b300-kv-working-set)。以 hot KV tokens 除以每顆容量,得到 HBM KV 受限的 GPU 數:

| 員工數 | 情境 | 模型池 | GPU 數(decode 受限) | GPU 數(HBM KV 受限) | KV ÷ decode |
|---|---|---|---|---|---|
| 10,000 人 | MX2 | Kimi K3 | 10.5 | 11.2 | 1.07 |
| 10,000 人 | MX2 | DeepSeek V4-Pro | 3.50 | 0.67 | 0.19 |
| 10,000 人 | MX3 | Kimi K3 | 12.8 | 13.2 | 1.03 |
| 10,000 人 | MX3 | DeepSeek V4-Pro | 4.22 | 0.11 | 0.03 |
| 10,000 人 | MX4 | Kimi K3 | 48.0 | 21.6 | 0.45 |
| 100,000 人 | MX2 | Kimi K3 | 90.5 | 74.1 | 0.82 |
| 100,000 人 | MX2 | DeepSeek V4-Pro | 32.1 | 4.99 | 0.16 |
| 100,000 人 | MX3 | Kimi K3 | 113 | 91.1 | 0.81 |
| 100,000 人 | MX3 | DeepSeek V4-Pro | 39.2 | 0.86 | 0.02 |
| 100,000 人 | MX4 | Kimi K3 | 480 | 186 | 0.39 |

### 另外兩個案例

100,000 人、組合 B、high(各池明細在 `calc/out/model_mix.md`):

| 情境 | 自建 GPU(線性需求) | 取整到操作點單位 | hot KV 合計 | warm KV 合計 | API 池:Bedrock 計量 TPM ÷ 預設配額 | open-weight 月成本(list price) | 各池 RPM 合計 ÷ 單一池 |
|---|---|---|---|---|---|---|---|
| MX1 | 0 | 0 | 0 | 0 | Opus 5.5 5.13×;Sonnet 5.5 19.86× | 價格見第 5 章 | 1.000 |
| MX2 | 682 | 690 | 3.79 TB | 65.3 TB | Opus 5.5 2.89× | $3.52M + Opus(價格見第 5 章) | 1.000 |
| MX3 | 1,252 | 1,264 | 8.34 TB | 144 TB | 無 API 池 | $5.96M | 1.000 |
| MX4 | 2,722 | 2,728 | 9.99 TB | 174 TB | 無 API 池 | $9.36M | 1.000 |

100,000 人、組合 D(軟體 / 網路公司)、base:

| 情境 | 自建 GPU(線性需求) | 取整到操作點單位 | hot KV 合計 | warm KV 合計 | API 池:Bedrock 計量 TPM ÷ 預設配額 | open-weight 月成本(list price) | 各池 RPM 合計 ÷ 單一池 |
|---|---|---|---|---|---|---|---|
| MX1 | 0 | 0 | 0 | 0 | Opus 5.5 2.63×;Sonnet 5.5 8.84× | 價格見第 5 章 | 1.000 |
| MX2 | 447 | 482 | 2.6 TB | 44.1 TB | Opus 5.5 1.46× | $2.42M + Opus(價格見第 5 章) | 1.001 |
| MX3 | 925 | 946 | 5.63 TB | 96 TB | 無 API 池 | $4.08M | 1.001 |
| MX4 | 1,084 | 1,088 | 5.41 TB | 94.1 TB | 無 API 池 | $5.17M | 1.000 |

### 讀出的重點

1. **R&D 與 OA 放在哪個模型,比 coding 的分流更影響 GPU 數。** 100,000 人由 MX4 改成 MX3 少 222 顆:R&D 的 23.2K 輸出 tokens/s 由 Kimi K3 移到 V4-Pro 省 174 顆(213 → 39.2),OA 移到 V4.1-Flash 省 38.5 顆,coding 的一半移到 GLM-5.3 只省 9.9 顆 [D]。原因是 output tokens/s per GPU 相差 5.4–22 倍(136 對 739 與 3,059)。
2. **Kimi K3 的 coding 池同時被 decode 與 HBM KV 卡住。** 在 MX2 與 MX3,K3 池 HBM KV 受限的 GPU 數是 decode 受限的 0.81–1.07 倍;到 high 用量時 KV 反超(429 對 414、532 對 518)。TP 下 MLA KV 在每個 rank 各存一份,decode context parallelism(DCP8)可把同一節點的 KV 容量由 1.93M 提高到 19.75M tokens(vLLM,B300,2026-09-13)[B] [vLLM blog, 13 Sep 2026](https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-09-13-kimi-k3-performance-optimization.md)。
3. **warm KV 需要 DRAM 層,量級是每 8 顆 GPU 0.5–1 TB。** 100,000 人、base:K3 池的 warm KV 為 8.63–28.6 TB、GLM 池 12.2 TB,折合每 8 顆 GPU 0.48–0.95 TB [D];InferenceX 的規則是每台伺服器最多 3 TB DRAM 做 KV offload,並量到 DRAM 為 HBM KV 容量 1.5–3 倍時最有效 [A] [InferenceX blog, 25 Aug 2026](https://inferencex.semianalysis.com/blog/deepseek-v4-pro-agentx-b200-vs-b300-kv-working-set)。沒有這一層的後果有量測:Kimi K3 在 B300 上只用 GPU 常駐 KV、併發 16 / 24 時 cache 命中率掉到 2.7%、TTFT 中位 86 s / 191 s,加 DRAM offload 後為 0.85 s / 6.2 s [A] [InferenceX perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml)。Kimi K3 的 warm KV 是下限:引擎為了 prefix caching 每 32K tokens 另存一份 recurrent state,每個 session 的份數查無公開資料。
4. **API 配額。** MX1 在 100,000 人時 Opus 5.5 池是預設的 0.92 倍(已過 80% 告警線)、Sonnet 5.5 池 3.35 倍;若 Sonnet 5.5 的 burndown 實為 10×,會是 4.69 倍 [D]。MX4 把全部流量放到 Bedrock 上的 Kimi K3 是預設 10M TPM 的 2.76 倍;借用 100M 類別的三個模型在 TPM 上都不到 1 倍,但該類別的 RPM 上限 10,000 不可調,組合 B、high 的 V4-Pro 池(13.5K RPM)會先碰到。
5. **list price 的成本。** 100,000 人、base:MX3 每月 $1.08M、MX4 $1.60M(Kimi K3 在這個 token 組成下的有效單價為 $0.74/M),矩陣用的混合實付均價 $0.72/M 給 $1.55M [D]。V4-Pro 池的有效單價只有 $0.23/M(MX2),因為 cached 輸入的牌價是 $0.044/M。
6. **小規模由最小部署單位決定。** 10,000 人時 MX2 的線性需求是 15.6 顆,但四個模型各一個操作點大小的部署(2、32、16、8 顆)合計 58 顆;MX4 只有一個模型,48 顆即可 [D]。模型數越多,要到越大的人數才划算。

### 不能換算到 Trainium、TPU 與 Cerebras 的部分

GPU 數依賴「該模型在該硬體、指定併發下每顆晶片的 output tokens/s」。本章所用的筆記中,這四個模型只有 NVIDIA 與 AMD GPU 的 AgentX 量測;它們在 Trainium、TPU 或 Cerebras 上的每晶片批次吞吐量查無公開資料(筆記只記到 TPU 有 Qwen3.5-397B 的結果、Trainium 有社群移植的 GLM-5.2,細節在第 1 與第 4 章)。因此「GPU 數」「HBM KV 受限的 GPU 數」兩欄無法換成晶片數或系統數。

可以直接帶過去的是需求側的四個量,它們與硬體無關:尖峰輸出 tokens/s、同時在途請求數(99.9%)、hot KV tokens、warm KV tokens。Cerebras 的 API 配額可用第一節的兩個 bucket 換算;一旦廠商或第三方公布每晶片(或每系統)在某併發下的 output tokens/s 與可常駐的 KV tokens,代入同一組公式即可。

## 敏感度分析

以 100,000 人、組合 B、base 為基準,影響最大的單一假設是 prefix caching 是否可用:失去快取時未快取輸入 TPM 變成 10.84 倍(24.5M → 265M),RPM 不變 [D]。其次是 coding 與 R&D 的用量級(RPM 0.55–3.46 倍)與員工的時區分布(0.59 倍)。

相對基準的倍數,依「RPM、未快取輸入 TPM、輸出 TPM、同時在途」四項中變動最大者排序:

| 排名 | 變動 | 尖峰 RPM | 未快取輸入 TPM | cache read TPM | 輸出 TPM | 同時在途(99.9%) |
|---|---|---|---|---|---|---|
| 1 | 沒有 prefix / prompt caching(輸入全部未快取) | 1.00× | 10.84× | 0.00× | 1.00× | 1.00× |
| 2 | coding 升到 high,其餘 base | 2.42× | 4.01× | 5.39× | 2.69× | 2.52× |
| 3 | R&D 升到 high,其餘 base | 3.46× | 2.50× | 1.42× | 3.35× | 3.32× |
| 4 | wafer-scale 等級的串流(每使用者 1,000 tokens/s) | 1.00× | 1.00× | 1.00× | 1.00× | 0.30× |
| 5 | coding 降到 low,其餘 base | 0.55× | 0.32× | 0.09× | 0.54× | 0.57× |
| 6 | 串流較快(每使用者 300 tokens/s) | 1.00× | 1.00× | 1.00× | 1.00× | 0.44× |
| 7 | 輸出 tokens × 2(reasoning 加重) | 1.00× | 1.00× | 1.00× | 2.00× | 1.74× |
| 8 | 串流較慢(每使用者 40 tokens/s) | 1.00× | 1.00× | 1.00× | 1.00× | 1.74× |
| 9 | 員工分散全球(s = 6.5%,基準為 11%) | 0.59× | 0.59× | 0.59× | 0.59× | 0.61× |
| 10 | OA 升到 high(office agent),其餘 base | 1.43× | 1.33× | 1.11× | 1.64× | 1.52× |
| 11 | 月底 / release 尖峰(d = 1.5) | 1.25× | 1.25× | 1.25× | 1.25× | 1.24× |
| 12 | 以平均平日估(d = 1.0) | 0.83× | 0.83× | 0.83× | 0.83× | 0.84× |
| 13 | 一日更集中(s = 12.5%) | 1.14× | 1.14× | 1.14× | 1.14× | 1.13× |

絕對值:

| 變動 | 尖峰 RPM | 未快取輸入 TPM | cache read TPM | 輸出 TPM | 全部 token TPM | 同時在途(99.9%) |
|---|---|---|---|---|---|---|
| 基準(100,000 人、組合 B、base、單一時區) | 4.76K | 24.5M | 212M | 3.13M | 240M | 865 |
| 沒有 prefix / prompt caching(輸入全部未快取) | 4.76K | 265M | 0 | 3.13M | 268M | 865 |
| coding 升到 high,其餘 base | 11.5K | 98M | 1.14B | 8.41M | 1.25B | 2.18K |
| R&D 升到 high,其餘 base | 16.5K | 61.2M | 302M | 10.5M | 374M | 2.88K |
| wafer-scale 等級的串流(每使用者 1,000 tokens/s) | 4.76K | 24.5M | 212M | 3.13M | 240M | 258 |
| coding 降到 low,其餘 base | 2.62K | 7.73M | 18.7M | 1.7M | 28.2M | 491 |
| 串流較快(每使用者 300 tokens/s) | 4.76K | 24.5M | 212M | 3.13M | 240M | 384 |
| 輸出 tokens × 2(reasoning 加重) | 4.76K | 24.5M | 212M | 6.26M | 243M | 1.51K |
| 串流較慢(每使用者 40 tokens/s) | 4.76K | 24.5M | 212M | 3.13M | 240M | 1.51K |
| 員工分散全球(s = 6.5%,基準為 11%) | 2.82K | 14.5M | 125M | 1.85M | 142M | 527 |
| OA 升到 high(office agent),其餘 base | 6.8K | 32.6M | 236M | 5.12M | 274M | 1.31K |
| 月底 / release 尖峰(d = 1.5) | 5.95K | 30.6M | 265M | 3.91M | 300M | 1.07K |
| 以平均平日估(d = 1.0) | 3.97K | 20.4M | 177M | 2.61M | 200M | 728 |
| 一日更集中(s = 12.5%) | 5.41K | 27.8M | 241M | 3.56M | 272M | 977 |

- prefix caching 是否可用、coding 的用量級、時區分布這三項決定 RPM 與 TPM 的量級:分別是未快取輸入 10.84 倍、0.32–4.01 倍、0.59 倍。R&D 升到 high 是 RPM 的最大推力(3.46 倍,每活躍日 540 次呼叫),而 R&D 的參數全部是判斷值,這一列的不確定性最大。
- 每條串流的速度對 RPM 與 TPM 沒有影響(1.00×),對併發影響很大:99.9% 在途數由 40 tokens/s 的 1,510 降到 1,000 tokens/s 的 258,相差 5.9 倍。快的硬體省的是併發槽與 hot KV,不是配額。
- d 與 s 的合理範圍只帶來 0.83–1.25 倍的變動,遠小於用量級的不確定性;先把 coding 與 R&D 的實際用量量出來,比調整尖峰係數有用。

## 與公開基準的交叉檢查

模型的 coding base(每活躍開發者日 15.7M tokens、每授權席次每月 168M)落在四個公開基準的範圍內或其下緣:Anthropic 的成本換算 13–23M / 活躍日、AWS 的 225M / 使用者 / 月上限(模型為 0.75 倍)、用量筆記的示範混合(模型低 13%)、Meta 的每員工每日 23.6M(模型的軟體公司 high 為 0.66 倍)[D]。

| 基準 | 公開數值 | 模型對應值 | 模型的位置 | 原因 |
|---|---|---|---|---|
| Anthropic Claude Code 建議表,500 人以上列的 RPM(2026-10-04 取得)[C] [Claude Code docs: Manage costs effectively](https://code.claude.com/docs/en/costs) | 每使用者 0.25–0.35 RPM | 純 coding、10,000 人、base:每授權開發者 0.194 RPM;a 改為 0.70 時 0.301 | a = 0.45 時低於(0.55–0.78 倍);a = 0.70 時在範圍內 | 表的單位是「使用者」;模型的 base 只有 45% 席次每日活躍,折合每席次每月 10.8 個活躍日,低於 Anthropic 成本數字隱含的 11.5–19 日 |
| 同一張表的 TPM | 每使用者 10–15K TPM | 全部 token 18.7K TPM;未快取輸入 + 輸出 1.61K TPM(a = 0.70:29.1K 與 2.50K) | 以全部 token 計高於(1.25–1.87 倍);不計 cache read 則遠低於(0.11–0.16 倍) | 表沒有定義 TPM 是否含 cache read;表內 TPM ÷ RPM 約 40–43K tokens/請求,介於模型每次呼叫的兩種計法之間(8.3K 與 96.7K,含尖峰修正) |
| AWS「Guidance for Claude Code with Amazon Bedrock」的 per-user 預設(repo commit 2026-08-20)[C] [QUOTA_MONITORING.md](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/blob/main/assets/docs/QUOTA_MONITORING.md) | 每使用者每月 225M tokens;每日約 8.25M | coding base:每席次每月 168M;每月活躍 19 日的開發者 297M;每活躍日 15.7M | 席次平均低於(0.75 倍);活躍 19 日者高於(1.32 倍);每活躍日為每日預設的 1.9 倍 | AWS 的數字是上限的預設值,未附依據,也未說明是否計入 cache read;照模型的 base 強度,每月活躍超過 14.4 日的開發者就會碰到 225M |
| 用量筆記的示範混合:10,000 人、70 / 20 / 10、各取中位值 [D] | 每工作日約 16.5B tokens,98% 來自工程師 | 每平日 14.4B tokens,98% 來自 coding | 低 13% | 筆記以每開發者日 18M(13–23M 的中段)計,模型的 coding base 是 15.7M;OA 與 R&D 兩項相同(0.10B 與 0.25B) |
| Meta:85,000 名以上員工 30 天用了 60.2T tokens(2026-04,轉述 The Information)[C] [The Pragmatic Engineer](https://blog.pragmaticengineer.com/the-pulse-tokenmaxxing-as-a-weird-new-trend/) | 每員工每日曆日 23.6M tokens | 85,000 人、組合 D、high:15.5M;純 coding、high:30.5M | 組合 D 的 high 低於(0.66 倍);純 coding 的 high 高於(1.29 倍) | Meta 的平均涵蓋全體員工,且當時有排行榜鼓勵用量(最高的個人 30 天約 280B);模型的 high 只到 P90 的每活躍日 $30,不含無人值守的 agent(Pegatron 單一開發者每活躍日 697M) |

另外兩項本章補算的檢查 [D]:

- **每員工每月支出。** 10,000 人、base、$0.72/M 下,組合 A–E 為每員工每月 $8.85–$61.2,與 Ramp 的中位數 $46(2026-04)同一量級 [B] [Ramp: AI token cost for businesses](https://ramp.com/blog/ai-token-cost-for-businesses);coding 席次每月 $121,低於 Anthropic 所說每位開發者每月 $150–250,原因同上表第一列(活躍日數較少)。
- **尖峰形狀。** 模型的「尖峰分鐘 ÷ 當日平均分鐘」是 24 × s × k = 3.04(請求數),乘上 f 後各類 token 為 3.16–3.58。筆記由 Copilot 的多工曲線推得單一時區大型組織約 2.7–3.4(全球混合的 1.8–1.9 再乘 1.5–1.8);請求數與輸出、cache read 在範圍內,未快取輸入略高於上緣,另外模型還乘了 d = 1.2 把基準移到 P95 平日。

## 網站呈現建議

- **互動計算器是本章的主體。** 輸入:員工數、角色組合(OA / coding / R&D 三個滑桿,合計 100%,附 A–E 預設)、每個角色的用量級(low / base / high,可展開改 a、r、u、c、o)、時區分布(s:0.052–0.125,附「單一時區 0.11」與「全球 0.065」兩個預設)、P95 日係數 d(1.0–1.8)、每串流速度 v(40–1,000 tokens/s)、路由(每個角色分到各模型的比例,附 MX1–MX4 預設)。輸出:尖峰 RPM、三類 TPM、同時在途(平均與 99.9%)、每席次的日 / 週 / 月用量、月成本,以及平台單位換算(Anthropic ITPM / OTPM、Bedrock 5× / 10× / 15× / 1×、Azure PTU、Google GSU、Cerebras 兩個 bucket)與對預設配額的倍數、各池的 GPU 數與 hot / warm KV。
- **self-test。** JavaScript 版必須重現 `calc/out/selftest.json`:N = 100,000、組合 B、base、s = 0.11 時,m = 4,142.6、k = 1.15、RPM = 4,763.99、U = 24,467,592.05、C = 212,124,055.00、O = 3,130,196.96、L = 778.8605、L99.9 = 865.3755、平日 tokens = 89,981,700,000、每月 tokens = 2,155,890,064,350、Azure PTU = 20,443.66、Google GSU(Opus 5.5)= 3,239.13。這個向量只涵蓋 k 在下限、單一池的情形;上線前應再以 `model.json` 內 N = 1,000 的列(k = 1.47)與一個 MX 情境(GPU 與 KV)各驗一次。
- **96 列矩陣做成可排序、可篩選的表**(資料來自 `matrix.csv`),欄位切換「請求與 token」「併發與用量」「平台單位」三組;頁面預設只顯示 10,000 與 100,000 人。
- **圖。** 三類 TPM 用堆疊長條(對數軸),因為 cache read 比輸出大兩個數量級;「同一份流量在各平台的計量」用橫向長條;每員工尖峰 RPM 對人數用折線,標出 k 到達 1.15 的位置;敏感度用 tornado 圖。
- **模型組合。** 每個 MX 情境一張卡片(GPU 數、hot / warm KV、API 池的配額倍數),操作點做成可點開的出處;GPU 數旁固定標示「線性需求、speculative decoding 為固定 acceptance」。
- **可以刪的。** 靜態頁不放 1,000 與 50,000 人的整表(計算器可算);計數規則的長表移到第 11 章的平台參考,這裡只留四個差異與換算結果。
