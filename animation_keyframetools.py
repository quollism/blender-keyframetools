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
    "name": "Keyframe Tools",
    "author": "quollism",
    "version": (0, 4, 1),
    "blender": (2, 79, 0),
    "description": "Some helpful tools for working with keyframes. Inspired by Alan Camilo's animBot toolset.",
    "warning": "Pre-release software. Only armature animation is supported so far. Working on it!",
    "category": "Animation"
    }

import bpy
from copy import deepcopy
from mathutils import Vector
from bpy.props import FloatVectorProperty

addon_keymaps = []

def get_selected_keys_and_extents():
    context = bpy.context
    pbones = []
    pbones.append(context.selected_pose_bones)
    curve_datas = []
    selected = []
    objects = []
    bones = []
    fcurves = []

    try:
        only_selected = context.space_data.dopesheet.show_only_selected
        show_hidden = context.space_data.dopesheet.show_hidden
    except:
        only_selected = True
        show_hidden = False

    def add_obj(obj):
        if show_hidden is False and obj.hide:
            return None
        if obj not in selected:
            selected.append(obj)

    def add_bone(b):
        if only_selected and not b.bone.select:
            return None
        add_obj(b.id_data)
        bones.append(b)

    for obj in context.scene.objects:
        if show_hidden is False and obj.hide:
            continue

        # Scan layers for object
        o = None
        for (index, l) in enumerate(context.scene.layers):
            if (l and obj.layers[index]):
                o = obj
                break
        if o is None:
            continue

        # Add object and bones
        if bool(only_selected and obj.select == False) is False:
            add_obj(obj)
        if obj.pose is not None:
            for (name, pbone) in obj.pose.bones.items():
                if any((only_selected is False, obj.select, pbone in pbones,)):
                    add_bone(pbone)


    # Add fcurves from objects
    for obj in selected:
        anim = obj.animation_data
        if anim and anim.action:
            fcurves.extend([(obj, fc) for fc in anim.action.fcurves])

    # Scan fcurves for keyframes
    for curve in fcurves:
        if curve.hide:
            continue
        first_co = None
        points = None
        last_co = None
        path = curve.data_path
        
        # Read path to get target's name
        if (path.startswith('pose.bones')):
            # btype =   'BONE'
            # bpath =   path.split('"]', 1)[1]      ## Transforms and custom prop
            # if (bpath.startswith('.')):       ## constraints?
                # bpath =   bpath.split('.', 1)[1]
            bname   =   (path.split('["', 1)[1].split('"]', 1)[0])
            bone    =   obj.pose.bones.get(bname)
        elif (path.startswith('bones')):    #data.bones
            # btype =   'BONE'
            # bpath =   path.split('"].', 1)[1]
            bname   =   (path.split('["', 1)[1].split('"]', 1)[0])
            bone    =   obj.bones.get(bname)
        else:
            # btype =   'OBJECT'
            # bpath =   path
            bname   =   obj.name
            bone    =   obj
        
        if (bone is None and curve.is_valid is True) or (bone is not None and bone != obj and bone not in bones):
            # Bone not selected
            continue

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

class GRAPH_OT_flatten_keyframes(bpy.types.Operator):
    """Converges keys and handles to a linear fit between the first and last keyframe of the selection"""
    bl_idname = "graph.flatten_keyframes"
    bl_label = "Flatten Keyframes"
    bl_options = {'REGISTER', 'UNDO'}
    add_to_menu = True

    def execute(self, context):
        curve_datas = get_selected_keys_and_extents()
        for curve_data in curve_datas:
            slopeMaker = keyframe_calculator(curve_data[1], curve_data[2])
            for i, keyframe in enumerate(curve_data[0]):
                keyframe.co[1] = slopeMaker.linear_fit(keyframe.co[0])
                keyframe.handle_left[1] = slopeMaker.linear_fit(keyframe.handle_left[0])
                keyframe.handle_right[1] = slopeMaker.linear_fit(keyframe.handle_right[0])
        return { 'FINISHED' }

class keyframe_calculator():
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

class GRAPH_OT_ease_keyframes(bpy.types.Operator):
    """Puts keys and handles along an eased curve between the first and last keyframe of the selection"""
    bl_idname = "graph.ease_keyframes"
    bl_label = "Ease Keyframes"
    bl_options = {'REGISTER', 'UNDO'}
    add_to_menu = True

    offset = FloatVectorProperty( name="Offset", size=3 )

    def execute(self, context):
        factor = self.offset[0]
        for curve_data in self._curve_datas:
            slopeMaker = keyframe_calculator(curve_data[1], curve_data[2])
            for i, keyframe in enumerate(curve_data[0]):
                keyframe.co[1] = slopeMaker.ease(keyframe.co[0], factor, curve_data[3][i]['co'][1])
                keyframe.handle_left[0] = keyframe.co[0] - 2
                keyframe.handle_left_type = 'FREE'
                keyframe.handle_left[1] = slopeMaker.ease(keyframe.handle_left[0], factor, curve_data[3][i]['handle_left'][1])
                keyframe.handle_right[0] = keyframe.co[0] + 2
                keyframe.handle_right_type = 'FREE'
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
        print(context)
        if context.space_data.type == 'GRAPH_EDITOR':
            self._initial_mouse = Vector((event.mouse_x, event.mouse_y, 0.0)) 
            self._curve_datas = get_selected_keys_and_extents()
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be graph editor")
            return {'CANCELLED'}

class GRAPH_OT_flatten_exaggerate_keyframes(bpy.types.Operator):
    """Scales keys and handles to/from a linear fit between the first and last keyframe of the selection"""
    bl_idname = "graph.flatten_exaggerate_keyframes"
    bl_label = "Flatten/Exaggerate Keyframes"
    bl_options = {'REGISTER', 'UNDO'}
    add_to_menu = True

    offset = FloatVectorProperty( name="Offset", size=3 )

    def execute(self, context):
        for curve_data in self._curve_datas:
            slopeMaker = keyframe_calculator(curve_data[1], curve_data[2])
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
            self._curve_datas = get_selected_keys_and_extents()
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "Active space must be graph editor")
            return {'CANCELLED'}

# BUGGY
class keyframetools_ShareKeys(bpy.types.Operator):
    """Shares keys between visisble animation channels in dope sheet"""
    bl_idname = "action.share_keyframes"
    bl_label = "Share Keyframes"
    bl_options = {'REGISTER', 'UNDO'}
    add_to_menu = True

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

class GRAPH_OT_place_cursor_and_pivot(bpy.types.Operator):
    """Places 2D cursor at selection and sets pivot mode to 2D cursor"""
    bl_idname = "graph.place_cursor_and_pivot"
    bl_label = "Place Cursor and Pivot"
    bl_options = {'REGISTER', 'UNDO_GROUPED'}
    # bl_undo_group = ""
    add_to_menu = True

    def execute(self, context):
        bpy.ops.graph.frame_jump()
        context.space_data.pivot_point = 'CURSOR'
        # now deselect everything
        bpy.ops.graph.select_all_toggle()
        return { 'FINISHED' }

def keyframetools_dopesheet_extra_controls(self, context):
    if context.space_data.mode in ('DOPESHEET', 'ACTION'):
        layout = self.layout
        layout.operator("action.share_keys", text="Share Keys")

# class GRAPH_MT_keyframetools_menu(bpy.types.Menu):
#     bl_label = "Keyframe Tools"
#     # just graph editor for now
#     bl_idname = "GRAPH_MT_keyframetools_menu"
#     add_to_menu = False

#     def draw(self, context):
#         if context.space_data.type == 'GRAPH_EDITOR':
#             layout = self.layout
#             for c in classes:
#                 if c.add_to_menu:
#                     layout.operator(c.bl_idname)
#         # else nothing

class GRAPH_PIE_keyframetools_piemenu(bpy.types.Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Keyframe Tools"
    bl_idname = "GRAPH_PIE_keyframetools_piemenu"
    add_to_menu = False

    def draw(self, context):
        if context.space_data.type == 'GRAPH_EDITOR':
            layout = self.layout
            pie = layout.menu_pie()
            pie.operator("graph.place_cursor_and_pivot", icon='CURSOR', text="Set Cursor and Pivot")
            pie.operator("graph.flatten_keyframes", icon='MAN_SCALE', text="Flatten Keys")
            pie.operator("graph.flatten_exaggerate_keyframes", icon='MAN_SCALE', text="Flatten/Exaggerate Keys")
            pie.operator("graph.ease_keyframes", icon='MAN_SCALE', text="Ease Keys")

classes = (
    # below operator is buggy mcbugbugs
    # keyframetools_ShareKeys,
    GRAPH_OT_flatten_keyframes,
    GRAPH_OT_flatten_exaggerate_keyframes,
    GRAPH_OT_ease_keyframes,
    GRAPH_OT_place_cursor_and_pivot,
    # GRAPH_MT_keyframetools_menu,
    GRAPH_PIE_keyframetools_piemenu
    )

def register():
    for c in classes:
        bpy.utils.register_class(c)
    # bpy.types.DOPESHEET_HT_header.append(keyframetools_dopesheet_extra_controls)
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Graph Editor', space_type='GRAPH_EDITOR')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'Z', 'PRESS', shift=True)
    kmi.properties.name = 'GRAPH_PIE_keyframetools_piemenu'
    addon_keymaps.append((km, kmi))

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    # bpy.types.DOPESHEET_HT_header.remove(keyframetools_dopesheet_extra_controls)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
        addon_keymaps.clear()

if __name__ == "__main__":
    register()
