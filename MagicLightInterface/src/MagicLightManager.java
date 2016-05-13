// Manages the 0...n Magic Light bulbs, and their groups
import java.net.*;
import java.nio.channels.IllegalBlockingModeException;
import java.io.*;
import java.util.*;

public class MagicLightManager {

	// Connection parameters
	final int LOCAL_PORT = 5577;
	final int REMOTE_PORT = 48899;
	
	private ArrayList<InetAddress> bulbAddresses;
	
	public MagicLightManager() throws IOException 
	{
		// Locate all lights
		bulbAddresses = findAllMagicLights();
	}
	
	public ArrayList<InetAddress> findAllMagicLights() throws IOException  
	{
		// Send broadcast
		DatagramSocket sock = new DatagramSocket(LOCAL_PORT);
		sock.setBroadcast(true);
		InetAddress broadcastIP = InetAddress.getByName("255.255.255.255");
		String discoverMsg = "HF-A11ASSISTHREAD";
		byte msg[] = discoverMsg.getBytes();
		DatagramPacket d = new DatagramPacket(msg, msg.length);
		d.setAddress(broadcastIP);
		d.setPort(REMOTE_PORT);
		sock.send(d);
		
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
			
			addrs.add(pack.getAddress());
		}
		
		System.out.println("Found " + addrs.size() + " bulb IP" + (addrs.size() == 1 ? "" : "s"));
		
		// Clean up
		sock.close();	
		return addrs;
	}

}
