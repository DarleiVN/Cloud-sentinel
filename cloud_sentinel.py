import json
from datetime import datetime, timezone

def get_mock_aws_data():
    """
    Simula as respostas do Boto3 para Volumes (describe_volumes) 
    e Elastic IPs (describe_addresses).
    """
    mock_ebs = {
        "Volumes": [
            {
                "VolumeId": "vol-0123456789abcdef0",
                "Size": 30,
                "State": "in-use",
                "VolumeType": "gp3",
                "CreateTime": datetime(2026, 5, 1, tzinfo=timezone.utc),
                "Attachments": [{"InstanceId": "i-abcdef01234567890", "State": "attached"}]
            },
            {
                "VolumeId": "vol-9876543210fedcba0",
                "Size": 50,
                "State": "available",
                "VolumeType": "gp2",
                "CreateTime": datetime(2026, 6, 10, tzinfo=timezone.utc),
                "Attachments": []
            }
        ]
    }

    # NOVA SIMULAÇÃO: Resposta do ec2_client.describe_addresses()
    mock_eip = {
        "Addresses": [
            {
                "PublicIp": "54.210.43.12",
                "AllocationId": "eipalloc-0123456789abcdef0",
                "InstanceId": "i-abcdef01234567890",  # ESTÁ EM USO (Ignorar)
                "AssociationId": "eipassoc-01234567"
            },
            {
                "PublicIp": "34.200.15.99",
                "AllocationId": "eipalloc-9876543210fedcba0",
                # SEM INSTANCE_ID = Alocado, cobrando e esquecido!
                "Domain": "vpc"
            }
        ]
    }

    return mock_ebs, mock_eip


def audit_ebs_volumes(mock_data):
    """Filtra volumes EBS ociosos (status 'available')."""
    idle_volumes = []
    for volume in mock_data.get("Volumes", []):
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


def audit_elastic_ips(mock_data):
    """
    Identifica Elastic IPs (EIP) alocados que não estão associados a nenhuma instância.
    """
    idle_eips = []
    
    # Varre a lista de endereços IP retornada
    for address in mock_data.get("Addresses", []):
        # Se NÃO houver o campo 'InstanceId', significa que o IP está órfão
        if "InstanceId" not in address:
            public_ip = address["PublicIp"]
            alloc_id = address["AllocationId"]
            
            # Cobrança padrão aproximada da AWS para EIP não associado: ~$0.005 por hora
            # Isso dá aproximadamente $3.60 dólares por mês parado!
            estimated_monthly_loss = 3.60
            
            idle_eips.append({
                "Resource_Type": "Elastic_IP",
                "Resource_Id": public_ip,
                "Details": f"Allocation ID: {alloc_id}",
                "Days_Idle": "N/A (Alocado/Sem Uso)",
                "Estimated_Monthly_Loss_USD": estimated_monthly_loss
            })
            
    return idle_eips


if __name__ == "__main__":
    print("[*] Iniciando motor de auditoria Cloud Sentinel...")
    
    # 1. Carrega os mocks separados
    ebs_mock, eip_mock = get_mock_aws_data()
    
    # 2. Executa as auditorias
    relatorio_completo = []
    relatorio_completo.extend(audit_ebs_volumes(ebs_mock))
    relatorio_completo.extend(audit_elastic_ips(eip_mock))
    
    # 3. Exibe o resultado consolidado
    print("\n[+] Relatório de Auditoria Consolidado (JSON Gerado):")
    print(json.dumps(relatorio_completo, indent=4, default=str))