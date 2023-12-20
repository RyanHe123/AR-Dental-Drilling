import numpy as np
from scipy.spatial.transform import Rotation 


csv_file_path = "12171058-calibration.csv"


from scipy.spatial.distance import cdist

def quaternion_logarithm(q):
    """Computes the logarithm of a quaternion.

    Args:
        q: A quaternion represented as a 4-dimensional NumPy array.

    Returns:
        The logarithm of the quaternion, also represented as a 4-dimensional NumPy array.
    """

    # Check if the input quaternion is a unit quaternion 
    if not np.allclose(np.dot(q, q), 1, atol=1e-4):
        raise ValueError("Input quaternion must be finite.")

    #TODO check if it is scalar-last representation
    cth = q[3]
    th = np.arccos(cth)
    log_q = np.zeros(4)
    log_q[0:3] = q[0:3] / np.sin(th) * th

    # Return the logarithm of the quaternion.
    return log_q

def quaternion_exponential(q):
    th = np.linalg.norm(q[0:3])
    exp_q = np.zeros(4)
    exp_q[3] = np.cos(th)
    exp_q[0:3] = q[0:3] / th * np.sin(th)

    return exp_q


if __name__ == "__main__":
    # csv loadtxt
    restored_data = np.loadtxt(csv_file_path, delimiter=',')
    num = restored_data.shape[0]
    translations = restored_data[:, 4:7]
    ave_translation = np.mean(translations, axis=0)
    print("translation: ", ave_translation)

    rotations = restored_data[:, 0:4]
    log_qs = np.zeros((num, 4))
    for i in range(num):
        log_qs[i] = quaternion_logarithm(rotations[i])

    ave_log_q = np.mean(log_qs, axis=0)
    ave_q = quaternion_exponential(ave_log_q)
    print("rotation: ", ave_q)

    # turn quaternion into rotation matrix
    rotaion = Rotation.from_quat(ave_q)
    R = rotaion.as_matrix()
    transformation = np.zeros((4, 4))
    transformation[0:3, 0:3] = R
    transformation[0:3, 3] = ave_translation
    transformation[3, 3] = 1
    print(transformation)

    # turn transformation into string
    print(np.array2string(transformation, separator=", "))





