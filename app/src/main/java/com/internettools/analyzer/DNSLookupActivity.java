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

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class DNSLookupActivity extends AppCompatActivity {
    
    private EditText domainInput;
    private Button lookupButton;
    private TextView resultText;
    private ScrollView scrollView;
    private ExecutorService executor;
    private Handler mainHandler;
    
    private static final String[] DEFAULT_DOMAINS = {
        "google.com", "facebook.com", "amazon.com", "netflix.com", "youtube.com"
    };
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dns_lookup);
        
        initializeViews();
        executor = Executors.newCachedThreadPool();
        mainHandler = new Handler(Looper.getMainLooper());
        
        // Set default domain
        domainInput.setText("google.com");
    }
    
    private void initializeViews() {
        domainInput = findViewById(R.id.domain_input);
        lookupButton = findViewById(R.id.lookup_button);
        resultText = findViewById(R.id.result_text);
        scrollView = findViewById(R.id.scroll_view);
        
        lookupButton.setOnClickListener(v -> startDNSLookup());
    }
    
    private void startDNSLookup() {
        String domain = domainInput.getText().toString().trim();
        if (domain.isEmpty()) {
            domain = "google.com";
        }
        
        lookupButton.setEnabled(false);
        resultText.setText("Looking up " + domain + "...\n");
        
        executor.execute(() -> {
            performDNSLookup(domain);
            mainHandler.post(() -> lookupButton.setEnabled(true));
        });
    }
    
    private void performDNSLookup(String domain) {
        StringBuilder result = new StringBuilder();
        result.append("DNS Lookup Results for: ").append(domain).append("\n");
        result.append("=====================================\n\n");
        
        try {
            // Get all IP addresses for the domain
            InetAddress[] addresses = InetAddress.getAllByName(domain);
            
            result.append("IP Addresses:\n");
            for (int i = 0; i < addresses.length; i++) {
                InetAddress address = addresses[i];
                result.append(i + 1).append(". ").append(address.getHostAddress());
                
                // Check if it's IPv4 or IPv6
                if (address.getHostAddress().contains(":")) {
                    result.append(" (IPv6)");
                } else {
                    result.append(" (IPv4)");
                }
                result.append("\n");
            }
            
            result.append("\nCanonical Hostname: ").append(addresses[0].getCanonicalHostName()).append("\n");
            
            // Test reachability
            result.append("\nReachability Test:\n");
            for (InetAddress address : addresses) {
                try {
                    long startTime = System.currentTimeMillis();
                    boolean reachable = address.isReachable(3000);
                    long endTime = System.currentTimeMillis();
                    
                    if (reachable) {
                        result.append("✓ ").append(address.getHostAddress())
                              .append(" - Reachable (").append(endTime - startTime).append("ms)\n");
                    } else {
                        result.append("✗ ").append(address.getHostAddress()).append(" - Unreachable\n");
                    }
                } catch (Exception e) {
                    result.append("✗ ").append(address.getHostAddress())
                          .append(" - Error: ").append(e.getMessage()).append("\n");
                }
            }
            
            // Additional DNS information
            result.append("\nDNS Information:\n");
            result.append("Hostname: ").append(addresses[0].getHostName()).append("\n");
            result.append("Is Loopback: ").append(addresses[0].isLoopbackAddress()).append("\n");
            result.append("Is Link Local: ").append(addresses[0].isLinkLocalAddress()).append("\n");
            result.append("Is Site Local: ").append(addresses[0].isSiteLocalAddress()).append("\n");
            result.append("Is Multicast: ").append(addresses[0].isMulticastAddress()).append("\n");
            
        } catch (UnknownHostException e) {
            result.append("Error: Unable to resolve domain name\n");
            result.append("Details: ").append(e.getMessage()).append("\n");
        } catch (Exception e) {
            result.append("Unexpected error: ").append(e.getMessage()).append("\n");
        }
        
        final String finalResult = result.toString();
        mainHandler.post(() -> {
            resultText.setText(finalResult);
            scrollView.fullScroll(View.FOCUS_DOWN);
        });
    }
    
    public void lookupDefaultDomains(View view) {
        lookupButton.setEnabled(false);
        resultText.setText("Looking up default domains...\n");
        
        executor.execute(() -> {
            StringBuilder result = new StringBuilder();
            result.append("Default Domains DNS Lookup\n");
            result.append("==========================\n\n");
            
            for (String domain : DEFAULT_DOMAINS) {
                result.append("Domain: ").append(domain).append("\n");
                result.append("----------------------------------------\n");
                
                try {
                    InetAddress[] addresses = InetAddress.getAllByName(domain);
                    
                    for (InetAddress address : addresses) {
                        result.append("IP: ").append(address.getHostAddress());
                        if (address.getHostAddress().contains(":")) {
                            result.append(" (IPv6)");
                        } else {
                            result.append(" (IPv4)");
                        }
                        result.append("\n");
                    }
                    
                    // Test reachability
                    try {
                        long startTime = System.currentTimeMillis();
                        boolean reachable = addresses[0].isReachable(2000);
                        long endTime = System.currentTimeMillis();
                        
                        if (reachable) {
                            result.append("Status: ✓ Reachable (").append(endTime - startTime).append("ms)\n");
                        } else {
                            result.append("Status: ✗ Unreachable\n");
                        }
                    } catch (Exception e) {
                        result.append("Status: ✗ Error testing reachability\n");
                    }
                    
                } catch (UnknownHostException e) {
                    result.append("Status: ✗ Unable to resolve\n");
                }
                
                result.append("\n");
                
                // Update UI after each domain
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
            
            mainHandler.post(() -> lookupButton.setEnabled(true));
        });
    }
    
    public void reverseDNSLookup(View view) {
        String domain = domainInput.getText().toString().trim();
        if (domain.isEmpty()) {
            domain = "8.8.8.8";
        }
        
        lookupButton.setEnabled(false);
        resultText.setText("Performing reverse DNS lookup for " + domain + "...\n");
        
        executor.execute(() -> {
            StringBuilder result = new StringBuilder();
            result.append("Reverse DNS Lookup for: ").append(domain).append("\n");
            result.append("=====================================\n\n");
            
            try {
                InetAddress address = InetAddress.getByName(domain);
                result.append("IP Address: ").append(address.getHostAddress()).append("\n");
                result.append("Hostname: ").append(address.getHostName()).append("\n");
                result.append("Canonical Hostname: ").append(address.getCanonicalHostName()).append("\n");
                
                // Additional information
                result.append("\nAddress Information:\n");
                result.append("Is Loopback: ").append(address.isLoopbackAddress()).append("\n");
                result.append("Is Link Local: ").append(address.isLinkLocalAddress()).append("\n");
                result.append("Is Site Local: ").append(address.isSiteLocalAddress()).append("\n");
                result.append("Is Multicast: ").append(address.isMulticastAddress()).append("\n");
                
            } catch (UnknownHostException e) {
                result.append("Error: Unable to perform reverse DNS lookup\n");
                result.append("Details: ").append(e.getMessage()).append("\n");
            }
            
            final String finalResult = result.toString();
            mainHandler.post(() -> {
                resultText.setText(finalResult);
                scrollView.fullScroll(View.FOCUS_DOWN);
                lookupButton.setEnabled(true);
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