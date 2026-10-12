# 第 1 章 晶片與系統規格

## 規格總表

截至 2026-10-04,買得到的 HBM 旗艦每顆記憶體在 96 GiB(Trainium2)到 288 GB(MI355X)之間、頻寬 2.9–8 TB/s(有資料者),單一 scale-up 域的總記憶體從 1,536 GiB(trn2.48xlarge)、約 20 TB(GB300 NVL72)到 1.77 PB(Ironwood 9,216 顆 pod);SRAM 路線相反,CS-4 整櫃 132 GB、129.6 PB/s,LPX 整櫃 128 GB、40 PB/s,對照 Vera Rubin NVL72 的 20.7 TB、1,400 TB/s。有公開牌價、可自助租到的只有 Trainium2(僅 Capacity Blocks)、Inferentia2、TPU v6e / TPU7x、Hopper / Blackwell GPU 與 MI355X;Trainium3、Vera Rubin NVL72、LPX、Helios、TPU 8i、CS-4 都沒有公開價格或自助 SKU,CS-3 只以 token API、Dedicated 或地端採購提供。

等級:A 獨立第三方量測;B 廠商 / 夥伴公布且揭露方法;C 廠商規格或宣稱;D 本文推算(附算式)。筆記標為「分析師」「產業媒體」「財報文件」者照原標示;公開牌價依各筆記原標(AWS 與 TPU 標 C,GPU 雲端 listing 標 B)。未另註日期的數字,讀取日為 2026-10-04。

### 每顆晶片

| 晶片 | 世代與狀態 | 製程 | 記憶體類型與容量 | 記憶體頻寬 | 標稱算力(註明精度) | 等級與來源 |
|---|---|---|---|---|---|---|
| AWS Trainium2 | 8 × NeuronCore-v3;GA 2024-12-03(Trn2 執行個體) | 5 nm(產業媒體;未點名晶圓廠) | 96 GiB HBM3(4 個 24 GB bank) | 2.9 TB/s | 1,299 TFLOPS FP8;667 TFLOPS BF16 | C;[Neuron docs: Trainium2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html)、[The Next Platform: Trainium4](https://www.nextplatform.com/2025/12/03/with-trainium4-aws-will-crank-up-everything-but-the-clocks/) |
| AWS Trainium3 | 8 × NeuronCore-v4(雙 chiplet);GA 2025-12-02(Trn3 UltraServers),2026 年初開始出貨 | 3 nm(AWS);TSMC N3P(SemiAnalysis) | 144 GiB HBM3E | 4.9 TB/s | 2,517 TFLOPS MXFP8 / MXFP4;671 TFLOPS BF16 | C;[Neuron docs: Trainium3](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium3.html)、[SemiAnalysis: Trainium3](https://newsletter.semianalysis.com/p/aws-trainium3-deep-dive-a-potential) |
| AWS Trainium4 | 已宣布未出貨(2025-12-02 宣布;2026-02-27 稱 2027 年開始交付) | 未公布 | 只稱 HBM 容量增加,未給數字 | Trainium3 的 4 倍(D:4 × 4.9 ≈ 19.6 TB/s) | FP4 至少 6 倍、FP8 3 倍(D:6 × 2.517 ≈ 15.1 PFLOPS;3 × 2.517 ≈ 7.6 PFLOPS) | C(倍數)、D(換算);[About Amazon: Trainium3 UltraServers](https://www.aboutamazon.com/news/aws/trainium-3-ultraserver-faster-ai-training-lower-cost)、[About Amazon: OpenAI](https://www.aboutamazon.com/news/aws/amazon-open-ai-strategic-partnership-investment) |
| AWS Inferentia2 | 2 × NeuronCore-v2;GA 2023-04-13(Inf2);無後繼晶片,軟體為維護模式 | 5 nm(產業媒體估計) | 32 GiB HBM | 820 GiB/s | 190 TFLOPS BF16 / FP16 / cFP8;380 TOPS INT8 | C;[Neuron docs: Inferentia2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html)、[AWS News Blog: Inf2 GA](https://aws.amazon.com/blogs/aws/amazon-ec2-inf2-instances-for-low-cost-high-performance-generative-ai-inference-are-now-generally-available/)、[The Next Platform: Trainium4](https://www.nextplatform.com/2025/12/03/with-trainium4-aws-will-crank-up-everything-but-the-clocks/) |
| Google TPU v6e(Trillium) | GA 2024-12-16 | 查無公開資料 | 32 GB HBM | 1,638 GBps | 918 TFLOPS BF16;1,836 TOPS int8 | C;[Google TPU v6e doc](https://docs.cloud.google.com/tpu/docs/v6e)、[Cloud TPU release notes](https://docs.cloud.google.com/tpu/docs/release-notes) |
| Google TPU7x(Ironwood) | Preview 2025-11-24;GA 2026-03-31 | 查無公開資料 | 192 GiB HBM(雙 chiplet 各 96 GB) | 7,380 GBps | 4,614 TFLOPS FP8(原生);2,307 TFLOPS BF16;無原生 FP4 | C;[Google TPU7x doc](https://docs.cloud.google.com/tpu/docs/tpu7x)、[Cloud TPU release notes](https://docs.cloud.google.com/tpu/docs/release-notes) |
| Google TPU 8i | 已宣布未出貨(2026-04-22;「generally available later this year」) | 查無公開資料 | 288 GB HBM(8 stack)加 384 MB SRAM | 8,601 GB/s | 10.1 PFLOPS FP4(FP8、BF16 未公布) | C;[Google Cloud: TPU 8 deep dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive)、[Google: eighth-generation TPU](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/eighth-generation-tpu-agentic-era/) |
| NVIDIA H200 | GA(AWS P5en 於 2024-12 推出) | 查無公開資料 | 141 GB(雲端 listing) | 查無公開資料 | 查無公開資料 | B(listing);[CoreWeave pricing](https://www.coreweave.com/pricing)、[Vantage: p5en](https://instances.vantage.sh/aws/ec2/p5en.48xlarge) |
| NVIDIA B200 | GA(AWS P6-B200 於 2025-05-15 推出) | 查無公開資料 | 180 GB(雲端 listing);GB200 NVL72 內 186 GB(D:13.4 TB ÷ 72) | 8 TB/s | 10 PFLOPS NVFP4(推論);FP8 各來源互異,見表後 | C、B(listing);[NVIDIA: Inside the Rubin platform](https://developer.nvidia.com/blog/inside-the-nvidia-rubin-platform-six-new-chips-one-ai-supercomputer/)、[CoreWeave pricing](https://www.coreweave.com/pricing)、[NVIDIA GB200 NVL72](https://www.nvidia.com/en-us/data-center/gb200-nvl72/) |
| NVIDIA B300 / Blackwell Ultra(GB300) | GA(AWS P6-B300、Nebius、OCI;CoreWeave 需洽業務) | 查無公開資料 | 270 GB(CoreWeave listing);GB300 NVL72 內約 278 GB(D:20 TB ÷ 72) | 8 TB/s(D:576 TB/s ÷ 72) | 15 PFLOPS dense FP4(D:1,080 ÷ 72) | B(listing)、D;[NVIDIA GB300 NVL72](https://www.nvidia.com/en-us/data-center/gb300-nvl72/)、[CoreWeave pricing](https://www.coreweave.com/pricing) |
| NVIDIA Rubin(Vera Rubin NVL72) | Preview(limited availability,CoreWeave 2026-09-30) | TSMC N3P(2025-08 roadmap 報導) | 288 GB HBM4 | 22 TB/s(2026-01 公告)對 19.4 TB/s(D:產品頁 1,400 TB/s ÷ 72) | 50 PFLOPS NVFP4 推論;35 PFLOPS NVFP4 訓練;17.5 PFLOPS FP8 / FP6(D:1,260 ÷ 72) | C、D;[NVIDIA: Inside the Rubin platform](https://developer.nvidia.com/blog/inside-the-nvidia-rubin-platform-six-new-chips-one-ai-supercomputer/)、[NVIDIA Vera Rubin NVL72](https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/)、[Tom's Hardware: NVIDIA roadmap](https://www.tomshardware.com/tech-industry/semiconductors/nvidia-enterprise-roadmap-rubin-rubin-ultra-feynman-and-silicon-photonics) |
| NVIDIA Groq 3 LPU(LP30) | 2026-08-24 宣布量產;無公開雲端 SKU | Samsung 4 nm 級(SF4X) | 500 MB SRAM(Tom's Hardware 寫 512 MB) | 150 TB/s | 1.2 PFLOPS FP8 | C;[NVIDIA Groq 3 LPX](https://www.nvidia.com/en-us/data-center/lpx/)、[StorageReview: LPX](https://www.storagereview.com/news/nvidia-groq-3-lpx-everything-we-know)、[SemiAnalysis: GTC 2026](https://newsletter.semianalysis.com/p/nvidia-the-inference-kingdom-expands) |
| AMD MI355X | GA(OCI 有牌價) | 查無公開資料 | 288 GB(OCI listing) | 查無公開資料 | 查無公開資料 | B(listing);[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| AMD MI455X | AMD 稱 2026 下半年量產部署;隨 Helios 於 2026 Q3 末開始出貨 | 2 nm / 3 nm(12 個 3D 堆疊 die) | 432 GB HBM4(12 × 36 GB) | 23.3 TB/s(AMD 產品頁)對 19.6 TB/s(2026-01 報導) | 最高 40 PFLOPS FP4;最高 20 PFLOPS FP8 | C;[AMD Instinct MI400](https://www.amd.com/en/products/accelerators/instinct/mi400.html)、[The Register: AMD](https://www.theregister.com/2026/01/07/mi500x_amd_ai/) |
| Cerebras WSE-3(CS-3) | 2024-03-13 發表(出貨起始日未見於所引來源) | TSMC 5 nm | 44 GB SRAM(整片晶圓) | 21 PB/s | 125 PFLOPS sparse FP16;dense 等效約 15.6 PFLOPS(分析師:125 ÷ 8) | C、分析師;[Cerebras: WSE-3 press release](https://www.cerebras.ai/press-release/cerebras-announces-third-generation-wafer-scale-engine)、[Cerebras S-1](https://www.sec.gov/Archives/edgar/data/2021728/000162828026025762/cerebras-sx1april2026.htm)、[SemiAnalysis: Cerebras](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) |
| Cerebras WSE-3T(CS-4) | 2026-08-18 宣布;廠商稱 2026 Q3 首批出貨,未獲證實 | 與 WSE-3 同一矽晶 | 44 GB SRAM(每片) | 43.2 PB/s(每片) | 250 PFLOPS sparse FP16(每片);dense 約 25 PFLOPS | C、分析師;[Cerebras: CS-4 press release](https://www.cerebras.ai/press-release/cerebras-unveils-cs-4-up-to-30-times-faster-than-gpu-based-solutions-3347356)、[TNW: CS-4](https://thenextweb.com/news/cerebras-cs-4-wafer-scale-ai-inference-system) |

- H200、B200、B300、MI355X 的「查無公開資料」是筆記缺口:NVIDIA H100 / H200 / DGX B200 與 AMD MI300 / MI350 系列產品頁因擷取被限流而未讀,不代表原廠未公布。
- Blackwell 每顆的 FP8 與 HBM 有三種說法:NVIDIA 產品頁的整櫃數字換算為每顆 10 PFLOPS FP8 / FP6、186–278 GB(D);Tom's Hardware(2025-12-05)列 B200 / B300 為 5.0 PFLOPS FP8、192 / 288 GB;The Register(2025-11-06)列 B200 為 4.5 PFLOPS FP8、192 GB;InferenceX 的 perf-changelog 也以每顆 288 GB 計 B300(「above B300's 288 GB HBM」),CoreWeave 的 270 若為 GiB 則約等於 290 GB(D)([NVIDIA GB200 NVL72](https://www.nvidia.com/en-us/data-center/gb200-nvl72/)、[Tom's Hardware: Trainium3](https://www.tomshardware.com/tech-industry/artificial-intelligence/amazon-launches-trainium3-ai-accelerator-competing-directly-against-blackwell-ultra-in-fp8-performance-new-trn3-gen2-ultraserver-takes-vertical-scaling-notes-from-nvidias-playbook)、[The Register: Ironwood](https://www.theregister.com/2025/11/06/googles_ironwood_tpus_ai/)、[InferenceX perf-changelog](https://github.com/SemiAnalysisAI/InferenceX/blob/main/inferencex-e2e/perf-changelog.yaml))。
- Rubin 的 HBM4 頻寬三度變動:13 TB/s(2025-08 roadmap)、22 TB/s(2026-01)、19.4 TB/s(D,現行產品頁);CoreWeave 2026-09-30 的上線文沿用產品頁數字,NVIDIA 未說明差異。
- 精度口徑不同,不可直接相比:Cerebras 的 PFLOPS 是 sparse FP16,GPU 是 dense;TPU 8i 的 10.1 PFLOPS 是 FP4,Ironwood 的 4,614 TFLOPS 是 FP8;AMD 的 FP4 是 MXFP4,NVIDIA 是 dense NVFP4。

### 每套系統

| 系統 | 晶片數 | 系統總記憶體 | 互連 | 功耗(若有) | 可得性與狀態 | 來源 |
|---|---|---|---|---|---|---|
| AWS trn2.48xlarge | 16 × Trainium2 | 1,536 GiB HBM | NeuronLink-v3,4×4 2D torus,每顆 1,024 GB/s;EFAv3 3,200 Gbps | 查無公開資料 | GA 2024-12-03;僅 Capacity Blocks(Ohio、Hyderabad) | (C)[Neuron docs: Trn2 architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trn2-arch.html)、[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| AWS Trn2 UltraServer | 64 × Trainium2 | 6,144 GiB HBM | 同上,另加跨 4 台的 ring(每顆 256 GB/s);EFA 12.8 Tbps | 查無公開資料 | Preview(2024-12-03 起,2026-10-04 仍標「available in preview」);無牌價 | (C)[AWS EC2 Trn2 page](https://aws.amazon.com/ec2/instance-types/trn2/) |
| AWS Trn3 Gen1 UltraServer | 64 × Trainium3 | 9,216 GiB HBM | NeuronLink-v4 加 NeuronSwitch-v1,all-to-all;EFA 12,800 Gbps | 查無公開資料 | GA 2025-12-02;無牌價、無 Capacity Blocks、無 Region 列表 | (C)[Neuron docs: Trn3 architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trn3-arch.html)、[AWS EC2 Trn3 page](https://aws.amazon.com/ec2/instance-types/trn3/) |
| AWS Trn3 Gen2 UltraServer | 144 × Trainium3 | 20,736 GiB HBM | 兩層 NeuronSwitch-v1,all-to-all;EFA 28,800 Gbps | 查無公開資料 | 軟體支援於 2026-04-09 至 2026-08-17 分批到位;客戶可用日與 Region 查無公開資料 | (C)[Neuron docs: Trn3 architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trn3-arch.html)、[Neuron docs: What's New](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/whats-new.html) |
| AWS inf2.48xlarge | 12 × Inferentia2 | 384 GiB HBM | NeuronLink-v2,每顆 192 GiB/s;網路 100 Gb | 查無公開資料 | GA;on-demand,us-east-1 每小時 $12.9813 | (C)[Neuron docs: Inf2 architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inf2-arch.html)、[AWS price list (us-east-1)](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json) |
| Google TPU v6e pod | 256 | 8,192 GB HBM(D:256 × 32 GB) | ICI 2D torus,每顆 800 GBps;DCN 每顆 100 Gbps | 查無公開資料 | GA 2024-12-16;on-demand 每 chip-hour $2.70 起 | (C)[Google TPU v6e doc](https://docs.cloud.google.com/tpu/docs/v6e)、[Cloud TPU pricing](https://cloud.google.com/tpu/pricing) |
| Google TPU7x(Ironwood)pod | 9,216(文件化 slice 最大 2,048;最小 VM 4 顆) | 1.77 PB HBM(4 顆 VM 為 768 GiB,D:4 × 192) | ICI 3D torus,每顆 1,200 GBps(9.6 Tb/s);DCN 每顆 100 Gbps | pod「nearly 10 MW」(D:每顆約 1.09 kW) | GA 2026-03-31;zone 僅 us-central1;on-demand 每 chip-hour $12.00 | (C)[Google TPU7x doc](https://docs.cloud.google.com/tpu/docs/tpu7x)、[Google Cloud: Ironwood GA post](https://cloud.google.com/blog/products/compute/ironwood-tpus-and-new-axion-based-vms-for-your-ai-workloads)、[Google: Ironwood](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/ironwood-tpu-age-of-inference/) |
| Google TPU 8i pod | 最多 1,152(1,024 active) | 約 332 TB HBM(D:1,152 × 288 GB) | Boardfly;ICI 19.2 Tb/s | 查無公開資料 | 已宣布未出貨(2026-04-22);無文件頁、價格、release note | (C)[Google Cloud: TPU 8 deep dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive)、[Google: eighth-generation TPU](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/eighth-generation-tpu-agentic-era/) |
| NVIDIA HGX H200 節點 | 8 × H200 | 1,128 GB HBM | 查無公開資料 | 查無公開資料 | GA;多雲有牌價 | (B)[CoreWeave pricing](https://www.coreweave.com/pricing) |
| NVIDIA HGX B200 節點 | 8 × B200 | 1,440 GB HBM | NVLink,每顆 1.8 TB/s | 查無公開資料 | GA;多雲有牌價 | (B、C)[CoreWeave pricing](https://www.coreweave.com/pricing)、[NVIDIA: Inside the Rubin platform](https://developer.nvidia.com/blog/inside-the-nvidia-rubin-platform-six-new-chips-one-ai-supercomputer/) |
| NVIDIA HGX B300 節點 | 8 × B300 | 2,144–2,160 GB HBM | 查無公開資料 | 查無公開資料 | GA(AWS P6-B300、Nebius、OCI);CoreWeave 需洽業務 | (B)[Thunder Compute: EC2 GPU](https://www.thundercompute.com/blog/ec2-gpu-instances)、[CoreWeave pricing](https://www.coreweave.com/pricing) |
| NVIDIA GB200 NVL72 | 72 × Blackwell 加 36 × Grace | 13.4 TB HBM3E | NVLink 130 TB/s | 查無公開資料 | GA;AWS Capacity Blocks、Azure、OCI、CoreWeave 有牌價 | (C)[NVIDIA GB200 NVL72](https://www.nvidia.com/en-us/data-center/gb200-nvl72/) |
| NVIDIA GB300 NVL72 | 72 × Blackwell Ultra 加 36 × Grace | 20 TB HBM | NVLink 130 TB/s | 查無公開資料 | GA;OCI 每 GPU-hour $18.00,CoreWeave 需洽業務 | (C)[NVIDIA GB300 NVL72](https://www.nvidia.com/en-us/data-center/gb300-nvl72/)、[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| NVIDIA Vera Rubin NVL72 | 72 × Rubin 加 36 × Vera | 20.7 TB HBM4 | NVLink 6:216 TB/s(產品頁)對 260 TB/s(2026-01、2026-03 公告) | 原廠未列;D:每櫃約 172–180 kW | Preview(limited availability,CoreWeave 2026-09-30);無牌價 | (C、D)[NVIDIA Vera Rubin NVL72](https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/)、[CoreWeave: Vera Rubin](https://www.coreweave.com/blog/cognition-becomes-first-customer-for-nvidia-vera-rubin-nvl72-on-coreweave-cloud) |
| NVIDIA Groq 3 LPX 機櫃 | 256 × Groq 3 LPU | 128 GB SRAM 加 12 TB DDR5 | scale-up 640 TB/s | 未揭露 | 2026-08-24 宣布量產;Nebius 首家採用,無公開 SKU | (C)[NVIDIA Groq 3 LPX](https://www.nvidia.com/en-us/data-center/lpx/)、[NVIDIA: LPX full production](https://nvidianews.nvidia.com/news/nvidia-groq-3-lpx-now-in-full-production-with-world-class-speed-for-agentic-ai) |
| AMD MI355X 節點(OCI BM.GPU.MI355X.8) | 8 × MI355X | 2,304 GB HBM | 查無公開資料 | 查無公開資料 | GA;OCI 每 GPU-hour $8.60 | (B)[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| AMD Helios | 72 × MI455X 加 18 × EPYC「Venice」 | 31 TB HBM4 | scale-up 260 TB/s(UALink over Ethernet);scale-out 43 TB/s | 查無公開資料 | 2026-07 宣布量產,2026 Q3 末開始出貨;無雲端 SKU 或價格 | (C)[AMD Instinct MI400](https://www.amd.com/en/products/accelerators/instinct/mi400.html)、[Moor Insights: AMD](https://moorinsightsstrategy.com/field-notes/amd-advancing-ai-2026-helios-ships-venice-swings-and-the-software-moat-narrows/) |
| Cerebras CS-3 | 1 片 WSE-3 | 44 GB SRAM(另有 KVSS 節點 6 TB DDR5) | 晶圓外 I/O 1.2 Tb/s(12 × 100GbE) | 約 25 kW(分析師) | 出貨中;token API、Dedicated、地端採購 | (C、分析師)[Cerebras: WSE-3 press release](https://www.cerebras.ai/press-release/cerebras-announces-third-generation-wafer-scale-engine)、[SemiAnalysis: Cerebras](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) |
| Cerebras CS-4 | 3 片 WSE-3T | 132 GB SRAM | 每櫃 7.2 Tb/s;Direct Wafer Links 最低 2 µs | 120–140 kW(Futurum、TNW)或 125–135 kW TDP(SemiAnalysis) | 2026-08-18 宣布;廠商稱 2026 Q3 首批出貨,未獲證實 | (C、分析師)[Cerebras: CS-4 press release](https://www.cerebras.ai/press-release/cerebras-unveils-cs-4-up-to-30-times-faster-than-gpu-based-solutions-3347356)、[Futurum: CS-4](https://futurumgroup.com/insights/cerebras-cs-4-makes-the-rack-the-new-chip-by-doubling-power-and-tripling-wafers/)、[SemiAnalysis: CS-4](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast) |

- 功耗欄多數空白:Trainium 任何一代的晶片與機櫃功耗、NVIDIA GB200 / GB300 / Vera Rubin NVL72 產品頁、LPX 與 Helios 都沒有機櫃功耗數字,TPU 各代的晶片 TDP 也查無公開資料。
- Ironwood 的每顆 1.09 kW 是把 Google 的「nearly 10 MW」除以 9,216 顆(D),涵蓋 Google 計入的全部項目,不是晶片 TDP;Vera Rubin 的 172–180 kW 算式見「NVIDIA / AMD GPU」一節。
- 「GA」不等於可自助取得:Trn3 UltraServers 在 2025-12-02 GA,十個月後仍無價格與 Region 列表。

## AWS Trainium / Inferentia

Trainium 目前能自助買到的只有 Trainium2:trn2.48xlarge 以 Capacity Blocks 計每 instance-hour $35.7608(每 chip-hour $2.235),有牌價的 Region 是 Ohio 與 Hyderabad;Trainium3 自 2025-12-02 GA 起沒有公開價格、Capacity Blocks 列或 Region 列表。亞太只有 Mumbai、Sydney、Melbourne(Trn1)與 Hyderabad、Melbourne(Trn2),Tokyo、Singapore、Taipei 都沒有 Trainium;Inferentia2 在 Tokyo、Singapore 等至少 14 個 Region 有 on-demand 牌價,但沒有 Inferentia3,軟體已進入維護模式。

### 各代晶片

記憶體與製程:

| 晶片 | 狀態與日期 | 製程 | NeuronCore | 裝置記憶體 | 記憶體頻寬 | 等級與來源 |
|---|---|---|---|---|---|---|
| Inferentia2 | GA 2023-04-13(Inf2);Neuron 安裝頁對照表列為用途「Inference」、狀態「Current」 | 5 nm(產業媒體估計) | 2 × NeuronCore-v2 | 32 GiB HBM | 820 GiB/s | C;[Neuron docs: Inferentia2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html)、[Neuron docs: Install](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/setup/index.html)、[The Next Platform: Trainium4](https://www.nextplatform.com/2025/12/03/with-trainium4-aws-will-crank-up-everything-but-the-clocks/) |
| Trainium1 | 2020-12 宣布(產業媒體);Trn1 GA,日期未擷取 | TSMC 7 nm、550 億個電晶體(產業媒體) | 2 × NeuronCore-v2 | 32 GiB(類型未載明) | 820 GiB/s | C;[Neuron docs: Trainium](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium.html)、[The Next Platform: Trainium4](https://www.nextplatform.com/2025/12/03/with-trainium4-aws-will-crank-up-everything-but-the-clocks/) |
| Trainium2 | 2023-11 宣布、2024-12 出貨(產業媒體);Trn2 GA 2024-12-03 | 5 nm(產業媒體;未點名晶圓廠) | 8 × NeuronCore-v3 | 96 GiB HBM3(4 個 24 GB bank) | 2.9 TB/s | C;[Neuron docs: Trainium2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html)、[AWS News Blog: Trn2 GA](https://aws.amazon.com/blogs/aws/amazon-ec2-trn2-instances-and-trn2-ultraservers-for-aiml-training-and-inference-is-now-available/) |
| Trainium3 | Trn3 UltraServers GA 2025-12-02;2026 年初開始出貨 | 3 nm(AWS);TSMC N3P 加 CoWoS-R(SemiAnalysis);「N3E or N3P」(Tom's Hardware) | 8 × NeuronCore-v4(雙 chiplet,各 4 核心) | 144 GiB HBM3E | 4.9 TB/s | C;[Neuron docs: Trainium3](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium3.html)、[SemiAnalysis: Trainium3](https://newsletter.semianalysis.com/p/aws-trainium3-deep-dive-a-potential)、[Tom's Hardware: Trainium3](https://www.tomshardware.com/tech-industry/artificial-intelligence/amazon-launches-trainium3-ai-accelerator-competing-directly-against-blackwell-ultra-in-fp8-performance-new-trn3-gen2-ultraserver-takes-vertical-scaling-notes-from-nvidias-playbook) |
| Trainium4 | 已宣布未出貨;2027 年開始交付 | 未公布(The Next Platform 猜 2 nm) | 未公布 | 未給數字;SemiAnalysis 稱 HBM4、8 stack、容量為 Trainium3 的 2 倍 | Trainium3 的 4 倍(D:約 19.6 TB/s) | C、產業媒體;[About Amazon: Trainium3 UltraServers](https://www.aboutamazon.com/news/aws/trainium-3-ultraserver-faster-ai-training-lower-cost)、[SemiAnalysis: Trainium3](https://newsletter.semianalysis.com/p/aws-trainium3-deep-dive-a-potential) |

算力與互連:

| 晶片 | 8-bit 算力 | 4-bit 算力 | BF16 / FP16 算力 | FP32 算力 | 晶片間互連 | 等級與來源 |
|---|---|---|---|---|---|---|
| Inferentia2 | 190 TFLOPS cFP8;380 TOPS INT8 | 無 | 190 TFLOPS | 47.5 TFLOPS | NeuronLink-v2(多晶片機型每顆 192 GiB/s) | C;[Neuron docs: Inferentia2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia2.html)、[Neuron docs: Inf2 architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inf2-arch.html) |
| Trainium1 | 190 TFLOPS cFP8;380 TOPS INT8 | 無 | 190 TFLOPS | 47.5 TFLOPS | NeuronLink-v2,每顆 384 GB/s | C;[Neuron docs: Trainium](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium.html) |
| Trainium2 | 1,299 TFLOPS FP8 | 不適用 | 667 TFLOPS | 181 TFLOPS | NeuronLink-v3,每顆 1.28 TB/s | C;[Neuron docs: Trainium2](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium2.html) |
| Trainium3 | 2,517 TFLOPS MXFP8 | 2,517 TFLOPS MXFP4(進 Tensor Engine 前轉為 MXFP8) | 671 TFLOPS | 183 TFLOPS | NeuronLink-v4,每顆 2.56 TB/s,經 NeuronSwitch-v1(PCIe Gen6) | C;[Neuron docs: Trainium3](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium3.html) |
| Trainium4 | Trainium3 的 3 倍(D:約 7.6 PFLOPS) | 至少 6 倍(D:至少 15.1 PFLOPS) | 未公布 | 未公布 | NVIDIA NVLink Fusion(AWS);UALink 224G 與 NVLink 448G 兩條路線(SemiAnalysis) | C、D、產業媒體;[About Amazon: Trainium3 UltraServers](https://www.aboutamazon.com/news/aws/trainium-3-ultraserver-faster-ai-training-lower-cost)、[SemiAnalysis: Trainium3](https://newsletter.semianalysis.com/p/aws-trainium3-deep-dive-a-potential) |

- Trainium3 對 Trainium2:FP8 加倍(1,299 → 2,517 TFLOPS)並新增 MXFP4,BF16 持平(667 → 671 TFLOPS);以 BF16 服務的模型只得到記憶體容量 1.5 倍、頻寬 1.7 倍與互連的好處。
- 實際的記憶體單位是 bank 而非晶片:Trainium2 的 4 個 24 GB bank 各由 2 個實體 NeuronCore-v3 共用,預設 LNC=2 下每個 logical core 擁有 24 GB。Trainium3 依同樣四 bank 配置為 36 GiB(D:144 ÷ 4),此配置出自 SemiAnalysis 的 benchmark 程式碼,AWS 晶片頁未載([Neuron docs: LNC](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-features/logical-neuroncore-config.html)、[InferenceX Trainium runner](https://github.com/SemiAnalysisAI/InferenceX/blob/main/operatorx/runners/trainium/runner.py))。
- 晶片內 SRAM:Trainium1 48 MiB、Trainium2 224 MiB(每核心 28 MB)、Trainium3 256 MiB(每核心 32 MiB);DMA 頻寬依序為 1、3.5、4.9 TB/s。
- AWS 文件自相矛盾兩處:Trainium2 的 sparse 算力(docs 2,563 TFLOPS,對 [AWS News Blog: Trn2 GA](https://aws.amazon.com/blogs/aws/amazon-ec2-trn2-instances-and-trn2-ultraservers-for-aiml-training-and-inference-is-now-available/) 的「up to 5.2 petaflops of sparse FP8」);Trainium3 的 NeuronLink-v4 頻寬(晶片頁 2.56 TB/s、系統表 2,048 GiB/s、EC2 頁「2TB/s of bandwidth per chip」（[AWS EC2 Trn3](https://aws.amazon.com/ec2/instance-types/trn3/)）、分層表合計 704 GB/s、SemiAnalysis 1.2 TB/s 單向)。
- 功耗:任何一代 Trainium 的晶片 TDP 與機櫃功耗都查無公開資料,AWS 只給相對值(Trn2 對 Trn1「3x more energy efficient」;Trainium3「40% better energy efficiency compared to previous generations」)。

### 系統與 UltraServer

| 系統 | 晶片數 | HBM 總量 | HBM 頻寬 | 標稱算力 | 晶片間互連 | EFA / 網路 | 狀態、等級與來源 |
|---|---|---|---|---|---|---|---|
| inf2.48xlarge | 12 × Inferentia2 | 384 GiB | 9,840 GiB/s | 2,280 TFLOPS BF16 | NeuronLink-v2,每顆 192 GiB/s | 100 Gb | GA;C;[Neuron docs: Inf2 architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inf2-arch.html) |
| trn1.32xlarge | 16 × Trainium1 | 512 GiB | 13,120 GiB/s(D:16 × 820;EC2 產品頁寫 9.8 TB/s) | 3,040 TFLOPS BF16;760 TFLOPS FP32(D:16 × 190;16 × 47.5) | NeuronLink-v2,2D torus | 800 Gbps | GA(日期未擷取);C、D;[Neuron docs: Trainium](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium.html)、[Neuron docs: Trn1/Trn1n architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trn1-arch.html)、[AWS EC2 Trn1 page](https://aws.amazon.com/ec2/instance-types/trn1/) |
| trn1n.32xlarge | 16 × Trainium1 | 512 GiB | 13,120 GiB/s(D:16 × 820) | 3,040 TFLOPS BF16(D:16 × 190) | NeuronLink-v2,2D torus | 1,600 Gbps | GA(日期未擷取);C、D;[Neuron docs: Trainium](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trainium.html)、[Neuron docs: Trn1/Trn1n architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trn1-arch.html)、[AWS EC2 Trn1 page](https://aws.amazon.com/ec2/instance-types/trn1/) |
| trn2.48xlarge / trn2u.48xlarge | 16 × Trainium2 | 1,536 GiB | 46.4 TB/s | 20.8 PFLOPS FP8;10.7 PFLOPS BF16;2.9 PFLOPS FP32 | NeuronLink-v3,4×4 2D torus,每顆 1,024 GB/s | EFAv3 3,200 Gbps | GA 2024-12-03;C;[Neuron docs: Trn2 architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trn2-arch.html) |
| Trn2 UltraServer(4 × trn2u.48xlarge) | 64 × Trainium2 | 6,144 GiB | 185.6 TB/s | 83.2 PFLOPS FP8;42.8 PFLOPS BF16;11.6 PFLOPS FP32 | 同上,另加跨 4 台的 ring,每顆 256 GB/s | 12.8 Tbps(EC2 頁);Neuron docs 表兩欄都寫 3,200 Gbps | Preview(2024-12-03 起,2026-10-04 仍是);C;[AWS EC2 Trn2 page](https://aws.amazon.com/ec2/instance-types/trn2/) |
| Trn3 Gen1 UltraServer | 64 × Trainium3(4 台 × 16) | 9,216 GiB | 313.6 TB/s | 161,088 TFLOPS MXFP8 / MXFP4;42,944 TFLOPS BF16;11,712 TFLOPS FP32 | NeuronLink-v4 加 NeuronSwitch-v1,all-to-all | 12,800 Gbps | GA 2025-12-02;C;[Neuron docs: Trn3 architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trn3-arch.html) |
| Trn3 Gen2 UltraServer | 144 × Trainium3(36 台 × 4) | 20,736 GiB | 705.6 TB/s | 362,448 TFLOPS MXFP8 / MXFP4;96,624 TFLOPS BF16;26,352 TFLOPS FP32 | 兩層 NeuronSwitch-v1,all-to-all | 28,800 Gbps | driver 支援 2026-04-09(SDK 2.29.0);客戶可用日查無公開資料;C;[Neuron docs: Trn3 architecture](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/trn3-arch.html) |

- 拓撲:Trn3 以 switched all-to-all 取代 2D torus,AWS 稱此設計對 MoE 模型與 autoregressive inference serving「especially optimized」。fabric 是 PCIe Gen6,每顆晶片有 4 條 x8 到機內 switch(256 GB/s)、5 條 x8 到跨機 switch(320 GB/s)、2 條 x8 跨櫃直連(128 GB/s)。
- 每顆晶片的 EFA(D:總量 ÷ 晶片數):Trn1 50 Gbps、Trn1n 100 Gbps、Trn2 與 Trn3 兩代皆 200 Gbps。
- AWS 的「up to 4.4x higher performance」「3.9x higher memory bandwidth」(Trn3 對 Trn2 UltraServer,[AWS EC2 Trn3 page](https://aws.amazon.com/ec2/instance-types/trn3/))是峰值規格比,不是工作負載量測(D:362.4 ÷ 83.2 = 4.36,其中 2.25 倍來自晶片數;705.6 ÷ 185.6 = 3.80)。
- 產業媒體:Gen1 為氣冷、Intel Xeon 主機,Gen2 為液冷、每 4 顆 Trainium3 配 1 顆 Graviton。Gen1 對應 NL32x2 Switched、Gen2 對應 NL72x2 Switched 是筆記比對晶片數所得,AWS 未公布([SemiAnalysis: Trainium3](https://newsletter.semianalysis.com/p/aws-trainium3-deep-dive-a-potential)、[Tom's Hardware: Trainium3](https://www.tomshardware.com/tech-industry/artificial-intelligence/amazon-launches-trainium3-ai-accelerator-competing-directly-against-blackwell-ultra-in-fp8-performance-new-trn3-gen2-ultraserver-takes-vertical-scaling-notes-from-nvidias-playbook))。

### 執行個體、價格與購買方式

每 chip-hour 為 AWS 公布值,未公布者以下式推算(D):

```latex
p_{\text{chip-hour}} = \frac{p_{\text{instance-hour}}}{N_{\text{chip}}}
```

| 執行個體 | 加速器 | On-demand($/h) | Capacity Blocks($/h) | 每 chip-hour($) | 購買方式 | 有牌價的 Region | 等級與來源 |
|---|---|---|---|---|---|---|---|
| inf2.xlarge | 1 × Inferentia2 | 0.7582 | 未列 | 0.7582 | on-demand | 至少 14 個,亞太見下表 | C;[AWS price list (us-east-1)](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json) |
| inf2.8xlarge | 1 × Inferentia2 | 1.9679 | 未列 | 1.9679 | on-demand | us-east-1 價;其餘未逐一擷取 | C;[AWS price list (us-east-1)](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json) |
| inf2.24xlarge | 6 × Inferentia2 | 6.4906 | 未列 | 1.0818(D) | on-demand | us-east-1 價;其餘未逐一擷取 | C、D;[AWS price list (us-east-1)](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json) |
| inf2.48xlarge | 12 × Inferentia2 | 12.9813 | 未列 | 1.0818(D) | on-demand | 13 個(Seoul 無此規格),亞太見下表 | C、D;[AWS price list (us-east-1)](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json) |
| trn1.2xlarge | 1 × Trainium1 | 1.34375 | 未列 | 1.34375 | on-demand | N. Virginia、Ohio、Oregon | C;[AWS price list (Ohio)](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28Ohio%29/Linux/index.json) |
| trn1.32xlarge | 16 × Trainium1 | 21.50 | 9.532 | on-demand 1.344(D);Capacity Blocks 0.596 | 兩者皆可 | on-demand:N. Virginia、Ohio、Oregon;Capacity Blocks 另加 Mumbai、Melbourne、Sydney、Stockholm | C、D;[AWS price list (Ohio)](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28Ohio%29/Linux/index.json)、[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| trn1n.32xlarge | 16 × Trainium1 | 24.78 | 未列 | 1.549(D) | on-demand | N. Virginia、Ohio、Oregon | C、D;[AWS price list (Ohio)](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28Ohio%29/Linux/index.json) |
| trn2.3xlarge | 1 × Trainium2 | 無牌價 | 2.235 | 2.235 | 僅 Capacity Blocks | Hyderabad、Melbourne、São Paulo | C;[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| trn2.48xlarge | 16 × Trainium2 | 無牌價 | 35.7608 | 2.235 | 僅 Capacity Blocks | Ohio、Hyderabad | C;[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| trn2u.48xlarge / Trn2 UltraServer | 16 / 64 × Trainium2 | 無牌價 | 未列 | 無公開價格 | 無自助途徑(Preview) | EC2 文件列 Trn2u 於 Hyderabad | C;[AWS EC2 instance types by Region](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-regions.html) |
| Trn3 UltraServers(家族名「Trn3pds」) | 64 或 144 × Trainium3 | 無牌價 | 未列 | 無公開價格 | 無自助途徑 | 無 | C;[AWS EC2 Trn3 page](https://aws.amazon.com/ec2/instance-types/trn3/)、[Neuron docs: UltraServer operator](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/deploy/eks/ultraserver-operator.html) |

- 價目日期:on-demand 取自 2026-09-25 發布的 AWS Linux 價目(查 35 個 Region);Capacity Blocks 頁與 Region 文件讀於 2026-10-04。
- Trn2 推出時的 Capacity Blocks 條款(2024-12-03):最多預留 64 個執行個體、最長 6 個月、最早 8 週前下訂([AWS News Blog: Trn2 GA](https://aws.amazon.com/blogs/aws/amazon-ec2-trn2-instances-and-trn2-ultraservers-for-aiml-training-and-inference-is-now-available/))。
- 2026-10-07 起 GPU 的 Capacity Blocks 再調漲,公告載明其餘價格不變,Trainium 不漲。同頁 B200 每 accelerator-hour $12.355、H200(P5en)$6.865,是 Trainium2 的 5.5 倍與 3.1 倍,2026-10-07 起為 6.4 倍與 3.5 倍(D:12.355 ÷ 2.235;6.865 ÷ 2.235;14.208 ÷ 2.235;7.895 ÷ 2.235);這是牌價比,不代表 tokens per dollar。
- 預留價只有 Trn1 的間接數字:Neuron benchmark 頁以「RI-Effective hourly rate」$8.197(trn1.32xlarge)計算,為 on-demand 的 38%(D:8.197 ÷ 21.50;[Neuron docs: Trn1 inference performance](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/benchmarks/trn1/trn1-inference-performance.html))。Trn2 與 Trn3 的 Savings Plan 或 Reserved 價格查無公開資料,Spot 未查。
- AWS 自家頁面不一致:Capacity Blocks 頁列 trn1.32xlarge 於 Stockholm,EC2 Region 頁沒有;EC2 Region 頁列 Trn2 於 Melbourne 與 São Paulo,但兩地只有 trn2.3xlarge 有 Capacity Blocks 價。

### 亞太 Region 對照

| Region | Inf2 on-demand(inf2.xlarge / inf2.48xlarge,$/h) | Trn1 | Trn2 | Trn3 |
|---|---|---|---|---|
| Tokyo | 1.1373 / 19.4719 | 無 | 無 | 無 |
| Seoul | 0.9098 / 未列(僅 xlarge) | 無 | 無 | 無 |
| Singapore | 1.0615 / 18.1738 | 無 | 無 | 無 |
| Sydney | 0.9857 / 16.8757 | 有;trn1.32xlarge 僅 Capacity Blocks | 無 | 無 |
| Mumbai | 0.9857 / 16.8757 | 有;trn1.32xlarge 僅 Capacity Blocks | 無 | 無 |
| Hyderabad | 無牌價 | 無 | 有;trn2.48xlarge 與 trn2.3xlarge 僅 Capacity Blocks,Trn2u 列於 Region 文件 | 無 |
| Melbourne | 無牌價 | 有;trn1.32xlarge 僅 Capacity Blocks | 有;僅 trn2.3xlarge 有 Capacity Blocks 價 | 無 |
| Taipei | 無 | 無 | 無 | 無 |
| Osaka、Hong Kong、Jakarta | 無牌價 | 無 | 無 | 無 |

來源(等級 C):[AWS price list (us-east-1)](https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/US%20East%20%28N.%20Virginia%29/Linux/index.json)(同一 URL 樣式逐 Region 查詢)、[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/)、[AWS EC2 instance types by Region](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-regions.html)。

- Taipei Region 沒有任何 accelerated-computing 執行個體。離台灣最近的 Inf2 在 Tokyo、Seoul(僅 xlarge)與 Singapore;最近的自助 Trainium2 在 Hyderabad 或 Melbourne,且只有 Capacity Blocks。
- Inf2 在 Tokyo 是美國價的 1.5 倍(D:19.4719 ÷ 12.9813)。
- Trn3 不在任何 Region 列表;Anthropic 2026-04-20 的協議提到「a meaningful expansion of international inference in Asia and Europe」,未指明 Region([About Amazon: Anthropic](https://www.aboutamazon.com/news/company-news/amazon-invests-additional-5-billion-anthropic-ai))。

### Inferentia 現況

- 沒有 Inferentia3:AWS Inferentia 頁(2026-09-25 更新)只列兩代,The Next Platform(2025-12-03)稱 AWS 自 Trainium2 起「stopped making Inferentia chips」。Benzinga 2024-12 的停止開發報導只讀到標題,AWS 也沒有第一方聲明說 Trainium 取代 Inferentia 或公布停售日([AWS Inferentia page](https://aws.amazon.com/ai/machine-learning/inferentia/)、[The Next Platform: Trainium4](https://www.nextplatform.com/2025/12/03/with-trainium4-aws-will-crank-up-everything-but-the-clocks/)、[Benzinga](https://www.benzinga.com/media/24/12/42356920/amazon-halts-inferentia-ai-chip-development-to-take-on-nvidia-how-trainium-is-shaping-up-to-be-the-new-weapon-in-ai-chip-wars))。
- 硬體仍在售:Inf1 與 Inf2 都在 2026-09-25 發布的 on-demand 價目中,Neuron 安裝頁的對照表把 Inf2 列為用途「Inference」、狀態「Current」,Inf1 為「Legacy inference」、「Legacy」([Neuron docs: Install](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/setup/index.html))。
- 軟體為維護模式:Inf2 的 Torch / XLA 推論路徑自 Neuron 2.31 起只收重大安全與錯誤修正,Inf1 的虛擬環境與 AMI 自 2.27(2025-12)起不再支援([Neuron docs: XLA inference maintenance](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/announcements/neuron2.x/announce-maintenance-pytorch-xla-inference.html)、[Neuron docs: Inf1 environments](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/announcements/neuron2.x/announce-eos-inf1-virtual-environments.html))。
- 容量上限:Inf2 每個核心 16 GB、整機最多 384 GiB(inf2.48xlarge);Inferentia1(2019)為 4 × NeuronCore-v1、8 GiB DRAM、50 GiB/s、64 TFLOPS FP16 / BF16([NxDI feature guide](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/developer_guides/feature-guide.html)、[Neuron docs: Inferentia](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/arch/neuron-hardware/inferentia.html))。

### 路線圖

| 項目 | 狀態(2026-10-04) | 關鍵日期 | 來源 |
|---|---|---|---|
| Trn3 Gen1 UltraServer(64 顆) | GA、出貨中;無牌價與 Region 列表 | GA 2025-12-02;SDK 2.27.0 支援 2025-12-19;2026-04-09 稱「just started shipping at the start of 2026」 | [About Amazon: Trainium3 UltraServers](https://www.aboutamazon.com/news/aws/trainium-3-ultraserver-faster-ai-training-lower-cost)、[Jassy shareholder letter](https://www.aboutamazon.com/news/company-news/amazon-ceo-andy-jassy-2025-letter-to-shareholders)、[Neuron docs: What's New](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/whats-new.html) |
| Trn3 Gen2 UltraServer(144 顆) | 軟體剛到位;客戶可用日與 Region 查無公開資料 | driver 2026-04-09(SDK 2.29.0);collectives ring 2026-05-21(2.30.0);one-rank-per-die ring、barrier、Mesh 2026-08-17(2.32.0) | [Neuron docs: What's New](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/about-neuron/whats-new.html) |
| Trainium4 | 已宣布未出貨 | 2025-12-02 公布倍數與 NVLink Fusion;2026-02-27「expected to begin delivery in 2027」;2026-04-09「about 18 months from broad availability」(D:約 2027-10);2026-07-31「already in development」 | [About Amazon: Trainium3 UltraServers](https://www.aboutamazon.com/news/aws/trainium-3-ultraserver-faster-ai-training-lower-cost)、[About Amazon: OpenAI](https://www.aboutamazon.com/news/aws/amazon-open-ai-strategic-partnership-investment)、[Jassy shareholder letter](https://www.aboutamazon.com/news/company-news/amazon-ceo-andy-jassy-2025-letter-to-shareholders)、[About Amazon: chips business](https://www.aboutamazon.com/news/aws/amazon-ai-chips-business-history) |
| 在 EC2 之外販售機櫃或晶片 | 未定 | 2026-04-29「a good chance we are going to sell racks in the next couple of years」;2026-07-30「a real chance we'll do that in the future」 | [Motley Fool: Q1 2026 call](https://www.fool.com/earnings/call-transcripts/2026/04/29/amazon-amzn-q1-2026-earnings-call-transcript/)、[Q2 2026 call transcript](https://stockanalysis.com/stocks/amzn/transcripts/657334-q2-2026/) |

- AWS 未說明 2025-12-02 的 GA 是否涵蓋 Gen2 硬體;2025-12 的 Trn3 教學需要 private beta 的 AMI 並註明「Please contact us to get access」([NxDI Trn3 gpt-oss-120b tutorial](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/libraries/nxd-inference/tutorials/trn3-gpt-oss-120b-tutorial.html))。
- SemiAnalysis(2025-12-04)預期 2026 年部署的 Trainium3 多數是氣冷的 NL32x2 Switched(「time to market SKU」),並警告 Trainium4「timelines may slip even further」;The Next Platform(2025-12-03)曾估「Late 2026 or early 2027」,早於 AWS 的 2027 說法。

### 供給與規模

| 日期 | 出處 | 內容 | 等級與來源 |
|---|---|---|---|
| 2025-10-29 | About Amazon(Project Rainier,更新版) | 「nearly half a million Trainium2 chips」;Claude 預計年底前用到「more than 1 million Trainium2 chips」 | C;[About Amazon: Project Rainier](https://www.aboutamazon.com/news/aws/aws-project-rainier-ai-trainium-chips-compute-cluster) |
| 2025-12-02 | Matt Garman,re:Invent | 已部署「More than 1 million Trainium chips」 | C;[DataCenterDynamics: Trn3 GA](https://www.datacenterdynamics.com/en/news/aws-makes-trainium3-ultraservers-generally-available/) |
| 2025-12-02 | About Amazon | EC2 UltraClusters 3.0 可串接「up to 1 million Trainium chips」 | C;[About Amazon: Trainium3 UltraServers](https://www.aboutamazon.com/news/aws/trainium-3-ultraserver-faster-ai-training-lower-cost) |
| 2026-02-05 | Andy Jassy,Q4 2025 法說會 | 「We've landed over 1.4 million Trainium two chips」;Trainium3 供給預計 2026 年中前幾乎全數被承諾 | C;[Motley Fool: Q4 2025 call](https://www.fool.com/earnings/call-transcripts/2026/02/05/amazon-amzn-q4-2025-earnings-call-transcript/) |
| 2026-02-27 | About Amazon(OpenAI) | OpenAI 承諾約 2 GW 的 Trainium 容量,涵蓋 Trainium3 與 Trainium4,2027 年起 | C;[About Amazon: OpenAI](https://www.aboutamazon.com/news/aws/amazon-open-ai-strategic-partnership-investment) |
| 2026-04-09 | Jassy 股東信 | Trainium2「has largely sold out」;Trainium3「nearly fully-subscribed」;Trainium4「A significant chunk … has already been reserved」 | C;[Jassy shareholder letter](https://www.aboutamazon.com/news/company-news/amazon-ceo-andy-jassy-2025-letter-to-shareholders) |
| 2026-04-20 | About Amazon(Anthropic) | Anthropic 十年支出承諾逾 $100 billion、最多 5 GW,涵蓋 Trainium2、Trainium3、Trainium4 | C;[About Amazon: Anthropic](https://www.aboutamazon.com/news/company-news/amazon-invests-additional-5-billion-anthropic-ai) |
| 2026-04-29 | Jassy,Q1 2026 法說會 | Trainium 營收承諾「over $225 billion」 | C;[Motley Fool: Q1 2026 call](https://www.fool.com/earnings/call-transcripts/2026/04/29/amazon-amzn-q1-2026-earnings-call-transcript/) |
| 2026-07-30 | Q2 2026 財報 | 晶片事業 run rate 超過 $25 billion(非僅 Trainium;股東信的口徑含 Graviton、Nitro) | C;[About Amazon: Q2 2026 results](https://www.aboutamazon.com/news/company-news/amazon-earnings-q2-2026-report) |
| 2026-07-31 | About Amazon | Claude「run on more than one million Trainium2 chips」 | C;[About Amazon: chips business](https://www.aboutamazon.com/news/aws/amazon-ai-chips-business-history) |

- Trainium3 與 Trainium4 的出貨量查無公開資料。
- 筆記推論:Rainier 約 50 萬顆、Claude 超過 100 萬顆、已到貨 140 萬顆三個數字互相吻合,Anthropic 用掉 Trainium2 機隊的大部分,留給 Bedrock 其他模型與外部 Trn2 客戶的是少數。

## Google TPU

Ironwood(TPU7x)是目前 GA 的推論旗艦:每顆 192 GiB HBM、7,380 GBps、4,614 TFLOPS FP8,pod 最大 9,216 顆;on-demand 每 chip-hour $12.00(us-central1),3 年承諾 $5.40,zone 只有 us-central1。第八代 TPU 8i(288 GB HBM、384 MB SRAM、10.1 PFLOPS FP4)於 2026-04-22 宣布「GA later this year」,到 2026-10-04 仍沒有文件頁、價格或 release note。

### 各代晶片

記憶體與狀態:

| 世代 | Google 定位 | 雲端狀態(2026-10-04) | HBM 容量 | HBM 頻寬 | SRAM(VMEM) | 原生加速 dtype | 等級與來源 |
|---|---|---|---|---|---|---|---|
| v5e | 訓練加推論,cost-efficient | 出貨中(GA 日期查無公開資料) | 16 GB | 800 GiBps(原文如此) | 未列 | int8、int4、bf16 | C;[Google TPU v5e doc](https://docs.cloud.google.com/tpu/docs/v5e) |
| v5p | 訓練 | 出貨中(GA 日期查無公開資料) | 95 GiB | 2,765 GBps | 未列 | int8、int4、bf16 | C;[Google TPU v5p doc](https://docs.cloud.google.com/tpu/docs/v5p) |
| v6e(Trillium) | 訓練、fine-tuning、serving | GA 2024-12-16 | 32 GB | 1,638 GBps | 未列 | int8、int4、bf16 | C;[Google TPU v6e doc](https://docs.cloud.google.com/tpu/docs/v6e) |
| TPU7x(Ironwood) | 「large-scale AI training and inference」 | Preview 2025-11-24;GA 2026-03-31 | 192 GiB | 7,380 GBps | 未公布(D:384 ÷ 3 ≈ 128 MB) | fp8_e4m3fn、fp8_e5m2、bf16 | C;[Google TPU7x doc](https://docs.cloud.google.com/tpu/docs/tpu7x)、[vLLM TPU support matrices](https://github.com/vllm-project/tpu-inference/tree/main/support_matrices) |
| TPU 8t | 大規模 pre-training | 已宣布未出貨(2026-04-22) | 216 GB(6 stack) | 6,528 GB/s | 128 MB | FP4 原生 | C;[Google Cloud: TPU 8 deep dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive)、[ServeTheHome: Hot Chips 2026](https://www.servethehome.com/googles-tpuv8s-for-training-and-inference-at-hot-chips-2026/) |
| TPU 8i | sampling、serving、reasoning | 已宣布未出貨(2026-04-22) | 288 GB(8 stack) | 8,601 GB/s | 384 MB | FP4 原生 | C;[Google Cloud: TPU 8 deep dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive)、[ServeTheHome: Hot Chips 2026](https://www.servethehome.com/googles-tpuv8s-for-training-and-inference-at-hot-chips-2026/) |

算力與互連:

| 世代 | BF16 算力 | 8-bit 算力 | FP4 算力 | ICI 拓撲 | ICI 頻寬(每顆,雙向) | DCN 頻寬(每顆) | 等級與來源 |
|---|---|---|---|---|---|---|---|
| v5e | 197 TFLOPS | 393 TOPS int8 | 無 | 2D torus | 400 GBps(4 port) | 每 8 顆主機 2 × 100 Gbps NIC | C;[Google TPU v5e doc](https://docs.cloud.google.com/tpu/docs/v5e) |
| v5p | 459 TFLOPS | 「FP8」459 TFLOPS(軟體模擬,無增益) | 無 | 3D torus | 1,200 GBps | 50 Gbps | C;[Google TPU v5p doc](https://docs.cloud.google.com/tpu/docs/v5p) |
| v6e(Trillium) | 918 TFLOPS | 1,836 TOPS int8 | 無 | 2D torus | 800 GBps(4 port) | 100 Gbps | C;[Google TPU v6e doc](https://docs.cloud.google.com/tpu/docs/v6e) |
| TPU7x(Ironwood) | 2,307 TFLOPS | 4,614 TFLOPS FP8(原生) | 無原生 FP4 | 3D torus | 1,200 GBps(9.6 Tb/s);每軸 200 GBps | 100 Gbps | C;[Google TPU7x doc](https://docs.cloud.google.com/tpu/docs/tpu7x) |
| TPU 8t | 未公布 | 未公布 | 12.6 PFLOPS | 3D torus | Ironwood 的 2 倍 | 最高為前代 4 倍(Virgo fabric) | C;[Google Cloud: TPU 8 deep dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive) |
| TPU 8i | 未公布 | 未公布 | 10.1 PFLOPS | Boardfly | 19.2 Tb/s | 未公布 | C;[Google Cloud: TPU 8 deep dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive)、[Google: eighth-generation TPU](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/eighth-generation-tpu-agentic-era/) |

- Ironwood 是第一代原生 FP8 的 TPU(先前世代以軟體模擬 FP8),沒有原生 FP4;MXU 自 v6e 起為 256×256([SemiAnalysis InferenceX: TPU](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam))。
- Ironwood 每顆為雙 chiplet,各含 1 個 TensorCore、2 個 SparseCore 與 96 GB HBM,JAX 把一顆晶片視為兩個 device;TPU 8i 以 2 個 TensorCore 加 1 個 Collectives Acceleration Engine 取代 4 個 SparseCore。
- 製程、die size、晶片 TDP 各代均查無公開資料;TPU 8i 的 FP8 與 BF16 算力未公布,所以「10.1 對 4.6 PFLOPS」不是同精度的 2.2 倍。

### Pod 規模與拓撲

| 世代 | pod 規模 | 拓撲細節 | 最小可租單位 | 冷卻與功耗 | 來源 |
|---|---|---|---|---|---|
| v6e | 256 顆 | 2D torus;每主機 8 顆 | 1 顆 VM(另有 4、8 顆);v6e-8 整機 VM 標為推論最佳化 | 未載明 | (C)[Google TPU v6e doc](https://docs.cloud.google.com/tpu/docs/v6e) |
| TPU7x(Ironwood) | 9,216 顆,共享 HBM 1.77 PB、42.5 exaflops;文件化 slice 由 2x2x1(4 顆)到 8x16x16(2,048 顆) | 3D torus;4×4×4 cube 共 64 顆為一櫃,最大 pod 用 144 個 cube 與 48 台 144×144 OCS;cube 內走銅線,cube 間走 800G 光學 | 4 顆 VM(224 vCPU、960 GB RAM) | 液冷;pod「nearly 10 MW」 | (C)[Google TPU7x doc](https://docs.cloud.google.com/tpu/docs/tpu7x)、[Google: Ironwood](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/ironwood-tpu-age-of-inference/)、[SemiAnalysis: TPUv7](https://newsletter.semianalysis.com/p/tpuv7-google-takes-a-swing-at-the) |
| TPU 8t | superpod 9,600 顆、300 櫃(D:每櫃 32 顆);HBM 2 PB;121 EFLOPS(FP4) | 3D torus;Virgo fabric 可串接超過 134,000 顆,bisection 頻寬 47 Pb/s | 每 tray 4 顆 | 第四代液冷;光學元件首次液冷 | (C)[Google Cloud: TPU 8 deep dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive)、[Google: eighth-generation TPU](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/eighth-generation-tpu-agentic-era/)、[ServeTheHome: Hot Chips 2026](https://www.servethehome.com/googles-tpuv8s-for-training-and-inference-at-hot-chips-2026/) |
| TPU 8i | 最多 1,152 顆(1,024 active) | Boardfly:4 顆 board、8 個 board 一個 group、36 個 group 經 OCS 相連,最多 7 hop(8×8×16 torus 為 16 hop) | 每 tray 4 顆;每顆 Axion CPU 配 2 顆 TPU | 第四代液冷 | (C)[Google Cloud: TPU 8 deep dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive) |

Ironwood 每顆晶片的 pod 級功耗(D),含 Google 計入「nearly 10 MW」的全部項目:

```latex
P_{\text{chip}} \approx \frac{10\ \text{MW}}{9{,}216} \approx 1.09\ \text{kW}
```

### 價格與承諾折扣

牌價讀於 2026-10-04,單位為美元每 chip-hour(等級 C,牌價;[Cloud TPU pricing](https://cloud.google.com/tpu/pricing))。

| 世代 | Region | On-demand | DWS Flex-start | DWS Calendar | 1 年承諾 | 3 年承諾 |
|---|---|---|---|---|---|---|
| Ironwood | us-central1(Iowa) | 12.00 | 6.00 | 8.40 | 8.40 | 5.40 |
| Ironwood | europe-west2(London) | 13.20 | 6.00 | 8.40 | 9.24 | 5.94 |
| Trillium(v6e) | us-east1、us-east5 | 2.70 | 1.35 | 1.89 | 1.89 | 1.22 |
| Trillium(v6e) | europe-west4(Amsterdam) | 2.97 | 1.35 | 1.89 | 2.08 | 1.34 |
| Trillium(v6e) | asia-northeast1(Tokyo) | 3.24 | 1.35 | 1.89 | 2.27 | 1.46 |
| v5p | us-east5、us-east1 | 4.20 | 2.10 | 2.94 | 2.94 | 1.89 |
| v5e | us-central1、us-east5、us-west1、us-west4 | 1.20 | 0.60 | 0.84 | 0.84 | 0.54 |
| v5e | us-south1(Dallas) | 1.416 | 0.60 | 0.84 | 0.9912 | 0.6372 |
| v5e | europe-west4、asia-southeast1 | 1.56 | 0.60 | 0.84 | 1.092 | 0.702 |

- 折扣(D,以 us-central1 的 Ironwood 計):1 年承諾與 DWS Calendar 為 on-demand 的 70%,3 年承諾 45%,DWS Flex-start 50%(8.40 ÷ 12.00;5.40 ÷ 12.00;6.00 ÷ 12.00)。價目頁把 3 年承諾定位於「512+ cores」、1 年承諾於「32-512 cores」。
- Ironwood 的 on-demand 是 Trillium 的 4.4 倍(D:12.00 ÷ 2.70);每 GB HBM 每小時為 Ironwood $0.0625、Trillium $0.084、v5e $0.075、v5p $0.044(D:牌價 ÷ HBM 容量)。
- 最小的 Ironwood 形狀(4 顆 VM)on-demand 每小時 $48,約每月 $35,000(D:4 × 12.00)。
- 計費以 node 處於 READY 的 chip-hour 計,Spot 價格為動態;價目頁沒有 TPU 8t 或 8i。
- 牌價與大客戶成本差距大:SemiAnalysis 估 Anthropic 向 GCP 取得的成本為每 TPU-hour $1.60、Google 內部 TCO 為每 chip-hour $1.03(分析師模型,非量測;[SemiAnalysis: TPUv7](https://newsletter.semianalysis.com/p/tpuv7-google-takes-a-swing-at-the)、[SemiAnalysis InferenceX: TPU](https://inferencex.semianalysis.com/blog/tpu-inferencex-full-steam))。

### 取用途徑、zone 與 quota

| 途徑 | 可用世代與形狀 | 狀態與限制 | 來源 |
|---|---|---|---|
| GKE | Ironwood 需 Standard 1.34.0-gke.2201000 或 Autopilot 1.34.1-gke.3084001 以上;可選 on-demand、Spot、Flex-start(最長 7 天)、calendar-mode 未來預留(最長 90 天)、長期預留 | 可用;on-demand「no guarantee that enough on-demand resources will be available」 | [Ironwood in GKE](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/tpu-ironwood)、[About TPUs in GKE](https://docs.cloud.google.com/kubernetes-engine/docs/concepts/tpus) |
| Compute Engine | TPU VM 與 managed instance group | GA 2026-06-01;舊的 Cloud TPU API 不再積極開發 | [Cloud TPU release notes](https://docs.cloud.google.com/tpu/docs/release-notes)、[TPUs in Compute Engine](https://docs.cloud.google.com/tpu/docs/tpus-in-compute-engine) |
| Vertex AI / Agent Platform 線上推論 | 單主機的 v5e、v6e、TPU7x(`tpu7x-standard-4t`) | 單主機可用;多主機為 Public preview | [Agent Platform: TPU online inference](https://docs.cloud.google.com/gemini-enterprise-agent-platform/machine-learning/predictions/use-tpu) |
| All Capacity mode | v6e、TPU7x;預留制,可見完整拓撲 | 可用;不適用 Compute Engine SLA | [All Capacity mode](https://docs.cloud.google.com/tpu/docs/all-capacity-overview) |
| 直接購買機櫃 | Ironwood:首批 40 萬顆(約 $10 billion 的成品機櫃)由 Broadcom 直接賣給 Anthropic | 分析師:目前只見 Anthropic 規模的買家 | [SemiAnalysis: TPUv7](https://newsletter.semianalysis.com/p/tpuv7-google-takes-a-swing-at-the) |
| TPU 8t / 8i | 興趣表單 | 已宣布未出貨 | [Google: eighth-generation TPU](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/eighth-generation-tpu-agentic-era/) |

| 世代 | Zone | 預設 on-demand quota(每專案每 zone) | 預設 preemptible quota |
|---|---|---|---|
| v5e | us-central1-a、us-south1-a、us-west1-c、us-west4-a、europe-west4-b | 512 cores | 1,536 cores |
| v5p | us-central1-a、us-east5-a、europe-west4-b | 128 cores | 768 cores |
| v6e | us-central1-b、us-east1-d、us-east5-a、us-east5-b、us-south1-ai1b、europe-west4-a、asia-northeast1-b、southamerica-west1-a | 512 cores | 1,536 cores |
| TPU7x | us-central1-ai1a、us-central1-c | 查無公開資料 | 查無公開資料 |

來源(等級 C):[TPU regions and zones](https://docs.cloud.google.com/tpu/docs/regions-zones)、[Cloud TPU quotas](https://docs.cloud.google.com/tpu/docs/quota);quota 為 Cloud TPU API 的預設值,GKE 與 Compute Engine 改用 Compute Engine quota。

- 亞洲在 zone 頁上只有 v6e 的 asia-northeast1-b(Tokyo,on-demand 每 chip-hour $3.24);TPU7x 的 zone 全在 us-central1。
- 價目頁與 zone 頁不一致:價目頁有 Ironwood 的 europe-west2 價格,zone 頁卻只列 us-central1;v5e 的 asia-southeast1 與 v5p 的 us-east1 也只見於價目頁。美國以外的買家需向 Google 確認實際 zone。
- 容量:v6e 與 v5p 追加 preemptible quota 的自動核准門檻在所有 zone 都是 0 cores,zone 頁註明「TPU types with higher numbers of chips or cores are available only in limited quantities」;Ironwood 的交期與 Spot 價位查無公開資料。

### 第八代的狀態

- 2026-04-22 宣布 TPU 8t(訓練)與 TPU 8i(推論),原文為「Both chips will be generally available later this year」與「will be available to Cloud customers soon」([Google: eighth-generation TPU](https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/eighth-generation-tpu-agentic-era/)、[Google Cloud: Next '26 infrastructure](https://cloud.google.com/blog/products/compute/ai-infrastructure-at-next26))。
- 到 2026-10-04:release notes 沒有 TPU 8 條目,價目頁沒有第八代,文件頁 `tpu8i` 與 `tpu8t` 回傳 404([Cloud TPU release notes](https://docs.cloud.google.com/tpu/docs/release-notes))。
- 軟體先行:vLLM TPU backend 已有「TPU v8i」裝置處理,每個 JAX device 144 GB,即每顆 288 GB 分給兩個核心([vLLM TPU utils.py](https://github.com/vllm-project/tpu-inference/blob/main/tpu_inference/utils.py))。
- 未經證實且與原廠矛盾:TNW(2026-04-22)稱第八代採 TSMC 2 nm、時程為 2027 年底,HBM stack 數為 8t 8 個、8i 6 個;Google 在 Hot Chips 2026 的說法是 8t 6 個、8i 8 個([TNW: TPU 8](https://thenextweb.com/news/google-ironwood-tpu-inference-cloud-next)、[ServeTheHome: Hot Chips 2026](https://www.servethehome.com/googles-tpuv8s-for-training-and-inference-at-hot-chips-2026/))。
- Ironwood 的 GA 日期有三種說法:Google Cloud 部落格 2025-11-06 稱「will be generally available in the coming weeks」,release notes 記 Preview 2025-11-24、GA 2026-03-31,TNW 稱在 Cloud Next 2026 才 GA;本章採 release notes([Google Cloud: Ironwood GA post](https://cloud.google.com/blog/products/compute/ironwood-tpus-and-new-axion-based-vms-for-your-ai-workloads))。
- 機型字串也不一致:TPU7x 文件稱所有拓撲都用 `tpu7x-standard-4t`,Google 的 Qwen3-32B recipe 卻建立 `tpu7x-standard-1t`(1 顆)的 node pool([Qwen3-32B recipe](https://github.com/AI-Hypercomputer/tpu-recipes/tree/main/inference/ironwood/vLLM/Qwen3-32B))。

## NVIDIA / AMD GPU

有公開價格的最新世代仍是 Blackwell:B200 on-demand 每 GPU-hour 在 Lambda、Nebius、CoreWeave 為 $6.69–8.60,在 AWS 與 OCI 約 $14;Vera Rubin NVL72(72 顆 Rubin,每顆 288 GB HBM4,整櫃 20.7 TB)2026-09-30 才在 CoreWeave 以 limited availability 上線,AMD Helios(72 顆 MI455X,每顆 432 GB,整櫃 31 TB)2026 Q3 末才開始出貨。價格方向是漲:AWS Capacity Blocks 在 2026-07-01 調漲約 20%,2026-10-07 再調 15%。

### NVIDIA:Hopper、Blackwell、Vera Rubin

每顆 GPU:

| GPU | 每顆 HBM | 記憶體頻寬 | 標稱算力 | scale-up 連結(每顆) | 狀態(2026-10-04) | 等級與來源 |
|---|---|---|---|---|---|---|
| H100(Hopper) | 80 GB(雲端 listing) | 查無公開資料 | 查無公開資料 | 查無公開資料 | GA;多雲可租 | B(listing);[CoreWeave pricing](https://www.coreweave.com/pricing)、[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| H200(Hopper) | 141 GB(雲端 listing) | 查無公開資料 | 查無公開資料 | 查無公開資料 | GA;AWS P5en 於 2024-12 推出 | B(listing);[CoreWeave pricing](https://www.coreweave.com/pricing)、[Vantage: p5en](https://instances.vantage.sh/aws/ec2/p5en.48xlarge) |
| B200(Blackwell,HGX 8-GPU) | 180 GB(雲端 listing) | 8 TB/s | 10 PFLOPS NVFP4(推論與訓練) | NVLink 1.8 TB/s | GA;AWS P6-B200 於 2025-05-15 推出 | C、B(listing);[NVIDIA: Inside the Rubin platform](https://developer.nvidia.com/blog/inside-the-nvidia-rubin-platform-six-new-chips-one-ai-supercomputer/)、[CoreWeave pricing](https://www.coreweave.com/pricing)、[Vantage: p6-b200](https://instances.vantage.sh/aws/ec2/p6-b200.48xlarge) |
| B300(Blackwell Ultra,HGX 8-GPU) | 270 GB(CoreWeave listing);AWS 8-GPU 節點列 2,144 GB | 查無公開資料 | 查無公開資料 | 查無公開資料 | GA:AWS(P6-B300)、Nebius、OCI;CoreWeave 需洽業務 | B(listing);[CoreWeave pricing](https://www.coreweave.com/pricing)、[Thunder Compute: EC2 GPU](https://www.thundercompute.com/blog/ec2-gpu-instances) |
| Blackwell(GB200 NVL72 內) | 186 GB(D:13.4 TB ÷ 72) | 8 TB/s(D:576 ÷ 72) | 10 PFLOPS dense NVFP4(D:720 ÷ 72);10 PFLOPS FP8 / FP6 | 1.8 TB/s(D:130 ÷ 72) | GA | D;[NVIDIA GB200 NVL72](https://www.nvidia.com/en-us/data-center/gb200-nvl72/) |
| Blackwell Ultra(GB300 NVL72 內) | 約 278 GB(D:20 TB ÷ 72);雲端列 279 GB | 8 TB/s(D:576 ÷ 72) | 15 PFLOPS dense FP4(D:1,080 ÷ 72);10 PFLOPS FP8 / FP6 | 1.8 TB/s(D:130 ÷ 72) | GA | D;[NVIDIA GB300 NVL72](https://www.nvidia.com/en-us/data-center/gb300-nvl72/) |
| Rubin(Vera Rubin NVL72 內) | 288 GB HBM4 | 22 TB/s(2026-01)對 19.4 TB/s(D:1,400 ÷ 72) | 50 PFLOPS NVFP4 推論;35 PFLOPS NVFP4 訓練;17.5 PFLOPS FP8 / FP6(D:1,260 ÷ 72) | NVLink 6:3.6 TB/s(2026-01、2026-03)對 3.0 TB/s(D:216 ÷ 72) | Preview(limited availability,CoreWeave 2026-09-30) | C、D;[NVIDIA: Inside the Rubin platform](https://developer.nvidia.com/blog/inside-the-nvidia-rubin-platform-six-new-chips-one-ai-supercomputer/)、[NVIDIA Vera Rubin NVL72](https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/) |
| Rubin Ultra | 每 package 1 TB HBM4E(4 個 reticle 尺寸的 die) | 32 TB/s(2025-08 roadmap) | 每 package 100 PFLOPS FP4 推論;每 package 3,600 W | NVLink 7;每顆每方向 14.4 Tbit/s | 已宣布未出貨(2027 下半年) | C;[Tom's Hardware: NVIDIA roadmap](https://www.tomshardware.com/tech-industry/semiconductors/nvidia-enterprise-roadmap-rubin-rubin-ultra-feynman-and-silicon-photonics)、[SemiAnalysis: GTC 2026](https://newsletter.semianalysis.com/p/nvidia-the-inference-kingdom-expands) |

機櫃級系統:

| 系統 | 組成 | GPU 記憶體 | 記憶體頻寬 | 標稱算力 | scale-up | 功耗與冷卻 | 狀態、等級與來源 |
|---|---|---|---|---|---|---|---|
| GB200 NVL72 | 72 × Blackwell 加 36 × Grace | 13.4 TB HBM3E | 576 TB/s | NVFP4 1,440(sparse)/ 720(dense)PFLOPS;FP8 / FP6 720 PFLOPS;FP16 / BF16 360 PFLOPS | NVLink 130 TB/s | 功耗查無公開資料 | GA;C;[NVIDIA GB200 NVL72](https://www.nvidia.com/en-us/data-center/gb200-nvl72/) |
| GB300 NVL72 | 72 × Blackwell Ultra 加 36 × Grace | 20 TB(「fast memory」合計 37 TB) | 最高 576 TB/s | FP4 1,440(sparse)/ 1,080(dense)PFLOPS;FP8 / FP6 720 PFLOPS;FP16 / BF16 360 PFLOPS | NVLink 130 TB/s | 功耗查無公開資料 | GA;C;[NVIDIA GB300 NVL72](https://www.nvidia.com/en-us/data-center/gb300-nvl72/) |
| Vera Rubin NVL72 | 72 × Rubin 加 36 × Vera(3,168 核心) | 20.7 TB HBM4 | 1,400 TB/s | NVFP4 推論 3,600 PFLOPS;NVFP4 訓練 2,520 PFLOPS;FP8 / FP6 訓練 1,260 PFLOPS | NVLink 6:216 TB/s(產品頁)對 260 TB/s(2026-01、2026-03 公告) | 全液冷,45 °C 溫水進水,約 4,000 lb;功耗查無公開資料 | Preview(limited availability,CoreWeave 2026-09-30);C;[NVIDIA Vera Rubin NVL72](https://www.nvidia.com/en-us/data-center/vera-rubin-nvl72/)、[NVIDIA: Vera Rubin POD](https://developer.nvidia.com/blog/nvidia-vera-rubin-pod-seven-chips-five-rack-scale-systems-one-ai-supercomputer/)、[CoreWeave: Vera Rubin](https://www.coreweave.com/blog/cognition-becomes-first-customer-for-nvidia-vera-rubin-nvl72-on-coreweave-cloud) |
| Rubin Ultra Kyber 機櫃(2025 年稱「NVL576」,2026 年稱「NVL144」) | 144 個 Rubin Ultra package(36 個 blade,各 4 顆 GPU 加 2 顆 Vera);72 台 NVLink 7 switch | 365 TB「fast memory」 | 4.6 PB/s(HBM4E) | 15 EFLOPS FP4 推論;5 EFLOPS FP8 訓練 | NVLink 7,1.5 PB/s | 600 kW | 已宣布未出貨(2027 下半年);C;[DCD: Rubin Ultra rack](https://www.datacenterdynamics.com/en/news/nvidias-rubin-ultra-nvl576-rack-expected-to-be-600kw-coming-second-half-of-2027/)、[SemiAnalysis: GTC 2026](https://newsletter.semianalysis.com/p/nvidia-the-inference-kingdom-expands) |

- 命名在兩年間翻轉:2025 年按 GPU die 計(「Vera Rubin NVL144」是 72 個雙 die package),2026 年按 package 計(今年出貨的叫 Vera Rubin NVL72,Kyber 機櫃叫 NVL144,「NVL576」「NVL1152」改指以 co-packaged optics 串接的多櫃域)。引用「NVL144」必須註明是哪一年的用法。
- GB300 的 dense FP4 1,080 PFLOPS 需複核:頁面擷取結果為「1440 | 10802 PFLOPS」,筆記判讀為 1,440(sparse)、1,080(dense)加註腳標記 2。
- Vera Rubin NVL72 對 GB200 NVL72(D):NVFP4 推論算力 5 倍(3,600 ÷ 720)、GPU 記憶體 1.54 倍(20.7 ÷ 13.4)、記憶體頻寬 2.4 倍(1,400 ÷ 576)。頻寬成長遠小於算力,與 NVIDIA 另加 LPX 作 decode 加速一致。
- CPU 側記憶體:GB200 / GB300 NVL72 為 17 TB LPDDR5X(14 TB/s),Vera Rubin NVL72 最高 54 TB LPDDR5X。Vera Rubin POD(2026-03-16 宣布)為 40 櫃、1,152 顆 Rubin(D:16 個 NVL72)加 Vera CPU、LPX、BlueField-4 STX 與 Spectrum-6 SPX 機櫃。
- 機櫃價格只有分析師估計(Futurum,TrendForce 2026-07-21 轉述):Vera Rubin 每櫃約 $3.5–4.0 million,Helios 約 $5.0–5.5 million([TrendForce: Helios](https://www.trendforce.com/news/2026/07/21/news-amds-first-rack-scale-ai-system-helios-challenges-nvidia-with-hbm4-memory-edge-but-reportedly-comes-at-a-higher-price/))。

Vera Rubin NVL72 的機櫃功耗沒有原廠數字,以下由 NVIDIA「100 MW AI factory」的 2 ZFLOPS 與 12 PB HBM4 反推(D),含 NVIDIA 假設的全部設施開銷:

```latex
P_{\text{rack}} \approx \frac{100{,}000\ \text{kW}}{2\ \text{ZFLOPS} \div 3.6\ \text{EFLOPS}} = 180\ \text{kW}
```

```latex
P_{\text{rack}} \approx \frac{100{,}000\ \text{kW}}{12\ \text{PB} \div 20.7\ \text{TB}} = 172\ \text{kW}
```

2025-08 roadmap 報導的每顆 Rubin 1,800 W 則對應 72 顆 GPU 合計 130 kW(D:72 × 1.8 kW);兩者都是估計,不是機櫃規格。

權重所需記憶體的粗估式(D;P 為參數量,b 為每個權重的位元數;未計 KV cache 與執行期開銷):

```latex
M_{\text{weights}}\,[\text{GB}] = P\,[10^{9}] \times \frac{b}{8}
```

- 依此式,1.0T 參數的模型在 FP8 下需 1,000 GB:8 × H200(1,128 GB)只剩 128 GB,8 × B200(1,440 GB)剩 440 GB,8 × B300(2,160 GB)剩 1,160 GB。
- 2.4T 以上的模型在 FP8 下放不進任何 8-GPU 節點,需要 NVL72 級機櫃或 Helios;筆記引用的 2.4T 與 2.8T 參數量是未經查證的報導值。

### AMD:MI300X 到 MI455X / Helios

| 產品 | HBM | 記憶體頻寬 | 標稱算力 | 互連 | 狀態(2026-10-04) | 等級與來源 |
|---|---|---|---|---|---|---|
| MI300X | 192 GB(OCI listing) | 查無公開資料 | 查無公開資料 | 查無公開資料 | GA;OCI 每 GPU-hour $6.00 | B(listing);[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| MI355X | 288 GB(OCI listing) | 查無公開資料 | 查無公開資料 | 查無公開資料 | GA;OCI 每 GPU-hour $8.60 | B(listing);[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| MI455X(MI400 系列;交易公告稱「MI450」) | 432 GB HBM4(12 × 36 GB) | 23.3 TB/s(AMD 頁「peak theoretical」)對 19.6 TB/s(2026-01 報導) | 最高 40 PFLOPS FP4;最高 20 PFLOPS FP8 | scale-up 每顆最高 3.6 TB/s | AMD 稱 2026 下半年量產部署 | C;[AMD Instinct MI400](https://www.amd.com/en/products/accelerators/instinct/mi400.html)、[The Register: AMD](https://www.theregister.com/2026/01/07/mi500x_amd_ai/) |
| Helios 機櫃(72 × MI455X 加 18 × EPYC「Venice」) | 31 TB HBM4 | 1.67 PB/s(AMD 頁)對 1.4 PB/s(2026-01、2026-07 報導) | 2.9 EFLOPS FP4;1.4 EFLOPS FP8 | scale-up 260 TB/s(UALink over Ethernet,72 顆單一 hop);scale-out 43 TB/s | 2026-07 宣布量產;2026 Q3 末開始出貨,Q4 至 2027 上半年放量;無雲端 SKU | C;[AMD Instinct MI400](https://www.amd.com/en/products/accelerators/instinct/mi400.html)、[Moor Insights: AMD](https://moorinsightsstrategy.com/field-notes/amd-advancing-ai-2026-helios-ships-venice-swings-and-the-software-moat-narrows/)、[TrendForce: Helios](https://www.trendforce.com/news/2026/07/21/news-amds-first-rack-scale-ai-system-helios-challenges-nvidia-with-hbm4-memory-edge-but-reportedly-comes-at-a-higher-price/) |

- MI325X 完全查無資料;MI300X 與 MI355X 只有 Oracle 形狀清單上的容量。
- AMD 自稱 MI455X / Helios 對 Vera Rubin:FP4 峰值多 15%、HBM 容量多 50%、HBM 頻寬多 6%、scale-out 頻寬多 50%(C)。Moor Insights 指出 FP4 是 AMD 的 MXFP4 對 NVIDIA 的 dense NVFP4;若 Rubin 以 19.4 TB/s 出貨,頻寬差距約為 20%(D:23.3 ÷ 19.44 = 1.20)。
- HBM4 供應:Samsung 供 AMD,報導良率 2025 Q4 為 50%、2026 下半年預期 60–70%;NVIDIA Rubin 的 HBM4 以 SK hynix 為主。
- 後續世代均已宣布未出貨:MI430X(432 GB HBM4,HPC 用)預計 2027,MI500 預計 2027、MI600 預計 2028。

### Rubin CPX 的下場

- 規格:128 GB GDDR7(非 HBM)、30 PFLOPS NVFP4,定位為分擔長 context 推論的 prefill;2025 年宣布,原定 2026 年底推出([Glenn Lockwood: Rubin CPX](https://www.glennklockwood.com/garden/processors/rubin-cpx))。
- 2026-03 的 GTC 沒有展出它;NVIDIA 沒有正式宣布取消,Ian Buck 暗示 Groq 3 LPU 可能縮小 Rubin CPX 的角色,並說公司「currently focused on integrating the Groq 3 LPX rack with Rubin」([Tom's Hardware: LPX at GTC](https://www.tomshardware.com/pc-components/gpus/nvidia-groq-3-lpu-and-groq-lpx-racks-join-rubin-platform-at-gtc-sram-packed-accelerator-boosts-every-layer-of-the-ai-model-on-every-token))。
- 第三方說法:Tom's Hardware(2026-03-19)稱它「appears — though not officially confirmed」已自 roadmap 移除;Glenn Lockwood 的筆記頁(2026-04-01)寫它「was cancelled by GTC26. Groq has replaced it.」([Tom's Hardware: Groq deal](https://www.tomshardware.com/tech-industry/semiconductors/nvidias-20-billion-groq-deal-produces-its-first-chip)、[Glenn Lockwood: Rubin CPX](https://www.glennklockwood.com/garden/processors/rubin-cpx))。
- 含意(筆記推論):CPX 補的是 prefill 的便宜算力,LPX 補的是 decode 的記憶體頻寬;2026 平台加速的是互動速度而非長 prompt 的吃入,prefill 仍留在 Rubin 的 HBM GPU 上。
- 未查證:供應鏈因素與 2027–2028 年以 HBM4 重新設計回歸的報導只讀到標題。

### Groq 3 LPU / LPX 與 GPU–LPU 分工

| 項目 | SRAM | SRAM 頻寬 | scale-up 頻寬 | 算力 | 其他 | 等級與來源 |
|---|---|---|---|---|---|---|
| Groq 3 LPU(LP30) | 500 MB(Tom's Hardware 寫 512 MB) | 150 TB/s | 2.5 TB/s(96 條 chip-to-chip link × 112 Gb/s) | 1.2 PFLOPS FP8 | Samsung 4 nm 級(SF4X),單一 die、無先進封裝;前一代 LPU 為 230 MB SRAM、14 nm | C;[NVIDIA Groq 3 LPX](https://www.nvidia.com/en-us/data-center/lpx/)、[StorageReview: LPX](https://www.storagereview.com/news/nvidia-groq-3-lpx-everything-we-know)、[SemiAnalysis: GTC 2026](https://newsletter.semianalysis.com/p/nvidia-the-inference-kingdom-expands) |
| LPX 機櫃(256 顆 LPU) | 128 GB | 40 PB/s | 640 TB/s | 307.2 PFLOPS FP8(D:256 × 1.2) | 另有 12 TB DDR5「for large models」;全液冷;功耗與價格未揭露 | C;[NVIDIA Groq 3 LPX](https://www.nvidia.com/en-us/data-center/lpx/)、[StorageReview: LPX](https://www.storagereview.com/news/nvidia-groq-3-lpx-everything-we-know) |

| 推論階段 | 執行位置 | 說明 |
|---|---|---|
| prefill(吃入 prompt、建立 KV cache) | Rubin GPU | NVIDIA:「Rubin GPUs handle large-scale context processing」 |
| decode 的 attention(讀取累積的 KV cache) | Rubin GPU | KV cache 的存取樣式是動態的,適合 HBM GPU |
| decode 的 FFN / MoE expert 層 | Groq 3 LPU | 無狀態、可靜態排程;也可產生 speculative decoding 的 draft token |
| 編排 | NVIDIA Dynamo | 每個 token 的迴圈為 GPU attention、LPU FFN、再回 GPU |

來源:[NVIDIA Groq 3 LPX](https://www.nvidia.com/en-us/data-center/lpx/)、[NVIDIA blog: LPX](https://blogs.nvidia.com/blog/vera-rubin-lpx-spectrum-x-nvlink-fusion/)、[StorageReview: LPX](https://www.storagereview.com/news/nvidia-groq-3-lpx-everything-we-know)、[SemiAnalysis: GTC 2026](https://newsletter.semianalysis.com/p/nvidia-the-inference-kingdom-expands)。

- LPX 是 co-processor:一櫃的記憶體頻寬約為 Vera Rubin NVL72 的 29 倍(D:40 PB/s ÷ 1.4 PB/s),容量只有 0.6%(D:128 GB ÷ 20.7 TB),單獨放不下大模型與其 KV cache。
- StorageReview 估算的 FFN 權重對 128 GB SRAM(2026-03-18,非量測):GPT-OSS 120B 為 53.4 GB(MXFP4),1 櫃;DeepSeek R1 為 623.1 GB(FP8),約 5 櫃;Kimi K2 為 948.0 GB(FP8),約 7.4 櫃(D:948 ÷ 128);GLM 5 為 1,374.8 GB(BF16),超過 10 櫃。沒有來源說明放在 12 TB DDR5 的權重如何維持 SRAM 等級的速度。
- 每櫃的 tray 配置說法不一:32 個 tray 各 8 顆(StorageReview,2026-03)對每 tray 16 顆(SemiAnalysis;StorageReview,2026-08);總數 256 顆一致。
- 可得性:2026-03-16 宣布,2026-08-24 稱「full production」;Nebius 是首家採用的雲(Nebius Token Factory),Groq 為早期營運商,Nebius 價目頁在 2026-10-04 沒有 LPX 品項;AWS 部署 LPU 只有次級報導([NVIDIA: LPX full production](https://nvidianews.nvidia.com/news/nvidia-groq-3-lpx-now-in-full-production-with-world-class-speed-for-agentic-ai)、[Nebius prices](https://nebius.com/prices))。
- 交易:約 $20 billion,2025-12 宣布;報導對它是資產收購或技術授權說法不一,條款查無公開資料([Yahoo Finance: Groq](https://finance.yahoo.com/technology/ai/articles/nvidia-nvda-20-billion-groq-190737433.html))。

### 雲端價格與方向

AWS 執行個體家族(美元每 GPU-hour;on-demand 取自價格鏡像站或次級來源,Capacity Blocks 取自 AWS 頁面,讀於 2026-10-04):

| 執行個體 | GPU | On-demand | Capacity Blocks 現行 | Capacity Blocks 2026-10-07 起 | 等級與來源 |
|---|---|---|---|---|---|
| p5.48xlarge | 8 × H100 | 6.88–8.60(次級來源) | 5.191(US);4.72(非 US) | 5.970 | B、次級;[Thunder Compute: EC2 GPU](https://www.thundercompute.com/blog/ec2-gpu-instances)、[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| p5e.48xlarge | 8 × H200 | 查無公開資料 | 5.97 | 6.866 | B;[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| p5en.48xlarge | 8 × H200 | 7.91 | 6.865(US);6.241(非 US) | 7.895 | B;[Vantage: p5en](https://instances.vantage.sh/aws/ec2/p5en.48xlarge)、[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| p6-b200.48xlarge | 8 × B200 | 14.24 | 12.355 | 14.208 | B;[Vantage: p6-b200](https://instances.vantage.sh/aws/ec2/p6-b200.48xlarge)、[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| p6-b300.48xlarge | 8 × B300 | 17.80(次級來源) | 14.04 | 16.146 | B、次級;[Thunder Compute: EC2 GPU](https://www.thundercompute.com/blog/ec2-gpu-instances)、[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| P6e-GB200 UltraServer(u-p6e-gb200x72 / x36) | 72 或 36 × GB200 | 不提供 | 10.582(Dallas Local Zone) | 公告未列入調整 | B;[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |

其他雲(美元每 GPU-hour,讀於 2026-10-04;Azure 為每 VM-hour;Google 的數字是 8-GPU VM 牌價 ÷ 8,D;OCI 的單價另以 [Oracle price list API](https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=USD) 核對):

| 雲 | SKU | GPU | On-demand | 承諾、預留或其他 | 等級與來源 |
|---|---|---|---|---|---|
| Google Cloud | a3-highgpu-8g | H100 | 11.06 | Spot 6.62;1 年 CUD 7.67;3 年 CUD 4.86;DWS Flex-start 4.79;DWS Calendar 5.20 | B;[Google Cloud GPU pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized) |
| Google Cloud | a3-megagpu-8g | H100 | 11.68 | Spot 6.99;1 年 CUD 8.03;3 年 CUD 5.08;DWS Flex-start 5.04;DWS Calendar 5.50 | B;[Google Cloud GPU pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized) |
| Google Cloud | a3-ultragpu-8g | H200 | 10.60 | Spot 6.36;1 年 CUD 7.31;3 年 CUD 4.65;DWS Flex-start 5.30;DWS Calendar 7.42 | B;[Google Cloud GPU pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized) |
| Google Cloud | a4-highgpu-8g | B200 | 無 on-demand 價 | Spot 4.95;1 年 CUD 11.12;3 年 CUD 7.09;DWS Flex-start 8.06;DWS Calendar 11.28 | B;[Google Cloud GPU pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized) |
| Azure | Standard_ND128isr_NDR_GB200_v6 | GB200(每台 VM 的 GPU 數未確認) | 每 VM-hour 108.16(East US 等 4 區);Central US 133.04–138.93 | 1 年預留每 VM-hour 69.22;3 年 47.59 | B;[Azure Retail Prices API](https://prices.azure.com/api/retail/prices?$filter=contains%28armSkuName,%27GB200%27%29) |
| OCI | BM.GPU.H100.8 | H100 | 10.00 | 查無公開資料 | B;[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| OCI | BM.GPU.H200.8 | H200 | 10.00 | 查無公開資料 | B;[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| OCI | BM.GPU.B200.8 | B200 | 14.00 | 查無公開資料 | B;[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| OCI | BM.GPU.B300 | B300 | 15.00 | 查無公開資料 | B;[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| OCI | BM.GPU.GB200.4 | GB200 | 16.00 | 查無公開資料 | B;[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| OCI | BM.GPU.GB300.4 | GB300 | 18.00 | 查無公開資料 | B;[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| OCI | BM.GPU.MI300X.8 | AMD MI300X | 6.00 | 查無公開資料 | B;[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| OCI | BM.GPU.MI355X.8 | AMD MI355X | 8.60 | 查無公開資料 | B;[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| CoreWeave | HGX H100(8 GPU) | H100 | 6.16 | 承諾用量最多折 60% | B;[CoreWeave pricing](https://www.coreweave.com/pricing) |
| CoreWeave | HGX H200(8 GPU) | H200 | 6.31 | 承諾用量最多折 60% | B;[CoreWeave pricing](https://www.coreweave.com/pricing) |
| CoreWeave | HGX B200(8 GPU) | B200 | 8.60 | 承諾用量最多折 60% | B;[CoreWeave pricing](https://www.coreweave.com/pricing) |
| CoreWeave | GB200 NVL72(4-GPU instance) | GB200 | 10.50 | 承諾用量最多折 60% | B;[CoreWeave pricing](https://www.coreweave.com/pricing) |
| CoreWeave | GB300 NVL72、HGX B300 | GB300、B300 | 需洽業務 | 需洽業務 | [CoreWeave pricing](https://www.coreweave.com/pricing) |
| Lambda | on-demand instance | H100 | 3.99 | 查無公開資料 | B;[Lambda pricing](https://lambda.ai/pricing) |
| Lambda | on-demand instance | B200 | 6.69 | 1-Click Clusters(HGX B200,2 週至 1 年):9.86(16 GPU)、9.36(64 GPU)、8.87(256 GPU 以上) | B;[Lambda pricing](https://lambda.ai/pricing) |
| Nebius | on-demand | H100 | 3.85 | 另一份標示「effective October 1, 2026」的價目為 4.50,性質不明 | B;[Nebius prices](https://nebius.com/prices) |
| Nebius | on-demand | H200 | 4.50 | 同一份價目為 5.40 | B;[Nebius prices](https://nebius.com/prices) |
| Nebius | on-demand | B200 | 7.15 | 同一份價目為 8.50 | B;[Nebius prices](https://nebius.com/prices) |
| Nebius | on-demand | B300 | 7.85 | 同一份價目為 9.50 | B;[Nebius prices](https://nebius.com/prices) |

Vera Rubin 與 LPX 在各雲的狀態:

| 雲 | Vera Rubin | LPX | 來源 |
|---|---|---|---|
| CoreWeave | Preview(limited availability,2026-09-30 起);稱已在多個 region 部署數百顆 Rubin;無牌價 | 查無公開資料 | [CoreWeave: Vera Rubin](https://www.coreweave.com/blog/cognition-becomes-first-customer-for-nvidia-vera-rubin-nvl72-on-coreweave-cloud) |
| Microsoft Azure | 2026-03 在實驗室首度上電驗證;稱數月內導入資料中心;未命名 VM 系列 | 查無公開資料 | [DCD: Azure Vera Rubin](https://www.datacenterdynamics.com/en/news/microsoft-claims-to-be-first-hyperscaler-to-power-on-nvidia-vera-rubin-nvl72-system/)、[Azure blog: Rubin](https://azure.microsoft.com/en-us/blog/microsofts-strategic-ai-datacenter-planning-enables-seamless-large-scale-nvidia-rubin-deployments/) |
| Google Cloud | 列名首批供應者;規劃 2026 下半年;價目頁無機型 | 查無公開資料 | [DCD: Azure Vera Rubin](https://www.datacenterdynamics.com/en/news/microsoft-claims-to-be-first-hyperscaler-to-power-on-nvidia-vera-rubin-nvl72-system/)、[Google Cloud GPU pricing](https://cloud.google.com/products/compute/pricing/accelerator-optimized) |
| AWS | 列名首批供應者(2026-01、2026-03);Capacity Blocks 頁無 Rubin 執行個體 | 僅次級報導稱將部署 LPU | [NVIDIA: Rubin platform release](https://nvidianews.nvidia.com/news/rubin-platform-ai-supercomputer)、[Tom's Hardware: Groq deal](https://www.tomshardware.com/tech-industry/semiconductors/nvidias-20-billion-groq-deal-produces-its-first-chip)、[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/) |
| Oracle(OCI) | 列名首批供應者;2026-10-01 的價目無 Rubin | 查無公開資料 | [NVIDIA: Rubin platform release](https://nvidianews.nvidia.com/news/rubin-platform-ai-supercomputer)、[OCI pricing](https://www.oracle.com/cloud/compute/pricing/) |
| Nebius | 列名首批供應者;價目頁未列 | 首家採用 LPX 的雲;無公開 SKU | [NVIDIA: LPX full production](https://nvidianews.nvidia.com/news/nvidia-groq-3-lpx-now-in-full-production-with-world-class-speed-for-agentic-ai)、[Nebius prices](https://nebius.com/prices) |
| Lambda、Together AI、Crusoe、Nscale | 列名 Vera Rubin 的 NVIDIA Cloud Partner;Lambda 價目頁無 Rubin | 查無公開資料 | [NVIDIA: Vera Rubin release](https://nvidianews.nvidia.com/news/nvidia-vera-rubin-platform)、[Lambda pricing](https://lambda.ai/pricing) |

- 方向:AWS 的 Capacity Blocks 在 2026-07-01 調漲約 20%(P5、P5e、P5en、P6-B200、P6-B300),2026-10-07 再漲 15%(D:14.208 ÷ 12.355;16.146 ÷ 14.04;7.895 ÷ 6.865),B200 的預留價三個多月累計約漲 38%(D:1.20 × 1.15)([Yahoo Finance: AWS price rise](https://ca.finance.yahoo.com/news/aws-raising-gpu-instance-prices-134610388.html)、[AWS Capacity Blocks pricing](https://aws.amazon.com/ec2/capacityblocks/pricing/))。
- 同一顆 B200 的 on-demand 價,AWS 與 OCI 是 CoreWeave、Nebius、Lambda 的 1.6–2.1 倍(D:14.00 ÷ 8.60 = 1.63;14.24 ÷ 6.69 = 2.13)。
- AWS on-demand 的 Spot 價(Vantage):p5en 每 GPU-hour $3.88、p6-b200 $6.44。Google 的 A4(B200)沒有 on-demand 價,A4X(GB200)與 A4X Max(GB300)不在公開價目頁。
- 待查證:Azure GB200 VM 若為 4 顆 GPU,on-demand 為每 GPU-hour $27.04(D:108.16 ÷ 4),但 GPU 數未確認;Azure 零售價 API 沒有 GB300 SKU;Together AI 的價格查無公開資料。
- 截至 2026-10-04,沒有任何 hyperscaler 公布 Vera Rubin 的執行個體類型或價格;Helios 與 MI455X 也沒有任何雲端 SKU。

## Cerebras WSE-3 / CS-3 / CS-4

每片 WSE-3 晶圓只有 44 GB SRAM(21 PB/s),2026-08-18 宣布的 CS-4 沿用同一矽晶、三片一櫃共 132 GB;超過一片晶圓的模型只能按層切成跨晶圓 pipeline,KV cache 又與權重共用這 44 GB,所以公有 API 的 context 上限停在 131K。取得途徑以業務洽談為主:公有 API 只剩 2 個模型,AWS Bedrock 整合自 2026-03-13 宣布後已延到 2027 Q1。

### 晶圓與系統規格

| 晶圓 | 狀態與日期 | 製程與規模 | SRAM | 記憶體頻寬 | 標稱算力(sparse FP16) | dense 等效 | 等級與來源 |
|---|---|---|---|---|---|---|---|
| WSE-3 | 2024-03-13 發表(出貨起始日未見於所引來源) | TSMC 5 nm;4 兆個電晶體;900,000 個 AI 核心(12 × 7 共 84 個 die) | 44 GB | 21 PB/s | 125 PFLOPS | 約 15.6 PFLOPS(分析師:125 ÷ 8,假設 8:1 sparsity) | C、分析師;[Cerebras: WSE-3 press release](https://www.cerebras.ai/press-release/cerebras-announces-third-generation-wafer-scale-engine)、[Cerebras S-1](https://www.sec.gov/Archives/edgar/data/2021728/000162828026025762/cerebras-sx1april2026.htm)、[SemiAnalysis: Cerebras](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) |
| WSE-3T | 2026-08-18 隨 CS-4 宣布 | 與 WSE-3 同一矽晶,非新架構;46,225 mm²;時脈約 2.8 GHz,原為約 1.4 GHz(單一來源) | 44 GB(不變) | 43.2 PB/s | 250 PFLOPS | 約 25 PFLOPS | C、分析師;[Cerebras: CS-4 press release](https://www.cerebras.ai/press-release/cerebras-unveils-cs-4-up-to-30-times-faster-than-gpu-based-solutions-3347356)、[TNW: CS-4](https://thenextweb.com/news/cerebras-cs-4-wafer-scale-ai-inference-system) |

| 系統 | 晶圓數 | SRAM 總量 | 晶圓外 I/O | 功耗 | 冷卻 | 外部記憶體 | 等級與來源 |
|---|---|---|---|---|---|---|---|
| CS-3 | 1 | 44 GB | 1.2 Tb/s(12 × 100GbE,經 12 顆 Xilinx FPGA),約 150 GB/s | 約 25 kW(「over 20 kW」;12 × 3.3 kW 電源) | 客製液冷;約 100 LPM,即約 4 LPM/kW(NVL72 參考值約 1.5);進水約 21 °C | 推論用 KVSS 節點:雙路 AMD CPU、6 TB DDR5,供 KV cache offload | 分析師;[SemiAnalysis: Cerebras](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) |
| CS-4 | 3 | 132 GB | 每片 2.4 Tb/s、每櫃 7.2 Tb/s;RoCE v2;Direct Wafer Links 最低 2 µs;fat-tree 延遲 3 µs(原 5 µs) | 120–140 kW(Futurum、TNW)或 125–135 kW TDP(SemiAnalysis) | 直接液冷(機櫃後方的「Wafer-Scale Backpack」),周邊元件氣冷 | 查無公開資料 | C、分析師;[Cerebras: CS-4 press release](https://www.cerebras.ai/press-release/cerebras-unveils-cs-4-up-to-30-times-faster-than-gpu-based-solutions-3347356)、[Futurum: CS-4](https://futurumgroup.com/insights/cerebras-cs-4-makes-the-rack-the-new-chip-by-doubling-power-and-tripling-wafers/)、[SemiAnalysis: CS-4](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast) |

- CS-4 是第一套多晶圓系統:每櫃 750 PFLOPS(sparse FP16)、129.6 PB/s 記憶體頻寬、160.5 PB/s fabric 頻寬,元件數為 CS-3 的一半。每片晶圓得到 2 倍功率,電源轉換由距晶圓 50 mm 縮到 0.5 mm。
- SRAM 不隨製程成長:WSE-1 為 18 GB(16 nm)、WSE-2 為 40 GB(7 nm)、WSE-3 為 44 GB(5 nm),SemiAnalysis 稱 5 nm 之後「SRAM scaling basically stops dead」。
- 效率說法互相矛盾:Cerebras 稱 CS-4 的 throughput per watt 為 CS-3 的 10 倍(C),SemiAnalysis 認為 performance per watt「at best a slight improvement over CS-3」([Cerebras blog: CS-4](https://www.cerebras.ai/blog/introducing-cerebras-cs-4)、[SemiAnalysis: CS-4](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast))。
- 價格:CS-3 與 CS-4 的售價查無公開資料;SemiAnalysis 估 CS-3 每櫃物料成本約 $450k(含 KVSS 節點),CS-4「similar to the CS-3」。CS-3 的 25 kW 也是 SemiAnalysis 的數字,Cerebras 官方頁未能讀取。

### 44 GB 上限的含意

權重存在晶圓上的 SRAM,所需晶圓數的下限(D;P 為參數量,b 為儲存位元數;未計 KV cache、activations 與 pipeline 餘裕):

```latex
N_{\text{wafer}} \ge \left\lceil \frac{P\,[10^{9}] \times b / 8}{44\ \text{GB}} \right\rceil
```

| 模型 | 參數量與儲存位元 | 權重大小 | 晶圓數下限(D) | 已揭露或分析師數字 | 來源 |
|---|---|---|---|---|---|
| Llama 3 70B | 70B,16 bit | 140 GB | 3.2,取 4 | 實際切成 4 片 WSE-3 | [SemiAnalysis: Cerebras](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) |
| GPT-5.3-Codex-Spark(分析師假設約 120B) | 120B,8 bit | 120 GB | 2.7,取 3 | 分析師估約 3 片 | [SemiAnalysis: Cerebras](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please) |
| Kimi K2.6(1T) | 1T,4 bit | 500 GB | 11.4,取 12 | 實際約 20 台 CS-3(單一來源),共 880 GB SRAM(D:20 × 44);權重以 4 bit 儲存、16-bit 浮點計算 | [VentureBeat: Kimi K2.6](https://venturebeat.com/technology/cerebras-says-its-chips-run-a-trillion-parameter-ai-model-nearly-7-times-faster-than-gpu-clouds)、[Cerebras blog: Kimi K2.6](https://www.cerebras.ai/blog/cerebras-kimi-k2-Enterprise) |
| DeepSeek V4(1.6T) | 1.6T,8 bit | 1,600 GB | 36.4,取 37 | 分析師估 1M context 最少約 20 套,256 個同時請求時約 40 套 | [SemiAnalysis, 19 Aug 2026](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast) |
| GLM-5.3(744B) | 744B,4 bit | 372 GB | 8.5,取 9(3 個 CS-4 櫃) | 無 | 本文推算 |
| Qwen3.8-2.4T-A95B(2.4T) | 2.4T,4 bit | 1,200 GB | 27.3,取 28(10 個 CS-4 櫃) | 無 | 本文推算 |
| Kimi K3(2.78T,以 2.8T 計) | 2.8T,4 bit | 1,400 GB | 31.8,取 32(11 個 CS-4 櫃) | 無 | 本文推算 |

- 本表以「參數量 × 儲存位元」估算;第 3 章改用 Hugging Face 上的實際 checkpoint 大小,得到 Kimi K3 36 片(MXFP4 1,560.9 GB)、DeepSeek-V4-Pro-0813 21 片(FP4 加 FP8 892.7 GB)、Qwen3.8-2.4T FP8 57 片,兩表的差異來自這個假設(D)。
- 對應方式:模型在層的邊界切開,每片晶圓把分到的層放在本地 SRAM,跨晶圓只傳 activations;每多一片晶圓,time-per-output-token 就多一段固定成本([Cerebras blog: GPT-5.6 Sol](https://www.cerebras.ai/blog/how-cerebras-serves-gpt-5-6-sol-at-up-to-750-tokens-per-second)、[SemiAnalysis: Cerebras](https://newsletter.semianalysis.com/p/cerebras-faster-tokens-please))。
- 儲存精度:權重以 16 / 8 / 4 bit 混合儲存、即時還原,activations、attention 與 KV cache 維持全精度([Cerebras docs: models](https://inference-docs.cerebras.ai/models/overview))。
- context 為何卡在 131K:每個 in-flight microbatch 各帶一份 KV cache,且「must live in the same 44GB of on-wafer SRAM that's already mostly consumed by weights」。pipeline 又有並行下限,N 個 stage 至少要 N 個 microbatch 才不讓晶圓閒置。
- 溢出路徑慢:KVSS 節點的 6 TB DDR5 在晶圓外 I/O 之後,CS-3 約 150 GB/s、CS-4 約 300 GB/s(D:1.2 Tb/s ÷ 8;2.4 Tb/s ÷ 8),KV cache 進出晶圓需「several milliseconds」。
- 實際上限:公有 API 兩個模型的付費層為 131K(`gpt-oss-120b`)與 131,072 tokens(`qwen-3.8-27b`,文件標 128K),Free Trial 約 65K;SemiAnalysis 的代理資料顯示 agentic 請求中位數約 96.3K tokens,已貼近上限([Cerebras docs: gpt-oss](https://inference-docs.cerebras.ai/models/openai-oss)、[Cerebras docs: Qwen 3.8 27B](https://inference-docs.cerebras.ai/models/qwen-3.8-27b))。
- 1M context 的代價(分析師):1.6T 模型在 CS-4 上跑 1M context 約需 20 個 system,加上 256 個並行請求約需 40 個 system、超過 $20 million 與約 1 MW;預期買家會跑 256K 而非 1M。「system」指晶圓或機櫃,筆記無法判定([SemiAnalysis: CS-4](https://newsletter.semianalysis.com/p/cerebrass-next-generation-cs-4-fast))。

### 供給與取得途徑

| 途徑 | 內容 | 狀態(2026-10-04) | 來源 |
|---|---|---|---|
| Shared Inference(公有 API) | 2 個模型:`gpt-oss-120b`、`qwen-3.8-27b`;層級為 Free Trial($5 額度,30 天到期,5 RPM)、Developer(`gpt-oss-120b` 為 1,000 RPM、uncached 1M TPM)、Enterprise(客製) | GA;沒有永久免費層 | [Cerebras docs: models](https://inference-docs.cerebras.ai/models/overview)、[Cerebras docs: rate limits](https://inference-docs.cerebras.ai/support/rate-limits) |
| Dedicated Inference | 預留容量與專屬 endpoint,可部署 fine-tuned 權重;家族含 GLM 4.X / 5.X、Kimi K2.X、DeepSeek V3.X | 企業洽談;各模型的 context、速度、價格未公布 | [Cerebras docs: Dedicated](https://inference-docs.cerebras.ai/dedicated/overview) |
| 地端採購(CS-3 / CS-4) | 2026 Q2 硬體營收 $54.1 million(GAAP) | 可購買;牌價查無公開資料 | 財報文件;[Cerebras Q2 2026 results (SEC)](https://www.sec.gov/Archives/edgar/data/2021728/000162828026056186/cbrsannouncesfinancialresu.htm) |
| 轉售通路 | AWS Marketplace、OpenRouter、Hugging Face、Vercel、Microsoft Marketplace、IBM watsonx Model Gateway | 可用 | [Cerebras pricing](https://www.cerebras.ai/pricing)、[Cerebras S-1](https://www.sec.gov/Archives/edgar/data/2021728/000162828026025762/cerebras-sx1april2026.htm) |
| Cerebras Code 訂閱 | Pro 每月 $50、Max 每月 $200 | 兩個方案都標示 sold out | [Cerebras Code](https://www.cerebras.ai/code) |
| AWS Bedrock(Trainium3 做 prefill,CS-3 做 decode,以 EFA 傳 KV cache) | 2026-03-13 宣布「launching in the next couple of months」 | 已宣布未出貨;Cerebras 2026-08-12 的 Q2 財報稱預計 2027 Q1,AWS 未就延後發表說明 | [About Amazon: AWS–Cerebras](https://www.aboutamazon.com/news/aws/aws-cerebras-ai-inference)、[Cerebras Q2 2026 results (SEC)](https://www.sec.gov/Archives/edgar/data/2021728/000162828026056186/cbrsannouncesfinancialresu.htm) |
| AMD Helios 做 prefill、Cerebras 做 decode(Cerebras 自有資料中心) | 目標 2026 Q4 上線 | 已宣布未出貨 | [Cerebras Q2 2026 results (SEC)](https://www.sec.gov/Archives/edgar/data/2021728/000162828026056186/cbrsannouncesfinancialresu.htm) |
| Neocloud | Gimlet Labs(規劃 100 MW、約 700–800 櫃,CS-4 於 2027);General Compute(2027 Q1 可用) | 2026-09 下旬簽約 | [Futurum: neoclouds](https://futurumgroup.com/insights/two-clouds-pick-cerebras-in-one-week-to-make-multi-silicon-inference-fast/) |

- 產能已被大單占用:OpenAI 合約為 750 MW、超過 $20 billion(可擴至 2 GW),而 Cerebras 到 2027 年底已上線或已簽約的容量是 600 MW 以上;750 MW 約合 5,800 個 CS-4 櫃、17,000 片晶圓的 IT 負載(D:750,000 kW ÷ 130 kW × 3)。
- 容量訊號:Cerebras 2026-05 解釋 Kimi 不上公有 gateway 的理由是「Everyone is in a capacity crunch. We prioritize our enterprise customers」([VentureBeat: Kimi K2.6](https://venturebeat.com/technology/cerebras-says-its-chips-run-a-trillion-parameter-ai-model-nearly-7-times-faster-than-gpu-clouds))。
- 供應鏈:管理層稱不使用 HBM 與其封裝、不依賴 3 nm 產能,並稱已有支撐成長所需的晶圓供應(未提製程節點),2026 年產出目標為 2025 上半年的 10 倍以上;S-1 則揭露「no formalized long-term supply or allocation commitments from TSMC」([Bitget News: Cerebras call](https://www.bitget.com/news/detail/12560605668861)、[Revelata: Cerebras IPO](https://substack.revelata.com/p/pressure-testing-the-cerebras-ipo))。
- 路線圖:CS-5(2027,新的 WSE 矽晶)與 CS-6(晶圓上加 3D 堆疊 DRAM)均已宣布未出貨;查無名為「WSE-4」的產品([Tom's Hardware: Cerebras at Hot Chips](https://www.tomshardware.com/tech-industry/artificial-intelligence/hot-chips-2026-cerebras-lays-out-the-future-of-wafer-scale-ai-nexus-system-architecture-triples-rack-scale-performance-cs-6-wafer-to-incorporate-stacked-dram))。

## 網站呈現建議

本章建議以 1 個可排序矩陣、3 張圖與 1 個計算器呈現,其餘分表收進各家族分頁。

- 總表:把「每顆晶片」與「每套系統」兩張表做成可排序、可篩選的矩陣,篩選條件為家族、記憶體類型(HBM 或 SRAM)與狀態,預設開啟「今天有公開牌價」;來源互異的格子同時顯示兩個值與各自來源。
- 圖 1:記憶體容量對記憶體頻寬的 log-log 散佈圖,提供「每顆」與「每套系統」兩個視角;GA 用實心、已宣布用空心,家族同時以形狀與顏色區分。
- 圖 2:各雲 on-demand 每 GPU-hour 價格的分組長條圖(H100、H200、B200、B300、GB200、GB300),加一條 AWS Capacity Blocks 在 2026-07-01 與 2026-10-07 兩次調漲的階梯線,並以 Trainium2 的 $2.235 作參考線。
- 圖 3:亞太 Region 對家族的可得性矩陣(Inf2、Trn1、Trn2、Trn3、TPU v6e、TPU7x),點選格子顯示購買方式與牌價,Taipei 一列預設高亮。
- 計算器:輸入參數量與儲存位元數,輸出權重大小、所需 WSE-3 晶圓數與 CS-4 櫃數,以及能否放進 8-GPU 節點、NVL72 級機櫃或 UltraServer;公式用本章的兩條算式。
- 可收合或刪減:Rubin Ultra、MI500 / MI600、CS-5 / CS-6 等遠期項目各留一行;AWS 高層發言表、TPU 取用途徑表與 AWS 系統表的主機細節收進展開區。
