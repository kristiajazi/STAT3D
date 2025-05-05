25-05-05

Read me file for the installation of docker desktop, ubuntu, nvidia tool kit

Steps

1. Install docker desktop (check all the boxes when installing docker)
2. Use this link to install ubuntu https://www.omgubuntu.co.uk/how-to-install-wsl2-on-windows-10
3. Open docker desktop and go to Settings>Resources>WSL integration>Enable Ubuntu>Apply and restart
4. Close docker desktop and launch it again
5. Open ubuntu and set the pw 
6. type the command nvidia-smi, this commands outputs a table where it states the GPU and version of cuda (12 or higher)
7. Go to nvidia webpage at the following website : https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html  

7.0 In ubuntu run the following commands 

7.1 In the "With apt: Ubuntu, Debian" section copy and run the command in Configure the production repository:

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

7.2 DO NOT copy and run THE COMMAND BELOW THAT WHICH SAYS : Optionally, configure the repository to use experimental packages:

sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.l

7.3 copy and run step 2 Update the packages list from the repository: sudo apt-get update

7.4 copy and run step 3 Install the NVIDIA Container Toolkit packages: sudo apt-get install -y nvidia-container-toolkit

7.5 EXIT ubuntu and restart it again

7.6 run : docker --help , to see if it is recognized

8. eventually, run : docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu20.04 nvidia-smi  , this will show the same table with the information displayed after performing step 6 , but this time we want to proof that docker is synchronized
