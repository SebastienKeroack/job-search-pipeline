//                                MIT License
//                     Copyright 2026, Sébastien Kéroack
// =============================================================================

// Recommended delay range in milliseconds (e.g., 25000-55000 ms)
const MIN_DELAY = 25000;
const MAX_DELAY = 55000;

// Generate a random delay in the range
const delay = Math.floor(Math.random() * (MAX_DELAY - MIN_DELAY + 1)) + MIN_DELAY;

// Wait for the delay (n8n Code node supports async/await)
await new Promise(resolve => setTimeout(resolve, delay));

// Optionally output the delay for logging/debugging
return [{ json: { waitedMs: delay } }];