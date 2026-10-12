### 10,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=base · MX1. Frontier API only (Opus share follows Anthropic's own split: 10% of chat, 54% of coding sessions)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Opus 5.5 (API / Bedrock) | 235 | 1.31M | 12M | 161K | 13.5M | 2.92M | 0.10× | 40.1 | 59.7 | n/a (API only) | – | – | – | see ch.5 prices |
| Claude Sonnet 5.5 (API / Bedrock) | 265 | 1.26M | 10.3M | 168K | 11.7M | 2.1M | 0.35× | 41.8 | 61.8 | n/a (API only) | – | – | – | see ch.5 prices |

### 10,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=base · MX2. Tiered routing (small open model for OA, open flagships + frontier for coding and R&D)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash (552B backbone) | 101 | 246K | 239K | 57.2K | 542K | 303K | 0.00× | 17.7 | 30.8 | 0.39 (B300, vLLM, FP4, c192 on 2 GPUs; 60 tok/s per user, TTFT 0.25 s) | – | 0.13 GB | 0 TB | $1.09K |
| GLM-5.3 (744B / 40B active) | 20.6 | 42.6K | 37.5K | 8.75K | 88.9K | 51.3K | 0.00× | 1.71 | 5.75 | 1.22 (GB300 NVL72, SGLang P/D, FP4, c128 on 32 GPUs (GLM-5.2 run); 101 tok/s per user, TTFT 2.33 s) | – | 1.01 GB | 0.01 TB | $586 |
| Kimi K3 (2.78T / 104B active) | 108 | 826K | 9.52M | 68.5K | 10.4M | 895K | 0.09× | 31.9 | 49.5 | 10.5 (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 11.2 | 84.3 GB | 1 TB | $47.4K |
| DeepSeek V4-Pro (1.6T / 49B active) | 175 | 876K | 7.02M | 124K | 8.02M | 1M | 0.01× | 59.4 | 83.3 | 3.5 (B300, SGLang, FP4, c384 on 8 GPUs; 37 tok/s per user, TTFT 2.94 s) | 0.67 | 18.1 GB | 0.25 TB | $15.3K |
| Claude Opus 5.5 (API / Bedrock) | 139 | 779K | 7.09M | 96.4K | 7.97M | 1.74M | 0.06× | 24.1 | 39.3 | n/a (API only) | – | – | – | see ch.5 prices |

### 10,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=base · MX3. Open-weight only (self-hosted or managed open-weight endpoints)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash (552B backbone) | 75.9 | 157K | 138K | 32.2K | 327K | 189K | 0.00× | 9.7 | 19.4 | 0.22 (B300, vLLM, FP4, c192 on 2 GPUs; 60 tok/s per user, TTFT 0.25 s) | – | 0.07 GB | 0 TB | $638 |
| GLM-5.3 (744B / 40B active) | 131 | 1.01M | 11.6M | 83.4K | 12.7M | 1.09M | 0.01× | 17.4 | 30.3 | 11.7 (GB300 NVL72, SGLang P/D, FP4, c128 on 32 GPUs (GLM-5.2 run); 101 tok/s per user, TTFT 2.33 s) | – | 125 GB | 1.38 TB | $37.1K |
| Kimi K3 (2.78T / 104B active) | 131 | 1.01M | 11.6M | 83.4K | 12.7M | 1.09M | 0.11× | 38.9 | 58.2 | 12.8 (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 13.2 | 99.2 GB | 1.22 TB | $59.2K |
| DeepSeek V4-Pro (1.6T / 49B active) | 196 | 579K | 612K | 150K | 1.34M | 728K | 0.01× | 71.8 | 98.1 | 4.22 (B300, SGLang, FP4, c384 on 8 GPUs; 37 tok/s per user, TTFT 2.94 s) | 0.11 | 3.05 GB | 0.04 TB | $11.2K |

### 10,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=base · MX4. One open flagship for everything (Kimi K3)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kimi K3 (2.78T / 104B active) | 476 | 2.45M | 21.2M | 313K | 24M | 2.76M | 0.28× | 146 | 183 | 48 (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 21.6 | 200 GB | 2.86 TB | $160K |

### 100,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=base · MX1. Frontier API only (Opus share follows Anthropic's own split: 10% of chat, 54% of coding sessions)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Opus 5.5 (API / Bedrock) | 2.23K | 12.4M | 114M | 1.52M | 128M | 27.6M | 0.92× | 379 | 440 | n/a (API only) | – | – | – | see ch.5 prices |
| Claude Sonnet 5.5 (API / Bedrock) | 2.54K | 12M | 98.3M | 1.61M | 112M | 20.1M | 3.35× | 400 | 461 | n/a (API only) | – | – | – | see ch.5 prices |

### 100,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=base · MX2. Tiered routing (small open model for OA, open flagships + frontier for coding and R&D)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash (552B backbone) | 860 | 2.1M | 2.04M | 488K | 4.63M | 2.59M | 0.03× | 151 | 190 | 3.33 (B300, vLLM, FP4, c192 on 2 GPUs; 60 tok/s per user, TTFT 0.25 s) | – | 0.82 GB | 0.01 TB | $10.9K |
| GLM-5.3 (744B / 40B active) | 139 | 287K | 253K | 58.9K | 599K | 346K | 0.00× | 11.5 | 22 | 8.24 (GB300 NVL72, SGLang P/D, FP4, c128 on 32 GPUs (GLM-5.2 run); 101 tok/s per user, TTFT 2.33 s) | – | 3.85 GB | 0.04 TB | $5.86K |
| Kimi K3 (2.78T / 104B active) | 929 | 7.13M | 82.1M | 591K | 89.8M | 7.72M | 0.77× | 275 | 327 | 90.5 (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 74.1 | 557 GB | 8.63 TB | $474K |
| DeepSeek V4-Pro (1.6T / 49B active) | 1.61K | 8.03M | 64.4M | 1.14M | 73.6M | 9.17M | 0.09× | 545 | 617 | 32.1 (B300, SGLang, FP4, c384 on 8 GPUs; 37 tok/s per user, TTFT 2.94 s) | 4.99 | 134 GB | 2.27 TB | $153K |
| Claude Opus 5.5 (API / Bedrock) | 1.24K | 6.96M | 63.3M | 860K | 71.1M | 15.6M | 0.52× | 215 | 261 | n/a (API only) | – | – | – | see ch.5 prices |

### 100,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=base · MX3. Open-weight only (self-hosted or managed open-weight endpoints)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash (552B backbone) | 620 | 1.28M | 1.13M | 263K | 2.67M | 1.54M | 0.02× | 79.2 | 107 | 1.79 (B300, vLLM, FP4, c192 on 2 GPUs; 60 tok/s per user, TTFT 0.25 s) | – | 0.37 GB | 0.01 TB | $6.38K |
| GLM-5.3 (744B / 40B active) | 1.16K | 8.91M | 103M | 739K | 112M | 9.65M | 0.10× | 154 | 192 | 103 (GB300 NVL72, SGLang P/D, FP4, c128 on 32 GPUs (GLM-5.2 run); 101 tok/s per user, TTFT 2.33 s) | – | 794 GB | 12.2 TB | $371K |
| Kimi K3 (2.78T / 104B active) | 1.16K | 8.91M | 103M | 739K | 112M | 9.65M | 0.96× | 344 | 402 | 113 (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 91.1 | 685 GB | 10.8 TB | $592K |
| DeepSeek V4-Pro (1.6T / 49B active) | 1.82K | 5.37M | 5.68M | 1.39M | 12.4M | 6.76M | 0.07× | 667 | 747 | 39.2 (B300, SGLang, FP4, c384 on 8 GPUs; 37 tok/s per user, TTFT 2.94 s) | 0.86 | 23.2 GB | 0.4 TB | $112K |

### 100,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=base · MX4. One open flagship for everything (Kimi K3)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kimi K3 (2.78T / 104B active) | 4.76K | 24.5M | 212M | 3.13M | 240M | 27.6M | 2.76× | 1.46K | 1.58K | 480 (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 186 | 1.72K GB | 28.6 TB | $1.6M |

### 100,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=high · MX1. Frontier API only (Opus share follows Anthropic's own split: 10% of chat, 54% of coding sessions)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Opus 5.5 (API / Bedrock) | 11.9K | 71.3M | 664M | 8.25M | 744M | 154M | 5.13× | 2.07K | 2.21K | n/a (API only) | – | – | – | see ch.5 prices |
| Claude Sonnet 5.5 (API / Bedrock) | 13.3K | 71.6M | 593M | 9.52M | 674M | 119M | 19.86× | 2.33K | 2.48K | n/a (API only) | – | – | – | see ch.5 prices |

### 100,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=high · MX2. Tiered routing (small open model for OA, open flagships + frontier for coding and R&D)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash (552B backbone) | 4.83K | 16M | 39M | 3.55M | 58.5M | 19.5M | 0.20× | 1.08K | 1.18K | 24.2 (B300, vLLM, FP4, c192 on 2 GPUs; 60 tok/s per user, TTFT 0.25 s) | – | 11.8 GB | 0.21 TB | $82.7K |
| GLM-5.3 (744B / 40B active) | 531 | 1.88M | 4.97M | 451K | 7.3M | 2.33M | 0.02× | 79 | 107 | 63 (GB300 NVL72, SGLang P/D, FP4, c128 on 32 GPUs (GLM-5.2 run); 101 tok/s per user, TTFT 2.33 s) | – | 61.2 GB | 0.87 TB | $54.2K |
| Kimi K3 (2.78T / 104B active) | 3.64K | 36.5M | 455M | 2.7M | 494M | 39.2M | 3.92× | 1.24K | 1.35K | 414 (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 429 | 2.99K GB | 51.1 TB | $2.48M |
| DeepSeek V4-Pro (1.6T / 49B active) | 9.5K | 48.5M | 389M | 6.41M | 444M | 54.9M | 0.55× | 3.1K | 3.27K | 181 (B300, SGLang, FP4, c384 on 8 GPUs; 37 tok/s per user, TTFT 2.94 s) | 27 | 725 GB | 13.2 TB | $908K |
| Claude Opus 5.5 (API / Bedrock) | 6.79K | 40M | 370M | 4.66M | 414M | 86.6M | 2.89× | 1.18K | 1.28K | n/a (API only) | – | – | – | see ch.5 prices |

### 100,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=high · MX3. Open-weight only (self-hosted or managed open-weight endpoints)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash (552B backbone) | 2.66K | 9.4M | 24.9M | 2.25M | 36.5M | 11.7M | 0.12× | 635 | 713 | 15.3 (B300, vLLM, FP4, c192 on 2 GPUs; 60 tok/s per user, TTFT 0.25 s) | – | 8.12 GB | 0.14 TB | $51.5K |
| GLM-5.3 (744B / 40B active) | 4.55K | 45.7M | 568M | 3.38M | 617M | 49.1M | 0.49× | 678 | 759 | 472 (GB300 NVL72, SGLang P/D, FP4, c128 on 32 GPUs (GLM-5.2 run); 101 tok/s per user, TTFT 2.33 s) | – | 4.4K GB | 75.5 TB | $1.99M |
| Kimi K3 (2.78T / 104B active) | 4.55K | 45.7M | 568M | 3.38M | 617M | 49.1M | 4.91× | 1.55K | 1.67K | 518 (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 532 | 3.71K GB | 63.8 TB | $3.1M |
| DeepSeek V4-Pro (1.6T / 49B active) | 13.5K | 42.1M | 95.7M | 8.76M | 147M | 50.9M | 0.51× | 4.29K | 4.49K | 247 (B300, SGLang, FP4, c384 on 8 GPUs; 37 tok/s per user, TTFT 2.94 s) | 8.4 | 226 GB | 4.14 TB | $821K |

### 100,000 employees · B. Manufacturing / hardware (ODM, EMS, semis) · level=high · MX4. One open flagship for everything (Kimi K3)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kimi K3 (2.78T / 104B active) | 25.3K | 143M | 1.26B | 17.8M | 1.42B | 161M | 16.07× | 8.26K | 8.55K | 2.72K (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 1.12K | 9.99K GB | 174 TB | $9.36M |

### 100,000 employees · D. Software / internet company · level=base · MX1. Frontier API only (Opus share follows Anthropic's own split: 10% of chat, 54% of coding sessions)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Claude Opus 5.5 (API / Bedrock) | 5.77K | 41.6M | 464M | 3.72M | 509M | 78.9M | 2.63× | 928 | 1.02K | n/a (API only) | – | – | – | see ch.5 prices |
| Claude Sonnet 5.5 (API / Bedrock) | 5.28K | 36.3M | 396M | 3.35M | 435M | 53.1M | 8.84× | 834 | 923 | n/a (API only) | – | – | – | see ch.5 prices |

### 100,000 employees · D. Software / internet company · level=base · MX2. Tiered routing (small open model for OA, open flagships + frontier for coding and R&D)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash (552B backbone) | 486 | 1.18M | 1.15M | 275K | 2.6M | 1.46M | 0.01× | 85.1 | 114 | 1.87 (B300, vLLM, FP4, c192 on 2 GPUs; 60 tok/s per user, TTFT 0.25 s) | – | 0.49 GB | 0.01 TB | $6.15K |
| GLM-5.3 (744B / 40B active) | 85.1 | 176K | 155K | 36.1K | 367K | 212K | 0.00× | 7.04 | 15.3 | 5.05 (GB300 NVL72, SGLang P/D, FP4, c128 on 32 GPUs (GLM-5.2 run); 101 tok/s per user, TTFT 2.33 s) | – | 2.67 GB | 0.02 TB | $3.35K |
| Kimi K3 (2.78T / 104B active) | 3.87K | 29.7M | 342M | 2.46M | 374M | 32.2M | 3.22× | 1.15K | 1.25K | 377 (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 284 | 2.14K GB | 36 TB | $1.97M |
| DeepSeek V4-Pro (1.6T / 49B active) | 3.41K | 23.8M | 258M | 2.23M | 284M | 26M | 0.26× | 1.07K | 1.17K | 62.9 (B300, SGLang, FP4, c384 on 8 GPUs; 37 tok/s per user, TTFT 2.94 s) | 17.2 | 463 GB | 8.13 TB | $434K |
| Claude Opus 5.5 (API / Bedrock) | 3.21K | 23.2M | 258M | 2.08M | 283M | 43.9M | 1.46× | 518 | 588 | n/a (API only) | – | – | – | see ch.5 prices |

### 100,000 employees · D. Software / internet company · level=base · MX3. Open-weight only (self-hosted or managed open-weight endpoints)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1-Flash (552B backbone) | 361 | 745K | 656K | 153K | 1.55M | 898K | 0.01× | 46.1 | 67.1 | 1.04 (B300, vLLM, FP4, c192 on 2 GPUs; 60 tok/s per user, TTFT 0.25 s) | – | 0.23 GB | 0 TB | $3.64K |
| GLM-5.3 (744B / 40B active) | 4.84K | 37.1M | 428M | 3.08M | 468M | 40.2M | 0.40× | 640 | 719 | 430 (GB300 NVL72, SGLang P/D, FP4, c128 on 32 GPUs (GLM-5.2 run); 101 tok/s per user, TTFT 2.33 s) | – | 2.97K GB | 50.8 TB | $1.55M |
| Kimi K3 (2.78T / 104B active) | 4.84K | 37.1M | 428M | 3.08M | 468M | 40.2M | 4.02× | 1.43K | 1.55K | 471 (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 352 | 2.65K GB | 45 TB | $2.47M |
| DeepSeek V4-Pro (1.6T / 49B active) | 1.01K | 2.99M | 3.16M | 772K | 6.92M | 3.76M | 0.04× | 370 | 430 | 21.8 (B300, SGLang, FP4, c384 on 8 GPUs; 37 tok/s per user, TTFT 2.94 s) | 0.5 | 13.4 GB | 0.22 TB | $62.2K |

### 100,000 employees · D. Software / internet company · level=base · MX4. One open flagship for everything (Kimi K3)

| Model pool | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | Bedrock-counted TPM | × default Bedrock quota | In-flight (mean) | In-flight (99.9%) | GPUs, decode-bound (÷0.8 util; operating point) | GPUs, HBM-KV-bound (in-flight contexts) | Hot KV (in-flight) | Warm KV (sessions kept for cache hits) | Month cost at first-party list price |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Kimi K3 (2.78T / 104B active) | 11K | 77.9M | 859M | 7.08M | 944M | 85M | 8.50× | 3.3K | 3.48K | 1.08K (GB300 NVL72, vLLM, MXFP4, c48 on 8 GPUs; 38 tok/s per user, TTFT 1.15 s) | 697 | 5.41K GB | 94.1 TB | $5.17M |
