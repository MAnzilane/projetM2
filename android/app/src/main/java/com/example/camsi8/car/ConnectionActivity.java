package com.example.camsi8.car;

import android.content.Intent;
import android.os.AsyncTask;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.RadioButton;
import android.widget.TextView;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.Socket;
import java.net.UnknownHostException;

import io.github.controlwear.virtual.joystick.android.JoystickView;

public class ConnectionActivity extends AppCompatActivity {

    public Button returnButton;
    public Button connectionButton, sendButton;
    private EditText portText, hostText, sendText;
    public TextView textResponse;
    private RadioButton rpi24Button, rpi26Button, hostButton;
    public ProgressBar spinner;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connection);

        returnButton = findViewById(R.id.returnButton);
        connectionButton = findViewById(R.id.connectionButton);
        sendButton = findViewById(R.id.sendButton);
        portText = findViewById(R.id.portText);
        hostText = findViewById(R.id.hostText);
        sendText = findViewById(R.id.sendText);
        textResponse = findViewById(R.id.textResponse);
        rpi24Button = findViewById(R.id.rpi24RadioButton);
        rpi26Button = findViewById(R.id.rpi26RadioButton);
        hostButton = findViewById(R.id.hostRadioButton);

        spinner= findViewById(R.id.progressBar);
        spinner.setVisibility(View.GONE);

        if(Global.isConnected())
            connectionButton.setText("Deconnexion");

        returnButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                final Intent mainActivity = new Intent(ConnectionActivity.this, MainActivity.class);
                startActivity(mainActivity);
            }
        });

        rpi24Button.setChecked(true);


        connectionButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String msg = "";
                String host = null;

                if(hostButton.isChecked()){
                    if (hostText.getText().toString().trim().length() == 0)
                        msg = "Entrez un Host";
                }

                if (portText.getText().toString().trim().length() == 0)
                    if(!msg.equals(""))
                        msg = msg + "\nEntrez un port";
                    else
                        msg = msg + "Entrez un port";

                Toast msgDisp = Toast.makeText(getBaseContext(), msg, Toast.LENGTH_SHORT);
                if(!msg.equals(""))
                    msgDisp.show();
                else{
                    if(hostButton.isChecked())
                        host = hostText.getText().toString();
                    else if(rpi24Button.isChecked())
                        host = "rpi24";
                    else
                        host = "rpi26";

                    Log.i("TCP", host);
                    if(Global.tcpClient == null){
                        Global.tcpClient = new TcpClient(
                                host,
                                Integer.parseInt(portText.getText().toString()),
                                ConnectionActivity.this);
                    }

                    if(Global.isConnected()){
                        try {
                            Global.tcpClient.disconnect();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                        Global.tcpClient = null;
                    }
                    else{
                        if(!Global.tcpClient.isCancelled())
                            Global.tcpClient = new TcpClient(
                                    host,
                                    Integer.parseInt(portText.getText().toString()),
                                     ConnectionActivity.this);
                        Global.tcpClient.execute();
                    }

                }
            }
        });

        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String msg = sendText.getText().toString();
                Global.tcpClient.sendMessage(msg);
            }
        });
    }
}
