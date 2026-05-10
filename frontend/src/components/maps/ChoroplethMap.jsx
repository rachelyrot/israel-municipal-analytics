import { useEffect, useRef } from 'react'
import L from 'leaflet'

const COLORS = ['#eff3ff', '#bdd7e7', '#6baed6', '#2171b5', '#084594']

function quantileBreaks(values, n = 5) {
  const sorted = [...values].sort((a, b) => a - b)
  return Array.from({ length: n - 1 }, (_, i) =>
    sorted[Math.floor((sorted.length * (i + 1)) / n)]
  )
}

function pickColor(value, breaks) {
  if (value == null) return '#d1d5db'
  for (let i = 0; i < breaks.length; i++) {
    if (value <= breaks[i]) return COLORS[i]
  }
  return COLORS[COLORS.length - 1]
}

export function ChoroplethMap({ geojson, onMunicipalityClick }) {
  const containerRef = useRef(null)
  const mapRef = useRef(null)
  const layerRef = useRef(null)

  // Init map once
  useEffect(() => {
    if (mapRef.current || !containerRef.current) return
    const israelBounds = L.latLngBounds(
      [29.3, 33.8],   // דרום-מערב
      [33.5, 36.0],   // צפון-מזרח
    )
    mapRef.current = L.map(containerRef.current, {
      center: [31.5, 35.0],
      zoom: 8,
      minZoom: 7,
      maxBounds: israelBounds,
      maxBoundsViscosity: 1.0,
    })
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a>',
      maxZoom: 14,
    }).addTo(mapRef.current)
  }, [])

  // Redraw layer when geojson changes
  useEffect(() => {
    if (!mapRef.current || !geojson) return
    if (layerRef.current) layerRef.current.remove()

    const values = geojson.features
      .map(f => f.properties?.value)
      .filter(v => v != null)

    const breaks = quantileBreaks(values)

    layerRef.current = L.geoJSON(geojson, {
      pointToLayer: (feature, latlng) => {
        const color = pickColor(feature.properties?.value, breaks)
        return L.circleMarker(latlng, {
          radius: 8,
          fillColor: color,
          fillOpacity: 0.85,
          color: '#fff',
          weight: 1.2,
        })
      },
      onEachFeature: (feature, layer) => {
        const { municipality_name, value, national_avg } = feature.properties || {}
        const valStr = value != null ? Number(value).toLocaleString('he-IL') : 'אין נתון'
        const avgStr = national_avg != null ? Number(national_avg).toLocaleString('he-IL') : '—'
        layer.bindTooltip(
          `<div dir="rtl" style="text-align:right">
            <strong>${municipality_name || ''}</strong><br/>
            ערך: ${valStr}<br/>
            ממוצע ארצי: ${avgStr}
          </div>`,
          { direction: 'top' }
        )
        if (onMunicipalityClick) {
          layer.on('click', () => onMunicipalityClick(feature.properties))
        }
      },
    }).addTo(mapRef.current)
  }, [geojson, onMunicipalityClick])

  return <div ref={containerRef} style={{ height: '100%', width: '100%' }} />
}
