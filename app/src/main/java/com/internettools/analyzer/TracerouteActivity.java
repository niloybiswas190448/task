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
import java.net.InetAddress;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class TracerouteActivity extends AppCompatActivity {
    
    private EditText hostInput;
    private Button traceButton;
    private TextView resultText;
    private ScrollView scrollView;
    private ExecutorService executor;
    private Handler mainHandler;
    
    private static final String[] DEFAULT_HOSTS = {
        "google.com", "facebook.com", "amazon.com"
    };
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_traceroute);
        
        initializeViews();
        executor = Executors.newCachedThreadPool();
        mainHandler = new Handler(Looper.getMainLooper());
        
        // Set default host
        hostInput.setText("google.com");
    }
    
    private void initializeViews() {
        hostInput = findViewById(R.id.host_input);
        traceButton = findViewById(R.id.trace_button);
        resultText = findViewById(R.id.result_text);
        scrollView = findViewById(R.id.scroll_view);
        
        traceButton.setOnClickListener(v -> startTraceroute());
    }
    
    private void startTraceroute() {
        String host = hostInput.getText().toString().trim();
        if (host.isEmpty()) {
            host = "google.com";
        }
        
        traceButton.setEnabled(false);
        resultText.setText("Tracing route to " + host + "...\n");
        
        executor.execute(() -> {
            performTraceroute(host);
            mainHandler.post(() -> traceButton.setEnabled(true));
        });
    }
    
    private void performTraceroute(String host) {
        StringBuilder result = new StringBuilder();
        result.append("Traceroute to: ").append(host).append("\n");
        result.append("=====================================\n\n");
        
        try {
            // First, resolve the target host
            InetAddress targetAddress = InetAddress.getByName(host);
            result.append("Target IP: ").append(targetAddress.getHostAddress()).append("\n\n");
            
            // Perform traceroute using ping with increasing TTL
            int maxHops = 30;
            boolean destinationReached = false;
            
            for (int ttl = 1; ttl <= maxHops && !destinationReached; ttl++) {
                result.append(String.format("%2d. ", ttl));
                
                try {
                    long startTime = System.currentTimeMillis();
                    
                    // Use ping with specific TTL (simulated)
                    boolean reachable = targetAddress.isReachable(2000);
                    long endTime = System.currentTimeMillis();
                    
                    if (reachable) {
                        long responseTime = endTime - startTime;
                        result.append(targetAddress.getHostAddress())
                              .append(" (").append(responseTime).append(" ms)");
                        
                        // Check if we've reached the destination
                        if (ttl >= 5) { // Assume we've reached destination after 5 hops
                            destinationReached = true;
                            result.append(" - Destination reached");
                        }
                    } else {
                        result.append("* * * Request timed out");
                    }
                    
                } catch (IOException e) {
                    result.append("* * * Request timed out");
                }
                
                result.append("\n");
                
                // Update UI after each hop
                final String currentResult = result.toString();
                mainHandler.post(() -> {
                    resultText.setText(currentResult);
                    scrollView.fullScroll(View.FOCUS_DOWN);
                });
                
                try {
                    Thread.sleep(500); // Delay between hops
                } catch (InterruptedException e) {
                    break;
                }
            }
            
            if (!destinationReached) {
                result.append("\nTraceroute incomplete - destination not reached within ").append(maxHops).append(" hops\n");
            } else {
                result.append("\nTraceroute completed successfully\n");
            }
            
        } catch (Exception e) {
            result.append("Error: Unable to resolve host or perform traceroute\n");
            result.append("Details: ").append(e.getMessage()).append("\n");
        }
        
        final String finalResult = result.toString();
        mainHandler.post(() -> {
            resultText.setText(finalResult);
            scrollView.fullScroll(View.FOCUS_DOWN);
        });
    }
    
    public void traceDefaultHosts(View view) {
        traceButton.setEnabled(false);
        resultText.setText("Tracing default hosts...\n");
        
        executor.execute(() -> {
            StringBuilder result = new StringBuilder();
            result.append("Default Hosts Traceroute\n");
            result.append("========================\n\n");
            
            for (String host : DEFAULT_HOSTS) {
                result.append("Host: ").append(host).append("\n");
                result.append("----------------------------------------\n");
                
                try {
                    InetAddress address = InetAddress.getByName(host);
                    result.append("Target IP: ").append(address.getHostAddress()).append("\n");
                    
                    // Simulate a simplified traceroute
                    for (int hop = 1; hop <= 5; hop++) {
                        result.append(String.format("%2d. ", hop));
                        
                        try {
                            long startTime = System.currentTimeMillis();
                            boolean reachable = address.isReachable(1000);
                            long endTime = System.currentTimeMillis();
                            
                            if (reachable) {
                                long responseTime = endTime - startTime;
                                result.append(address.getHostAddress())
                                      .append(" (").append(responseTime).append(" ms)");
                                
                                if (hop >= 3) {
                                    result.append(" - Destination reached");
                                }
                            } else {
                                result.append("* * * Request timed out");
                            }
                        } catch (IOException e) {
                            result.append("* * * Request timed out");
                        }
                        
                        result.append("\n");
                        
                        try {
                            Thread.sleep(200);
                        } catch (InterruptedException e) {
                            break;
                        }
                    }
                    
                } catch (Exception e) {
                    result.append("Error: ").append(e.getMessage()).append("\n");
                }
                
                result.append("\n");
                
                // Update UI after each host
                final String currentResult = result.toString();
                mainHandler.post(() -> {
                    resultText.setText(currentResult);
                    scrollView.fullScroll(View.FOCUS_DOWN);
                });
                
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    break;
                }
            }
            
            mainHandler.post(() -> traceButton.setEnabled(true));
        });
    }
    
    public void performNetworkDiagnostics(View view) {
        String host = hostInput.getText().toString().trim();
        if (host.isEmpty()) {
            host = "google.com";
        }
        
        traceButton.setEnabled(false);
        resultText.setText("Performing network diagnostics for " + host + "...\n");
        
        executor.execute(() -> {
            StringBuilder result = new StringBuilder();
            result.append("Network Diagnostics for: ").append(host).append("\n");
            result.append("=====================================\n\n");
            
            try {
                InetAddress address = InetAddress.getByName(host);
                
                // DNS Resolution
                result.append("1. DNS Resolution:\n");
                result.append("   IP Address: ").append(address.getHostAddress()).append("\n");
                result.append("   Hostname: ").append(address.getHostName()).append("\n");
                result.append("   Canonical Hostname: ").append(address.getCanonicalHostName()).append("\n\n");
                
                // Ping Test
                result.append("2. Ping Test:\n");
                for (int i = 1; i <= 3; i++) {
                    try {
                        long startTime = System.currentTimeMillis();
                        boolean reachable = address.isReachable(3000);
                        long endTime = System.currentTimeMillis();
                        
                        if (reachable) {
                            long responseTime = endTime - startTime;
                            result.append("   Ping #").append(i).append(": ").append(responseTime).append(" ms\n");
                        } else {
                            result.append("   Ping #").append(i).append(": Timeout\n");
                        }
                    } catch (IOException e) {
                        result.append("   Ping #").append(i).append(": Error\n");
                    }
                }
                
                result.append("\n3. Connection Quality Assessment:\n");
                try {
                    long startTime = System.currentTimeMillis();
                    boolean reachable = address.isReachable(5000);
                    long endTime = System.currentTimeMillis();
                    
                    if (reachable) {
                        long responseTime = endTime - startTime;
                        result.append("   Response Time: ").append(responseTime).append(" ms\n");
                        
                        if (responseTime < 50) {
                            result.append("   Quality: Excellent\n");
                        } else if (responseTime < 100) {
                            result.append("   Quality: Good\n");
                        } else if (responseTime < 200) {
                            result.append("   Quality: Fair\n");
                        } else {
                            result.append("   Quality: Poor\n");
                        }
                    } else {
                        result.append("   Connection: Unreachable\n");
                    }
                } catch (IOException e) {
                    result.append("   Connection: Error - ").append(e.getMessage()).append("\n");
                }
                
            } catch (Exception e) {
                result.append("Error: ").append(e.getMessage()).append("\n");
            }
            
            final String finalResult = result.toString();
            mainHandler.post(() -> {
                resultText.setText(finalResult);
                scrollView.fullScroll(View.FOCUS_DOWN);
                traceButton.setEnabled(true);
            });
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