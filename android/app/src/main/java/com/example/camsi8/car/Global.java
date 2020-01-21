package com.example.camsi8.car;

import android.content.Context;
import android.widget.Toast;

import org.json.JSONObject;

import java.util.concurrent.Semaphore;

public class Global{
    public static final float MAXSPEED = 102;
    public static final float MINSPEED = 24;
    public static final float MINANGLE = 0;
    public static final float MAXANGLE = 256;
    public static final float OFFSET = 128;


    public static TcpClient tcpClient;
    public static boolean tcpExecute;
    public static final Semaphore semaphore = new Semaphore(0);

    public static boolean sendMessage(String msg, Context ctxt){
        if(tcpClient != null)
            tcpClient.sendMessage(msg);
        else{
            Toast t = Toast.makeText(ctxt, "Aucune connexion", Toast.LENGTH_SHORT);
            t.show();
            return false;
        }

        return true;
    }

    public static boolean sendMessage(JSONObject msg, Context ctxt){
        if(tcpClient != null)
            tcpClient.sendMessage(msg);
        else{
            Toast t = Toast.makeText(ctxt, "Aucune connexion", Toast.LENGTH_SHORT);
            t.show();
            return false;
        }

        return true;
    }

    public static boolean isConnected(){
        if(tcpClient != null)
            return tcpClient.isConnected();
        return false;
    }

    public static String getIp(){
        if(isConnected())
            return tcpClient.getIp();
        return null;
    }
}
