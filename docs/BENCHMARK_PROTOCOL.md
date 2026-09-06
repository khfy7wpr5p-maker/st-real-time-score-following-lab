# Benchmark Protocol

## Minimum metrics

- median absolute alignment error,
- mean/percentile alignment error when useful,
- percentage within 50/100/250/500 ms,
- realtime factor and CPU cost,
- end-to-end latency,
- recovery time after loss of position,
- failure rate,
- confidence calibration when available.

## Robustness scenarios

Clean alignment, tempo drift, rubato, wrong note, missing note, extra note, pause, restart, repeat, skip, backward jump, polyphonic overlap and noisy microphone.

## Comparison rule

No approach wins because of one accuracy number alone. Accuracy, latency, recovery, CPU, robustness and implementation complexity are considered together.

## Reproducibility

A benchmark run must record code revision, dependency versions, dataset/fixture manifest, configuration, random seed where relevant, machine/runtime information and raw per-example results before aggregation.
