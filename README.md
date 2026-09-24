# Network KPI Tracker — CI/CD Pipeline

A fully automated CI/CD pipeline built from scratch: **Git → GitHub → Jenkins → Docker → AWS ECR → AWS EC2**.

The application itself (`app.py`) is intentionally trivial — a single-endpoint Python HTTP server with zero external dependencies. That's deliberate: the point of this project isn't the app, it's everything that happens to it between a `git push` and it running live on a public server, fully automatically, with no manual deploy steps.

## What this demonstrates

- A Jenkins pipeline (defined as code in the `Jenkinsfile`) that runs automated tests, builds a Docker image, pushes it to a private AWS registry, and deploys it to a live server — triggered automatically by polling GitHub for new commits, not by manually clicking "build."
- Secure credential handling: AWS keys and an SSH private key are stored in Jenkins' credential store and referenced only by ID — never hardcoded, and automatically masked in build logs.
- Least-privilege IAM: the EC2 instance authenticates to AWS via an attached IAM role (no stored keys on the server at all), scoped to read-only ECR access.
- A custom Jenkins Docker image, built to include exactly the tools the pipeline needs (`docker`, `aws`, `python3`) — including working around a real Debian packaging quirk where the standard `docker.io` package doesn't ship the Docker CLI binary.
- Fail-fast design: automated tests run before the image is ever built or deployed, so a broken change never reaches the server.

## Architecture
you GitHub Jenkins AWS
─── ────── ─────── ───
git push ────────▶ (polled ────────▶ pipeline starts (Poll SCM,
every ~2min) checks for new commits)
│
├─ 1. Checkout (git checkout)
├─ 2. Test (python3 test_app.py)
├─ 3. Build (docker build)
├─ 4. Push to ECR ─────────────────▶ ECR repo
└─ 5. Deploy to EC2 ──(ssh)────────▶ EC2 pulls
image via
IAM role,
runs it


## Repo layout
app.py the application (a single /health endpoint)
test_app.py automated test — starts the real app, verifies the real response
Dockerfile packages app.py into a container image
Jenkinsfile the pipeline definition — 5 stages, read top to bottom
jenkins/ Dockerfile + plugins.txt for the custom Jenkins image
trust-policy.json IAM trust policy allowing EC2 to assume its deploy role
user_data.sh EC2 boot script — installs and starts Docker on first launch


## Tools and services used

Git, GitHub, Jenkins (Docker-outside-of-Docker), Docker, AWS ECR, AWS EC2, AWS IAM (roles and instance profiles), AWS CLI, Python (standard library only — zero pip installs anywhere in the pipeline).

## The pipeline, stage by stage

1. **Checkout** — pulls the latest commit from GitHub.
2. **Test** — runs `test_app.py`, which starts the real app as a subprocess and makes a real HTTP request to it, asserting the response is correct. A failure here stops the pipeline immediately — nothing gets built or deployed.
3. **Build Docker Image** — builds a fresh image, tagged with the Jenkins build number for traceability (never overwrites a generic `latest` tag).
4. **Push to ECR** — authenticates using AWS credentials stored in Jenkins (masked in logs), tags, and pushes the image to a private ECR repository.
5. **Deploy to EC2** — SSHes into the EC2 instance (using a key stored in Jenkins' credential store) and tells it to pull the new image and replace the running container. The EC2 instance itself authenticates to ECR using its attached IAM role — no AWS keys are ever stored on the server.

## Notable engineering problems solved along the way

- **A Windows-specific `docker login` bug**: piping a password through PowerShell (`| docker login --password-stdin`) silently corrupted the input to a native executable. Diagnosed by isolating each layer (network, token validity, Docker's credential helper) before finding the actual cause — a PowerShell pipe quirk, irrelevant on Linux.
- **A missing Docker CLI inside the Jenkins container**: the Debian `docker.io` package installed the daemon but not the actual `docker` command in this environment — confirmed by searching the filesystem for the binary. Fixed by downloading Docker's official static CLI binary directly, the same approach used for tools like `kubectl` in CI images.
- **Docker socket permissions**: Jenkins' non-root user couldn't access the mounted Docker socket by default — fixed by identifying the socket's owning group ID and adding the container to that group at startup.
- **An unresponsive EC2 host**: both SSH and HTTP started failing identically on a running, AWS-healthy-per-status-checks instance. Diagnosed as a host-level issue (not a security group or app problem, since an unrestricted port failed too) and resolved with a full stop/start (which migrates the instance to different underlying hardware — something a simple reboot can't do).

## Running it yourself

- An AWS account with an IAM user that can manage EC2, ECR, and IAM roles.
- Docker installed, to run Jenkins locally (or on any reachable host).
- A GitHub repository to push this to.

Provision an ECR repository and an EC2 instance with an appropriate IAM role (see `trust-policy.json` and `user_data.sh`), build the custom Jenkins image from `jenkins/`, add your AWS and SSH credentials to Jenkins' credential store, point a Pipeline job at this repo, and push — the `Jenkinsfile` handles everything else.

## Verifying it's live

```bash
curl http://<ec2-public-ip>/health
```

## Possible next steps

- Replace Poll SCM with a real GitHub webhook (requires Jenkins on a publicly reachable host rather than a local machine).
- Replace the single EC2 instance with an Auto Scaling Group behind a Load Balancer for zero-downtime rolling deploys.
- Manage infrastructure with Terraform instead of one-off AWS CLI commands.
