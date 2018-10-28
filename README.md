# blender-keyframetools

Some handy tools for working with keyframes in Blender. Inspired by Alan Camilo's animBot.

## Limitations

This software is in its very very very very early stages. It is offered here because people on Twitter were all like "wow this looks awesome i want to try it". And it's even a little bit useful!

**Note**: This tool doesn't work for all types of F-Curves yet. Bones and object-level animation are good to go as of 0.5.0 but properties in materials, the scene and the world don't respond to these tools yet because they're in a different part of the API. (Hopefully this weird state of affairs gets fixed in Blender 2.8's Python API.)

**Only in development for 2.79b, does not work in 2.8 yet. 2.8 is wonderful though, isn't it?**

## Functions

### Pie menu

The pie menu (formerly bound to Shift+Z) needs to be set up manually in the keymap for now. (This will be easier in the future.)

To set up the hotkey:

* Go to File -> User Preferences -> Input, scroll down to "Graph Editor", then "Graph Editor (Global)"
* Scroll down to where it says "Add new", then click it and fill in the following information.

* Operator name: wm.call\_menu\_pie
* Name field (greyed out, click it anyway): GRAPH\_PIE\_keyframetools\_piemenu

Please refer to the pie menu setup image included in the codebase for how it should look. And don't forget to save your user preferences afterwards!

You can also access the functions from the Space Bar. (2.8 is not supported yet.)

### Graph Editor

#### Keyframe manipulating tools

All of these should work with multiple bone channels and object-level animation. Material values and scene-level 

* **Flatten Keyframes** (hotkey Ctrl+A): Non-interactively flattens selected keyframes to a straight line between the first and last keyframe of the selection. Useful for tidying up. Works on multiple channels.
* **Flatten/Exaggerate Keyframes** (hotkey D): Interactively flattens or exaggerates selected keyframes along a straight line between the first and last keyframe of the selection. Useful for making a motion smaller or bigger. Also works on multiple channels. 
* **Ease Keyframes** (hotkey Shift+A): Interactively create an ease in or ease out for a selection of keyframes. Useful for tidying up an ease pattern. Also works on multiple channels.

#### Shortcut tool

* **Place Cursor and Pivot** (hotkey Ctrl+Shift+G): Places the 2D Cursor at the selection and changes Pivot Center to 2D Cursor. Like Ctrl+G but better.

## Roadmap

These are the current priorities as of version 0.5.0 (27 October 2018)

### Coming Keyframe-Related Additions

* Smooth Rough tool from animBot (will be called Dampen/Excite)
* More stuff depending on what Looch thinks is useful :)

### Coming Other Changes and Fixes

* UI: Make the pie menu hotkey settable from user preferences.
* All: Make all F-Curve types manipulable, including properties belonging to materials, scenes and worlds.
* Ease: Do something more helpful with out-of-bounds keys 

Work on Blender 2.8 compatibility will begin after 2.8 API is declared stable by the Blender devs, maybe November? 

## Acknowledgements

Thanks to

* Luciano "Looch" Muñoz for guidance and encouragment
* Irmitya for making object-level animation work and choosing some hotkeys! :)
* Alan Camilo for inspiring us with animBot
