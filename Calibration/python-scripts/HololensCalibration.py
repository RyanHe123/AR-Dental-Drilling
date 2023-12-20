import time
import socket
import numpy as np
from sksurgerynditracker.nditracker import NDITracker
from scipy.spatial.transform import Rotation
from SupportiveFunctions import *
import keyboard
import csv
from TransformationAverage import *
if __name__ == "__main__":
    #Initialize NDI
    romfile_path_drill = "Tracker_files\Head_frame.rom"
    romfile_path_tooth = "Tracker_files\Tooth_model.rom"
    SETTINGS = {"tracker type": "polaris", "romfiles": [romfile_path_drill, romfile_path_tooth]}
    TRACKER = NDITracker(SETTINGS)

    #Initialize Socket Server
    HOST = '10.203.196.160'  
    PORT = 12345 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    TRACKER.start_tracking()
    isRecording = False

    csv_file_path = time.strftime("%m%d%H%M") + "-calibration.csv"
    file = open(csv_file_path, "a", newline='')
    csv_writer = csv.writer(file)
    first_R = np.zeros((3, 3))
    isFirstTime = True
    with client_socket:
        while(1):
            if keyboard.is_pressed('s'):
                isRecording = True
                print("Recording")

            if keyboard.is_pressed('q'):
                file.close()
                restored_data = np.loadtxt(csv_file_path, delimiter=',')
                num = restored_data.shape[0]
                translations = restored_data[:, 4:7]
                rotations = restored_data[:, 0:4]
                log_qs = np.zeros((num, 4))
                new_translations = np.zeros((num, 3))
                s = num
                index = 0
                for i in range(num):
                    if rotations[i, 0] < 0:
                        s -= 1
                        continue
                    log_qs[index] = quaternion_logarithm(rotations[i])
                    new_translations[index] = translations[i]
                    index += 1
                print("s: ", s)
                print(new_translations.shape)
                print(new_translations)
                log_qs = log_qs[0:s, :]
                ave_log_q = np.mean(log_qs, axis=0)
                ave_q = quaternion_exponential(ave_log_q)
                print("rotation: ", ave_q)

                # turn quaternion into rotation matrix
                rotaion = Rotation.from_quat(ave_q)
                R = rotaion.as_matrix()
                transformation = np.zeros((4, 4))
                transformation[0:3, 0:3] = first_R
                new_translations = new_translations[0:s, :]
                ave_translation = np.mean(new_translations, axis=0)
                transformation[0:3, 3] = ave_translation
                transformation[3, 3] = 1
                print(transformation)

                # turn transformation into string
                print(np.array2string(transformation, separator=", "))
                break
            see1 = True
            see2 = True
            data = client_socket.recv(1024)
            DrillNDI = np.eye(4)
            ToothNDI = np.eye(4)
            ToothHolo = np.eye(4)
            if not data:
                break
            else:
                datastr = str(data, encoding='utf-8')
                rows = datastr.strip().split('\n')
                if len(rows) == 4:  
                    ToothHolo = parse_unity_transformation(rows)
                else:
                    continue
            
            #print("Star: ", ToothHolo)    
            port_handles, timestamps, framenumbers, tracking, quality = TRACKER.get_frame()
            num = 0
        
            for ti in tracking:
                num = num + 1
                if str(ti[0][3]) != "nan" and str(ti[1][3]) != "nan" and str(ti[2][3]) != "nan":
                    see2 = True
                    if num == 1:
                        DrillNDI = ti
                    if num == 2:
                        ToothNDI = ti
                    #print("NDI: ", ToothNDI)
                else:
                    see2 = False  
                    break

            #print("NDI: ", see2)    
            if see1 == True and see2 == True:
                result = compute_T_HM1(DrillNDI, ToothNDI, ToothHolo)
                print("Calibration: ", result)
                if isRecording:
                    if isFirstTime:
                        isFirstTime = False
                        first_R = result[0:3, 0:3]
                    R = result[0:3, 0:3]
                    rotaion = Rotation.from_matrix(R)
                    q = rotaion.as_quat()
                    print("quaternion", q)
                    # combine R and q in one numpy array
                    data_to_save = np.concatenate((q, result[0:3, 3]), axis=None)
                    data_to_save = data_to_save.reshape(1, 7)
                    print("shape: ", data_to_save.shape)
                    np.savetxt(file, data_to_save, delimiter=',')
            else:
                continue

    TRACKER.stop_tracking()
    TRACKER.close()