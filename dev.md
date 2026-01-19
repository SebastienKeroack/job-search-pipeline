# Init
```bash
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/msys2
conda update -n base -c defaults conda -y

conda env create -f ci/environment.yaml
conda activate job-search-pipeline
```

# Test
```bash
node --test job_search_pipeline/utils/parse/job_score/code.test.js
node --test job_search_pipeline/utils/parse/cover_letter/code.test.js
pytest
```
