# GMA: Benchmarking General Mobile Assistants in Challenging Real-World Scenarios

This repository contains the GMA benchmark code, including 300 tasks across four difficulty tiers, agent implementations, reproducible environment setup, and automated evaluation. The prepared Docker image provides the Android applications and emulator environment required to run the benchmark.

## System Requirements

- Linux/AMD64 host
- Python 3.12
- Docker with privileged-container support

## Install The Python Package

```bash
git clone git@github.com:zhu-yiqi/GMA.git
cd GMA

python3.12 -m venv .venv
source .venv/bin/activate
pip install uv
uv sync
```

## Configure Model Access

Create a private runtime configuration from the committed example:

```bash
cp configs/config.example.toml configs/config.toml
chmod 600 configs/config.toml
```

Edit `configs/config.toml` and set the agent type, model, OpenAI-compatible base URL, and API key:

```toml
[agent]
type = "qwen_agent"
model = "your-model-name"
base_url = "https://your-endpoint.example/v1"
api_key = "your-api-key"
```

`configs/config.toml` is ignored by Git and is loaded automatically by `gma eval`, `gma test`, and `gma manual`. To use a different file, pass `--config path/to/config.toml`. Command-line model arguments override the configuration file, and `GMA_*` environment variables override file values. Leave user-simulator model fields empty to reuse the selected task-agent credentials.

The built-in agent types are `qwen_agent` and `claude_agent`. List the agent types available in the installed version with:

```bash
./.venv/bin/gma agent list
```

## Get The Prepared Docker Image

GMA supports two distribution sources. Whichever source you use, the commands below create the local tag `gma:ready`, which is the runtime default.

### Option 1: Docker Hub

Pull the ready image from [`stephenzhu0218/gma`](https://hub.docker.com/repository/docker/stephenzhu0218/gma/general), then create the local runtime tag:

```bash
docker pull stephenzhu0218/gma:ready
docker tag stephenzhu0218/gma:ready gma:ready
```

### Option 2: ModelScope

Download `gma-ready.tar.gz` from [`StephenZhu0218/GMA`](https://modelscope.cn/datasets/StephenZhu0218/GMA):

```bash
pip install modelscope
modelscope download --dataset StephenZhu0218/GMA gma-ready.tar.gz --local_dir .
```

Load the archive into Docker:

```bash
docker load -i gma-ready.tar.gz
docker images | grep gma
```

The archive is expected to load as `gma:ready`. If it loads under another tag, retag it:

```bash
docker tag <loaded-image-id-or-tag> gma:ready
```

## Start GMA Environments

Before starting containers, load the host kernel NAT/iptables modules. This is required because GMA containers use Docker-in-Docker and rely on host NAT routing support. Run this on the host after boot and before `gma env up`:

```bash
sudo modprobe ip_tables
sudo modprobe iptable_nat
sudo modprobe iptable_filter
```

If you are already root, omit `sudo`.

`gma env up` uses `gma:ready` by default. Start one environment:

```bash
./.venv/bin/gma env up --count 1
```

Start multiple environments:

```bash
./.venv/bin/gma env up --count 10
```

To use a differently tagged image without retagging it, pass `--image`, for example `--image stephenzhu0218/gma:ready`.

List running environments:

```bash
./.venv/bin/gma env list
```

By default, environment `N` uses:

- backend port: `8100 + N`, for example env 1 uses `http://localhost:8101`
- browser emulator view port: `5920 + N`, for example env 1 uses `http://localhost:5921/vnc.html`

Stop all GMA environments:

```bash
./.venv/bin/gma env down
```

## Operate A Remote Emulator From A Local Laptop

noVNC lets you operate a remote emulator from a local browser without local ADB. Start the environment on the remote server, then create an SSH tunnel from your laptop.

For env 0:

```bash
ssh -N -L 5920:localhost:5920 -L 8100:localhost:8100 <remote-server>
```

Then open:

```text
http://localhost:5920/vnc.html
```

For env `N`, forward `5920 + N` for noVNC and `8100 + N` for the backend. The backend port is only needed if you want to run local `gma manual` or `gma eval`; for browser-only operation, forwarding the noVNC port is enough.

## Run A Manual Task

List available tasks:

```bash
./.venv/bin/gma task list
```

Initialize a task in one environment and manually operate the emulator:

```bash
./.venv/bin/gma manual ElementXSendLongTimeNoSeeJordanTask --url http://localhost:8100
```

Inside the manual shell, use:

```text
eval      # evaluate current state
ask ...   # ask the simulated user if the task supports user interaction
quit      # run final evaluation and exit
```

## Run Evaluation

Start at least as many environments as the desired parallelism, then run an evaluation. The agent type, model, endpoint, and API key are read from `configs/config.toml`:

```bash
./.venv/bin/gma eval \
  --task ElementXSendLongTimeNoSeeJordanTask TravelReviewEmiratesSep30FlightTask \
  --max-steps 50 \
  --max-concurrency 2 \
  --log-dir logs/example_run \
  --no-evaluate-each-step
```

For a larger task set, pass more task names after `--task`, or omit `--task` to run all registered tasks. Logs and trajectories are written under `--log-dir`.

Useful options:

- `--max-steps`: maximum agent steps per task
- `--max-concurrency`: number of parallel tasks, bounded by running containers
- `--no-evaluate-each-step`: evaluate only after final answer or termination
- `--no-skip-finished`: rerun tasks that already have completed logs
- `--last-images`: number of recent screenshots retained in model context
- `--action-only-history`: retain normalized actions without reasoning in history
- `--caption-old-images`: caption screenshots older than the retained-image window
- `--freeform-state`: maintain a latest-only free-form task-state record
- `--structured-state`: maintain task state from explicit before/after screenshots

Use `--agent-type`, `--model`, `--base-url`, or `--api-key` only when you want to override `configs/config.toml` for a particular run.

## Acknowledgements

We thank the developers of [AndroidWorld](https://github.com/google-research/android_world) and [MobileWorld](https://github.com/Tongyi-MAI/MobileWorld) for open-sourcing their work. We referred to their benchmark infrastructure when developing GMA. We also thank the developers of the open-source projects on which the seven GMA applications are based.

| Application | Source |
| --- | --- |
| ElementX | [Android client](https://github.com/element-hq/element-x-android), [Dendrite server](https://github.com/element-hq/dendrite) |
| Tempus | [Android client](https://github.com/eddyizm/tempus), [Navidrome server](https://github.com/navidrome/navidrome) |
| XiaoShiLiu | [Project](https://github.com/ZTMYO/XiaoShiLiu) |
| HMDP | [Project](https://github.com/java-up-up/hmdp-plus) |
| Meituan | [Web client](https://github.com/zwStar/vue-meituan), [Server](https://github.com/zwStar/meituan-backend) |
| Mall | [Web client](https://github.com/macrozheng/mall-app-web), [Server](https://github.com/macrozheng/mall) |
| Travel | [Project](https://github.com/mojahidhasan/fullstack-nextjs-golobe-travel-agency) |
