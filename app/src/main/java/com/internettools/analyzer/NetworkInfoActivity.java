package com.internettools.analyzer;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkInfo;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.io.IOException;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.Enumeration;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class NetworkInfoActivity extends AppCompatActivity {
    
    private TextView localIpText, publicIpText, networkTypeText, wifiInfoText, 
                     connectionInfoText, dnsInfoText;
    private ExecutorService executor;
    private Handler mainHandler;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_network_info);
        
        initializeViews();
        executor = Executors.newCachedThreadPool();
        mainHandler = new Handler(Looper.getMainLooper());
        
        loadNetworkInfo();
    }
    
    private void initializeViews() {
        localIpText = findViewById(R.id.local_ip_text);
        publicIpText = findViewById(R.id.public_ip_text);
        networkTypeText = findViewById(R.id.network_type_text);
        wifiInfoText = findViewById(R.id.wifi_info_text);
        connectionInfoText = findViewById(R.id.connection_info_text);
        dnsInfoText = findViewById(R.id.dns_info_text);
    }
    
    private void loadNetworkInfo() {
        // Get local network information
        getLocalNetworkInfo();
        
        // Get public IP address
        getPublicIpAddress();
        
        // Get DNS information
        getDNSInfo();
    }
    
    private void getLocalNetworkInfo() {
        ConnectivityManager connectivityManager = 
            (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        
        Network activeNetwork = connectivityManager.getActiveNetwork();
        if (activeNetwork != null) {
            NetworkCapabilities capabilities = 
                connectivityManager.getNetworkCapabilities(activeNetwork);
            
            if (capabilities != null) {
                String networkType = "Unknown";
                if (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)) {
                    networkType = "WiFi";
                    getWifiInfo();
                } else if (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR)) {
                    networkType = "Mobile Data";
                } else if (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)) {
                    networkType = "Ethernet";
                }
                
                networkTypeText.setText("Network Type: " + networkType);
                
                // Connection info
                StringBuilder connectionInfo = new StringBuilder();
                connectionInfo.append("Link Speed: ");
                if (capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)) {
                    connectionInfo.append("Internet Available\n");
                }
                if (capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)) {
                    connectionInfo.append("Validated Connection\n");
                }
                if (capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_NOT_METERED)) {
                    connectionInfo.append("Unmetered Connection\n");
                }
                
                connectionInfoText.setText(connectionInfo.toString());
            }
        }
        
        // Get local IP address
        try {
            Enumeration<NetworkInterface> networkInterfaces = 
                NetworkInterface.getNetworkInterfaces();
            
            while (networkInterfaces.hasMoreElements()) {
                NetworkInterface networkInterface = networkInterfaces.nextElement();
                Enumeration<InetAddress> addresses = networkInterface.getInetAddresses();
                
                while (addresses.hasMoreElements()) {
                    InetAddress address = addresses.nextElement();
                    if (!address.isLoopbackAddress() && address.getHostAddress().indexOf(':') < 0) {
                        localIpText.setText("Local IP: " + address.getHostAddress());
                        break;
                    }
                }
            }
        } catch (SocketException e) {
            localIpText.setText("Local IP: Unable to determine");
        }
    }
    
    private void getWifiInfo() {
        WifiManager wifiManager = (WifiManager) getApplicationContext()
            .getSystemService(Context.WIFI_SERVICE);
        
        if (wifiManager != null && wifiManager.isWifiEnabled()) {
            WifiInfo wifiInfo = wifiManager.getConnectionInfo();
            if (wifiInfo != null) {
                String ssid = wifiInfo.getSSID();
                if (ssid.startsWith("\"") && ssid.endsWith("\"")) {
                    ssid = ssid.substring(1, ssid.length() - 1);
                }
                
                int signalStrength = wifiInfo.getRssi();
                int frequency = wifiInfo.getFrequency();
                
                String wifiDetails = String.format("SSID: %s\nSignal Strength: %d dBm\nFrequency: %d MHz",
                    ssid, signalStrength, frequency);
                
                wifiInfoText.setText(wifiDetails);
            }
        } else {
            wifiInfoText.setText("WiFi: Not connected");
        }
    }
    
    private void getPublicIpAddress() {
        executor.execute(() -> {
            try {
                // Use multiple services for redundancy
                String[] ipServices = {
                    "https://api.ipify.org",
                    "https://httpbin.org/ip",
                    "https://icanhazip.com"
                };
                
                String publicIp = null;
                for (String service : ipServices) {
                    try {
                        java.net.URL url = new java.net.URL(service);
                        java.net.HttpURLConnection connection = 
                            (java.net.HttpURLConnection) url.openConnection();
                        connection.setConnectTimeout(5000);
                        connection.setReadTimeout(5000);
                        
                        java.io.BufferedReader reader = new java.io.BufferedReader(
                            new java.io.InputStreamReader(connection.getInputStream()));
                        String response = reader.readLine();
                        reader.close();
                        connection.disconnect();
                        
                        // Parse IP from response
                        if (response != null) {
                            if (response.contains("ip")) {
                                // JSON response
                                int start = response.indexOf("\"ip\":\"") + 6;
                                int end = response.indexOf("\"", start);
                                if (start > 5 && end > start) {
                                    publicIp = response.substring(start, end);
                                    break;
                                }
                            } else {
                                // Plain IP response
                                publicIp = response.trim();
                                break;
                            }
                        }
                    } catch (IOException e) {
                        continue;
                    }
                }
                
                final String finalIp = publicIp;
                mainHandler.post(() -> {
                    if (finalIp != null) {
                        publicIpText.setText("Public IP: " + finalIp);
                    } else {
                        publicIpText.setText("Public IP: Unable to determine");
                    }
                });
                
            } catch (Exception e) {
                mainHandler.post(() -> publicIpText.setText("Public IP: Error"));
            }
        });
    }
    
    private void getDNSInfo() {
        executor.execute(() -> {
            try {
                String[] dnsServers = {"8.8.8.8", "1.1.1.1", "208.67.222.222"};
                StringBuilder dnsInfo = new StringBuilder("DNS Servers:\n");
                
                for (String dns : dnsServers) {
                    try {
                        InetAddress address = InetAddress.getByName(dns);
                        long startTime = System.currentTimeMillis();
                        boolean reachable = address.isReachable(3000);
                        long endTime = System.currentTimeMillis();
                        
                        if (reachable) {
                            dnsInfo.append("• ").append(dns).append(" (")
                                   .append(endTime - startTime).append("ms)\n");
                        } else {
                            dnsInfo.append("• ").append(dns).append(" (unreachable)\n");
                        }
                    } catch (IOException e) {
                        dnsInfo.append("• ").append(dns).append(" (error)\n");
                    }
                }
                
                mainHandler.post(() -> dnsInfoText.setText(dnsInfo.toString()));
                
            } catch (Exception e) {
                mainHandler.post(() -> dnsInfoText.setText("DNS: Error retrieving information"));
            }
        });
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (executor != null) {
            executor.shutdown();
        }
    }
}