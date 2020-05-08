import org.apache.commons.math3.distribution.BetaDistribution;
import org.cloudbus.cloudsim.allocationpolicies.VmAllocationPolicy;
import org.cloudbus.cloudsim.allocationpolicies.VmAllocationPolicySimple;
import org.cloudbus.cloudsim.brokers.DatacenterBroker;
import org.cloudbus.cloudsim.brokers.DatacenterBrokerSimple;
import org.cloudbus.cloudsim.cloudlets.Cloudlet;
import org.cloudbus.cloudsim.cloudlets.CloudletSimple;
import org.cloudbus.cloudsim.core.CloudSim;
import org.cloudbus.cloudsim.datacenters.Datacenter;
import org.cloudbus.cloudsim.datacenters.DatacenterSimple;
import org.cloudbus.cloudsim.distributions.PoissonDistr;
import org.cloudbus.cloudsim.hosts.Host;
import org.cloudbus.cloudsim.hosts.HostSimple;
import org.cloudbus.cloudsim.provisioners.PeProvisionerSimple;
import org.cloudbus.cloudsim.provisioners.ResourceProvisionerSimple;
import org.cloudbus.cloudsim.resources.Pe;
import org.cloudbus.cloudsim.resources.PeSimple;
import org.cloudbus.cloudsim.schedulers.cloudlet.CloudletSchedulerTimeShared;
import org.cloudbus.cloudsim.schedulers.vm.VmSchedulerTimeShared;
import org.cloudbus.cloudsim.util.Conversion;
import org.cloudbus.cloudsim.utilizationmodels.UtilizationModel;
import org.cloudbus.cloudsim.utilizationmodels.UtilizationModelDynamic;
import org.cloudbus.cloudsim.utilizationmodels.UtilizationModelFull;
import org.cloudbus.cloudsim.vms.Vm;
import org.cloudbus.cloudsim.vms.VmSimple;
import org.cloudsimplus.builders.tables.CloudletsTableBuilder;
import org.cloudsimplus.faultinjection.HostFaultInjection;
import org.cloudsimplus.listeners.EventInfo;
import org.cloudsimplus.listeners.EventListener;
import org.cloudsimplus.listeners.VmHostEventInfo;
import org.glassfish.tyrus.client.ClientManager;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import javax.websocket.*;
import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.CountDownLatch;
import java.util.function.BiFunction;
import java.util.logging.Logger;

/* This class describes an interface which sends any data required by FTM such as the current parameters
    of the VMs and handles all requests such as creating another VM and allocating resources to it.
 */
/*public class InterfaceToSendData {
    private InterfaceToSendData() throws InterruptedException {

    }
}*/


/**
 * This class acts as the Client Endpoint for the websocket connection and handles all communication.
 * It also describes an interface which sends any data required by FTM such as the current parameters
 * of the VMs and handles all requests such as creating another VM and allocating resources to it.
 */
@ClientEndpoint
public class Client {

    @OnOpen
    public void onOpen(Session session) {
        //System.out.println("yolo7");
        //System.out.println("Connected ... " + session.getId());
    }

    @OnMessage
    public void onMessage(String message, Session session) {
        //System.out.println("yolo8");
        //System.out.println("Received ...." + message);
        messageQueue.add(message);
    }

    @OnClose
    public void onClose(Session session, CloseReason closeReason) {
        //System.out.println(String.format("Session %s close because of %s", session.getId(), closeReason));
        //latch.countDown();
    }

    /**
     * Constants related to the websocket connection.
     */
    private Logger logger = Logger.getLogger(this.getClass().getName());
    public static CountDownLatch latch;
    private static Queue<String> messageQueue = new LinkedList<>();
    private static String port;

    /**
     * Constants related to Cloud Architecture configuration.
     */
    private static final int HOST_PES = 10; // Random number as of now, TODO: Get this initially from FTM through a socket connection probably. DONE.
    private static final int SCHEDULING_INTERVAL = 1; // Random number as of now, TODO: Discuss. DONE.
    private static final int NUMBER_OF_HOSTS = 50; // Random number as of now, TODO: Get this initially from FTM through a socket connection probably. DONE
    private static final int TIME_TILL_TERMINATION = 40; // Random time as of now, very big time as discussed
    private static final int TOTAL_LOCATIONS = 10; //Random number as of now.
    private static JSONArray locations;

    /**
     * Constants related to injection of faults (needed by CloudSim).
     */
    private static HostFaultInjection fault;
    //private static int count = 0;
    private static PoissonDistr poisson;
    private static final double MEAN_FAILURE_NUMBER_PER_HOUR = 0;

    /**
     * Constants related to generation of faults (needed by our program).
     */
    private static final double LOWER_BOUND = 0.0;
    private static final double UPPER_BOUND = 1.0;
    private static final HashMap<Integer, Pair> locationThreshold = new HashMap<>();
    private static Set<Map.Entry<Integer, Pair>> locationThresholdEntrySet;
    private static final double THRESHOLD_PERCENTAGE = 0.5;
    private static final double THRESHOLD_LOCATION = LOWER_BOUND + ((1 - LOWER_BOUND) * THRESHOLD_PERCENTAGE);
    private static final double THRESHOLD_HOST = LOWER_BOUND + ((1 - LOWER_BOUND) * THRESHOLD_PERCENTAGE);
    private static final long SEED_LOCATION = 123456L;
    private static final long SEED_HOST = 234567L;
    private static final long SEED_INDEX = 345678L;
    private static final Random random = new Random(SEED_LOCATION);
    private static final double ALPHA = 1;
    private static final double BETA = 1;
    private static final BetaDistribution betaDistributionLocation = new BetaDistribution(ALPHA, BETA);
    private static final BetaDistribution betaDistributionHost = new BetaDistribution(ALPHA, BETA);
    private static final BetaDistribution betaDistributionIndex = new BetaDistribution(ALPHA, BETA);
    private static String threshold1FromCMD;
    private static String threshold2FromCMD;
    private static String seed1FromCMD;
    private static String seed2FromCMD;
    private static String seed3FromCMD;

    /**
     * Constants related to debugging.
     */
    static StringBuilder debugRandoms = new StringBuilder();
    static StringBuilder debugHosts = new StringBuilder();
    static StringBuilder debugLocations = new StringBuilder();

    /**
     * Variables related to working of CloudSim.
     */
    private static String finishClientID;
    private static/*final*/ CloudSim simulation;
    private static/*final*/ Session currSession;
    private static/*final*/ DatacenterBroker broker;
    private static/*final*/ Datacenter datacenter;
    static final List<Host> hostList = new ArrayList<>(NUMBER_OF_HOSTS);
    private static final List<Vm> vmList = new ArrayList<>();
    private static List<Vm> unchangedList = new ArrayList<>();
    private static HashMap<Integer, Integer> idMap = new HashMap<>();
    private static final List<Cloudlet> cloudletList = new ArrayList<>();
    //private final String URL_OF_SERVER_GET = "http://192.168.1.8:8081"; // URL of server for all GET
    //private final String URL_OF_SERVER_POST = "http://192.168.1.8:8000"; // URL of server for all POST
    private static EventListener<EventInfo> onClockTickListener;
    private static BiFunction<VmAllocationPolicy, Vm, Optional<Host>> findHostForVm;
    private static EventListener<VmHostEventInfo> hostAllocationListener;

    /**
     *  Variables related to parsing of argument file.
     */
    private static JSONParser jsonParser = new JSONParser();

    //vm.setID() -> For location
    //vm.setDescription() -> For Client ID

    /**
     * vm.setID() -> For location
     * vm.setDescription() -> For Client ID
     */

    public static void main(String[] args) {
        //latch = new CountDownLatch(1);
        /*try{
            Thread.sleep(15000);
        }catch (InterruptedException e){
            e.printStackTrace();
        }*/
        //Client clientTest = new Client();
        onClockTickListener = eventInfo -> {
            //System.out.println("yolo4");

            /*double randomGeneratedForLocation = LOWER_BOUND + (random.nextDouble() * (UPPER_BOUND - LOWER_BOUND));
            for(Map.Entry<Integer, Pair> entry : locationThresholdEntrySet){
                if(randomGeneratedForLocation > entry.getValue().getFirst()
                        && (int)(eventInfo.getTime()) >= 15){
                    double randomGeneratedForHost = LOWER_BOUND + (random.nextDouble() * (UPPER_BOUND - LOWER_BOUND));
                    if(randomGeneratedForHost > entry.getValue().getSecond()){
                        int factor = NUMBER_OF_HOSTS / TOTAL_LOCATIONS;
                        int id = entry.getKey();
                        int startIdx = factor * id;
                        int randomHostIndex = ThreadLocalRandom.current().nextInt(startIdx, startIdx + factor);
                        if(hostList.get(randomHostIndex).getFailedPesNumber() != HOST_PES){
                            fault.generateHostFault(hostList.get(randomHostIndex));
                        }
                    }
                }
            }*/

            if((int)(eventInfo.getTime()) == TIME_TILL_TERMINATION - 2){
                JSONObject finalMessage = new JSONObject();
                finalMessage.put("desc", "finish");
                finalMessage.put("client_id", finishClientID);
                try {
                    currSession.getBasicRemote().sendObject(finalMessage);
                    System.out.println(finalMessage);
                } catch (IOException | EncodeException e) {
                    e.printStackTrace();
                }
            }

            if((int)(eventInfo.getTime()) >= 15){
                double randomGeneratedForLocation = LOWER_BOUND + (betaDistributionLocation.sample() * (UPPER_BOUND - LOWER_BOUND));
                //System.out.println(randomGeneratedForLocation + " loc ");
                debugRandoms.append(randomGeneratedForLocation).append(" ");
                for(Map.Entry<Integer, Pair> entry : locationThresholdEntrySet){
                    if(randomGeneratedForLocation > entry.getValue().getFirst()){
                        double randomGeneratedForHost = LOWER_BOUND + (betaDistributionHost.sample() * (UPPER_BOUND - LOWER_BOUND));
                        debugRandoms.append(randomGeneratedForHost).append(" ");
                        //System.out.println(randomGeneratedForHost + " host ");
                        if(randomGeneratedForHost > entry.getValue().getSecond()){
                            int factor = NUMBER_OF_HOSTS / TOTAL_LOCATIONS;
                            int id = entry.getKey();
                            int startIdx = factor * id;
                            int randomHostIndex = (int)(Math.floor(startIdx + (betaDistributionIndex.sample() * factor)));
                            //System.out.println(randomHostIndex + " idx ");
                            debugRandoms.append(randomHostIndex).append(" ");
                            if(hostList.get(randomHostIndex).getFailedPesNumber() != HOST_PES){
                                fault.generateHostFault(hostList.get(randomHostIndex));
                            }
                        }
                    }
                }
            }

            /*if(randomGenerated > THRESHOLD && (int)(eventInfo.getTime()) >= 15){
                int randomHostIndex = ThreadLocalRandom.current().nextInt(0, hostList.size());
                fault.generateHostFault(hostList.get(randomHostIndex));
            }*/

            while(messageQueue != null && !messageQueue.isEmpty()) {
                String receivedMessage = getRecMessage();
                if(receivedMessage != null && !receivedMessage.isEmpty()){
                    //System.out.println("yolo9");
                    JSONObject obj = new JSONObject(receivedMessage);
                    parseAndRoute(obj);
                }
            }

            /*String receivedMessage = getRecMessage();
            if(!receivedMessage.isEmpty()){
                //System.out.println("yolo9");
                JSONObject obj = new JSONObject(receivedMessage);
                parseAndRoute(obj);
            }*/

            /*if((int)eventInfo.getTime() == 15){
                fault.generateHostFault(hostList.get(0));
                fault.generateHostFault(hostList.get(5));
                fault.generateHostFault(hostList.get(10));
            }*/

            if((int)eventInfo.getTime() == 15){
                for(Host host : hostList){
                    //System.out.println(host.getVmList().size());
                    debugHosts.append(host.getVmList().size()).append(" ");
                }
            }

            /*if((int)(simulation.clockInMinutes() * 60) >= TIME_TILL_TERMINATION){
                simulation.terminate();
            }else if((int)(simulation.clockInMinutes()) >= 1
                    && count == 0){
                createFaultInjectionForHosts(datacenter);
                count++;
            }*/

            try{
                Thread.sleep(1000);
            }catch (InterruptedException e){
                e.printStackTrace();
            }
        };

        hostAllocationListener = vmHostEventInfo -> {
            JSONObject hostAllocationReply = new JSONObject();
            hostAllocationReply.put("desc", "host_allocation");
            hostAllocationReply.put("client_id", vmHostEventInfo.getVm().getDescription());

            int find = -1;
            for(int i = 0; i < unchangedList.size(); i++){
                if(unchangedList.get(i) == vmHostEventInfo.getVm()){
                    find = i;
                    break;
                }
            }
            int vmID = -1;
            Set<Map.Entry<Integer, Integer>> entries = idMap.entrySet();
            for(Map.Entry<Integer, Integer> entry : entries){
                if(entry.getValue() == find){
                    vmID = entry.getKey();
                    break;
                }
            }

            hostAllocationReply.put("vm_id", vmID + "");

            //System.out.println(hostAllocationReply);
            try {
                currSession.getBasicRemote().sendObject(hostAllocationReply);
            } catch (IOException | EncodeException e) {
                e.printStackTrace();
            }
        };

        try{
            org.json.simple.JSONObject obj = (org.json.simple.JSONObject) jsonParser.parse(new FileReader(args[0]));
            threshold1FromCMD = (String) obj.get("threshold1");
            threshold2FromCMD = (String) obj.get("threshold2");
            seed1FromCMD = (String) obj.get("seed1");
            seed2FromCMD = (String) obj.get("seed2");
            seed3FromCMD = (String) obj.get("seed3");
            port = (String) obj.get("port");
        }catch (IOException | ParseException e){
            e.printStackTrace();
        }

        /*File file = new File(args[0]);
        String arguments = "";
        try {
            BufferedReader br = new BufferedReader(new FileReader(file));

            String st;
            while ((st = br.readLine()) != null) {
                arguments = st;
            }
        }catch(IOException e){
            e.printStackTrace();
        }

        String[] argsArray = arguments.split(" ");
        for(String str : argsArray){
            System.out.print(str + " ");
        }*/

        betaDistributionLocation.reseedRandomGenerator(Long.parseLong(seed1FromCMD));
        betaDistributionHost.reseedRandomGenerator(Long.parseLong(seed2FromCMD));
        betaDistributionIndex.reseedRandomGenerator(Long.parseLong(seed3FromCMD));

        for(int i = 0; i < TOTAL_LOCATIONS; i++) {
            locationThreshold.put(i, new Pair(Double.parseDouble(threshold1FromCMD), Double.parseDouble(threshold2FromCMD)));
        }

        locationThresholdEntrySet = locationThreshold.entrySet();

        ClientManager client = ClientManager.createClient();
        try {
            //System.out.println("yolo1");
            //currSession = client.connectToServer(Client.class, new URI("ws://localhost:8081/ws"));
            String url = "ws://localhost:" + port + "/ws";
            currSession = client.connectToServer(Client.class, new URI(url));
            System.out.println(currSession.getId());
            locations = new JSONArray();
            for(int i = 0; i < TOTAL_LOCATIONS; i++){
                locations.put(i + "");
            }

            //System.out.println("yolo2");
            simulation = new CloudSim();
            simulation.terminateAt(TIME_TILL_TERMINATION);

            datacenter = createDatacenter();

            broker = new DatacenterBrokerSimple(simulation);

            //broker0.submitVmList(vmList);
            //broker0.submitCloudletList(cloudletList);

            //simulation.addOnClockTickListener(this::onClickTickListener);

            //fault = new HostFaultInjection(datacenter);
            createFaultInjectionForHosts(datacenter);

            simulation.addOnClockTickListener(onClockTickListener);
            //System.out.println("yolo3");
            simulation.start();

            /*System.out.printf(
                    "%n# Mean Number of Failures per Hour: %.3f (1 failure expected at each %.2f hours).%n",
                    MEAN_FAILURE_NUMBER_PER_HOUR, poisson.getInterArrivalMeanTime());
            System.out.printf("# Number of Host faults: %d%n", fault.getNumberOfHostFaults());
            System.out.printf("# Number of VM faults (VMs destroyed): %d%n", fault.getNumberOfFaults());
            System.out.printf("# Time the simulations finished: %.4f hours%n", simulation.clockInHours());
            System.out.printf("# Mean Time To Repair Failures of VMs in minutes (MTTR): %.2f minute%n", fault.meanTimeToRepairVmFaultsInMinutes());
            System.out.printf("# Mean Time Between Failures (MTBF) affecting all VMs in minutes: %.2f minutes%n", fault.meanTimeBetweenVmFaultsInMinutes());
            System.out.printf("# Hosts MTBF: %.2f minutes%n", fault.meanTimeBetweenHostFaultsInMinutes());
            System.out.printf("# Availability: %.2f%%%n%n", fault.availability()*100);*/
            //currSession.getBasicRemote().sendText("1");
            //currSession.getBasicRemote().sendText("2");

            /*try{
                Thread.sleep(15000);
            }catch (InterruptedException e){
                e.printStackTrace();
            }*/

            //latch.await();
        } catch (DeploymentException | URISyntaxException /*| InterruptedException*/ | IOException e) {
            throw new RuntimeException(e);
        }

        final List<Cloudlet> finishedCloudlets = broker.getCloudletFinishedList();
        new CloudletsTableBuilder(finishedCloudlets).build();

        System.out.println(debugRandoms.toString());
        System.out.println(debugHosts.toString());
        System.out.println(debugLocations.toString());
    }

    /**
     * This function creates a datacenter with a list of hosts.
     * @return Datacenter with the given hosts.
     */
    private static Datacenter createDatacenter() {
        for(int i = 0; i < NUMBER_OF_HOSTS; i++) {
            Host host = createHost();
            hostList.add(host);
        }

        findHostForVm = (vmAllocationPolicy, vm) -> {
            int factor = NUMBER_OF_HOSTS / TOTAL_LOCATIONS;
            int id = (int)(vm.getId());
            int startIdx = factor * id;
            int min = Integer.MAX_VALUE;
            Host rv = null;
            for(int i = startIdx; i < startIdx + factor; i++){
                Host host = hostList.get(i);
                if(min > host.getVmList().size()){
                    min = host.getVmList().size();
                    rv = host;
                }
            }

            return rv != null ? Optional.of(rv) : Optional.empty();
        };

        VmAllocationPolicySimple vmAllocationPolicy = new VmAllocationPolicySimple();
        vmAllocationPolicy.setFindHostForVmFunction(findHostForVm);

        final Datacenter dc = new DatacenterSimple(simulation, hostList, vmAllocationPolicy);
        dc.setSchedulingInterval(SCHEDULING_INTERVAL);
        return dc;
    }

    /**
     * This function creates a host with pes, RAM, storage and bandwidth.
     * @return Host with the given specs.
     */
    private static Host createHost() {
        List<Pe> peList = new ArrayList<>(HOST_PES);

        for (int i = 0; i < HOST_PES; i++) {
            peList.add(new PeSimple(20000, new PeProvisionerSimple()));
        }

        final long ram = 131072; // Random number as of now, TODO: Get this initially from FTM through a socket connection probably. DONE 128GB.
        final long bw = 16384; // Random number as of now, TODO: Get this initially from FTM through a socket connection probably. DONE (40 * 8) / 20 Mbps.
        final long storage = 819200; // Random number as of now, TODO: Get this initially from FTM through a socket connection probably. DONE 800GB.
        Host host = new HostSimple(ram, bw, storage, peList);
        host
                .setRamProvisioner(new ResourceProvisionerSimple())
                .setBwProvisioner(new ResourceProvisionerSimple())
                .setVmScheduler(new VmSchedulerTimeShared());
        return host;
    }

    private static void createFaultInjectionForHosts(Datacenter datacenter) {
        final long seed = 112717613L;
        poisson = new PoissonDistr(MEAN_FAILURE_NUMBER_PER_HOUR, seed);

        fault = new HostFaultInjection(datacenter, poisson);
        fault.setMaxTimeToFailInHours(800);
        //fault.generateHostFault(hostList.get(0));

        //fault.addVmCloner(broker, new VmClonerSimple(this::cloneVm, this::cloneCloudlets));
    }

    /**
     * This function creates a VM with the given specs as received from FTM.
     * @param message - Contains the specs sent by FTM.
     */
    private static void createVm(JSONObject message){
        JSONArray vmArray = message.getJSONArray("VM");
        for(int i = 0; i < vmArray.length(); i++){
            JSONObject vmConfig = vmArray.getJSONObject(i);
            String clientID = "";
            if(message.has("client_id")){
                finishClientID = message.getString("client_id");
                clientID = message.getString("client_id");
            }
            int vmID = Integer.parseInt(vmConfig.getString("vm_id"));
            int mips = Integer.parseInt(vmConfig.getString("mips"));
            int pes = Integer.parseInt(vmConfig.getString("pes"));
            int ram = Integer.parseInt(vmConfig.getString("ram"));
            int bandwidth = Integer.parseInt(vmConfig.getString("bandwidth"));
            int size = Integer.parseInt(vmConfig.getString("size"));
            int location = vmConfig.getInt("location");

            debugLocations.append(location).append(" ");

            Vm vm = new VmSimple(mips, pes)
                    .setRam(ram).setBw(bandwidth).setSize(size)
                    .setCloudletScheduler(new CloudletSchedulerTimeShared());

            vm.setId(location);
            vm.setDescription(clientID);
            vm.addOnHostAllocationListener(hostAllocationListener);
            vmList.add(vm);
            unchangedList.add(vm);
            idMap.put(vmID, unchangedList.size() - 1);
        }

        broker.submitVmList(vmList);
        vmList.clear();
    }

    /**
     * This function updates an already created VM with the given specs as received from FTM.
     * @param message - Contains the specs sent by FTM.
     */
    private static void updateVm(JSONObject message){
        JSONArray vmArray = message.getJSONArray("VM");
        JSONObject newVmConfig = vmArray.getJSONObject(0);
        int ram = Integer.parseInt(newVmConfig.getString("ram"));
        String clientID = "";
        if(message.has("client_id")){
            clientID = message.getString("client_id");
        }
        int bandwidth = Integer.parseInt(newVmConfig.getString("bandwidth"));
        int size = Integer.parseInt(newVmConfig.getString("size"));

        int vmID = Integer.parseInt(message.getString("ID"));

        int mappedID = idMap.get(vmID);
        Vm currVm = vmList.get(mappedID);
        int mips = (int) currVm.getMips();
        int pes = (int) currVm.getNumberOfPes();

        Host toBeDeletedVmHost = currVm.getHost();
        toBeDeletedVmHost.destroyVm(currVm);

        vmList.remove(mappedID);
        //unchangedList.remove(vmID);
        //broker.submitVmList(vmList);

        Vm vm = new VmSimple(mips, pes)
                .setRam(ram).setBw(bandwidth).setSize(size)
                .setCloudletScheduler(new CloudletSchedulerTimeShared());
        toBeDeletedVmHost.createVm(vm);
        vmList.add(mappedID, vm);
        //unchangedList.add(vmID, new Pair(vm, false));
        broker.submitVmList(vmList);

        /*if(!unchangedList.get(vmID).isRemoved) {
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
        }*/
    }

    /**
     * This function deletes an already created VM.
     * @param message - Contains the id sent by FTM.
     */
    private static void deleteVm(JSONObject message){
        int vmID = Integer.parseInt(message.getString("ID"));
        String clientID = "";
        if(message.has("client_id")){
            clientID = message.getString("client_id");
        }

        int mappedID = idMap.get(vmID);
        Vm currVm = vmList.get(mappedID);
        Host toBeDeletedVmHost = currVm.getHost();
        toBeDeletedVmHost.destroyVm(currVm);

        vmList.remove(mappedID);
        idMap.remove(vmID);
        //unchangedList.get(vmID).isRemoved = true;

        broker.submitVmList(vmList);

        /*if(!unchangedList.get(vmID).isRemoved){
            Vm currVm = unchangedList.get(vmID).vm;
            Host toBeDeletedVmHost = currVm.getHost();
            toBeDeletedVmHost.destroyVm(currVm);

            vmList.remove(vmID);
            unchangedList.get(vmID).isRemoved = true;

            broker.submitVmList(vmList);
        }*/
    }

    /**
     * This function creates a single cloudlet with the parameters given.
     * @param message - Contains the requirements sent by FTM.
     */
    private static void createCloudlet(JSONObject message) {
        UtilizationModel um = new UtilizationModelDynamic(0.2);

        JSONArray cloudletArray = message.getJSONArray("cloudlet");
        String clientID = "";
        if(message.has("client_id")){
            clientID = message.getString("client_id");
        }
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
    private static JSONObject statusVm(JSONObject message){
        String clientID = "";
        if(message.has("client_id")){
            clientID = message.getString("client_id");
        }
        int vmID = Integer.parseInt(message.getString("id"));
        JSONObject allDataJSON = null;

        int mappedID = idMap.get(vmID);
        Vm currVm = unchangedList.get(mappedID);
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

        if(currVm.isCreated()){
            isWorkingOrFailed = "working";
        }else{
            isWorkingOrFailed = "failed";
        }

        allDataJSON = new JSONObject();
        allDataJSON.put("client_id", clientID);
        allDataJSON.put("desc", "status");
        allDataJSON.put("vm_id", vmID + "");
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
        /*if(!unchangedList.get(vmID).isRemoved){
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

            *//*String allData = "{\"desc\":\"vm_status_reply\"," +
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
                    "\"condition\": \"" + isWorkingOrFailed + "\"}";*//*

            allDataJSON = new JSONObject();
            allDataJSON.put("client_id", clientID);
            allDataJSON.put("desc", "status");
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
        }*/

        return allDataJSON;
    }

    /**
     * This method is used to migrate a VM from one host to another.
     * @param message - Contains the ID of the VM to be migrated.
     */
    private static void migrateVm(JSONObject message){
        int vmID = Integer.parseInt(message.getString("id"));
        int mappedID = idMap.get(vmID);
        String clientID = "";
        if(message.has("client_id")){
            clientID = message.getString("client_id");
        }

        JSONObject migrationStarted = new JSONObject();
        migrationStarted.put("desc", "migration_successful");
        migrationStarted.put("client_id", clientID);
        migrationStarted.put("vm_id", vmID);

        Vm vm = unchangedList.get(mappedID);
        for(Host host : hostList){
            if(host.getVmList().isEmpty() && host.isSuitableForVm(vm) && host.getVmsMigratingIn().isEmpty()){
                String delay = vm.getRam().getCapacity() / Conversion.bitesToBytes(host.getBw().getCapacity() * datacenter.getBandwidthPercentForMigration()) + "";
                migrationStarted.put("delay", delay);
                try {
                    currSession.getBasicRemote().sendObject(migrationStarted);
                } catch (IOException | EncodeException e) {
                    e.printStackTrace();
                }
                datacenter.requestVmMigration(vm, host);
                return;
            }
        }

        int min = Integer.MAX_VALUE;
        Host vmHost = unchangedList.get(mappedID).getHost();
        Host temp = null;
        for(Host host : hostList){
            if(min > host.getVmList().size()){
                if(host != vmHost){
                    min = host.getVmList().size();
                    temp = host;
                }
            }
        }

        /*if(temp == null){
            return;
        }*/

        String delay = vm.getRam().getCapacity() / Conversion.bitesToBytes(temp.getBw().getCapacity() * datacenter.getBandwidthPercentForMigration()) + "";
        migrationStarted.put("delay", delay);
        try {
            currSession.getBasicRemote().sendObject(migrationStarted);
        } catch (IOException | EncodeException e) {
            e.printStackTrace();
        }

        datacenter.requestVmMigration(vm, temp);


        /*if(!unchangedList.get(vmID).isRemoved){
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
        }*/
    }

    /**
     * This function returns an array containing all possible locations.
     * @return - Array containing all locations.
     */
    private static JSONArray sendLocations(){
        return locations;
    }

    /**
     * This function is called at the passing of every single simulated second.
     * @param evtInfo - Contains the description of the event that triggered this listener. In this case,
     *                the passing of every second (simulated) is the trigger.
     */
    public void onClickTickListener(EventInfo evtInfo) {

        //System.out.println("yolo4");
        String receivedMessage = getRecMessage();
        if(!receivedMessage.isEmpty()){
            //System.out.println("yolo9");
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
    private static void parseAndRoute(JSONObject message){
        //System.out.println("yolo5");
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
                //System.out.println(rv);
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

    public static String getRecMessage() {
        //System.out.println("yolo6");
        String send = "";
        if(messageQueue != null && !messageQueue.isEmpty()){
            send = messageQueue.poll();
        }
        return send;
    }
}