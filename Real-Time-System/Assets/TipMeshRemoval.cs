using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TipMeshRemoval : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void OnCollisionStay(Collision collision)
    {

        Debug.Log("Collision with" + collision.collider.name);
        Debug.Log("Collision num" + collision.contacts.Length);
        // 101323 Write New AddDepressionNew Algorithm

        foreach (var contact in collision.contacts)
        {
            Debug.DrawRay(contact.point, contact.normal, Color.red);
            //Debug.Log("Distance: " + Vector3.Distance(drilltip.transform.position, contact.point));
            Debug.Log("contact point" + contact.point);

        }

    }
}
