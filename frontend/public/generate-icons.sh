#!/bin/bash
# Generate simple placeholder PWA icons using ImageMagick or create simple SVG icons

# Create a simple 192x192 PNG icon (blue circle with "N" for Navo)
convert -size 192x192 xc:transparent -fill "#3b82f6" -draw "circle 96,96 96,0" -fill white -font Arial-Bold -pointsize 120 -gravity center -annotate +0+0 "N" pwa-192x192.png 2>/dev/null || echo "ImageMagick not available, creating placeholder"

# Create a simple 512x512 PNG icon
convert -size 512x512 xc:transparent -fill "#3b82f6" -draw "circle 256,256 256,0" -fill white -font Arial-Bold -pointsize 320 -gravity center -annotate +0+0 "N" pwa-512x512.png 2>/dev/null || echo "ImageMagick not available, creating placeholder"

# Create favicon
convert -size 32x32 xc:transparent -fill "#3b82f6" -draw "circle 16,16 16,0" -fill white -font Arial-Bold -pointsize 20 -gravity center -annotate +0+0 "N" favicon.ico 2>/dev/null || echo "ImageMagick not available"
