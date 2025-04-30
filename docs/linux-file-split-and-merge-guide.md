# Linux File Split and Merge Guide

## Split Large Files

Split a large file into 99MB chunks:

````bash
# Replace source.mp4 with your filename
FILENAME="source.mp4"
split -b 99m -d "$FILENAME" "${FILENAME}_part_"
````

## Merge Split Files

Merge the split parts back together:

````bash
cat "${FILENAME}_part_"* > "restored_${FILENAME}"
````

## Verify File Integrity

Compare original and restored files using `cmp`:

````bash
cmp --silent "$FILENAME" "restored_${FILENAME}" && \
echo "✅ Files are identical" || echo "❌ Files are different"
````

## Clean Up (Optional)

Remove split files after successful verification:

````bash
rm "${FILENAME}_part_"*
````

## Example Output

```
source.mp4_part_00
source.mp4_part_01
source.mp4_part_02
...
```

**Features:**

- Uses numeric suffixes (`-d`)
- 99MB chunks (`-b 99m`)
- Simple verification with `cmp`
- No external dependencies
- Works on any Linux distribution

**Note:** Replace `source.mp4` with your actual filename in all commands.
