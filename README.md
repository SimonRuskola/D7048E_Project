# D7048E_Project
Using Movella dot as input for games

## Requirements

- Works on Windows maybe others
- Bluetooth module
- Python 3.9
- Movella dot SDK downloaded on Windows. This file needs to exist: 
  `file:///C:/Program%20Files/Movella/DOT%20PC%20SDK%202023.6/SDK%20Files/Python/x64/movelladot_pc_sdk-2023.6.0-cp39-none-win_amd64.whl`

## Setup for accelerometer to gamepad

1. In the root directory, run:
   ```sh
   pip install -r requirementsMovella.txt
   ```

2. Run the following script:
   ```sh
   python AccelerometerGamepad/movelladot_receive_data_test.py
   ```

3. Try in any game.

----------------------------------------------------------------

## Setup to run ASCII Racer

1. In the root directory, run:
   ```sh
   pip install -r requirementsMovella.txt
   ```

2. Then, in `ascii_racer-master`, run:
   ```sh
   python setup.py install
   ```
   
3. Run the following script and wait for your Movella dot to connect via Bluetooth:
   ```sh
   python ascii_racer-master/asciiracer/movelladot_receive_data.py
   ```

4. Then, run `asciiracer` anywhere to start the game.

