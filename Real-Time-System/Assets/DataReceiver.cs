using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Text;
using Unity.VisualScripting;
using UnityEngine;

public class DataReceiver : MonoBehaviour
{
    private TcpClient client;
    private NetworkStream stream;
    private byte[] buffer = new byte[1024];
    private bool mode = true;
    public Camera Holocamera;
    public GameObject DrillObject;
    private Matrix4x4 unity2ndi;
    private Matrix4x4 handConvert = new Matrix4x4(
        new Vector4(0f, 1f, 0f, 0f), 
	    new Vector4(-1f, 0f, 0f, 0f), 
	    new Vector4(0f, 0f, -1f, 0f), 
	    new Vector4(0f, 0f, 0f, 1f)
    );

    // Start is called before the first frame update

    Vector3 offset_pos = new Vector3(-0.0164f, -0.0022f, 0.003f);
    Quaternion offset_rot = new Quaternion(-0.00113f, -0.98901f, 0.06319f, 0.13367f);



    void Start()
    {
        try
        {
            client = new TcpClient("127.0.0.1", 12345);
            stream = client.GetStream();
        }
        catch (Exception e)
        {
            Debug.LogError("server connection error: " + e.Message);
        }

    }

    // Update is called once per frame
    void Update()
    {
        int bytesRead = stream.Read(buffer, 0, buffer.Length);
        string receivedData = Encoding.UTF8.GetString(buffer, 0, bytesRead);
        // print(receivedData);
        string[] words = receivedData.Split(',');
        Matrix4x4 offset_transformation = Matrix4x4.TRS(offset_pos, offset_rot, Vector3.one);


        if (mode)
        {
            if (words.Length == 15)
            {
                float state = float.Parse(words[0]);
 
                if (state == 1)
                {
                    //Debug.Log("Received Translation: " + "x: " + words[0] + " y: " + words[1] + " z: " + words[2]);
                    float tx = float.Parse(words[1]);
                    float ty = float.Parse(words[2]);
                    float tz = float.Parse(words[3]);

                    float qx = float.Parse(words[4]);
                    float qy = float.Parse(words[5]);
                    float qz = float.Parse(words[6]);
                    float qw = float.Parse(words[7]);

                    Vector3 TFHC_pos = new Vector3(tx, ty, tz);
                    Quaternion TFHC_rot = new Quaternion(qx, qy, qz, qw);
                    Matrix4x4 TFHC = Matrix4x4.TRS(TFHC_pos, TFHC_rot.normalized, Vector3.one);

                    Vector3 HC_pos = Holocamera.transform.position;
                    Quaternion HC_rot = Holocamera.transform.rotation;

                    
                    Matrix4x4 HC = Matrix4x4.TRS(HC_pos, HC_rot, Vector3.one);

                    Matrix4x4 result = HC * TFHC * offset_transformation;

                    this.transform.rotation = result.rotation;
                    this.transform.position = result.GetPosition();
                }
                else
                {
                    mode = false;

                    
                    // Unity to NDI
                }
                float tx2 = float.Parse(words[8]);
                float ty2 = float.Parse(words[9]);
                float tz2 = float.Parse(words[10]);

                float qx2 = float.Parse(words[11]);
                float qy2 = float.Parse(words[12]);
                float qz2 = float.Parse(words[13]);
                float qw2 = float.Parse(words[14]);

                Vector3 ndi2tooth_pos = new Vector3(tx2, ty2, tz2);
                Quaternion ndi2tooth_rot = new Quaternion(qx2, qy2, qz2, qw2);
                Matrix4x4 ndi2tooth = Matrix4x4.TRS(ndi2tooth_pos, ndi2tooth_rot.normalized, Vector3.one);

                Matrix4x4 virtualTooth = Matrix4x4.TRS(this.transform.position, this.transform.rotation, Vector3.one);
                unity2ndi = virtualTooth * Matrix4x4.Inverse(offset_transformation) * Matrix4x4.Inverse(handConvert) * Matrix4x4.Inverse(ndi2tooth);
                //Debug.Log("inverse" + Matrix4x4.Inverse(handConvert));
                //print(unity2ndi.rotation);
                
            }
            else
            {
                Debug.Log("Invalid Data!");
            }

        }
        else
        {
            if (words.Length == 15)
            {
                float tx = float.Parse(words[8]);
                float ty = float.Parse(words[9]);
                float tz = float.Parse(words[10]);

                float qx = float.Parse(words[11]);
                float qy = float.Parse(words[12]);
                float qz = float.Parse(words[13]);
                float qw = float.Parse(words[14]);

                Vector3 ndi2tooth_pos = new Vector3(tx, ty, tz);
                Quaternion ndi2tooth_rot = new Quaternion(qx, qy, qz, qw);
                Matrix4x4 ndi2tooth = Matrix4x4.TRS(ndi2tooth_pos, ndi2tooth_rot.normalized, Vector3.one);

                tx = float.Parse(words[1]);
                ty = float.Parse(words[2]);
                tz = float.Parse(words[3]);

                qx = float.Parse(words[4]);
                qy = float.Parse(words[5]);
                qz = float.Parse(words[6]);
                qw = float.Parse(words[7]);

                Vector3 ndi2drill_pos = new Vector3(tx, ty, tz);
                Quaternion ndi2drill_rot = new Quaternion(qx, qy, qz, qw);
                Matrix4x4 ndi2drill = Matrix4x4.TRS(ndi2drill_pos, ndi2drill_rot.normalized, Vector3.one);

                Matrix4x4 tooth = unity2ndi * ndi2tooth * handConvert * offset_transformation;
                Matrix4x4 drill = unity2ndi * ndi2drill * handConvert;

                this.transform.rotation = tooth.rotation;
                this.transform.position = tooth.GetPosition();

                DrillObject.transform.rotation = drill.rotation;
                DrillObject.transform.position = drill.GetPosition();

            }
            else
            {
                Debug.Log("Invalid Data!");
            }

        }
    }
}
