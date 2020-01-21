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
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.TextView;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

public class ScenarioActivity extends AppCompatActivity {
    private Button autoButton, lineButton, roadmapButton, returnButton, updateButton, colorButton, homeButton;
    private ImageButton stopImageButton;
    private ListView listView;
    private TextView sec;

    private String TAG = "scenario";
    private ArrayList<String> roadMaps = new ArrayList<String>();
    private View selection;
    private String selected;
    private ArrayAdapter<String> adapter, adapter_color;
    private Spinner color_spinner;

    @Override
    protected void onResume() {
        super.onResume();
        if(Global.isConnected()){
            Global.tcpClient.onCreateRoadmap(roadMaps, adapter);
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_scenario);

        updateButton = findViewById(R.id.updateButton);
        roadmapButton = findViewById(R.id.roadmapButton);
        autoButton = findViewById(R.id.autoButton);
        lineButton = findViewById(R.id.lineButton);
        listView = findViewById(R.id.listView);
        sec = findViewById(R.id.secText);
        returnButton = findViewById(R.id.returnButton);
        colorButton  = findViewById(R.id.colorButton);
        homeButton = findViewById(R.id.homeButton);
        stopImageButton = findViewById(R.id.stopImageButton);

        adapter = new ArrayAdapter<String>(ScenarioActivity.this,
                android.R.layout.simple_list_item_1, roadMaps);
        listView.setAdapter(adapter);



        color_spinner = findViewById(R.id.color_spinner);
        ArrayAdapter<CharSequence> adapter_color = ArrayAdapter.createFromResource(this,
                R.array.color_array, android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        color_spinner.setAdapter(adapter_color);

        stopImageButton.setOnClickListener(new View.OnClickListener() {
            @Override
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

        homeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "go_home");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        updateButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "updateroadmaps");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        roadmapButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(selected != null){
                    JSONObject jsonMsg = new JSONObject();
                    try {
                        jsonMsg.put("ACTION", "set_roadmap");
                        jsonMsg.put("VALUE", selected);
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Global.sendMessage(jsonMsg, getApplicationContext());
                }
            }
        });

        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                if(selection != null)
                    selection.setBackgroundColor(Color.WHITE);

                selection = adapter.getView(position, view, parent);
                selection.setBackgroundColor(Color.RED);
                selected = (String) listView.getItemAtPosition(position);
            }
        });

        returnButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                final Intent mainActivity = new Intent(ScenarioActivity.this, MainActivity.class);
                startActivity(mainActivity);
            }
        });

        autoButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String msg = "Auto Button : " + autoButton.getText();
                Log.i(TAG, msg);
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "auto_pilot");
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });

        lineButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                JSONObject jsonMsg = new JSONObject();
                if(sec.getText().length() != 0) {
                    try {
                        jsonMsg.put("ACTION", "line");
                        jsonMsg.put("VALUE", sec.getText());
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Global.sendMessage(jsonMsg, getApplicationContext());
                }
            }
        });

        colorButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.i(TAG, "color_scenario debug: " + color_spinner.getSelectedItem().toString());
                JSONObject jsonMsg = new JSONObject();
                try {
                    jsonMsg.put("ACTION", "color");
                    jsonMsg.put("VALUE", color_spinner.getSelectedItem().toString());
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                Global.sendMessage(jsonMsg, getApplicationContext());
            }
        });
    }
}
