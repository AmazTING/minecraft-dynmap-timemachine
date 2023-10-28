pip install -r "requirements.txt"
python dynmap-timemachine.py https://map.ccnetmc.com/nationsmap world flat "[10750,65,-1]" "[336,336]" 0 right.png -v
python dynmap-timemachine.py https://map.ccnetmc.com/nationsmap world flat "[-10750,65,0]" "[336,336]" 0 left.png -v
python ./borders/main.py
python ./borders/upscaler.py
vips.exe crop "right.png" "rightcropped.png" 128 0 85888 86016 --vips-progress
vips.exe arrayjoin "left.png rightcropped.png" final.tif[compression=deflate,tile,bigtiff] --across 2 --vips-progress
vips.exe composite2 "final.tif" "borders_resized.tif" full_map.tif[compression=deflate,tile,bigtiff] "over" --x -128 --vips-progress
