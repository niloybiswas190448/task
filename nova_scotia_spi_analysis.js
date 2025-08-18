// Nova Scotia SPI Analysis - Simple Google Earth Engine Code
// This script calculates SPI for Nova Scotia for multiple years

// Define Nova Scotia boundary (simplified)
var novaScotia = ee.Geometry.Rectangle([-66.5, 43.0, -59.5, 47.5]);

// Define years of interest
var years = [2001, 2008, 2019, 2022, 2023, 2024];

// Function to calculate SPI for a given year
function calculateSPI(year) {
  // Get precipitation data for the year (3-month period for SPI-3)
  var startDate = ee.Date.fromYMD(year, 1, 1);
  var endDate = ee.Date.fromYMD(year, 12, 31);
  
  // Use CHIRPS precipitation data
  var precipitation = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
    .filterDate(startDate, endDate)
    .select('precipitation')
    .sum();
  
  // Calculate 30-year climatology (1991-2020) for the same period
  var climatologyStart = ee.Date.fromYMD(1991, 1, 1);
  var climatologyEnd = ee.Date.fromYMD(2020, 12, 31);
  
  var climatology = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
    .filterDate(climatologyStart, climatologyEnd)
    .select('precipitation')
    .sum();
  
  // Calculate mean and standard deviation of climatology
  var mean = climatology.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: novaScotia,
    scale: 5000,
    maxPixels: 1e9
  }).get('precipitation');
  
  var stdDev = climatology.reduceRegion({
    reducer: ee.Reducer.stdDev(),
    geometry: novaScotia,
    scale: 5000,
    maxPixels: 1e9
  }).get('precipitation');
  
  // Calculate SPI
  var spi = precipitation.subtract(mean).divide(stdDev);
  
  return spi.set('year', year);
}

// Calculate SPI for all years
var spiCollection = ee.ImageCollection(years.map(calculateSPI));

// Visualization parameters
var spiVis = {
  min: -3,
  max: 3,
  palette: ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen']
};

// Display SPI for each year
years.forEach(function(year) {
  var spiImage = spiCollection.filter(ee.Filter.eq('year', year)).first();
  
  Map.addLayer(spiImage, spiVis, 'SPI ' + year);
});

// Set map center to Nova Scotia
Map.centerObject(novaScotia, 7);

// Export function for each year
function exportSPI(year) {
  var spiImage = spiCollection.filter(ee.Filter.eq('year', year)).first();
  
  Export.image.toDrive({
    image: spiImage,
    description: 'NovaScotia_SPI_' + year,
    folder: 'NovaScotia_SPI_Analysis',
    scale: 5000,
    region: novaScotia,
    maxPixels: 1e9
  });
}

// Export all years
years.forEach(exportSPI);

// Print summary statistics
print('SPI Analysis for Nova Scotia');
print('Years analyzed:', years);
print('SPI Collection:', spiCollection);

// Add legend
var legend = ui.Panel({
  style: {
    width: '300px',
    padding: '10px'
  }
});

var legendTitle = ui.Label({
  value: 'SPI Values',
  style: {fontWeight: 'bold', fontSize: '16px', margin: '10px 0'}
});
legend.add(legendTitle);

var colors = ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen'];
var values = ['-3 to -2', '-2 to -1', '-1 to 0', '0 to 1', '1 to 2', '2 to 3'];

colors.forEach(function(color, index) {
  var colorBox = ui.Label({
    style: {
      backgroundColor: color,
      padding: '8px',
      margin: '0 0 4px 6px'
    }
  });
  
  var description = ui.Label({
    value: values[index],
    style: {margin: '0 0 4px 6px'}
  });
  
  legend.add(ui.Panel({
    widgets: [colorBox, description],
    layout: ui.Panel.Layout.Flow('horizontal')
  }));
});

Map.add(legend);