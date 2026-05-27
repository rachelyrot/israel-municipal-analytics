import { useEffect, useRef } from 'react'
import L from 'leaflet'

// Viridis 5-stop palette (dark purple → bright yellow)
const VIRIDIS = ['#440154', '#3e4989', '#26828e', '#6ece58', '#fde725']

function quantileBreaks(values, n = 5) {
  const sorted = [...values].sort((a, b) => a - b)
  return Array.from({ length: n - 1 }, (_, i) =>
    sorted[Math.floor((sorted.length * (i + 1)) / n)]
  )
}

function pickColor(value, breaks) {
  if (value == null) return '#d1d5db'
  for (let i = 0; i < breaks.length; i++) {
    if (value <= breaks[i]) return VIRIDIS[i]
  }
  return VIRIDIS[VIRIDIS.length - 1]
}

function fmt(value, isPercentage = false) {
  if (value == null) return 'אין נתון'
  const n = Number(value)
  if (isPercentage)
    return n.toLocaleString('he-IL', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + '%'
  return n.toLocaleString('he-IL', { maximumFractionDigits: 0 })
}

export function ChoroplethMap({ geojson, isPercentage = false, unit = '', onMunicipalityClick, selectedMunicipalityId }) {
  const containerRef = useRef(null)
  const mapRef = useRef(null)
  const layerRef = useRef(null)

  // Init map once
  useEffect(() => {
    if (mapRef.current || !containerRef.current) return
    const israelBounds = L.latLngBounds([29.3, 33.8], [33.5, 36.0])
    mapRef.current = L.map(containerRef.current, {
      center: [31.5, 35.0],
      zoom: 8,
      minZoom: 7,
      maxBounds: israelBounds,
      maxBoundsViscosity: 1.0,
    })
    // CartoDB Positron — clean light-gray tiles matching reference site
    L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
      {
        attribution:
          '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors ' +
          '© <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19,
      }
    ).addTo(mapRef.current)
  }, [])

  // Redraw layer when data or selection changes
  useEffect(() => {
    if (!mapRef.current || !geojson) return
    if (layerRef.current) layerRef.current.remove()

    const values = geojson.features
      .map(f => f.properties?.value)
      .filter(v => v != null)

    const breaks = quantileBreaks(values)

    layerRef.current = L.geoJSON(geojson, {
      pointToLayer: (feature, latlng) => {
        const isSelected = feature.properties?.municipality_id === selectedMunicipalityId
        const color = pickColor(feature.properties?.value, breaks)
        return L.circleMarker(latlng, {
          radius: isSelected ? 6 : 3,
          fillColor: color,
          fillOpacity: 0.9,
          color: isSelected ? '#1e3a8a' : 'rgba(255,255,255,0.6)',
          weight: isSelected ? 2 : 0.8,
        })
      },
      onEachFeature: (feature, layer) => {
        const { municipality_name, value, national_avg } = feature.properties || {}
        const valStr = fmt(value, isPercentage)
        const avgStr = national_avg != null ? fmt(national_avg, isPercentage) : null
        const unitStr = !isPercentage && unit ? `<span style="color:#6b7280;font-size:11px"> ${unit}</span>` : ''
        layer.bindTooltip(
          `<div dir="rtl" style="text-align:right;font-size:11px;line-height:1.4">
            <strong style="font-size:12px">${municipality_name || ''}</strong><br/>
            ${valStr}${unitStr}
            ${avgStr ? `<br/><span style="color:#9ca3af;font-size:10px">ממוצע ארצי: ${avgStr}${unitStr}</span>` : ''}
          </div>`,
          { direction: 'top' }
        )
        if (onMunicipalityClick) {
          layer.on('click', () => onMunicipalityClick(feature.properties))
        }
      },
    }).addTo(mapRef.current)
  }, [geojson, isPercentage, onMunicipalityClick, selectedMunicipalityId])

  return <div ref={containerRef} style={{ height: '100%', width: '100%' }} />
}
