// Manages the 0...n Magic Light bulbs, and their groups
import java.net.*;
import java.nio.channels.IllegalBlockingModeException;
import java.io.*;
import java.util.*;

public class MLManager {

	// Connection parameters
	final int LOCAL_PORT = 5577;
	final int REMOTE_PORT = 48899;
	
	// Create a type that includes the hardware name of the remote
//	public class RemoteDevice extends InetAddress {
//
//		RemoteDevice(String ipAddress, String ) {
//			super();
//			// TODO Auto-generated constructor stub
//		}
//		
//	}
	
	private ArrayList<InetAddress> MLAddresses;
	ArrayList<MLInterface> MLInterfaces;
	
	public MLManager() throws IOException 
	{
		// Locate all lights (get IP addresses)
		MLAddresses = findAllMLs();
		
		// Initialize bulb interface objects
		MLInterfaces = new ArrayList<MLInterface>();
		for (InetAddress addr : MLAddresses){
			MLInterfaces.add(new MLInterface(addr, REMOTE_PORT));
		}
	}
	
	public ArrayList<InetAddress> findAllMLs() throws IOException  
	{
		// Send broadcast to get all bulbs to respond
		DatagramSocket sock = new DatagramSocket(LOCAL_PORT);
		sock.setBroadcast(true);
		InetAddress broadcastIP = InetAddress.getByName("255.255.255.255");
		byte msg[] = "HF-A11ASSISTHREAD".getBytes();
		DatagramPacket discoverPacket = new DatagramPacket(msg, msg.length);
		discoverPacket.setAddress(broadcastIP);
		discoverPacket.setPort(REMOTE_PORT);
		sock.send(discoverPacket);
		
		// Build list of IP addresses
		sock.setSoTimeout(1500); // ms
		ArrayList<InetAddress> addrs = new ArrayList<InetAddress>();
		while (true)
		{
			// Read in message
			byte[] buf = new byte[1024];
			DatagramPacket pack = new DatagramPacket(buf, buf.length);
			try {
				sock.receive(pack);
			}
			catch (SocketTimeoutException e){
				break;
			}
			catch (IOException | IllegalBlockingModeException e){
				System.out.println("Could not read from incoming buffer.");
				break;
			}
			
			// IP address
			addrs.add(pack.getAddress());
			
			// Get the bulb name (MAC address also available)
			String data = new String(pack.getData(), "US-ASCII");
			String bulbName;
			try {
				bulbName = data.split(",")[2];
			}
			catch (ArrayIndexOutOfBoundsException e){
				System.out.println("Could not read information from bulb. Bulb name not recovered.");
			}
			
			
		}
		
		// Print results
		int n = addrs.size();
		System.out.println("Found " + n + " bulb IP" + (n == 1 ? "" : "s"));
		
		// Clean up
		sock.close();	
		return addrs;
	}

}
