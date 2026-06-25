from datetime import datetime, timezone

def audit_ebs_volumes(data):
    """Filtra volumes EBS ociosos (status 'available')."""
    idle_volumes = []
    for volume in data.get("Volumes", []):
        if volume.get("State") == "available":
            vol_id = volume["VolumeId"]
            size = volume["Size"]
            create_time = volume["CreateTime"]
            days_idle = (datetime.now(timezone.utc) - create_time).days
            estimated_monthly_loss = size * 0.10
            
            idle_volumes.append({
                "Resource_Type": "EBS_Volume",
                "Resource_Id": vol_id,
                "Details": f"{size}GB ({volume['VolumeType']})",
                "Days_Idle": days_idle,
                "Estimated_Monthly_Loss_USD": round(estimated_monthly_loss, 2)
            })
    return idle_volumes

def audit_elastic_ips(data):
    """Identifica Elastic IPs alocados e não associados."""
    idle_eips = []
    for address in data.get("Addresses", []):
        if "InstanceId" not in address:
            public_ip = address["PublicIp"]
            alloc_id = address["AllocationId"]
            idle_eips.append({
                "Resource_Type": "Elastic_IP",
                "Resource_Id": public_ip,
                "Details": f"Allocation ID: {alloc_id}",
                "Days_Idle": "N/A",
                "Estimated_Monthly_Loss_USD": 3.60
            })
    return idle_eips

def audit_ec2_right_sizing(data):
    """Identifica instâncias EC2 ligadas com uso de CPU abaixo de 10%."""
    underutilized_instances = []
    
    for reservation in data.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            state = instance.get("State", {}).get("Name")
            cpu_usage = instance.get("CpuUtilizationAverage", 100.0)
            
            # Filtro: Se estiver rodando E a CPU média for menor que 10%
            if state == "running" and cpu_usage < 10.0:
                instance_id = instance["InstanceId"]
                instance_type = instance["InstanceType"]
                
                # Estimativa de economia simulada ao fazer o downgrade de tipo
                estimated_savings = 23.00 
                
                underutilized_instances.append({
                    "Resource_Type": "EC2_Instance_RightSizing",
                    "Resource_Id": instance_id,
                    "Details": f"Type: {instance_type} | Avg CPU: {cpu_usage}%",
                    "Days_Idle": "N/A",
                    "Estimated_Monthly_Loss_USD": round(estimated_savings, 2)
                })
                
    return underutilized_instances