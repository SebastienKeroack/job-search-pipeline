## Job posting data
- Title: {{ $('loop-over-jobs-stage-2').item.json.job ?? 'N/A' }}
- Salary: {{ $('loop-over-jobs-stage-2').item.json.salary ?? 'N/A' }}
- Type: {{ $('loop-over-jobs-stage-2').item.json.type ?? 'N/A' }}
- City: {{ $('loop-over-jobs-stage-2').item.json.city ?? 'N/A' }}
## Job description
```text
{{ $('loop-over-jobs-stage-2').item.json.description ?? 'N/A' }}
```
## Candidate profile (resume)
```text
{{ $('resume').item.json.content ?? 'N/A' }}
```
## Scorer output
```text
total_score: {{ $json.total_score ?? 'N/A' }}
breakdown_score.skill_match: {{ $json.breakdown?.skill_match ?? 'N/A' }}
breakdown_score.compensation: {{ $json.breakdown?.compensation ?? 'N/A' }}
breakdown_score.benefits: {{ $json.breakdown?.benefits ?? 'N/A' }}
breakdown_score.employment_type: {{ $json.breakdown?.employment_type ?? 'N/A' }}
reason: {{ $json.short_reason ?? 'N/A' }}
```