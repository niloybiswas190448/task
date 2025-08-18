# Nova Scotia Standardized Precipitation Index (SPI) Analysis

## Overview
This repository contains Google Earth Engine scripts for calculating the Standardized Precipitation Index (SPI) for Nova Scotia, Canada, for the years 2001, 2008, 2019, 2022, 2023, and 2024.

## Files Included

### 1. `NovaScotia_SPI_Calculation.js` - Basic SPI Analysis
- **Purpose**: Core SPI calculation using CHIRPS precipitation data
- **Features**:
  - Annual SPI calculation (1, 3, 6, 12-month scales)
  - Seasonal SPI analysis (Winter, Spring, Summer, Fall)
  - Monthly SPI for recent years (2022-2024)
  - Drought event detection
  - Basic trend analysis
  - Export functionality for results

### 2. `NovaScotia_SPI_Advanced.js` - Advanced SPI Analysis
- **Purpose**: Enhanced SPI analysis with multiple datasets and advanced features
- **Features**:
  - Multi-dataset ensemble (CHIRPS, ERA5, GPM IMERG)
  - Data quality checks and validation
  - Drought severity and frequency analysis
  - Advanced trend analysis with statistical significance
  - Comprehensive visualization with interactive legend
  - Enhanced export capabilities

## How to Use

### Prerequisites
1. Google Earth Engine account (https://earthengine.google.com/)
2. Access to Google Earth Engine Code Editor
3. Basic knowledge of JavaScript and Earth Engine

### Step-by-Step Instructions

#### 1. Access Google Earth Engine
- Go to https://code.earthengine.google.com/
- Sign in with your Google account
- Ensure you have Earth Engine access enabled

#### 2. Load the Script
- Copy the content of either script file
- Paste it into the Code Editor
- Click "Run" to execute the script

#### 3. View Results
- The script will automatically center the map on Nova Scotia
- Multiple layers will be added to the map showing different SPI analyses
- Use the layer controls to toggle different visualizations

#### 4. Export Results (Optional)
- Uncomment the export functions at the bottom of the script
- Run the script again to initiate exports
- Results will be saved to your Google Drive

## SPI Classification

The scripts use the following SPI classification system:

| SPI Range | Classification |
|-----------|----------------|
| SPI < -2.0 | Extremely Dry |
| -2.0 ≤ SPI < -1.5 | Very Dry |
| -1.5 ≤ SPI < -1.0 | Moderately Dry |
| -1.0 ≤ SPI < 1.0 | Near Normal |
| 1.0 ≤ SPI < 1.5 | Moderately Wet |
| 1.5 ≤ SPI < 2.0 | Very Wet |
| SPI ≥ 2.0 | Extremely Wet |

## Data Sources

### Precipitation Datasets
1. **CHIRPS Daily** (UCSB-CHG/CHIRPS/DAILY)
   - High-resolution precipitation estimates
   - Global coverage from 1981 to present
   - 0.05° spatial resolution

2. **ERA5 Daily** (ECMWF/ERA5/DAILY) - Advanced version only
   - European Centre for Medium-Range Weather Forecasts
   - Reanalysis data with high accuracy
   - 0.1° spatial resolution

3. **GPM IMERG V06** (NASA/GPM_L3/IMERG_V06) - Advanced version only
   - NASA's Global Precipitation Measurement
   - Multi-satellite precipitation estimates
   - 0.1° spatial resolution

### Study Area
- **Region**: Nova Scotia, Canada
- **Coordinates**: 43.0°N to 47.5°N, 59.5°W to 66.5°W
- **Area**: Approximately 55,284 km²

## Analysis Features

### Basic Script Features
- **Multi-scale Analysis**: 1, 3, 6, and 12-month SPI calculations
- **Seasonal Analysis**: Winter, Spring, Summer, and Fall SPI
- **Monthly Analysis**: Detailed monthly SPI for recent years
- **Drought Detection**: Automatic identification of drought events
- **Statistical Analysis**: Summary statistics and trend analysis

### Advanced Script Features
- **Ensemble Analysis**: Combines multiple precipitation datasets
- **Data Quality Checks**: Validates data availability and quality
- **Drought Frequency**: Calculates drought occurrence frequency
- **Severity Analysis**: Quantifies drought severity and duration
- **Trend Analysis**: Linear regression analysis of SPI trends
- **Interactive Visualization**: Enhanced map layers with legend

## Output Files

### Image Exports
- Annual SPI results (GeoTIFF format)
- Seasonal SPI results
- Monthly SPI results
- Drought frequency maps
- Trend analysis maps

### Table Exports
- Summary statistics (CSV format)
- Drought event analysis
- Trend analysis results

## Customization Options

### Modify Target Years
```javascript
var targetYears = [2001, 2008, 2019, 2022, 2023, 2024];
// Add or remove years as needed
```

### Adjust Study Area
```javascript
var novaScotiaBoundary = ee.Geometry.Rectangle([-66.5, 43.0, -59.5, 47.5]);
// Modify coordinates for different regions
```

### Change Analysis Scales
```javascript
var scales = [1, 3, 6, 12]; // Modify SPI time scales
```

### Adjust Drought Thresholds
```javascript
var droughtThreshold = -1; // Modify drought classification threshold
```

## Troubleshooting

### Common Issues

1. **"No data available" error**
   - Check if the target years have sufficient historical data
   - Verify dataset availability for the study area

2. **Export failures**
   - Ensure you have sufficient Google Drive storage
   - Check Earth Engine quotas and limits

3. **Slow processing**
   - Reduce the study area size
   - Use coarser resolution for faster processing
   - Limit the number of target years

### Performance Optimization
- Use appropriate scale parameters (5000m recommended)
- Limit maxPixels to reasonable values
- Process data in smaller chunks if needed

## Technical Notes

### SPI Calculation Method
The SPI is calculated using the following formula:
```
SPI = (X - μ) / σ
```
Where:
- X = precipitation value for the period
- μ = mean precipitation for the baseline period
- σ = standard deviation for the baseline period

### Baseline Period
- 30-year historical baseline (before the target year)
- Ensures robust statistical analysis
- Accounts for climate variability

### Statistical Assumptions
- Precipitation follows a gamma distribution
- Data is normally distributed after transformation
- Stationarity assumption for baseline period

## References

1. McKee, T.B., Doesken, N.J., & Kleist, J. (1993). The relationship of drought frequency and duration to time scales. *Proceedings of the 8th Conference on Applied Climatology*, 17-22.

2. Guttman, N.B. (1999). Accepting the standardized precipitation index: a calculation algorithm. *Journal of the American Water Resources Association*, 35(2), 311-322.

3. World Meteorological Organization (WMO). (2012). Standardized Precipitation Index User Guide. *WMO-No. 1090*.

## Support

For technical support or questions:
1. Check the Google Earth Engine documentation
2. Review the Earth Engine community forums
3. Ensure you have proper Earth Engine access permissions

## License

This code is provided for educational and research purposes. Please ensure compliance with Google Earth Engine terms of service and data usage policies.