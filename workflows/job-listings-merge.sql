-- Select all columns from both inputs
SELECT *
FROM input1 i1

-- Left join input2 so we keep all rows from input1
-- even when there is no matching URL in input2
LEFT JOIN input2 i2
  ON i1.[url] = i2.[url]

-- Filter to rows where input2 is missing
-- or where the score is missing or invalid
WHERE i2.[url] IS NULL        -- No matching URL found in input2
   OR i2.[score] IS NULL      -- Score is NULL
   OR i2.[score] = ''         -- Score is an empty string
   OR i2.[score] = 'N/A'      -- Score marked as not available
   OR i2.[score] = 'TODO'     -- Score marked as a placeholder
