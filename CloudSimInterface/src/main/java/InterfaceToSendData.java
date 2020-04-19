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
import org.glassfish.tyrus.client.ClientManager;
import org.json.JSONArray;
import org.json.JSONObject;

import javax.websocket.*;
import java.io.*;
import java.net.*;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.concurrent.CountDownLatch;
import java.util.logging.Logger;

/** This class describes an interface which sends any data required by FTM such as the current parameters
    of the VMs and handles all requests such as creating another VM and allocating resources to it.
 */
public class InterfaceToSendData {
    private final int HOST_PES = 8; // Random number as of now, TODO: Get this initially from FTM through a socket connection probably. DONE.
    private final int SCHEDULING_INTERVAL = 1; // Random number as of now, TODO: Discuss. DONE.
    private final int NUMBER_OF_HOSTS = 100; // Random number as of now, TODO: Get this initially from FTM through a socket connection probably. DONE
    private final int TIME_TILL_TERMINATION = 10000; // Random time as of now, very big time as discussed
    private final int TOTAL_LOCATIONS = 5; //Random number as of now.
    private JSONArray locations;

    private final CloudSim simulation;
    private final Session currSession;
    private final DatacenterBroker broker;
    private final Datacenter datacenter;
    final List<Host> hostList = new ArrayList<>(NUMBER_OF_HOSTS);
    private final List<Vm> vmList = new ArrayList<>();
    private List<Pair> unchangedList = new ArrayList<>();
    private final List<Cloudlet> cloudletList = new ArrayList<>();
//    private final String URL_OF_SERVER_GET = "http://192.168.1.8:8081"; // URL of server for all GET
//    private final String URL_OF_SERVER_POST = "http://192.168.1.8:8000"; // URL of server for all POST

    public static void main(String[] args) {
        new InterfaceToSendData();
    }

    private InterfaceToSendData(){

        Client.latch = new CountDownLatch(1);
        ClientManager client = ClientManager.createClient();
        try {
            currSession = client.connectToServer(Client.class, new URI("ws://localhost:8081/ws"));
            //currSession.getBasicRemote().sendText("1");
            //currSession.getBasicRemote().sendText("2");

            Client.latch.await();
        } catch (DeploymentException | URISyntaxException | InterruptedException | IOException e) {
            throw new RuntimeException(e);
        }

        locations = new JSONArray();
        for(int i = 0; i < TOTAL_LOCATIONS; i++){
            locations.put(i + "");
        }

        simulation = new CloudSim();
        simulation.terminateAt(TIME_TILL_TERMINATION);

        datacenter = createDatacenter();

        broker = new DatacenterBrokerSimple(simulation);

//        broker0.submitVmList(vmList);
//        broker0.submitCloudletList(cloudletList);

        simulation.addOnClockTickListener(this::onClickTickListener);

        simulation.start();
    }

    /**
     * This function creates a datacenter with a list of hosts.
     * @return Datacenter with the given hosts.
     */
    private Datacenter createDatacenter() {
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

        final long ram = 16384; // Random number as of now, TODO: Get this initially from FTM through a socket connection probably. DONE 16GB.
        final long bw = 40960; // Random number as of now, TODO: Get this initially from FTM through a socket connection probably. DONE 40Mbps.
        final long storage = 51200; // Random number as of now, TODO: Get this initially from FTM through a socket connection probably. DONE 50GB.
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
            int location = Integer.parseInt(vmConfig.getString("location"));

            Vm vm = new VmSimple(mips, pes)
                    .setRam(ram).setBw(bandwidth).setSize(size)
                    .setCloudletScheduler(new CloudletSchedulerTimeShared());

            vmList.add(vm);
            unchangedList.add(new Pair(vm, false));
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

        if(!unchangedList.get(vmID).isRemoved) {
            Vm currVm = unchangedList.get(vmID).vm;
            int mips = (int) currVm.getMips();
            int pes = (int) currVm.getNumberOfPes();

            Host toBeDeletedVmHost = currVm.getHost();
            toBeDeletedVmHost.destroyVm(currVm);

            vmList.remove(vmID);
            unchangedList.remove(vmID);
            broker.submitVmList(vmList);

            Vm vm = new VmSimple(mips, pes)
                    .setRam(ram).setBw(bandwidth).setSize(size)
                    .setCloudletScheduler(new CloudletSchedulerTimeShared());
            toBeDeletedVmHost.createVm(vm);
            vmList.add(vmID, vm);
            unchangedList.add(vmID, new Pair(vm, false));
            broker.submitVmList(vmList);
        }
    }

    /**
     * This function deletes an already created VM.
     * @param message - Contains the id sent by FTM.
     */
    private void deleteVm(JSONObject message){
        int vmID = Integer.parseInt(message.getString("ID"));

        if(!unchangedList.get(vmID).isRemoved){
            Vm currVm = unchangedList.get(vmID).vm;
            Host toBeDeletedVmHost = currVm.getHost();
            toBeDeletedVmHost.destroyVm(currVm);

            vmList.remove(vmID);
            unchangedList.get(vmID).isRemoved = true;

            broker.submitVmList(vmList);
        }
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
     * This method returns the 'status' of the given VM.
     * @param message - Contains a VM ID so we can identify which VM's status is needed.
     * @return The data asked for.
     */
    private JSONObject statusVm(JSONObject message){
        int vmID = Integer.parseInt(message.getString("id"));
        JSONObject allDataJSON = null;
        if(!unchangedList.get(vmID).isRemoved){
            Vm currVm = unchangedList.get(vmID).vm;
            String allocatedBw, availableBw, capacityBw, currentRequestedBw, cpuPercentUtilization,
                    currentRequestedTotalMips, allocatedRam, availableRam, capacityRam, currentRequestedRam,
                    allocatedStorage, availableStorage, capacityStorage, isWorkingOrFailed;
            allocatedBw = currVm.getBw().getAllocatedResource() + ""; //TODO: Decide what to return. Everything. DONE.
            availableBw = currVm.getBw().getAvailableResource() + "";
            capacityBw = currVm.getBw().getCapacity() + "";
            currentRequestedBw = currVm.getCurrentRequestedBw() + "";
            cpuPercentUtilization = currVm.getCpuPercentUtilization() + "";
            currentRequestedTotalMips = currVm.getCurrentRequestedTotalMips() + "";
            allocatedRam = currVm.getRam().getAllocatedResource() + "";
            availableRam = currVm.getRam().getAvailableResource() + "";
            capacityRam = currVm.getRam().getCapacity() + "";
            currentRequestedRam = currVm.getCurrentRequestedRam() + "";
            allocatedStorage = currVm.getStorage().getAllocatedResource() + "";
            availableStorage = currVm.getStorage().getAvailableResource() + "";
            capacityStorage = currVm.getStorage().getCapacity() + "";

            if(unchangedList.get(vmID).vm.isWorking()){
                isWorkingOrFailed = "working";
            }else{
                isWorkingOrFailed = "failed";
            }

            /*String allData = "{\"desc\":\"vm_status_reply\"," +
                    "\"allocated_bandwidth\": \"" + allocatedBw + "\"," +
                    "\"available_bandwidth\": \"" + availableBw + "\"," +
                    "\"capacity_bandwidth\": \"" + capacityBw + "\"," +
                    "\"current_requested_bandwidth\": \"" + currentRequestedBw + "\"," +
                    "\"cpu_percent_utilization\": \"" + cpuPercentUtilization + "\"," +
                    "\"current_requested_total_mips\": \"" + currentRequestedTotalMips + "\"," +
                    "\"allocated_ram\": \"" + allocatedRam + "\"," +
                    "\"available_ram\": \"" + availableRam + "\"," +
                    "\"capacity_ram\": \"" + capacityRam + "\"," +
                    "\"current_requested_ram\": \"" + currentRequestedRam + "\"," +
                    "\"allocated_storage\": \"" + allocatedStorage + "\"," +
                    "\"available_storage\": \"" + availableStorage + "\"," +
                    "\"capacity_storage\": \"" + capacityStorage + "\"," +
                    "\"condition\": \"" + isWorkingOrFailed + "\"}";*/

            allDataJSON = new JSONObject();
            allDataJSON.put("desc", "vm_status_reply");
            allDataJSON.put("allocated_bandwidth", allocatedBw);
            allDataJSON.put("available_bandwidth", availableBw);
            allDataJSON.put("capacity_bandwidth", capacityBw);
            allDataJSON.put("current_requested_bandwidth", currentRequestedBw);
            allDataJSON.put("cpu_percent_utilization", cpuPercentUtilization);
            allDataJSON.put("current_requested_total_mips", currentRequestedTotalMips);
            allDataJSON.put("allocated_ram", allocatedRam);
            allDataJSON.put("available_ram", availableRam);
            allDataJSON.put("capacity_ram", capacityRam);
            allDataJSON.put("current_requested_ram", currentRequestedRam);
            allDataJSON.put("allocated_storage", allocatedStorage);
            allDataJSON.put("available_storage", availableStorage);
            allDataJSON.put("capacity_storage", capacityStorage);
            allDataJSON.put("condition", isWorkingOrFailed);
        }

        return allDataJSON;
    }

    /**
     * This method is used to migrate a VM from one host to another.
     * @param message - Contains the ID of the VM to be migrated.
     */
    private void migrateVm(JSONObject message){
        boolean empty = false;
        int vmID = Integer.parseInt(message.getString("id"));
        if(!unchangedList.get(vmID).isRemoved){
            Vm vm = unchangedList.get(vmID).vm;
            for(Host host : hostList){
                if(host.getVmList().isEmpty()){
                    datacenter.requestVmMigration(vm, host);
                    empty = true;
                }
            }

            if(!empty){
                int min = Integer.MAX_VALUE;
                Host vmHost = unchangedList.get(vmID).vm.getHost();
                Host temp = null;
                for(Host host : hostList){
                    if(min >= host.getVmList().size()){
                        min = host.getVmList().size();
                        if(host != vmHost){
                            temp = host;
                        }
                    }
                }

                datacenter.requestVmMigration(vm, temp);
            }
        }
    }

    /**
     * This function returns an array containing all possible locations.
     * @return - Array containing all locations.
     */
    private JSONArray sendLocations(){
        return locations;
    }

    /**
     * This function is called at the passing of every single simulated second.
     * @param evtInfo - Contains the description of the event that triggered this listener. In this case,
     *                the passing of every second (simulated) is the trigger.
     */
    private void onClickTickListener(EventInfo evtInfo) {

        String receivedMessage = Client.getRecMessage();
        if(!receivedMessage.isEmpty()){
            JSONObject obj = new JSONObject(receivedMessage);
            parseAndRoute(obj);
        }
        /*Runnable communicationRunnable = new Runnable() {
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
        }*/
    }

    /**
     * This function routes the message received to the appropriate function provided by CloudSim
     * and sends a reply wherever needed.
     * @param message - Contains the message received from FTM.
     */
    private void parseAndRoute(JSONObject message){
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
            //TODO: Decide how to select destination host. Select random host with least VMs. DONE.
            migrateVm(message);
        }else if(description.equalsIgnoreCase("status")){
            JSONObject rv = statusVm(message);
            try {
                currSession.getBasicRemote().sendObject(rv);
            } catch (IOException | EncodeException e) {
                e.printStackTrace();
            }
        }else if(description.equalsIgnoreCase("get_location")){
            JSONArray rv = sendLocations();
            try {
                currSession.getBasicRemote().sendObject(rv);
            } catch (IOException | EncodeException e) {
                e.printStackTrace();
            }
        }
    }

    /**
     * Class used to maintain VM IDs even after removal of some VMs.
     */
    private class Pair {
        Vm vm;
        boolean isRemoved;

        Pair(){

        }

        Pair(Vm vm, boolean isRemoved){
            this.vm = vm;
            this.isRemoved = isRemoved;
        }

        public Vm getVm() {
            return vm;
        }

        public boolean isRemoved() {
            return isRemoved;
        }
    }
}


/**
 * This class acts as the Client Endpoint for the websocket connection and handles all communication.
 */
@ClientEndpoint
class Client {

    private Logger logger = Logger.getLogger(this.getClass().getName());
    public static CountDownLatch latch;
    private static Queue<String> messageQueue = new LinkedList<>();

    public static String getRecMessage() {
        String send = "";
        if(!messageQueue.isEmpty()){
            send = messageQueue.poll();
        }
        return send;
    }

    @OnOpen
    public void onOpen(Session session) {
        logger.info("Connected ... " + session.getId());
    }

    @OnMessage
    public void onMessage(String message, Session session) {
        logger.info("Received ...." + message);
        messageQueue.add(message);
    }

    @OnClose
    public void onClose(Session session, CloseReason closeReason) {
        logger.info(String.format("Session %s close because of %s", session.getId(), closeReason));
        latch.countDown();
    }
}