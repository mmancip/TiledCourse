#!/bin/bash
pgrep "(.*session.*|.*terminal.*|.*onsole.*)" | xargs -I{} cat /proc/{}/environ 2>/dev/null | tr '\0' '\n' | grep -m1 '^DISPLAY=' |tee -a ./out_DISPLAY
