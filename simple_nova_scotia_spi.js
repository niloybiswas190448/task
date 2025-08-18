// SIMPLE Nova Scotia SPI Analysis
// Copy and paste this code directly into Google Earth Engine Code Editor

// Step 1: Define Nova Scotia area
var novaScotia = ee.Geometry.Rectangle([-66.5, 43.0, -59.5, 47.5]);

// Step 2: List of years you want to analyze
var years = [2001, 2008, 2019, 2022, 2023, 2024];

// Step 3: Simple SPI calculation function
function getSPI(year) {
  // Get rainfall data for the year
  var yearData = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
    .filterDate(year + '-01-01', year + '-12-31')
    .select('precipitation')
    .sum();
  
  // Get long-term average (1991-2020)
  var longTermData = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
    .filterDate('1991-01-01', '2020-12-31')
    .select('precipitation')
    .sum();
  
  // Calculate SPI = (current - average) / standard deviation
  var mean = longTermData.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: novaScotia,
    scale: 5000
  }).get('precipitation');
  
  var std = longTermData.reduceRegion({
    reducer: ee.Reducer.stdDev(),
    geometry: novaScotia,
    scale: 5000
  }).get('precipitation');
  
  var spi = yearData.subtract(mean).divide(std);
  return spi.set('year', year);
}

// Step 4: Calculate SPI for all years
var allSPI = ee.ImageCollection(years.map(getSPI));

// Step 5: Set up the map
Map.centerObject(novaScotia, 7);

// Step 6: Add layers to map with colors
var colors = {
  min: -3,
  max: 3,
  palette: ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen']
};

// Add each year as a separate layer
years.forEach(function(year) {
  var spiLayer = allSPI.filter(ee.Filter.eq('year', year)).first();
  Map.addLayer(spiLayer, colors, 'SPI ' + year);
});

// Step 7: Export maps to Google Drive
years.forEach(function(year) {
  var spiLayer = allSPI.filter(ee.Filter.eq('year', year)).first();
  
  Export.image.toDrive({
    image: spiLayer,
    description: 'NovaScotia_SPI_' + year,
    folder: 'NovaScotia_SPI',
    scale: 5000,
    region: novaScotia
  });
});

// Step 8: Print results
print('SPI Analysis Complete for Nova Scotia');
print('Years analyzed:', years);
print('SPI Data:', allSPI);

// Step 9: Add simple legend
var legend = ui.Panel({
  style: {width: '200px', padding: '10px'}
});

legend.add(ui.Label('SPI Values:'));
legend.add(ui.Label('Red = Very Dry (-3 to -2)'));
legend.add(ui.Label('Orange = Dry (-2 to -1)'));
legend.add(ui.Label('Yellow = Slightly Dry (-1 to 0)'));
legend.add(ui.Label('Light Green = Normal (0 to 1)'));
legend.add(ui.Label('Green = Wet (1 to 2)'));
legend.add(ui.Label('Dark Green = Very Wet (2 to 3)'));

Map.add(legend);