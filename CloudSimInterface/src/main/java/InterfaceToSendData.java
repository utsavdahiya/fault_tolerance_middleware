import com.google.gson.JsonObject;
import org.cloudbus.cloudsim.core.CloudSim;
import org.cloudsimplus.listeners.EventInfo;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

/** This class describes an interface which sends any data required by FTM such as the current parameters
    of the VMs and handles all requests such as creating another VM and allocating resources to it.
 */

public class InterfaceToSendData {
    private final CloudSim simulation;
    private final int TIME_TILL_TERMINATION = 10000; /* Random time as of now, very big time as discussed */
    private final String URL_OF_SERVER = "http://192.168.1.8:8000"; /* URL of server for all GET and POST */

    public static void main(String[] args) {
        new InterfaceToSendData();
    }

    private InterfaceToSendData(){
        simulation = new CloudSim();
        simulation.terminateAt(TIME_TILL_TERMINATION);

        simulation.addOnClockTickListener(this::onClickTickListener);
    }

    /**
     * This function is called at the passing of every single simulated second.
     * @param evtInfo - Contains the description of the event that triggered this listener. In this case,
     *                the passing of every second (simulated) is the trigger.
     */
    private void onClickTickListener(EventInfo evtInfo) {
        Runnable communicationRunnable = new Runnable() {
            @Override
            public void run() {
                try {
                    URL urlOfServer = new URL(URL_OF_SERVER);
                    HttpURLConnection connectionObject = (HttpURLConnection) urlOfServer.openConnection();
                    connectionObject.setRequestMethod("GET");
                    int responseCode = -1; //Response Code of the request like 200 for success and 404 for not found.
                    responseCode = connectionObject.getResponseCode();

                    BufferedReader input = null;
                    if(responseCode == HttpURLConnection.HTTP_OK) {
                        input = new BufferedReader(new InputStreamReader(connectionObject.getInputStream()));

                        String inputLine = "";
                        StringBuffer receivedMessage = new StringBuffer();

                        while (true) {
                            if (!((inputLine = input.readLine()) != null)) {
                                break;
                            }

                            receivedMessage.append(inputLine);
                        }

                        input.close();

                        //GETting message ends here.

                        JsonObject toBeSent = route(receivedMessage.toString());

                        //POSTing result starts here.
                    }else{
                        System.out.println("GET request didn't work" + responseCode);
                    }

                }catch (MalformedURLException e){
                    e.printStackTrace();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        };
    }

    /**
     * This function routes the message received to the appropriate function provided by CloudSim.
     * @param message - Contains the message received from FTM.
     * @return - returns a JsonObject with the appropriate data.
     */
    private JsonObject route(String message){
        return null;
    }
}
