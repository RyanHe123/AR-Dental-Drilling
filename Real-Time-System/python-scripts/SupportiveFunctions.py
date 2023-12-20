import numpy as np
from scipy.spatial.transform import Rotation

def build_transformation(rotation, translation):
    transformation_matrix = np.eye(4)

    # Set the rotation part of the matrix
    transformation_matrix[:3, :3] = rotation

    # Set the translation part of the matrix
    transformation_matrix[:3, 3] = translation

    return transformation_matrix

def extract_rot_trans(matrix):
    rotation_matrix = matrix[:3, :3]

    # Extract translation vector (rightmost column)
    translation_vector = matrix[:3, 3]

    return rotation_matrix, translation_vector

def convert_to_meter(transformation):

    translation = transformation[:3, 3] / 1000
    transformation[:3, 3] = translation
    
    return  transformation

def compute_HC_TF(DrillNDI, ToothNDI, Result):
    intermediate = np.array([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, -1, 0], [0 ,0, 0, 1]])
    HCTF = np.linalg.inv(Result) @ np.linalg.inv(DrillNDI) @ ToothNDI @ intermediate
    
    return HCTF



def transformation2str(E):
    R, T = extract_rot_trans(E)
    Rot = Rotation.from_matrix(R)
    Q = Rot.as_quat()
    pose_msg = str(T[0]) + "," + str(T[1]) + "," + str(T[2])
    pose_msg += "," + str(Q[0]) + "," + str(Q[1]) + "," + str(Q[2]) + "," + str(Q[3])
    return pose_msg