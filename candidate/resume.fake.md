# Sebastien Keroack — Candidate Profile

## Identity
- **Name**: Sebastien Keroack
- **Location**: Quebec City, QC, Canada
- **Links**:  
  - LinkedIn: https://www.linkedin.com/in/sébastien-kéroack  
  - GitHub: https://github.com/SebastienKeroack  
  - Portfolio: https://sebastienkeroack.com  

## Target Roles
- **Primary**: Entry-level to junior-level roles
- **Secondary**: Mid-level roles when skill match is strong

## Languages
- **French**: Native
- **English**: Advanced

## Work Preferences
- **Remote**: Open to fully-remote roles
- **Hybrid / On-site**: Open if within ~50 km of Quebec City, QC

## Work Authorization & Availability
- **Work authorization**: Canada (Canadian citizen)
- **Availability**: Immediately

## Summary
Software engineer with experience in **Python, C++, PHP, and JavaScript**, and applied **machine learning** work using **PyTorch, TensorFlow, and ONNX**. Built systems spanning **data collection/processing**, **model training/evaluation**, and **deployment** using **Docker** and **Kubernetes**, plus web/backend development. Used the OpenAI API **chat/completions** with **structured JSON outputs** (no tools/function calling). Built an on-prem Kubernetes platform with security/observability components and automated the setup using **Bash scripts**. Targeting **ML/MLOps**, **Python backend**, **data engineering**, and **platform/cloud** roles.

## Education
- **Self-taught** (2010–present): Software engineering + ML through projects, technical documentation, and research papers
- **Formal education**: Secondary school (incomplete)
- **Certifications**: None

---

## Technical Skills (Self-assessed, 0–5)

### Skill Proficiency Scale (MANDATORY)
All skills are **self-assessed** on a 0–5 scale:
- **0**: No exposure
- **1**: Basic familiarity (tutorial-level, requires supervision)
- **2**: Familiar (can contribute with guidance) → entry-level acceptable
- **3**: Intermediate (scoped tasks with autonomy) → junior-level
- **4**: Advanced (design and ship independently) → mid-level
- **5**: Expert (can mentor/teach) → senior+

**Matching rules used by downstream evaluators**:
- Skill is **present** if score ≥2
- Skill is **strong** if score ≥4
- Never infer higher proficiency than stated

### Programming Languages
- Python (N/A)
- C++ (N/A)
- C (N/A)
- Shell (N/A)
- JavaScript (N/A)
- PHP (N/A)
- HTML (N/A)
- CSS (N/A)
- MQL4 (N/A)
- C# (N/A)
- Dart (N/A)
- CUDA (N/A)

### Machine Learning / AI
- PyTorch (N/A)
- TensorFlow (N/A)
- scikit-learn (N/A)
- BERT / fine-tuning (N/A)
- ONNX (N/A)
- Bayesian Optimization (N/A)

### Data Engineering / Processing
- NumPy (N/A)
- pandas (N/A)
- Web scraping (N/A)
- Selenium (N/A)
- jobspy (N/A)
- SQL (N/A)
- MySQL (N/A)

### Backend / APIs
- REST APIs (N/A)
- gRPC (N/A)
- Protobuf (N/A)
- OpenAI API (N/A)
- Google Sheets API (N/A)
- Google Drive API (N/A)

### DevOps / Platform
- Git (N/A)
- Docker (N/A)
- Kubernetes (N/A)
- containerd (N/A)
- CoreDNS (N/A)
- HashiCorp Vault (N/A)
- Helm (N/A)
- Prometheus (N/A)
- Loki (N/A)
- Harbor (N/A)
- Cilium (N/A)
- Gateway API (N/A)
- kubeadm (N/A)
- cert-manager (N/A)
- etcd (N/A)
- Longhorn (N/A)
- NVIDIA Operator (N/A)
- Redis (N/A)
- MinIO (N/A)
- CNPG (CloudNativePG) (N/A)

### Web / Frontend
- Node.js (N/A)
- Flutter (N/A)

### Testing / Code Quality
- pytest (N/A)
- flake8 (N/A)
- pycodestyle (N/A)
- black (N/A)
- isort (N/A)
- ESLint (N/A)
- Prettier (N/A)
- Stylelint (N/A)
- lint-staged (N/A)
- Composer (N/A)
- PHPCS (N/A)
- PHPCBF (N/A)

### Tooling / OS / Other
- Linux / Windows (N/A)
- OOP (N/A)
- PowerShell (N/A)
- SDLC (N/A)
- n8n automation (N/A)
- Ollama LLM tooling (N/A)
- Matplotlib (N/A)
- Seaborn (N/A)
- Visual Studio (N/A)
- CMake (N/A)
- MSVC (N/A)
- Bazel (N/A)
- Unity (N/A)
- Qt (N/A)
- Reverb (N/A)
- Blender (N/A)
- OIDC (N/A)
- PKI (N/A)
- KMS (N/A)
- C++/CLI (.NET) (N/A)
- XAMPP (N/A)

---

## Experience

### Freelance Machine Learning Developer | Quebec, QC | Mar 2020 – Apr 2020
Built a hybrid intrusion-detection prototype combining signature-based and anomaly-based detection for unseen attacks. Implemented decision tree and SVM baselines; produced confusion matrices and metrics dashboards. Designed a PyTorch model to emulate a Wallace tree multiplier (1–4 bit); improved accuracy by 83%.

**Tech used**: Python, PyTorch, scikit-learn, NumPy, pandas, Matplotlib, Seaborn

---

## Selected Projects

### Job Search Pipeline (LLM-assisted) | 2026
Built an automation pipeline using n8n with Python (jobspy) and JavaScript plus Google Sheets/Drive APIs. Exports structured job rows to Google Sheets. Used the OpenAI API (chat/completions) with structured JSON outputs to: (N/A) infer job level from job descriptions, (N/A) assess fit between a candidate profile and a job listing, (N/A) draft a cover letter, and (N/A) draft an outreach email to a recruiter. Uses an iterative workflow where each step feeds the next (compatibility score → application letter → outreach email).

**Repository**: https://github.com/SebastienKeroack/job-search-pipeline  
**Tech used**: n8n, Python, jobspy, JavaScript, OpenAI API, Google Sheets API, Google Drive API

### On-Prem Kubernetes Cluster Platform (Security + Observability) | 2025
Configured an on-prem **3-node** Kubernetes cluster (Kubernetes 1.34) using kubeadm (production-only; no separate dev namespace), including platform, security, storage, and observability components: HashiCorp Vault (used as OIDC provider and for secrets encryption using KMS), Harbor (configured to use the on-prem Vault OIDC provider for credentials), cert-manager, Cilium (with Gateway API), Prometheus + Loki, CoreDNS, etcd, Longhorn, CNPG (CloudNativePG), NVIDIA Operator, Redis, MinIO, and PKI management (root CA in cold storage with intermediate/leaf certificates for the cluster). Used REST to configure the Vault cluster. Applied default kubeadm RBAC and added additional RBAC rules for Vault KMS and Vault Kubernetes services. Did not configure NetworkPolicies. Automated the setup using Bash scripts (no Ansible/Terraform).

**Tech used**: Kubernetes, kubeadm, Helm, HashiCorp Vault, OIDC, PKI, KMS, Harbor, Prometheus, Loki, Cilium, Gateway API, cert-manager, CoreDNS, etcd, Longhorn, CNPG, NVIDIA Operator, Redis, MinIO, Shell (Bash)

### Portfolio Website (Multilingual) | Feb 2023 – Nov 2025
Built a multilingual website with structured content, responsive UI, adaptive themes, and SEO metadata. Implemented CAPTCHA-protected forms and deployed on a PHP server.

**Repository**: https://github.com/SebastienKeroack/sebastienkeroack-portfolio  
**Tech used**: HTML, CSS, JavaScript, PHP, Node.js

### Neural Architecture Search (RL) | Mar 2021 – May 2023
Built a TensorFlow controller that generates candidate architectures via reinforcement learning and optimization. Built the training/execution pipeline from scratch as a multi-node setup across multiple machines, and implemented gRPC (Protobuf) communication so candidate architectures can report model scores/results back to the controller for learning. Centralized results storage using Reverb.

**Tech used**: Python, TensorFlow, gRPC, Protobuf, Reverb

### FX Sentiment Analysis (NLP) | Feb 2020 – Mar 2021
Built an NLP data pipeline: automated data collection with Selenium; cleaned and tokenized text datasets; built a web labeling interface for supervised dataset creation. Fine-tuned a pretrained BERT model for sentiment classification.

**Tech used**: Python, Selenium, TensorFlow, PHP, MySQL, JavaScript

### Deep Learning Library (C++/CUDA) | Feb 2016 – Nov 2019
Built a C++/CUDA deep learning library with hand-coded backpropagation (no autograd), focusing on performance and memory efficiency. Built tooling/integration using CMake and MSVC.

**Repository**: https://github.com/SebastienKeroack/deep-learning  
**Tech used**: C++, CUDA, CMake, MSVC, Visual Studio, C++/CLI (.NET)

### Automated Trading Bot (MetaTrader) | 2015
Built an experimental trading bot prototype (unreliable results); this project sparked a transition toward deep learning.

**Tech used**: MQL4

### 3D Video Game Prototype | 2013
Built a Unity3D game with core mechanics (movement, NPCs, combat, health, inventory, equipment, buffs, customization).

**Tech used**: Unity, C#, Blender

### Log Viewing Web Dashboard (Full-stack) | 2012
Built an authenticated dashboard backed by MySQL for viewing activity logs; supported account creation from the login page.

**Tech used**: HTML, CSS, JavaScript, PHP, SQL (MySQL), XAMPP

### Automation Tool (Click Recording) | 2011 – 2012
Built a Qt application that records mouse click coordinates for simple automation.

**Tech used**: Qt, C++

### Messaging Application | 2011
Built a TCP messaging application (friends list + global chat) using Qt Creator.

**Tech used**: Qt, C++
