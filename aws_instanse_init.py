#!/bin/python3
import boto3
import time
import os
import subprocess as sp

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
        return response2['Reservations'][0]['Instances'][0]['State']['Name']
    except:
        os.system("tput setaf 1")
        print("\n!! Error in stopping instance !! \n")
        os.system("tput setaf 7")
     
if __name__ == "__main__":   
    os.system("clear")
    os.system("tput setaf 3")
    default = "default"
    profile = input("Enter profile name: ") or default
    os.system("tput setaf 7") 
    
    if profile !='':
        session = boto3.Session(profile_name=profile)
        client = session.resource('ec2')
        region_list = region_list(client) 
        while True:
            x=1
            try: 
                for i in region_list:
                    os.system("tput setaf 6")
                    print("{0} {1}".format(x, i))
                    os.system("tput setaf 7")
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
                os.system("tput setaf 7")
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
        data = list_instances(client)
        while True:
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
                    os.system("tput setaf 7")
                    os.system("tput setaf 3")
                    inst_num = input("\nEnter the instance number to start: ")
                    os.system("tput setaf 7")
                    if inst_num != '' and int(inst_num) < len(data) and int(inst_num) >= 0:
                        inst_id = [data[int(inst_num)]['Id']]
                        public_ip_address = start_instances(client, inst_id)
                        break
                    else: 
                        if int(inst_num)<0:
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
                    if ans == 'y':
                        os.system("tput setaf 3")
                        key_name = input("\n Enter complete path to ssh key: ")
                        os.system("tput setaf 7")
                        return_code = sp.getstatusoutput('ls {0}'.format(key_name))[0]
                        if return_code != 0:
                            os.system("tput setaf 1")
                            print("\n!! Error !! --> Please give correct path to ssh key file.\n")
                            os.system("tput setaf 7")
                        if public_ip_address != None and public_ip_address != "" and return_code==0 :
                            os.system("ssh -i {0} ec2-user@{1}".format(key_name, public_ip_address))
                        else: 
                            os.system("tput setaf 1")
                            print("\n!! Error !! --> wrong option given\n")
                            os.system("tput setaf 7")
                   
                os.system("tput setaf 3")
                input("\n--- Return to main menu by pressing Enter---")
                os.system("tput setaf 7")
                
            if temp == '3':
                os.system("clear")
                while True:
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
                    os.system("tput setaf 7")
                    os.system("tput setaf 3")
                    inst_num = input("Enter the instance number to stop: ")
                    os.system("tput setaf 7")
                    if inst_num != '' and int(inst_num) < len(data) and int(inst_num) >= 0:
                        inst_id = [data[int(inst_num)]['Id']]
                        stop_instances(client, inst_id)
                        os.system("tput setaf 2")
                        print("Instance stopped Successfully")
                        os.system("tput setaf 7")   
                    else: 
                        if int(inst_num)<0:
                            break
                        else: 
                            os.system("tput setaf 1")
                            print("\n!! Error !! --> Please enter valid instance number.\n")
                            os.system("tput setaf 7")
                            input("----- Please try again -----")
                            os.system("clear")
                            
                os.system("tput setaf 3")
                input("\n--- Return to main menu by pressing Enter---")
                os.system("tput setaf 7")
            
            if temp == '4':
                os.system("tput setaf 7")
                os.system("clear")
                break

    except: 
        os.system("tput setaf 3")
        print("\n!! Error !! -->Please contact the Developer\n")
        os.system("tput setaf 7")
        
    
else: 
    os.system("clear")
    os.system("tput setaf 1")
    print("\n!! Error !! -->Please provide profile name\n")
    os.system("tput setaf 7")

