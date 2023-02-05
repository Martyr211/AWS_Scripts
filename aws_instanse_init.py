#!/bin/python3
import boto3
import time
import os
import subprocess as sp

inst_num = 0
def list_all_instances():
    try:
        region_meta_data = client.meta.client.describe_regions()['Regions']
        ec2_regions = []
        for region in region_meta_data:
            client = session.resource('ec2', region_name=region['RegionName'])
            for instance in client.instances.all():
                print(
                    "Id: {0}\nPlatform: {1}\nType: {2}\nPublic IPv4: {3}\nAMI: {4}\nState: {5}\n".format(
                    instance.id, instance.platform, instance.instance_type, instance.public_ip_address, instance.image.id, instance.state
                    )
                )   
    except:
        print("No instances found")

def region_list(client):
    region_meta_data = client.meta.client.describe_regions()['Regions']
    ec2_regions = []
    for region in region_meta_data:
        ec2_regions.append(region['RegionName'])
    return ec2_regions

def list_instances(client):
    try:
        server_list = []
        response = client.meta.client.describe_instances()
        for i in response['Reservations']:
            key = i.get('Instances')[0]['Tags'][0]['Key']
            if key == 'Name':
                value = {
                    "Name":i.get('Instances')[0]['Tags'][0]['Value'],
                    "Id":i.get('Instances')[0]['InstanceId'],
                    "state":i.get('Instances')[0]['State']['Name'] 
                }
                server_list.append(value)
        return server_list        
    except:
        os.system("tput setaf 6")
        print("No instances found")
        os.system("tput setaf 7")
            
def start_instances(client, inst_id):
    try:
        response1 = client.meta.client.start_instances(InstanceIds = inst_id)
        if response1['StartingInstances'][0]['CurrentState']['Name'] == 'pending':
            os.system("tput setaf 5")
            print("\nWaiting for instance to start...\n")
            os.system("tput setaf 7")
        instance_runner_waiter = client.meta.client.get_waiter('instance_running')
        instance_runner_waiter.wait(InstanceIds=inst_id)    
        response2 = client.meta.client.describe_instances(InstanceIds = inst_id)
        os.system("tput setaf 2")
        print("\nInstance started successfully\n")
        os.system("tput setaf 7")
        public_ip_address = response2['Reservations'][0]['Instances'][0]['PublicIpAddress']
        print(public_ip_address)
        return public_ip_address
    except:
        os.system("tput setaf 1")
        print("\n!! Error in starting instance !!\n")
        os.system("tput setaf 7")
        
def stop_instances(client, inst_id):
    try: 
        response1 = client.meta.client.stop_instances(InstanceIds = inst_id)
        if response1['StoppingInstances'][0]['CurrentState']['Name'] == 'stopping':
            os.system("tput setaf 5")
            print("\nWaiting for instance to stop...\n")
            os.system("tput setaf 7")    
        instance_runner_waiter = client.meta.client.get_waiter('instance_stopped')
        instance_runner_waiter.wait(InstanceIds=inst_id)    
        response2 = client.meta.client.describe_instances(InstanceIds = inst_id)
        os.system("tput setaf 2")
        print("\nInstance stopped successfully\n")
        os.system("tput setaf 7")
        return response2['Reservations'][0]['Instances'][0]['State']['Name']
    except:
        os.system("tput setaf 1")
        print("\n!! Error in stopping instance !! \n")
        os.system("tput setaf 7")
    
    
 
if __name__ == "__main__":   
    return_code = sp.getstatusoutput('aws --version')[0]
    if return_code != 0:
        os.system("tput setaf 1")
        print("AWS CLI not installed")
        os.system("tput setaf 3")
        print("\n----Install AWS CLI----\n")
        os.system("tput setaf 7")
        if sp.getstatusoutput("msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi")[0] == 0:
            os.system("tput setaf 2")
            print("AWS CLI installed successfully")
            os.system("tput setaf 7")
            return_code = sp.getstatusoutput('aws --version')[0]
            if return_code != 0:
                exit()
    else:
        while True:
            os.system("clear")
            temp = sp.check_output("aws configure list-profiles", shell=True)
            if temp == b'':
                os.system("tput setaf 1")
                print("!! Error !! --> AWS CLI not configured\n")
                os.system("tput setaf 7")
                print("Type 0 | To configure AWS CLI: ")
                print("Type 1 | To exit: ")
                os.system("tput setaf 3")
                temp = int(input("> "))
                os.system("tput setaf 7")
                if temp == 0:
                    os.system("tput setaf 3")
                    profile_name = input("Enter any profile name: ")
                    os.system("tput setaf 7")
                    os.system("aws configure --profile {}".format(profile_name)) 
                if temp == 1:
                    exit()
                if temp != 0 and temp != 1:
                    os.system("tput setaf 1")
                    print("\n!! Error !! --> Invalid input")
                    os.system("tput setaf 7")
                    input("\nPress Enter to continue...")
            else:   
                temp = temp.decode("utf-8")
                temp = list(temp.split())
                while True:
                    x = 0
                    os.system("tput setaf 6")
                    print("Select Your AWS profile\n")
                    for i in temp:
                        print(" {0} | {1}".format(x,i))
                        x+=1
                    print("-1 | Exit")
                    os.system("tput setaf 3")
                    profile = int(input("Enter the profile number: "))
                    os.system("tput setaf 7")
                    if profile!='' and profile < len(temp) and profile >= 0:
                        profile = temp[profile]
                        break
                    else: 
                        if profile == -1:
                            exit()
                        else:
                            os.system("tput setaf 1")
                            print("Invalid profile number")
                            os.system("tput setaf 7")
                            input("\n------Please try again-------")    
                            os.system("clear")
                if profile != '':
                    os.system("clear")
                    break
                
    if profile !='':
        session = boto3.Session(profile_name=profile)
        client = session.resource('ec2')
        region_list = region_list(client) 
        while True:
            x=1
            try: 
                os.system("tput setaf 6")
                for i in region_list:
                    print("{0} {1}".format(x, i))
                    x+=1
                os.system("tput setaf 3")
                temp = input("Enter region number: ")
                os.system("tput setaf 7")
                if temp != '' and int(temp) <= len(region_list) and int(temp) >= 0:
                    region = region_list[int(temp)-1]
                    break
                else: 
                    os.system("tput setaf 1")
                    print("\n !! Error !! --> please enter valid region number.\n")
                    os.system("tput setaf 7")
            except: 
                os.system("tput setaf 1")
                print("\n!! Error !! -->Invalid region number.\n")
                os.systam("tput setaf 5")
                input("----- Please try again -----")
                os.system("tput setaf 7")
                break
    else:
        os.system("tput setaf 1")
        print("\n!! Error !! --> Invalid profile name.\n")
        os.system("tput setaf 7")
            
    #Script
    try:
        while True:
            data = list_instances(client)
            os.system("clear")
            os.system("tput setaf 6")
            print("Type 1: List Instances with status")
            print("Type 2: Start Instances")
            print("Type 3: Stop Instances")
            print("Type 4: Exit")
            os.system("tput setaf 3")
            temp = input("> ")
            os.system("tput setaf 7")
            
            if temp == '1':
                os.system("tput setaf 6")
                print("List of instances launched in region: ".format(region))
                os.system("tput setaf 7")
                x = 0
                os.system("clear")
                for i in data:
                    os.system("tput setaf 6")
                    print("{0} | {1} status ---------- {2}".format(x,i['Name'],i['state']))
                    os.system("tput setaf 7")
                    x += 1
                os.system("tput setaf 6")
                print("\n--- Return to main menu --- \n")
                os.system("tput setaf 3")
                input("> ")
                os.system("tput setaf 7")
                
            if temp == '2':
                os.system("clear")
                while True:
                    data = list_instances(client)
                    x=0
                    os.system("tput setaf 6")
                    print("\nList of instances launched in region: ".format(region))
                    os.system("tput setaf 7")
                    for i in data:
                        os.system("tput setaf 6")
                        print(" {0} | {1} status ---------- {2}".format(x,i['Name'],i['state']))
                        os.system("tput setaf 7")
                        x += 1
                    os.system("tput setaf 6")
                    print("-1 | Return to main menu")
                    os.system("tput setaf 3")
                    inst_num = input("\nEnter the instance number to start: ")
                    os.system("tput setaf 7")
                    if inst_num != '' and int(inst_num) < len(data) and int(inst_num) >= 0:
                        inst_id = [data[int(inst_num)]['Id']]
                        public_ip_address = start_instances(client, inst_id)
                        break
                    else: 
                        if inst_num != '' and int(inst_num)<0:
                            break
                        else: 
                            os.system("tput setaf 1")
                            print("\n!! Error !! --> Please enter valid instance number.\n")
                            os.system("tput setaf 7") 
                            input("\n----- Please try again -----")
                            os.system("clear")
                            
                if inst_num != '' and int(inst_num) < len(data) and int(inst_num) >= 0:        
                    os.system("tput setaf 4")
                    ans = input("\nDo you want to connect to the instance? (y/n): ")
                    os.system("tput setaf 7")
                    for i in range(0,10):
                        if ans == 'y':
                            os.system("tput setaf 3")
                            ans = input("\nDo you want to choose ssh key from current directory? (y/n): ")
                            os.system("tput setaf 7")
                            if ans == 'y':
                                os.system("tput setaf 6")
                                result = sp.run("ls -1 *.pem", stdout=sp.PIPE, shell=True, encoding='utf-8')
                                key_list = [item for item in result.stdout.split('\n') if item] #output is in string format therefore spliting the output via '\n' & remove the blank item from list
                                status = result.returncode
                                if status == 0:
                                    x=0
                                    print("List of private keys you have in current directory: ") 
                                    for i in key_list: 
                                        print('{0} | {1}'.format(x, i))
                                        x+=1
                                    os.system("tput setaf 3")
                                    key = int(input("Enter key number: "))
                                    os.system("tput setaf 7")
                                    if key != '' and int(key) < len(key_list) and int(key) >= 0:
                                        key_name = key_list[int(key)] 
                                    else:
                                        os.system("tput setaf 1")
                                        print("\n !! Error !! --> please enter valid key number.\n")
                                        os.system("tput setaf 7")
                                        continue
                            else:
                                os.system("tput setaf 3")
                                key_name = input("\nEnter complete path to ssh key: ")
                                os.system("tput setaf 7")   
                                return_code = sp.getstatusoutput('ls {0}'.format(key_name))[0]
                                if return_code != 0:
                                    os.system("tput setaf 1")
                                    print("\n!! Error !! --> Please give correct path to ssh key file in quotes ''\n")
                                    os.system("tput setaf 7")
                                    continue
                        break
                    if key>0 or return_code==0 :
                        if public_ip_address != None and public_ip_address != "":
                            os.system("ssh -i {0} ec2-user@{1}".format(key_name, public_ip_address))
                    print("\n----- Return to main menu -----\n")
                    input("> ")
                
            if temp == '3':
                os.system("clear")
                while True:
                    data = list_instances(client)
                    os.system("tput setaf 6")
                    print("List of instances launched in region: ".format(region))
                    os.system("tput setaf 7")
                    x = 0
                    for i in data:
                        os.system("tput setaf 6")
                        print(" {0} | {1} status ---------- {2}".format(x,i['Name'],i['state']))
                        os.system("tput setaf 7")
                        x += 1
                    os.system("tput setaf 6")
                    print("-1 | Return to main menu")
                    os.system("tput setaf 3")
                    inst_num = input("Enter the instance number to stop: ")
                    os.system("tput setaf 7")
                    if inst_num != '' and int(inst_num) < len(data) and int(inst_num) >= 0:
                        inst_id = [data[int(inst_num)]['Id']]
                        stop_instances(client, inst_id)
                        print("\n----- Return to main menu -----\n")
                        os.system("clear")
                    else: 
                        if inst_num != '' and int(inst_num)<0:
                            break
                        else: 
                            os.system("tput setaf 1")
                            print("\n!! Error !! --> Please enter valid instance number.\n")
                            os.system("tput setaf 7")
                            input("----- Please try again -----")
                            os.system("clear")
                os.system("tput setaf 7")
            
            if temp == '4':
                os.system("tput setaf 7")
                os.system("clear")
                break

    except: 
        os.system("tput setaf 3")
        print("\n!! Error !! -->Please contact the Developer\n")
        os.system("tput setaf 7")
        input("\n--- Exit Code by pressing Enter---")
        os.system("clear")
    
else: 
    os.system("tput setaf 1")
    print("\n!! Error !! -->Please provide profile name\n")
    input("\n--- Exit Code by pressing Enter---")
    os.system("tput setaf 7")
    os.system("clear")

