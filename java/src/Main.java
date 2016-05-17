import java.io.*;

// Launch Magic Light application

public class Main {

	public static void main(String[] args) {
		try {
		MLManager manager = new MLManager();
		}
		catch (IOException e){
			System.out.println("Failed to initialize MLManager");
			return;
		}
	}

}
