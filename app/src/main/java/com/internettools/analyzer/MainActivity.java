package com.internettools.analyzer;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.View;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

public class MainActivity extends AppCompatActivity {
    
    private static final int PERMISSION_REQUEST_CODE = 123;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Check and request permissions
        checkPermissions();
        
        // Set up click listeners for tool cards
        setupToolCards();
    }
    
    private void checkPermissions() {
        String[] permissions = {
            Manifest.permission.INTERNET,
            Manifest.permission.ACCESS_NETWORK_STATE,
            Manifest.permission.ACCESS_WIFI_STATE,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        };
        
        for (String permission : permissions) {
            if (ContextCompat.checkSelfPermission(this, permission) 
                != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, permissions, PERMISSION_REQUEST_CODE);
                break;
            }
        }
    }
    
    private void setupToolCards() {
        CardView speedTestCard = findViewById(R.id.speed_test_card);
        CardView networkInfoCard = findViewById(R.id.network_info_card);
        CardView pingTestCard = findViewById(R.id.ping_test_card);
        CardView dnsLookupCard = findViewById(R.id.dns_lookup_card);
        CardView portScannerCard = findViewById(R.id.port_scanner_card);
        CardView tracerouteCard = findViewById(R.id.traceroute_card);
        
        speedTestCard.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, SpeedTestActivity.class);
            startActivity(intent);
        });
        
        networkInfoCard.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, NetworkInfoActivity.class);
            startActivity(intent);
        });
        
        pingTestCard.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, PingTestActivity.class);
            startActivity(intent);
        });
        
        dnsLookupCard.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, DNSLookupActivity.class);
            startActivity(intent);
        });
        
        portScannerCard.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, PortScannerActivity.class);
            startActivity(intent);
        });
        
        tracerouteCard.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, TracerouteActivity.class);
            startActivity(intent);
        });
    }
    
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }
            
            if (!allGranted) {
                Toast.makeText(this, "Some permissions are required for full functionality", 
                             Toast.LENGTH_LONG).show();
            }
        }
    }
}