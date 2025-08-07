# Internet Tools Analyzer - Android App

A comprehensive Java Android application that provides various internet analysis tools and network diagnostics capabilities. This app allows users to analyze their internet connection, perform speed tests, and gather detailed network information.

## Features

### 🚀 Speed Test
- **Download Speed Test**: Measures how fast you can receive data from the internet
- **Upload Speed Test**: Measures how fast you can send data to the internet
- **Ping Test**: Measures response time to test servers
- **Real-time Progress**: Shows live updates during testing
- **Connection Quality Assessment**: Provides quality ratings based on results

### 🌐 Network Information
- **Local IP Address**: Displays your device's local network IP
- **Public IP Address**: Shows your public internet IP address
- **Network Type**: Identifies WiFi, Mobile Data, or Ethernet connection
- **WiFi Details**: Shows SSID, signal strength, and frequency
- **DNS Information**: Tests connectivity to popular DNS servers
- **Connection Status**: Validates internet connectivity

### 📡 Ping Test
- **Custom Host Testing**: Ping any hostname or IP address
- **Multiple Ping Attempts**: Performs 5 ping tests for accuracy
- **Statistics**: Shows average, minimum, and maximum response times
- **Default Hosts**: Quick test with popular websites
- **Connection Quality Assessment**: Rates connection quality

### 🔍 DNS Lookup
- **Forward DNS Resolution**: Resolve domain names to IP addresses
- **Reverse DNS Lookup**: Get hostname from IP address
- **Multiple IP Support**: Shows all IP addresses for a domain
- **IPv4/IPv6 Support**: Displays both IPv4 and IPv6 addresses
- **Reachability Testing**: Tests if resolved IPs are reachable

### 🔌 Port Scanner
- **Common Ports Scan**: Tests 13 common service ports
- **Custom Port Range**: Scan specific port ranges (80-90)
- **Service Identification**: Shows which services are running
- **Multiple Host Support**: Scan multiple hosts simultaneously
- **Real-time Results**: Shows results as scanning progresses

### 🛣️ Traceroute
- **Network Path Tracing**: Shows the route to destination
- **Hop-by-Hop Analysis**: Displays each network hop
- **Response Time Measurement**: Measures latency at each hop
- **Network Diagnostics**: Comprehensive network analysis
- **Default Hosts**: Quick trace to popular websites

## Technical Features

### Architecture
- **Modern Android Architecture**: Uses AndroidX and Material Design
- **Multi-threading**: Background operations for network tests
- **Permission Handling**: Proper runtime permission requests
- **Error Handling**: Comprehensive error handling and user feedback

### UI/UX
- **Material Design**: Modern, clean interface following Material Design guidelines
- **Card-based Layout**: Organized information in easy-to-read cards
- **Real-time Updates**: Live progress indicators and status updates
- **Responsive Design**: Works on various screen sizes and orientations
- **Dark/Light Theme Support**: Adapts to system theme preferences

### Network Capabilities
- **HTTP/HTTPS Support**: Secure connections to test servers
- **Socket Operations**: Low-level network testing capabilities
- **DNS Resolution**: Native DNS lookup functionality
- **Port Scanning**: TCP socket connection testing
- **Reachability Testing**: ICMP ping simulation

## Installation

### Prerequisites
- Android Studio Arctic Fox or later
- Android SDK 21 (API level 21) or higher
- Java 8 or higher

### Build Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd internet-tools-analyzer
   ```

2. **Open in Android Studio**
   - Launch Android Studio
   - Select "Open an existing Android Studio project"
   - Navigate to the project directory and select it

3. **Sync Project**
   - Wait for Gradle sync to complete
   - Resolve any dependency issues if prompted

4. **Build and Run**
   - Connect an Android device or start an emulator
   - Click "Run" (green play button) in Android Studio
   - Select your target device and install the app

### Required Permissions

The app requires the following permissions:
- `INTERNET`: For network connectivity
- `ACCESS_NETWORK_STATE`: To check network status
- `ACCESS_WIFI_STATE`: To get WiFi information
- `ACCESS_FINE_LOCATION`: For precise location (optional)
- `ACCESS_COARSE_LOCATION`: For approximate location (optional)

## Usage Guide

### Getting Started
1. **Launch the App**: Open the Internet Tools Analyzer app
2. **Grant Permissions**: Allow the requested permissions when prompted
3. **Select a Tool**: Choose from the available network analysis tools
4. **Follow Instructions**: Each tool provides specific instructions for use

### Speed Test
1. Tap the "Speed Test" card
2. Click "Start Speed Test"
3. Wait for the test to complete (download, upload, and ping tests)
4. View your results and connection quality assessment

### Network Information
1. Tap the "Network Info" card
2. The app automatically loads and displays:
   - Your local and public IP addresses
   - Network connection type and details
   - WiFi information (if connected)
   - DNS server status

### Ping Test
1. Tap the "Ping Test" card
2. Enter a hostname or IP address
3. Click "Ping Host" for custom testing
4. Or click "Default Hosts" for quick testing
5. View detailed ping statistics and quality assessment

### DNS Lookup
1. Tap the "DNS Lookup" card
2. Enter a domain name or IP address
3. Click "DNS Lookup" for forward resolution
4. Click "Reverse DNS Lookup" for reverse resolution
5. View all resolved IP addresses and reachability

### Port Scanner
1. Tap the "Port Scanner" card
2. Enter a hostname or IP address
3. Choose scanning option:
   - "Scan Common Ports" for standard service ports
   - "Custom Port Range" for specific ports
   - "Default Hosts" for quick testing
4. View open ports and running services

### Traceroute
1. Tap the "Traceroute" card
2. Enter a hostname or IP address
3. Click "Start Traceroute" to begin path analysis
4. Or click "Network Diagnostics" for comprehensive analysis
5. View the network path and hop-by-hop details

## Technical Details

### Network Testing Methods
- **Speed Tests**: Uses HTTP/HTTPS connections to measure data transfer rates
- **Ping Tests**: Simulates ICMP ping using reachability testing
- **DNS Resolution**: Uses Java's InetAddress class for DNS lookups
- **Port Scanning**: Creates TCP socket connections to test port availability
- **Traceroute**: Simulates traceroute using ping with increasing TTL

### Performance Considerations
- **Background Processing**: All network operations run on background threads
- **Timeout Handling**: Proper timeout configuration to prevent hanging
- **Memory Management**: Efficient resource usage and cleanup
- **Battery Optimization**: Minimizes battery impact during testing

### Security Features
- **HTTPS Only**: Uses secure connections for speed tests
- **Permission Validation**: Proper runtime permission handling
- **Input Validation**: Validates user inputs before network operations
- **Error Handling**: Graceful handling of network errors and timeouts

## Troubleshooting

### Common Issues

**App crashes on startup**
- Ensure all permissions are granted
- Check if device has internet connectivity
- Restart the app and try again

**Speed test fails**
- Check internet connection
- Try again during off-peak hours
- Ensure no other apps are using heavy bandwidth

**Ping test shows timeouts**
- Verify the hostname/IP is correct
- Check if the target is reachable from your network
- Try with different hosts

**Port scanner shows no results**
- Some networks block port scanning
- Try scanning common ports only
- Check firewall settings

### Performance Tips
- Close other apps using internet during speed tests
- Use WiFi for more accurate results
- Run tests multiple times for better accuracy
- Avoid testing during peak network usage hours

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on different devices
5. Submit a pull request

### Code Style
- Follow Android coding conventions
- Use meaningful variable and method names
- Add comments for complex logic
- Ensure proper error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, questions, or feature requests:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review the app's help documentation

## Version History

### Version 1.0
- Initial release
- Speed test functionality
- Network information display
- Ping test capabilities
- DNS lookup features
- Port scanning tools
- Traceroute functionality
- Modern Material Design UI

---

**Note**: This app is designed for educational and diagnostic purposes. Always respect network policies and use responsibly. Some features may be restricted on certain networks or devices.