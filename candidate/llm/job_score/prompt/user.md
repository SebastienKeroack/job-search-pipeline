## Job posting data
- Title: {{ $('loop-over-jobs1').item.json.job }}
- Salary: {{ $('loop-over-jobs1').item.json.salary }}
- Type: {{ $('loop-over-jobs1').item.json.type }}
- City: {{ $('loop-over-jobs1').item.json.city }}
## Job description
```text
{{ $('loop-over-jobs1').item.json.description }}
```
## Candidate profile (resume)
```text
{{ $('candidate').item.json.resume }}
```