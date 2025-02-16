#Mimecraft

##Instructions
Load imu.ino onto an Arduino and then run thread.py, then switch to your Minecraft game in fullscreen.

##Inspiration
Minecraft is one of the most popular games ever created, and to this day, we love to take some time out of our busy days to build castles or fight monsters. However, the traditional keyboard-mouse user interface was preventing us from fully immersing ourselves into our playing experiences. Furthermore, as broke engineering students, we can't afford fancy technologies like VR headsets to elevate our gameplay. Simultaneously, us engineering students will surely find a way to overcomplicate every problem with the power of technology. Therefore, we wanted to bridge the real and virtual worlds by creating an ultra-affordable way to bring Minecraft into real life -- by controlling the player with real-world movements!

##What it does
Mimecraft enables a player to seamlessly control their Minecraft character through real-world motion controls. For example, a user can: rotate their head in real life to turn the player's camera accordingly; swing their left and right arms to enable the in-game inputs of attacking and placing blocks, respectively; and more! Mimecraft can run on top of any version of Minecraft on PC, and requires extremely minimal and inexpensive setup.

##How we built it
We discretized the grand challenge of playing Minecraft with real-life actions into individual sub-tasks such as movement, mouse clicks, and camera controls; these fundamental sub-tasks can ultimately accomplish any in-game task. For camera controls, we interfaced with the MPU6050's accelerometer and gyrosocpe via Arduino Uno, to accurately map a user's head movements to camera movements. For movement and clicking, we used MediaPipe body position landmarks on OpenCV2 and created custom algorithms to translate real-life walking and limb angles to in-game movement and item interaction. To actuate our in-game character, we used the pynput library.

##Challenges we ran into
Early on, we had made several assumptions about the architecture of our project. Initially, we were using a Raspberry Pi to send signals to our test PC, which was hosting a local server, to enable inter-device communications and in-game inputs via different libraries (which required server functionality). We actually got this setup to work, however, we realized that we wouldn't need to use any sort of server and we could just send inputs to the game (at the expense of some lost time). We tried to add more complexity to our project via additional sensors. For example, we tried to use a heartrate sensor to determine whether the in-game player would be walking or running, but after some hours of debugging, we were unable to get the sensor to work. Finally (and most importantly), head position tracking proved to be an extremely difficult task. We initially intended to fuse readings from our webcam and IMU, however, the latter was relatively imprecise given the distance between the camera and its target. Our IMU was also extremely imprecise and hypersensitive. We took extensive efforts to calibrate IMU measurements (i.e. by using complementary filters to fuse gyroscope and accelerometer data to receive accurate readings), and map certain motion patterns to correspond to in-game camera movements such that the movements were natural and comfortable for the user.

##Accomplishments that we're proud of
We built accurate, real-life control of Minecraft with extremely accessible components in just 24 hours! We're glad to have built a prototype that is of high-enough fidelity such that we would actually enjoy playing it.

##What we learned
-Real-time pose estimation with computer vision -Denoising techniques for motion sensors -Serial interfaces and socket connections -How to create a Minecraft server

##What's next for Mimecraft
We'd like to implement inventory and crafting functionality into Mimecraft; we developed a concept to do this via a pushbutton interface on a breadboard (to emulate a real-life workbench) but opted against doing so, due to the large number of components we would need despite our tight hardware limitations. We would also like to combine our calibrated camera and IMU to achieve sensor fusion, for highly-accurate tracking of head movements via an extended Kalman filter (EKF). Finally, we'd like to design a lightweight, nonobstructive headset on which we can place our IMU for improved user comfort; currently, we were limited by the short USB cables.
