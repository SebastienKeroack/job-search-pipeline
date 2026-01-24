## Job listing
```text
- Title: {{ $('loop-over-jobs1').item.json.job }}
- Level: {{ $('loop-over-jobs1').item.json.level }}
- Salary: {{ $('loop-over-jobs1').item.json.salary }}
- Type: {{ $('loop-over-jobs1').item.json.type }}
- City: {{ $('loop-over-jobs1').item.json.city }}
{{ $('loop-over-jobs1').item.json.description }}
```
## Curriculum Vitae
```text
{{ $('candidate').item.json.resume }}
```
