package com.example.camsi8.car;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.webkit.WebView;

import org.json.JSONException;
import org.json.JSONObject;

import io.github.controlwear.virtual.joystick.android.JoystickView;

public class VideoActivity extends AppCompatActivity {

    private WebView streamWebView;
    private String URL = "http://rpi26:8080/stream_simple.html";
    private int speedCar, angleCar;
    private String TAG = "video ";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_video);
        angleCar = -1;
        speedCar = -1;

        JoystickView joystick = findViewById(R.id.joystick);

        streamWebView = findViewById(R.id.streamWebView);

        streamWebView.getSettings().setLoadWithOverviewMode(true);
        streamWebView.getSettings().setUseWideViewPort(true);
        if(Global.isConnected())
            URL = "http://" + Global.getIp() + ":8080/stream_simple.html";
        streamWebView.loadUrl(URL);

        //// JOYSTICK ////
        /****************/
        joystick.setOnMoveListener(new JoystickView.OnMoveListener() {
            @Override
            public void onMove(int angle, int strength) {
                int newAngle, newSpeed;
                JSONObject jsonMsg = new JSONObject();

                if(angle == 0 && strength == 0)
                    Global.sendMessage("stop", getApplicationContext());

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
                            Global.sendMessage(msg, getApplicationContext());
                        }
                    }
                }
            }
        });
        /*****************************/
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
