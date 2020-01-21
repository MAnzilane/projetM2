package com.example.camsi8.car;

import android.content.Intent;
import android.graphics.Color;
import android.support.annotation.ColorInt;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

public class Angle_test extends AppCompatActivity {
    private Button returnButton, button_stop, button_speed, button_left, button_right, button_forward, button_straight;
    private EditText et_speed;
    private TextView tv_exec_time;

    private long timer_start = -1, time_past;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_angle_test);

        returnButton    = findViewById(R.id.returnButton);
        button_stop     = findViewById(R.id.button_stop);
        button_speed    = findViewById(R.id.button_speed);
        button_left     = findViewById(R.id.button_left);
        button_right    = findViewById(R.id.button_right);
        button_forward  = findViewById(R.id.button_forward);
        button_straight = findViewById(R.id.button_straight);

        et_speed        = findViewById(R.id.et_speed);
        tv_exec_time    = findViewById(R.id.tv_exec_time);

        returnButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                final Intent mainActivity = new Intent(Angle_test.this, MainActivity.class);
                startActivity(mainActivity);
            }
        });

        button_stop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //stop timer
                if (timer_start != -1)
                    time_past = (System.currentTimeMillis() - timer_start) ;
                tv_exec_time.setText(String.valueOf(time_past));

                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "stop_angle");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        button_speed.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "set_speed");
                    jsonMsg.put("VALUE", et_speed.getText().toString());
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        button_left.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "left++");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        button_right.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "right++");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        button_straight.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "home_angle_test");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        button_forward.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //start timer
                timer_start = System.currentTimeMillis();
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "forward_angle");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });



    }
}
