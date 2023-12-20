using System;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using IRToolTrack;

public class DataStreaming : MonoBehaviour
{
    private TcpClient client;
    private NetworkStream stream;
    private byte[] buffer = new byte[1024];
    private IRToolController irtoolcontroller;

    // Correct the ip before building
    // TODO mayebe we can design a UI to input the ip address
    public String ip_address = "10.203.196.160";

    // Add main camera into the script
    public GameObject main_camera;
    
    //GameObject TipObject = GameObject.Find("Pivot Tip");
    private void Start()
    {
        irtoolcontroller = GetComponent<IRToolController>();
        try
        {
            client = new TcpClient(ip_address, 12345);
            stream = client.GetStream();
        }
        catch (Exception e)
        {
            Debug.LogError("server connection error: " + e.Message);
        }
    }

    private void Update()
    {
        //DateTime currentTime = DateTime.Now;
        //int hour = currentTime.Hour;
        //int minute = currentTime.Minute;
        //int second = currentTime.Second;
        Quaternion R = this.transform.rotation;
        Vector3 T = this.transform.position;

        Matrix4x4 marker = Matrix4x4.TRS(T, R, Vector3.one);
        Quaternion R_camera = main_camera.transform.rotation;
        Vector3 T_camera = main_camera.transform.position;
        Matrix4x4 camera = Matrix4x4.TRS(T_camera, R_camera, Vector3.one);

        Matrix4x4 ECM = camera.inverse * marker;
        //Vector3 T_CM = ECM.GetPosition();
        //Quaternion R_CM = ECM.rotation;

        if (stream.CanWrite)
        {
            string clientMessage;
         
            // clientMessage = R.ToString() + "#" + T.ToString();
            // clientMessage = R_CM.ToString() + "#" + T_CM.ToString();
            clientMessage = ECM.ToString("F10");
       
            byte[] clientMessageAsByteArray = Encoding.ASCII.GetBytes(clientMessage);
            // Write byte array to socketConnection stream.                 
            stream.Write(clientMessageAsByteArray, 0, clientMessageAsByteArray.Length);
            Debug.Log("Client sent his message - should be received by server");
        }

    }
    private void OnDestroy()
    {
        stream.Close();
        client.Close();
    }
}