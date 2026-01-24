## Parameters
- Method: POST
- URL: https://api.openai.com/v1/responses
- Authentication: Predefined Credential Type
- Credential Type: OpenAi
- OpenAi: OpenAi account
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
  "model": "gpt-5-mini",
  "reasoning": {"effort": "low"},
  "max_output_tokens": 2048,
  "instructions": {{ JSON.stringify($json.system) }},
  "input": {{ JSON.stringify($json.user) }},
  "text": {
    "format": {
      "name": "content",
      "type": "json_schema",
      "strict": true,
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "score": {"type": "integer", "minimum": 0, "maximum": 10},
          "reasoning": {"type": "string", "maxLength": 1800}
        },
        "required": ["score", "reasoning"]
      }
    }
  },
  "store": false
}
```
// 900000 milliseconds = 15 minutes
- Timeout: 900000
