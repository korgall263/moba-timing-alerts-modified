# MOBA timer alerts

## What is this
`moba.py` is a script to start right when your game of Deadlock begins (i.e. run it, then click enter in the window when the clock hits 10).
This is a relatively common MOBA training technique.

It plays voice lines and/or sound effects to alert you when particular events that happen on a set schedule happen.
You can change the alerts by editing the code.
Currently:
- alerts when a new wave spawns ("Wave.")
- plays a short beep every 10s to remind you to check the map
- Alerts when small/medium/large and safe camps spawn ("[size] camps.")
- Alerts 1min before, 30s before, and 10s before buffs (and potentially urn) spawn.

`generate.py` uses your system speech synth to generate TTS versions of the alerts I mentioned.
You don't need to use this if you don't want; I threw in the ones I generated.

`moba.py` requires `pygame`. `generate.py` requires `pyttsx3`. Install `pygame` or both with pip.

## I don't like your set of alerts, sounds, etc.
Just edit `events` in `moba.py`, and provide/generate your own sounds.

## Why is this?
I kinda wanted to try it and spent longer than it would've taken to write it myself making LLMs do the job.
Just saving you a step!

## What can I do with this?
Whatever you want.


##Modieded## - code updated with chatgpt, I am not a programmer
Added:
-Alt+p global pause (install keyboard - "pip install keyboard"
-"sync mm:ss" command
- basic graphic display to show:
--current time
--paused or not
--3 next up events
--list of events except map check

