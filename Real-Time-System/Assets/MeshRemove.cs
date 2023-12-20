using HapticGUI;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
// DEBUG 10132023 For removing ambiguity, remove using System.Numerics;
// using System.Numerics;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.UIElements;

[RequireComponent(typeof(MeshFilter))]
public class MeshRemove : MonoBehaviour
{
    //public Color vertexColor;
    public float maximumDepression;
    public GameObject square;
    public Material color_change;
    public Material color_stable;
    private MeshFilter meshFilter;
    public GameObject drilltip;
    private List<UnityEngine.Vector3> originalVertices;
    private List<UnityEngine.Vector3> updatedVertices;

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {

    }

    private int CloestPoint(Vector3 depressionPoint)
    {
        meshFilter = GetComponent<MeshFilter>();

        originalVertices = meshFilter.sharedMesh.vertices.ToList();
        var dp = new Vector4(depressionPoint.x, depressionPoint.y, depressionPoint.z, 1);
        var localPos4 = this.transform.worldToLocalMatrix * dp;
        var localPos = new Vector3(localPos4.x, localPos4.y, localPos4.z);
        int index = 0;
        float minivalue = 1000.0f;
        for (int i = 0; i < originalVertices.Count; i++)
        {
            var distance = (localPos - originalVertices[i]).magnitude;
            if (distance <= minivalue)
            {
                index = i;
                minivalue = distance;
            }
        }
        return index;
    }

    private void OnCollisionStay(Collision collision)
    {
        meshFilter = GetComponent<MeshFilter>();
        //ContactPoint ct = collision.contacts[0];
        Renderer renderer = square.GetComponent<Renderer>();
        // renderer.material = color_change;
        // DEBUG
        //Debug.Log("Collision with" + collision.collider.name);
        //Debug.Log("Collision num" + collision.contacts.Length);
        // 101323 Write New AddDepressionNew Algorithm
        originalVertices = meshFilter.sharedMesh.vertices.ToList();
        updatedVertices = meshFilter.sharedMesh.vertices.ToList();

        foreach (var contact in collision.contacts)
        {
            int index = CloestPoint(contact.point);
           

            Vector4 minVer = new Vector4(originalVertices[index].x, originalVertices[index].y, originalVertices[index].z, 1);
            Vector4 worldPos = this.transform.localToWorldMatrix * minVer;
            Vector3 minVerWorld = new Vector3(worldPos.x, worldPos.y, worldPos.z);
            //Debug.Log("Distance: " + Vector3.Distance(drilltip.transform.position, contact.point));
            //Debug.Log("contact point" + contact.point);
            //Debug.Log("tip location" + drilltip.transform.position);
            float dis = (minVerWorld - contact.point).magnitude;
            Debug.Log("dis" + dis);
            if (dis < 0.0005f)
            {
                Debug.DrawRay(contact.point, contact.normal, Color.red);
                //AddDepression(contact.point, contact.normal);
                for (int i = (index - 3); i < (index + 3); i++)
                {
                    Vector3 normal = contact.normal;
                    //var newVert = originalVertices[index] + this.transform.worldToLocalMatrix.rotation * UnityEngine.Vector3.down * 10 * maximumDepression;
                    if (normal[1] > 0)
                    {
                        normal = -normal;
                    }
                    var newVert = originalVertices[i] + this.transform.worldToLocalMatrix.rotation * normal * 5 * maximumDepression;
                    updatedVertices.RemoveAt(i);
                    updatedVertices.Insert(i, newVert);
                }

                renderer.material = color_change;
            }
            else
            {
                renderer.material = color_stable;
            }
            //print("drilling");

        }
        meshFilter.mesh.SetVertices(updatedVertices);
        meshFilter.mesh.RecalculateNormals();
        meshFilter.mesh.RecalculateBounds();





        if (GetComponent<MeshRenderer>() == null)
        {
            gameObject.AddComponent<MeshRenderer>();
        }
        GetComponent<MeshCollider>().sharedMesh = GetComponent<MeshFilter>().mesh;
        
    }

    private void OnCollisionExit(Collision collision)
    {
        Renderer renderer = square.GetComponent<Renderer>();
        renderer.material = color_stable;
    }
}
