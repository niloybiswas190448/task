# Nova Scotia SPI Analysis - Google Earth Engine

This is a simple Google Earth Engine script to calculate and visualize Standardized Precipitation Index (SPI) for Nova Scotia.

## What is SPI?
SPI (Standardized Precipitation Index) measures drought conditions by comparing current precipitation to historical averages. Values range from -3 (very dry) to +3 (very wet).

## How to Use This Code

### Step 1: Access Google Earth Engine
1. Go to [Google Earth Engine Code Editor](https://code.earthengine.google.com/)
2. Sign in with your Google account
3. If you don't have access, request it from Google

### Step 2: Copy the Code
1. Open the file `simple_nova_scotia_spi.js`
2. Copy all the code
3. Paste it into the Google Earth Engine Code Editor

### Step 3: Run the Analysis
1. Click the "Run" button in the Code Editor
2. Wait for the processing to complete (may take a few minutes)
3. The map will show SPI layers for each year

### Step 4: Export Maps
1. Go to the "Tasks" tab in the Code Editor
2. You'll see export tasks for each year
3. Click "Run" on each task to download the maps to your Google Drive

## What the Code Does

1. **Defines Nova Scotia area** - Uses a rectangle covering Nova Scotia
2. **Calculates SPI for each year** - Compares yearly rainfall to 30-year average (1991-2020)
3. **Creates visualizations** - Color-coded maps showing drought conditions
4. **Exports results** - Saves maps to your Google Drive

## Years Analyzed
- 2001
- 2008  
- 2019
- 2022
- 2023
- 2024

## Color Legend
- **Red**: Very Dry (SPI -3 to -2)
- **Orange**: Dry (SPI -2 to -1)
- **Yellow**: Slightly Dry (SPI -1 to 0)
- **Light Green**: Normal (SPI 0 to 1)
- **Green**: Wet (SPI 1 to 2)
- **Dark Green**: Very Wet (SPI 2 to 3)

## Data Source
Uses CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data) daily precipitation data.

## Customization
To analyze different years, simply change the `years` array in the code:
```javascript
var years = [2001, 2008, 2019, 2022, 2023, 2024]; // Change these years
```

## Output Files
The script will create separate map files for each year in your Google Drive folder called "NovaScotia_SPI".