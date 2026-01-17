#!/bin/bash
#                                  MIT License
#                       Copyright 2026, Sébastien Kéroack
# ==============================================================================

# Check for required files
required_files=(
  "env.sh"
  "candidate/resume.md"
  "candidate/info.json"
  "candidate/avatar.jpeg"
  "candidate/cover_letter.template.html"
)

missing=0
for file in "${required_files[@]}"; do
  if [ ! -f "$file" ]; then
    ext="${file##*.}"
    file_name="${file%.*}"
    [ "$missing" -eq 1 ] && echo "---"
    echo "Error: $file file not found!"
    echo "Create it by copying:"
    echo "  cp ${file_name}.fake.${ext} $file"
    case "$file" in
      "env.sh")
        echo "Then edit $file to add your environment configuration parameters."
        ;;
      "candidate/resume.md")
        echo "Then edit $file to add your resume information in markdown format."
        ;;
      "candidate/info.json")
        echo "Then edit $file to add your personal information in JSON format."
        ;;
      "candidate/avatar.jpeg")
        echo "Then replace $file with your actual avatar image."
        ;;
      "candidate/cover_letter.template.html")
        echo "Then edit $file to customize your cover letter template."
        ;;
      *)
        ;;
    esac
    missing=1
  fi
done

[ "$missing" -eq 1 ] && exit 1
echo "All required candidate files are present."
exit 0