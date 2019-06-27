# blender-keyframetools

Handy tools for working with keyframes in Blender. Inspired by Alan Camilo's animBot.

## Limitations

This add-on is in its very early stages of development. It is offered here because people on Twitter were all "wow this looks awesome i want to try it".

**Note**: This tool doesn't work for all types of F-Curves yet!

* Good to go: Bones, object properties and object-level animation.
* Not working yet: Shape keys, properties of materials, the scene and the world aren't editable yet. The add-on doesn't know they don't work yet though which is strangely cute of it. :)

## Functions

All current functions are for the Graph Editor only.

### Keyframe manipulating tools

All of these should work with multiple bone channels and object-level animation. Material values and scene-level 

* **Flatten Keyframes** (hotkey Ctrl+A): Non-interactively flattens selected keyframes to a straight line between the first and last keyframe of the selection. Useful for tidying up. Works on multiple channels.
* **Flatten/Exaggerate Keyframes** (hotkey D): Interactively flattens or exaggerates selected keyframes along a straight line between the first and last keyframe of the selection. Useful for making a motion smaller or bigger. Also works on multiple channels. 
* **Ease Keyframes** (hotkey Shift+A): Interactively create an ease in or ease out for a selection of keyframes. Useful for tidying up an ease pattern. Also works on multiple channels. 

### Shortcut tool

* **Place Cursor and Pivot** (hotkey Ctrl+Shift+G): Places the 2D Cursor at the selection and changes Pivot Center to 2D Cursor. Like Ctrl+G but better.

### Pie menu

The pie menu is bound to Shift+Z. This gives you Ease Keys, Flatten Keys, Flatten/Exaggerate Keys and Place Cursor and Pivot.

### Changing hotkeys

If you don't like the hotkeys, you can always change them in the keymap!

* Go to File -> User Preferences -> Input
* Change the Search mode to Key Binding, then type in the hotkey Z.
* Scroll down to "Graph Editor" and look for the hotkey in question by function. (Note: The pie menu is disguised as "Call Pie Menu", see the pie menu setup graphic for how it should look)
* To change the hotkey, hit the > to the left and change the key to whatever you like. To get rid of the shortcut, click the big X.

Don't forget to save your user preferences afterwards! (Hint: click **Save User Settings** at the bottom left.)

You can also access the functions from the Function Search menu. (Space Bar on legacy keymap.)

## Roadmap

These are the current priorities as of version 0.6.1 (27 June 2019)

### Coming Other Changes and Fixes

* All: Make all F-Curve types manipulable, including properties belonging to materials, scenes and worlds.
* Ease: Do something more helpful with out-of-bounds keys 
* Share Keys: Make it work again

### Coming Keyframe-Related Additions

* Smooth Rough tool from animBot (probably will be called Dampen/Excite)
* More stuff depending on what Looch thinks is useful :)

Please do not ask for timelines. :)

## Acknowledgements

Thanks to

* Luciano "Looch" Muñoz for guidance and encouragment
* Irmitya for contributing object-level animation and finally choosing some hotkeys! :)
* Alan Camilo for inspiring us with animBot
