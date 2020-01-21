package com.example.camsi8.car;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.os.StrictMode;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.AbsoluteLayout;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.VideoView;

import org.json.JSONException;
import org.json.JSONObject;

import io.github.controlwear.virtual.joystick.android.JoystickView;

public class MainActivity extends AppCompatActivity {
    private Button connectionButton, scenarioButton, stopButton, syncButton, button_angle_test, videoButton;
    private ImageButton button_rotate_left, button_rotate_right, downButton, leftButton, rightButton, upButton, calibrateLeftButton, calibrateRightButton, left90, right90, button_reset;
    private TextView positionText;
    private String TAG = "main";
    private int speedCar, angleCar;

    @Override
    protected void onResume() {
        super.onResume();

        if(Global.isConnected()) {
            Global.tcpClient.onCreateMain(positionText);
            Log.i(TAG, "Position text OK!");
        }
        else
            Log.i(TAG, "Position text bad");
    }

    @SuppressLint("ClickableViewAccessibility")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);


        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);

        connectionButton = findViewById(R.id.connectionButton);
        downButton = findViewById(R.id.downButton);
        leftButton = findViewById(R.id.leftButton);
        rightButton = findViewById(R.id.rightButton);
        left90 = findViewById(R.id.left90);
        right90 = findViewById(R.id.right90);
        upButton = findViewById(R.id.upButton);
        scenarioButton = findViewById(R.id.scenarioButton);
        stopButton = findViewById(R.id.stopButton);
        calibrateLeftButton = findViewById(R.id.calibrateLeftButton);
        calibrateRightButton = findViewById(R.id.calibrateRightButton);
        syncButton = findViewById(R.id.syncButton);
        button_rotate_left = findViewById(R.id.button_rotate_left);
        button_rotate_right = findViewById(R.id.button_rotate_right);
        button_angle_test = findViewById(R.id.button_angle_test);
        button_reset = findViewById(R.id.button_reset);
        videoButton = findViewById(R.id.videoButton);
        positionText = findViewById(R.id.positionTextView);

        JoystickView joystick = findViewById(R.id.joystick);

        angleCar = -1;
        speedCar = -1;



         ////  Change Activity ////
        /************************/

        connectionButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                final Intent connectionActivity = new Intent(MainActivity.this, ConnectionActivity.class);
                startActivity(connectionActivity);
            }
        });

        scenarioButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                final Intent scenarioActivity = new Intent(MainActivity.this, ScenarioActivity.class);
                startActivity(scenarioActivity);
            }
        });

        button_angle_test.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                final Intent Angle_test_intent = new Intent(MainActivity.this, Angle_test.class);
                startActivity(Angle_test_intent);
            }
        });

        videoButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                final Intent videoIntent = new Intent(MainActivity.this, VideoActivity.class);
                startActivity(videoIntent);
            }
        });


        /*************************/



         //// JOYSTICK ////
        /****************/
        joystick.setOnMoveListener(new JoystickView.OnMoveListener() {
            @Override
            public void onMove(int angle, int strength) {
                if(Global.isConnected()){
                    int newAngle, newSpeed;
                    JSONObject jsonMsg = new JSONObject();

                    if(angle == 0 && strength == 0) {
                        try {
                            jsonMsg.put("ACTION", "stop");
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                        Global.sendMessage(jsonMsg, getApplicationContext());
                    }

                    else{
                        String msg = "Angle : " + angle + " Strength : " + strength;
                        Log.i(TAG,msg);

                        newAngle = calculAngle(strength, angle);
                        newSpeed = calculSpeed(strength, angle);
                        if(newAngle != angleCar){
                            angleCar = newAngle;
                            msg = "New Angle : " + newAngle;
                            Log.i(TAG, msg);
                            int temp = convertToAngle(angleCar);

                            try {
                                jsonMsg.put("ACTION", "set_angle");
                                jsonMsg.put("VALUE", temp);
                            } catch (JSONException e) {
                                e.printStackTrace();
                            }
                            Global.sendMessage(jsonMsg, getApplicationContext());
                        }
                        if(newSpeed != speedCar){
                            speedCar = newSpeed;
                            int temp = convertToSpeed(Math.abs(speedCar));
                            msg = "New Speed : " + speedCar;
                            Log.i(TAG, msg);
                            if(speedCar < 0){
                                try {
                                    jsonMsg.put("ACTION", "set_backward");
                                    jsonMsg.put("VALUE", temp);
                                } catch (JSONException e) {
                                    e.printStackTrace();
                                }
                                Global.sendMessage(jsonMsg, getApplicationContext());
                            }
                            else{
                                try {
                                    jsonMsg.put("ACTION", "set_forward");
                                    jsonMsg.put("VALUE", temp);
                                } catch (JSONException e) {
                                    e.printStackTrace();
                                }
                                Global.sendMessage(jsonMsg, getApplicationContext());
                            }
                        }
                    }
                }
            }
        });
        /*****************************/


        //// BUTTON ////
        /*************/
        syncButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "sync");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        stopButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "stop");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        rightButton.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                JSONObject jsonMsg = new JSONObject();
                if(event.getActionMasked() == MotionEvent.ACTION_DOWN){
                    try {
                        jsonMsg.put("ACTION", "right");
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Global.sendMessage(jsonMsg, getApplicationContext());
                }
                else if(event.getActionMasked() == MotionEvent.ACTION_UP){
                    try {
                        jsonMsg.put("ACTION", "home");
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Global.sendMessage(jsonMsg, getApplicationContext());
                }


                return true;
            }
        });

        leftButton.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                JSONObject jsonMsg = new JSONObject();
                if(event.getActionMasked() == MotionEvent.ACTION_DOWN) {
                    try {
                        jsonMsg.put("ACTION", "left");
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Global.sendMessage(jsonMsg, getApplicationContext());
                }
                else if(event.getActionMasked() == MotionEvent.ACTION_UP){
                    try {
                        jsonMsg.put("ACTION", "home");
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Global.sendMessage(jsonMsg, getApplicationContext());
                }

                return true;
            }
        });

        right90.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "right90");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        left90.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "left90");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());

            }
        });

        upButton.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                JSONObject jsonMsg = new JSONObject();

                if(event.getActionMasked() == MotionEvent.ACTION_DOWN) {
                    try {
                        jsonMsg.put("ACTION", "forward");
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Global.sendMessage(jsonMsg, getApplicationContext());
                }
                else if(event.getActionMasked() == MotionEvent.ACTION_UP) {
                    try {
                        jsonMsg.put("ACTION", "stop");
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Global.sendMessage(jsonMsg, getApplicationContext());
                }


                return true;
            }
        });

        downButton.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                JSONObject jsonMsg = new JSONObject();
                if(event.getActionMasked() == MotionEvent.ACTION_DOWN){
                    try {
                        jsonMsg.put("ACTION", "backward");
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Global.sendMessage(jsonMsg,getApplicationContext());
                }
                else if(event.getActionMasked() == MotionEvent.ACTION_UP) {
                    try {
                        jsonMsg.put("ACTION", "stop");
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Global.sendMessage(jsonMsg,getApplicationContext());
                }

                return true;
            }
        });

        button_rotate_left.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "rotate_left");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        button_rotate_right.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "rotate_right");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        button_reset.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "reset");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        calibrateLeftButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "offset-");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        calibrateRightButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "offset+");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });
    }

    private int calculAngle(int strength, int angle){
        double tempAngle = (double) angle;
        double tempStrength = (double) strength;

        return ((int) (Math.cos(tempAngle * Math.PI / 180) * tempStrength));
    }

    private int calculSpeed(int strength, int angle){
        double tempAngle = (double) angle;
        double tempStrength = (double) strength;

        return ((int) ((Math.sin(tempAngle * Math.PI / 180) * tempStrength)));
    }


    private int convertToAngle(int val){
        if(val >= -100 && val <=100){
            float valT = new Float(val);
            return ((int) (((valT + 100) / (100+100)) * (Global.MAXANGLE - Global.MINANGLE) + Global.MINANGLE));
        }

        return -1;
    }

    private int convertToSpeed(int val){
        //A = 0 B = 100,  C = 24 - D = 102
        //Y = (X-A)/(B-A) * (D-C) + C

        if(val >= 0 && val <=100){
            float valT = new Float(val);
            return ((int) ((valT / 100) * (Global.MAXSPEED - Global.MINSPEED) + Global.MINSPEED));
        }

        return -1;
    }
}
