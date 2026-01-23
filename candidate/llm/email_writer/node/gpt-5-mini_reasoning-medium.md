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
  "reasoning": {"effort": "medium"},
  "max_output_tokens": 8192,
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
          "subject": {"type": "string", "maxLength": 98},
          "body": {"type": "string", "maxLength": 2730}
        },
        "required": ["subject", "body"]
      }
    }
  },
  "store": false
}
```
