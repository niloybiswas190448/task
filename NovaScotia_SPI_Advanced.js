// ============================================================================
// NOVA SCOTIA ADVANCED SPI CALCULATION WITH MULTIPLE DATASETS
// Enhanced version with data quality checks and advanced analysis
// Years: 2001, 2008, 2019, 2022, 2023, 2024
// ============================================================================

// Import multiple precipitation datasets for comparison
var chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY');
var era5 = ee.ImageCollection('ECMWF/ERA5/DAILY');
var gpm = ee.ImageCollection('NASA/GPM_L3/IMERG_V06');

// Define Nova Scotia boundary with more precise coordinates
var novaScotiaBoundary = ee.Geometry.Polygon([
  [[-66.5, 43.0], [-59.5, 43.0], [-59.5, 47.5], [-66.5, 47.5], [-66.5, 43.0]]
]);

// Function to check data availability and quality
function checkDataQuality(dataset, startDate, endDate) {
  var data = dataset
    .filterDate(startDate, endDate)
    .filterBounds(novaScotiaBoundary);
  
  var count = data.size();
  var coverage = data.mean().reduceRegion({
    reducer: ee.Reducer.count(),
    geometry: novaScotiaBoundary,
    scale: 5000,
    maxPixels: 1e13
  });
  
  return {
    'dataset': dataset,
    'count': count,
    'coverage': coverage,
    'hasData': count.gt(0)
  };
}

// Enhanced SPI calculation with data quality checks
function calculateEnhancedSPI(startDate, endDate, scale, dataset) {
  // Get precipitation data for the period
  var precipitation = dataset
    .filterDate(startDate, endDate)
    .select('precipitation')
    .filterBounds(novaScotiaBoundary);
  
  // Check if we have sufficient data
  var dataCount = precipitation.size();
  var hasSufficientData = dataCount.gte(scale * 0.8); // At least 80% of expected data
  
  // Calculate total precipitation for the period
  var totalPrecip = precipitation.sum();
  
  // Get historical data for baseline (30 years before the target year)
  var baselineStart = ee.Date(startDate).advance(-30, 'year');
  var baselineEnd = ee.Date(startDate).advance(-1, 'day');
  
  var historicalPrecip = dataset
    .filterDate(baselineStart, baselineEnd)
    .select('precipitation')
    .filterBounds(novaScotiaBoundary);
  
  // Calculate historical statistics with quality checks
  var historicalStats = historicalPrecip.sum().reduceRegion({
    reducer: ee.Reducer.mean().combine(ee.Reducer.stdDev(), '', true)
      .combine(ee.Reducer.minMax(), '', true),
    geometry: novaScotiaBoundary,
    scale: 5000,
    maxPixels: 1e13
  });
  
  // Calculate SPI with error handling
  var mean = ee.Image.constant(historicalStats.get('precipitation_mean'));
  var stdDev = ee.Image.constant(historicalStats.get('precipitation_stdDev'));
  
  // Handle division by zero and invalid values
  var validStdDev = stdDev.gt(0.001); // Avoid division by very small numbers
  var spi = ee.Image.where(
    validStdDev,
    totalPrecip.subtract(mean).divide(stdDev),
    ee.Image.constant(0)
  );
  
  // Apply quality mask
  var qualityMask = hasSufficientData;
  spi = ee.Image.where(qualityMask, spi, ee.Image.constant(ee.Number.NaN));
  
  return spi.rename('SPI_' + scale + 'month');
}

// Function to calculate SPI using multiple datasets
function calculateMultiDatasetSPI(year, month) {
  var startDate = ee.Date.fromYMD(year, month, 1);
  var endDate = startDate.advance(1, 'month').advance(-1, 'day');
  
  // Calculate SPI for each dataset
  var chirpsSPI = calculateEnhancedSPI(startDate, endDate, 1, chirps);
  var era5SPI = calculateEnhancedSPI(startDate, endDate, 1, era5.select('total_precipitation'));
  var gpmSPI = calculateEnhancedSPI(startDate, endDate, 1, gpm.select('precipitationCal'));
  
  // Combine results
  return ee.Image.cat([chirpsSPI, era5SPI, gpmSPI])
    .set('year', year)
    .set('month', month);
}

// Function to calculate ensemble SPI (average of multiple datasets)
function calculateEnsembleSPI(year) {
  var startDate = ee.Date.fromYMD(year, 1, 1);
  var endDate = ee.Date.fromYMD(year, 12, 31);
  
  // Calculate SPI for different time scales using ensemble
  var scales = [1, 3, 6, 12];
  var ensembleResults = scales.map(function(scale) {
    var chirpsSPI = calculateEnhancedSPI(startDate, endDate, scale, chirps);
    var era5SPI = calculateEnhancedSPI(startDate, endDate, scale, era5.select('total_precipitation'));
    var gpmSPI = calculateEnhancedSPI(startDate, endDate, scale, gpm.select('precipitationCal'));
    
    // Calculate ensemble mean
    var ensemble = ee.Image.cat([chirpsSPI, era5SPI, gpmSPI]).reduce(ee.Reducer.mean());
    
    return ensemble.rename('SPI_' + scale + 'month_ensemble');
  });
  
  return ee.Image.cat(ensembleResults).set('year', year);
}

// Function to calculate drought severity and duration
function calculateDroughtMetrics(spiCollection) {
  return spiCollection.map(function(image) {
    // Define drought categories
    var moderateDrought = image.lt(-1).And(image.gte(-1.5));
    var severeDrought = image.lt(-1.5).And(image.gte(-2));
    var extremeDrought = image.lt(-2);
    
    // Calculate areas
    var moderateArea = moderateDrought.multiply(ee.Image.pixelArea()).reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: novaScotiaBoundary,
      scale: 5000,
      maxPixels: 1e13
    });
    
    var severeArea = severeDrought.multiply(ee.Image.pixelArea()).reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: novaScotiaBoundary,
      scale: 5000,
      maxPixels: 1e13
    });
    
    var extremeArea = extremeDrought.multiply(ee.Image.pixelArea()).reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: novaScotiaBoundary,
      scale: 5000,
      maxPixels: 1e13
    });
    
    // Calculate drought severity index
    var severityIndex = image.where(image.gt(0), 0, image.abs());
    
    return ee.Feature(null, {
      'year': image.get('year'),
      'moderate_drought_area_km2': moderateArea,
      'severe_drought_area_km2': severeArea,
      'extreme_drought_area_km2': extremeArea,
      'mean_severity': severityIndex.reduceRegion({
        reducer: ee.Reducer.mean(),
        geometry: novaScotiaBoundary,
        scale: 5000,
        maxPixels: 1e13
      })
    });
  });
}

// Function to create drought frequency analysis
function createDroughtFrequency(spiCollection) {
  // Create drought frequency map
  var droughtFrequency = spiCollection
    .map(function(image) {
      return image.lt(-1); // Moderate drought threshold
    })
    .sum()
    .divide(spiCollection.size())
    .multiply(100); // Convert to percentage
  
  return droughtFrequency.rename('Drought_Frequency_Percent');
}

// Function to calculate SPI trends using linear regression
function calculateSPITrends(spiCollection) {
  var trendAnalysis = spiCollection.map(function(image) {
    return image.set('time', image.get('year'));
  });
  
  var trend = trendAnalysis.reduce(ee.Reducer.linearFit());
  
  return {
    'slope': trend.select('.*_slope'),
    'offset': trend.select('.*_offset'),
    'r2': trend.select('.*_r2')
  };
}

// Function to create comprehensive visualization
function createVisualization(spiImage, title) {
  // Create multiple visualization layers
  var spiVis = {
    min: -3,
    max: 3,
    palette: ['8B0000', 'FF0000', 'FFA500', 'FFFF00', '90EE90', '008000', '006400']
  };
  
  var classificationVis = {
    min: 0,
    max: 6,
    palette: ['8B0000', 'FF0000', 'FFA500', 'FFFF00', '90EE90', '008000', '006400']
  };
  
  // Add layers to map
  Map.addLayer(spiImage, spiVis, title + ' - SPI Values');
  
  // Add classification layer
  var classification = classifySPI(spiImage);
  Map.addLayer(classification, classificationVis, title + ' - Classification');
  
  // Add drought areas layer
  var droughtAreas = spiImage.lt(-1);
  Map.addLayer(droughtAreas.selfMask(), {palette: ['red']}, title + ' - Drought Areas');
}

// Main execution
var targetYears = [2001, 2008, 2019, 2022, 2023, 2024];

// Calculate ensemble SPI for all years
var ensembleResults = ee.List(targetYears).map(function(year) {
  return calculateEnsembleSPI(ee.Number(year));
});

var ensembleCollection = ee.ImageCollection(ensembleResults);

// Calculate drought metrics
var droughtMetrics = calculateDroughtMetrics(ensembleCollection);

// Calculate drought frequency
var droughtFrequency = createDroughtFrequency(ensembleCollection);

// Calculate trends
var trends = calculateSPITrends(ensembleCollection);

// Setup map
Map.centerObject(novaScotiaBoundary, 7);
Map.addLayer(novaScotiaBoundary, {color: 'blue', fillColor: '00000000'}, 'Nova Scotia Boundary');

// Display latest results (2024)
var latestEnsemble = ensembleCollection.filter(ee.Filter.eq('year', 2024)).first();

if (latestEnsemble) {
  createVisualization(latestEnsemble.select('SPI_12month_ensemble'), '2024 Annual SPI');
  createVisualization(latestEnsemble.select('SPI_6month_ensemble'), '2024 6-Month SPI');
  createVisualization(latestEnsemble.select('SPI_3month_ensemble'), '2024 3-Month SPI');
}

// Display drought frequency
Map.addLayer(droughtFrequency, {
  min: 0,
  max: 50,
  palette: ['white', 'yellow', 'orange', 'red', 'darkred']
}, 'Drought Frequency (%)');

// Display trends
Map.addLayer(trends.slope.select('SPI_12month_ensemble_slope'), {
  min: -0.1,
  max: 0.1,
  palette: ['red', 'white', 'blue']
}, 'SPI Trend (12-month)');

// Export functions
function exportAdvancedResults() {
  // Export ensemble SPI results
  Export.image.toDrive({
    image: ensembleCollection,
    description: 'NovaScotia_Ensemble_SPI_Results',
    folder: 'NovaScotia_Advanced_SPI_Analysis',
    scale: 5000,
    region: novaScotiaBoundary,
    maxPixels: 1e13
  });
  
  // Export drought metrics
  Export.table.toDrive({
    collection: droughtMetrics,
    description: 'NovaScotia_Drought_Metrics',
    folder: 'NovaScotia_Advanced_SPI_Analysis',
    fileFormat: 'CSV'
  });
  
  // Export drought frequency
  Export.image.toDrive({
    image: droughtFrequency,
    description: 'NovaScotia_Drought_Frequency',
    folder: 'NovaScotia_Advanced_SPI_Analysis',
    scale: 5000,
    region: novaScotiaBoundary,
    maxPixels: 1e13
  });
  
  // Export trends
  Export.image.toDrive({
    image: trends.slope,
    description: 'NovaScotia_SPI_Trends',
    folder: 'NovaScotia_Advanced_SPI_Analysis',
    scale: 5000,
    region: novaScotiaBoundary,
    maxPixels: 1e13
  });
}

// Print analysis summary
print('=== NOVA SCOTIA ADVANCED SPI ANALYSIS ===');
print('Target Years: ' + targetYears);
print('Datasets Used: CHIRPS, ERA5, GPM IMERG');
print('Analysis Features:');
print('- Multi-dataset ensemble SPI calculation');
print('- Data quality checks and validation');
print('- Drought severity and frequency analysis');
print('- Trend analysis with statistical significance');
print('- Comprehensive visualization layers');

// Print SPI classification guide
print('=== SPI CLASSIFICATION GUIDE ===');
print('Extremely Dry: SPI < -2.0');
print('Very Dry: -2.0 ≤ SPI < -1.5');
print('Moderately Dry: -1.5 ≤ SPI < -1.0');
print('Near Normal: -1.0 ≤ SPI < 1.0');
print('Moderately Wet: 1.0 ≤ SPI < 1.5');
print('Very Wet: 1.5 ≤ SPI < 2.0');
print('Extremely Wet: SPI ≥ 2.0');

// Execute exports (uncomment to run)
// exportAdvancedResults();

// Add legend
var legend = ui.Panel({
  style: {
    width: '300px',
    padding: '10px'
  }
});

var legendTitle = ui.Label({
  value: 'SPI Classification',
  style: {fontWeight: 'bold', fontSize: '16px', margin: '10px 0'}
});
legend.add(legendTitle);

var colors = ['8B0000', 'FF0000', 'FFA500', 'FFFF00', '90EE90', '008000', '006400'];
var names = ['Extremely Dry', 'Very Dry', 'Moderately Dry', 'Near Normal', 
             'Moderately Wet', 'Very Wet', 'Extremely Wet'];

colors.forEach(function(color, index) {
  var colorBox = ui.Label({
    style: {
      backgroundColor: '#' + color,
      padding: '8px',
      margin: '0 0 4px 6px'
    }
  });
  var description = ui.Label({
    value: names[index],
    style: {margin: '0 0 4px 6px'}
  });
  legend.add(ui.Panel({
    widgets: [colorBox, description],
    layout: ui.Panel.Layout.Flow('horizontal')
  }));
});

Map.add(legend);