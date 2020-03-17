import org.cloudbus.cloudsim.allocationpolicies.VmAllocationPolicySimple;
import org.cloudbus.cloudsim.brokers.DatacenterBroker;
import org.cloudbus.cloudsim.brokers.DatacenterBrokerSimple;
import org.cloudbus.cloudsim.cloudlets.Cloudlet;
import org.cloudbus.cloudsim.cloudlets.CloudletSimple;
import org.cloudbus.cloudsim.core.CloudSim;
import org.cloudbus.cloudsim.datacenters.Datacenter;
import org.cloudbus.cloudsim.datacenters.DatacenterSimple;
import org.cloudbus.cloudsim.hosts.Host;
import org.cloudbus.cloudsim.hosts.HostSimple;
import org.cloudbus.cloudsim.provisioners.PeProvisionerSimple;
import org.cloudbus.cloudsim.provisioners.ResourceProvisionerSimple;
import org.cloudbus.cloudsim.resources.Pe;
import org.cloudbus.cloudsim.resources.PeSimple;
import org.cloudbus.cloudsim.schedulers.cloudlet.CloudletSchedulerTimeShared;
import org.cloudbus.cloudsim.schedulers.vm.VmSchedulerTimeShared;
import org.cloudbus.cloudsim.utilizationmodels.UtilizationModel;
import org.cloudbus.cloudsim.utilizationmodels.UtilizationModelDynamic;
import org.cloudbus.cloudsim.utilizationmodels.UtilizationModelFull;
import org.cloudbus.cloudsim.vms.Vm;
import org.cloudbus.cloudsim.vms.VmSimple;
import org.cloudsimplus.listeners.EventInfo;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.Socket;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

/** This class describes an interface which sends any data required by FTM such as the current parameters
    of the VMs and handles all requests such as creating another VM and allocating resources to it.
 */
public class InterfaceToSendData {
    private final CloudSim simulation;
    private final DatacenterBroker broker;
    private final Datacenter datacenter;
    private final List<Vm> vmList = new ArrayList<>();
    private final List<Cloudlet> cloudletList = new ArrayList<>();
    private final int HOST_PES = 8; /* Random number as of now, TODO: Get this initially from FTM through a socket connection probably */
    private final int SCHEDULING_INTERVAL = 1; /* Random number as of now, TODO: Discuss */
    private final int NUMBER_OF_HOSTS = 2; /* Random number as of now, TODO: Get this initially from FTM through a socket connection probably */
    private final int TIME_TILL_TERMINATION = 10000; /* Random time as of now, very big time as discussed */
    private final String URL_OF_SERVER_GET = "http://192.168.1.8:8081"; /* URL of server for all GET*/
    private final String URL_OF_SERVER_POST = "http://192.168.1.8:8000"; /* URL of server for all POST*/

    public static void main(String[] args) {
        new InterfaceToSendData();
    }

    private InterfaceToSendData(){
        simulation = new CloudSim();
        simulation.terminateAt(TIME_TILL_TERMINATION);

        datacenter = createDatacenter();

        broker = new DatacenterBrokerSimple(simulation);



//        broker0.submitVmList(vmList);
//        broker0.submitCloudletList(cloudletList);

        Socket socket = new Socket("192.168.1.8",8888);
        PrintWriter outToServer = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()));
        outToServer.print(pairs[0].lat + " " + pairs[0].lang);

        simulation.addOnClockTickListener(this::onClickTickListener);

        simulation.start();
    }

    /**
     * This function creates a datacenter with a list of hosts.
     * @return Datacenter with the given hosts.
     */
    private Datacenter createDatacenter() {
        final List<Host> hostList = new ArrayList<>(NUMBER_OF_HOSTS);
        for(int i = 0; i < NUMBER_OF_HOSTS; i++) {
            Host host = createHost();
            hostList.add(host);
        }

        final Datacenter dc = new DatacenterSimple(simulation, hostList, new VmAllocationPolicySimple());
        dc.setSchedulingInterval(SCHEDULING_INTERVAL);
        return dc;
    }

    /**
     * This function creates a host with pes, RAM, storage and bandwidth.
     * @return Host with the given specs.
     */
    private Host createHost() {
        List<Pe> peList = new ArrayList<>(HOST_PES);

        for (int i = 0; i < HOST_PES; i++) {
            peList.add(new PeSimple(1000, new PeProvisionerSimple()));
        }

        final long ram = 2048; /* Random number as of now, TODO: Get this initially from FTM through a socket connection probably */
        final long bw = 10000; /* Random number as of now, TODO: Get this initially from FTM through a socket connection probably */
        final long storage = 10000; /* Random number as of now, TODO: Get this initially from FTM through a socket connection probably */
        Host host = new HostSimple(ram, bw, storage, peList);
        host
                .setRamProvisioner(new ResourceProvisionerSimple())
                .setBwProvisioner(new ResourceProvisionerSimple())
                .setVmScheduler(new VmSchedulerTimeShared());
        return host;
    }

    /**
     * This function creates a VM with the given specs as received from FTM.
     * @param message - Contains the specs sent by FTM.
     */
    private void createVm(JSONObject message){
        JSONArray vmArray = message.getJSONArray("VM");
        for(int i = 0; i < vmArray.length(); i++){
            JSONObject vmConfig = vmArray.getJSONObject(i);
            int mips = Integer.parseInt(vmConfig.getString("mips"));
            int pes = Integer.parseInt(vmConfig.getString("pes"));
            int ram = Integer.parseInt(vmConfig.getString("ram"));
            int bandwidth = Integer.parseInt(vmConfig.getString("bandwidth"));
            int size = Integer.parseInt(vmConfig.getString("size"));

            Vm vm = new VmSimple(mips,pes)
                    .setRam(ram).setBw(bandwidth).setSize(size)
                    .setCloudletScheduler(new CloudletSchedulerTimeShared());

            vmList.add(vm);
        }

        broker.submitVmList(vmList);
    }

    /**
     * This function updates an already created VM with the given specs as received from FTM.
     * @param message - Contains the specs sent by FTM.
     */
    private void updateVm(JSONObject message){
        JSONArray vmArray = message.getJSONArray("VM");
        JSONObject newVmConfig = vmArray.getJSONObject(0);
        int ram = Integer.parseInt(newVmConfig.getString("ram"));
        int bandwidth = Integer.parseInt(newVmConfig.getString("bandwidth"));
        int size = Integer.parseInt(newVmConfig.getString("size"));

        int vmID = Integer.parseInt(message.getString("ID"));
        vmList.get(vmID).setRam(ram).setBw(bandwidth).setSize(size);

        broker.submitVmList(vmList);
    }

    /**
     * This function deletes an already created VM.
     * @param message - Contains the id sent by FTM.
     */
    private void deleteVm(JSONObject message){
        int vmID = Integer.parseInt(message.getString("ID"));
        vmList.remove(vmID);

        broker.submitVmList(vmList);
    }

    /**
     * This function creates a single cloudlet with the parameters given.
     * @param message - Contains the requirements sent by FTM.
     */
    private void createCloudlet(JSONObject message) {
        UtilizationModel um = new UtilizationModelDynamic(0.2);

        JSONArray cloudletArray = message.getJSONArray("cloudlet");
        for(int i = 0; i < cloudletArray.length(); i++){
            JSONObject vmConfig = cloudletArray.getJSONObject(i);
            int fileSize = Integer.parseInt(vmConfig.getString("file_size"));
            int outputSize = Integer.parseInt(vmConfig.getString("output_size"));
            int pes = Integer.parseInt(vmConfig.getString("pes"));
            int length = Integer.parseInt(vmConfig.getString("length"));

            Cloudlet cloudlet = new CloudletSimple(length, pes)
                    .setFileSize(fileSize)
                    .setOutputSize(outputSize)
                    .setUtilizationModelCpu(new UtilizationModelFull())
                    .setUtilizationModelRam(um)
                    .setUtilizationModelBw(um);

            cloudletList.add(cloudlet);
        }

        broker.submitCloudletList(cloudletList);
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
                    URL urlOfServerGet = new URL(URL_OF_SERVER_GET);
                    HttpURLConnection connectionObject = (HttpURLConnection) urlOfServerGet.openConnection();
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

                        JSONObject responseObject = new JSONObject(receivedMessage.toString());
                        String toBeSent = parseAndRoute(responseObject);

                        //POSTing result starts here.
                        URL urlOfServerPost = new URL(URL_OF_SERVER_POST);
                        HttpURLConnection connectionPostObject = (HttpURLConnection) urlOfServerPost.openConnection();
                        connectionPostObject.setRequestMethod("POST");
                        connectionPostObject.setDoOutput(true);

                        int responseCodePost = -1; //Response Code of the request like 200 for success and 404 for not found.
                        responseCodePost = connectionPostObject.getResponseCode();
                        OutputStream output = connectionPostObject.getOutputStream();
                        output.write(toBeSent.getBytes());
                        output.flush();
                        output.close();

                        if (responseCodePost == HttpURLConnection.HTTP_OK) {
                            BufferedReader inPost = new BufferedReader(new InputStreamReader(
                                    connectionPostObject.getInputStream()));
                            String inputLinePost;
                            StringBuffer responsePost = new StringBuffer();

                            while ((inputLinePost = inPost.readLine()) != null) {
                                responsePost.append(inputLinePost);
                            }
                            inPost.close();

                            System.out.println(responsePost.toString());
                        } else {
                            System.out.println("POST request didn't work" + responseCodePost);
                        }
                    }else{
                        System.out.println("GET request didn't work" + responseCode);
                    }

                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        };

        Thread thread = new Thread(communicationRunnable, "TRIAL");
        thread.start();
        try {
            thread.sleep(1000L);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    /**
     * This function routes the message received to the appropriate function provided by CloudSim.
     * @param message - Contains the message received from FTM.
     * @return - returns a JSONObject with the appropriate data.
     */
    private String parseAndRoute(JSONObject message){
        String description = message.getString("desc");

        if(description.equalsIgnoreCase("instantiate_vm")){
            createVm(message);
        }else if(description.equalsIgnoreCase("updation")){
            updateVm(message);
        }else if(description.equalsIgnoreCase("deletion")){
            deleteVm(message);
        }else if(description.equalsIgnoreCase("instantiate_cloudlet")){
            createCloudlet(message);
        }else if(description.equalsIgnoreCase("migration")){

        }else if(description.equalsIgnoreCase("status")){

        }

        return "yolo";
    }
}
