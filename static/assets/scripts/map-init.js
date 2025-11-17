/**
 * Leaflet map initialization for orthophoto display
 * Extracted from inline scripts for CSP compliance
 */

(function() {
    'use strict';

    /**
     * Initialize the Leaflet map with GeoTIFF layer
     */
    function initMap() {
        var mapContainer = document.getElementById('map');
        if (!mapContainer) return;

        // Get the orthophoto URL from data attribute
        var geotiffUrl = mapContainer.getAttribute('data-geotiff-url');
        if (!geotiffUrl) {
            console.error('No GeoTIFF URL provided');
            return;
        }

        // Trim whitespace from URL
        geotiffUrl = geotiffUrl.trim();

        var popup = L.popup();
        var map = L.map('map');

        var osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            markerZoomAnimation: true,
            zoomControl: true,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        });

        var osm2 = L.tileLayer('https://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            maxZoom: 25,
            attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
        });

        var googleStreets = L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
            maxZoom: 20,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
        });

        var googleHybrid = L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', {
            maxZoom: 25,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
        }).addTo(map);

        var googleSat = L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
            maxZoom: 20,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
        });

        var googleTerrain = L.tileLayer('https://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', {
            maxZoom: 20,
            subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
        });

        var baseLayers = {
            "Google Hybrid": googleHybrid
        };

        L.control.layers(baseLayers).addTo(map);

        // Load the GeoTIFF file
        fetch(geotiffUrl)
            .then(function(response) {
                return response.arrayBuffer();
            })
            .then(function(arrayBuffer) {
                parseGeoraster(arrayBuffer).then(function(georaster) {
                    console.log("georaster:", georaster);

                    var layer = new GeoRasterLayer({
                        georaster: georaster,
                        opacity: 100,
                        resolution: 256
                    });
                    layer.addTo(map);

                    map.fitBounds(layer.getBounds());
                });
            })
            .catch(function(error) {
                console.error('Failed to load GeoTIFF:', error);
            });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMap);
    } else {
        initMap();
    }
})();
