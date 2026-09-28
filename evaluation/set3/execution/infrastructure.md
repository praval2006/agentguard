# Execution infrastructure notes

- One isolated Python process per case; one run_acceptance call each.
- Fresh existing application_server default instances for profile, shipping and
  preferences only. Their exact ephemeral base URLs and lifecycle timestamps are
  in the case metadata. Context managers completed shutdown before process exit.
- No servers for catalog/promotion, whose frozen scenarios are unsupported only.
- The harness passes the loaded scenario dictionaries unchanged and verifies their
  nonmutation. It neither assigns verdicts nor implements an HTTP client.
- The stage attempt and each case attempt are created exclusively before work;
  rerunning the harness refuses to overwrite them. Result files also use exclusive
  creation. No retries were performed.
- Execution and the separate regression run used approved sandbox escalation for
  loopback binding. No preliminary denied bind or failed evaluation attempt occurred.
  No remote services or external model providers were used.
- All five subprocess exit codes are 0. All seven HTTP observations are established,
  with no timeout/body truncation or missing parsed JSON. Infrastructure failures: 0.
- Full regression ran once afterward: 304 tests passed, exit code 0. The exact log
  is regression.log. It did not rerun this evaluation harness or alter frozen inputs.
