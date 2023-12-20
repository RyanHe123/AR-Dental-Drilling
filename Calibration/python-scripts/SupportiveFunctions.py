import numpy as np

def build_transformation(rotation, translation):
    transformation_matrix = np.eye(4)

    # Set the rotation part of the matrix
    transformation_matrix[:3, :3] = rotation

    # Set the translation part of the matrix
    transformation_matrix[:3, 3] = translation

    return transformation_matrix

def convert_to_meter(transformation):

    translation = transformation[:3, 3] / 1000
    transformation[:3, 3] = translation
    
    return  transformation

def parse_unity_transformation(rows):
    transformation_matrix = np.zeros((4, 4))

    for i, row in enumerate(rows):
        elements = row.split()
        for j, element in enumerate(elements):
            transformation_matrix[i, j] = float(element)

    return transformation_matrix

def compute_T_HM1(NM1, NM2, HM2):
    """
    compute the transformation matrix between Hololens and marker frames fixed on Hololens
    NM1: Marker fixed on Hololens read by NDI
    NM2: Marker fixed on Tooth read by NDI
    HM2: Marker fixed on Tooth read by Hololens 
    """
    # add a transformation between right-hand and left-hand coordinate systems
    intermediate = np.array([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, -1, 0], [0 ,0, 0, 1]])
    HM1 = np.linalg.inv(convert_to_meter(NM1)) @ convert_to_meter(NM2) @ intermediate @ np.linalg.inv(HM2) 
    #print("NDI to HoloCamera: ", convert_to_meter(NM2) @ intermediate @ np.linalg.inv(HM2))
    return HM1