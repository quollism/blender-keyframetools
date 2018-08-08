# blender-keyframe-manipulation-tools

An add-on for Blender with handy tools for working with keyframes.

## Limitations

This software is in its very very very very very very early stages. It is offered here because people on Twitter were all like "wow this looks awesome i want to try it".

It does not work in Blender 2.8 yet. The 2.8 API is still unstable. We're developing it for 2.79b.

* **Only tested in 2.79b for now, does not work in 2.8**
* The tools currently only works on bone keyframes. **They do not work on object keyframes**.
* There are **no keymaps or pie menus yet**. These will come.

## Functions

This add-on currently adds the following operators. You can get to them via Space Bar search. (Again, 2.8 is not supported yet.)

### Graph Editor

#### Keyframe manipulating tools

All of these should work with multiple bone channels. They do not work on object animation. Yet.

* **Flatten Keyframes**: Non-interactively flattens selected keyframes to a straight line between the first and last keyframe of the selection. Useful for tidying up.
* **Flatten/Exaggerate Keyframes**: Interactively flattens or exaggerates selected keyframes along a straight line between the first and last keyframe of the selection. Useful for making a motion smaller or bigger.
* **Ease Keyframes**: Interactively create an ease in or ease out for a selection of keyframes. Useful for tidying up an ease pattern.   

#### Shortcut tool

* **Place Cursor and Pivot**: Places the 2D Cursor at the selection and changes Pivot Center to 2D Cursor. Ctrl+G but better. Suggest keymapping it Ctrl+Shift+G. 

## Roadmap

* Some kind of pie menu or keymap.
* Add: Smooth Rough tool from animBot (will be called Dampen/Excite)
* Make existing tools work with object-level animation
* More to follow...
* Work on Blender 2.8 compatibility once 2.8 API is declared stable. 
