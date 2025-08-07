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

public class PingTestActivity extends AppCompatActivity {
    
    private EditText hostInput;
    private Button pingButton;
    private TextView resultText;
    private ScrollView scrollView;
    private ExecutorService executor;
    private Handler mainHandler;
    
    private static final String[] DEFAULT_HOSTS = {
        "google.com", "facebook.com", "amazon.com", "netflix.com", "youtube.com"
    };
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ping_test);
        
        initializeViews();
        executor = Executors.newCachedThreadPool();
        mainHandler = new Handler(Looper.getMainLooper());
        
        // Set default host
        hostInput.setText("google.com");
    }
    
    private void initializeViews() {
        hostInput = findViewById(R.id.host_input);
        pingButton = findViewById(R.id.ping_button);
        resultText = findViewById(R.id.result_text);
        scrollView = findViewById(R.id.scroll_view);
        
        pingButton.setOnClickListener(v -> startPingTest());
    }
    
    private void startPingTest() {
        String host = hostInput.getText().toString().trim();
        if (host.isEmpty()) {
            host = "google.com";
        }
        
        pingButton.setEnabled(false);
        resultText.setText("Pinging " + host + "...\n");
        
        executor.execute(() -> {
            performPingTest(host);
            mainHandler.post(() -> pingButton.setEnabled(true));
        });
    }
    
    private void performPingTest(String host) {
        StringBuilder result = new StringBuilder();
        result.append("Ping Test Results for: ").append(host).append("\n");
        result.append("=====================================\n\n");
        
        // Perform multiple pings
        int successfulPings = 0;
        long totalTime = 0;
        long minTime = Long.MAX_VALUE;
        long maxTime = 0;
        
        for (int i = 1; i <= 5; i++) {
            try {
                long startTime = System.currentTimeMillis();
                InetAddress address = InetAddress.getByName(host);
                boolean reachable = address.isReachable(5000); // 5 second timeout
                long endTime = System.currentTimeMillis();
                
                if (reachable) {
                    long pingTime = endTime - startTime;
                    successfulPings++;
                    totalTime += pingTime;
                    minTime = Math.min(minTime, pingTime);
                    maxTime = Math.max(maxTime, pingTime);
                    
                    result.append("Ping #").append(i).append(": ")
                          .append(pingTime).append(" ms\n");
                } else {
                    result.append("Ping #").append(i).append(": Timeout\n");
                }
                
                // Update UI after each ping
                final String currentResult = result.toString();
                mainHandler.post(() -> {
                    resultText.setText(currentResult);
                    scrollView.fullScroll(View.FOCUS_DOWN);
                });
                
                // Wait a bit between pings
                Thread.sleep(1000);
                
            } catch (IOException | InterruptedException e) {
                result.append("Ping #").append(i).append(": Error - ").append(e.getMessage()).append("\n");
            }
        }
        
        // Calculate statistics
        if (successfulPings > 0) {
            double avgTime = (double) totalTime / successfulPings;
            result.append("\nStatistics:\n");
            result.append("Successful pings: ").append(successfulPings).append("/5\n");
            result.append("Average time: ").append(String.format("%.1f", avgTime)).append(" ms\n");
            result.append("Minimum time: ").append(minTime).append(" ms\n");
            result.append("Maximum time: ").append(maxTime).append(" ms\n");
            
            // Connection quality assessment
            result.append("\nConnection Quality: ");
            if (avgTime < 50) {
                result.append("Excellent");
            } else if (avgTime < 100) {
                result.append("Good");
            } else if (avgTime < 200) {
                result.append("Fair");
            } else {
                result.append("Poor");
            }
        } else {
            result.append("\nAll pings failed. Host may be unreachable or network issues detected.");
        }
        
        final String finalResult = result.toString();
        mainHandler.post(() -> {
            resultText.setText(finalResult);
            scrollView.fullScroll(View.FOCUS_DOWN);
        });
    }
    
    public void pingDefaultHosts(View view) {
        pingButton.setEnabled(false);
        resultText.setText("Pinging default hosts...\n");
        
        executor.execute(() -> {
            StringBuilder result = new StringBuilder();
            result.append("Default Hosts Ping Test\n");
            result.append("========================\n\n");
            
            for (String host : DEFAULT_HOSTS) {
                result.append("Testing: ").append(host).append("\n");
                
                try {
                    long startTime = System.currentTimeMillis();
                    InetAddress address = InetAddress.getByName(host);
                    boolean reachable = address.isReachable(3000);
                    long endTime = System.currentTimeMillis();
                    
                    if (reachable) {
                        long pingTime = endTime - startTime;
                        result.append("✓ ").append(pingTime).append(" ms\n");
                    } else {
                        result.append("✗ Timeout\n");
                    }
                    
                } catch (IOException e) {
                    result.append("✗ Error: ").append(e.getMessage()).append("\n");
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
            
            mainHandler.post(() -> pingButton.setEnabled(true));
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