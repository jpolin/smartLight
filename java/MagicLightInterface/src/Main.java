import java.io.*;

// Launch Magic Light application

public class Main {

	public static void main(String[] args) {
		try {
		MagicLightManager manager = new MagicLightManager();
		}
		catch (IOException e){
			System.out.println("Failed to initialize MagicLightManager");
			return;
		}
	}

}
