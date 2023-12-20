from sksurgerynditracker.nditracker import NDITracker
import numpy as np
import socket
from scipy.spatial.transform import Rotation
from SupportiveFunctions import extract_rot_trans
from SupportiveFunctions import compute_HC_TF
from SupportiveFunctions import transformation2str
from SupportiveFunctions import convert_to_meter
import time

import keyboard




if __name__ == "__main__":

    HOST = '127.0.0.1'  
    PORT = 12345 
    romfile_path_tooth = "Tracker_files\Tooth_model.rom"
    romfile_path_hololens = "Tracker_files\Head_frame.rom"
    romfile_path_drill = "Tracker_files\Tracker_frame.rom"

    SETTING1 = {"tracker type": "polaris", "romfiles": [romfile_path_tooth, romfile_path_hololens]}
    SETTING2 = {"tracker type": "polaris", "romfiles": [romfile_path_tooth,  romfile_path_drill]}
    TRACKER1 = NDITracker(SETTING1)
    

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")

    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    TRACKER1.start_tracking()

    see = True
    Result = np.array([[ 0.22272608,  0.06870815,  0.97245695,  0.01185803],
                       [ 0.97294089, -0.07856854, -0.21728579,  0.10463461],
                       [-0.06147521, -0.9945382 ,  0.08434824,  0.02675   ],
                       [ 0.        ,  0.        ,  0.        ,  1.        ]])
    
    # use this flag to switch mode
    setup = False
    
    while(1):

        if keyboard.is_pressed('k'):
            setup = True
            TRACKER1.stop_tracking()
            TRACKER1.close()
            TRACKER2 = NDITracker(SETTING2)
            TRACKER2.start_tracking()
            print("The setup has been completed. You can start drilling now.")
        
        if not setup:
            port_handles, timestamps, framenumbers, tracking, quality = TRACKER1.get_frame()
        else:
            port_handles, timestamps, framenumbers, tracking, quality = TRACKER2.get_frame()
        num = 0
        ToothNDI = np.eye(4)
        HololensNDI = np.eye(4)
        DrillNDI = np.eye(4)
        ndi_frames = [False] * 2

        for t in tracking:
            num = num + 1
            if str(t[0][3]) != "nan" and str(t[1][3]) != "nan" and str(t[2][3]) != "nan":
                if num == 1:
                    ToothNDI = t
                if num == 2:
                    if not setup:
                        HololensNDI = t
                    else:
                        DrillNDI = t
                ndi_frames[num - 1]  = True

        if not setup:
            if ndi_frames[0] and ndi_frames[1]:
                HololensNDI = convert_to_meter(HololensNDI)
                ToothNDI = convert_to_meter(ToothNDI)
                HCTF = compute_HC_TF(HololensNDI, ToothNDI, Result)
                # add NDI-to-Tooth
                pose_msg = str(1) + "," + transformation2str(HCTF) + "," + transformation2str(ToothNDI)
                print(pose_msg)
                client_socket.send(pose_msg.encode())
        else:
            if ndi_frames[0] and ndi_frames[1]:
                ToothNDI = convert_to_meter(ToothNDI)
                DrillNDI = convert_to_meter(DrillNDI)
                pose_msg = str(2) + "," + transformation2str(DrillNDI) + "," + transformation2str(ToothNDI)
                print(pose_msg)
                client_socket.send(pose_msg.encode())


    TRACKER2.stop_tracking()
    TRACKER2.close()