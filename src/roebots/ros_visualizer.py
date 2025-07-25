# Copyright (c) 2025 Adrian Röfer, Robot Learning Lab, University of Freiburg
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import numpy as np

try:
    import rospy

    from geometry_msgs.msg import Pose        as PoseMsg, \
                                Point       as PointMsg, \
                                Vector3     as Vector3Msg, \
                                Quaternion  as QuaternionMsg, \
                                PoseStamped as PoseStampedMsg
    from std_msgs.msg           import ColorRGBA as ColorRGBAMsg
    from visualization_msgs.msg import Marker,\
                                    MarkerArray

    from .ros_serializer import ROS_SERIALIZER


    def del_marker(Id, namespace):
        out = Marker()
        out.ns = namespace
        out.header.stamp = rospy.Time.now()
        out.id = Id
        out.action = Marker.DELETE
        return out


    def blank_marker(Id, namespace, color, frame):
        out = Marker()
        out.ns = namespace
        out.header.stamp = rospy.Time(0) # .now()
        out.header.frame_id = frame
        out.pose.orientation.w = 1
        out.id = Id
        out.action = Marker.ADD
        out.color  = ROS_SERIALIZER.serialize(color, ColorRGBAMsg)
        out.frame_locked = True
        return out


    def color(r,g,b,a=1):
        out = ColorRGBAMsg()
        out.r = r
        out.g = g
        out.b = b
        out.a = a
        return out


    class ROSVisualizer(object):
        def __init__(self, vis_topic, world_frame='world'):
            self.ids     = {}
            self.lastIds = {}
            self.publisher = rospy.Publisher(vis_topic, MarkerArray, queue_size=1, tcp_nodelay=1, latch=True)
            self.world_frame = world_frame
            self.current_msg = {}

        def begin_draw_cycle(self, *layers):
            if len(layers) == 0:
                layers = self.ids.keys()

            for layer in layers:
                if layer not in self.ids:
                    self.ids[layer] = 0
                    #print('Added new layer {}'.format(layer))
                self.lastIds[layer] = self.ids[layer]
                self.ids[layer] = 0
                self.current_msg[layer] = MarkerArray()

        def consume_id(self, namespace):
            if not namespace in self.ids:
                self.ids[namespace] = 0
                self.lastIds[namespace] = 0
                self.current_msg[namespace] = MarkerArray()

            self.ids[namespace] += 1
            return self.ids[namespace] - 1


        def render(self, *layers):
            if len(layers) == 0:
                layers = self.ids.keys()

            out_msg = MarkerArray()
            for namespace in layers:
                Id = self.ids[namespace]
                out_msg.markers.extend(self.current_msg[namespace].markers)
                out_msg.markers.extend([del_marker(x, namespace) for x in range(Id, self.lastIds[namespace])])

            self.publisher.publish(out_msg)

        def __resframe(self, frame):
            if frame == None:
                return self.world_frame
            return frame

        def draw_sphere(self, namespace, position, radius, color=(1, 0, 0, 1), frame=None):
            marker = blank_marker(self.consume_id(namespace), namespace, color, self.__resframe(frame))
            marker.type = Marker.SPHERE
            marker.pose.position = ROS_SERIALIZER.serialize(position, PointMsg)
            marker.scale = ROS_SERIALIZER.serialize([radius * 2] * 3, Vector3Msg)
            self.current_msg[namespace].markers.append(marker)

        def draw_ellipsoid(self, namespace, pose, size, color=(1, 0, 0, 1), frame=None):
            marker = blank_marker(self.consume_id(namespace), namespace, color, self.__resframe(frame))
            marker.type  = Marker.SPHERE
            marker.pose  = ROS_SERIALIZER.serialize(pose, PoseMsg)
            marker.scale = ROS_SERIALIZER.serialize(size, Vector3Msg)
            self.current_msg[namespace].markers.append(marker)

        def draw_cube(self, namespace, pose, scale, color=(1, 0, 0, 1), frame=None):
            self.draw_shape(namespace, pose, scale, Marker.CUBE, color, frame)

        def draw_points(self, namespace, pose, size, points, color=(1, 0, 0, 1), frame=None, colors=None):
            marker = blank_marker(self.consume_id(namespace), namespace, color, self.__resframe(frame))
            marker.type = Marker.POINTS
            marker.pose = ROS_SERIALIZER.serialize(pose, PoseMsg)
            marker.points = [ROS_SERIALIZER.serialize(p, PointMsg) for p in points]
            marker.colors = [] if colors is None else [ROS_SERIALIZER.serialize(c, ColorRGBAMsg) for c in colors]
            marker.scale.x = size
            marker.scale.y = size
            marker.scale.z = size
            self.current_msg[namespace].markers.append(marker)

        def draw_strip(self, namespace, pose, size, points, color=(1, 0, 0, 1), frame=None, colors=None):
            marker = blank_marker(self.consume_id(namespace), namespace, color, self.__resframe(frame))
            marker.type = Marker.LINE_STRIP
            marker.pose = ROS_SERIALIZER.serialize(pose, PoseMsg)
            marker.points = [ROS_SERIALIZER.serialize(p, PointMsg) for p in points]
            marker.colors = [] if colors is None else [ROS_SERIALIZER.serialize(c, ColorRGBAMsg) for c in colors]
            marker.scale.x = size
            marker.scale.y = size
            marker.scale.z = size
            self.current_msg[namespace].markers.append(marker)

        def draw_lines(self, namespace, pose, size, points, color=(1, 0, 0, 1), frame=None, colors=None):
            marker = blank_marker(self.consume_id(namespace), namespace, color, self.__resframe(frame))
            marker.type = Marker.LINE_LIST
            marker.pose = ROS_SERIALIZER.serialize(pose, PoseMsg)
            marker.points = [ROS_SERIALIZER.serialize(p, PointMsg) for p in points]
            marker.colors = [] if colors is None else [ROS_SERIALIZER.serialize(c, ColorRGBAMsg) for c in colors]
            marker.scale.x = size
            marker.scale.y = size
            marker.scale.z = size
            self.current_msg[namespace].markers.append(marker)

        def draw_cube_batch(self, namespace, pose, size, positions, color=(1, 0, 0, 1), frame=None, colors=None):
            marker = blank_marker(self.consume_id(namespace), namespace, color, self.__resframe(frame))
            marker.type = Marker.CUBE_LIST
            marker.pose = ROS_SERIALIZER.serialize(pose, PoseMsg)
            marker.points = [ROS_SERIALIZER.serialize(p, PointMsg) for p in positions]
            marker.colors = [] if colors is None else [ROS_SERIALIZER.serialize(c, ColorRGBAMsg) for c in colors]
            marker.scale.x = size
            marker.scale.y = size
            marker.scale.z = size
            self.current_msg[namespace].markers.append(marker)

        def draw_poses(self, namespace, pose, size, line_width, poses, color=(1, 1, 1, 1), frame=None):
            positions = []
            for p in poses:
                pos = p[:, 3]
                positions += [pos, pos + p[:, 0] * size, pos, pos + p[:, 1] * size, pos, pos + p[:, 2] * size]
            colors = np.vstack([np.hstack([np.eye(4)[:3]] * 2)] * len(poses)).reshape((-1, 4))
            colors[:, 3] = 1
            self.draw_lines(namespace, pose, line_width, positions, (1, 1, 1, 1), frame, colors)


        def draw_cylinder(self, namespace, pose, length, radius, r=0, g=0, b=1, a=1, frame=None):
            self.draw_shape(namespace, pose, (radius * 2, radius * 2, length), Marker.CYLINDER, color, frame)

        def draw_arrow(self, namespace, start, end, color=(1, 1, 1, 1), width=0.01, frame=None):
            marker = blank_marker(self.consume_id(namespace), namespace, color, self.__resframe(frame))
            marker.type = Marker.ARROW
            marker.scale.x = width
            marker.scale.y = 2 * width
            marker.points.extend([ROS_SERIALIZER.serialize(start, PointMsg), 
                                ROS_SERIALIZER.serialize(end, PointMsg)])
            self.current_msg[namespace].markers.append(marker)

        def draw_vector(self, namespace, position, vector, color=(1, 1, 1, 1), width=0.01, frame=None):
            self.draw_arrow(namespace, position, position + vector, color, width, frame)

        def draw_text(self, namespace, position, text, color=(1, 1, 1, 1), height=0.08, frame=None):
            marker = blank_marker(self.consume_id(namespace), namespace, color, self.__resframe(frame))
            marker.type = Marker.TEXT_VIEW_FACING
            marker.pose.position = ROS_SERIALIZER.serialize(position, PointMsg)
            marker.scale.z = height
            marker.text = text
            self.current_msg[namespace].markers.append(marker)

        def draw_shape(self, namespace, pose, scale, shape, color=(1, 1, 1, 1), frame=None):
            marker = blank_marker(self.consume_id(namespace), namespace, color, self.__resframe(frame))
            marker.type = shape
            marker.pose = ROS_SERIALIZER.serialize(pose, PoseMsg)
            marker.scale = ROS_SERIALIZER.serialize(scale, Vector3Msg)
            self.current_msg[namespace].markers.append(marker)

        def draw_mesh(self, namespace, pose, scale, resource, frame=None, color=(1, 1, 1, 1), use_mat=True):
            marker = blank_marker(self.consume_id(namespace), namespace, color, self.__resframe(frame))
            marker.type = Marker.MESH_RESOURCE
            marker.pose = ROS_SERIALIZER.serialize(pose, PoseMsg)
            marker.scale = ROS_SERIALIZER.serialize(scale, Vector3Msg)
            marker.mesh_resource = resource
            marker.mesh_use_embedded_materials = use_mat
            self.current_msg[namespace].markers.append(marker)

except ImportError:
    class ROSVisualizer(object):
        def __init__(self, *args, **kwargs):
            raise ImportError("ROSVisualizer requires ROS to be installed and sourced. Please install ROS and source your workspace before using this class.")
        