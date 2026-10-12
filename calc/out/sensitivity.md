| Change from base | Peak RPM | Uncached-in TPM | Cache-read TPM | Output TPM | All-token TPM | In-flight (99.9%) | RPM vs base | Uncached-in TPM vs base |
|---|---|---|---|---|---|---|---|---|
| Base case (100,000 employees, mix B, base level, single time zone) | 4.76K | 24.5M | 212M | 3.13M | 240M | 865 | 1.00× | 1.00× |
| Global population (busy-hour share 6.5% instead of 11%) | 2.82K | 14.5M | 125M | 1.85M | 142M | 527 | 0.59× | 0.59× |
| Sharper day (busy-hour share 12.5%) | 5.41K | 27.8M | 241M | 3.56M | 272M | 977 | 1.14× | 1.14× |
| Average weekday instead of P95 weekday (d = 1.0) | 3.97K | 20.4M | 177M | 2.61M | 200M | 728 | 0.83× | 0.83× |
| Month-end / release peak (d = 1.5) | 5.95K | 30.6M | 265M | 3.91M | 300M | 1.07K | 1.25× | 1.25× |
| Coding at high level, others base | 11.5K | 98M | 1.14B | 8.41M | 1.25B | 2.18K | 2.42× | 4.01× |
| Coding at low level, others base | 2.62K | 7.73M | 18.7M | 1.7M | 28.2M | 491 | 0.55× | 0.32× |
| OA at high level (office agents), others base | 6.8K | 32.6M | 236M | 5.12M | 274M | 1.31K | 1.43× | 1.33× |
| R&D at high level, others base | 16.5K | 61.2M | 302M | 10.5M | 374M | 2.88K | 3.46× | 2.50× |
| No prefix / prompt caching (all input uncached) | 4.76K | 265M | 0 | 3.13M | 268M | 865 | 1.00× | 10.84× |
| Output tokens ×2 (more reasoning) | 4.76K | 24.5M | 212M | 6.26M | 243M | 1.51K | 1.00× | 1.00× |
| Slower streams (40 tok/s per user) | 4.76K | 24.5M | 212M | 3.13M | 240M | 1.51K | 1.00× | 1.00× |
| Fast streams (300 tok/s per user) | 4.76K | 24.5M | 212M | 3.13M | 240M | 384 | 1.00× | 1.00× |
| Wafer-scale class streams (1,000 tok/s per user) | 4.76K | 24.5M | 212M | 3.13M | 240M | 258 | 1.00× | 1.00× |
