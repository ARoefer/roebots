try:
    import rospy
    import numpy as np

    from geometry_msgs.msg import Pose        as PoseMsg, \
                                  Point       as PointMsg, \
                                  Vector3     as Vector3Msg, \
                                  Quaternion  as QuaternionMsg, \
                                  PoseStamped as PoseStampedMsg
    from std_msgs.msg import ColorRGBA as ColorRGBAMsg

    from .utils  import real_quat_from_matrix
    from .colors import ANALOGOUS

    class ROSSerializer(object):
        def __init__(self):
            self._serializers = {}
            self._type_serializers = {}
            self._deserializers = {}
            self._type_deserializers = {}

        def serialize(self, data, out_type=None):
            if out_type is None:
                try:
                    return self._serializers[type(data)](data)
                except KeyError as e:
                    raise Exception(f'No auto serializer for data of type {type(data)} found. Original Exception:\n{e}')
            
            if type(data) == out_type:
                return data

            try:
                ser = self._type_serializers[out_type]
                return ser[type(data)](data)
            except KeyError as e:
                raise Exception(f'Serializer for data of type {type(data)} to {out_type} found. Original Exception:\n{e}')
        
        def deserialize(self, data, out_type=None):
            if out_type is None:
                try:
                    return self._deserializers[type(data)](data)
                except KeyError as e:
                    raise Exception(f'No auto deserializer for data of type {type(data)} found. Original Exception:\n{e}')
            
            if type(data) == out_type:
                return data

            try:
                ser = self._type_deserializers[out_type]
                return ser[type(data)](data)
            except KeyError as e:
                raise Exception(f'Deserializer for data of type {type(data)} to {out_type} found. Original Exception:\n{e}')

        def add_serializer(self, f_ser, in_types, out_types):
            for t in in_types:
                self._serializers[t] = f_ser
            
            for to in out_types:
                if to not in self._type_serializers:
                    self._type_serializers[to] = {}
        
                for t in in_types:
                    self._type_serializers[to][t] = f_ser
        
        def add_deserializer(self, f_des, in_types, out_type):
            for t in in_types:
                self._deserializers[t] = f_des
            
            for to in out_types:
                if to not in self._type_deserializers:
                    self._type_deserializers[to] = {}
        
                for t in in_types:
                    self._type_deserializers[to][t] = f_des
    
            for t in in_types:
                self._type_deserializers[to][t] = f_des

    ROS_SERIALIZER = ROSSerializer()
except ModuleNotFoundError:
    rospy = None


if rospy is not None:
    def serialize_np_matrix_quat(mat):
        quat    = real_quat_from_matrix(mat[:3, :3])
        out     = QuaternionMsg(*quat)
        sq_norm = (np.asarray(quat) ** 2).sum()
        if np.abs(sq_norm - 1.0) > 1e-3:
            raise Exception('Non-normalized quaternion')
        return out

    def serialize_np_4x4_pose(mat):
        return PoseMsg(serialize_3_point(mat[:, 3]), 
                    serialize_np_matrix_quat(mat[:3, :3]))

    def serialize_np_mat_point_vec(mat):
        return serialize_np_4x1_matrix(mat.T[3] if mat.ndim == 2 else mat)

    def serialize_np_4x1_matrix(mat):
        mat = mat.flatten()
        if len(mat) < 4 or mat[3] != 0:
            return serialize_3_point(mat[:3])
        return serialize_3_vector(mat[:3])

    def serialize_4_quaternion(iterable):
        return QuaternionMsg(*iterable)

    def serialize_3_point(iterable):
        return PointMsg(iterable[0], iterable[1], iterable[2])

    def serialize_3_vector(iterable):
        return Vector3Msg(iterable[0], iterable[1], iterable[2])

    def serialize_color(iterable):
        return ColorRGBAMsg(iterable[0], iterable[1], iterable[2], iterable[3] if len(iterable) >= 4 else 1.0)

    def serialize_str_color(hex_str):
        return ColorRGBAMsg(*(np.asarray([int(s[-6:], base=16) for s in ANALOGOUS.flatten()]).astype('>u4').view(np.uint8) / 255))


    ROS_SERIALIZER.add_serializer(serialize_np_matrix_quat, {np.ndarray}, {QuaternionMsg})
    ROS_SERIALIZER.add_serializer(serialize_np_4x4_pose, {np.ndarray}, {PoseMsg})
    ROS_SERIALIZER.add_serializer(serialize_np_4x1_matrix, {np.ndarray}, {PointMsg, Vector3Msg})
    ROS_SERIALIZER.add_serializer(serialize_4_quaternion, {tuple, list}, {QuaternionMsg})
    ROS_SERIALIZER.add_serializer(serialize_3_point, {tuple, list}, {PointMsg})
    ROS_SERIALIZER.add_serializer(serialize_3_vector, {tuple, list}, {Vector3Msg})
    ROS_SERIALIZER.add_serializer(serialize_color, {tuple, list, np.ndarray}, {serialize_color})
else:
    ROS_SERIALIZER = None
