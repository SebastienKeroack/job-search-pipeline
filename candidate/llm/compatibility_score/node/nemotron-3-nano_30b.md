## Parameters
- Method: POST
- URL: http://ollama:11434/v1/chat/completions
- Authentication: None
- Send Query Parameters: OFF
- Send Headers: ON
- Specify Headers: Using Fields Below
  - Name: Content-Type
  - Value: application/json
- Send Body: ON
- Body Content Type: JSON
- Specify Body: Using JSON
```json
{
  "model": "nemotron-3-nano:30b",
  "temperature": 0,
  "max_tokens": 2048,
  "messages": [
    { "role": "system", "content": {{ JSON.stringify($json.system) }} },
    { "role": "user", "content": {{ JSON.stringify($json.user) }} }
  ],
  "response_format": { "type": "json_object" },
  "stream": false
}
```
### Options:
- Timeout: 2700000
