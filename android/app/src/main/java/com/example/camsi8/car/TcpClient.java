package com.example.camsi8.car;

import android.app.Activity;
import android.os.AsyncTask;
import android.os.StrictMode;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.concurrent.Semaphore;


public class TcpClient extends AsyncTask<Void, String, Void>{
    String TAG = "TCP";
    String dstAddress;
    int dstPort;
    String response = "";
    Socket socket = null;
    PrintWriter out;
    OutputStream output;
    BufferedReader in;
    ArrayList<String> roadMaps = null;
    ArrayAdapter<String> adapter = null;
    ConnectionActivity activity;
    TextView position = null;

    TcpClient(String addr, int port, ConnectionActivity actvt){
        dstAddress = addr;
        dstPort = port;
        activity = actvt;
    }

    @Override
    protected Void doInBackground(Void... arg0) {
        try {
            Log.i(TAG, "Before");
            publishProgress("progress");
            socket = new Socket();
            socket.connect(new InetSocketAddress(dstAddress, dstPort), 5000);
            Log.i(TAG, "After");
            publishProgress("stopprogress");
            output = socket.getOutputStream();
            out = new PrintWriter(output);
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        }
        catch (UnknownHostException e) {
            e.printStackTrace();
            response = "UnknownHostException: " + e.toString();
            Log.i(TAG, response);
        }
        catch (IOException e) {
            e.printStackTrace();
            response = "IOException: " + e.toString();
            Log.i(TAG, response);
        }
        finally {
            if(this.isConnected()){
                publishProgress("Deconnexion");
                if(in != null){
                    String msgReceive = null;
                    while(true){
                        try {
                            msgReceive = in.readLine();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                        if(msgReceive != null) {
                            Log.i(TAG, msgReceive);
                            if(msgReceive.startsWith("roadmaps=")){
                                String item = msgReceive.split("=")[1];
                                Log.i(TAG, "Start With, and item is " + item);
                                publishProgress("roadmaps", item);
                            }
                            else{
                                String item = msgReceive;
                                Log.i(TAG, "Item : " + item);
                                publishProgress("position", item);
                            }
                        }
                        if(msgReceive == null)
                            break;
                    }
                }
                Log.i(TAG, "End connection ! ");
                try {
                    if(socket.isConnected())
                        socket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            else
                response = "Not connected";
        }
        return null;
    }

    @Override
    protected void onPostExecute(Void result) {
        Log.i(TAG, "Connection stopped");
        publishProgress("stopprogress");
        activity.textResponse.setText(response);
        activity.connectionButton.setText("Connexion");
        super.onPostExecute(result);
    }

    @Override
    protected void onProgressUpdate(String... item) {
        super.onProgressUpdate(item);
        if(item[0].equals("Connexion") || item[0].equals("Deconnexion")){
            activity.connectionButton.setText(item[0]);
        }
        else if(item[0].equals("progress")){
            activity.spinner.setVisibility(View.VISIBLE);
            activity.getWindow().setFlags(WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE, WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE);
        }
        else if(item[0].equals("stopprogress")){
            activity.spinner.setVisibility(View.INVISIBLE);
            activity.getWindow().clearFlags(WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE);
        }
        else if(item[0].equals("position")){
            Log.i(TAG, "Position !");
            if(position != null)
                position.setText(item[1]);
        }
        else if(item[0].equals("roadmaps")){
            if(roadMaps != null){
                roadMaps.add(item[1]);
                adapter.notifyDataSetChanged();
            }
        }
    }

    public boolean isConnected(){
        if(socket == null)
            return false;
        else
            if(socket.isConnected())
                return true;
            else
                return false;
    }

    public void disconnect() throws IOException {
        try {
            socket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
        publishProgress("Connexion");
    }

    public boolean sendMessage(String msg){
        if(this.isConnected()){
            if (out != null && !out.checkError()) {
                Log.i(TAG, "SendMessage");
                out.print(msg);
                out.flush();
                return true;
            }
        }
        return false;
    }

    public boolean sendMessage(JSONObject msg){
        if(this.isConnected()){
            if (out != null && !out.checkError()) {
                Log.i(TAG, "SendMessage");
                out.print(msg);
                out.flush();
                return true;
            }
        }
        return false;
    }

    public void onCreateRoadmap(ArrayList <String> roadMaps, ArrayAdapter<String> adapter){
        this.roadMaps = roadMaps;
        this.adapter = adapter;
    }

    public void onCreateMain(TextView pos){
        this.position = pos;
    }

    public String getIp(){
        return String.valueOf(socket.getInetAddress());
    }

}
