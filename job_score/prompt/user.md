## Job posting data
- Title: {{ $('loop-over-jobs').item.json.job ?? 'N/A' }}
- Salary: {{ $('loop-over-jobs').item.json.salary ?? 'N/A' }}
- Type: {{ $('loop-over-jobs').item.json.type ?? 'N/A' }}
- City: {{ $('loop-over-jobs').item.json.city ?? 'N/A' }}
## Job description
```text
{{ $('loop-over-jobs').item.json.description ?? 'N/A' }}
```
## Candidate profile (resume)
```text
{{ $('resume').item.json.content ?? 'N/A' }}
```