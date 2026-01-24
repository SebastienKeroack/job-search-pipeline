## Job listing
```text
- Title: {{ $('loop-over-jobs2').item.json.job }}
- Level: {{ $('loop-over-jobs2').item.json.level }}
- Salary: {{ $('loop-over-jobs2').item.json.salary }}
- Type: {{ $('loop-over-jobs2').item.json.type }}
- City: {{ $('loop-over-jobs2').item.json.city }}
- Source: {{ $('loop-over-jobs2').item.json.site }}
{{ $('loop-over-jobs2').item.json.description }}
```
## Curriculum Vitae
```text
{{ $('candidate').item.json.resume }}
```
## Compatibility score
```text
score: {{ $('loop-over-jobs2').item.json.score }}
reasoning: {{ $('loop-over-jobs2').item.json.score_reasoning }}
```
