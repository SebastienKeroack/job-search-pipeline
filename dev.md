# Init
```bash
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2
conda update -n base -c defaults conda -y

conda env create -f ci/environment.yml
conda activate job-search-pipeline
```

# Test
```bash
node --test job_score/parse/code.test.js
node --test cover_letter/parse/code.test.js
pytest -q fetch/utils/salary_test.py
```

# Update workflows with resume, location, query
```bash
# Update with your own resume
bash workflows/update.sh
# OR
# Redact using fake data
bash workflows/redact.sh
```