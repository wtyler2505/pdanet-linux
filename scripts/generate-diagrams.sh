#!/bin/bash
# generate-diagrams.sh - Automated diagram generation for PdaNet Linux

set -euo pipefail

DOCS_DIR="docs/architecture"
PUML_FILES="$DOCS_DIR/*.puml"
OUTPUT_DIR="$DOCS_DIR/generated"
TOOLS_DIR="tools"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Create necessary directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$TOOLS_DIR"

log "Generating PdaNet Linux architecture diagrams..."

# Download PlantUML if not present
PLANTUML_JAR="$TOOLS_DIR/plantuml.jar"
if [[ ! -f "$PLANTUML_JAR" ]]; then
    log "PlantUML not found. Downloading latest version..."

    # Try to download from GitHub releases
    if command -v wget &> /dev/null; then
        wget -O "$PLANTUML_JAR" "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
    elif command -v curl &> /dev/null; then
        curl -L -o "$PLANTUML_JAR" "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar"
    else
        error "Neither wget nor curl found. Please install one of them or manually download PlantUML."
        exit 1
    fi

    if [[ ! -f "$PLANTUML_JAR" ]]; then
        error "Failed to download PlantUML. Please check your internet connection."
        exit 1
    fi

    log "PlantUML downloaded successfully."
fi

# Check Java availability
if ! command -v java &> /dev/null; then
    error "Java is required but not installed. Please install OpenJDK 8 or later."
    exit 1
fi

# Generate diagrams
DIAGRAM_COUNT=0
FAILED_COUNT=0

log "Processing PlantUML files in $DOCS_DIR..."

for puml_file in $DOCS_DIR/*.puml; do
    if [[ -f "$puml_file" ]]; then
        filename=$(basename "$puml_file" .puml)
        log "  Generating diagrams for $filename..."

        # Generate PNG for web display (high resolution)
        if java -jar "$PLANTUML_JAR" -tpng -Sbackgroundcolor=white -o "$(realpath $OUTPUT_DIR)" "$puml_file"; then
            log "    ✓ PNG generated"
        else
            error "    ✗ Failed to generate PNG"
            ((FAILED_COUNT++))
            continue
        fi

        # Generate SVG for high-quality print and web
        if java -jar "$PLANTUML_JAR" -tsvg -o "$(realpath $OUTPUT_DIR)" "$puml_file"; then
            log "    ✓ SVG generated"
        else
            warn "    ⚠ Failed to generate SVG (non-critical)"
        fi

        # Generate text format for accessibility
        if java -jar "$PLANTUML_JAR" -ttxt -o "$(realpath $OUTPUT_DIR)" "$puml_file"; then
            log "    ✓ Text version generated"
        else
            warn "    ⚠ Failed to generate text version (non-critical)"
        fi

        ((DIAGRAM_COUNT++))
    fi
done

if [[ $DIAGRAM_COUNT -eq 0 ]]; then
    warn "No PlantUML files found in $DOCS_DIR"
    exit 0
fi

if [[ $FAILED_COUNT -gt 0 ]]; then
    error "Failed to generate $FAILED_COUNT out of $DIAGRAM_COUNT diagrams"
    exit 1
fi

log "Successfully generated diagrams for $DIAGRAM_COUNT files"
log "Output directory: $OUTPUT_DIR"

# Generate index.html for easy viewing
log "Generating diagram index..."

cat > "$OUTPUT_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PdaNet Linux - Architecture Diagrams</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .diagram-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .diagram-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background: #fafafa;
        }
        .diagram-card h3 {
            margin-top: 0;
            color: #34495e;
        }
        .diagram-card img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        .download-links {
            margin-top: 10px;
        }
        .download-links a {
            display: inline-block;
            margin-right: 10px;
            padding: 5px 10px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 12px;
        }
        .download-links a:hover {
            background: #2980b9;
        }
        .timestamp {
            text-align: center;
            color: #7f8c8d;
            margin-top: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>PdaNet Linux - Architecture Diagrams</h1>
        <p>This page contains all architecture diagrams for the PdaNet Linux project, generated from PlantUML source files.</p>

        <div class="diagram-grid">
EOF

# Add each diagram to the index
for png_file in "$OUTPUT_DIR"/*.png; do
    if [[ -f "$png_file" ]]; then
        filename=$(basename "$png_file" .png)

        # Create diagram card
        cat >> "$OUTPUT_DIR/index.html" << EOF
            <div class="diagram-card">
                <h3>$filename</h3>
                <img src="$(basename "$png_file")" alt="$filename diagram">
                <div class="download-links">
                    <a href="$(basename "$png_file")">PNG</a>
EOF

        # Add SVG link if available
        if [[ -f "$OUTPUT_DIR/$filename.svg" ]]; then
            echo "                    <a href=\"$filename.svg\">SVG</a>" >> "$OUTPUT_DIR/index.html"
        fi

        # Add text link if available
        if [[ -f "$OUTPUT_DIR/$filename.txt" ]]; then
            echo "                    <a href=\"$filename.txt\">Text</a>" >> "$OUTPUT_DIR/index.html"
        fi

        cat >> "$OUTPUT_DIR/index.html" << EOF
                </div>
            </div>
EOF
    fi
done

# Close HTML
cat >> "$OUTPUT_DIR/index.html" << EOF
        </div>

        <div class="timestamp">
            Generated on $(date '+%Y-%m-%d %H:%M:%S')
        </div>
    </div>
</body>
</html>
EOF

log "Diagram index generated: $OUTPUT_DIR/index.html"
log "Diagram generation complete!"

# Show summary
echo
echo "=== Generation Summary ==="
echo "Total diagrams: $DIAGRAM_COUNT"
echo "Failed: $FAILED_COUNT"
echo "Output directory: $OUTPUT_DIR"
echo "View diagrams: file://$(realpath $OUTPUT_DIR)/index.html"