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


9. Open docker desktop and pool Massi container : PS C:\Users\Kristi> docker pull pyrevo/cellpose-gpu:1.0

9.0 Create a prova folder in test folder and mount to the docker image pulled before : PS C:\Users\Kristi> docker run -it --rm --gpus all -v C:/Users/Kristi/Desktop/STAT3D/test:/prova docker.io/pyrevo/cellpose-gpu:1.0

9.1 Go in the prova folder : root@f5a4a99e0211:/# cd prova

9.2 Check what the folder contains : root@f5a4a99e0211:/prova# ls

9.3 Check if cellpose is all right : root@f5a4a99e0211:/prova# cellpose --help

9.4 Run cellpose : python -m cellpose --dir /prova --pretrained_model nuclei --chan 0 --chan2 0 --img_filter _morphology2.ome --diameter 17 --do_3D --save_tif --verbose --use_gpu  

10. Try run on supercomputer : not needed to run  from step 1 to step 8 , start from step 9 directly !!

test on my pc on date 250506 : successful, 3D cellpose worked after running script "_zeta" which outputs the image called "z4_and_5_level2_morphology_zeta" (this script extracts only z 4 and 5 from z stack of level 2 and merges them together in a new smaller 3D tiff that contains only the focused cells, also this formats allows to use very quickly cellpose gui with gpu if the user wants to train the model by him/her self) , the following commands were run from docker desktop
a) docker pull pyrevo/cellpose-gpu:1.0
b) docker run -it --rm --gpus all -v C:/Users/Kristi/Desktop/STAT3D/test:/prova docker.io/pyrevo/cellpose-gpu:1.0
c)cd prova
d)ls
e)python -m cellpose --dir /prova --pretrained_model nuclei --chan 0 --chan2 0 --img_filter _zeta --diameter 17 --do_3D --save_tif --verbose --use_gpu
result :
2025-05-06 19:53:42,574 [INFO] network run in 1287.61s
2025-05-06 19:56:29,558 [INFO] masks created in 166.85s
2025-05-06 19:56:34,617 [INFO] >>>> TOTAL TIME 1460.16 sec
2025-05-06 19:56:53,379 [INFO] 100%|##########| 1/1 [24:41<00:00, 1481.05s/it]
2025-05-06 19:56:53,379 [INFO] 100%|##########| 1/1 [24:41<00:00, 1481.05s/it]
2025-05-06 19:56:53,380 [INFO] >>>> completed in 1484.319 sec

test of 250509 , run from github 
Run the new image following the steps 
1.docker login ghcr.io -u YOUR_GITHUB_USERNAME , this means :  docker login ghcr.io -u kristiajazi
2.Pw is the token MV_KA
3.docker pull ghcr.io/kristiajazi/stat3d:latest
4. docker run --platform linux/amd64 --gpus all -it -v C:/Users/Kristi/Desktop/STAT3D/test:/stat3d ghcr.io/kristiajazi/stat3d:latest
5.ls
6.python -m cellpose --dir /stat3d --pretrained_model nuclei --chan 0 --chan2 0 --img_filter _zeta --diameter 17 --do_3D --save_tif --verbose --use_gpu
Note : without --gpus all it does not recognize the nvidia card 


25/05/14 computerSC
1. docker pull ghcr.io/kristiajazi/stat3d:latest
2. docker run --platform linux/amd64 --gpus all -it -v C:/Users/Malin_Group/Desktop/prova:/stat3d ghcr.io/kristiajazi/stat3d:latest
3. python -m cellpose --dir . --pretrained_model nuclei --chan 0 --chan2 0 --img_filter _morphology_zeta --diameter 17 --do_3D --save_tif --verbose --use_gpu
