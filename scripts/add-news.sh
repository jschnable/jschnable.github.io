#!/bin/bash
#
# Add a news item to the Schnable Lab website
# Usage: ./scripts/add-news.sh
#

NEWS_FILE="_data/news.yml"
IMAGES_DIR="images/News_Images"

# Change to repo root
cd "$(dirname "$0")/.." || exit 1

echo "=== Add News Item ==="
echo

# Date (default: today)
DEFAULT_DATE=$(date +%Y-%m-%d)
read -rp "Date [$DEFAULT_DATE]: " DATE
DATE=${DATE:-$DEFAULT_DATE}

# Title (required)
while [[ -z "$TITLE" ]]; do
    read -rp "Title: " TITLE
done

# Summary (required)
echo "Summary (press Enter twice when done):"
SUMMARY=""
while IFS= read -r line; do
    [[ -z "$line" ]] && break
    SUMMARY="${SUMMARY}${SUMMARY:+ }${line}"
done

# Image (optional)
echo
echo "Image options:"
echo "  1. Enter path to existing image in $IMAGES_DIR"
echo "  2. Enter full path to copy a new image"
echo "  3. Leave blank for no image"
read -rp "Image: " IMAGE_INPUT

IMAGE=""
if [[ -n "$IMAGE_INPUT" ]]; then
    if [[ -f "$IMAGES_DIR/$IMAGE_INPUT" ]]; then
        # Existing image in News_Images
        IMAGE="/$IMAGES_DIR/$IMAGE_INPUT"
    elif [[ -f "$IMAGE_INPUT" ]]; then
        # Copy new image to News_Images
        BASENAME=$(basename "$IMAGE_INPUT")
        cp "$IMAGE_INPUT" "$IMAGES_DIR/$BASENAME"
        IMAGE="/$IMAGES_DIR/$BASENAME"
        echo "Copied image to $IMAGES_DIR/$BASENAME"
    elif [[ "$IMAGE_INPUT" == /* ]]; then
        # Absolute path provided (assume it's correct)
        IMAGE="$IMAGE_INPUT"
    else
        echo "Warning: Image not found, skipping"
    fi
fi

# People (optional)
echo
echo "People page links (e.g., /peoplepages/RyleighK/)"
echo "Enter one per line, blank line when done:"
PEOPLE=()
while IFS= read -r person; do
    [[ -z "$person" ]] && break
    PEOPLE+=("$person")
done

# Build the YAML entry
echo
echo "=== Preview ==="
echo "- date: '$DATE'"
echo "  title: $TITLE"
[[ -n "$IMAGE" ]] && echo "  image: $IMAGE"
echo "  summary: \"$SUMMARY\""
if [[ ${#PEOPLE[@]} -gt 0 ]]; then
    echo "  people:"
    for p in "${PEOPLE[@]}"; do
        echo "    - $p"
    done
fi
echo

read -rp "Add this entry? [Y/n]: " CONFIRM
CONFIRM=${CONFIRM:-Y}

if [[ "$CONFIRM" =~ ^[Yy] ]]; then
    # Create the new entry
    ENTRY="- date: '$DATE'
  title: $TITLE"
    [[ -n "$IMAGE" ]] && ENTRY="$ENTRY
  image: $IMAGE"
    ENTRY="$ENTRY
  summary: \"$SUMMARY\""
    if [[ ${#PEOPLE[@]} -gt 0 ]]; then
        ENTRY="$ENTRY
  people:"
        for p in "${PEOPLE[@]}"; do
            ENTRY="$ENTRY
    - $p"
        done
    fi

    # Prepend to news.yml (newer items at top)
    {
        echo "$ENTRY"
        cat "$NEWS_FILE"
    } > "${NEWS_FILE}.tmp" && mv "${NEWS_FILE}.tmp" "$NEWS_FILE"

    echo "Added news item to $NEWS_FILE"
else
    echo "Cancelled"
fi
