# Medical Sorting Robot (3 Degrees of Freedom - 3DoF)

## Overview
This project involves the design and implementation of a robotic arm with three degrees of freedom (3DoF) and computer vision capabilities. The system is developed for sorting medical objects based on their color and shape, utilizing a combination of hardware and software tools.

**Development Timeline:** July 2024 - December 2024

## Features
- **Robotic Arm with 3DoF:** Fabricated using 3D printing and consists of Dynamixel AX-12A smart servos.
- **Computer Vision Integration:** Utilizes OpenCV for object detection based on color and shape.
- **Python & Arduino Control:** Python handles the computer vision and robotic control, while Arduino manages the gripper control.
- **Key Tools:**
  - **Arduino:** For gripper mechanism control.
  - **Python:** Used for high-level control and computer vision tasks.
  - **OpenCV:** Library for image processing and object detection.
  - **U2D2:** Interface for Dynamixel servo communication.
  - **3D Printing:** Used for fabricating the robotic arm components.

## System Components
1. **Dynamixel AX-12A Servos:** These smart servos provide movement for the robotic arm's 3 degrees of freedom.
2. **U2D2 Controller:** Facilitates communication between servos and control software.
3. **Camera:** Enables real-time object detection and attribute identification.
4. **Arduino:** Operates the robotic gripper for object manipulation.

## How It Works
1. The camera captures the workspace and detects objects using OpenCV.
2. Object attributes like color and shape are identified, and their positions are calculated.
3. The Python-based control software computes the arm's movement using inverse kinematics.
4. Dynamixel servos adjust the arm to the target position.
5. The Arduino-controlled gripper picks and places the object in the desired location.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- OpenCV library installed
- Dynamixel SDK installed
- Arduino IDE installed

### Hardware Setup
1. Connect the Dynamixel servos to the U2D2 controller.
2. Mount the camera securely above the workspace.
3. Wire the Arduino to the gripper and ensure proper power supply.
4. Connect the U2D2 and Arduino to the computer via USB.

### Software Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/MaximilianoAntonio/Medical-sorting-robot
   cd Medical-sorting-robot
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Upload the Arduino sketch to the Arduino board for gripper control.
4. Run the Python control script:
   ```bash
   python ControlEstados.py
   ```

## Project Structure
- **ControlEstados.py:** Main script implementing state-based logic for robotic arm and gripper operations.
- **Control.py:** Handles arm movement and object detection processes.
- **Ax12.py:** Library for managing interactions with Dynamixel AX-12A servos.
- **Control brazo.py:** Utility script for servo calibration and testing.

## Video Demonstration
You can showcase your robot in action by embedding a video link below. Replace `your_video_id` with the YouTube video ID of your demonstration:

[![Watch the Robot in Action]]([https://www.youtube.com/watch?v=your_video_id](https://www.youtubeeducation.com/watch?v=Cd75hz88lqM))

## Future Improvements
- Expand object detection capabilities to include texture analysis.
- Enhance the sorting algorithm for handling more complex tasks.
- Integrate advanced machine learning models for improved detection and decision-making.

