# Warp Watcher
A minimal tornado webapp to display thumbnails of micrographs processed by [Warp](http://www.warpem.com/warp/).

![Warp Watcher Screenshot](screenshot.png?raw=true)

Because windows is not amenable to multiple remote users, we have found it
useful to be able to track warp progress remotely. This minimal python-based
application allows remote viewing in a mobile-friendly format of the thumbnails
output by warp over time. The server has global state, as it is intended to view
the live output of warp as it runs. Every user will see the same data and
changing the warp folder changes the views for all users.

## Installation and Operation
This program requires `python 3.7` due to the async/await syntax used.
Due to changes in the IOLoop, this program is not windows compatible if run with
`python 3.8` or above.

Setup:
```bash
git clone https://github.com/bbarad/warp_watcher && cd warp_watcher
pip install -r requirements.txt # only requirement currently is tornado
python main.py --port=8080 --parent_path=$WARP_PARENT_PATH --thumbnail_count=200
```

Operation:
1. Point a web browser at the IP or DNS name and port for the computer running
the program.
2. Click "Update Warp Directory" and provide the name of the warp directory -
not the full path, most of which should be in the `parent_path` configuration flag.
3. Wait.

_Note: Warp's thumbnails reflect not only the raw image, but any overlays that are
applied in the `Real Space` panel - including displaying particle positions,
local defocus, and masking._

## Future Directions
As warp becomes RESTful, this program may be expanded to include more status
information about warp's progress.
