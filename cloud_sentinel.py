import json
import sys
from datetime import datetime, timezone

# Tenta importar o boto3. Se não estiver no venv ativo, avisa o usuário.
try:
    import boto3
    from botocore.exceptions import NoCredentialsError, PartialCredentialsError
except ImportError:
    print("[!] Erro: Boto3 não encontrado. Ative o venv com 'source venv/bin/activate' e rode 'pip install boto3'")
    sys.exit(1)

def get_mock_aws_data():
    """Simula as respostas do Boto3 para testes locais."""
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
    mock_eip = {
        "Addresses": [
            {
                "PublicIp": "54.210.43.12",
                "AllocationId": "eipalloc-0123456789abcdef0",
                "InstanceId": "i-abcdef01234567890",
                "AssociationId": "eipassoc-01234567"
            },
            {
                "PublicIp": "34.200.15.99",
                "AllocationId": "eipalloc-9876543210fedcba0",
                "Domain": "vpc"
            }
        ]
    }
    return mock_ebs, mock_eip

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

if __name__ == "__main__":
    print("[*] Iniciando motor de auditoria Cloud Sentinel...")
    
    # INTERRUPTOR: True = Mock/Simulado | False = AWS Real
    MODO_MOCK = False
    
    relatorio_completo = []

    if MODO_MOCK:
        print("[!] Executando em MODO SIMULADO (Dados Sintéticos).")
        ebs_data, eip_data = get_mock_aws_data()
        relatorio_completo.extend(audit_ebs_volumes(ebs_data))
        relatorio_completo.extend(audit_elastic_ips(eip_data))
    else:
        print(" Conectando à AWS Real via Boto3...")
        try:
            # Inicializa o cliente EC2 usando o perfil padrão configurado na máquina
            ec2_client = boto3.client("ec2", region_name="us-east-1")
            
            # Coleta os dados em tempo real da AWS
            real_ebs = ec2_client.describe_volumes()
            real_eip = ec2_client.describe_addresses()
            
            # Executa a mesma lógica de auditoria nos dados reais
            relatorio_completo.extend(audit_ebs_volumes(real_ebs))
            relatorio_completo.extend(audit_elastic_ips(real_eip))
            
        except (NoCredentialsError, PartialCredentialsError):
            print("[X] Erro de Autenticação: Nenhuma credencial AWS encontrada na WSL.")
            print("[i] Para corrigir, será necessário rodar 'aws configure' futuramente.")
            sys.exit(1)
        except Exception as e:
            print(f"[X] Erro inesperado ao conectar na AWS: {e}")
            sys.exit(1)
    
    print("\n[+] Relatório de Auditoria Consolidado (JSON Gerado):")
    print(json.dumps(relatorio_completo, indent=4, default=str))