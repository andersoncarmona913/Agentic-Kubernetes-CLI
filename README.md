# 🤖 Kubernetes AI Agent with kubectl Integration

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.34%2B-326CE5.svg)](https://kubernetes.io/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900.svg)](https://aws.amazon.com/bedrock/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **An intelligent Agentic Kubernetes CLI assistant** that integrates your **local MCP server** with **AWS Bedrock**, enabling natural language control over **kubectl commands**, **cluster management**, and **real-time Kubernetes insights**.


---

## 🚀 Features

### 🗣️ Natural Language Kubernetes Operations
- Conversational `kubectl` interface — execute commands in plain English
- AI-powered command generation and validation
- Context-aware management of clusters and namespaces
- Real-time monitoring: pods, logs, resources, and events

### ⚙️ Advanced Capabilities
- ✅ **Resource Management** — List, describe, and manage Kubernetes resources
- 📊 **Troubleshooting Assistant** — Analyze logs and diagnose issues
- 🔄 **Context Switching** — Move between clusters easily
- ⚡ **Interactive CLI** — Friendly prompt-driven interface

---

## 🎥 Demo

Below is an example interaction between the **User** and the **Agentic Kubernetes CLI** demonstrating real-time troubleshooting and remediation.

---

**🧑‍💻 User:** list all pods in the cluster  
**🤖 Agent:** There are no running pods, but one pod `nginx` is showing an issue (`ImagePullBackOff`).

**🧑‍💻 User:** analyze the issue with `nginx` pod  
**🤖 Agent:** Issue identified — the container image tag `nginx:lt` is incorrect and not found in the registry.

**🧑‍💻 User:** fix the image tag issue and make the pod running  
**🤖 Agent:** Updated the image tag to `nginx:latest`, redeployed the pod, and verified that it is now **Running** successfully.

---

<video width="640" height="360" controls>
  <source src="https://github.com/user-attachments/assets/c30c4288-793c-4554-98ac-185075a621f0" type="video/mp4">
  Your browser does not support the video tag.
</video>

[🎥 Watch Full Demo Video](https://github.com/user-attachments/assets/c30c4288-793c-4554-98ac-185075a621f0)

---


## 📚 Table of Contents

- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Examples](#-examples)
- [Architecture](#-architecture)
- [MCP Tools](#-mcp-tools)
---

## 🔧 Prerequisites

### Required Software
- [Python 3.12+](https://www.python.org/downloads/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- Access to a running **Kubernetes cluster**
- **AWS account** with Bedrock API access

### AWS Bedrock Setup
1. Enable Claude models in the AWS Bedrock console  
2. Configure AWS credentials with Bedrock access  
3. Ensure IAM permissions for `bedrock:InvokeModel`  

---

## 📦 Installation

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/Tarique-B-DevOps/Agentic-Kubernetes-CLI.git
cd Agentic-Kubernetes-CLI

# Install dependencies
pip install -r requirements.txt

# Verify kubectl installation
kubectl version --client

# Run the agent
python3 agent.py
```

---

## ⚙️ Configuration

### Environment Variables

Set or export the following variables before running the agent:

```bash
# AWS Bedrock Configuration
export BEDROCK_MODEL_REGION=us-east-1
export BEDROCK_MODEL_ID=apac.anthropic.claude-3-5-sonnet-20241022-v2:0

# AWS Credentials (optional if configured with AWS CLI)
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

---

## 🎯 Usage

### Start the Agent

```bash
python3 agent.py
```

### Example Interactive Commands

```bash
⎈ kubectl> list all pods in production namespace
⎈ kubectl> what's wrong with my nginx deployment?
⎈ kubectl> show me the last 100 logs from api-server
⎈ kubectl> switch to staging cluster
```

---

## 💡 Examples

### List Pods

```bash
⎈ kubectl> show all pods in the cluster
```
**AI Response:**
```
✅ Command executed successfully:
NAME                     READY   STATUS    RESTARTS   AGE
nginx-7854ff8877-2kxq9   1/1     Running   0          5d
api-server-abc123        1/1     Running   2          3d
```

### Troubleshoot a Pod

```bash
⎈ kubectl> why is my app-server pod failing?
```
**AI Response:**
```
Analyzing pod app-server...
Issue: ImagePullBackOff
Root Cause: Container exits with code 1
Last Error: Connection refused to database:5432
Suggestion: Check database service and credentials
```

### View Logs

```bash
⎈ kubectl> get the last 50 lines of logs from nginx pod and summarize
```

### Manage Contexts

```bash
⎈ kubectl> list all available clusters
⎈ kubectl> switch to production-cluster
⎈ kubectl> what's my current context?
```

### Scale Deployments

```bash
⎈ kubectl> scale nginx deployment to 5 replicas
```

### Namespace Operations

```bash
⎈ kubectl> show all resources in kube-system namespace
⎈ kubectl> get all deployments across all namespaces
```

---

## 🏗️ Architecture

### System Components

![Architecture Diagram](https://github.com/user-attachments/assets/4e21ee25-fb6c-4750-8c1f-4d2d410248fc)

---

## 🧩 MCP Tools

### run_kubectl_command

```python
{
  "command": "kubectl get pods -n default -o json",
  "return_code": 0,
  "stdout": "...",
  "success": true
}
```

### kubectl_context

```python
{
  "action": "list",
  "success": true,
  "output": "..."
}
```