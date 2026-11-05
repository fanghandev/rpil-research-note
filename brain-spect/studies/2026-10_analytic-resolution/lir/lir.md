Half-max width (mm), mean (min-max over 12 directions), alpha = 1e-3 lambda_max; energy share beyond 15 mm in %.

| case | r=0 | r=30 | r=60 | r=80 | r=95 |
|---|---|---|---|---|---|
| GATE SRM (ideal_lir.py) | **6.4** (5.2-7.3) | **5.8** (4.7-6.7) | **5.8** (4.9-6.7) | **5.9** (5.0-6.7) | **5.0** (3.8-7.1) |
| (i) current mix, converging | **9.8** (9.5-10.0) | **9.6** (9.4-9.9) | **7.9** (7.5-8.3) | **6.5** (6.2-6.8) | **5.5** (4.6-6.7) |
| (ii) uniform 1.215, parallel | **9.9** (9.8-10.0) | **11.1** (11.0-11.2) | **8.9** (7.6-10.4) | **7.7** (6.9-8.7) | **6.2** (5.4-7.2) |
| (iii) uniform 1.215, converging | **9.2** (9.1-9.3) | **9.1** (8.6-9.7) | **7.7** (7.1-8.3) | **6.2** (6.0-6.3) | **5.3** (4.9-5.8) |
| (iv) current mix, parallel | **10.9** (10.8-11.0) | **11.4** (11.1-11.6) | **9.3** (8.2-10.6) | **8.4** (7.6-9.3) | **6.7** (5.8-8.0) |
| (i) current mix, converging + GATE-like MC noise | **4.7** (3.7-5.7) | **2.5** (2.1-2.9) | **4.6** (4.1-5.2) | **4.3** (3.7-5.1) | **4.2** (3.0-5.8) |
| (ii) uniform 1.215, parallel + GATE-like MC noise | **6.3** (5.5-6.9) | **6.0** (5.3-6.3) | **6.7** (5.3-8.5) | **5.1** (4.3-5.7) | **5.2** (4.5-6.2) |
| (iii) uniform 1.215, converging + GATE-like MC noise | **6.5** (6.0-6.9) | **3.3** (2.6-3.8) | **4.4** (4.0-5.0) | **5.2** (5.0-5.4) | **4.8** (4.3-5.1) |
| (iv) current mix, parallel + GATE-like MC noise | **8.0** (7.1-8.7) | **7.2** (6.3-8.1) | **6.4** (4.6-7.9) | **5.2** (4.2-5.9) | **4.7** (4.0-5.8) |

| case (far-field share, %) | r=0 | r=30 | r=60 | r=80 | r=95 |
|---|---|---|---|---|---|
| GATE SRM (ideal_lir.py) | 5.9 | 7.9 | 4.8 | 4.7 | 2.5 |
| (i) current mix, converging | 1.1 | 1.4 | 2.0 | 1.6 | 1.7 |
| (ii) uniform 1.215, parallel | 1.4 | 3.3 | 2.9 | 2.5 | 1.7 |
| (iii) uniform 1.215, converging | 1.4 | 1.4 | 2.4 | 1.6 | 2.1 |
| (iv) current mix, parallel | 1.9 | 3.2 | 2.4 | 2.1 | 1.5 |
| (i) current mix, converging + GATE-like MC noise | 8.3 | 9.2 | 7.5 | 3.7 | 2.8 |
| (ii) uniform 1.215, parallel + GATE-like MC noise | 5.5 | 8.9 | 5.4 | 5.9 | 4.1 |
| (iii) uniform 1.215, converging + GATE-like MC noise | 5.4 | 9.0 | 6.5 | 3.6 | 2.6 |
| (iv) current mix, parallel + GATE-like MC noise | 6.3 | 9.6 | 6.6 | 5.7 | 2.7 |
