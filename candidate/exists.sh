#!/bin/bash
#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

# Check for required files
required_files=(
  ".env"
  "candidate/resume.md"
  "candidate/candidate.json"
  "candidate/search.json"
  "candidate/application_letter.html"
  "candidate/avatar.jpeg"
)

missing=0
for file in "${required_files[@]}"; do
  if [ ! -f "$file" ]; then
    # Get file extension and name
    ext="${file##*.}"
    file_name="${file%.*}"

    # Print error message with instructions
    [ "$missing" -eq 1 ] && echo "---"
    echo "Error: $file file not found!"
    echo "Create it by copying:"
    echo "  cp ${file_name}.example.${ext} $file"
    case "$file" in
      ".env")
        echo "Then edit $file to add your environment configuration parameters."
        ;;
      "candidate/resume.md")
        echo "Then edit $file to add your resume information in markdown format."
        ;;
      "candidate/candidate.json")
        echo "Then edit $file to add your personal information in JSON format."
        ;;
      "candidate/search.json")
        echo "Then edit $file to add your search criteria in JSON format."
        ;;
      "candidate/application_letter.html")
        echo "Then edit $file to customize your application letter template."
        ;;
      "candidate/avatar.jpeg")
        echo "Then replace $file with your actual avatar image."
        ;;
      *) echo "Please create and edit $file accordingly."
        ;;
    esac
    missing=1
  fi
done

if [ -f "candidate/search.json" ]; then
  # Remove // and /* */ comments, then pretty-print with jq
  temp_file=$(mktemp)
  sed -E 's/\/\/.*$//; s/\/\*.*\*\///g' "candidate/search.json" \
    | jq '.' > "$temp_file"
  mv "$temp_file" candidate/search.json
fi

[ "$missing" -eq 1 ] && exit 1
echo "All required candidate files are present."
exit 0
