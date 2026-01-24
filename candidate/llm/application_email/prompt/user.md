## Job listing
```text
- Title: {{ $('loop-over-jobs4').item.json.job }}
- Salary: {{ $('loop-over-jobs4').item.json.salary }}
- Type: {{ $('loop-over-jobs4').item.json.type }}
- City: {{ $('loop-over-jobs4').item.json.city }}
- Source: {{ $('loop-over-jobs4').item.json.site }}
{{ $('loop-over-jobs4').item.json.description }}
```
## Curriculum Vitae
```text
{{ $('candidate').item.json.resume }}
```
## Compatibility score
```text
score: {{ $('loop-over-jobs4').item.json.score }}
reasoning: {{ $('loop-over-jobs4').item.json.score_reasoning }}
```
## Application letter
```text
{{ $('loop-over-jobs4').item.json.application_letter }}
```
