# Harness recheck: CODE

Reviewed parent patch to `enter_scene.py:608-625` and ran only the extracted launch-loop AST
with mocked attempt(). Six supplied tests passed; independent counterexamples still fail
the stopping requirement.

`failure_tokens` at lines 617-618 omits FATAL, Fatal error, Unhandled exception:,
GpuMarkerHung and GpuCheckpointHang. Each marker in the archived warmup log with
outcome=ok, hold_exit=None, hold_s=300 reaches the counted process. See
`harness_counterexamples.py` and its output. During hold the real attempt() does not call
consume() (lines 463-472), so a newly emitted marker need not have changed outcome.

The new branch reads only log_<tag>_warmup.txt. copy_artifacts also archives
stdout_<tag>_warmup.txt (lines 485-489). A forbidden marker emitted only to stdout during
hold likewise cannot stop the second process.

Use the complete forbidden-marker rule consistently across both archived streams before
allowing the counted process. No emulator or harness main was invoked in this review.
