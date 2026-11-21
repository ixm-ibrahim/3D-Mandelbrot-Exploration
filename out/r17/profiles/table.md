| rule | what it is | close cut: worst hair (limit 0.3) | bench, eight tests | cliff at gap 0.001 | net wraps / inside out | turned inside out | stretch, largest (flat rule = 1) |
|---|---|---|---|---|---|---|---|
| `oneplane` | Sphere inversions, one plane | 0.00 | fails J4 | 0.002 | 2 / 0.00 | 0.0 % | 1.0 |
| `lathe` | Quaternion square (lathe) | n/a | fails J3, J4, J8 | 0.002 | 0 / 1.00 | 50.0 % | 1.0 |
| `along` | Turning plane, along | 3.12 | passes all eight | 0.00599 | 0 / 1.60 | 39.0 % | 3.0 |
| `away` | Turning plane, away | 17.00 | fails J8 | 0.00997 | 4 / 0.01 | 4.0 % | 5.0 |
| `p_lin` | Turning plane, along; fades to the lathe at the axis (a = t) | 38.63 | fails J4, J8 | 0.00383 | 0 / 1.43 | 42.2 % | 1.9 |
| `p_ss` | Turning plane, along; fades to the lathe at the axis (smooth step) | 17.05 | passes all eight | 0.00413 | 0 / 1.46 | 42.0 % | 2.1 |
| `p_cot` | Turning plane, along; fades to the lathe at the negative axis only | 15.39 | passes all eight | 0.002 | 0 / 1.24 | 49.4 % | 1.2 |
| `p_half` | Turning plane, along, half strength (slope 0.5 to 1.5) | 12.96 | fails J3, J4, J8 | 0.004 | 0 / 1.14 | 42.3 % | 2.0 |
| `p_n4` | Turning plane, along; narrow flat spots (slope at most 1.38) | 48.52 | not run | 0.0035 | 0 / 1.36 | 44.5 % | 1.8 |
| `p_n8` | Turning plane, along; narrower flat spots (slope at most 1.24) | 31.42 | fails J3, J4, J8 | 0.00298 | 0 / 1.27 | 46.2 % | 1.5 |
| `p_n8c` | Turning plane, along; narrow flat spots, lathe at the negative axis | 37.74 | not run | 0.002 | 0 / 1.20 | 48.3 % | 1.2 |
| `p_h4` | Turning plane, along; wide flat spots (crossing slope 3.7) | 1.08 | passes all eight | 0.0126 | 0 / 2.15 | 29.2 % | 6.3 |
| `p_h16` | Turning plane, along; wider flat spots (crossing slope 7.1) | 2.09 | not run | 0.0265 | 0 / 2.53 | 19.0 % | 13.3 |
| `p_tt1` | Nearest plane, crossing smoothed (slope 1.6) | 4.13 | not run | 0.00428 | 0 / 1.55 | 43.0 % | 2.1 |
| `p_tt4` | Nearest plane, crossing smoothed (slope 6.3) | 5.18 | not run | 0.0231 | 0 / 2.42 | 21.5 % | 11.6 |
| `p_tt16` | Nearest plane, crossing smoothed in a thin band (slope 25) | 1.27 | passes all eight | 0.0972 | 0 / 2.80 | 8.1 % | 49.0 |
| `p_tt64` | Nearest plane, crossing smoothed in a very thin band (slope 100) | 0.41 | fails J5 | 0.377 | 0 / 2.92 | 2.7 % | 198.4 |
| `p_tt128` | Nearest plane, crossing smoothed in a band 0.9 degrees wide (slope 200) | n/a | fails J5 | 0.71 | 0 / 2.94 | 1.5 % | 397.8 |
| `p_tt256` | Nearest plane, crossing smoothed in a hair-thin band (slope 400) | 0.21 | passes all eight | 1.23 | 0 / 2.95 | 0.8 % | 796.4 |
| `p_tt1024` | Nearest plane, crossing smoothed in a band 0.04 degrees wide (slope 1600) | 0.12 | passes all eight | 2 | 0 / 2.96 | 0.2 % | 3175.5 |
| `p_aw_n8` | Turning plane, away; narrow flat spots | 8.84 | not run | 0.00697 | 4 / 0.00 | 3.7 % | 3.5 |
| `p_aw_h4` | Turning plane, away; wide flat spots | 3.72 | not run | 0.0166 | 4 / 0.02 | 3.8 % | 8.3 |
| `p_aw_tt4` | Nearest plane mirrored, crossing smoothed (away kind) | 5.51 | not run | 0.0269 | 4 / 0.03 | 3.1 % | 13.5 |
| `p_aw_tt16` | Nearest plane mirrored, crossing smoothed in a thin band (away kind) | 1.87 | not run | 0.0994 | 4 / 0.05 | 1.3 % | 50.8 |
| `p_aw_tt64` | Nearest plane mirrored, crossing smoothed in a very thin band (away kind) | 0.55 | not run | 0.359 | 4 / 0.06 | 0.4 % | 194.0 |
| `p_aw_tt256` | Nearest plane mirrored, crossing smoothed in a hair-thin band (away kind) | 0.54 | not run | 1.06 | 4 / 0.06 | 0.1 % | 772.9 |
| `p_aw_tt1024` | Nearest plane mirrored, crossing smoothed in a band 0.1 degrees wide (away kind) | 0.29 | not run | 1.85 | 4 / 0.07 | 0.0 % | 3076.8 |
| `twoplane` | Two planes, nearest plane (reference look) | 0.04 | fails J6 | 1.95 | 3 / 0.00 | 0.0 % | 1.0 |
