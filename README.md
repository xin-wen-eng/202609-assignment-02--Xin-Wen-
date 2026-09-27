---
title: "Assignment 2: CI/CD Deployment to AWS EC2"
---
# Assignment 2: CI/CD Deployment to AWS EC2

## Objective

The goal of this assignment is to provision and deploy an example API server in your AWS account using DevOps best practices. You will provision a raw AWS EC2 server and build a Continuous Deployment (CD) pipeline using GitHub Actions.

By the end of this assignment, you will have a workflow where pushing code to GitHub automatically updates your live web server, and Gradescope automatically verifies it's running.

## Learning Goals

- Provision a Virtual Machine (EC2) on AWS.
- Configure Network Security (Security Groups) for Web and SSH traffic.
- Manage cloud credentials securely using GitHub Secrets.
- Write a GitHub Actions workflow to automate deployment and testing.

**AI Tools:** You may use AI coding assistants to help draft configuration files or troubleshoot errors. Review any AI-generated code carefully before running it — you are responsible for understanding and defending every line you submit.

## Part 1: The Application

Your repository contains a simple API server in the `api_server/` directory:

- `server.py`: A Flask web server with a `/healthcheck` endpoint.
- `requirements.txt`: Python dependencies.

**Do not modify the application code.** You will deploy it as-is.

## Part 2: Infrastructure Setup (AWS)

### 2.1 Launch an EC2 Instance
Manually launch an EC2 server and configure it for ssh access. 

1. Log in to the AWS Console and navigate to EC2. Make sure you are in the **us-west-2 (Oregon)** region.
2. Click **Launch Instances**.
3. **Name:** `assign2-server`.
4. **OS Image:** Ubuntu Server 24.04 LTS (HVM), SSD Volume Type.
5. **Instance Type:** `t3.micro` (Free tier eligible).
6. **Key Pair:**
   - Click **Create new key pair** (or use an existing one).
   - Name: `assign2-key`.
   - Type: RSA. Format: `.pem`.
   - Download the file (e.g., `assign2-key.pem`). **Save this now** — you cannot download it again.

### 2.2 Network Settings (Security Groups)

1. In "Network settings," click **Edit**. (You can use your default VPC.)
2. Ensure **Auto-assign public IP** is enabled.
3. Select **Create security group**.
4. Add the following inbound rules:
   - **SSH:** Port 22 | Source: `0.0.0.0/0` (Anywhere)
   - **HTTP:** Port 80 | Source: `0.0.0.0/0` (Anywhere)
5. Click **Launch Instance**.

### 2.3 Get Your Connection Info

1. Go to EC2 Dashboard > Instances.
2. Click your new instance. It may take up to 30 seconds to start and show a public IP address.
3. Copy the **Public IPv4 address** (e.g., `54.123.45.67`).


## Part 3: Configure GitHub Repo Secrets

GitHub needs permission to log in to your server to update the code. Store your private key and IP address securely as repository secrets.

1. In your GitHub repository, go to **Settings > Secrets and variables > Actions**.
2. Click **New repository secret** and add the following:

| Name | Value |
|---|---|
| `EC2_HOST` | Your EC2 public IPv4 address (e.g., `54.12.34.56`) |
| `EC2_USERNAME` | `ubuntu` |
| `EC2_SSH_KEY` | The full contents of your downloaded `.pem` file, including the `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----` lines. Make sure there's a newline after the final "END RSA" line. |

---

## Part 4: Create the Deployment Pipeline

You will create a GitHub Action that triggers every time you push code. We'll cover how GitHub Actions works in more depth in Module 3 — for now, copy the workflow below and focus on understanding what each step does.

1. In your repository, goto the directory: `.github/workflows/`

2. Create a file named `deploy.yml` inside that folder by copying the example file. You don't need to modify it. 

3. Review it to understand what each step does before moving on.

   ```yaml
   name: Deploy to EC2
   on: [push]
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout Code
           uses: actions/checkout@v4

         - name: Copy Files to EC2
           uses: appleboy/scp-action@master
           with:
             host: ${{ secrets.EC2_HOST }}
             username: ${{ secrets.EC2_USERNAME }}
             key: ${{ secrets.EC2_SSH_KEY }}
             source: "."
             target: "/home/ubuntu/api-assignment"

         - name: Start Server
           uses: appleboy/ssh-action@master
           with:
             host: ${{ secrets.EC2_HOST }}
             username: ${{ secrets.EC2_USERNAME }}
             key: ${{ secrets.EC2_SSH_KEY }}
             script: |
               set -e
               cd /home/ubuntu/api-assignment
               # Install Dependencies
               sudo apt-get update
               sudo apt-get install -y python3-pip
               sudo pip3 install --break-system-packages -r api_server/requirements.txt
               # Stop old service
               sudo systemctl stop api-server.service || true
               sudo systemctl reset-failed api-server.service || true
               # Start Server
               sudo systemd-run --unit=api-server --no-block \
                 --working-directory=/home/ubuntu/api-assignment \
                 python3 api_server/server.py
               # Verify startup
               sleep 5
               sudo systemctl is-active api-server.service
   ```

---

## Part 5: Submission (Gradescope)

Cloud Programming Assignments in this course are submitted and graded through **Gradescope**, using a GitHub-linked autograder. For this assignment, the autograder makes a **live HTTP request** to your deployed EC2 instance — it needs to know your instance's public IP to do that.

### 5.1 Add `server_info.txt`

Create a file named `server_info.txt` in the root of your repository containing **only** your instance's public IP address:

```text
54.123.45.67
```

Do not include any other text, your private key, or any other credentials in this file.

### 5.2 Commit and Push
Run these git commands to update your local repository and push a copy to github. 

```bash
# see the status of your local repository files
git status
# adds the modified files to the pending commit list (staging)
git add .github/workflows/deploy.yml server_info.txt
# commit the changes in your local repository
git commit -m "Add deployment pipeline and server info"
# copy the changes to the github repository
git push origin main
```

### 5.3 Watch the GitHub Action
Once the changes are successfully pushed to Github, Github Actions will detect the deploy workflow that you added
and will execute the workflow. 

- Go to the **Actions** tab in your GitHub repository.
- You should see the workflow running. Click on it to watch the logs and activity. It may take 1-3 minutes. 
- If it turns green, your server is deployed and running.
- To verify the app is running, you can use the `curl` program or a browser to check.
   - **Browser:** enter `http://<your-ip>/healthcheck` in a browser.
   - **curl:** run `curl http://<your-ip>/healthcheck` on the command line. 
- Expected Response:

    ```json
    {"status": "ok"}
    ```

### 5.4 Submit in Gradescope
If the app is running and verified, then you can run the autograder to submit the assignment and receive credit. 

- Go to the Assignment 2 entry in Gradescope.
- Click **Submit Assignment > GitHub**.
- Select your repository and the `main` branch.
- Click **Upload**.

Gradescope will run the autograder using your provided ip address and verify the working app. 

**If you stop and restart your EC2 instance, its public IP will change.** Update both the `EC2_HOST` GitHub secret and `server_info.txt`, then resubmit.

### 5.5 Clean Up

Once your submission passes:

1. Go to AWS > EC2 > Instances.
2. Select `assign2-server`.
3. **Instance State > Terminate (Delete) Instance.**

Terminating stops the billing charges for this instance. You may resubmit as many times as needed before the deadline — just remember to keep your instance running until you're done.

## Grading Rubric

- **(2 points)** EC2 instance launched correctly with appropriate security group rules (SSH + HTTP open).
- **(2 points)** GitHub repository secrets (`EC2_HOST`, `EC2_USERNAME`, `EC2_SSH_KEY`) configured correctly.
- **(3 points)** `deploy.yml` workflow correctly copies code and starts the server on push, verified by a successful GitHub Actions run.
- **(3 points)** `server_info.txt` present and correct; Gradescope's live health check against `/healthcheck` returns `{"status": "ok"}` with HTTP 200.
- **(-3 points)** Sensitive information (e.g., a private key) committed to the repository.

## Troubleshooting & FAQ

- **Q: The Action failed with "Connection Timed Out."**
  A: Check your AWS Security Group. You likely forgot to allow Port 22 (SSH) or Port 80 (HTTP) from "Anywhere" (`0.0.0.0/0`). It's also possible your `api_server` did not start — check the workflow logs.
- **Q: The Action failed with "Permission denied (publickey)."**
  A: Your `EC2_SSH_KEY` secret is likely incorrect. Make sure you copied the entire content of the `.pem` file, including the dashed BEGIN/END lines, plus a trailing newline.
- **Q: Gradescope's health check fails even though my Action succeeded.**
  A: Check that `server_info.txt` contains your current public IP with no extra text, and that you haven't stopped/restarted the instance since your last IP update.
- **Q: I stopped my instance and started it again, and now deployment fails.**
  A: Stopping a standard EC2 instance changes its public IP. Update the `EC2_HOST` GitHub secret **and** `server_info.txt` with the new IP, then push again.
