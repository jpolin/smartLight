// Handle all low-level network communication with specific bulb
import java.net.*;
import java.io.*;

public class MLInterface {

	private InetAddress addr;
	private Socket sock;
	private DataInputStream streamIn;
	private DataOutputStream streamOut;
	
	public MLInterface(InetAddress addr, int remote_port) throws IOException 
	{
		this.addr = addr;
		sock = new Socket(this.addr, remote_port);
		// Set up streams
		streamIn = new DataInputStream(sock.getInputStream());
		streamOut = new DataOutputStream(sock.getOutputStream());
	}
	
	

}
