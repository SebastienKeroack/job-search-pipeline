## Job posting data
- Title: {{ $('loop-over-jobs4').item.json.job }}
- Salary: {{ $('loop-over-jobs4').item.json.salary }}
- Type: {{ $('loop-over-jobs4').item.json.type }}
- City: {{ $('loop-over-jobs4').item.json.city }}
- Source: {{ $('loop-over-jobs4').item.json.site }}
## Job description
```text
{{ $('loop-over-jobs4').item.json.description }}
```
## Candidate profile
```text
{{ $('candidate').item.json.resume }}
```
## Scoring output
```text
score: {{ $('loop-over-jobs4').item.json.score }}
reasoning: {{ $('loop-over-jobs4').item.json.score_reasoning }}
```
## Cover letter
```text
{{ $('loop-over-jobs4').item.json.cover_letter }}
```
