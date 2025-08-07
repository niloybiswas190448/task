package com.internettools.analyzer;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class SpeedTestActivity extends AppCompatActivity {
    
    private TextView downloadSpeedText, uploadSpeedText, pingText, statusText;
    private ProgressBar progressBar;
    private Button startTestButton;
    private ExecutorService executor;
    private Handler mainHandler;
    
    private static final String[] TEST_URLS = {
        "https://httpbin.org/bytes/1024",
        "https://httpbin.org/bytes/2048",
        "https://httpbin.org/bytes/4096"
    };
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_speed_test);
        
        initializeViews();
        executor = Executors.newCachedThreadPool();
        mainHandler = new Handler(Looper.getMainLooper());
    }
    
    private void initializeViews() {
        downloadSpeedText = findViewById(R.id.download_speed_text);
        uploadSpeedText = findViewById(R.id.upload_speed_text);
        pingText = findViewById(R.id.ping_text);
        statusText = findViewById(R.id.status_text);
        progressBar = findViewById(R.id.progress_bar);
        startTestButton = findViewById(R.id.start_test_button);
        
        startTestButton.setOnClickListener(v -> startSpeedTest());
    }
    
    private void startSpeedTest() {
        startTestButton.setEnabled(false);
        progressBar.setVisibility(View.VISIBLE);
        statusText.setText("Starting speed test...");
        
        executor.execute(() -> {
            // Test ping first
            testPing();
            
            // Test download speed
            testDownloadSpeed();
            
            // Test upload speed
            testUploadSpeed();
            
            mainHandler.post(() -> {
                startTestButton.setEnabled(true);
                progressBar.setVisibility(View.GONE);
                statusText.setText("Speed test completed!");
            });
        });
    }
    
    private void testPing() {
        try {
            long startTime = System.currentTimeMillis();
            URL url = new URL("https://httpbin.org/get");
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(5000);
            connection.setRequestMethod("GET");
            
            int responseCode = connection.getResponseCode();
            long endTime = System.currentTimeMillis();
            
            if (responseCode == 200) {
                long pingTime = endTime - startTime;
                mainHandler.post(() -> pingText.setText("Ping: " + pingTime + " ms"));
            }
            
            connection.disconnect();
        } catch (IOException e) {
            mainHandler.post(() -> pingText.setText("Ping: Failed"));
        }
    }
    
    private void testDownloadSpeed() {
        mainHandler.post(() -> statusText.setText("Testing download speed..."));
        
        long totalBytes = 0;
        long startTime = System.currentTimeMillis();
        
        for (String testUrl : TEST_URLS) {
            try {
                URL url = new URL(testUrl);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(10000);
                
                InputStream inputStream = connection.getInputStream();
                byte[] buffer = new byte[8192];
                int bytesRead;
                
                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    totalBytes += bytesRead;
                }
                
                inputStream.close();
                connection.disconnect();
                
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        
        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;
        
        if (duration > 0) {
            double speedMbps = (totalBytes * 8.0) / (1024 * 1024 * duration / 1000.0);
            mainHandler.post(() -> downloadSpeedText.setText(
                String.format("Download: %.2f Mbps", speedMbps)));
        }
    }
    
    private void testUploadSpeed() {
        mainHandler.post(() -> statusText.setText("Testing upload speed..."));
        
        long totalBytes = 0;
        long startTime = System.currentTimeMillis();
        
        try {
            URL url = new URL("https://httpbin.org/post");
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setDoOutput(true);
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(10000);
            
            // Create test data
            byte[] testData = new byte[1024 * 1024]; // 1MB
            for (int i = 0; i < testData.length; i++) {
                testData[i] = (byte) (i % 256);
            }
            
            OutputStream outputStream = connection.getOutputStream();
            outputStream.write(testData);
            outputStream.flush();
            outputStream.close();
            
            totalBytes = testData.length;
            
            int responseCode = connection.getResponseCode();
            connection.disconnect();
            
            if (responseCode == 200) {
                long endTime = System.currentTimeMillis();
                long duration = endTime - startTime;
                
                if (duration > 0) {
                    double speedMbps = (totalBytes * 8.0) / (1024 * 1024 * duration / 1000.0);
                    mainHandler.post(() -> uploadSpeedText.setText(
                        String.format("Upload: %.2f Mbps", speedMbps)));
                }
            }
            
        } catch (IOException e) {
            mainHandler.post(() -> uploadSpeedText.setText("Upload: Failed"));
        }
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (executor != null) {
            executor.shutdown();
        }
    }
}