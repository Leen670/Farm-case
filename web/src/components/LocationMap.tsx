import { useEffect } from "react";
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const SATELLITE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";

const pinIcon = L.divIcon({
  className: "farm-pin",
  html: "",
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

export type MapTarget = { lat: number; lon: number; key: number };

function ClickPick({ onPick }: { onPick: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(event) {
      onPick(event.latlng.lat, event.latlng.lng);
    },
  });
  return null;
}

function FlyTo({ target }: { target: MapTarget | null }) {
  const map = useMap();
  useEffect(() => {
    if (!target) return;
    map.flyTo([target.lat, target.lon], 10);
  }, [map, target]);
  return null;
}

export function LocationMap({
  lat,
  lon,
  flyTo,
  onPick,
}: {
  lat: number | null;
  lon: number | null;
  flyTo: MapTarget | null;
  onPick: (lat: number, lon: number) => void;
}) {
  const placed = lat != null && lon != null;
  const center: [number, number] = placed ? [lat, lon] : [20, 10];

  return (
    <MapContainer center={center} zoom={placed ? 6 : 2} className="location-map" scrollWheelZoom>
      <TileLayer
        attribution="Tiles &copy; Esri"
        url={SATELLITE}
        maxZoom={19}
      />
      <ClickPick onPick={onPick} />
      <FlyTo target={flyTo} />
      {placed && <Marker position={[lat, lon]} icon={pinIcon} />}
    </MapContainer>
  );
}
