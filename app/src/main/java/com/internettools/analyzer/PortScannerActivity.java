package com.internettools.analyzer;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ScrollView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class PortScannerActivity extends AppCompatActivity {
    
    private EditText hostInput;
    private Button scanButton;
    private TextView resultText;
    private ScrollView scrollView;
    private ExecutorService executor;
    private Handler mainHandler;
    
    private static final int[] COMMON_PORTS = {
        21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443
    };
    
    private static final String[] PORT_SERVICES = {
        "FTP", "SSH", "Telnet", "SMTP", "DNS", "HTTP", "POP3", "IMAP", 
        "HTTPS", "IMAPS", "POP3S", "HTTP-Alt", "HTTPS-Alt"
    };
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_port_scanner);
        
        initializeViews();
        executor = Executors.newCachedThreadPool();
        mainHandler = new Handler(Looper.getMainLooper());
        
        // Set default host
        hostInput.setText("google.com");
    }
    
    private void initializeViews() {
        hostInput = findViewById(R.id.host_input);
        scanButton = findViewById(R.id.scan_button);
        resultText = findViewById(R.id.result_text);
        scrollView = findViewById(R.id.scroll_view);
        
        scanButton.setOnClickListener(v -> startPortScan());
    }
    
    private void startPortScan() {
        String host = hostInput.getText().toString().trim();
        if (host.isEmpty()) {
            host = "google.com";
        }
        
        scanButton.setEnabled(false);
        resultText.setText("Scanning ports on " + host + "...\n");
        
        executor.execute(() -> {
            performPortScan(host);
            mainHandler.post(() -> scanButton.setEnabled(true));
        });
    }
    
    private void performPortScan(String host) {
        StringBuilder result = new StringBuilder();
        result.append("Port Scan Results for: ").append(host).append("\n");
        result.append("=====================================\n\n");
        
        int openPorts = 0;
        int totalPorts = COMMON_PORTS.length;
        
        for (int i = 0; i < COMMON_PORTS.length; i++) {
            int port = COMMON_PORTS[i];
            String service = PORT_SERVICES[i];
            
            result.append("Scanning port ").append(port).append(" (").append(service).append(")... ");
            
            boolean isOpen = isPortOpen(host, port);
            
            if (isOpen) {
                result.append("✓ OPEN\n");
                openPorts++;
            } else {
                result.append("✗ CLOSED\n");
            }
            
            // Update UI after each port
            final String currentResult = result.toString();
            mainHandler.post(() -> {
                resultText.setText(currentResult);
                scrollView.fullScroll(View.FOCUS_DOWN);
            });
            
            try {
                Thread.sleep(100); // Small delay to avoid overwhelming the network
            } catch (InterruptedException e) {
                break;
            }
        }
        
        // Summary
        result.append("\nScan Summary:\n");
        result.append("=============\n");
        result.append("Total ports scanned: ").append(totalPorts).append("\n");
        result.append("Open ports: ").append(openPorts).append("\n");
        result.append("Closed ports: ").append(totalPorts - openPorts).append("\n");
        
        if (openPorts > 0) {
            result.append("\nOpen ports found:\n");
            for (int i = 0; i < COMMON_PORTS.length; i++) {
                if (isPortOpen(host, COMMON_PORTS[i])) {
                    result.append("• Port ").append(COMMON_PORTS[i])
                          .append(" (").append(PORT_SERVICES[i]).append(")\n");
                }
            }
        }
        
        final String finalResult = result.toString();
        mainHandler.post(() -> {
            resultText.setText(finalResult);
            scrollView.fullScroll(View.FOCUS_DOWN);
        });
    }
    
    private boolean isPortOpen(String host, int port) {
        Socket socket = null;
        try {
            socket = new Socket();
            socket.connect(new InetSocketAddress(host, port), 2000); // 2 second timeout
            return true;
        } catch (IOException e) {
            return false;
        } finally {
            if (socket != null) {
                try {
                    socket.close();
                } catch (IOException e) {
                    // Ignore
                }
            }
        }
    }
    
    public void scanCustomPorts(View view) {
        String host = hostInput.getText().toString().trim();
        if (host.isEmpty()) {
            host = "google.com";
        }
        
        scanButton.setEnabled(false);
        resultText.setText("Scanning custom port range on " + host + "...\n");
        
        executor.execute(() -> {
            StringBuilder result = new StringBuilder();
            result.append("Custom Port Range Scan for: ").append(host).append("\n");
            result.append("=====================================\n\n");
            
            // Scan ports 80-90 (common web ports)
            int openPorts = 0;
            for (int port = 80; port <= 90; port++) {
                result.append("Scanning port ").append(port).append("... ");
                
                boolean isOpen = isPortOpen(host, port);
                
                if (isOpen) {
                    result.append("✓ OPEN\n");
                    openPorts++;
                } else {
                    result.append("✗ CLOSED\n");
                }
                
                // Update UI after each port
                final String currentResult = result.toString();
                mainHandler.post(() -> {
                    resultText.setText(currentResult);
                    scrollView.fullScroll(View.FOCUS_DOWN);
                });
                
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    break;
                }
            }
            
            result.append("\nCustom Scan Summary:\n");
            result.append("===================\n");
            result.append("Ports scanned: 80-90\n");
            result.append("Open ports: ").append(openPorts).append("\n");
            
            final String finalResult = result.toString();
            mainHandler.post(() -> {
                resultText.setText(finalResult);
                scrollView.fullScroll(View.FOCUS_DOWN);
                scanButton.setEnabled(true);
            });
        });
    }
    
    public void scanDefaultHosts(View view) {
        scanButton.setEnabled(false);
        resultText.setText("Scanning default hosts...\n");
        
        String[] defaultHosts = {"google.com", "facebook.com", "amazon.com"};
        
        executor.execute(() -> {
            StringBuilder result = new StringBuilder();
            result.append("Default Hosts Port Scan\n");
            result.append("========================\n\n");
            
            for (String host : defaultHosts) {
                result.append("Host: ").append(host).append("\n");
                result.append("----------------------------------------\n");
                
                int openPorts = 0;
                for (int i = 0; i < COMMON_PORTS.length; i++) {
                    int port = COMMON_PORTS[i];
                    String service = PORT_SERVICES[i];
                    
                    boolean isOpen = isPortOpen(host, port);
                    
                    if (isOpen) {
                        result.append("✓ Port ").append(port).append(" (").append(service).append(")\n");
                        openPorts++;
                    }
                }
                
                if (openPorts == 0) {
                    result.append("No open ports found\n");
                }
                
                result.append("\n");
                
                // Update UI after each host
                final String currentResult = result.toString();
                mainHandler.post(() -> {
                    resultText.setText(currentResult);
                    scrollView.fullScroll(View.FOCUS_DOWN);
                });
                
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    break;
                }
            }
            
            mainHandler.post(() -> scanButton.setEnabled(true));
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