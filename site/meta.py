"""Site map and per-chapter presentation settings. Leads restate each chapter's own opening conclusions."""

REV = '2026-10-05'      # revision date shown in the header (fact-check completed)
DATA_DATE = '2026-10-04'  # data as-of date
SITE_NAME = 'Inference ASIC Atlas'
SITE_ZH = '推論晶片圖鑑'

CHAPTERS = [
    dict(n=1, slug='01-silicon', src='01-silicon.md', nav='晶片與系統規格', en='SILICON', norm=True,
         h1='晶片與系統規格',
         lead='買得到的 HBM 旗艦每顆記憶體在 96 GiB（Trainium2）到 288 GB（MI355X）之間；SRAM 路線的 CS-4 整櫃只有 132 GB。'
              '有公開牌價、可自助租到的只有 Trainium2（僅 Capacity Blocks）、Inferentia2、TPU v6e / TPU7x、Hopper / Blackwell GPU 與 MI355X。',
         tabs=['規格總表', 'Trainium / Inferentia', 'TPU', 'GPU', 'Cerebras']),
    dict(n=2, slug='02-engines', src='02-engines.md', nav='推論引擎', en='ENGINES',
         h1='軟體堆疊與推論引擎',
         lead='同時涵蓋 GPU 與非 GPU 加速器的引擎只有 vLLM 與 SGLang。Trainium 仍在開發的只有 vLLM Neuron plugin（Beta），'
              'Inferentia2 的 NxD Inference 已進入維護模式，Cerebras 只有自己的專有堆疊；InferenceX 的 AgentX 快照中沒有任何一個引擎在所有模型與硬體上領先。',
         tabs=['支援矩陣', '優缺點', '編譯式與動態']),
    dict(n=3, slug='03-architectures', src='03-architectures.md', nav='模型架構支援', en='ARCHITECTURES',
         h1='模型架構支援',
         lead='四個開源旗艦全是 MoE 加混合式注意力。9 類架構中 NVIDIA GPU 有 7 類列為「支援」，AMD GPU 6 類、Google TPU 2 類、'
              'Trainium 1 類，Inferentia2 與 Cerebras 為 0 類；有 recipe 標示驗證硬體的旗艦，NVIDIA 有 4 個、AMD 有 3 個，其餘晶片為 0 個。',
         tabs=['架構與支援度', '模型清單']),
    dict(n=4, slug='04-open-models', src='04-open-models.md', nav='開源模型效能', en='OPEN MODELS', norm=True,
         h1='開源模型效能：Kimi、GLM、DeepSeek、Qwen',
         lead='Kimi K3、GLM-5.3、DeepSeek V4 Pro、V4.1 Flash 與 Qwen3.8 2.4T 在 2026-10-04 都沒有公開的 ASIC 端點；'
              '它們最快的端點為 185–723 t/s，依廠商自述全部是 GPU 上的軟體堆疊。自架的獨立量測只有 GPU（InferenceX）。',
         tabs=['模型規格', 'TPS 與 TTFT', '自架 benchmark', '供應矩陣']),
    dict(n=5, slug='05-proprietary-models', src='05-proprietary-models.md', nav='私有模型效能', en='PROPRIETARY MODELS',
         h1='私有模型效能：Claude、GPT、Gemini、Nova、Grok',
         lead='23 筆「私有模型 ↔ 晶片」的公開對應全部來自廠商聲明或媒體報導，沒有任何廠商公布每晶片吞吐量。'
              '獨立量測到的是每使用者速度：旗艦推理模型在第一方 API 約 45–92 tokens/s；Anthropic fast mode 在 Claude Opus 5.5 上以 2 倍價格換到 1.66 倍速度。',
         tabs=['晶片對應', 'TPS / TTFT 與 fast mode', '價格與 context']),
    dict(n=6, slug='06-technique-matrix', src='06-technique-matrix.md', nav='技術支援矩陣', en='TECHNIQUE MATRIX',
         h1='34 項推論技術在 6 種晶片上的支援狀態',
         lead=None,  # generated from the matrix counts
         tabs=['支援矩陣', '原因與替代做法']),
    dict(n=7, slug='07-long-context', src='07-long-context.md', nav='長上下文 200K / 1M', en='LONG CONTEXT',
         h1='長上下文：200K 與 1M',
         lead='公開且可重現的 1M-token 開源模型服務只出現在 NVIDIA 與 AMD 的 GPU 上。ASIC 路徑的公開上限低得多：'
              'Cerebras 公開雲與 Trainium 文件記載的配置約 131K，Google 公開的 TPU repository 內最大值為 98,304 tokens。',
         tabs=None),   # custom plan
    dict(n=8, slug='08-metrics', src='08-metrics.md', nav='效能與成本', en='PERFORMANCE AND COST',
         h1='效能與成本指標比較',
         lead='沒有任何單一 benchmark 同時涵蓋五個家族；同條件的跨硬體比較只有兩組：gpt-oss-120b 上 Cerebras 對最快的非 ASIC 端點為 5.5×，'
              'InferenceX 上 Ironwood 對 B200 / B300 為 1.05×（20 tok/s/user）。以牌價換算的每百萬 output tokens 成本，Ironwood 3 年承諾為 $1.44，B200 為 $1.88–4.00。',
         tabs=['效能', '成本與能效', '評分卡']),
    dict(n=9, slug='09-deployment', src='09-deployment.md', nav='部署模式', en='DEPLOYMENT',
         h1='部署模式',
         lead='五個家族中只有 GPU 在 6 類部署模式都買得到。Bedrock serverless 在四個開源家族中只提供 1 個當代旗艦（Kimi K3）；'
              '在 AWS 上要為開放權重旗艦取得容量確定性，只剩自管 GPU。',
         tabs=['部署選項', '各晶片的模式', '決策樹']),
    dict(n=10, slug='10-capacity', src='10-capacity.md', nav='容量計算器', en='CAPACITY PLANNER', norm=True,
         h1='從員工數算到尖峰 RPM 與 TPM',
         lead='輸入人數、角色組合與用量級，得到 P95 平日尖峰分鐘的 RPM、三類 TPM、同時在途請求數，以及各平台要申請的數字。'
              '結果全部是本文推算 [D]，每個參數的出處在第 11 章。',
         tabs=['方法與公式', '每人用量', '情境', '模型組合', '敏感度', '交叉檢查']),
    dict(n=11, slug='11-evidence', src='11-evidence.md', nav='估算依據', en='EVIDENCE',
         h1='估算依據與佐證',
         lead='佐證總表共 94 列：33 列直接採用量測或文件值，16 列在量測範圍內取值，14 列由廠商宣稱或金額換算，28 列是判斷值。'
              '三個角色的佐證強度依序是 coding、OA、R&D。',
         tabs=['佐證總表', '公開參考資料', '已知缺口']),
]

GROUPS = [
    ('硬體 HARDWARE', [1]),
    ('軟體 SOFTWARE', [2, 6]),
    ('模型 MODELS', [3, 4, 5]),
    ('情境 SCENARIOS', [7, 8, 9]),
    ('規劃 PLANNING', [10, 11, 12]),
]

# first sub-tab label when a section's opening block (before its first ###) is long enough to be a panel of its own
FIRST_SUB = {
    (7, '各推論技術在長上下文下有效或失效'): '判定表',
    (9, '選型決策樹'): '決策樹',
    (8, '效能總表'): '可比性',
    (10, '情境計算'): '總表',
}

FAMILIES = [
    dict(id='nv', tag='GPU', cls='gpu', name='NVIDIA GPU', engine='vLLM 0.30.0'),
    dict(id='amd', tag='AMD', cls='amd', name='AMD GPU', engine='ATOM、vLLM、SGLang'),
    dict(id='trn', tag='TRN', cls='trn', name='Trainium', engine='vLLM Neuron 0.24 Beta'),
    dict(id='inf', tag='INF', cls='inf', name='Inferentia2', engine='NxDI（維護模式）'),
    dict(id='tpu', tag='TPU', cls='tpu', name='Google TPU', engine='vLLM TPU 0.30.0'),
    dict(id='wse', tag='WSE', cls='wse', name='Cerebras', engine='公開 API'),
]
