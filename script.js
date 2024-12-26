const map = L.map('map', {
    center: [20, 0],
    zoom: 2,
    zoomControl: false,
    zoomDelta: .25,
    zoomSnap: .25
  });

  const activateBtn = document.querySelector('.activate-btn');
  let isEnabled = true;

  enableMap();
  activateBtn.innerHTML = 'Deactivate Map';

  L.control.zoom({ position: 'topright' }).addTo(map);

  new L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: `attribution: &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attribution">CARTO</a>`,
    detectRetina: true
  }).addTo(map);

  const searchControl = L.control({ position: 'bottomleft' });

  searchControl.onAdd = function(map) {
    const div = L.DomUtil.create('div', 'search-container');
    div.innerHTML = `
      <h3>Input Geometry Name</h3>
      <input type="text" id="geometry-search" placeholder="Enter geometry name..." class="search-input">
      <div class="search-credits">
        Made by <a href="https://github.com/Milesd04" target="_blank">Victor Gabriel Dominguez</a> using the
        <a href="https://wbkd.github.io/leaflet-truesize/" target="_blank">Leaflet TrueSize Plugin</a>
      </div>
    `;

    L.DomEvent.disableClickPropagation(div);
    return div;
  };

  searchControl.addTo(map);

  async function loadGeometry(geometryName) {
    console.log('Attempting to load geometry:', geometryName);
    try {
      const response = await fetch(`data/${geometryName}.geojson`);
      console.log('Fetch response:', response);
      if (!response.ok) throw new Error('Geometry not found');

      const geojsonData = await response.json();
      console.log('Loaded GeoJSON data:', geojsonData);
      return geojsonData;
    } catch (error) {
      console.error('Error loading geometry:', error);
      return null;
    }
  }

  document.getElementById('geometry-search').addEventListener('keypress', async function(e) {
    if (e.key === 'Enter') {
      const geometryName = this.value.trim();
      if (!geometryName) return;

      const geojsonData = await loadGeometry(geometryName);
      if (geojsonData) {
        try {
          const geometry = new L.trueSize(geojsonData).addTo(map);

          const removeBtn = document.createElement('button');
          removeBtn.innerHTML = 'Remove Geometry';
          removeBtn.className = 'remove-btn';

          document.body.appendChild(removeBtn);

          removeBtn.addEventListener('click', () => {
            map.removeLayer(geometry);
            document.body.removeChild(removeBtn);
          });

          this.value = '';
        } catch (error) {
          console.error('Error creating or removing layer:', error);
        }
      }
    }
  });

  activateBtn.addEventListener('click', () => {
    if (isEnabled) {
      activateBtn.innerHTML = 'Activate Map';
      disableMap();
    } else {
      activateBtn.innerHTML = 'Deactivate Map';
      enableMap();
    }
    isEnabled = !isEnabled;
  });

  function disableMap() {
    map.dragging.disable();
    map.touchZoom.disable();
    map.doubleClickZoom.disable();
    map.scrollWheelZoom.disable();
    map.boxZoom.disable();
    map.keyboard.disable();
    if (map.tap) map.tap.disable();
    document.getElementById('map').style.cursor = 'default';
  }

  function enableMap() {
    map.dragging.enable();
    map.touchZoom.enable();
    map.doubleClickZoom.enable();
    map.scrollWheelZoom.enable();
    map.boxZoom.enable();
    map.keyboard.enable();
    if (map.tap) map.tap.enable();
    document.getElementById('map').style.cursor = 'grab';
  }
