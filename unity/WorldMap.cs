// GET https://farm-case-api.onrender.com/api/world-map
//
// image_url is a north-up Blue Marble picture, 2048 x 1024.
// If the WebGL build cannot load that host, load the API host plus proxy_path
// instead. Use proxy_path exactly; do not encode it a second time.
//
// x is pixels from the left. y is pixels from the top of the picture.
// Unity textures count y from the bottom, so flip a texture coordinate first:
// y = height - y.

using System;
using UnityEngine;

[Serializable]
public class WorldMapInfo
{
    public string image_url;
    public int width;
    public int height;
    public string proxy_path;

    public static WorldMapInfo FromJson(string json)
    {
        return JsonUtility.FromJson<WorldMapInfo>(json);
    }
}

public static class WorldMap
{
    public static void PixelToLatLon(float x, float y, int width, int height, out float lon, out float lat)
    {
        lon = x / width * 360f - 180f;
        lat = 90f - y / height * 180f;
    }
}
