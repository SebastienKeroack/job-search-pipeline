-- Select rows from input1 where either:
-- 1. [url] does NOT exist in input2 (unmatched urls)
-- 2. [url] exists in input2 and [score] is empty, null, 'N/A', or 'TODO'
SELECT *
FROM input1 i1
LEFT JOIN input2 i2 ON i1.[url] = i2.[url]
WHERE i2.[url] IS NULL
   OR i2.[score] IS NULL
   OR i2.[score] = ''
   OR i2.[score] = 'N/A'
   OR i2.[score] = 'TODO'