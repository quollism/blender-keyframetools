# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Keyframe Manipulation Tools",
    "author": "quollism",
    "version": (0, 4),
    "blender": (2, 79, 0),
    "description": "Some helpful tools for working with keyframes. Inspired by Alan Camilo's animBot toolset.",
    "warning": "Pre-release software. Only armature animation is supported so far. Working on it!",
    "category": "Animation"
}

import bpy
from copy import deepcopy
from mathutils import Vector
from bpy.props import FloatVectorProperty

class keytools_FlattenKeys(bpy.types.Operator):
    """Converges keys and handles to a linear fit between the first and last keyframe of the selection"""
    bl_idname = "graph.flatten_keys"
    bl_label = "Flatten Keyframes"

    def execute(self, context):
        curve_datas = keytools_getSelectedKeysAndExtents()
        for curve_data in curve_datas:
            slopeMaker = keytools_slopeMaker(curve_data[1], curve_data[2])
            for i, keyframe in enumerate(curve_data[0]):
                keyframe.co[1] = slopeMaker.linear_fit(keyframe.co[0])
                keyframe.handle_left[1] = slopeMaker.linear_fit(keyframe.handle_left[0])
                keyframe.handle_right[1] = slopeMaker.linear_fit(keyframe.handle_right[0])
        return { 'FINISHED' }

def keytools_getSelectedKeysAndExtents():
    curve_datas = []
    bone_names = [b.name for b in bpy.context.selected_pose_bones]
    fcurves = bpy.context.active_object.animation_data.action.fcurves
    for curve in fcurves:
        first_co = None
        points = None
        last_co = None
        if curve.data_path.split('"')[1] in bone_names:
            keyframes_referenced = []
            keyframes_data = []
            for keyframe in curve.keyframe_points:
                if keyframe.select_control_point:
                    if first_co == None:
                        first_co = keyframe.co
                    else:
                        last_co = keyframe.co
                    keyframes_referenced.append(keyframe)
                    keyframes_data.append( {
                        'co': deepcopy(keyframe.co),
                        'handle_left': deepcopy(keyframe.handle_left),
                        'handle_right': deepcopy(keyframe.handle_right)
                    } ) # needs to be all three data points!
            if last_co != None:
                curve_datas.append([keyframes_referenced, first_co, last_co, keyframes_data])
    return curve_datas

class keytools_slopeMaker():
    def __init__(self, first_co, last_co):
        self.start_frame = first_co[0]
        self.start_value = first_co[1]
        self.finish_frame = last_co[0]
        self.finish_value = last_co[1]
        self.length = last_co[0] - first_co[0]
        self.height = last_co[1] - first_co[1]

    def linear_fit(self, frame):
        position = (frame - self.start_frame) / self.length
        unadjusted_value = position * self.height
        final_value = self.start_value + unadjusted_value
        # print("value for "+str(frame)+" calculated at "+str(final_value)+" from unadjusted value "+str(unadjusted_value))
        return final_value

    def flatten_exaggerate(self, frame, orig_value, factor):
        linear_value = self.linear_fit(frame)
        final_value = (orig_value - linear_value) * factor + linear_value
        # print("value for "+str(frame)+" calculated at "+str(final_value))
        return final_value

    # TODO: a nicer way to handle out-of-bounds frames
    def ease(self, frame, exponent, orig_value):
        position = (frame - self.start_frame) / self.length
        if position < 0 or position > 1:
            return orig_value # do nothing for now
        # if exponent is 0.0 then we can just calculate the linear case and go home for the day
        if exponent != 0.0:
            # ensure exponent never drifts beyond anything usable
            safe_exponent = max(1, min(10, (abs(exponent) + 1)))
            # invert the position to get an inverse curve
            if exponent < 0:
                position = 1 - position
            position = pow(position, safe_exponent)
        # invert the position back again so we don't get an upside-down curve
        if exponent < 0:
            position = 1 - position
        final_value = self.start_value + (position * self.height)
        return final_value        

class keytools_EaseKeys(bpy.types.Operator):
    """Puts keys and handles along an eased curve between the first and last keyframe of the selection"""
    bl_idname = "graph.ease_key_selection"
    bl_label = "Ease Keyframes"

    offset = FloatVectorProperty( name="Offset", size=3 )

    def execute(self, context):
        factor = self.offset[0]
        for curve_data in self._curve_datas:
            slopeMaker = keytools_slopeMaker(curve_data[1], curve_data[2])
            for i, keyframe in enumerate(curve_data[0]):
                keyframe.co[1] = slopeMaker.ease(keyframe.co[0], factor, curve_data[3][i]['co'][1])
                keyframe.handle_left[1] = slopeMaker.ease(keyframe.handle_left[0], factor, curve_data[3][i]['handle_left'][1])
                keyframe.handle_right[1] = slopeMaker.ease(keyframe.handle_right[0], factor, curve_data[3][i]['handle_right'][1])

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.offset = (self._initial_mouse - Vector((event.mouse_x, event.mouse_y, 0.0))) * -0.02
            self.execute(context)
            context.area.header_text_set("Ease Factor %.4f" % (self.offset[0]))

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set()
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            for curve_data in self._curve_datas:
                for i, keyframe in enumerate(curve_data[0]):
                    keyframe.co[1] = curve_data[3][i]['co'][1]
                    keyframe.handle_left[1] = curve_data[3][i]['handle_left'][1]
                    keyframe.handle_right[1] = curve_data[3][i]['handle_right'][1]                
            context.area.header_text_set()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'GRAPH_EDITOR':
            self._initial_mouse = Vector((event.mouse_x, event.mouse_y, 0.0)) 
            self._curve_datas = keytools_getSelectedKeysAndExtents()
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be graph editor")
            return {'CANCELLED'}

class keytools_FlattenExaggerateKeys(bpy.types.Operator):
    """Scales keys and handles to/from a linear fit between the first and last keyframe of the selection"""
    bl_idname = "graph.flatten_exaggerate_key_selection"
    bl_label = "Flatten/Exaggerate Keyframes"

    offset = FloatVectorProperty( name="Offset", size=3 )

    def execute(self, context):
        for curve_data in self._curve_datas:
            slopeMaker = keytools_slopeMaker(curve_data[1], curve_data[2])
            shifted_offset = self.offset[0] + 1
            for i, keyframe in enumerate(curve_data[0]):
                keyframe.co[1] = slopeMaker.flatten_exaggerate(
                    keyframe.co[0], curve_data[3][i]['co'][1], shifted_offset)
                keyframe.handle_left[1] = slopeMaker.flatten_exaggerate(
                    keyframe.handle_left[0], curve_data[3][i]['handle_left'][1], shifted_offset)
                keyframe.handle_right[1] = slopeMaker.flatten_exaggerate(
                    keyframe.handle_right[0], curve_data[3][i]['handle_right'][1], shifted_offset)

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.offset = (self._initial_mouse - Vector((event.mouse_x, event.mouse_y, 0.0))) * -0.01
            self.execute(context)
            context.area.header_text_set("Flatten/Exaggerate Factor %.4f" % (self.offset[0] + 1))

        elif event.type == 'LEFTMOUSE':
            context.area.header_text_set()
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            for curve_data in self._curve_datas:
                for i, keyframe in enumerate(curve_data[0]):
                    keyframe.co[1] = curve_data[3][i]['co'][1]
                    keyframe.handle_left[1] = curve_data[3][i]['handle_left'][1]
                    keyframe.handle_right[1] = curve_data[3][i]['handle_right'][1]                
            context.area.header_text_set()
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.space_data.type == 'GRAPH_EDITOR':
            self._initial_mouse = Vector((event.mouse_x, event.mouse_y, 0.0)) 
            self._curve_datas = keytools_getSelectedKeysAndExtents()
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be graph editor")
            return {'CANCELLED'}

# BUGGY
class keytools_ShareKeys(bpy.types.Operator):
    """Shares keys between visisble animation channels in dope sheet"""
    bl_idname = "action.share_keys"
    bl_label = "Share Keys"

    def execute(self, context):
        # so the vague problem with this
        # is that it overwrites keys from the original
        # which is not what we want
        # but hey better than nothing
        # store current frame from this scene in return_frame
        start_frame = context.scene.frame_current
        context.scene.frame_current = 1
        last_keyed_frame = 0
        bpy.ops.screen.keyframe_jump(next=True)
        #   if current keyframe same as last_keyed frame, break loop
        while last_keyed_frame != context.scene.frame_current:
        # go to "first key"
        # loop:
            #   insert keyframe: bpy.ops.action.keyframe_insert
            bpy.ops.action.keyframe_insert(type='ALL')
            #   record current frame in last_keyed_frame
            last_keyed_frame = context.scene.frame_current
            #   advance to next keyframe: bpy.ops.action.
            bpy.ops.screen.keyframe_jump(next=True)
        # set frame back to return_frame
        context.scene.frame_current = start_frame
        return { 'FINISHED' }

class keytools_PlaceCursorAndPivot(bpy.types.Operator):
    """Places 2D cursor at selection and sets pivot mode to 2D cursor"""
    bl_idname = "graph.place_cursor_and_pivot"
    bl_label = "Place Cursor and Pivot"

    def execute(self, context):
        bpy.ops.graph.frame_jump()
        context.space_data.pivot_point = 'CURSOR'
        # now deselect everything
        bpy.ops.graph.select_all_toggle()
        return { 'FINISHED' }

def keytools_dopesheet_extra_controls(self, context):
    if context.space_data.mode in ('DOPESHEET', 'ACTION'):
        layout = self.layout
        layout.operator("action.share_keys", text="Share Keys")

def register():
    bpy.utils.register_class(keytools_EaseKeys)
    bpy.utils.register_class(keytools_FlattenKeys)
    bpy.utils.register_class(keytools_FlattenExaggerateKeys)
    bpy.utils.register_class(keytools_PlaceCursorAndPivot)
    # buggy
    # bpy.utils.register_class(keytools_ShareKeys)
    # bpy.types.DOPESHEET_HT_header.append(keytools_dopesheet_extra_controls)

def unregister():
    # bpy.types.DOPESHEET_HT_header.remove(keytools_dopesheet_extra_controls)
    # buggy
    # bpy.utils.unregister_class(keytools_ShareKeys)
    bpy.utils.unregister_class(keytools_PlaceCursorAndPivot)
    bpy.utils.unregister_class(keytools_FlattenExaggerateKeys)
    bpy.utils.unregister_class(keytools_FlattenKeys)
    bpy.utils.unregister_class(keytools_EaseKeys)

if __name__ == "__main__":
    register()