// ============================================================================
// NOVA SCOTIA STANDARDIZED PRECIPITATION INDEX (SPI) CALCULATION
// Years: 2001, 2008, 2019, 2022, 2023, 2024
// ============================================================================

// Import required datasets
var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY');
var novaScotia = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')
  .filter(ee.Filter.eq('country_na', 'Canada'))
  .geometry();

// Define Nova Scotia boundary (approximate)
var novaScotiaBoundary = ee.Geometry.Rectangle([-66.5, 43.0, -59.5, 47.5]);

// Function to calculate SPI for a given time period
function calculateSPI(startDate, endDate, scale) {
  // Get precipitation data for the period
  var precipitation = chirps
    .filterDate(startDate, endDate)
    .select('precipitation')
    .filterBounds(novaScotiaBoundary);
  
  // Calculate total precipitation for the period
  var totalPrecip = precipitation.sum();
  
  // Get historical data for baseline (30 years before the target year)
  var baselineStart = ee.Date(startDate).advance(-30, 'year');
  var baselineEnd = ee.Date(startDate).advance(-1, 'day');
  
  var historicalPrecip = chirps
    .filterDate(baselineStart, baselineEnd)
    .select('precipitation')
    .filterBounds(novaScotiaBoundary);
  
  // Calculate historical statistics
  var historicalStats = historicalPrecip.sum().reduceRegion({
    reducer: ee.Reducer.mean().combine(ee.Reducer.stdDev(), '', true),
    geometry: novaScotiaBoundary,
    scale: scale,
    maxPixels: 1e13
  });
  
  // Calculate SPI
  var mean = ee.Image.constant(historicalStats.get('precipitation_mean'));
  var stdDev = ee.Image.constant(historicalStats.get('precipitation_stdDev'));
  
  var spi = totalPrecip.subtract(mean).divide(stdDev);
  
  return spi.rename('SPI_' + scale + 'month');
}

// Function to calculate SPI for multiple time scales
function calculateMultiScaleSPI(year) {
  var startDate = ee.Date.fromYMD(year, 1, 1);
  var endDate = ee.Date.fromYMD(year, 12, 31);
  
  // Calculate SPI for different time scales
  var spi1month = calculateSPI(startDate, endDate, 1);
  var spi3month = calculateSPI(startDate, endDate, 3);
  var spi6month = calculateSPI(startDate, endDate, 6);
  var spi12month = calculateSPI(startDate, endDate, 12);
  
  return ee.Image.cat([spi1month, spi3month, spi6month, spi12month])
    .set('year', year);
}

// Function to calculate SPI for specific months
function calculateMonthlySPI(year, month) {
  var startDate = ee.Date.fromYMD(year, month, 1);
  var endDate = startDate.advance(1, 'month').advance(-1, 'day');
  
  return calculateSPI(startDate, endDate, 1)
    .set('year', year)
    .set('month', month);
}

// Function to calculate seasonal SPI
function calculateSeasonalSPI(year) {
  var winter = calculateSPI(
    ee.Date.fromYMD(year, 12, 1),
    ee.Date.fromYMD(year + 1, 2, 28),
    3
  ).rename('SPI_Winter');
  
  var spring = calculateSPI(
    ee.Date.fromYMD(year, 3, 1),
    ee.Date.fromYMD(year, 5, 31),
    3
  ).rename('SPI_Spring');
  
  var summer = calculateSPI(
    ee.Date.fromYMD(year, 6, 1),
    ee.Date.fromYMD(year, 8, 31),
    3
  ).rename('SPI_Summer');
  
  var fall = calculateSPI(
    ee.Date.fromYMD(year, 9, 1),
    ee.Date.fromYMD(year, 11, 30),
    3
  ).rename('SPI_Fall');
  
  return ee.Image.cat([winter, spring, summer, fall])
    .set('year', year);
}

// Function to classify SPI values
function classifySPI(spiImage) {
  return spiImage.remap(
    [-999, -2, -1.5, -1, 1, 1.5, 2, 999],
    [0, 1, 2, 3, 4, 5, 6, 7]
  ).rename('SPI_Classification');
}

// Function to add SPI classification labels
function addSPIClassification(spiImage) {
  var classification = classifySPI(spiImage);
  var labels = ee.List(['Extremely Wet', 'Very Wet', 'Moderately Wet', 
                        'Near Normal', 'Moderately Dry', 'Very Dry', 'Extremely Dry']);
  
  return classification.remap(
    [1, 2, 3, 4, 5, 6, 7],
    [0, 1, 2, 3, 4, 5, 6]
  ).rename('SPI_Category');
}

// Main execution for all target years
var targetYears = [2001, 2008, 2019, 2022, 2023, 2024];
var spiResults = ee.List(targetYears).map(function(year) {
  return calculateMultiScaleSPI(ee.Number(year));
});

var spiCollection = ee.ImageCollection(spiResults);

// Calculate seasonal SPI for all years
var seasonalResults = ee.List(targetYears).map(function(year) {
  return calculateSeasonalSPI(ee.Number(year));
});

var seasonalCollection = ee.ImageCollection(seasonalResults);

// Calculate monthly SPI for the most recent years (2022-2024)
var recentYears = [2022, 2023, 2024];
var monthlyResults = [];

recentYears.forEach(function(year) {
  for (var month = 1; month <= 12; month++) {
    monthlyResults.push(calculateMonthlySPI(year, month));
  }
});

var monthlyCollection = ee.ImageCollection(monthlyResults);

// Create visualization parameters
var spiVisParams = {
  min: -3,
  max: 3,
  palette: ['8B0000', 'FF0000', 'FFA500', 'FFFF00', '90EE90', '008000', '006400']
};

var classificationVisParams = {
  min: 0,
  max: 6,
  palette: ['8B0000', 'FF0000', 'FFA500', 'FFFF00', '90EE90', '008000', '006400']
};

// Export functions
function exportSPIResults() {
  // Export annual SPI results
  Export.image.toDrive({
    image: spiCollection,
    description: 'NovaScotia_Annual_SPI_Results',
    folder: 'NovaScotia_SPI_Analysis',
    scale: 5000,
    region: novaScotiaBoundary,
    maxPixels: 1e13
  });
  
  // Export seasonal SPI results
  Export.image.toDrive({
    image: seasonalCollection,
    description: 'NovaScotia_Seasonal_SPI_Results',
    folder: 'NovaScotia_SPI_Analysis',
    scale: 5000,
    region: novaScotiaBoundary,
    maxPixels: 1e13
  });
  
  // Export monthly SPI results
  Export.image.toDrive({
    image: monthlyCollection,
    description: 'NovaScotia_Monthly_SPI_Results',
    folder: 'NovaScotia_SPI_Analysis',
    scale: 5000,
    region: novaScotiaBoundary,
    maxPixels: 1e13
  });
}

// Function to create summary statistics
function createSummaryStats() {
  var summaryStats = spiCollection.map(function(image) {
    var stats = image.reduceRegion({
      reducer: ee.Reducer.mean().combine(ee.Reducer.stdDev(), '', true)
        .combine(ee.Reducer.minMax(), '', true),
      geometry: novaScotiaBoundary,
      scale: 5000,
      maxPixels: 1e13
    });
    
    return ee.Feature(null, stats).set('year', image.get('year'));
  });
  
  Export.table.toDrive({
    collection: summaryStats,
    description: 'NovaScotia_SPI_Summary_Statistics',
    folder: 'NovaScotia_SPI_Analysis',
    fileFormat: 'CSV'
  });
}

// Function to detect drought events
function detectDroughtEvents() {
  var droughtEvents = spiCollection.map(function(image) {
    // Define drought threshold (SPI < -1)
    var droughtMask = image.lt(-1);
    var severeDroughtMask = image.lt(-1.5);
    var extremeDroughtMask = image.lt(-2);
    
    var droughtArea = droughtMask.multiply(ee.Image.pixelArea()).reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: novaScotiaBoundary,
      scale: 5000,
      maxPixels: 1e13
    });
    
    var severeDroughtArea = severeDroughtMask.multiply(ee.Image.pixelArea()).reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: novaScotiaBoundary,
      scale: 5000,
      maxPixels: 1e13
    });
    
    var extremeDroughtArea = extremeDroughtMask.multiply(ee.Image.pixelArea()).reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: novaScotiaBoundary,
      scale: 5000,
      maxPixels: 1e13
    });
    
    return ee.Feature(null, {
      'year': image.get('year'),
      'drought_area_km2': droughtArea,
      'severe_drought_area_km2': severeDroughtArea,
      'extreme_drought_area_km2': extremeDroughtArea
    });
  });
  
  Export.table.toDrive({
    collection: droughtEvents,
    description: 'NovaScotia_Drought_Events_Analysis',
    folder: 'NovaScotia_SPI_Analysis',
    fileFormat: 'CSV'
  });
}

// Function to create trend analysis
function createTrendAnalysis() {
  var trendAnalysis = spiCollection.map(function(image) {
    var trend = image.reduceRegion({
      reducer: ee.Reducer.linearFit(),
      geometry: novaScotiaBoundary,
      scale: 5000,
      maxPixels: 1e13
    });
    
    return ee.Feature(null, trend).set('year', image.get('year'));
  });
  
  Export.table.toDrive({
    collection: trendAnalysis,
    description: 'NovaScotia_SPI_Trend_Analysis',
    folder: 'NovaScotia_SPI_Analysis',
    fileFormat: 'CSV'
  });
}

// Main execution
print('Nova Scotia SPI Analysis for Years: ' + targetYears);
print('Analysis includes:');
print('- Annual SPI (1, 3, 6, 12 month scales)');
print('- Seasonal SPI (Winter, Spring, Summer, Fall)');
print('- Monthly SPI (2022-2024)');
print('- Drought event detection');
print('- Trend analysis');

// Display results for the most recent year (2024)
var latestSPI = spiCollection.filter(ee.Filter.eq('year', 2024)).first();
var latestSeasonal = seasonalCollection.filter(ee.Filter.eq('year', 2024)).first();

// Add layers to map
Map.centerObject(novaScotiaBoundary, 7);
Map.addLayer(novaScotiaBoundary, {color: 'blue'}, 'Nova Scotia Boundary');

if (latestSPI) {
  Map.addLayer(latestSPI.select('SPI_12month'), spiVisParams, 'SPI 12-month (2024)');
  Map.addLayer(latestSPI.select('SPI_6month'), spiVisParams, 'SPI 6-month (2024)');
  Map.addLayer(latestSPI.select('SPI_3month'), spiVisParams, 'SPI 3-month (2024)');
  Map.addLayer(latestSPI.select('SPI_1month'), spiVisParams, 'SPI 1-month (2024)');
}

if (latestSeasonal) {
  Map.addLayer(latestSeasonal.select('SPI_Summer'), spiVisParams, 'Summer SPI (2024)');
  Map.addLayer(latestSeasonal.select('SPI_Winter'), spiVisParams, 'Winter SPI (2024)');
}

// Execute exports (uncomment to run)
// exportSPIResults();
// createSummaryStats();
// detectDroughtEvents();
// createTrendAnalysis();

// Print summary information
print('SPI Classification:');
print('- Extremely Dry: SPI < -2.0');
print('- Very Dry: -2.0 ≤ SPI < -1.5');
print('- Moderately Dry: -1.5 ≤ SPI < -1.0');
print('- Near Normal: -1.0 ≤ SPI < 1.0');
print('- Moderately Wet: 1.0 ≤ SPI < 1.5');
print('- Very Wet: 1.5 ≤ SPI < 2.0');
print('- Extremely Wet: SPI ≥ 2.0');

print('Data Sources:');
print('- Precipitation: CHIRPS Daily (UCSB-CHG/CHIRPS/DAILY)');
print('- Study Area: Nova Scotia, Canada');
print('- Analysis Period: 2001, 2008, 2019, 2022, 2023, 2024');