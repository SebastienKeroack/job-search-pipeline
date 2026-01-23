## Job posting data
- Title: {{ $('loop-over-jobs2').item.json.job }}
- Salary: {{ $('loop-over-jobs2').item.json.salary }}
- Type: {{ $('loop-over-jobs2').item.json.type }}
- City: {{ $('loop-over-jobs2').item.json.city }}
- Source: {{ $('loop-over-jobs2').item.json.site }}
## Job description
```text
{{ $('loop-over-jobs2').item.json.description }}
```
## Candidate profile
```text
{{ $('candidate').item.json.resume }}
```
## Scoring output
```text
score: {{ $('loop-over-jobs2').item.json.score }}
reasoning: {{ $('loop-over-jobs2').item.json.score_reasoning }}
```
