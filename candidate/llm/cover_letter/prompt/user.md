## Job posting data
- Title: {{ $('loop-over-jobs2').item.json.job }}
- Salary: {{ $('loop-over-jobs2').item.json.salary }}
- Type: {{ $('loop-over-jobs2').item.json.type }}
- City: {{ $('loop-over-jobs2').item.json.city }}
## Job description
```text
{{ $('loop-over-jobs2').item.json.description }}
```
## Candidate profile (resume)
```text
{{ $('candidate').item.json.resume }}
```
## Scorer output
```text
score: {{ $('loop-over-jobs2').item.json.score }}
reasoning: {{ $('loop-over-jobs2').item.json.score_reasoning }}
```