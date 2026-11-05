# Cardiac SRM production on OSPool: status

Recorded 2026-10-09 from the OSPool access point, the sshfs mount
(`~/ospool/cardiac_spect_srm` = `ospool:/ospool/ap40/data/<ospool-user>/cardiac_spect_srm`) and the
local campaign directories in `/data/<user>/opengate_sim/data/cardiac_spect/`.

## Batches

All batches use a 5 MBq uniform 210 mm sphere, 100 × 1 s chunks per job, 1 / 1.5 / 2 mm SRMs.

| Batch | Cluster | Jobs submitted | Tarballs returned | Combined locally |
| --- | --- | --- | --- | --- |
| `batch_20260909_012610` | 14996562 | 10,000 | 9,937 | yes: 9,937 partials, 4.97 × 10¹² primaries (240 head files) |
| `batch_20260911_104934` | 15295120 | 20,000 | 19,949 | partly: 16,596 partials, 8.30 × 10¹² primaries (combined 2026-09-17, before the last 3,353 returned) |
| `batch_20260917_114257` | 15668035 | 10,000 | 9,996 | no: 9,996 extracted (9,832 1 mm partials, 4.92 × 10¹² primaries), never combined |

- **Merged SRM:** `batch_20260909_20260911_merged` (2026-09-18) holds 26,533 partials and
  1.33 × 10¹³ primaries (240 head files), plus cropped 150 and 160 mm variants. It covers the
  first two batches as they were then.
- **Not merged yet:** the last 3,353 partials of `batch_20260911_104934` (~1.7 × 10¹²
  primaries) and all of `batch_20260917_114257` (4.92 × 10¹²).
- **Available in total:** 39,882 returned jobs, ~2.0 × 10¹³ primaries, i.e. about 1.5 × the
  current merge.

## Problems

- **The combine timer is broken.** `qmirt-cardiac-combine.service` last ran on 2026-10-06 and failed:
  `submit_htcondor/run_cardiac_campaign_combine.sh` calls
  `payload/python/cardiac_parallel_srm_pipeline.py`, which is not in the repo. The timer is
  inactive. `batch_20260917_114257` therefore never got past extraction.
- **Held jobs, removed 2026-10-09** (`condor_rm` limited to held jobs of these two clusters; the
  queue is now empty). They could not finish, so their partials are lost:
  - 15295120: 73 jobs exceeded OSPool's 20 h execute limit (HoldReasonCode 47);
  - 15668035: 4 jobs exceeded their disk allocation (HoldReasonCode 47).

- cluster 15295120 (73 jobs): ProcId 239, 552, 714, 1004, 1148, 1207, 1234, 1522, 2069, 2276, 2646, 2835, 2853, 2880, 3168, 3181, 3187, 3322, 3530, 3560, 4131, 4364, 4371, 4517, 4578, 4628, 5183, 5185, 5206-5207, 5225, 5279, 5564, 6455, 6622, 6817, 6858, 6936, 7013, 7241, 7341-7342, 7378-7379, 7510, 7539, 7647, 8091, 8140, 8205, 8213, 8300, 8441, 8550, 8621, 9075, 9249, 9299, 9326, 10319, 10488, 11217, 11333, 11338, 11743, 11784-11785, 11791, 12941, 15158, 15274, 18775, 19059
- cluster 15668035 (4 jobs): ProcId 1884, 4288, 6911, 8867

## To do

1. Restore or replace the combine step (`cardiac_parallel_srm_pipeline.py`), then combine
   the rest of `batch_20260911_104934` and all of `batch_20260917_114257`.
2. Re-merge all three batches (`payload/python/merge_cardiac_campaigns.py`): ~2.0 × 10¹³ primaries.
