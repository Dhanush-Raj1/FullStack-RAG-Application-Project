> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://docs.nvidia.com/nemoclaw/llms.txt.
> For full documentation content, see https://docs.nvidia.com/nemoclaw/llms-full.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://docs.nvidia.com/nemoclaw/_mcp/server.

# Release Notes

> Changelog and feature history for NemoClaw releases.

NVIDIA NemoClaw is available in early preview starting March 16, 2026. Use this page to track changes.

## v0.0.53

NemoClaw v0.0.53 focuses on safer sandbox recreation, stricter onboarding preflight defaults, local inference reliability, policy coverage, and day-two repair workflows:

* `nemoclaw onboard` backs up workspace state before deleting an existing sandbox during recreation, including sandboxes that are registered but not ready. If the backup is partial or fails, onboarding aborts before delete so workspace, skills, extensions, identity, memory, messaging state, and credentials are not silently dropped. Set `NEMOCLAW_RECREATE_WITHOUT_BACKUP=1` only when you intentionally want a fresh workspace.
* Under-provisioned container-runtime warnings now default to abort in interactive onboarding. Pressing Enter at the warning stops the run so you can resize Docker Desktop or Colima before the sandbox build stalls. Non-interactive runs continue with a warning, and `NEMOCLAW_IGNORE_RUNTIME_RESOURCES=1` still suppresses the check when you have already accepted the resource trade-off.
* OpenClaw sandboxes can use the new `openclaw-pricing` policy preset for model-pricing reference fetches from LiteLLM and OpenRouter. NemoClaw suggests this preset during OpenClaw onboarding so session JSONL records can populate `usage.cost` without widening egress beyond the two read-only pricing endpoints.
* Local Ollama onboarding is more accurate. NemoClaw validates the `/api/tags` response body through the authenticated proxy, honors accepted no-tools overrides through validation and proxy setup, and uses Ollama's reported runtime context length for `contextWindow` unless you set `NEMOCLAW_CONTEXT_WINDOW`.
* Onboarding and gateway reuse recover from more host-runtime drift. NemoClaw recovers stopped gateways before preserving PVC-backed state, verifies gateway containers before reusing port-conflict state, defers Docker-driver gateway teardown until step `[2/8]`, records Docker-driver sandboxes on macOS, and uses Docker `--gpus` rather than CDI repair on WSL Docker Desktop.
* The sandbox and integration paths handle more common failures cleanly, including Brave Search credential rewrite through OpenShell providers, Telegram placeholder repair, host-gateway `web_fetch` routing, read-only host targets for `share mount`, live gateway drift in `list`, host-alias Kubernetes invocations, Jetson bridge DNS preflight failures, and non-ready sandboxes during maintenance backups.
* Hermes startup no longer treats a fresh root-entrypoint layout as locked state, which avoids false locked-layout detection during sandbox boot.
* Maintainer tooling can export a signed skills catalog, detect untracked files during skills refresh diffs, and run the stale-issue verification workflow added for maintainers.

## v0.0.52

NemoClaw v0.0.52 upgrades the bundled OpenClaw runtime, repairs Hermes sandbox startup, restores onboarding ready output, and hardens Slack onboarding, Windows bootstrap, and private-network handling:

* Bundles OpenClaw 2026.5.22 as the NemoClaw runtime target through `OPENCLAW_VERSION` in the NemoClaw Dockerfiles. The runtime upgrade addresses Telegram, Discord, and Slack channel registration issues seen on the 2026.5.18 runtime. `nemoclaw-blueprint/blueprint.yaml` keeps `min_openclaw_version` as a compatibility floor for direct blueprint consumers, so the blueprint floor can be lower than the Dockerfile target. Run `nemoclaw <name> rebuild` to pick up the new OpenClaw runtime in existing sandboxes.
* Hermes sandbox startup is more reliable on the v0.14 root entrypoint. NemoClaw precreates `hooks`, `image_cache`, `audio_cache`, and `logs/curator` under `HERMES_HOME`, makes `/sandbox/.hermes` sticky group-writable so the `gateway` user can create runtime state without removing sandbox-owned config files, stops precreating `/sandbox/.hermes/gateway.pid` as a symlink that Hermes v0.14 treats as a PID race, and clears legacy PID and lock state before launch.
* `nemoclaw onboard` ready output points users at `nemoclaw <name> dashboard-url --quiet` again, restoring the dashboard guidance that regressed during an earlier onboarding refactor.
* Slack onboarding validates preconfigured Slack tokens before treating Slack as configured. Invalid `SLACK_BOT_TOKEN` values from the environment or stored credentials no longer cause onboarding to skip the Slack prompt, so the wizard re-prompts for a valid `xoxb-...` token instead of silently advancing with a token Slack cannot use.
* The Windows bootstrap script defers first-run Ubuntu account setup to a separate WSL handoff window again, which keeps PowerShell prompt alignment intact during install. The default distro is `Ubuntu-24.04`, and `bootstrap-windows.ps1 -DistroName Ubuntu` reuses an existing `Ubuntu` distribution.
* The blueprint private-network blocklist reloads when `private-networks.yaml` changes on disk, so long-running NemoClaw processes validate SSRF and private-network rules against the current file instead of stale cached data.

## v0.0.51

NemoClaw v0.0.51 improves messaging controls, local inference setup, sandbox diagnostics, policy validation, and onboarding recovery:

* Slack setup now supports channel allowlisting. During onboarding, `channels add slack`, and non-interactive rebuilds, set `SLACK_ALLOWED_CHANNELS` to restrict channel `@mention` handling to selected Slack channel IDs. Combine it with `SLACK_ALLOWED_USERS` when you want both channel and member checks.
* Local Ollama setup now detects host installations that are below the minimum supported version and offers an explicit upgrade path. On macOS, NemoClaw uses Homebrew. On Linux, NemoClaw uses the system installer for upgrades and refuses non-interactive upgrade paths that would require a hidden sudo prompt.
* Non-interactive Linux Ollama setup can use a sudo-free user-local install path when passwordless sudo is unavailable. The docs now describe `NEMOCLAW_OLLAMA_INSTALL_MODE`, the user-local install trade-offs, and the manual `zstd` requirement.
* Managed Ollama model selection now uses a memory-aware registry for starter models. If a known bootstrap model does not fit currently available GPU memory, NemoClaw warns and falls back to the largest known model that does fit instead of starting a model that is likely to fail.
* `nemoclaw onboard` restores the managed vLLM menu entry for DGX Spark and DGX Station hosts, which had been hidden after a previous onboard refactor dropped the `gpu.platform` value the vLLM menu builder relies on.
* `nemoclaw resources` and `NEMOCLAW_RESOURCE_PROFILE` expose sandbox CPU and memory profiles. Profiles can be selected during onboarding, and `NEMOCLAW_CPU` or `NEMOCLAW_RAM` can override the selected profile for scripted runs.
* Cloudflare named tunnels are supported through `CLOUDFLARE_TUNNEL_TOKEN`. `nemoclaw tunnel start` passes the token through the environment and expects the named tunnel route to already point at the dashboard port.
* Jira policy validation guidance now matches the maintained preset. Use a Node HTTPS status probe for Atlassian API access and an explicit status-only curl probe for `auth.atlassian.com` when validating approved requests manually.
* Sandbox logs merge OpenClaw gateway output and OpenShell audit events into one stream, and `--tail` applies once to the merged result so policy denials appear beside gateway logs.
* Onboarding recovers more cleanly across host and runtime edge cases, including root-owned config sync directories, stale dashboard port allocation, unreachable Docker daemons, stale dashboard forwards, default NVIDIA CDI spec directories, and Linux Docker-driver health checks.

## v0.0.50

NemoClaw v0.0.50 focused on onboarding reliability, local inference hardening, messaging diagnostics, and sandbox lifecycle cleanup:

* `nemoclaw onboard` detects DGX Spark hosts where managed Ollama falls back to CPU execution. Local inference setup fails the Ollama validation step with a tailored diagnostic, adds a Spark `OLLAMA_LLM_LIBRARY=cuda_v13` systemd override when that backend is installed, and enables the managed Linux Ollama service so local inference survives reboot.
* Compatible endpoint setup rejects `host.docker.internal` inference URLs because OpenShell sandboxes do not have a portable host-service route through that name. Use Local Ollama's authenticated proxy path or a policy-managed host service instead.
* Telegram setup now surfaces BotFather group privacy guidance. Disable privacy mode, then remove and re-add the bot to each group before testing group delivery.
* Maintenance commands recover the OpenShell gateway before retrying sandbox-list operations, which makes rebuild, recover, upgrade, and backup flows more resilient after gateway drift.
* NemoClaw no longer writes proxy hooks into sandbox shell startup files. Local proxy configuration stays on supported OpenShell and NemoClaw paths rather than mutating user shell rc files.
* Windows bootstrap installs Ubuntu 24.04 when WSL is present but no Ubuntu distribution is registered.

