using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ReadTransformation : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        Vector3 pos = this.transform.position;
        Quaternion quat = this.transform.rotation;

        print(quat);
        print(pos);

    }
}
