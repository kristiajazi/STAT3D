#!/bin/bash
# STAT3D system information display

# Activate pixi environment
export PATH="/etc/stat3d/.pixi/envs/default/bin:$PATH"

echo "=== STAT3D System Information ==="
echo ""
echo "Container built: $(date -r /etc/stat3d/pixi.toml +'%Y-%m-%d %H:%M' 2>/dev/null || echo 'unknown')"
echo "Pixi version: $(pixi --version 2>/dev/null || echo 'unavailable')"
echo ""
echo "=== Python Environment ==="
python --version
echo ""
echo "=== Python Packages ==="
pip list
echo ""
echo "=== R Environment ==="
R --version | head -n1
echo ""
echo "=== R Packages ==="
R -e "ip <- installed.packages()[,c(1,3)]; print(as.data.frame(ip), row.names=FALSE)" 2>/dev/null
echo ""
echo "=== Conda/Pixi Packages ==="
pixi list
